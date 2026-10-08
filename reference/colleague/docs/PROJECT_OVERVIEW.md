# SCONTO-SVU — Vue d'ensemble du projet

> Document généré par analyse du fichier de modèle AnyLogic `SCONTO_SVU_GENERIC10-4.alp` et des fichiers de données associés présents à la racine du dépôt. Aucun fichier `.alp`, `database/`, `.json`, `.ttl` ou `.xlsx` n'a été modifié pour produire cette documentation.

## 1. Qu'est-ce que ce projet ?

Ce dépôt contient un **modèle de simulation à événements discrets / multi-agents** construit avec **AnyLogic** (version modèle `8.9.7`, moteur `8.9.8`). Le modèle s'appelle en interne `SCONTO_VSM_Generic` (package Java `sconto_vsm_generic`) et est distribué ici sous le nom de fichier `SCONTO_SVU_GENERIC10-4.alp` (4ᵉ itération connue dans ce dossier, après `-2` et `-3`).

L'objectif du modèle, tel qu'il ressort du code et des commentaires internes, est de **combiner et d'agréger deux référentiels de modélisation de chaîne logistique** :

- **VSM (Value Stream Mapping)** : cartographie de la chaîne de valeur — postes, flux physiques, flux d'information, temps de cycle, stocks, taux de valeur ajoutée (`champTauxVA`), rapport VSM (`getRapportVSM`).
- **SCOR (Supply Chain Operations Reference model)** : structuration des activités par macro-processus **Plan / Source (S) / Make (M) / Deliver (D) / Return (SR/DR)**, avec des codes de micro-activités de niveau 3 du type `sS1.1`, `sM1.2`, `sD1.3`, etc. Le modèle calcule les **5 attributs de performance SCOR** :
  - `RL` — Reliability (Fiabilité)
  - `RS` — Responsiveness (Réactivité)
  - `AG` — Agility (Agilité)
  - `CO` — Cost (Coût)
  - `AM` — Asset Management (Gestion des actifs)

  Ces scores (`scoreRL`, `scoreRS`, `scoreAG`, `scoreCO`, `scoreAM`) sont pondérés (poids `champPoidsRL/RS/AG/CO/AM`, configurables par scénario) et agrégés en un **Indice de Performance global (PI)** via `calculerPIGlobal`. Une méthode **AHP (Analytic Hierarchy Process)** est utilisée pour la pondération des métriques (`poidsAHPPourCodeSCOR`, `scorerGoulotAHP`, `appliquerPoidsAttributsSCOR`).

Le modèle intègre en plus explicitement :
- une **hiérarchie ISA-95** (niveaux `STRATEGIC` / `TACTICAL` / `OPERATIONAL` / `MACHINE`) pour l'alignement organisationnel/ontologique, portée par le JSON de scénario plutôt que codée en dur ;
- une architecture **multi-agents hiérarchique inspirée d'ADACOR** (holonique), avec des agents `StrategicAgent`, `TacticalAgent`, `OperationalAgent`, `CoordinatorAgent` et un `BlackboardAgent` (pattern tableau noir pour la coordination/négociation entre agents) ;
- un **export vers une ontologie OWL/RDF (Turtle)** décrivant chaque run de simulation (voir `SCENARIOS_AND_DATA.md`) ;
- un **export Excel** périodique des résultats et un stockage en base **HSQLDB** embarquée.

> **SCONTO** et **SVU** : ces acronymes apparaissent systématiquement dans les noms de fichiers et les préfixes d'ontologie (`sconto-vsm.org`, `sconto-svu`) mais leur développement complet (ce que chaque lettre signifie précisément) n'est explicité nulle part dans les fichiers analysés. *À confirmer avec l'utilisateur.* Par déduction contextuelle uniquement : SCOR + VSM semblent être à l'origine de "SC…" / "…VSM", et "SVU" pourrait désigner une variante ou un sous-système ("Simulation..." ?) — hypothèse non vérifiée.

## 2. Cas d'usage / instance de données

Le modèle est **générique** (`GENERIC10`, package `sconto_vsm_generic`) mais a été paramétré et exécuté pour au moins les cas suivants (visibles via les scénarios JSON et les fichiers d'export) :

| Cas | Fichiers associés |
|---|---|
| **ZENER SA Togo** (chaîne d'embouteillage de GPL — bonbonnes de gaz) | `scenario_ZENER_SA_Togo_v*.json`, `SCONTO_SVU_ABOX_ZENER_SA_Togo_RUN_*.ttl`, `SCONTO_SVU_RESULTS_ZENER_SA_Togo_RUN_*.xlsx`, `export_ZENER_SA_Togo.xlsx` |
| Vélo urbain | `scenario_2_velo_urbain.json` |
| Automobile GX5 | `scenario_3_automobile_gx5.json` |
| VeloTech Assembly | `export_VeloTech_Assembly.xlsx` |
| Hiérarchie de test | `scenario_ZENER_TEST_hierarchie.json` |

Le cas **ZENER SA Togo** est de loin le plus documenté et le plus exécuté (17 runs `.ttl`/`.xlsx` horodatés entre le 26 et le 30 août 2026). D'après le scénario `scenario_ZENER_SA_Togo_v72.json` : entreprise focale = *ZENER SA Togo*, 5 acteurs (fournisseurs de GPL, de bouteilles vides, d'accessoires, l'entreprise focale, etc.), 71 postes, 1 machine, 5 sous-scénarios de débit.

## 3. Architecture générale / flux de données

```
scenario_<Client>_v<N>.json  ──►  Modèle AnyLogic (SCONTO_SVU_GENERIC10-4.alp)
   (paramètres, acteurs,            │
    postes, hiérarchie ISA-95,      ├──► base HSQLDB embarquée (database/)
    pondérations SCOR)              │      (journal des runs, config, logs)
                                     │
                                     ├──► export périodique Excel
                                     │      SCONTO_SVU_RESULTS_<Client>_RUN_<t1>_<t2>.xlsx
                                     │
                                     └──► export ontologique RDF/Turtle (ABox)
                                            SCONTO_SVU_ABOX_<Client>_RUN_<t1>_<t2>.ttl
                                            (individus conformes aux ontologies
                                             Core 4.3.0 + Agent Extension 1.1.2
                                             + AER Communication Extension 1.1.2)
```

Détails dans `MODEL_STRUCTURE.md` (structure interne du modèle) et `SCENARIOS_AND_DATA.md` (schémas JSON/SQL/TTL).

## 4. Fichiers non liés au modèle

- `Rapport journalier PAYZY-10 août 2026.pdf` : document sans lien apparent avec le modèle de simulation (rapport journalier d'une activité "PAYZY"). Non traité dans cette documentation.
- Les icônes PNG (`aiguillage.png`, `factory-machine.png`, `forklift.png`, etc.) sont des pictogrammes utilisés dans la présentation graphique (vue animée) du modèle AnyLogic pour représenter acteurs, postes et flux.

## 5. Historique des versions du modèle

Trois fichiers `.alp` coexistent dans le dépôt : `SCONTO_SVU_GENERIC10-2.alp`, `-3.alp`, `-4.alp` (tailles croissantes : 2 191 540 → 2 200 939 → 2 204 920 octets), modifiés respectivement les 28, 29 et 30 août 2026. Aucun changelog explicite n'a été trouvé dans le XML ; les commentaires internes utilisent des marqueurs de sprint/feature du type `S2.1`, `S2.2`, `C08`, `C14` (probablement des identifiants de tickets/étapes de développement internes, distincts des codes SCOR `S1.x`/`M1.x`/`D1.x`). *Signification exacte de ces marqueurs à confirmer avec l'utilisateur.* Seul `-4.alp` (le plus récent) a été analysé en détail ; `-2` et `-3` sont conservés comme historique.

## 6. Pour aller plus loin

- `MODEL_STRUCTURE.md` — détail des agents AnyLogic, fonctions clés, expérience de simulation.
- `SCENARIOS_AND_DATA.md` — schéma des scénarios JSON, de la base HSQLDB et de l'ontologie RDF/Turtle exportée.
- `CLAUDE.md` — point d'entrée rapide pour une future session Claude Code sur ce projet.
