#!/usr/bin/env python3
"""Insere des graphiques Excel natifs dans la feuille "Historique Dashboard"
d'un fichier SCONTO_SVU_RESULTS_*.xlsx deja produit par une simulation.

Usage:
    python generate_dashboard_charts.py [chemin_vers_le_fichier.xlsx]

Sans argument, le script prend automatiquement le fichier
SCONTO_SVU_RESULTS_*.xlsx le plus recemment modifie du repertoire courant.

A lancer APRES la fin du run : le fichier est reecrit en continu pendant la
simulation par AnyLogic, donc un lancement pendant un run en cours serait
ecrase au cycle d'export suivant.
"""

import glob
import os
import sys
import tempfile

from openpyxl import load_workbook
from openpyxl.chart import LineChart, Reference
from openpyxl.chart.axis import ChartLines
from openpyxl.chart.legend import Legend
from openpyxl.chart.text import RichText
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.drawing.line import LineProperties
from openpyxl.drawing.text import (
    CharacterProperties,
    Paragraph,
    ParagraphProperties,
    RichTextProperties,
)

SHEET_SOURCE = "Historique Dashboard"
SHEET_CHARTS = "Graphiques Dashboard"

# Palette categorielle (huit teintes distinguables, y compris en daltonisme) --
# ordre fixe : chaque graphique reutilise les teintes a partir du slot 1, donc
# deux series occupant la meme position dans deux graphiques different ont
# une couleur coherente d'un graphique a l'autre.
PALETTE = [
    "2A78D6",  # bleu
    "EB6834",  # orange
    "1BAF7A",  # aqua
    "EDA100",  # jaune
    "E87BA4",  # magenta
    "008300",  # vert
    "4A3AA7",  # violet
    "E34948",  # rouge
]

COULEUR_GRILLE = "E1E0D9"
COULEUR_AXE = "C3C2B7"
COULEUR_TEXTE = "52514E"

# (titre, unite, [(index_colonne_1-based, nom_serie), ...])
# Colonne 1 = Temps simulation (s), utilisee comme axe des categories partout.
GROUPES_GRAPHIQUES = [
    ("PI vs PI cible", None, [(24, "PI"), (25, "PI cible")]),
    ("Scores SCOR", None, [
        (19, "RL"), (20, "RS"), (21, "AG"), (22, "CO"), (23, "AM"),
    ]),
    ("Debit (ent/h)", "ent/h", [
        (2, "Order Throughput"), (15, "Production Throughput"),
    ]),
    ("Lead Time (min)", "min", [
        (3, "Avg Lead Time"), (16, "Order Lead Time"),
    ]),
    ("Temps courts (s)", "s", [
        (7, "Waiting Time"), (14, "Takt Time"),
    ]),
    ("Taux (%)", "%", [
        (6, "PCE"), (11, "Taux de conformite qualite"), (12, "Scrap Rate"), (13, "Rework Rate"),
    ]),
    ("Stocks", None, [
        (4, "WIP"), (5, "Finished Stock"), (17, "Raw Material Stock"),
    ]),
    ("Commandes (nb)", "nb", [
        (8, "Order Mode MTS"), (9, "Order Mode MTO"), (10, "Delayed Orders"),
    ]),
    ("Supplier Lead Time (h)", "h", [
        (18, "Supplier Lead Time"),
    ]),
]

ROWS_PAR_GRAPHIQUE = 24  # espacement vertical entre graphiques (agrandis) sur la feuille cible


def trouver_fichier_resultat(repertoire="."):
    candidats = glob.glob(os.path.join(repertoire, "SCONTO_SVU_RESULTS_*.xlsx"))
    if not candidats:
        raise FileNotFoundError(
            "Aucun fichier SCONTO_SVU_RESULTS_*.xlsx trouve dans " + os.path.abspath(repertoire)
        )
    return max(candidats, key=os.path.getmtime)


def est_placeholder_vide(ws):
    """Detecte la ligne placeholder ecrite quand historiqueDashboard est vide
    (cote .alp : "Aucun point capte..."), pour eviter de generer des
    graphiques sur une feuille sans donnees reelles."""
    if ws.max_row <= 1:
        return True
    if ws.max_row == 2:
        premiere_valeur = ws.cell(row=2, column=1).value
        if isinstance(premiere_valeur, str):
            return True
    return False


def _texte_axe(taille=1000, couleur=COULEUR_TEXTE):
    """RichText compact pour les titres/etiquettes d'axe (taille en 1/100 pt)."""
    cp = CharacterProperties(sz=taille, solidFill=couleur)
    pp = ParagraphProperties(defRPr=cp)
    return RichText(bodyPr=RichTextProperties(), p=[Paragraph(pPr=pp, endParaRPr=cp)])


def construire_graphique(ws, titre, unite, series, derniere_ligne):
    chart = LineChart()
    chart.title = titre
    chart.style = 2
    # Format agrandi (en cm) pour laisser respirer les courbes et la legende.
    chart.height = 11
    chart.width = 30

    chart.x_axis.title = "Temps (s)"
    chart.y_axis.title = unite if unite else titre
    chart.x_axis.delete = False
    chart.y_axis.delete = False

    # Grille et axes discrets mais lisibles, coherents avec les autres graphiques.
    for axis in (chart.x_axis, chart.y_axis):
        axis.majorGridlines = ChartLines(
            spPr=GraphicalProperties(ln=LineProperties(solidFill=COULEUR_GRILLE, w=6350))
        )
        axis.spPr = GraphicalProperties(ln=LineProperties(solidFill=COULEUR_AXE))
        axis.txPr = _texte_axe(900)
    chart.x_axis.title.tx.rich.p[0].pPr = ParagraphProperties(
        defRPr=CharacterProperties(sz=1000, b=True, solidFill=COULEUR_TEXTE)
    )
    chart.y_axis.title.tx.rich.p[0].pPr = ParagraphProperties(
        defRPr=CharacterProperties(sz=1000, b=True, solidFill=COULEUR_TEXTE)
    )

    # Legende en bas : sur des series bruitees, une legende laterale ou
    # superposee finit par chevaucher les courbes -- en bas, elle reste
    # toujours lisible quelle que soit l'amplitude des donnees.
    chart.legend = Legend(legendPos="b")
    chart.legend.overlay = False

    categories = Reference(ws, min_col=1, min_row=2, max_row=derniere_ligne)

    # titles_from_data=True : le nom de chaque serie vient directement de
    # l'en-tete de colonne ecrit par ecrireFeuilleExcel() cote .alp.
    for col_idx, _ in series:
        data = Reference(ws, min_col=col_idx, min_row=1, max_row=derniere_ligne)
        chart.add_data(data, titles_from_data=True)

    # Une couleur nettement distincte par serie (memes slots de palette
    # d'un graphique a l'autre) + traits plus epais, sans marqueurs, pour
    # que les courbes se distinguent meme quand elles se croisent.
    for idx, s in enumerate(chart.series):
        couleur = PALETTE[idx % len(PALETTE)]
        s.graphicalProperties.line.solidFill = couleur
        s.graphicalProperties.line.width = 22225  # ~1.75 pt en EMU
        s.marker.symbol = "none"
        s.smooth = False

    chart.set_categories(categories)
    return chart


def generer_graphiques(chemin_xlsx):
    wb = load_workbook(chemin_xlsx)

    if SHEET_SOURCE not in wb.sheetnames:
        print(f"Feuille '{SHEET_SOURCE}' introuvable dans {chemin_xlsx} -- rien a faire.")
        return 0

    ws_source = wb[SHEET_SOURCE]

    if est_placeholder_vide(ws_source):
        print(
            f"'{SHEET_SOURCE}' ne contient aucune donnee reelle "
            "(placeholder 'Aucun point capte...' ou feuille vide) -- "
            "aucun graphique genere."
        )
        return 0

    derniere_ligne = ws_source.max_row
    nb_points = derniere_ligne - 1
    print(f"{nb_points} point(s) trouve(s) dans '{SHEET_SOURCE}'.")

    if SHEET_CHARTS in wb.sheetnames:
        del wb[SHEET_CHARTS]
    ws_charts = wb.create_sheet(SHEET_CHARTS)

    nb_graphiques = 0
    for i, (titre, unite, series) in enumerate(GROUPES_GRAPHIQUES):
        chart = construire_graphique(ws_source, titre, unite, series, derniere_ligne)
        ancre = f"A{1 + i * ROWS_PAR_GRAPHIQUE}"
        ws_charts.add_chart(chart, ancre)
        nb_graphiques += 1

    # Ecriture atomique : fichier temporaire dans le meme repertoire puis
    # remplacement, pour ne jamais laisser un .xlsx corrompu en cas
    # d'interruption (meme principe que exporterToutesLesTablesExcel() cote AnyLogic).
    repertoire = os.path.dirname(os.path.abspath(chemin_xlsx))
    fd, chemin_tmp = tempfile.mkstemp(suffix=".xlsx", dir=repertoire)
    os.close(fd)
    try:
        wb.save(chemin_tmp)
        os.replace(chemin_tmp, chemin_xlsx)
    except PermissionError:
        if os.path.exists(chemin_tmp):
            os.remove(chemin_tmp)
        print(
            f"Impossible d'ecrire dans {chemin_xlsx} : le fichier est probablement "
            "ouvert dans Excel (ou un autre programme). Fermez-le puis relancez le script."
        )
        sys.exit(1)
    except Exception:
        if os.path.exists(chemin_tmp):
            os.remove(chemin_tmp)
        raise

    print(f"{nb_graphiques} graphique(s) ecrit(s) dans la feuille '{SHEET_CHARTS}' de {chemin_xlsx}")
    return nb_graphiques


def main():
    if len(sys.argv) > 1:
        chemin_xlsx = sys.argv[1]
    else:
        chemin_xlsx = trouver_fichier_resultat(".")
        print(f"Fichier detecte automatiquement : {chemin_xlsx}")

    if not os.path.isfile(chemin_xlsx):
        print(f"Fichier introuvable : {chemin_xlsx}")
        sys.exit(1)

    generer_graphiques(chemin_xlsx)


if __name__ == "__main__":
    main()
