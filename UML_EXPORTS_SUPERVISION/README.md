# Export des diagrammes UML — Communications inter-agents SCONTO-SVU (V2)

Ce dossier contient chaque diagramme du document
`docs/uml_agent_communications/SCONTO_SVU_UML_Communications_Agents.pdf`
exporté individuellement, pour envoi séparé ou intégration dans une
présentation. Version V2 : diagrammes épurés (sans note interne), statuts
runtime corrigés par confrontation directe à l'ABox du Run 01.

## Structure

```
UML_EXPORTS_SUPERVISION/
├── README.md          (ce fichier)
├── PDF/                12 fichiers, vectoriel
├── PNG/                12 fichiers, raster haute résolution (~2500 px de large)
├── SVG/                12 fichiers, vectoriel
└── SOURCES/            12 fichiers .tex (TikZ/PGF) + uml-style.tex (style partagé)
```

Aucune capture d'écran AnyLogic : chaque figure est un diagramme UML
généré à partir de code TikZ/PGF (LaTeX), directement à partir des mêmes
sources que le document principal. Chaque export est autonome : il ne
renvoie à aucune autre figure pour être compris (légende agent et
identifiants techniques inclus dans l'image elle-même).

## Convention de statut

`●` Observé Run 01 · `○` Implémenté, non observé · `△` Non testé (MTO/ETO).
Voir le document principal, section 2.4, pour la définition complète.

## Tableau des figures

| Fichier | Type UML | Cas représenté | Agents principaux | Processus SCOR | Statut |
|---|---|---|---|---|---|
| `01_architecture_globale_agents` | Vue d'ensemble | Architecture globale des communications multi-agents | Stratégique, Tactique, Coordinateur, Pilote opérationnel, Exécution, Fournisseur, Client | Tous | ○ Implémenté (architecture) ; ● Observé Run 01 (chaîne MTS et chaîne Source/Make via réapprovisionnement autonome) |
| `02_activite_flux_global` | Activité (à couloirs) | Flux métier global, réception à clôture et reporting | Client, Deliver, Tactique, Source, Make | Source, Make, Deliver | ● Observé Run 01 |
| `03_activite_reception_commande` | Activité | Tronc commun de réception et de validation d'une commande cliente | AOe-sD1.2, AOp-sD1, CA-sD1, AT-sP4 | Deliver | ● Observé Run 01 |
| `04_activite_mts_stock_suffisant` | Activité | Livraison directe depuis un stock de produit fini suffisant | AT-sP4, CA-sD1, AOp-sD1, AOe-sD1.x | Deliver | ● Observé Run 01 |
| `05_activite_source_make_deliver` | Activité (avec décision) | Décision matière et branchement Source/Make lorsque le stock de produit fini est insuffisant | AT-sP3, CA-sM1, AT-sP2, CA-sS1 | Source, Make | ● Observé Run 01 (via `REAPPRO_1`) |
| `06_activite_reappro_autonome` | Activité | Réapprovisionnement autonome par un ordre interne `REAPPRO_n` | Politique de stock, CA-sS1/CA-sM1 | Source, Make | ● Observé Run 01 |
| `07_sequence_reception_commande` | Séquence | Réception et validation d'une commande client | CustomerActor, AOe-sD1.2, AOp-sD1, CA-sD1, AT-sP4 | Deliver | ● Observé Run 01 |
| `08_sequence_livraison_directe` | Séquence | Livraison directe depuis le stock MTS | CA-sD1, AOp-sD1, AOe-sD1.8..12, CustomerActor | Deliver | ● Observé Run 01 |
| `09_sequence_consultation_fournisseur` | Séquence | Consultation du fournisseur en cas de matière insuffisante | AT-sP3, AT-sP2, CA-sS1, AOp-sS1.1, AOe-sS1.2, SupplierActor | Source | ● Observé Run 01 (via `REAPPRO_1`) |
| `10_sequence_approvisionnement` | Séquence | Approvisionnement matière et retour vers Make | AT-sP2, CA-sS1, AOp-sS1.1, AOe-sS1.2/.3, SupplierActor, AT-sP3 | Source | ● Observé Run 01 (via `REAPPRO_1`) |
| `11_sequence_make` | Séquence (fragment `loop`) | Planification et exécution de la production | AT-sP3, CA-sM1, AOp-sM1.1, AOe-sM1.2..7, AT-sP4 | Make | ● Observé Run 01 pour la planification, `ExecutionStart`, `ExecutionProgress` ; ○ `ExecutionEnd`/`ProductionCompleted`/`ProductAvailableForDelivery` |
| `12_sequence_livraison_reporting` | Séquence | Clôture de la livraison et remontée du reporting | AOe-sD1.12, AOp-sD1, CA-sD1, AT-sP4, AS-sP1 | Deliver | ● Observé Run 01 |

## Sources de vérité

Chaque message et chaque identifiant d'agent provient de
`tracerFluxHierarchique()` dans `model/SCONTO_SVU_GENERIC_MASTER.alp`,
ou de l'ABox du Run 01
(`model/run 01/SCONTO_SVU_ABOX_ZENER_SA_Togo_RUN_1773129600000_1790441166512.ttl`,
`experimentSeed "1001"`). Voir le document principal, sections 1 et annexe A,
pour le détail complet des sources et de la méthode.

## Régénération

Depuis `docs/uml_agent_communications/figures/`, chaque figure dispose
d'un wrapper `standalone-NN-nom.tex` :

```
xelatex -interaction=nonstopmode standalone-NN-nom.tex
pdftoppm -png -r <dpi> standalone-NN-nom.pdf sortie
pdftocairo -svg standalone-NN-nom.pdf sortie.svg
```

Le DPI des PNG est calculé pour viser environ 2500 px de large par figure.

Ce dossier ne modifie aucun `.alp`, aucun code Java, aucun scénario JSON.
