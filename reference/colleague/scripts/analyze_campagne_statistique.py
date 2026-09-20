# -*- coding: utf-8 -*-
"""
Analyse de la campagne de replications statistiques (reponse a la reserve
methodologique #1 / Correction_chap5.docx S1.2).

Lit SUIVI_CAMPAGNE_STATISTIQUE.csv (liste de runs nominal/perturbe), determine
automatiquement une fenetre d'observation commune (le moment ou TOUS les runs
ont livre leurs 45 commandes clients), puis compare les deux groupes en
groupes independants (pas de graine commune imposee : la variabilite
naturelle du run en temps reel sert de source d'independance entre runs,
verifiee empiriquement -- deux runs nominaux a reglages identiques produisent
deja des trajectoires de WIP nettement differentes).

Usage :
    python analyze_campagne_statistique.py
Necessite : openpyxl, scipy (pip install openpyxl scipy si absent).
"""
import csv
import os
import statistics as st
import sys

import openpyxl
from scipy import stats

BASE = os.path.dirname(os.path.abspath(__file__))
SUIVI_CSV = os.path.join(BASE, "SUIVI_CAMPAGNE_STATISTIQUE.csv")
NB_COMMANDES_CLIENTS_ATTENDU = 45
# Le compteur periodique "Order Mode MTS/MTO (nb)" de la feuille "Historique
# Dashboard" est capture toutes les ~30s : la cloture de la toute derniere
# commande tombe systematiquement entre deux captures (verifie sur plusieurs
# runs : le maximum observe dans cette colonne plafonne a 44 alors que le
# .ttl confirme bien 45 commandes SERVIE/EN_RETARD en fin de run). On
# detecte donc la livraison complete des commandes clients a 44, pas 45.
NB_COMMANDES_CLIENTS = NB_COMMANDES_CLIENTS_ATTENDU - 1

# Indices de colonne (0-based) dans la feuille "Historique Dashboard"
COL_T = 0
COL_WIP = 3
COL_STOCK_FINI = 4
COL_LEAD_TIME = 2
COL_MTS = 7
COL_MTO = 8
COL_DELAYED = 9
COL_RL = 19
COL_RS = 20
COL_AG = 21
COL_CO = 22
COL_AM = 23
COL_PI = 24


def charger_lignes(fichier_xlsx):
    path = fichier_xlsx if os.path.isabs(fichier_xlsx) else os.path.join(BASE, fichier_xlsx)
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb["Historique Dashboard"]
    rows = [r for r in ws.iter_rows(values_only=True)][1:]
    return [r for r in rows if isinstance(r[COL_T], (int, float))]


def temps_livraison_complete(rows):
    """Premier instant ou MTS+MTO livrees atteint NB_COMMANDES_CLIENTS."""
    for r in rows:
        mts = r[COL_MTS] if isinstance(r[COL_MTS], (int, float)) else 0
        mto = r[COL_MTO] if isinstance(r[COL_MTO], (int, float)) else 0
        if mts + mto >= NB_COMMANDES_CLIENTS:
            return r[COL_T]
    return rows[-1][COL_T]  # jamais atteint -> on prend la fin du run, signale plus bas


def extraire_indicateurs(rows, fenetre_s):
    fenetre = [r for r in rows if r[COL_T] <= fenetre_s]
    if not fenetre:
        fenetre = rows

    def col(i):
        return [r[i] for r in fenetre if isinstance(r[i], (int, float))]

    dernier = fenetre[-1]
    return {
        "pi": dernier[COL_PI],
        "rl": dernier[COL_RL],
        "rs": dernier[COL_RS],
        "ag": dernier[COL_AG],
        "co": dernier[COL_CO],
        "am": dernier[COL_AM],
        "wip_moy": st.mean(col(COL_WIP)),
        "wip_max": max(col(COL_WIP)),
        "stock_moy": st.mean(col(COL_STOCK_FINI)),
        "stock_max": max(col(COL_STOCK_FINI)),
        "lead_time_moy": st.mean(col(COL_LEAD_TIME)),
        "retards": dernier[COL_DELAYED],
    }


def ic95_moyenne(valeurs):
    n = len(valeurs)
    moy = st.mean(valeurs)
    if n < 2:
        return moy, moy, moy
    ec = st.stdev(valeurs)
    marge = stats.t.ppf(0.975, df=n - 1) * ec / (n ** 0.5)
    return moy, moy - marge, moy + marge


def cohen_d_independant(a, b):
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return float("nan")
    sp2 = ((na - 1) * st.variance(a) + (nb - 1) * st.variance(b)) / (na + nb - 2)
    sp = sp2 ** 0.5
    return (st.mean(b) - st.mean(a)) / sp if sp > 0 else float("nan")


def analyse_groupes_independants(nominal, perturbe):
    moy_n, moy_p = st.mean(nominal), st.mean(perturbe)
    t_stat, p_value = stats.ttest_ind(perturbe, nominal, equal_var=False)
    d = cohen_d_independant(nominal, perturbe)
    return {
        "diff_moyenne": moy_p - moy_n,
        "t_stat": t_stat,
        "p_value": p_value,
        "cohen_d": d,
        "significatif_5pct": p_value < 0.05,
    }


def main():
    if not os.path.exists(SUIVI_CSV):
        print(f"Fichier introuvable : {SUIVI_CSV}")
        sys.exit(1)

    runs = {"nominal": [], "perturbe": []}
    with open(SUIVI_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter=";"):
            fichier = row["fichier_xlsx"].strip()
            regime = row["regime"].strip()
            if not fichier or regime not in runs:
                continue
            runs[regime].append(fichier)

    n_nom, n_per = len(runs["nominal"]), len(runs["perturbe"])
    if n_nom < 2 or n_per < 2:
        print(f"Pas assez de runs pour une analyse statistique : {n_nom} nominal / {n_per} perturbe (minimum 2 par regime).")
        return

    print(f"=== Campagne statistique — {n_nom} run(s) nominal / {n_per} run(s) perturbe ===\n")

    # 1) charger toutes les lignes et determiner la fenetre commune
    toutes_lignes = {}
    fenetres = []
    for regime in ("nominal", "perturbe"):
        for fichier in runs[regime]:
            rows = charger_lignes(fichier)
            toutes_lignes[fichier] = rows
            t_livraison = temps_livraison_complete(rows)
            fenetres.append(t_livraison)
            complet = any(
                (r[COL_MTS] or 0) + (r[COL_MTO] or 0) >= NB_COMMANDES_CLIENTS
                for r in rows
            )
            statut = "OK" if complet else "!! JAMAIS ATTEINT 45/45 -- verifier ce run"
            print(f"  [{regime:9}] {fichier} : livraison complete a t={t_livraison:.0f}s ({statut})")

    fenetre_commune = max(fenetres)
    print(f"\nFenetre d'observation commune retenue (auto) : t = {fenetre_commune:.0f}s")
    print("(= l'instant le plus tardif ou UN des runs de la campagne a livre ses 45 commandes clients)\n")

    # 2) extraire les indicateurs de chaque run a cette fenetre commune
    donnees = {"nominal": {}, "perturbe": {}}
    for regime in ("nominal", "perturbe"):
        for fichier in runs[regime]:
            d = extraire_indicateurs(toutes_lignes[fichier], fenetre_commune)
            for k, v in d.items():
                donnees[regime].setdefault(k, []).append(v)

    indicateurs = [
        ("pi", "PI global"),
        ("rl", "RL — Fiabilite"),
        ("rs", "RS — Reactivite"),
        ("ag", "AG — Agilite"),
        ("co", "CO — Cout"),
        ("am", "AM — Actifs"),
        ("wip_moy", "WIP moyen"),
        ("wip_max", "WIP max"),
        ("stock_moy", "Stock fini moyen"),
        ("stock_max", "Stock fini max"),
        ("lead_time_moy", "Lead time moyen (min)"),
        ("retards", "Commandes en retard"),
    ]

    print(f"{'Indicateur':<24}{'Nominal (IC95%)':<28}{'Perturbe (IC95%)':<28}{'Diff. (perturbe-nominal)':<28}{'p-value':<10}{'Cohen d':<10}")
    print("-" * 128)
    for key, label in indicateurs:
        nom_vals = donnees["nominal"][key]
        per_vals = donnees["perturbe"][key]
        nom_moy, nom_bas, nom_haut = ic95_moyenne(nom_vals)
        per_moy, per_bas, per_haut = ic95_moyenne(per_vals)
        r = analyse_groupes_independants(nom_vals, per_vals)
        sig = "**" if r["significatif_5pct"] else ""
        print(
            f"{label:<24}"
            f"{nom_moy:7.3f} [{nom_bas:7.3f};{nom_haut:7.3f}]  "
            f"{per_moy:7.3f} [{per_bas:7.3f};{per_haut:7.3f}]  "
            f"{r['diff_moyenne']:+8.3f}                "
            f"{r['p_value']:.4f}{sig:<3}"
            f"{r['cohen_d']:6.2f}"
        )

    print(f"\n** = difference significative au seuil de 5% (test t de Welch, groupes independants, n_nominal={n_nom}, n_perturbe={n_per})")
    print("Methode : groupes independants (pas de graine commune imposee) -- la variabilite naturelle du")
    print("run en temps reel a ete verifiee comme suffisante pour produire des trajectoires distinctes.")


if __name__ == "__main__":
    main()
