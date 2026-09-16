# Analyse de fusion — branche collègue V6.5-corr-b vs modèle maître SCONTO-SVU

## 1. Sources analysées

- ZIP collègue : `cc42f4aa-92cb-4a98-8d9e-0d4018007fb8.zip`
- Modèle `.alp` joint : `2b60802a-13a7-434c-b6a8-800367784b62.alp`
- Modèle du ZIP : `V6.5-corr-b/SCONTO_SVU_GENERIC10-4.alp`
- Modèle maître courant : `SCONTO_SVU_FINAL_VALIDATED_FORECAST_DATACO_MULTIPRODUCT_CONCURRENT_FIX.alp`

Le `.alp` joint séparément et `SCONTO_SVU_GENERIC10-4.alp` du ZIP sont strictement identiques (même SHA-256 : `43552932ba9f9cfa86591a1a41c6f7cd6c72d4d7bbc64b3e12f57b996284bbcf`).

Le dépôt Git du ZIP ne fournit pas d'historique exploitable pour un merge classique : un seul commit initial est présent et la quasi-totalité des travaux récents est non suivie par Git. La fusion doit donc être faite sémantiquement au niveau XML/Java AnyLogic, pas par `git merge`.

## 2. Inventaire du ZIP

Le ZIP contient :

- 1 modèle `.alp` principal ;
- 1 scénario JSON ZENER (`scenario_ZENER_SA_Togo_v72.json`) ;
- 10 documents Markdown d'architecture, validation et résultats ;
- 2 scripts Python d'analyse / génération de graphiques ;
- 3 DOCX (relecture doctorale, scénarios, rapport comparatif) ;
- 6 CSV de runs / suivi statistique ;
- 65 exports ABox `.ttl` ;
- 67 exports de résultats `.xlsx` ;
- une base HSQLDB `database/` ;
- des images/icônes de présentation AnyLogic.

Les `.ttl`, `.xlsx` et `database/` sont essentiellement des artefacts de run / preuves expérimentales. Ils ne doivent pas être fusionnés dans le code maître comme sources métier.

## 3. Delta structurel du modèle

| Élément | Modèle collègue | Modèle maître |
|---|---:|---:|
| Taille | 2 290 956 octets | 2 244 316 octets |
| IDs AnyLogic | 1 685 | 1 846 |
| Fonctions AnyLogic | 337 | 363 |
| Composants nommés | 2 275 | 2 385 |

Le maître contient davantage de composants visuels/fonctionnels car il inclut le module Prophet/DataCo, la vue Prévisions/Recalibrator et la fondation multi-produit.

Comparaison sémantique :

- 21 composants nommés existent uniquement dans la branche collègue ;
- 114 composants nommés existent uniquement dans le maître (majoritairement Forecast/DataCo/multi-produit) ;
- 42 fonctions communes ont un corps Java différent ;
- 2 événements communs ont une action différente ;
- plusieurs méthodes Java embarquées dans les blocs de code (non représentées comme `<Function>` AnyLogic) existent seulement d'un côté.

Tout le lot de correctifs `C15.1` à `C15.31` est absent du maître actuel. Le maître contient en revanche `C14.68`, lié aux corrections les plus récentes de notre branche.

## 4. Nouveautés majeures de la branche collègue

### 4.1. Refonte du Performance Index / conformité SCOR

Le changement le plus important est la réécriture très profonde de `StrategicAgent.calculerPIGlobal()` : ~29,4 k caractères dans la branche collègue contre ~12,4 k dans le maître.

Principales évolutions :

- phase d'amorçage : PI maintenu à la cible tant que le périmètre mesuré n'est pas suffisant ;
- poids effectif nul pour les familles sans données réelles ;
- seuil d'échantillon RL avant activation dans le PI ;
- traçabilité du périmètre réellement pondéré (`attributsPonderesPI`, `sommePoidsEffectifsPI`) ;
- correction du coût `CO.1.1` en utilisant les unités réellement livrées (`unitesLivreesClients`) au lieu d'un compteur inadéquat ;
- nettoyage des métriques RL redondantes : `RL.3.33` / `RL.3.35` deviennent informatives ;
- dans le code final, `RL.2.2` est l'indicateur RL réellement pondéré ;
- `AG.3.32` reste une métrique SCOR réelle ; les autres composantes AG sont explicitement des proxies (`PROXY.AG.SYSTEM_UTILIZATION`, `PROXY.AG.STABILITE_DEBIT`) ;
- `AM.2.2` reste une métrique SCOR réelle ; la disponibilité machine est renommée `PROXY.AM.DISPONIBILITE_MACHINE` au lieu d'être revendiquée comme `AM.3.9` ;
- normalisation RS corrigée par rapport aux temps nominaux pondérés réels des chemins ;
- ajout d'une décroissance hyperbolique pour les métriques `RS.2.x` afin d'éviter une saturation permanente à 0 quand Make est très dégradé.

Cette partie est scientifiquement importante et doit être portée dans le maître.

### 4.2. Détection continue des retards / engagement client

Ajouts dans `CommandeAgent` :

- `retardConstate` ;
- `modeEngagementClient` ;
- `dureeClientAccumulee`.

Ajouts dans la logique embarquée :

- `dureeMetierEcoulee()` ;
- `delaiEngagementCommande()` / `delaiEngagementMetierSecondes()` ;
- `evaluerRetardsCommandesOuvertes()` ;
- `evaluerPonctualiteMetier()` ;
- `borneLeadTimeClientSecondes()`.

Un nouvel événement `bilanPeriodique` exécute toutes les 60 s : détection des retards, diagnostic des commandes bloquées et bilan de commandes.

But : une commande ouverte et déjà hors engagement doit dégrader RL immédiatement, sans attendre une éventuelle livraison finale.

**Attention de fusion** : les engagements 4 h / 8 h / 24 h et la séparation du périmètre client ont été calibrés pour ZENER. Notre maître DataCo possède sa propre logique de promesse (`overrideDelaiPromesseDataCo`, délais issus de DataCo). Il faut porter le mécanisme, pas recopier aveuglément les constantes ZENER.

### 4.3. Correction critique du rattachement flux → commande (`C15.28`)

Nouvelle méthode `fluxAppartientACommande(idFlux,idCommande)`.

Elle remplace les recherches fragiles par `contains(cmd.idCommande)`. Exemple du bug : `CMD_44_F_12` contient textuellement `CMD_4`, ce qui faisait créditer les unités de CMD_44 à CMD_4.

Cette correction doit être portée en priorité dans le maître, notamment dans `finDeParcours()` et `rebuter()`. Elle est générique et compatible avec le multi-produit.

### 4.4. Ordonnancement MTO

`CoordinatorAgent.ordonnancerProduction()` a été modifié pour libérer **tout le carnet MTO** à chaque cycle, trié par priorité puis EDD, sans porte GOULOT/PANNE et sans plafond d'ordres.

Objectif : empêcher une grosse commande (pic 200 unités) de bloquer artificiellement les suivantes.

**Attention** : c'est un changement de comportement fort. Sur notre campagne DataCo à 365 commandes, un portage brut peut accroître fortement le WIP. À intégrer seulement après un test A/B sur le maître.

### 4.5. Historisation du dashboard / export Excel

La branche collègue ajoute un historique complet du dashboard :

- `historiqueDashboard` ;
- `capturerPointHistoriqueDashboard()` ;
- `historiqueDashboardColumns()` / `historiqueDashboardRows()` ;
- capture au démarrage puis à chaque cycle d'`ExcelExportManager` ;
- feuille Excel `Historique Dashboard` ;
- environ 25 colonnes : temps, KPI opérationnels, RL/RS/AG/CO/AM, PI, cible, périmètre pondéré.

Le script `generate_dashboard_charts.py` produit ensuite des graphiques Excel natifs à partir de cet historique.

À porter dans le maître, en conservant nos feuilles Forecast/DataCo et nos exports propres.

### 4.6. Export matière par article

Ajout `detailStockMatiereParMatiere()` pour ne plus sommer des unités physiques hétérogènes (kg GPL + bouteilles + kits). Cette valeur est exportée dans les séries de dashboard / CSV.

C'est une amélioration méthodologique utile et générique : le maître devrait la conserver.

### 4.7. Vue holonique / états des agents (`C14.52`–`C14.55`)

Les correctifs portent sur la cohérence entre états physiques et vue hiérarchique :

- flux visuels MTS font passer temporairement les agents Deliver en `WORKING`, sans les transformer en goulots ;
- popup OperationalAgent recalculé poste par poste plutôt que depuis un flag de groupe ;
- suppression du gel des agents Plan P2-P5 ;
- nouvelle source unique `etatCoordinateurMacro()` utilisée à la fois pour couleur et popup du Coordinateur.

Ces changements sont essentiellement orthogonaux au module DataCo et sont de bons candidats au portage.

### 4.8. Numérotation / distinction commandes clients et REAPPRO

La branche collègue ajoute `seqCommandeClient` et des bilans distinguant commandes clientes et ordres internes.

Notre maître dispose déjà d'une solution plus récente (`prochainNumeroCommandeClient()`, `estCommandeClient()`, `estOrdreReappro()`, etc.). **Ne pas recopier `seqCommandeClient`** ; garder la mécanique du maître et ne porter que les améliorations de libellés/logs utiles.

### 4.9. Diagnostic de production / commandes bloquées

Ajouts :

- `diagnostiquerCommandesBloquees()` ;
- traces `[DIAG-BLOQUEE]` ;
- meilleure traçabilité des `ExecutionStart` ;
- compte des unités terminées par commande.

Objectif : distinguer un vrai deadlock d'un lot volumineux encore en train de traverser Make.

À porter : utile pour le diagnostic du maître, particulièrement avec les gros ordres REAPPRO multi-produit.

### 4.10. Bouton de perturbation “Pic ponctuel 200 unités”

Nouveau contrôle natif `btnPicPonctuel200`, destiné aux campagnes nominal/perturbé. Il déclenche `declencherPicPonctuelDemande(200)` en un clic.

Le maître possède déjà son propre panneau de perturbations et des mécanismes de retard fournisseur. Ce bouton peut être conservé comme scénario de test mais doit être intégré à la vue actuelle sans remplacer nos contrôles.

## 5. Chaîne expérimentale ajoutée autour du modèle

Le ZIP ne contient pas seulement du code : il apporte une vraie chaîne de validation expérimentale.

### Campagne nominale / perturbée

- scénario nominal ZENER à 45 commandes ;
- scénario perturbé par une commande exceptionnelle de 200 unités ;
- rapport comparatif nominal/perturbé ;
- traçage WIP, stocks, lead time, retards, RL/RS/AG/CO/AM et PI.

### Campagne statistique

- 3 réplications nominales + 3 perturbées ;
- `SUIVI_CAMPAGNE_STATISTIQUE.csv` ;
- `analyze_campagne_statistique.py` ;
- test t de Welch, IC 95 %, d de Cohen ;
- rapport final `RAPPORT_CAMPAGNE_STATISTIQUE.md`.

Résultat rapporté : 7 indicateurs sur 12 significatifs à 5 %, PI moyen 8,811 nominal vs 7,390 perturbé, écart -1,421, p < 0,0001.

Cette chaîne peut être conservée comme outillage de validation, indépendamment du merge du `.alp`.

## 6. Incohérences documentaires détectées

`ARBRE_PI_SCOR.md` n'est pas entièrement synchronisé avec le code final.

Il indique encore :

- RL.2.1 et RL.2.2 pondérés à 1/2 chacun ;
- AG.1.1 comme composante réelle ;
- AM.3.9 comme disponibilité machine réelle.

Or le code final de `calculerPIGlobal()` fait :

- `RL.2.1` informatif, poids 0 ; `RL.2.2` pondéré ;
- `AG.3.32` + deux proxies explicites ;
- `AM.2.2` + proxy disponibilité machine.

Il faudra donc mettre à jour ce document après fusion. Les rapports récents sont plus proches du code final que `ARBRE_PI_SCOR.md`.

## 7. Éléments du maître à préserver absolument

La branche maître actuelle possède de nombreux blocs absents du modèle collègue :

- module Prophet/DataCo complet ;
- vue `viewPrevisions` ;
- chargement Prophet et DataCo ;
- Recalibrator, écarts, bar charts et courbes dynamiques ;
- AutoCommande DataCo 2017 ;
- garde annuelle 2017 ;
- multi-produit DataCo (`stockFiniParProduit`, catalogue produits, rotation Sports/Clothing/Electronics) ;
- synchronisation stock par produit → stock agrégé ;
- dépendances commande cliente ↔ REAPPRO ;
- registre détaillé des temps commande ;
- perturbations fournisseur et manifeste de run ;
- correction `C14.68` de concurrence sur la politique de stock produit.

Ces blocs ne doivent jamais être remplacés par les versions plus anciennes du modèle collègue.

## 8. Cartographie de fusion

### Portage direct / faible risque

- variables StrategicAgent liées au PI (`attributsPonderesPI`, `sommePoidsEffectifsPI`, flags de présence, tolérance RS, etc.) ;
- `etatCoordinateurMacro()` ;
- `nombreCommandesClosesFiabilite()` ;
- `unitesLivreesClients()` ;
- champ `retardConstate` et mécanisme de retard (avec adaptation DataCo des engagements) ;
- `fluxAppartientACommande()` ;
- diagnostics commandes bloquées ;
- `detailStockMatiereParMatiere()` ;
- logique `NormalizationProfile.decroissanceLente` et `majBorneCycleMacro()` ;
- correctifs vue holonique ;
- historique Dashboard + scripts externes.

### Fusion manuelle obligatoire

| Fonction / bloc | Pourquoi |
|---|---|
| `demarrerSimulation()` | maître = Forecast/DataCo + multi-produit + perturbations ; collègue = warm-up PI + historique Dashboard |
| `genererCommande()` | maître = choix produit, DataCo override, retard fournisseur ; collègue = engagement client figé / ancien compteur client |
| `finDeParcours()` | maître = stock multi-produit, dépendances REAPPRO, temps commande ; collègue = retard + rattachement strict flux/commande |
| `chargerScenarioJSON()` / `sauverScenarioJSON()` | schémas ont divergé |
| `clearScenarioBeforeJsonLoad()` | états Forecast/DataCo + états PI à réinitialiser ensemble |
| `exporterToutesLesTablesExcel()` | maître et collègue ajoutent des feuilles différentes |
| `ExcelExportManager` | il faut réunir capture dashboard + exports actuels |
| `AnimationMessagesManager` | conserver impérativement `traiterPipelinePrevisionDataCo()` du maître |
| `ordonnancerProduction()` | changement de comportement majeur ; validation A/B nécessaire |
| `stockProduitFiniDisponibleTotal()` | la version maître multi-produit doit rester source de vérité |
| `arreterSimulation()` | réunir export ABox/Excel/final snapshot avec états Forecast |
| `routerEntite()` | intégrer le suivi de durée client sans casser le routage actuel |
| `rebuter()` | porter uniquement le rattachement strict `fluxAppartientACommande()` |

### Ne pas reprendre tel quel

- `seqCommandeClient` : redondant avec la solution maître plus récente ;
- `verifierFillRate()` version collègue : elle garde une sémantique historique sur `commandes.size()` ; le PI collègue lui-même ne s'y fie plus. La version maître, limitée aux commandes clientes closes, est plus saine ;
- `stockProduitFiniDisponibleTotal()` collègue : incompatible avec la source de vérité multi-produit du maître ;
- constantes d'engagement ZENER 4 h / 8 h / 24 h : à rendre compatibles avec le mode DataCo et ses délais promis ;
- logique de lancement de première commande démonstrative du collègue : ne doit jamais réactiver des commandes aléatoires/démo en mode DataCo.

## 9. Ordre recommandé pour la fusion

1. Créer une copie de la version maître actuelle.
2. Porter les classes/variables et helpers C15 sans conflit (PI, retard, rattachement strict, normalisation, dashboard).
3. Porter `calculerPIGlobal()` et ses dépendances, puis compiler.
4. Porter les correctifs holoniques C14.52-C14.55, puis compiler.
5. Fusionner manuellement `demarrerSimulation`, `genererCommande`, `finDeParcours`, `routerEntite`, exports et JSON, en préservant DataCo/multi-produit.
6. Ajouter historique Dashboard / Excel.
7. Tester scénario maître DataCo 2017 (365 commandes) pour non-régression Forecast/Recalibrator.
8. Tester ZENER nominal 45 commandes.
9. Tester ZENER perturbé +200 unités.
10. Comparer PI/RL/RS et vérifier que les stocks multi-produit / Forecast restent inchangés.

## 10. Conclusion

Les travaux du collègue ne sont pas une simple évolution UI : ils constituent une seconde branche importante centrée sur **la validité scientifique du PI SCOR, la détection des retards, la robustesse des métriques, la traçabilité des runs et la validation statistique nominal/perturbé**.

Notre branche maître est plus avancée sur **Forecast/DataCo, Recalibrator, multi-produit et politiques de stock**.

Les deux branches sont donc très complémentaires, mais elles ont divergé dans plusieurs fonctions centrales. Une substitution brute du `.alp` collègue ferait perdre les fonctionnalités DataCo récentes. La bonne stratégie est une fusion sémantique contrôlée, fonction par fonction, avec compilation et run de non-régression à chaque lot.
