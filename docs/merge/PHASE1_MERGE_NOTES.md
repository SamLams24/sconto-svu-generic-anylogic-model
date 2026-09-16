# Fusion collègue → maître — Phase 1

Base maître : `SCONTO_SVU_FINAL_VALIDATED_FORECAST_DATACO_MULTIPRODUCT_CONCURRENT_FIX.alp`

Sortie : `SCONTO_SVU_MASTER_MERGE_COLLEAGUE_PHASE1.alp`

## Éléments fusionnés

1. **Rattachement strict flux → commande**
   - ajout de `fluxAppartientACommande(idFlux,idCommande)` ;
   - remplacement des deux usages fragiles de `contains()` dans la fin de parcours et le rebut.

2. **Diagnostic des commandes bloquées**
   - ajout de `diagnostiquerCommandesBloquees()` ;
   - événement `diagnosticPeriodiqueCommandes` toutes les 60 s de simulation ;
   - diagnostic uniquement, aucune mutation du statut ou du routage.

3. **Historique Dashboard**
   - `historiqueDashboard` ;
   - `capturerPointHistoriqueDashboard()` ;
   - `historiqueDashboardColumns()` / `historiqueDashboardRows()` ;
   - remise à zéro à chaque démarrage ;
   - capture initiale + capture automatique à chaque export ;
   - nouvelle feuille Excel `Historique Dashboard`.

4. **Stock matière détaillé**
   - ajout `detailStockMatiereParMatiere()` ;
   - le stock fini de l'historique utilise `stockProduitFiniDisponibleTotal()` pour respecter la source de vérité multi-produit.

5. **Fondations PI / SCOR**
   - champs de périmètre PI ajoutés au StrategicAgent (`attributsPonderesPI`, `sommePoidsEffectifsPI`, etc.) ;
   - `nombreCommandesClosesFiabilite()` ;
   - `unitesLivreesClients()` ;
   - pas encore de remplacement de `calculerPIGlobal()` : prévu en Phase 2.

6. **Fondation RS / normalisation**
   - extension backward-compatible de `NormalizationProfile` avec `decroissanceLente` ;
   - surcharge de constructeur ;
   - décroissance hyperbolique optionnelle pour les métriques COST ;
   - `majBorneCycleMacro()` ;
   - persistance JSON du champ `decroissanceLente`.

7. **Cohérence des coordinateurs holoniques**
   - ajout `etatCoordinateurMacro()` comme source unique ;
   - `couleurSupervisorMacro()` et `popupSupervisor()` raccordés à cette même source ;
   - popup basé sur les compteurs réellement alimentés par la génération 2.

## Éléments explicitement préservés du maître

- Prophet / DataCo / Recalibrator ;
- vue Prévisions et graphiques ;
- AutoCommande 2017 ;
- multi-produit Sports / Clothing / Electronics ;
- `stockFiniParProduit` comme source de vérité ;
- dépendances commande ↔ REAPPRO ;
- perturbations fournisseur / manifeste ;
- correction de concurrence `C14.68` (snapshot de `listeProduits`).

## Non fusionné en Phase 1

- refonte complète de `calculerPIGlobal()` ;
- détection continue des retards / engagement client ;
- réécriture `ordonnancerProduction()` ;
- modifications comportementales majeures du moteur.

## Validation statique effectuée

- XML parsé correctement ;
- 1848 IDs / 1848 IDs uniques ;
- aucun doublon d'ID ;
- protections Forecast, multi-produit et concurrence toujours présentes.

## Test AnyLogic recommandé

1. Build uniquement.
2. Charger le JSON DataCo V2.
3. Démarrer un run court (quelques jours simulés).
4. Vérifier l'absence d'exception.
5. Vérifier les logs `[DIAG-BLOQUEE]` toutes les 60 s seulement si des commandes sont encore en cours.
6. Ouvrir l'Excel exporté et vérifier la feuille `Historique Dashboard`.
7. Vérifier que le mode DataCo, Prophet/Recalibrator et la rotation multi-produit restent inchangés.
