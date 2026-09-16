# CLAUDE.md — Mission de fusion SCONTO-SVU Generic

## Mission

Fusionner progressivement dans `model/SCONTO_SVU_GENERIC_MASTER.alp` les avancées génériques pertinentes de la version collègue `reference/colleague/SCONTO_SVU_GENERIC10-4_COLLEAGUE.alp`.

La cible est un **moteur AnyLogic générique**, piloté par scénarios JSON, et non une version spécialisée DataCo.

## Sources de vérité

1. **Master à préserver** : `model/SCONTO_SVU_GENERIC_MASTER.alp`.
2. **Donneur fonctionnel** : `reference/colleague/SCONTO_SVU_GENERIC10-4_COLLEAGUE.alp`.
3. **Historique et intention du collègue** : `reference/colleague/docs/*.md`.
4. **Analyse préalable de fusion** : `docs/merge/*.md`.

Ne jamais remplacer le master complet par le donneur. Porter les changements sélectivement et expliquer chaque différence.

## Lecture obligatoire avant toute modification

Lire dans cet ordre :

1. `reference/colleague/docs/CLAUDE.md`
2. `reference/colleague/docs/PROJECT_OVERVIEW.md`
3. `reference/colleague/docs/MODEL_STRUCTURE.md`
4. `reference/colleague/docs/SCENARIOS_AND_DATA.md`
5. `reference/colleague/docs/DOCUMENTATION_SCENARIOS_VALIDATION.md`
6. `reference/colleague/docs/ARBRE_PI_SCOR.md`
7. `docs/merge/ANALYSE_FUSION_COLLEGUE_VS_MASTER.md`
8. `docs/merge/PHASE1_MERGE_NOTES.md` et `PHASE2_PI_SCOR_MERGE_NOTES.md` si présents.

**Attention :** les documents du collègue peuvent être en retard sur son code. En cas de contradiction, relever explicitement l'écart et vérifier l'implémentation dans le `.alp` donneur.

## Interdiction : ne pas injecter DataCo dans le noyau générique

Ne pas ajouter au master générique les éléments spécialisés DataCo, notamment :

- Prophet 2017 et ses fichiers de prévision ;
- Recalibrator DataCo ;
- AutoCommande DataCo ;
- mode `DATACO` / replay DataCo ;
- bornage calendrier forcé à 2017 ;
- vues et histogrammes DataCo spécifiques ;
- noms de produits `DATACO_SPORTS`, `DATACO_CLOTHING`, `DATACO_ELECTRONICS` codés en dur ;
- ressources Excel DataCo codées en dur.

Le noyau générique peut conserver/recevoir des **capacités génériques** utiles à DataCo (multi-produit générique, stocks par produit, prévision abstraite, interfaces d'extension), mais sans connaissance métier DataCo codée dans le moteur.

## Règle ZENER

ZENER est un **scénario de validation**, pas le comportement codé en dur du moteur. Tout ce qui peut être porté dans `scenario_ZENER_*.json` doit rester configurable par JSON. Ne pas ajouter de constante spécifique ZENER dans le noyau sauf nécessité technique déjà structurée dans le modèle, et la signaler si elle existe.

## Plan de fusion

### Bloc A — corrections sûres
- matching strict flux/commande (`CMD_4` ne doit pas matcher `CMD_44`) ;
- diagnostics commandes bloquées ;
- détail stock matière par matière/unité ;
- historique Dashboard et export Excel ;
- cohérence des états holoniques / `etatCoordinateurMacro()`.

### Bloc B — PI / SCOR
- warm-up / amorçage ;
- attributs réellement disponibles et poids effectifs ;
- seuil d'échantillon RL ;
- normalisation RS lente/hyperbolique ;
- codes SCOR vs proxies ;
- périmètre entreprise focale ;
- `calculerPIGlobal()` et fonctions auxiliaires.

### Bloc C — retards / engagement client
- détection continue des retards ;
- `retardConstate`, `modeEngagementClient`, `dureeClientAccumulee` ;
- événement périodique ;
- engagements **configurables/génériques**, jamais spécifiques DataCo.

### Bloc D — moteur conflictuel
- `demarrerSimulation()` ;
- `genererCommande()` ;
- `finDeParcours()` ;
- `routerEntite()` ;
- `rebuter()` ;
- chargement/sauvegarde JSON ;
- exports.

### Bloc E — ordonnancement
Comparer l'ordonnancement du collègue avec le master. Ne pas libérer aveuglément tout le carnet si cela peut faire exploser le WIP. Proposer une stratégie générique et configurable, puis attendre validation avant modification lourde.

## Workflow Git obligatoire

- Ne jamais travailler directement sur `main`.
- Branche de travail recommandée : `integration/claude-generic-merge`.
- Un commit cohérent par bloc fonctionnel.
- Après chaque commit, mettre à jour `MERGE_PROGRESS.md`.
- Pousser la branche après chaque bloc validé statiquement.
- Ne pas merger vers `main` sans validation humaine du Build AnyLogic et du run court.

## Contrôles après chaque modification

Au minimum :

1. XML bien formé ;
2. IDs AnyLogic uniques ;
3. pas de références cassées aux agents/fonctions ;
4. pas de duplication de fonction/variable/event ;
5. pas de nouveau hard-code DataCo/ZENER ;
6. comparaison des fonctions modifiées avec master et donneur ;
7. journal des modifications ;
8. indiquer ce qui nécessite un Build/run AnyLogic manuel.

## Sortie attendue à chaque bloc

Produire un résumé :

- fichiers/objets modifiés ;
- fonctions/variables/events ajoutés ou fusionnés ;
- comportement conservé du master ;
- comportement importé du collègue ;
- conflits rencontrés et choix effectués ;
- risques ;
- protocole de test manuel AnyLogic.
