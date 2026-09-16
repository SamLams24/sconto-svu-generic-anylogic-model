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
