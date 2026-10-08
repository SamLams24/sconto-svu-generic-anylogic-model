# Fusion collègue → maître — Phase 2 PI / SCOR

## Base

- Base maître : `SCONTO_SVU_MASTER_MERGE_COLLEAGUE_PHASE1.alp`
- Branche de référence collègue : `2b60802a-13a7-434c-b6a8-800367784b62.alp`
- Sortie : `SCONTO_SVU_MASTER_MERGE_COLLEAGUE_PHASE2_PI_SCOR.alp`

## Diagnostic du test Phase 1

Le chargement du JSON DataCo configure la chaîne logistique (acteurs, produits, matières, scénarios, stocks) mais **n'active pas** le mode de génération `DATACO`.

Ainsi, avec le JSON DataCo chargé mais le switch DataCo désactivé :

- `modeGenerationDemandes` reste `TEST` ;
- `autoCommandeDataCoActive` reste `false` ;
- la date n'est pas forcée au 01/01/2017 ;
- Prophet/Recalibrator ne pilotent pas le replay ;
- en revanche `modeMultiProduitActif=true` et `rotationProduitsActive=true` proviennent du JSON ;
- les commandes de test utilisent donc les scénarios `DATACO_SPORTS`, `DATACO_CLOTHING`, `DATACO_ELECTRONICS` et leurs matières.

Les logs `Q* MAT_CLOTHING`, `Q* MAT_ELECTRONICS` sont donc attendus. Ils appartiennent à la politique de stock/MRP du scénario chargé, pas au mode AutoCommande DataCo.

## Anomalie maître détectée pendant ce test

Le log stratégique contenait par exemple :

`stock=53928/...`

alors que le stock multi-produit agrégé était voisin de 17 976. Le rapport est exactement x3 : la boucle stratégique parcourait les trois scénarios produit mais lisait à chaque fois `niveauStock` du même poste M1.5, qui contient désormais le **stock agrégé**.

Correction Phase 2 :

```java
PosteGenericAgent stockFini = main.trouverStockFiniPourScenario(sc);
double stockObserve = main.modeMultiProduitActif
    ? main.stockFiniDisponiblePourScenario(sc, stockFini)
    : ((stockFini != null) ? stockFini.niveauStock : 0);
```

Le total stratégique redevient la somme des trois stocks par produit, sans triple comptage.

## Fusion PI / SCOR

### `StrategicAgent.calculerPIGlobal()`

La logique de la branche collègue a été portée avec notamment :

- périmètre du PI limité à l'entreprise focale ;
- reconstruction des bundles Source / Make / Deliver / Return à partir des postes de l'entreprise focale ;
- Reliability pondérée uniquement sur une mesure réellement observable (`RL.2.2`) ;
- exclusion du PI des mesures informatives qui ne disposent pas de données indépendantes ;
- cycle macro-processus calculé avec traitement + attente ;
- bornes RS nominales construites depuis le chemin réellement emprunté ;
- CO calculé avec les unités réellement livrées et non un compteur hybride ;
- utilisation explicite de proxies pour stabilité du débit et disponibilité machine ;
- poids PI effectifs : un attribut sans données n'est pas interprété comme une performance nulle ;
- phase d'amorçage : PI maintenu à la cible tant que le périmètre de mesure n'est pas comparable ;
- logs `[SCOR-DETAIL]` pour expliquer la décomposition RL/RS/AG/CO/AM.

### `StrategicAgent.prevoirDemande()`

La prévision de demande stratégique ne dépend plus de la production terminée. Elle est calculée depuis les **commandes clientes créées**, hors `REAPPRO_`, globalement et par produit.

Cela supprime la boucle de rétroaction :

`production autonome -> nbTermines -> prévision -> stock cible -> davantage de production`.

Le lissage exponentiel alpha=0,3 est conservé, avec un garde-fou d'au moins deux commandes pour former un débit observé.

## RS / normalisation

Ajout de la fonction :

```java
double dureeTraitementNominale(PosteGenericAgent p)
```

Les profils explicites suivants sont disponibles :

- `PROXY.AG.STABILITE_DEBIT`
- `PROXY.AM.DISPONIBILITE_MACHINE`
- `PROXY.AG.SYSTEM_UTILIZATION`

Les codes SCOR historiques `AG.1.1` et `AM.3.9` sont conservés dans les profils legacy pour compatibilité, mais la nouvelle logique PI ne les revendique plus pour des grandeurs qui ne correspondent pas à leur définition SCOR.

## Cohérence des exports SCOR

Ont également été synchronisées avec la nouvelle sémantique :

- `codesProcessusPourMetriqueSCOR()` ;
- `valeurRuntimeMetriqueSCOR()` ;
- `uniteMetriqueSCOR()` ;
- `sourceFormuleMetriqueSCOR()`.

## Préservé sans modification

- Prophet ;
- Recalibrator ;
- AutoCommande DataCo ;
- borne stricte 2017 ;
- `stockFiniParProduit` ;
- rotation SPORTS / CLOTHING / ELECTRONICS ;
- politique REAPPRO multi-produit ;
- correctif `ConcurrentModificationException` ;
- historique Dashboard ajouté en Phase 1.

## Vérifications statiques

- XML `.alp` valide ;
- 1 848 IDs ;
- 1 848 IDs uniques ;
- aucune collision d'ID ;
- fonctions Forecast/DataCo toujours présentes ;
- fonctions PI/SCOR Phase 2 présentes ;
- aucune dépendance Phase 3 (`retardConstate`, engagements client continus) introduite prématurément.

## Test recommandé

1. Build AnyLogic.
2. Charger le JSON DataCo.
3. Laisser le mode DataCo désactivé et lancer un court run TEST : vérifier que `stock=` stratégique est voisin du stock agrégé réel, pas x3.
4. Vérifier `[SCOR-DETAIL]` et la phase `AMORCAGE`.
5. Vérifier la feuille `Historique Dashboard` et les colonnes `Attributs pondérés dans le PI` / `Somme des poids effectifs`.
6. Ensuite seulement tester un court run avec le mode DataCo activé.
