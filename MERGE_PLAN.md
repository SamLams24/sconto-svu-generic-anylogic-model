# Plan de fusion — Generic master ← branche collègue

## Architecture de versions

Le projet comporte deux lignées distinctes :

1. **SCONTO-SVU Generic** : moteur principal, configurable par JSON, utilisable pour ZENER et d'autres chaînes.
2. **SCONTO-SVU DataCo** : adaptation expérimentale spécialisée, dérivée du générique, contenant Forecast/Prophet/Recalibrator/AutoCommande/replay DataCo et ressources propres à DataCo.

Le merge actuel concerne **uniquement la lignée Generic**.

## Stratégie

La version collègue est utilisée comme donneur de fonctionnalités. Elle ne devient pas automatiquement la base. Chaque fonction modifiée doit être comparée avec le master générique, puis portée en préservant la configurabilité.

## Validation

Après chaque bloc : validation statique par Claude Code, push Git, revue, puis Build/run AnyLogic manuel. Les résultats manuels sont consignés dans `MERGE_PROGRESS.md` avant de passer au bloc suivant.

## Ordre des blocs

1. **Bloc A — corrections sûres** : A.1 matching strict flux/commande, A.2 diagnostic
   commandes bloquées, A.3 stock matière détaillé, A.4 historique Dashboard/Excel,
   A.5 cohérence des états holoniques.
2. **Bloc M — fondation multi-produit Generic** (décision du 2026-09-16, ajoutée après
   A.1/A.2, avant B) : audit de la fondation multi-produit déjà présente dans le master
   (`modeMultiProduitActif`, `stockFiniParProduit`, etc.), portage sélectif de
   mécanismes génériques depuis la référence technique
   `reference/dataco-multiproduct/` (jamais les éléments spécifiques DataCo — Prophet,
   Recalibrator, AutoCommande, 2017, catalogue produits DataCo), sous 13 invariants et
   10 tests M-1 à M-10. Détail complet dans `MERGE_PROGRESS.md`. Placé avant le Bloc B
   car le multi-produit influence stocks/demande/réappro/Make/stratégique/KPI, dont
   dépend la refonte PI/SCOR.
3. **Bloc B — PI / SCOR** : warm-up, poids effectifs, RL/RS, proxies SCOR explicites,
   périmètre entreprise focale, `calculerPIGlobal()`.
4. **Bloc C — retards / engagement client** : détection continue, à composer avec le
   mécanisme de délai déjà présent dans le master.
5. **Bloc D — moteur conflictuel** : fusion manuelle fonction par fonction
   (`demarrerSimulation`, `genererCommande`, `finDeParcours`, `routerEntite`, JSON,
   exports).
6. **Bloc E — ordonnancement MTO** : RISKY, isolé, test A/B avant tout portage, jamais
   mélangé à un autre bloc.
