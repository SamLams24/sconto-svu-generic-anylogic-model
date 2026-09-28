# Export des diagrammes UML — Communications inter-agents SCONTO-SVU (V2.2)

Ce dossier contient chaque diagramme du document
`docs/uml_agent_communications/SCONTO_SVU_UML_Communications_Agents.pdf`
exporté individuellement, pour envoi séparé ou intégration dans une
présentation. Version V2.2 : corrections factuelles (attribution exacte de
`PromisedDeliveryDate`, chaîne de confirmation détaillée message par
message, identifiants de pilotes précisés), typographie corrigée.

## Structure

```
UML_EXPORTS_SUPERVISION/
├── README.md          (ce fichier)
├── PDF/                12 fichiers, vectoriel
├── PNG/                12 fichiers, raster haute résolution (~2500 px de large)
├── SVG/                12 fichiers SVG (11 vectoriels + 1 exception raster documentée)
├── SOURCES/            12 fichiers .tex (TikZ/PGF) + uml-style.tex (style partagé)
└── PRESENTATION/       variantes compactes (paysage) de 3 figures verticales,
                        pour PowerPoint / projection / partage mobile
    ├── PDF/, PNG/, SVG/, SOURCES/
```

Aucune figure originale n'a été remplacée par une variante de présentation :
`PRESENTATION/` s'ajoute au contenu existant.

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
| `03_activite_reception_commande` | Activité | Tronc commun de réception et de validation d'une commande cliente | AOe-sD1.2, AOp-sD1.1, AOp-sD1.3, AOe-sD1.8, CA-sD1, AT-sP4 | Deliver | ● Observé Run 01 |
| `04_activite_mts_stock_suffisant` | Activité | Livraison directe depuis un stock de produit fini suffisant | AT-sP4, CA-sD1, AOp-sD1.3, AOe-sD1.x | Deliver | ● Observé Run 01 |
| `05_activite_source_make_deliver` | Activité (avec décision) | Décision matière et branchement Source/Make lorsque le stock de produit fini est insuffisant | AT-sP3, CA-sM1, AT-sP2, CA-sS1 | Source, Make | ● Observé Run 01 (via `REAPPRO_1`) |
| `06_activite_reappro_autonome` | Activité | Réapprovisionnement autonome par un ordre interne `REAPPRO_n` | Politique de stock, CA-sS1/CA-sM1 | Source, Make | ● Observé Run 01 |
| `07_sequence_reception_commande` | Séquence | Réception et validation d'une commande client, agent par agent (7 lifelines distinctes) | CustomerActor, AOe-sD1.2, AOp-sD1.1, AOp-sD1.3, AOe-sD1.8, CA-sD1, AT-sP4 | Deliver | ● Observé Run 01 |
| `08_sequence_livraison_directe` | Séquence | Livraison directe depuis le stock MTS, à partir de `DeliveryPlan` | AT-sP4, CA-sD1, AOp-sD1.3/.7 (vue agrégée), AOe-sD1.8..12 (vue agrégée), CustomerActor | Deliver | ● Observé Run 01 |
| `09_sequence_consultation_fournisseur` | Séquence | Consultation du fournisseur en cas de matière insuffisante | AT-sP3, AT-sP2, CA-sS1, AOp-sS1.1, AOe-sS1.2, SupplierActor | Source | ● Observé Run 01 (via `REAPPRO_1`) |
| `10_sequence_approvisionnement` | Séquence | Approvisionnement matière et retour vers Make | AT-sP2, CA-sS1, AOp-sS1.1, AOe-sS1.2/.3 (vue agrégée), SupplierActor, AT-sP3 | Source | ● Observé Run 01 (via `REAPPRO_1`) |
| `11_sequence_make` | Séquence (fragment `loop`) | Planification et exécution de la production | AT-sP3, CA-sM1, AOp-sM1.1, AOe-sM1.2..7 (vue agrégée), AT-sP4 | Make | ● Observé Run 01 pour la planification, `ExecutionStart`, `ExecutionProgress` ; ○ `ExecutionEnd`/`ProductionCompleted`/`ProductAvailableForDelivery` |
| `12_sequence_livraison_reporting` | Séquence | Clôture de la livraison et remontée du reporting | AOe-sD1.12, AOp-sD1.7, CA-sD1, AT-sP4, AS-sP1 | Deliver | ● Observé Run 01 |

## Variantes de présentation

Trois diagrammes d'activité très verticaux (peu lisibles en diaporama)
disposent d'une variante compacte, réorganisée en deux rangées gauche
à droite, dans `PRESENTATION/` :

| Fichier | Figure originale |
|---|---|
| `03_activite_reception_commande_presentation` | `03_activite_reception_commande` |
| `04_activite_mts_stock_suffisant_presentation` | `04_activite_mts_stock_suffisant` |
| `06_activite_reappro_autonome_presentation` | `06_activite_reappro_autonome` |

Même contenu et mêmes identifiants d'agents que la figure originale ;
seule la disposition change.

## Vérification des exports

Chaque PDF a été recompilé et inspecté visuellement page par page. Chaque
PNG a été rendu à la résolution cible et inspecté. Chaque SVG a été
rasterisé (Chromium headless) et inspecté, pas seulement validé comme
XML bien formé.

### Exception documentée : `09_sequence_consultation_fournisseur.svg`

Sur cette figure uniquement, deux libellés contenant « Feasibility »
étaient mal dessinés lors de la conversion en SVG (glyphe erroné, absent
du PDF source et de son rendu raster). Quatre méthodes locales ont été
essayées avant de conclure :

1. `pdftocairo -svg` (référence de police intégrée) : défaut présent.
2. `dvisvgm --pdf` (référence de police intégrée, format alternatif) : même défaut.
3. `dvisvgm --pdf --no-fonts` (conversion des glyphes en chemins vectoriels,
   sans aucune référence de police) : même défaut. Ce test isole le
   problème dans les contours de glyphe eux-mêmes tels qu'intégrés dans le
   PDF par la chaîne XeLaTeX/xdvipdfmx, pas dans un outil de conversion SVG.
4. Conversion native XeLaTeX → XDV → `dvisvgm` (sans passer par le PDF) :
   techniquement inapplicable, le positionnement absolu de TikZ sous
   XeLaTeX dépendant du greffon PDF (xdvipdfmx) et ne se reconstruisant pas
   correctement à partir du XDV seul.

Un test isolé (les mêmes mots seuls, hors du diagramme complet) démontre
que le défaut n'est pas une faute de frappe dans le code source : les
mêmes mots s'y affichent correctement. Le défaut n'apparaît que dans ce
diagramme précis, avec ses répétitions particulières de sous-chaînes, et
uniquement lors de l'extraction de glyphes pour le SVG.

Aucune des méthodes locales disponibles ne produit un SVG vectoriel texte
correct pour cette figure. Le SVG de `09_sequence_consultation_fournisseur`
est donc fourni sous forme alternative : image PNG haute résolution
encapsulée dans un conteneur SVG, garantissant un texte identique au PDF
source. C'est un fichier `.svg` valide et à l'échelle correcte, mais ce
n'est pas un vectoriel texte pour cette figure spécifique. Les 11 autres
SVG du dossier (et les 3 SVG de `PRESENTATION/`) sont du texte vectoriel
réel, confirmé par inspection rasterisée.

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
