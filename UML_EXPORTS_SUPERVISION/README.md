# Export des diagrammes UML — Communications inter-agents SCONTO-SVU

Ce dossier contient chaque diagramme du document
`docs/uml_agent_communications/SCONTO_SVU_UML_Communications_Agents.pdf`
exporté individuellement, pour envoi séparé ou intégration dans une
présentation.

## Structure

```
UML_EXPORTS_SUPERVISION/
├── README.md          (ce fichier)
├── PDF/                12 fichiers, vectoriel
├── PNG/                12 fichiers, raster haute résolution (~2400 px de large)
└── SVG/                12 fichiers, vectoriel
└── SOURCES/            12 fichiers .tex (TikZ/PGF) + uml-style.tex (style partagé)
```

Aucune capture d'écran AnyLogic : chaque figure est un diagramme UML
généré à partir de code TikZ/PGF (LaTeX), directement à partir des mêmes
sources que le document principal.

## Tableau des figures

| Fichier | Type UML | Cas représenté | Agents principaux | Processus SCOR | Statut |
|---|---|---|---|---|---|
| `01_architecture_globale_agents` | Vue d'ensemble (composants) | Architecture globale des communications multi-agents | Strategic, Tactical, Coordinator, Operational Pilot, Operational Execution, Supplier, Customer | Tous (Plan/Source/Make/Deliver) | Implémenté dans le modèle |
| `02_activite_flux_global` | Activité (à couloirs) | ACT-01 — Flux métier global, réception à clôture/reporting | Customer, Deliver, Tactical, Source/Make | Source, Make, Deliver | Partiellement observé (chemin MTS) |
| `03_activite_reception_commande` | Activité | ACT-02 — Tronc commun de réception et validation | AOe-sD1.2, AOp-sD1, CA-sD1, AT-sP4 | Deliver | Observé runtime |
| `04_activite_mts_stock_suffisant` | Activité | ACT-03 — Cas MTS, stock produit fini suffisant | AT-sP4, CA-sD1, AOp-sD1, AOe-sD1.x | Deliver | Observé Run 01 |
| `05_activite_source_make_deliver` | Activité (avec décision) | ACT-04/05 — Stock insuffisant : décision matière, Source si nécessaire, Make, Deliver | AT-sP3, CA-sM1, AOp-sM1.1, AT-sP2, CA-sS1 | Source, Make | Implémenté, non validé runtime |
| `06_activite_reappro_autonome` | Activité | ACT-06 — Réapprovisionnement autonome (`REAPPRO_n`) | Main (politique de stock), CA-sS1/sM1 | Source, Make | Observé Run 01 |
| `07_sequence_reception_commande` | Séquence | SEQ-01 — Réception et validation d'une commande client | CustomerActor, AOe-sD1.2, AOp-sD1, CA-sD1, AT-sP4 | Deliver | Observé runtime |
| `08_sequence_livraison_directe` | Séquence | SEQ-02 — Livraison directe depuis le stock MTS | CA-sD1, AOp-sD1, AOe-sD1.8..12, CustomerActor | Deliver | Observé Run 01 |
| `09_sequence_consultation_fournisseur` | Séquence | SEQ-03 — Insuffisance matière, consultation fournisseur | AT-sP3, AT-sP2, CA-sS1, AOp-sS1.1, AOe-sS1.2, SupplierActor | Source | Implémenté, non validé runtime |
| `10_sequence_approvisionnement` | Séquence | SEQ-04 — Approvisionnement et retour vers Make | AT-sP2, CA-sS1, AOp-sS1.1, AOe-sS1.2/.3, SupplierActor, AT-sP3 | Source | Implémenté, non validé runtime |
| `11_sequence_make` | Séquence (avec fragment `loop`) | SEQ-05 — Planification et exécution Make | AT-sP3, CA-sM1, AOp-sM1.1, AOe-sM1.2..7, AT-sP4 | Make | Partiellement observé ; `ExecutionProgress`/`ExecutionEnd` implémentés, non observés |
| `12_sequence_livraison_reporting` | Séquence | SEQ-06 — Clôture de livraison et remontée du reporting | AOe-sD1.12, AOp-sD1, CA-sD1, AT-sP4, AS-sP1 | Deliver | Observé Run 01 |

## Sources de vérité

Chaque message et chaque identifiant d'agent provient de
`tracerFluxHierarchique()` dans `model/SCONTO_SVU_GENERIC_MASTER.alp`,
de `POST_MERGE_COMPLETENESS_AUDIT.md`, d'`EXPERIMENTATION_FOUNDATION.md`,
ou de l'annexe déjà publiée `documentation/appendices/g-messages-flux-global.tex`
(dépôt de documentation), elle-même auditée contre un export ABox d'un run
réel. Voir le document principal (§1–§2) pour le détail complet.

## Régénération

Depuis `docs/uml_agent_communications/figures/`, chaque figure dispose
d'un wrapper `standalone-NN-nom.tex` :

```
xelatex -interaction=nonstopmode standalone-NN-nom.tex
pdftoppm -png -r <dpi> standalone-NN-nom.pdf sortie
pdftocairo -svg standalone-NN-nom.pdf sortie.svg
```

Ce dossier ne modifie aucun `.alp`, aucun code Java, aucun scénario JSON.
