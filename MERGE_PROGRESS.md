# MERGE_PROGRESS

## État initial

- [x] Repository propre initialisé depuis la baseline générique validée (2026-09-16)
- [x] Branche `integration/claude-generic-merge` créée
- [x] Documentation collègue lue
- [x] Diff structurel master ↔ collègue produit (voir §Audit structurel ci-dessous)

## Divergence documentaire détectée (2026-09-16)

`docs/merge/ANALYSE_FUSION_COLLEGUE_VS_MASTER.md`, `PHASE1_MERGE_NOTES.md` et
`PHASE2_PI_SCOR_MERGE_NOTES.md` décrivent une fusion **antérieure et différente** :
leur "maître" est `SCONTO_SVU_FINAL_VALIDATED_FORECAST_DATACO_MULTIPRODUCT_CONCURRENT_FIX.alp`
(lignée DataCo : Prophet, Recalibrator, AutoCommande 2017, multi-produit
Sports/Clothing/Electronics), explicitement listé dans ces notes comme "éléments du
maître à préserver absolument". Ce n'est **pas** `model/SCONTO_SVU_GENERIC_MASTER.alp`,
la cible de la présente mission (Generic uniquement).

Vérification effectuée :
- `model/SCONTO_SVU_GENERIC_MASTER.alp` : 2 242 148 octets, **0 occurrence** de
  `DATACO_SPORTS|DATACO_CLOTHING|DATACO_ELECTRONICS|Prophet|Recalibrator|AutoCommande` —
  confirmé comme modèle générique pur, sans dépendance DataCo.
- `reference/colleague/SCONTO_SVU_GENERIC10-4_COLLEAGUE.alp` : SHA-256
  `43552932ba9f9cfa86591a1a41c6f7cd6c72d4d7bbc64b3e12f57b996284bbcf`, identique au
  fichier `.alp` analysé dans `ANALYSE_FUSION_COLLEGUE_VS_MASTER.md` (même hash). Le
  contenu technique de cette analyse (ce que le collègue a changé : PI/SCOR,
  `fluxAppartientACommande`, historique dashboard, etc.) reste donc valide et a été
  réutilisé. En revanche, les sections "quoi fusionner où" et "à préserver dans le
  maître" de ces 3 docs ne s'appliquent pas ici : elles ont été **recalculées à neuf**
  ci-dessous contre le vrai master Generic.
- `PROJECT_OVERVIEW.md`/`MODEL_STRUCTURE.md` du collègue (`reference/colleague/docs/`)
  décrivent eux-mêmes un modèle générique pur (cas ZENER SA Togo), cohérent avec le
  hash ci-dessus — aucune contradiction de ce côté.

**Conclusion** : ces 3 fichiers `docs/merge/*.md` sont conservés comme référence
historique du delta fonctionnel collègue, mais ne doivent pas être utilisés comme
guide de "ce qu'il faut préserver dans le master" pour la lignée Generic.

## Audit structurel master ↔ collègue (2026-09-16)

Comparaison XML directe (`ActiveObjectClass`, `Function`/`Body`, `Variable`, `Event`,
compte d'`Id`) entre `model/SCONTO_SVU_GENERIC_MASTER.alp` (2 242 148 octets, 1675 Id
uniques, 334 fonctions, 253 variables) et
`reference/colleague/SCONTO_SVU_GENERIC10-4_COLLEAGUE.alp` (2 290 956 octets, 1685 Id
uniques, 337 fonctions, 258 variables).

**Classes actives** : identiques des deux côtés (`Main`, `PosteGenericAgent`,
`FluxEntity`, `CommandeAgent`, `StrategicAgent`, `TacticalAgent`, `OperationalAgent`,
`CoordinatorAgent`, `BlackboardAgent`, `Movable`) — aucune classe ajoutée/supprimée.

**Fonctions AnyLogic (`<Function>`) uniquement côté collègue (3)** :
- `etatCoordinateurMacro()` — SAFE (source unique couleur+popup Coordinateur)
- `nombreCommandesClosesFiabilite()` — SAFE (support RL)
- `unitesLivreesClients()` — SAFE (assiette CO.1.1 correcte)

**Fonctions communes au corps différent (39)** — classées :

| Fonction | Classe | Delta | Catégorie |
|---|---:|---|---|
| `finDeParcours` | Bug matching CMD_N/CMD_NM (`.contains` fragile) | **SAFE — PORTÉ (ce bloc)** |
| `rebuter` | idem, chemin rebut | **SAFE — PORTÉ (ce bloc)** |
| `calculerPIGlobal` | 12,4k→29,4k car., refonte warm-up/poids effectifs/proxies | RISKY — Bloc B |
| `prevoirDemande` | découplage de la production terminée | ADAPT — Bloc B (déjà partiellement porté côté master ?) |
| `ajusterDebits`, `analyserEtat` | logique goulot/holonique liée au PI | ADAPT — Bloc B/A |
| `couleurSupervisorMacro`, `popupSupervisor`, `popupOperationalAgent` | cohérence état holonique (C14.52-55) | SAFE — Bloc A (suite) |
| `tauxCommandesLivreesCloses`, `verifierFillRate` | sémantique RL/Fill Rate | ADAPT — Bloc B |
| `codesProcessusPourMetriqueSCOR`, `valeurRuntimeMetriqueSCOR`, `uniteMetriqueSCOR`, `sourceFormuleMetriqueSCOR` | cohérence exports SCOR avec nouveau PI | ADAPT — Bloc B (dépend de calculerPIGlobal) |
| `ordonnancerProduction` | libère tout le carnet MTO sans porte goulot | **RISKY — Bloc E, isolé, ne pas mélanger** |
| `chargerScenarioJSON`, `chargerConfig`, `demarrerSimulation`, `genererCommande`, `routerEntite`, `exporterToutesLesTablesExcel`, `arreterSimulation` | schémas/flux propres à chaque lignée, tailles proches | ADAPT — Bloc D, fusion manuelle fonction par fonction |
| `dashboardGlobalColumns/Rows`, `dashboardMicroColumns/Rows`, `kpiParPosteColumns/Rows`, `nonRegressionRows`, `tableDashboardGlobalText`, `tableDashboardMacroSCORText`, `getRapportVSM`, `kpiCliValFunction`, `kpiLogisticsText`, `pceGlobalText`, `tauxCommandesConformes`, `exporterCSV` | tables/exports dashboard, deltas mineurs de libellés/colonnes | ADAPT — à revoir avec Bloc Historique Dashboard |
| `logEvent` | 160 car. (master) vs 1245 car. (collègue) | À examiner — Bloc A candidat (traçabilité) |

**Variables ajoutées côté collègue (15)**, toutes liées à PI/SCOR/retards — Bloc B/C :
`attributsPonderesPI`, `sommePoidsEffectifsPI`, `seuilMinEchantillonRL`,
`perimetrePIDejaComplet`, `plafondMultipleDebitBase`, `facteurToleranceCycleMacro`,
`dernierLogDetailSCOR`, `donneesRLPresentesPrecedent`, `donneesRSPresentesPrecedent`,
`donneesAMPresentesPrecedent`, `retardConstate`, `modeEngagementClient`,
`dureeClientAccumulee`, `compteurCyclesExportExcel`, `verboseLogs`.

**Variables présentes uniquement côté master (10)** — mécanisme de suivi de délai déjà
existant dans le master, distinct de celui du collègue, à ne pas écraser :
`attenteStockOuverte`, `tDebutAttenteStock`, `tFinAttenteStock`,
`dureeAttenteStockReelleSec`, `dureeTraitementClientReelleSec`,
`dureeReapproImputeeReelleSec`, `leadTimeClientReelSec`, `ordresReapproLies`,
`ordresReapproImputes`, `commandesClientesCouvertes`. **Point d'attention pour le
Bloc C** : le master a déjà sa propre logique de temps d'attente/engagement — le
portage de `retardConstate`/`modeEngagementClient` du collègue devra composer avec
elle, pas la remplacer.

**Événements** : le collègue ajoute `bilanPeriodique` (60 s — détection retards +
diagnostic commandes bloquées) ; absent du master — Bloc A/C.

**Fonctions embarquées hors `<Function>` AnyLogic** (code Java libre dans les blocs
`Body`/sections de classe, invisibles à l'inventaire `<Function>`) :
- `fluxAppartientACommande(idFlux, idCommande)` — présent 4× dans le collègue (déf. +
  3 usages/mentions), absent du master. **Confirmé bug réel dans le master** avant ce
  bloc : `refCommandeFlux.contains(cmd.idCommande)` (ligne ~11736) et
  `e.idFlux.contains(cmdRebut.idCommande)` (ligne ~12777) — `"CMD_44_F_12".contains("CMD_4")`
  est vrai, donc les unités de `CMD_44` étaient créditées à `CMD_4`.
- `diagnostiquerCommandesBloquees()` / trace `[DIAG-BLOQUEE]` — présents chez le
  collègue, absents du master. Bloc A, prochain sous-bloc.
- Deux usages de `.contains(cmd.idCommande)` restants dans le master
  (`commandesClotureesTracees`, `aerCommandesRetardTracees`, lignes ~5791/~22836) sont
  des `HashSet<String>.contains()` (appartenance exacte à un ensemble d'IDs déjà
  traités), **pas** liés au bug de sous-chaîne — volontairement non touchés.

## Bloc A — corrections sûres
- [x] Matching strict flux/commande — **PORTÉ** (2026-09-16, commit `bf0e490`, Build/run utilisateur OK)
- [x] Diagnostic commandes bloquées — **PORTÉ ET VALIDÉ FONCTIONNELLEMENT** (2026-09-16/17, commit `0363b6b`, `[DIAG-BLOQUEE]` observé réellement sur `REAPPRO_1`)
- [x] Stock matière détaillé — **PORTÉ ET VALIDÉ** (2026-09-16, commit `d52d431`, consommé et validé via le Bloc A.4)
- [x] Historique Dashboard / Excel — **TERMINÉ / FIGÉ** (2026-09-16/17, commits `69c78d6`…`0da7d92`, `e32fbed` ; voir "Validation utilisateur définitive — Bloc A.4" ci-dessous)
- [x] États holoniques cohérents — **PORTÉ ET VALIDÉ** (2026-09-17, commit `e7652ed`, Coordinateur ESCALADE réel observé et justifié par un vrai goulot Make, non-régression A.4 confirmée)
- [ ] Build AnyLogic utilisateur
- [ ] Run court générique utilisateur

### Journal — Bloc A.1 : matching strict flux/commande (2026-09-16)

- **Source** : `reference/colleague/SCONTO_SVU_GENERIC10-4_COLLEAGUE.alp`, fonction
  `fluxAppartientACommande` (lignes ~7722-7728 du fichier collègue, correctif `C15.28`).
- **Fichier modifié** : `model/SCONTO_SVU_GENERIC_MASTER.alp`.
- **Fonctions/variables touchées** :
  - ajout `boolean fluxAppartientACommande(String idFlux, String idCommande)` (nouvelle
    méthode Java libre, insérée dans `Main`, juste avant `definirIdentiteMovable`) ;
  - `finDeParcours()` : remplacement de
    `refCommandeFlux.contains(cmd.idCommande)` par
    `fluxAppartientACommande(refCommandeFlux, cmd.idCommande)` ;
  - `rebuter()` : remplacement de `e.idFlux.contains(cmdRebut.idCommande)` par
    `fluxAppartientACommande(e.idFlux, cmdRebut.idCommande)`.
- **Décision** : portage à l'identique de la logique collègue (égalité stricte ou
  préfixe suivi de `"_"`), sans reprendre son commentaire/numérotation `C15.28`
  (renumérotation interne collègue non pertinente pour Generic) ; commentaire réécrit
  pour expliquer le bug en français dans le style du master.
- **Incompatibilités** : aucune — signature de fonction nouvelle, aucun appelant
  existant cassé, comportement identique à l'égalité exacte (cas `idFlux==idCommande`)
  et strictement plus correct sur les préfixes.
- **Éléments non fusionnés dans ce bloc** : `diagnostiquerCommandesBloquees()` et
  l'événement `bilanPeriodique` (diagnostic seul, sans mutation d'état) — prévus pour
  le sous-bloc A.2, afin de garder un commit à responsabilité unique.
- **Validations statiques** :
  - XML bien formé (`xml.etree.ElementTree`) : OK.
  - IDs AnyLogic : 1675/1675 uniques, inchangé (aucun élément `<Function>`/`<Variable>`
    AnyLogic ajouté, seulement du code Java libre dans un `Body` existant).
  - `git diff --check` : aucune erreur d'espace blanc.
  - Grep DataCo (`DATACO_*|Prophet|Recalibrator|AutoCommande`) sur
    `model/SCONTO_SVU_GENERIC_MASTER.alp` : 0 occurrence, avant et après.
  - Les 2 usages restants de `.contains(cmd.idCommande)` dans le master
    (`commandesClotureesTracees`, `aerCommandesRetardTracees`) vérifiés comme
    `HashSet<String>.contains()` (membership exact), non concernés par le bug,
    volontairement non modifiés.
- **Build AnyLogic** : **OK** (0 erreur, validé par l'utilisateur, 2026-09-16).
- **Run** : **OK** — run nominal Generic/ZENER, aucune exception observée,
  comportement des commandes et flux cohérent (validé par l'utilisateur, 2026-09-16).
- **Commit** : `bf0e490` (message `fix(generic): strict command-flow matching`).

## Bloc A — corrections sûres (suite)

### Journal — Bloc A.2 : diagnostic des commandes bloquées (2026-09-16)

**Analyse préalable (collègue)** :
- `diagnostiquerCommandesBloquees()` (collègue, ~ligne 7770, correctif `C15.29`) :
  parcourt `commandes`, ne retient que les commandes au statut `EN_COURS`/`EN_LIVRAISON`,
  compare `produitsTerminesParCommandeRuntime.get(idCommande)` à `cmd.qte`, et journalise
  l'écart via `board.logEvent("[DIAG-BLOQUEE] ...")`. Aucune écriture d'état : ni
  `cmd.statut`, ni stock, ni production, ni PI, ni routage — confirmé purement
  observateur à la lecture du code (seules opérations : lecture de champs + `Map.get` +
  `logEvent`, le tout dans un `try { } catch (Throwable ignored) {}`).
  La seule variable qu'elle lit et qui n'existe pas dans le master est
  `cmd.retardConstate` (mécanisme de retard du collègue, Bloc C).
- Événement `bilanPeriodique` (collègue, `Main`, cyclique 60 s, condition
  `modeExecution`) : son `Action` **mélange trois responsabilités** :
  1. `evaluerRetardsCommandesOuvertes()` — détection continue des retards / engagement
     client → appartient au **Bloc C**, non portée ici ;
  2. `diagnostiquerCommandesBloquees()` — diagnostic pur → **Bloc A.2, porté** ;
  3. `logBilanCommandes()` — bilan agrégé `[BILAN]` (commandes total/livrées/bloquées/
     refusées, client vs réappro) — fonction **absente du master**, non demandée pour ce
     bloc, non portée (aucun événement périodique équivalent n'existe déjà dans le
     master ; ajoutée seule elle introduirait une fonctionnalité hors du périmètre
     validé pour A.2).
  - Périodicité : 60 s, `OccurrenceDate=1781078400000` — valeur identique à celle déjà
    utilisée par les événements cycliques existants du master (`snapshotWIP`, etc.),
    donc convention générique du modèle, pas une date ZENER codée en dur.
  - Dépendances vérifiées présentes dans le master avant portage : `commandes`,
    `produitsTerminesParCommandeRuntime`, `board` (type `BlackboardAgent`, méthode
    `logEvent(String)` déjà présente), champs `CommandeAgent.idCommande/statut/
    typeCommande/qte/tCreation`.
- **Décision de séparation** : le bloc A.2 ne porte que `diagnostiquerCommandesBloquees()`
  et un événement `bilanPeriodique` dont l'`Action` n'appelle **que** cette fonction.
  `evaluerRetardsCommandesOuvertes()` et `logBilanCommandes()` restent à porter
  respectivement au Bloc C et à une décision ultérieure explicite.

**Fichier modifié** : `model/SCONTO_SVU_GENERIC_MASTER.alp`.

**Fonctions/variables/événements touchés** :
- ajout `void diagnostiquerCommandesBloquees()` dans `Main` (juste après
  `fluxAppartientACommande`, avant `definirIdentiteMovable`) — copie fonctionnelle du
  collègue, avec la ligne de log amputée de `| retardConstate=" + cmd.retardConstate`
  (champ inexistant dans ce master, Bloc C) ;
- ajout de l'événement `Main.bilanPeriodique` (cyclique 60 s, condition
  `modeExecution`, IDs `1791000009401`/`1791000009402` réutilisés du collègue — aucune
  collision constatée dans le master), `Action` = appel unique à
  `diagnostiquerCommandesBloquees();`, avec commentaire explicite indiquant que
  `evaluerRetardsCommandesOuvertes()` et `logBilanCommandes()` sont volontairement hors
  périmètre.

**Ce qui a été porté** : le diagnostic pur des commandes bloquées, journalisé toutes les
60 s de simulation via `[DIAG-BLOQUEE]`, sans aucune incidence sur l'état de simulation.

**Ce qui a été adapté** : suppression de la référence à `cmd.retardConstate` (absent du
master) dans la ligne de log, sans quoi le code n'aurait pas compilé.

**Ce qui n'a pas été porté (et pourquoi)** :
- `evaluerRetardsCommandesOuvertes()` + champ `retardConstate` + `modeEngagementClient`
  + `dureeClientAccumulee` → Bloc C, à composer avec le mécanisme de délai déjà présent
  dans le master (`attenteStockOuverte`, `leadTimeClientReelSec`, etc., cf. audit
  structurel ci-dessus) ;
- `logBilanCommandes()` (bilan `[BILAN]` agrégé) → fonctionnalité utile mais hors
  périmètre explicitement demandé pour A.2 ; à proposer séparément si souhaité.

**Incident constaté et corrigé pendant ce bloc** : après édition, `git diff` faisait
apparaître un changement non intentionnel et non expliqué du champ interne
`Model/Name` (`SCONTO_SVU_FINAL_VALIDATED` → `SCONTO_SVU_GENERIC_MASTER`), sans lien
avec les modifications demandées et non issu d'une commande explicite de cette session.
Par prudence, cette ligne a été restaurée à sa valeur committée avant tout commit,
pour garder ce bloc strictement single-responsibility. À surveiller sur les prochains
blocs.

**Validations statiques** :
- XML bien formé (`xml.etree.ElementTree`) : OK.
- IDs AnyLogic : 1677/1677 uniques (+2 par rapport à A.1, correspondant aux deux
  `<Id>` de l'événement `bilanPeriodique` ; aucun doublon).
- `git diff --check` : aucune erreur d'espace blanc.
- `git diff --stat` : 73 insertions, 0 suppression (confirme l'absence de régression
  ailleurs dans le fichier, notamment sur le champ `Model/Name` après restauration).
- Grep DataCo (`DATACO_*|Prophet|Recalibrator|AutoCommande`) sur
  `model/SCONTO_SVU_GENERIC_MASTER.alp` : 0 occurrence.
- Références : `diagnostiquerCommandesBloquees()` n'est appelée qu'à un seul endroit
  (l'événement `bilanPeriodique`), aucune fonction supprimée/renommée.
- **Build AnyLogic** : **OK** (0 erreur, validé par l'utilisateur, 2026-09-16).
- **Run nominal** : **OK** — run nominal Generic/ZENER, aucune exception, chargement du
  scénario ZENER OK, flux Source/Make/Deliver cohérents, politique autonome de stock et
  approvisionnement fonctionnelle (validé par l'utilisateur, 2026-09-16).
- **Diagnostic fonctionnel forcé (commande volontairement bloquée)** : **À TESTER
  ULTÉRIEUREMENT**. Aucune ligne `[DIAG-BLOQUEE]` observée sur ce run nominal — attendu,
  puisque aucune commande n'y est restée `EN_COURS`/`EN_LIVRAISON` sans clôturer ; ce
  n'est pas un signal de non-régression négatif, mais le test positif du diagnostic
  (avec une commande maintenue ouverte/bloquée) reste à faire séparément.
- **Commit** : `0363b6b` (message `feat(generic): add blocked-order diagnostic`).

### Journal — Bloc A.3 : stock matière détaillé par article (2026-09-16)

**Analyse préalable (collègue et master)** :
- `detailStockMatiereParMatiere()` (collègue, ~ligne 6848) : parcourt `fichesMatiere`
  et produit une chaîne `"idMatiere=valeur|idMatiere=valeur|..."` (une valeur par
  matière, format machine-parseable, séparateur `|` choisi pour ne pas entrer en
  collision avec le `;` du CSV français). Purement lecture — aucune écriture d'état.
  Chez le collègue, sa **seule et unique** consommatrice est
  `capturerPointHistoriqueDashboard()` (ligne ~6954), qui appartient au **Bloc A.4**
  (Historique Dashboard/Excel), non encore porté.
- Master : possède déjà la fonction sœur `niveauStockMatiereText()` (ligne ~6966,
  identique caractère pour caractère à la version collègue), qui affiche la même
  information sous forme de texte lisible (`"GPL_VRAC : 600\n..."`) sur une carte du
  tableau de bord (`TextCode` à la ligne ~29836) — **usage UI uniquement, pas
  d'export**. Le master expose par ailleurs un agrégat hétérogène équivalent au
  problème documenté par le collègue : la fonction AnyLogic `stockMatiereDisponibleTotal()`
  (ligne ~19523) somme `f.stockDisponible` sur toutes les matières sans distinction
  d'unité (kg + bouteilles + kits additionnés), utilisée uniquement dans
  `valeurRuntimeMetriqueSCOR()` pour `AM.3.16`/`AM.2.8`. `detailStockMatiereParMatiere()`
  était totalement **absente** du master avant ce bloc.
- Vérifié : ni `exporterCSV()` (master ou collègue) ni aucune autre fonction d'export
  existante n'utilisent `detailStockMatiereParMatiere()` — son seul point de
  branchement réel (l'historique Dashboard) n'existe pas encore dans ce master.

**Décision de portage** : porter uniquement la fonction `detailStockMatiereParMatiere()`
elle-même, comme utilitaire autonome, sans la brancher sur un export ou une carte
dashboard prématurément — exactement le même traitement que `niveauStockMatiereText()`
qui coexiste déjà dans le master sans être reliée à un export CSV/Excel. Le branchement
dans l'historique Dashboard/Excel (colonne dédiée) est laissé au Bloc A.4, pour ne pas
préempter les décisions de format de cette fonctionnalité pas encore auditée.

**Fichier modifié** : `model/SCONTO_SVU_GENERIC_MASTER.alp`.

**Fonctions touchées** :
- ajout `String detailStockMatiereParMatiere()` dans `Main`, juste après
  `niveauStockMatiereText()` (même famille de fonctions de reporting stock matière,
  numérotée "5bis" dans le commentaire pour rester cohérente avec la numérotation
  "5."/"6." déjà présente dans le master à cet endroit).

**Ce qui a été porté** : la fonction telle quelle (portage à l'identique, aucune
adaptation de logique nécessaire — `FicheMatiere.idMatiere`/`stockDisponible`
existent déjà dans le master avec la même sémantique).

**Ce qui n'a pas été porté (et pourquoi)** : le branchement dans
`capturerPointHistoriqueDashboard()` / une colonne d'export — cette fonction n'existe
pas encore dans le master (Bloc A.4). Ajouter le branchement maintenant aurait
anticipé une décision de format (nom de colonne, position) qui appartient à l'audit du
Bloc A.4.

**Validations statiques** :
- XML bien formé : OK.
- IDs AnyLogic : 1677/1677 uniques, inchangé (nouvelle méthode Java libre uniquement,
  aucun élément `<Function>`/`<Variable>` AnyLogic ajouté).
- `git diff --check` : aucune erreur d'espace blanc.
- `git diff --stat` : 21 insertions, 0 suppression (aucune régression ailleurs, champ
  `Model/Name` toujours à sa valeur committée).
- Grep DataCo (`DATACO_*|Prophet|Recalibrator|AutoCommande`) : 0 occurrence.
- Références : `detailStockMatiereParMatiere()` n'est appelée nulle part pour l'instant
  (fonction disponible, non encore consommée) — comportement intentionnel, cf. décision
  de portage ci-dessus ; aucune fonction supprimée/renommée.
- **Build AnyLogic** : **OK** (0 erreur, validé par l'utilisateur, 2026-09-16).
- **Validation fonctionnelle** : **différée au Bloc A.4**. `detailStockMatiereParMatiere()`
  n'étant appelée par rien dans ce bloc, aucun run fonctionnel spécifique n'est requis
  avant A.4 (confirmé par l'utilisateur) ; sa sortie ne sera observable qu'une fois
  branchée dans l'historique Dashboard.
- **Commit** : `d52d431` (message `feat(generic): add per-material stock detail`).

## Audit des fichiers non suivis apparus sous model/ (2026-09-16)

Suite au Build/Run AnyLogic de l'utilisateur sur `model/SCONTO_SVU_GENERIC_MASTER.alp`,
`git status --short` a révélé 32 chemins non suivis (30 icônes PNG dont `box (1).png`,
`CLAUDE.md`, `README.md`, `scenario_ZENER_SA_Togo_v39.json`, `database/` avec `db.data`/
`db.properties`/`db.script`). **Audit purement descriptif — rien n'a été committé,
supprimé ni ajouté au `.gitignore`.**

Méthode : `git status --short`, SHA-256 de chaque fichier comparé à ses équivalents
(racine du repo, `assets/`), recherche du nom de fichier dans
`model/SCONTO_SVU_GENERIC_MASTER.alp`, inspection de la section `<Database>` du modèle.

| Fichier(s) | SHA-256 identique à | Référencé dans le `.alp` | Classification | Explication |
|---|---|---|---|---|
| 30× `model/*.png` (dont `box (1).png`) | racine **et** `assets/` (3 copies identiques) | **Oui** — `<ClassName>`/`<Path>` (ex. `aiguillage.png` ligne ~44770/~53479) | **REQUIRED_RESOURCE** | Le `.alp` référence ces icônes par chemin relatif ; AnyLogic les cherche à côté du fichier `.alp` qu'il ouvre. Absentes de `model/` avant le Build, il les a matérialisées là au moment de l'ouverture/sauvegarde du projet. |
| `model/scenario_ZENER_SA_Togo_v39.json` | racine (identique) | Non (0 occurrence — le chargement de scénario est dynamique, pas une ressource intégrée au build) | **USER_SCENARIO** | Probablement chargé/copié par l'utilisateur pendant le test de chargement ZENER (dialogue de sélection de fichier ouvrant par défaut dans le dossier du `.alp`). |
| `model/CLAUDE.md`, `model/README.md` | racine (identique) | Non (0 occurrence) | **DUPLICATE** | Aucun lien avec le moteur AnyLogic ; correspond à une copie complète du dossier source plutôt qu'à une ressource requise par le modèle — origine exacte non certaine (AnyLogic "Save Model As" avec copie de dossier, ou action manuelle). |
| `model/database/db.data`, `db.properties`, `db.script` | **Différent** de `database/` racine (`SET DATABASE UNIQUE NAME` distinct : `HSQLDBA0AB809148` vs `HSQLDB9F47CA2508` ; tailles différentes ; pas de `.lck`/`.log`) | Section `<Database><Logging>true</Logging></Database>` présente (ligne ~52340), sans chemin explicite | **RUNTIME_GENERATED** | Base HSQLDB de logging technique AnyLogic, régénérée par le run effectué depuis `model/` (chemin par défaut relatif au `.alp` ouvert) — distincte et indépendante de la base déjà présente à la racine du dépôt (héritée du clone initial, liée à l'ancien `SCONTO_VSM_Generic.alp`). |

Aucun fichier classé `UNKNOWN` — une explication cohérente a été trouvée pour chacun.

**Aparté (hors périmètre de cet audit, noté pour information)** : `reference/dataco-multiproduct/`
a été ajouté avec un fichier nommé `SCONTO_SVU_FINAL_VALIDATED_FORECAST_DATACO_MULTIPRODUCT_CONCURRENT_FIX.alp`
(2 244 316 octets) — nom différent de celui annoncé dans le message utilisateur
(`SCONTO_SVU_DATACO_MULTIPRODUCT_REFERENCE.alp`), mais taille identique à l'ancien
"maître" DataCo déjà répertorié dans `docs/merge/ANALYSE_FUSION_COLLEGUE_VS_MASTER.md`.
Non analysé plus avant : le Bloc M n'a pas commencé (cf. section Bloc M ci-dessous).

**Aucune action de nettoyage effectuée.** Décision laissée à l'utilisateur.

## Hygiène repository — ressources AnyLogic sous model/ (2026-09-16)

Suite à l'audit ci-dessus, vérification précise avant toute action Git, pour rendre le
repository reproductible depuis un clone propre.

**1. Vérification par fichier — référence dans le `.alp` + identité SHA-256** :
sur les 28 PNG non suivis sous `model/` (dont `box (1).png`), **25 sont réellement
référencés** dans `model/SCONTO_SVU_GENERIC_MASTER.alp` (1 à 4 occurrences chacun, via
`<ClassName>` et/ou `<Path>`) et **3 ne le sont pas du tout** (0 occurrence, vérifié
aussi insensible à la casse, et absents également du `.alp` collègue) :
`control-system.png`, `industrial-revolution.png`, `packages.png`. Reclassés
**DUPLICATE** (probablement copiés en bloc par AnyLogic avec les fichiers réellement
nécessaires, sans lien avec ce que le modèle utilise). Les 25 fichiers réellement
référencés ont chacun un SHA-256 strictement identique à leur copie de la racine du
dépôt **et** de `assets/` (3 copies identiques, vérifié individuellement).

**2. Format de référence** : chaque ressource référencée l'est par **nom de fichier nu**
(`<ClassName><![CDATA[aiguillage.png]]></ClassName>`, `<Path><![CDATA[aiguillage.png]]></Path>`),
jamais par chemin explicite du type `../assets/aiguillage.png`. Chaque référence est
accompagnée de `<Location>FILE_SYSTEM</Location>` dans le bloc `<Resource>` du modèle :
AnyLogic résout donc ces fichiers **relativement au dossier du `.alp` lui-même**. Le
`.alp` attend bien les fichiers à côté de lui — conformément à la règle donnée, aucune
modification en masse des chemins internes du `.alp` n'a été effectuée.

**Décision** : ajouter au Git uniquement les 25 PNG `REQUIRED_RESOURCE` sous `model/`
(liste : `aiguillage.png`, `back-office.png`, `box (1).png`, `container.png`,
`delay02.png`, `delivery-truck.png`, `email.png`, `enterprise.png`, `facility.png`,
`factory-machine.png`, `forklift.png`, `gestion.png`, `jacket.png`, `manufacturing.png`,
`ordre.png`, `produit.png`, `replacement.png`, `roadmap.png`, `stock.png`,
`stockage.png`, `stockage02.png`, `stocks.png`, `storage.png`,
`supply-chain-management.png`, `task.png`), dans un commit administratif distinct
(`chore(anylogic): track model runtime resources`). Les 3 PNG non référencés
(`control-system.png`, `industrial-revolution.png`, `packages.png`) restent non
suivis, comme les autres duplicatas.

**3. `model/database/`** : contenu inspecté avant toute décision `.gitignore`.
`model/database/db.script` ne contient que des tables `*_RAW_LOG` standard
(`AGENTS_RAW_LOG`, `AGENT_TYPES_RAW_LOG`, `EVENTS_RAW_LOG`, `TRACE_RAW_LOG`,
`STATISTICS_RAW_LOG`, etc.) et des tables internes `AL_*` de l'explorateur de base
AnyLogic — aucune table métier SCOR/VSM custom, cohérent avec la description déjà
faite de la base racine `database/` dans `reference/colleague/docs/SCENARIOS_AND_DATA.md`
§2 ("logging technique standard AnyLogic"). Le `.alp` déclare
`<Database><Logging>true</Logging>...</Database>` sans chemin explicite : AnyLogic
régénère cette base au dossier courant du `.alp` à chaque run avec DB logging actif.
`model/database/db.script` porte d'ailleurs un `SET DATABASE UNIQUE NAME` différent de
celui de la racine (`HSQLDBA0AB809148` vs `HSQLDB9F47CA2508`), confirmant deux bases
indépendantes. **Confirmé : donnée runtime régénérable, pas une donnée source.**
Règle `.gitignore` ajoutée : `model/database/`.

**Exclu de tout commit/`.gitignore` pour l'instant, conformément à la consigne** :
`model/CLAUDE.md`, `model/README.md`, `model/scenario_ZENER_SA_Togo_v39.json` (restent
non suivis, non supprimés du disque — possible copie faite par AnyLogic, pas de
perturbation du modèle local de l'utilisateur), ainsi que `control-system.png`,
`industrial-revolution.png`, `packages.png` (DUPLICATE non référencés, mêmes égards).

**Commit administratif** : `bf9bea4` (message `chore(anylogic): track model runtime resources`).

### Journal — Bloc A.4 : historique Dashboard / export Excel (2026-09-16)

**Analyse préalable (collègue)** :
- `historiqueDashboard` : `ArrayList<Object[]>` sur `Main`, un point par appel de
  `capturerPointHistoriqueDashboard()`, vidé à chaque `demarrerSimulation()`.
- `capturerPointHistoriqueDashboard()` : capture 28 valeurs par point (KPI dashboard +
  SCOR + PI), purement lecture, écrit uniquement dans `historiqueDashboard`.
- `historiqueDashboardColumns()`/`historiqueDashboardRows()` : en-têtes + lignes pour
  `ecrireFeuilleExcel()`, avec repli à 1 cellule si l'historique est vide.
- `compteurCyclesExportExcel` : **découple** la capture (chaque cycle
  `champIntervalleExportExcel`, léger) de l'écriture physique du classeur complet
  (~25 feuilles, lourde et synchrone), reportée toutes les ~300 s simulées via
  `cyclesParEcriture = round(300 / champIntervalleExportExcel)`. Optimisation de
  performance documentée par le collègue (`C15.16`) — **distincte** de l'ajout de
  l'historique lui-même.
- Événement concerné : `ExcelExportManager` (cyclique, période
  `champIntervalleExportExcel`, condition `modeExecution && exportExcelActif &&
  !c14SnapshotFinalEffectue`). Chez le collègue, son `Action` appelle
  `capturerPointHistoriqueDashboard()` puis, seulement tous les `cyclesParEcriture`
  cycles, `exporterToutesLesTablesExcel()`.
- `exporterToutesLesTablesExcel()` : diff complet avec le master — **une seule ligne
  diffère** entre les deux versions (confirmé par diff textuel des deux corps de
  fonction) : le master appelle `ecrireFeuilleExcel(..., "Manifeste Run", ...)` à cet
  endroit (feuille propre au master, absente chez le collègue), le collègue y appelle
  l'équivalent Historique Dashboard. Tout le reste de la fonction (dont le mécanisme
  d'écriture atomique par fichier temporaire) est déjà identique.
- Nom de feuille Excel : `"Historique Dashboard"` (dernière feuille écrite avant la
  finalisation du classeur, chez le collègue comme dans le master après portage).
- Fréquence de capture : un point par cycle de `champIntervalleExportExcel` (30 s par
  défaut), plus une capture initiale à `t=0` dans `demarrerSimulation()`.
- `detailStockMatiereParMatiere()` : déjà portée au Bloc A.3, consommée ici pour la
  première fois (colonne 18).

**Tableau d'analyse colonne par colonne** (26 colonnes retenues sur 28 chez le
collègue — 2 reportées, voir plus bas) :

| # | Colonne collègue | Source / fonction | Présente dans master ? | Sémantique identique ? | Décision |
|---|---|---|---|---|---|
| 1 | Temps simulation (s) | `time()` | Oui (natif AnyLogic) | Oui | PORTER |
| 2 | Order Throughput (ent/h) | `nbTermines` | Oui | Oui | PORTER |
| 3 | Avg Lead Time (min) | `board.kpiGlobal.avgLeadTime() / 60.0` (correction 2026-09-16 : le `/ 60.0` manquait dans cette table, voir A.4-FIX-1 — présent dans le code depuis le portage initial) | Oui | Oui | PORTER |
| 4 | Work In Process (Products) | `wipReelSansJetonsVisuels()` | Oui, corps identique (vérifié) | Oui | PORTER |
| 5 | Finished Stock (Products) | boucle `postes`/`estPosteStockFini()` | Oui, `estPosteStockFini()` identique | Oui | PORTER |
| 6 | PCE (%) | `board.kpiZener`/`kpiGlobal.pce()` | Oui | Oui | PORTER |
| 7 | Waiting Time (s) | `tempsAttenteGlobalCoherent()` | Oui, **corps différent** (master : `orderWaitingTimeGlobal()`, commentaire "VSM-FIX-05 — wrapper de compatibilité, aucune reconstruction par PCE") | Non — le master a sa propre correction, plus récente | **ADAPTER** : appeler la fonction du master telle quelle, ne pas écraser par la version collègue |
| 8 | Order Mode - MTS (nb) | `board.nbMTS` | Oui | Oui | PORTER |
| 9 | Order Mode - MTO (nb) | `board.nbMTO` | Oui | Oui | PORTER |
| 10 | Delayed Orders (nb) | `commandesRetardeesCount()` | Oui, **corps différent** (collègue ajoute `\|\| c.retardConstate`, champ Bloc C absent du master) | Non | **ADAPTER** : appeler la fonction du master telle quelle (EN_RETARD + client uniquement) |
| 11 | Taux de conformité qualité (%) | `tauxRemplissagePct()` | Oui, `<Function>` identique | Oui | PORTER |
| 12 | Scrap Rate (%) | `tauxRebutPct()` | Oui, identique | Oui | PORTER |
| 13 | Rework Rate (%) | `tauxReprisePct()` | Oui, identique | Oui | PORTER |
| 14 | Takt Time (s) | `calculerTaktTimeSec()` | Oui, identique | Oui | PORTER |
| 15 | Production Throughput (ent/h) | `throughputMakeAffiche()` | Oui, identique | Oui | PORTER |
| 16 | Order Lead Time (min) | `board.kpiGlobal.avgLeadTime() / 60.0` | Oui (doublon volontaire de la colonne 3 déjà présent chez le collègue) | Oui | PORTER (doublon conservé tel quel, non corrigé — décision de design du collègue, pas de notre ressort dans un portage à l'identique) |
| 17 | Raw Material Stock (unités) | boucle locale sur `fichesMatiere` | Le master a une fonction équivalente déjà existante `stockMatiereDisponibleTotal()` (utilisée par `valeurRuntimeMetriqueSCOR()` pour AM.3.16/AM.2.8) | Oui (même somme), avec clamp `Math.max(0, ...)` côté master | **ADAPTER** : appeler `stockMatiereDisponibleTotal()` du master plutôt que dupliquer une boucle équivalente |
| 18 | Raw Material Stock — détail par matière | `detailStockMatiereParMatiere()` | Oui — portée au Bloc A.3 | Oui | PORTER |
| 19 | Supplier Lead Time (h) | `delaiFournisseurMoyenHeures()` | Oui, identique | Oui | PORTER |
| 20-24 | SCOR RL/RS/AG/CO/AM | `strategic.scoreRL/RS/AG/CO/AM` | Oui (champs présents, alimentés par le `calculerPIGlobal()` **actuel** du master) | Champs identiques, calcul différent (Bloc B) | PORTER **en l'état** : valeurs actuelles du master, sans anticiper la refonte PI/SCOR |
| 25 | PI (indice de performance courant) | `strategic.piGlobalCourant` | Oui | Idem | PORTER en l'état |
| 26 | PI cible | `strategic.ciblePIGlobal` | Oui | Idem | PORTER en l'état |
| 27 | Attributs pondérés dans le PI | `strategic.attributsPonderesPI` | **Non** — champ absent du master | — | **REPORTER** (Bloc B) |
| 28 | Somme des poids effectifs | `strategic.sommePoidsEffectifsPI` | **Non** — champ absent du master | — | **REPORTER** (Bloc B) |

**Décision sur les colonnes reportées** : les colonnes 27/28 ne sont pas ajoutées avec
une valeur factice (ex. `"N/A"`) — elles sont simplement absentes de la feuille pour
l'instant, pour ne pas laisser croire à une traçabilité de périmètre PI qui n'existe
pas encore dans ce master. La feuille "Historique Dashboard" du master compte donc
**26 colonnes** (au lieu de 28 chez le collègue). Elles seront ajoutées au Bloc B en
même temps que les champs `attributsPonderesPI`/`sommePoidsEffectifsPI`.

**`compteurCyclesExportExcel` (mécanisme de throttling d'écriture)** : **non porté**.
Décision : c'est une optimisation de performance indépendante de l'ajout de
l'historique (le collègue les a livrées ensemble, mais elles n'ont pas de dépendance
fonctionnelle l'une envers l'autre — la capture peut très bien être appelée à chaque
cycle sans changer la cadence d'écriture du fichier). La porter maintenant aurait
changé un comportement existant du master (fréquence de réécriture du classeur pour
les ~25 feuilles déjà en place), ce qui dépasse le périmètre "ajouter un historique
Dashboard" de ce bloc. Peut être proposée séparément si des runs longs révèlent un
problème de performance à l'écriture Excel.

**Fichier modifié** : `model/SCONTO_SVU_GENERIC_MASTER.alp`.

**Fonctions/variables/appels touchés** :
- ajout `public java.util.ArrayList<Object[]> historiqueDashboard` (champ `Main`, à
  côté de `historiqueFluxInformationnels`) ;
- ajout `void capturerPointHistoriqueDashboard()`, `String[] historiqueDashboardColumns()`,
  `Object[][] historiqueDashboardRows()` (juste après `detailStockMatiereParMatiere()`) ;
- `demarrerSimulation()` : ajout de `historiqueDashboard.clear();` (juste après
  `reinitialiserHistoriqueFluxInformationnels();`) et d'une capture initiale
  `try { capturerPointHistoriqueDashboard(); } catch (Throwable ignoredHistoriqueDashboard) {}`
  (juste après `actualiserTempsSimulation();`) ;
- `exporterToutesLesTablesExcel()` : ajout d'une ligne
  `ecrireFeuilleExcel(wb, styleEntete, styleNormal, "Historique Dashboard", historiqueDashboardColumns(), historiqueDashboardRows());`
  juste après la feuille "Manifeste Run" (déjà propre au master, conservée) ;
- événement `ExcelExportManager` : ajout de l'appel `capturerPointHistoriqueDashboard();`
  juste avant l'appel existant à `exporterToutesLesTablesExcel();`.

**Ce qui a été porté** : le mécanisme complet d'historique temporel (champ, capture,
colonnes, lignes, feuille Excel, reset par run, capture initiale + périodique), pour
26 des 28 colonnes du collègue.

**Ce qui a été adapté** :
- colonne 7 (Waiting Time) → fonction déjà corrigée du master (`tempsAttenteGlobalCoherent()`,
  "VSM-FIX-05"), pas la reconstruction PCE du collègue ;
- colonne 10 (Delayed Orders) → fonction déjà présente du master (EN_RETARD + client),
  sans le `retardConstate` du Bloc C ;
- colonne 17 (Raw Material Stock agrégat) → réutilisation de `stockMatiereDisponibleTotal()`
  déjà existante dans le master, au lieu de dupliquer une boucle équivalente.

**Ce qui n'a pas été porté (et pourquoi)** :
- colonnes 27/28 (traçabilité du périmètre PI) → champs `attributsPonderesPI`/
  `sommePoidsEffectifsPI` absents du master, Bloc B ;
- `compteurCyclesExportExcel` (throttling d'écriture Excel) → optimisation de
  performance distincte, changerait un comportement existant du master, hors
  périmètre de "ajouter un historique Dashboard" ;
- `evaluerRetardsCommandesOuvertes()`/`retardConstate` (déjà exclus depuis A.2) →
  toujours Bloc C.

**Validations statiques** :
- XML bien formé : OK.
- IDs AnyLogic : 1677/1677 uniques, inchangé (nouvelles méthodes Java libres
  uniquement, aucun élément `<Function>`/`<Variable>` AnyLogic ajouté, `historiqueDashboard`
  est un champ Java libre comme `historiqueFluxInformationnels`).
- `git diff --check` : aucune erreur d'espace blanc.
- `git diff --stat` : 136 insertions, 3 suppressions (les 3 suppressions correspondent
  à la mise à jour du commentaire, devenu obsolète, au-dessus de
  `detailStockMatiereParMatiere()` — plus aucune trace de "pas encore appelée depuis
  un export").
- Grep DataCo : 0 occurrence.
- Nombre de colonnes == nombre de valeurs par ligne : vérifié programmatiquement,
  **26 == 26**, dans le même ordre.
- `capturerPointHistoriqueDashboard()` : vérifié qu'elle n'écrit que dans
  `historiqueDashboard` (variables locales `rl/rs/ag/co/am/pi/piCible/stockFini` mises
  à part) — aucune écriture sur `commandes`, `postes`, `strategic`, `board`, aucun
  appel à une fonction de mutation (uniquement des lectures/fonctions déjà utilisées
  ailleurs comme sources d'affichage/export en lecture seule).
- Échappement Excel/chaînes : `ecrireFeuilleExcel()` (inchangée) gère déjà la
  distinction numérique/texte cellule par cellule (`estCelluleNumerique()`) — la seule
  chaîne libre introduite est `detailStockMatiereParMatiere()`
  (`"idMatiere=valeur\|idMatiere=valeur"`), déjà validée au Bloc A.3, sans caractère
  spécial Excel (`=`, `\|` ne déclenchent pas d'interprétation de formule car la
  cellule est écrite via `setCellValue(String)`, pas en tant que formule).
- `ecrireFeuilleExcel()` : vérifié qu'elle itère sur
  `min(ligne.length, colonnes.length)` — confirme qu'un repli à 1 cellule (historique
  vide) ne provoque aucun crash face à un en-tête de 26 colonnes.
- **Build AnyLogic** : EN ATTENTE (utilisateur).
- **Run** : EN ATTENTE (utilisateur). Protocole suggéré : lancer un run court avec
  export Excel actif, ouvrir le classeur généré, vérifier la feuille "Historique
  Dashboard" (26 colonnes, ≥1 ligne après le premier cycle `champIntervalleExportExcel`),
  confirmer que les 25 autres feuilles existantes sont inchangées.
- **Commit** : `69c78d6` (message `feat(generic): add dashboard history export`).

### Vérification unités — Avg Lead Time / Order Lead Time (2026-09-16)

Demandée avant validation définitive du Bloc A.4 : les colonnes "Avg Lead Time (min)"
et "Order Lead Time (min)" utilisent toutes deux `board.kpiGlobal.avgLeadTime() / 60.0`
— vérification qu'il n'y a pas d'incohérence d'unité entre elles ou avec le reste du
master.

**1. Définition exacte** (`KPIBundle`, ligne ~53123) :
```java
public double avgLeadTime() { return avgCycleTime() + avgWaitTime(); }
```
`avgCycleTime()`/`avgWaitTime()` = moyenne (pondérée si `weightTotal>0`, sinon simple)
de `sumCycleTime`/`sumWaitTime`, alimentées par `addObservation(cycleTime, waitTime, ...)`.

**2. Unité réelle** : les valeurs passées à `addObservation()` proviennent de deltas de
temps de simulation bruts (`ModelTimeUnit = Second`, déclaré en tête du `.alp`). Preuve
directe la plus explicite : `enregistrerFinCommandeGlobale()` calcule
`double lt = Math.max(0.001, cmd.leadTimeClientReelSec);` — le suffixe `Sec` du nom de
variable est sans ambiguïté — puis appelle `board.notifierFin(lt, wt, vat, ...)`, qui
alimente `kpiGlobal`. Confirmation supplémentaire dans l'export CSV existant
(`exporterToutesLesTablesExcel`/`exporterCSV`, ligne 47294) :
`pw.println("entreprise;niveau;cle;avgCycleTime_s;avgWaitTime_s;avgLeadTime_s;pce_pct;count");`
— le suffixe `_s` de l'en-tête CSV est explicite. Egalement confirmé dans l'export ABox
RDF (ligne ~8802) : `{"order_fulfillment_lead_time","core:LeadTime",...,orderFulfillmentLeadTimeGlobal(),"s"}`.

**3. Usages existants dans le master** : deux cartes dashboard *déjà en place avant ce
bloc* convertissent déjà `avgLeadTime()` en minutes par `/ 60.0` :
- carte "Avg Lead Time" (TextCode ligne ~30323) :
  `String.format("%.1f", board.kpiGlobal.avgLeadTime() / 60.0)` ;
- carte "Order Lead Time", fonction `orderLeadTimeText()` (ligne ~15330-15347), qui
  calcule **quatre** valeurs (MTS, MTO, Global, ZENER), toutes divisées par 60 et
  suffixées `" min"` dans la chaîne retournée : `glob = board.kpiGlobal.avgLeadTime() / 60.0`
  en est très exactement la composante "Global".

**4. Valeurs de run documentées** (`reference/colleague/docs/DOCUMENTATION_SCENARIOS_VALIDATION.md`,
scénario 0) : "Lead time global | 18364,97 s" (brut, secondes) coexistant avec
"Délai de livraison (Order Lead Time) | MTS=329,0 min ; Global=329,0 min" pour le même
type de métrique dans le même document — cohérent avec une métrique nativement en
secondes, affichée en minutes après conversion explicite.

**5. Conclusion explicite : SECONDES.** `board.kpiGlobal.avgLeadTime()` retourne des
secondes ; toute conversion en minutes doit diviser par 60. C'est exactement ce que
font les deux colonnes de l'historique Dashboard.

**6. Vérification des deux colonnes de l'historique Dashboard** :

| Colonne | Expression | Conversion | Libellé | Verdict |
|---|---|---|---|---|
| "Avg Lead Time (min)" | `fmt1(board.kpiGlobal.avgLeadTime() / 60.0)` | `/ 60.0` (s → min) | "(min)" | Correct, cohérent avec la carte dashboard "Avg Lead Time" existante |
| "Order Lead Time (min)" | `fmt1(board.kpiGlobal.avgLeadTime() / 60.0)` | `/ 60.0` (s → min) | "(min)" | Correct — équivaut exactement à la composante "Global" de la carte "Order Lead Time" (`orderLeadTimeText()`) existante |

**Aucune incohérence d'unité.** Les deux colonnes portent la même conversion et le même
libellé d'unité ; **aucun commit fonctionnel supplémentaire n'est requis**. La seule
observation (déjà notée au moment du portage A.4, sans lien avec les unités) est que
les deux colonnes portent la **même valeur** — un doublon volontaire hérité du design
original du collègue (déjà présent tel quel dans son propre fichier, reproduit à
l'identique lors du portage), qui correspond désormais précisément à la composante
"Global" (par opposition à MTS/MTO/ZENER) de la carte enrichie `orderLeadTimeText()`
du master. Ce n'est pas un défaut d'unité et n'appelle aucune correction dans le
périmètre de cette vérification.

### Validation utilisateur A.4 (2026-09-16)

- **Build AnyLogic** : OK, 0 erreur.
- **Run ZENER court** : OK.
- **Feuille "Historique Dashboard"** : présente.
- **26 colonnes** : confirmées.
- **Plusieurs snapshots temporels** : confirmés (plusieurs lignes capturées au fil du run).
- **`detailStockMatiereParMatiere()`** : correctement exporté (colonne détail par matière).
- **Feuilles historiques existantes** : inchangées.
- **Aucune exception**.
- **Vérification unités Lead Time** : effectuée ci-dessus, aucune incohérence trouvée.

**Validation revue à la baisse** : cette entrée reposait sur une observation visuelle
du classeur (feuille présente, 26 colonnes, plusieurs lignes). Une analyse plus
approfondie de l'export réel et de l'ABox du même run (ci-dessous, A.4-FIX-1 à 3) a
révélé un défaut fonctionnel réel (A.4-FIX-2) masqué par cette observation de surface
— l'historique contenait bien "plusieurs" lignes, mais s'arrêtait à t=60 s sur un run
allant jusqu'à t=582 s. **La validation définitive du Bloc A.4 est reportée après
A.4-FIX-1/2/3 et un nouveau run utilisateur.**

### A.4-FIX — corrections suite à l'analyse de l'export réel (2026-09-16)

Analyse demandée de l'export Excel + ABox d'un run réel (582 s, PI=8,192, 3 commandes
closes, Lead Time final=15250,79 s). Trois corrections identifiées.

#### A.4-FIX-1 — Unité du Lead Time (colonne 3)

**Vérification demandée** : définition exacte de `avgLeadTime()`, son unité réelle,
usages existants, valeurs de run, conclusion explicite.

- **Définition** (`KPIBundle`, ligne ~53123) : `avgLeadTime() = avgCycleTime() + avgWaitTime()`.
- **Unité réelle : SECONDES.** Déjà établi lors de la vérification unités du tour
  précédent (voir section ci-dessus) : variable source `cmd.leadTimeClientReelSec`
  (suffixe `Sec` explicite), en-tête CSV existant `avgLeadTime_s`, unité `"s"` dans
  l'export ABox. Confirmé une seconde fois par l'export réel analysé : "Order
  Fulfillment Lead Time (secondes) = 15250.79" (Dashboard Global) et
  `LEAD_TIME_MOYEN = 15250.79` (Traces Agrégées) désignent la même grandeur.
- **Vérification de la colonne 3 dans le CODE actuel** (`model/SCONTO_SVU_GENERIC_MASTER.alp`,
  fonction `capturerPointHistoriqueDashboard()`) :
  ```java
  fmt1(board.kpiGlobal.avgLeadTime() / 60.0),   // colonne 3 "Avg Lead Time (min)"
  ...
  fmt1(board.kpiGlobal.avgLeadTime() / 60.0),   // colonne 16 "Order Lead Time (min)"
  ```
  **Le code porte déjà la conversion `/ 60.0` sur les deux colonnes** — vérifié par
  grep direct sur le fichier committé (`69c78d6`), avant toute modification de ce
  correctif. **Il n'y a pas de bug fonctionnel dans le code.**
- **Origine réelle de l'alerte** : le tableau d'analyse consigné dans ce document (ligne
  "3 | Avg Lead Time (min) | `board.kpiGlobal.avgLeadTime()` | ...") **omettait
  par erreur d'écriture le `/ 60.0`** dans la colonne "Source / fonction", donnant
  l'impression trompeuse d'une valeur brute en secondes sous une étiquette "(min)".
  Corrigé ci-dessus (voir la ligne 3 du tableau, section Journal A.4).
- **Décision** : aucune modification de code nécessaire (déjà correct : conversion
  `/60.0` + libellé "(min)" cohérents sur les deux colonnes). Correction apportée
  uniquement à la documentation.

#### A.4-FIX-2 — l'historique s'arrête prématurément (défaut réel, corrigé)

**Cause racine identifiée** : `capturerPointHistoriqueDashboard()` était appelée depuis
l'`Action` de l'événement `ExcelExportManager`, dont la `Condition` est
`modeExecution && exportExcelActif && !c14SnapshotFinalEffectue`. Or `c14SnapshotFinalEffectue`
passe à `true` de façon **permanente pour le reste du run** dès la **première** clôture
de commande cliente, dans deux chemins de code identiques (fin de parcours normal et
un second chemin de clôture Deliver), tous deux gardés uniquement par
`aboxExportActif && aboxExportSurClotureCommande` (pas de garde `!c14SnapshotFinalEffectue`
avant d'y entrer — chaque clôture réexporte et re-positionne le drapeau à `true`).
Conséquence : dès qu'une commande se clôt (souvent tôt dans le run), `ExcelExportManager`
— et donc la capture qui y était piggybackée — s'arrête définitivement, même si la
simulation continue ensuite pendant plusieurs centaines de secondes. Confirmé
exactement par l'observation utilisateur : capture arrêtée à t=60 s sur un run allant
jusqu'à t=582 s.

**Correctif appliqué — capture DÉCOUPLÉE de l'écriture Excel**, solution la moins
invasive retenue (nouvel événement dédié plutôt que restructuration d'`ExcelExportManager`) :

1. Nouvel événement `Main.DashboardHistoryManager` (cyclique, période
   `champIntervalleExportExcel` — même cadence générique que l'export, aucun nouveau
   champ de configuration), **condition réduite à `modeExecution` seul** (indépendant
   de `exportExcelActif` et de `c14SnapshotFinalEffectue`) : `Action` = appel unique à
   `capturerPointHistoriqueDashboard()`.
2. `ExcelExportManager` **revient à son état exact d'avant le Bloc A.4** (plus d'appel
   de capture dans son `Action`) — aucun changement à sa logique d'écriture existante,
   conformément à la consigne de ne pas réintroduire une réécriture des ~25 feuilles
   toutes les 30 s.
3. **Garde anti-doublon temporel** : nouveau champ `dernierTempsCaptureHistoriqueDashboard`
   (double, réinitialisé à `-1.0` dans `demarrerSimulation()` aux côtés de
   `historiqueDashboard.clear()`) ; `capturerPointHistoriqueDashboard()` retourne
   immédiatement si `time()` égale déjà ce champ (tolérance `1e-4`), et le met à jour
   sinon. Empêche toute double ligne pour le même instant si un cycle
   `DashboardHistoryManager` coïncide avec une clôture de commande.
4. **Snapshot final garanti** : `arreterSimulation()` appelle désormais
   `capturerPointHistoriqueDashboard()` (protégée par try/catch) avant de positionner
   `modeExecution = false`, puis `exporterToutesLesTablesExcel()` si
   `exportExcelActif` — pour que l'arrêt manuel d'un run (cas exact observé : dernier
   cycle périodique antérieur à l'arrêt réel) capture et écrive bien le dernier point,
   même si l'écriture périodique était déjà désactivée par `c14SnapshotFinalEffectue`.
   Sans cet ajout, `arreterSimulation()` ne réécrivait jamais le classeur (comportement
   d'origine, antérieur à tout portage), et les points capturés après la dernière
   écriture physique auraient été perdus.

**Ce qui n'a pas été modifié** : les deux points d'export "sur clôture de commande"
(`finDeParcours()`/second chemin Deliver) et leur positionnement de
`c14SnapshotFinalEffectue` sont **inchangés** — la capture continue désormais
indépendamment d'eux, donc leur comportement d'origine (export immédiat + flag) reste
utile (écrit l'historique accumulé jusqu'à cet instant) sans qu'il soit nécessaire d'y
toucher.

#### A.4-FIX-3 — agrégat stock matière hétérogène : renommage de l'en-tête

**Constat** : la colonne "Raw Material Stock (unités)" additionne des grandeurs
physiquement hétérogènes (`GPL_VRAC=600` + `BOUTEILLE_VIDE_12KG=250` +
`ACCESSOIRES_KIT=300` = `1150`), déjà signalé comme limite connue de
`stockMatiereDisponibleTotal()` (conservée pour compatibilité avec les métriques SCOR
`AM.3.16`/`AM.2.8` existantes — **non modifiées dans ce correctif**, leur refonte
appartient au Bloc B).

**Correctif** : en-tête renommé dans `historiqueDashboardColumns()` uniquement :
`"Raw Material Stock (unites)"` → `"Raw Material Stock (agrégat legacy, unités hétérogènes)"`.
Aucun changement de la valeur calculée ni de la fonction `stockMatiereDisponibleTotal()`
elle-même. La colonne "Raw Material Stock — détail par matière"
(`detailStockMatiereParMatiere()`, Bloc A.3) reste la représentation scientifiquement
exploitable, inchangée.

**Fichier modifié** : `model/SCONTO_SVU_GENERIC_MASTER.alp`.

**Validations statiques** :
- XML bien formé : OK.
- IDs AnyLogic : 1679/1679 uniques (+2 pour les deux `<Id>` du nouvel événement
  `DashboardHistoryManager`), aucun doublon.
- `git diff --check` : aucune erreur d'espace blanc.
- Grep DataCo : 0 occurrence.
- Colonnes == valeurs par ligne : toujours **26 == 26** (aucune colonne ajoutée/retirée,
  un seul libellé renommé), revérifié programmatiquement.
- Aucune mutation métier depuis la capture : `capturerPointHistoriqueDashboard()`
  n'écrit toujours que dans `historiqueDashboard` et le nouveau
  `dernierTempsCaptureHistoriqueDashboard` (bookkeeping interne à l'historique
  lui-même, pas un état métier) ; `arreterSimulation()` ne modifie que
  `modeExecution` (comportement déjà existant, inchangé dans son ordre logique) et
  déclenche des écritures fichier (I/O), pas une mutation de commande/stock/routage/PI.
- Aucune duplication abusive de timestamp : garde `dernierTempsCaptureHistoriqueDashboard`
  vérifiée (tolérance `1e-4`).
- Snapshot final garanti : `arreterSimulation()` capture et exporte avant de couper
  `modeExecution`, y compris si le dernier cycle périodique remonte à plusieurs
  secondes.
- **Build AnyLogic** : EN ATTENTE (utilisateur).
- **Run** : EN ATTENTE (utilisateur). Protocole suggéré : reproduire un run similaire
  au run analysé (au moins une commande close avant la fin), vérifier que
  l'historique Dashboard continue d'accumuler des lignes après la première clôture de
  commande et jusqu'à la fin réelle du run (y compris un point à l'arrêt manuel s'il
  est utilisé), et que la colonne 17 porte son nouveau libellé.
- **Commit** : voir SHA ci-dessous (message `fix(generic): correct dashboard history semantics`).

**Bloc A.4 : validation définitive EN ATTENTE du nouveau run utilisateur post-fix.**

### A.4-FIX-4 — finalisation robuste sur arrêt de run (2026-09-17)

**Validation du run post A.4-FIX-2/3** : confirmée par l'utilisateur — la capture
périodique dédiée fonctionne (snapshots t=14,4 / 30 / 60 / 90 / ... / 600, continuant
bien après les premières clôtures de commande). Une nouvelle analyse croisée
Excel + ABox + CSV du même run a cependant révélé un problème de **finalisation** :
Excel/ABox figés à t=628 (synchronisés entre eux : 3 commandes closes, PI=8,039,
274 `RawEvent` = 274 événements "Execution Brute") alors que le CSV du même run va
jusqu'à t=1489,888 et contient des traces de CMD_4 à CMD_7 (588 lignes postérieures
à t=628) — preuve que la simulation avait continué bien au-delà du dernier
Excel/ABox persisté.

**Investigation menée avant toute modification** (consigne explicite : ne rien
modifier tant que la cause n'est pas établie) :

1. **Tous les chemins d'arrêt identifiés** : recherche exhaustive dans
   `model/SCONTO_SVU_GENERIC_MASTER.alp` de `arreterSimulation()`, de tout bloc
   "on destroy"/"on finish", et des tags enfants de `ActiveObjectClass` (`Main`) et
   de `SimulationExperiment`.
2. **Appelant(s) actuel(s) de `arreterSimulation()`** : **un seul**, le bouton
   `button3` ("Arreter et voir resultats"), dont la propriété était
   `<Enabled>false</Enabled>` — **le bouton est désactivé, donc `arreterSimulation()`
   n'est jamais réellement invocable depuis l'interface.**
3. **Origine du CSV allant jusqu'à t=1489,888** : élucidée — un bouton natif distinct
   et **toujours actif**, `btnDashExport` ("Exporter CSV"), appelle
   `supervisor.exporterCSV(nomEntreprise)` (fonction de `CoordinatorAgent`,
   totalement indépendante du pipeline Excel/ABox de `Main`). Un second mécanisme,
   un bouton générique "Exporter CSV" dans les popups de table (`exportTableToCSV()`),
   est également indépendant. Le CSV à t=1489,888 provient donc d'un clic manuel sur
   l'un de ces boutons à ce moment du run, sans lien avec un défaut du pipeline
   Excel/ABox — **rien à corriger côté CSV**.
4. **`DashboardHistoryManager` actif après t=628 ?** — oui, quasi certainement : sa
   condition est `modeExecution` seul (A.4-FIX-2), indépendante de
   `c14SnapshotFinalEffectue` et de `exportExcelActif` côté écriture ; rien dans le
   code n'aurait pu l'arrêter avant t=1489. Le problème n'est donc **pas** la capture
   (déjà corrigée en A.4-FIX-2) mais l'**écriture** : plus aucun déclencheur d'écriture
   Excel/ABox n'intervient après la dernière clôture de commande, faute de
   `arreterSimulation()` accessible.
5. **Recherche d'un hook de cycle de vie AnyLogic** (Option B envisagée) : absente.
   Les tags enfants de `ActiveObjectClass` (`Main`) sont
   `Id, Name, AdditionalClassCode, StartupCode, Generic, GenericParameter,
   FlowChartsUsage, SamplesToKeep, LimitNumberOfArrayElements, ElementsLimitValue,
   MakeDefaultViewArea, SceneGridColor, SceneBackgroundColor, SceneSkybox,
   AgentProperties, EnvironmentProperties, DatasetsCreationProperties, ScaleRuler,
   CurrentLevel, ConnectionsId, Variables, Events, Functions, AgentLinks,
   EmbeddedObjects, Presentation, Areas` — seul `StartupCode` existe, **aucun bloc
   "on destroy"/"on finish"**. La section `SimulationExperiment` ne contient aucun
   champ de ce type non plus (`StopOption=Never`, pas de code de fin). **Conclusion :
   le bouton natif Stop/Terminate d'AnyLogic ne peut déclencher aucun code du
   modèle** — confirmé, pas supposé.

**Décision — solution la moins invasive retenue** (évaluation des options A/B/C
demandées) :
- **Option A** (faire appeler `arreterSimulation()` par le bouton natif AnyLogic) :
  impossible — ce bouton est un contrôle du moteur, hors de portée du code modèle.
- **Option B** (hook de cycle de vie sur l'agent Main) : **indisponible** dans ce
  schéma `.alp`/cette version AnyLogic (vérifié au point 5) ; tenter un contournement
  bas niveau (API moteur non documentée dans ce fichier) aurait été invasif et non
  vérifiable statiquement — écarté par prudence.
- **Option C retenue, réduite à l'essentiel** : nouvelle fonction unique et
  **idempotente** `finaliserRunEtExporter()`, appelée par `arreterSimulation()`
  (qui reste l'unique point d'entrée réel) — **et réactivation du bouton
  `button3`** (`<Enabled>false</Enabled>` → `<Enabled>true</Enabled>`), qui est la
  correction déterminante : sans point d'entrée UI accessible, aucune finalisation
  côté modèle n'est possible, quelle que soit la qualité du code de finalisation.

**Fichier modifié** : `model/SCONTO_SVU_GENERIC_MASTER.alp`.

**Fonctions/variables/contrôles touchés** :
- ajout `boolean runFinalise` (champ `Main`, garde d'idempotence, remis à `false`
  dans `demarrerSimulation()` aux côtés des autres réinitialisations de l'historique) ;
- ajout `void finaliserRunEtExporter()` : si `runFinalise` est déjà vrai, ne fait
  rien ; sinon positionne `runFinalise=true` puis (a) capture finale via
  `capturerPointHistoriqueDashboard()` (déjà protégée contre les doublons de temps,
  A.4-FIX-2), (b) export ABox si `aboxExportActif && aboxExportSurArret` (même garde
  que l'ancien code d'`arreterSimulation()`, raison `"RUN_FINALIZED"`), (c) export
  Excel complet si `exportExcelActif` ;
- `arreterSimulation()` : simplifiée — conserve `modeExecution=false`,
  `arrivee.reset()`, le log `"=== SIMULATION ARRETEE ..."`, puis délègue tout le reste
  à un appel unique `finaliserRunEtExporter();` (élimine la duplication de logique
  introduite en A.4-FIX-2) ;
- **contrôle `button3`** ("Arreter et voir resultats") : `Enabled` passé de `false` à
  `true`.

**Ce qui n'a pas été touché (conformément à la consigne C14)** : les deux chemins
d'export "sur clôture de commande" (`finDeParcours()`/second chemin Deliver) et leur
positionnement de `c14SnapshotFinalEffectue` restent **strictement inchangés** — ces
snapshots de preuve continuent d'exister exactement comme avant. Aucune tentative de
renommer ou de refactoriser ce drapeau n'a été faite (audit complet non réalisé,
hors périmètre de ce correctif).

**Limite assumée et documentée (dans le code et ici)** : si l'utilisateur arrête le
run via le bouton natif Stop/Terminate d'AnyLogic plutôt que via "Arreter et voir
resultats", `finaliserRunEtExporter()` ne sera **pas** appelée — aucune solution
fiable et vérifiable n'a été trouvée pour intercepter cet arrêt natif depuis le
modèle. **Recommandation utilisateur : toujours cliquer sur "Arreter et voir
resultats" pour obtenir un export final synchronisé.**

**Validations statiques** :
- XML bien formé : OK.
- IDs AnyLogic : 1679/1679 uniques, inchangé (aucun élément `<Function>`/`<Variable>`
  AnyLogic ajouté — `finaliserRunEtExporter()` est du code Java libre comme
  `capturerPointHistoriqueDashboard()` ; seul le contrôle `button3` existant a été
  modifié, sans nouvel `<Id>`).
- `git diff --check` : aucune erreur d'espace blanc.
- Grep DataCo : 0 occurrence.
- Idempotence vérifiée par lecture : un second appel à `finaliserRunEtExporter()`
  retourne immédiatement (`if (runFinalise) return;`) — aucun risque de double export
  ABox, de doublon de dernière ligne Dashboard, ni de mutation de stock/commande (la
  fonction ne touche ni l'un ni l'autre de toute façon, capture + export seulement).
- Aucune duplication de timestamp final : `capturerPointHistoriqueDashboard()`
  conserve sa garde `dernierTempsCaptureHistoriqueDashboard` (A.4-FIX-2), qui
  s'applique aussi à l'appel de finalisation.
- **Build AnyLogic** : EN ATTENTE (utilisateur).
- **Run** : EN ATTENTE (utilisateur). Protocole suggéré : run > 900 s, puis clic sur
  "Arreter et voir resultats" (désormais actif) pour arrêter normalement ; vérifier
  (1) CSV max time ≈ Tfinal (via un export manuel, pour comparaison) ; (2) dernière
  ligne Historique Dashboard ≈ Tfinal ; (3) l'Excel final est bien réécrit après
  cette ligne ; (4) l'ABox finale correspond au même run (raison
  `RUN_FINALIZED`) ; (5) aucune exception au clic ; (6) aucun doublon de timestamp
  final dans l'historique.
- **Commit** : voir SHA ci-dessous (message `fix(generic): finalize dashboard history on run stop`).

**Bloc A.4 : validation définitive toujours EN ATTENTE du run post A.4-FIX-4.**

### A.4-FIX-5 — ABox finale absente + terminaison réelle du moteur (2026-09-17)

**Validation du run post A.4-FIX-4** : confirmée — mécanisme Historique Dashboard
totalement fonctionnel : ~81 snapshots, premier ~t=16,5, cadence 30 s régulière,
snapshots jusqu'à t=2370, **snapshot final exact à t=2391,3**, aucun timestamp
dupliqué, 26 colonnes cohérentes, export Excel final réussi (`[EXCEL] Export Excel #6
reussi`). **A.2 (diagnostic commandes bloquées) validé fonctionnellement** :
`[DIAG-BLOQUEE]` réellement observé sur `REAPPRO_1`. Deux problèmes résiduels
identifiés par analyse croisée Excel/ABox/CSV, traités ici.

#### A.4-FIX-5A — ABox finale absente

**Investigation menée avant toute modification** :

1. **`aboxExportActif`** : déclaré `public boolean aboxExportActif = true;` (défaut
   codé en dur), rechargé depuis le JSON via `jsonBool(am,"enabled",true)` — donc
   `true` par défaut, sauf configuration explicite contraire.
2. **`aboxExportSurArret`** : déclaré `public boolean aboxExportSurArret = false;`
   (défaut codé en dur), rechargé depuis le JSON via
   `jsonBool(am,"exportOnStop",false)` — **`false` par défaut**, sauf activation
   explicite `"exportOnStop": true` dans le scénario JSON.
3. **`exporterABoxRuntimeTTL(String raison)`** : commence par
   `if (!aboxExportActif) return "";` (garde interne supplémentaire, cohérente avec
   le point 1). Construit un `run:exportReason` et un `run:simulationTimeSeconds`
   à partir de `raison` et `time()` au moment de l'appel — mécanisme sain, aucune
   anomalie trouvée ici.
4. **Nom de fichier** : `"SCONTO_SVU_ABOX_" + aboxSafeId(nomEntreprise) + "_" +
   aboxEnsureRunId() + ".ttl"`, où `aboxEnsureRunId()` calcule `aboxRunId` **une
   seule fois par run** (`if (aboxRunId == null || aboxRunId.isEmpty())`, mis en
   cache pour tout le run) — donc **toutes les exportations ABox d'un même run
   écrivent dans EXACTEMENT LE MÊME FICHIER et se remplacent mutuellement** (pas de
   suffixe temporel variable par export, contrairement à la convention `RUN_<t1>_<t2>`
   décrite dans `reference/colleague/docs/SCENARIOS_AND_DATA.md` — **divergence
   documentaire notée** : cette doc semble décrire un comportement plus ancien ou
   différent du code actuel du master ; le code fait foi). Ce n'est pas un défaut :
   cela signifie qu'un export réussi écrase simplement le précédent, donc que le
   fichier `.ttl` présent sur disque reflète toujours le DERNIER export réussi.
5. **Cause exacte établie** : `finaliserRunEtExporter()` gardait son export ABox
   derrière `aboxExportActif && aboxExportSurArret` (fidèle au code original
   d'`arreterSimulation()` avant tout portage). Pour le scénario du run analysé,
   `aboxExportSurArret=false` — **l'appel n'a donc jamais eu lieu**, ce qui est le
   comportement STRICTEMENT ATTENDU compte tenu de cette configuration. Le dernier
   export ABox réussi restait celui de la clôture de `CMD_6`
   (`exportReason=ORDER_CLOSED_CMD_6`), écrit par le mécanisme de clôture de
   commande (C14, `aboxExportSurClotureCommande`, **inchangé**), qui n'a plus été
   réécrit depuis faute d'un événement déclencheur postérieur (aucune commande
   close après CMD_6, et le point 5B ci-dessous explique pourquoi la finalisation
   elle-même n'a pas non plus produit un déclencheur ABox par défaut).

**Décision** : **aucun changement de sémantique** apporté à `aboxExportSurArret` — ce
réglage scénario existant (`"exportOnStop"`) est respecté tel quel, ne pas en
présumer une intention différente sans audit complet demandé par l'utilisateur.
**Correctif appliqué = observabilité, pas changement de comportement** : ajout de
logs explicites (voir section Logging ci-dessous) pour que ce SKIP, auparavant
totalement silencieux, soit désormais visible et explicite dans le journal
(`[FINALIZE] ABox finale SKIP : aboxExportActif=... ; aboxExportSurArret=...`).
**Recommandation utilisateur** : pour obtenir systématiquement un TTL final
synchronisé avec l'Excel final à chaque arrêt, activer `"exportOnStop": true` dans
le scénario JSON — décision volontairement laissée à l'utilisateur, cette bascule
existante n'appartenant pas au périmètre de ce correctif.

#### Logging finalisation (toutes les étapes de `finaliserRunEtExporter()`)

Ajout de `board.logEvent(...)` explicites à chaque étape, remplaçant les
`catch (Throwable ignored...) {}` silencieux par des traces non destructives mais
visibles :
- `[FINALIZE] Dashboard final capture t=...`
- `[FINALIZE-ERROR] Dashboard : ...` (si exception)
- `[FINALIZE] ABox finale exportee <fichier> | t=...` (si le garde `aboxExportActif
  && aboxExportSurArret` est satisfait)
- `[FINALIZE] ABox finale SKIP : aboxExportActif=... ; aboxExportSurArret=...` (sinon)
- `[FINALIZE-ERROR] ABox : ...` (si exception)
- `[FINALIZE] Excel final exporte t=...`
- `[FINALIZE] Excel final SKIP : exportExcelActif=false` (sinon)
- `[FINALIZE-ERROR] Excel : ...` (si exception)
- `[FINALIZE] finishSimulation demande = true/false` (dans `arreterSimulation()`,
  après l'appel, voir A.4-FIX-5B)

**Robustesse `runFinalise`** : stratégie **simple** retenue (un seul drapeau,
positionné à `true` avant les exports), documentée explicitement dans le code :
un export qui échoue ne sera pas retenté par un second appel (idempotence
prioritaire sur la reprise automatique), mais l'échec reste visible via
`[FINALIZE-ERROR]`. Pas de séparation en 3 drapeaux (`dashboardFinalCapture`/
`aboxFinalExportee`/`excelFinalExporte`) — jugée non nécessaire au regard de
l'objectif (idempotence + visibilité, pas résilience/reprise).

#### A.4-FIX-5B — terminaison réelle du moteur AnyLogic

**Observation du run réel** : après `[T=2391.3] === SIMULATION ARRETEE - PI=7.809
===` et `[T=2391.3] [EXCEL] Export Excel #6 reussi`, le journal continuait avec
`[T=2400.0] [HOLON-STRAT] ...` puis `[T=2400.0] [DIAG-BLOQUEE] ...`, et l'interface
est restée active jusqu'à environ t=2477. **`modeExecution=false` et
`arrivee.reset()` n'arrêtent que la logique métier du modèle, pas le moteur de
simulation AnyLogic lui-même**, qui continue à faire avancer le temps et déclencher
les événements cycliques (`bilanPeriodique`, `DashboardHistoryManager`, etc.) tant
qu'il n'est pas explicitement arrêté.

**API utilisée** : `Agent.finishSimulation()` (héritée par `Main`, qui étend
`Agent`), appelée directement comme `finishSimulation()`. D'après la documentation
de l'API AnyLogic (méthode stable, présente depuis plusieurs versions majeures) :
termine la simulation après l'événement courant, sans détruire immédiatement le
modèle — les résultats restent consultables. C'est la sémantique demandée
(privilégiée à `getEngine().finish()`/`stopSimulation()`, non utilisées).
**Signature utilisée** : `boolean finishSimulation()` (sans argument, retour
booléen indiquant si la demande a été acceptée).

**Aucun usage préalable de cette API dans `model/SCONTO_SVU_GENERIC_MASTER.alp` ni
dans `reference/colleague/`** — vérifié par grep, aucun résultat des deux côtés.
**Cette signature n'a donc pas pu être confirmée par compilation locale** (aucun
outil de build AnyLogic disponible dans cet environnement) : elle repose sur la
documentation Agent de l'API AnyLogic 8.9.x. **Le Build AnyLogic de l'utilisateur
reste la validation de référence**, comme pour l'ensemble de cette fusion.

**Emplacement exact** : dans `arreterSimulation()`, après `finaliserRunEtExporter()`
(donc après capture Dashboard finale + export ABox + export Excel), conformément à
l'ordre demandé :
```java
modeExecution = false;
arrivee.reset();
strategic.piGlobalCourant = strategic.calculerPIGlobal();
board.logEvent("=== SIMULATION ARRETEE - PI=... ===");
finaliserRunEtExporter();
boolean finishOk = finishSimulation();
board.logEvent("[FINALIZE] finishSimulation demande = " + finishOk);
```

**Fichier modifié** : `model/SCONTO_SVU_GENERIC_MASTER.alp`.

**Ce qui n'a pas été touché** : aucun changement aux snapshots C14 de clôture de
commande, à `c14SnapshotFinalEffectue`, à `calculerPIGlobal()`/PI-SCOR, ni à la
fondation multi-produit (`stockFiniParProduit`, `synchroniserListeProduits()`, etc.)
— confirmé par l'emplacement des deux seuls blocs de diff (`finaliserRunEtExporter()`
et `arreterSimulation()`).

**Validations statiques** :
- XML bien formé : OK.
- IDs AnyLogic : 1679/1679 uniques, inchangé (uniquement du code Java libre modifié/
  ajouté, aucun élément `<Function>`/`<Variable>` AnyLogic ajouté).
- `git diff --check` : aucune erreur d'espace blanc.
- Grep DataCo : 0 occurrence.
- Diff confiné à 2 fonctions (`finaliserRunEtExporter()` lignes ~7129-7186,
  `arreterSimulation()` lignes ~11868-11901) : aucun changement C14/PI-SCOR/
  multi-produit, vérifié par les plages de lignes du diff.
- **Build AnyLogic** : EN ATTENTE (utilisateur) — vérification de compilation de
  `finishSimulation()` en particulier.
- **Run** : EN ATTENTE (utilisateur). Protocole suggéré : run > 900 s, clic sur
  "Arreter et voir resultats", puis vérifier (1) le moteur s'arrête réellement peu
  après (plus d'événements `[HOLON-STRAT]`/`[DIAG-BLOQUEE]` après le log
  `[FINALIZE] finishSimulation demande=...`) ; (2) présence des nouveaux logs
  `[FINALIZE]` ; (3) si `"exportOnStop": true` est activé dans le scénario, présence
  d'un TTL `RUN_FINALIZED` avec un `simulationTimeSeconds` proche du temps d'arrêt
  réel ; (4) sinon, présence du log `[FINALIZE] ABox finale SKIP` expliquant
  l'absence.
- **Commit** : voir SHA ci-dessous (message `fix(generic): finalize and finish model execution`).

**Bloc A.4 : validation définitive toujours EN ATTENTE du run post A.4-FIX-5.**

### Validation utilisateur définitive — Bloc A.4 (2026-09-17, commit `0da7d92`)

Run analysé sur console complète, Excel final, ABox TTL finale et CSV.

- **Build AnyLogic** : OK.
- **Run** : OK — Tfinal console = 2161,8 s, PI final = 7,896.
- **Séquence de finalisation observée**, cohérente avec l'ordre implémenté :
  ```
  [T=2161.8] === SIMULATION ARRETEE - PI=7.896 ===
  [T=2161.8] [FINALIZE] Dashboard final capture t=2161.8
  [T=2161.8] [S2.2-ABOX] ... raison=RUN_FINALIZED
  [T=2161.8] [FINALIZE] ABox finale exportee ...
  [T=2161.8] [EXCEL] Export Excel #6 reussi ...
  [T=2161.8] [FINALIZE] Excel final exporte t=2161.8
  [T=2161.8] [FINALIZE] finishSimulation demande = true
  ```
  **Aucun événement métier après Tfinal — le moteur AnyLogic s'arrête réellement**
  (confirme A.4-FIX-5B : `finishSimulation()` fonctionne comme documenté).
- **A.4 Historique Dashboard** : VALIDÉ — 73 snapshots, 73 timestamps uniques,
  initial=48,3, cadence périodique 30s (60, 90, ... 2160), final exact=2161,8,
  PI final=7,896, aucune duplication.
- **A.4 ABox RUN_FINALIZED** : VALIDÉ — `runId=RUN_1773129600000_1789659541911`,
  `exportReason=RUN_FINALIZED`, `simulationTimeSeconds=2161,75`, `RawEvent=975`,
  TTL syntaxiquement valide. Ce run avait donc `"exportOnStop": true` activé
  (cf. A.4-FIX-5A) — confirme que le chemin `aboxExportSurArret=true` fonctionne
  correctement une fois activé par l'utilisateur.
- **A.4 finishSimulation** : VALIDÉ — moteur réellement arrêté, aucune activité
  résiduelle observée.
- **Cohérence croisée** : 975 événements "Execution Brute" Excel == 975 `RawEvent`
  ABox ; Dashboard Global PI=7,896 cohérent partout ; 0 erreur Excel
  (`#REF!`/`#DIV/0!`/`#VALUE!`/`#NAME?`/`#N/A`).
- **A.2 diagnostic `[DIAG-BLOQUEE]`** : **VALIDÉ FONCTIONNELLEMENT** — observé
  réellement sur `REAPPRO_1` lors du run précédent (post A.4-FIX-4).
- **CSV** : non synchronisé avec la finalisation (exporté manuellement vers
  t≈2133/2477 selon les runs, avant l'arrêt) — **comportement attendu, pas un
  défaut A.4** (le CSV est un mécanisme totalement indépendant, cf. A.4-FIX-5A).
  Synchronisation éventuelle à revoir dans un futur bloc si souhaité.
- **Point mineur noté pour un futur bloc (A.4 non rouvert pour cela)** : la feuille
  "Synthèse C14" affiche `exports=5` alors que l'export final réel est `#6`
  (compteur probablement lu avant son incrément) — cosmétique, sans impact sur les
  données exportées.

**BLOC A.4 : STATUT FINAL = TERMINÉ / FIGÉ.**

## Bloc A.5 — cohérence des états holoniques (2026-09-17)

**Objectif** : uniformiser la détermination et la représentation des états des agents
holoniques (Coordinateur, Supervisor/OperationalPilot, OperationalExecution), sans
modifier le comportement métier.

### Audit master vs collègue (avant modification)

| Fonction | Master (avant) | Collègue | Différence | Dépendances | Risque | Décision |
|---|---|---|---|---|---|---|
| `etatCoordinateurMacro()` | **Absente** | Présente (`Main`, C14.55) — calcule l'état ESCALADE/AJUSTEMENT/SURVEILLANCE d'un Coordinateur et le mémorise dans `sv.etatAgent`/`sv.tEntreeEtat` | Fonction manquante côté master | Lit `supervisorsMacro`, `opAgents`, `tacticals` (déjà tous présents et identiques) | Faible — logique de détection strictement identique à celle déjà dans `couleurSupervisorMacro()` du master | **PORTER** telle quelle, aucune adaptation nécessaire |
| `couleurSupervisorMacro()` | Calcule la couleur en DIRECT, dupliquant intégralement (mêmes variables, mêmes commentaires C14.27/C14.51) la logique de détection goulot/escalade | Délègue à `etatCoordinateurMacro()` puis mappe le résultat en couleur | Master duplique la logique ; collègue l'a factorisée après avoir ajouté la fonction source unique | `etatCoordinateurMacro()` (à porter) | Faible — pur refactor de délégation, résultat identique | **ADAPTER** : refactoriser pour déléguer, comme le collègue |
| `popupSupervisor()` | Affiche `sv.etatAgent` (texte d'état) et `sv.nbAlertesTraitees`/`sv.nbReequilibrages`/`sv.dernierGoulot` | Affiche `etatCoordinateurMacro(macro)` (avec repli sur `sv.etatAgent`) et `sv.nbMessagesHierarchiquesRecus`/`sv.dernierMessageHierarchique` | **Bug confirmé dans le master** : `sv.etatAgent` n'est écrit QUE par `traiterAlertesTactiques()`, qui retourne à sa 1ère ligne réelle dès que `realignementFluxHierarchiqueActif=true` (routage "génération 2", **actif par défaut**, confirmé `= true`) — `sv.etatAgent` reste donc figé à sa valeur d'initialisation `"IDLE"` **à vie**. Un Coordinateur affiché en ROUGE peut donc montrer un popup "Inactif / en attente". Même cause racine pour `nbAlertesTraitees`/`nbReequilibrages`/`dernierGoulot`, alimentés uniquement par le même circuit mort (`recevoirAlerteGoulot()`/`prendreDecisionAHP()`, tous deux inatteignables sous génération 2) | `etatCoordinateurMacro()` (à porter) ; `sv.nbMessagesHierarchiquesRecus`/`sv.dernierMessageHierarchique` — **déjà présents et alimentés dans le master**, byte-identiques au collègue (bloc "BOITE HIERARCHIQUE GENERATION 2", `recevoirMessageHierarchique()`, vérifié sur les 4 classes StrategicAgent/TacticalAgent/CoordinatorAgent/OperationalAgent) | Faible — tous les compteurs de remplacement existent déjà et sont déjà alimentés ; aucune nouvelle donnée à faire vivre | **PORTER** : texte d'état via la source unique + remplacement des 3 compteurs morts par les compteurs déjà vivants |
| `popupOperationalAgent()` | Utilise `p.goulot`, un **flag de groupe** écrit identiquement sur tous les postes du groupe par `analyserEtat()` dès qu'un seul déclenche GOULOT | Recalcule un état **propre à chaque poste individuel** (mêmes seuils `op.seuilAlertFile`/`seuilGoulotWT`, entités métier réelles uniquement) | **Bug confirmé** (C14.53) : des micro-activités s'affichent "GOULOT" alors qu'elles n'ont encore traité aucune unité, simplement parce qu'un AUTRE poste du même groupe est en goulot | `estFluxVisuelSeulement()`, `op.seuilAlertFile`, `op.seuilGoulotWT` — tous **déjà présents** dans le master | Faible — pure représentation, mêmes seuils que la détection de groupe déjà en place, aucune nouvelle définition de goulot | **PORTER** telle quelle |
| `ajusterDebits()` (`StrategicAgent`) | Ajuste `sc.debitParHeure` (débit de production MTS) à partir de `piGlobalCourant`, prévision de demande, écart de stock cible | Diffère uniquement sur des points **PI/production** : `pi = performanceDisponible ? piGlobalCourant : ciblePIGlobal` (amorçage PI), plafond `plafondMultipleDebitBase` (garde-fou débit) — **aucune ligne relative à IDLE/WORKING/GOULOT/PANNE/popup/couleur** | 100% logique de production/PI, sans rapport avec la représentation d'état holonique | `ciblePIGlobal`, `plafondMultipleDebitBase` — champs du Bloc B, absents du master | **Hors périmètre A.5** | **REPORTER au Bloc B intégralement** — rien porté ici |
| `analyserEtat()` (`OperationalAgent`) | (a) Garde `if (!ROLE_SUPERVISEUR && !ROLE_EXECUTION) return;` qui gèle les groupes Plan (rôle TACTIQUE) à `"IDLE"` à vie ; (b) un jeton visuel seul (ex. animation MTS) ne compte nulle part → poste affiché IDLE même quand une commande réelle le traverse | (a) Garde supprimée (C14.54) ; (b) `boolean visuelEnCours` détecte la présence d'un jeton visuel et bascule l'état sur `WORKING` transitoire au lieu de `IDLE`, **sans jamais** compter dans `fileReelle`/`wtMoyen`/GOULOT | Deux bugs de représentation confirmés (Plan figé, activité MTS invisible) ; **aucun changement des seuils/critères GOULOT/PANNE**, qui restent `tailleFile > seuilAlertFile \|\| wtMoyen > seuilGoulotWT`, identiques avant/après | Aucune — modifications autonomes, mêmes champs déjà présents | Faible — vérifié : la détection GOULOT/PANNE elle-même est bit-à-bit inchangée ; seule la branche IDLE/WORKING est affinée | **PORTER** les 2 correctifs (C14.52 + C14.54) ; **NE PAS toucher** au reste (détection goulot, émission AER, `p.goulot`, inchangés) |

**Confirmation empirique de la cause racine (avant tout portage)** :
- `realignementFluxHierarchiqueActif = true` (défaut codé en dur, master ligne ~7564) → routage génération 2 actif par défaut.
- `CoordinatorAgent.etatAgent` valeur d'initialisation = `"IDLE"` (vérifié dans la déclaration `<Variable>`).
- `traiterAlertesTactiques()` (master) : `if (main.realignementFluxHierarchiqueActif) return;` en toute première ligne utile → `etatAgent`/`nbAlertesTraitees`/`recevoirAlerteGoulot()` jamais atteints sous g2.
- `prendreDecisionAHP()` : `if (alertesGoulot.isEmpty()) return;` — `alertesGoulot` n'est peuplée que par `recevoirAlerteGoulot()`, lui-même mort sous g2 → `nbReequilibrages` également mort, par transitivité.
- `recevoirMessageHierarchique()`/`nbMessagesHierarchiquesRecus`/`dernierMessageHierarchique` : présents et **byte-identiques** au collègue sur les 4 classes concernées — confirmés vivants (mécanisme "génération 2" indépendant du circuit mort ci-dessus).

### Portage réalisé

**Fichier modifié** : `model/SCONTO_SVU_GENERIC_MASTER.alp`.

1. **Ajout `String etatCoordinateurMacro(String macro)`** (nouvelle `<Function>` sur `Main`,
   juste avant `couleurSupervisorMacro()`) : portage à l'identique de la fonction
   collègue — calcule l'état ESCALADE/AJUSTEMENT/SURVEILLANCE (même logique
   goulot/wtDepasse/reeqRecent que `couleurSupervisorMacro()` d'origine), et
   synchronise `sv.etatAgent`/`sv.tEntreeEtat` à chaque appel (au lieu de ne
   jamais les écrire sous génération 2).
2. **`couleurSupervisorMacro()` refactorisée** : délègue désormais à
   `etatCoordinateurMacro(macro)` puis mappe le résultat en couleur — résultat
   strictement identique à l'ancienne version (mêmes 4 couleurs, mêmes conditions),
   élimine la duplication de logique.
3. **`popupSupervisor()`** :
   - "État courant" utilise `etatCoordinateurMacro(macro)` (repli sur `sv.etatAgent`
     si `null`, ex. coordinateur sans OP rattaché) — ne peut plus jamais contredire
     la couleur du pavé ;
   - "Alertes traitées"/"Rééquilibrages"/"Dernier goulot" (toujours 0/0/"—")
     remplacés par "Messages hiérarchiques reçus"/"Dernier message" (déjà vivants).
4. **`popupOperationalAgent()`** : la boucle sur `op.postesLies` recalcule un état
   propre à chaque poste (`fileReellePoste`/`wtPoste`, mêmes seuils que
   `analyserEtat()`), au lieu de lire `p.goulot` (flag de groupe). Le préfixe
   `[idPoste]` est ajouté à chaque ligne (comme chez le collègue) pour identifier
   sans ambiguïté le poste concerné.
5. **`analyserEtat()`** : suppression de la garde de rôle (les groupes Plan
   reflètent désormais leur occupation réelle comme Source/Make/Deliver/Return) ;
   ajout de `visuelEnCours` (bascule IDLE→WORKING transitoire sur simple passage
   d'un jeton visuel, sans jamais alimenter GOULOT/PANNE).

### Ce qui n'a pas été porté (et pourquoi)

- **`ajusterDebits()` intégralement** : aucune ligne ne concerne la représentation
  d'état holonique ; toutes les différences (amorçage PI, plafond de débit) relèvent
  du Bloc B (PI/SCOR) et de la production — reporté sans exception.
- **Détection GOULOT/PANNE elle-même** (`tailleFile > seuilAlertFile || wtMoyen >
  seuilGoulotWT`, `p.enPanne`) : **strictement inchangée** dans `analyserEtat()`,
  `couleurSupervisorMacro()`/`etatCoordinateurMacro()` — aucune nouvelle définition
  scientifique du goulot introduite, conformément à la consigne.
- **`p.goulot`** (flag de groupe écrit par `analyserEtat()`) : toujours calculé et
  écrit à l'identique ; seul son usage en LECTURE dans le popup individuel a été
  remplacé par un recalcul par poste — le flag de groupe lui-même reste utilisé
  ailleurs (ex. `couleurSupervisorMacro`/`etatCoordinateurMacro` via `op.etatHolon`).

### Vérification des principes A.5

- **Source unique par holon** : Coordinateur → `etatCoordinateurMacro()` utilisé par
  couleur ET popup ; OperationalAgent → `etatHolon` (déjà unique, `analyserEtat()`)
  utilisé par couleur/popup de groupe, complété par un recalcul par poste
  strictement représentatif dans le popup individuel — pas une seconde source de
  vérité, un raffinement d'affichage à grain plus fin.
- **Pas de confusion Coordinateur / Supervisor-Pilot / OperationalExecution** :
  chaque fonction modifiée reste strictement dans le périmètre de sa propre classe
  (`CoordinatorAgent` pour `etatCoordinateurMacro`, `OperationalAgent` pour
  `analyserEtat`/`popupOperationalAgent`) ; aucun champ d'une classe lu par une
  fonction d'une autre classe au-delà de ce qui existait déjà.
- **Aucune contamination inter-macro-processus** : `etatCoordinateurMacro(macro)`
  filtre strictement les `OperationalAgent` de CE `macro` (`macroPrefixe(n3).equals(macro)`,
  inchangé) — un Coordinateur Deliver ne peut pas hériter d'un état Make.
- **Aucun hardcode ZENER/DataCo** : aucune chaîne de ce type introduite ; grep DataCo
  confirmé à 0.

### Tests à prévoir (non automatisables sans AnyLogic — protocole manuel suggéré)

- **H-1** (IDLE cohérent) : poste sans aucune activité → `analyserEtat()` retourne
  `IDLE` (visuelEnCours=false, positionOccupee=false) ; popup individuel affiche
  "en attente (aucune unité traitée)".
- **H-2** (WORKING cohérent) : poste avec entité métier réelle en file/traitement →
  `WORKING` partout (groupe et popup individuel).
- **H-3** (GOULOT réel) : `fileReellePoste > seuilAlertFile` ou `wtPoste > seuilGoulotWT`
  sur au moins un poste → ce poste affiche "⚠️ GOULOT (file=…, attente=…s)" dans le
  popup individuel ; les autres postes du même groupe, non en goulot, ne l'affichent
  plus (contrairement à l'ancien comportement `p.goulot` de groupe).
- **H-4** (PANNE réelle) : `p.enPanne=true` sur un poste → priorité absolue,
  "🟣 EN PANNE" affiché pour CE poste uniquement dans le popup individuel.
- **H-5** (pas de contamination inter-macro) : un Coordinateur Deliver en
  SURVEILLANCE ne doit jamais afficher ESCALADE simplement parce que Make est en
  ESCALADE — vérifié par le filtre `macroPrefixe(n3).equals(macro)` dans
  `etatCoordinateurMacro()`, inchangé du master.
- **H-6** (popup/couleur/texte cohérents) : cliquer sur un Coordinateur affiché en
  ROUGE (escalade) → le popup doit désormais afficher "État courant : Escalade"
  (au lieu de "Inactif / en attente" avant ce bloc).

### Validations statiques

- XML bien formé : OK.
- IDs AnyLogic : 1655/1655 uniques (+1 pour le nouvel élément `<Function>`
  `etatCoordinateurMacro`), aucun doublon.
- `git diff --check` : aucune erreur d'espace blanc.
- Grep DataCo : 0 occurrence.
- Diff confiné à 3 zones (`etatCoordinateurMacro`/`couleurSupervisorMacro` ~L21879-
  21990 ; `popupOperationalAgent`/`popupSupervisor` ~L22075-22260 ;
  `analyserEtat` ~L50554-50762) — **aucun changement** à `ajusterDebits()`,
  `calculerPIGlobal()`, aux fonctions multi-produit
  (`stockFiniParProduit`/`synchroniserListeProduits`), aux stocks, commandes,
  routage, génération de commandes, ordonnancement MTO, ou exports.
- **Build AnyLogic** : EN ATTENTE (utilisateur).
- **Run** : EN ATTENTE (utilisateur). Protocole suggéré : run court générique
  (ZENER ou autre), observer au moins un Coordinateur passer en rouge (escalade)
  et vérifier que son popup dit "Escalade" (pas "Inactif / en attente") ; ouvrir le
  popup d'un `OperationalAgent` en goulot de groupe et vérifier que seuls les
  postes individuellement en goulot l'affichent.
- **Commit** : `e7652ed` (message `feat(generic): unify holonic agent states`).

### Validation utilisateur définitive — Bloc A.5 (2026-09-17)

Run analysé sur Excel final, CSV brut/agrégé, CSV KPI, ABox TTL finale, observation
runtime.

- **Build AnyLogic** : OK.
- **Coordinateur ESCALADE réel observé et justifié** : un Coordinateur est
  réellement passé au ROUGE pendant le run, corrélé à un vrai goulot Make
  (`ACT_4|M1.2` avgWaitTime≈509,4s ; `ACT_4|M1.3` avgWaitTime≈33,5s ; audit AER
  ~t=1095-1097 : `sM1.2.1` GOULOT WT≈1027s file=179, `sM1.3.1` GOULOT WT≈247s
  file=4). Chaîne AER observée : OperationalExecution → AOp-sM1.1 → CA-sM1 →
  AT-sP3 → CA-sM1 → AOp-sM1.1 → OperationalExecution. **La branche
  ESCALADE/rouge a donc été réellement exercée**, et comme
  `couleurSupervisorMacro()`/`popupSupervisor()` dérivent désormais tous deux de
  `etatCoordinateurMacro()`, le problème historique "pavé rouge / popup IDLE" est
  **considéré corrigé**. Goulot correctement circonscrit à Make/CA-sM1, aucune
  contamination inter-macro anormale constatée (confirme H-3/H-5).
- **Non-régression A.4** : Tfinal=1117,9s ; ABox `reason=RUN_FINALIZED`,
  `simulationTimeSeconds=1117,9`, `RawEvent=539` == 539 événements Excel
  "Execution Brute" ; Historique Dashboard 39 snapshots/39 timestamps uniques,
  dernier=1117,9, PI final≈8,15 (CSV KPI `PI_GLOBAL=8,1499`, cohérent) ; 0 erreur
  Excel, 0 exception runtime.
- **Non-régression du retrait de la garde de rôle (`analyserEtat()`)** : un flux
  Plan réel observé (`P3.4 / PLANIFICATION_PRODUCTION_COMMANDE`) — confirme que
  les groupes Plan reflètent maintenant une activité réelle sans effet de bord
  négatif observé sur ce run.

**BLOC A.5 : VALIDÉ.**

## BLOC A — STATUT GLOBAL : TERMINÉ / FIGÉ (2026-09-17)

A.1 (matching strict), A.2 (diagnostic commandes bloquées), A.3 (stock matière
détaillé), A.4 (historique Dashboard/Excel/ABox/finalisation moteur) et A.5
(cohérence des états holoniques) sont tous portés et validés par l'utilisateur sur
runs réels. **A.1–A.5 ne seront plus modifiés sauf bug démontré par un nouveau run.**
Poursuite exclusive avec le Bloc M (fondation multi-produit Generic).

## Bloc M — Fondation multi-produit Generic (2026-09-16, M.1 EN COURS depuis 2026-09-17)

**Ordonnancement décidé** : après les blocs SAFE A.3/A.4/A.5, avant la refonte PI/SCOR
du Bloc B (le multi-produit influence stocks, demande, réappro, Make, stratégique et
plusieurs KPI — architecture à stabiliser avant de finaliser PI/SCOR).

**Fondation existante dans le master à auditer avant toute implémentation (ne pas
supprimer/réécrire aveuglément)** :
- Variables : `modeMultiProduitActif`, `rotationProduitsActive`, `nomProduitParDefaut`,
  `LigneCommandeProduit`, `listeProduits`, `catalogueProduits`, `stockFiniParProduit`,
  `lignesProduitParCommande`.
- Fonctions : `synchroniserListeProduits()`, `scenarioProduitParNom()`,
  `scenarioProduitParDefaut()`, `choisirScenarioProduit()`,
  `enregistrerLigneProduitCommande()`, `stockFiniDisponiblePourScenario()`,
  `consommerStockFiniProduit()`, `verifierPolitiqueStockProduit()`.

**Nouvelle source donneuse (technique uniquement)** :
`reference/dataco-multiproduct/SCONTO_SVU_FINAL_VALIDATED_FORECAST_DATACO_MULTIPRODUCT_CONCURRENT_FIX.alp`
(2 244 316 octets — nom réel différent de celui annoncé initialement
`SCONTO_SVU_DATACO_MULTIPRODUCT_REFERENCE.alp`, cf. aparté ci-dessus). Donneur pour les
seuls mécanismes multi-produit génériques : `stockInitialParProduit`,
`sommeStockFiniParProduit()`, `synchroniserStockFiniAgrege()`,
`stockInitialConfigurePourProduit()`, `initialiserStocksProduits()`,
`crediterStockFiniProduit()`, `consommerStockFiniProduit()`,
`stockFiniDisponiblePourScenario()`, initialisation/sauvegarde JSON multi-produit,
politique autonome par produit, correction `ConcurrentModificationException` par
snapshot stable.

**Interdiction absolue** : ne jamais porter depuis cette référence
`DATACO_SPORTS`/`DATACO_CLOTHING`/`DATACO_ELECTRONICS`, Prophet, Recalibrator,
AutoCommande DataCo, calendrier 2017, fichiers/vues Forecast DataCo, logique de demande
DataCo, ou tout nom/acteur spécifique DataCo.

**Invariants du futur multi-produit Generic** (13, résumés) :
1. Compatibilité mono-produit totale (`modeMultiProduitActif=false` par défaut,
   comportement historique inchangé).
2. Source de vérité unique : mono-produit → `niveauStock` ; multi-produit →
   `stockFiniParProduit` (agrégat `niveauStock` = somme, affichage/KPI seulement).
3. Jamais de duplication du stock global entre produits (répartition, pas multiplication).
4. JSON peut fournir optionnellement `modeMultiProduitActif` + `stockInitialParProduit`.
5. Aucun nombre de produits codé en dur (N produits).
6. Aucun nom de produit codé en dur.
7. Une référence ne consomme jamais le stock d'une autre.
8. La production d'une référence crédite uniquement cette référence.
9. Réapprovisionnement calculé par produit.
10. Snapshot stable pour toute boucle multi-produit itérant une collection
    reconstructible par une fonction appelée (anti-ConcurrentModificationException).
11. `rotationProduitsActive` reste un outil de test générique, `false` par défaut,
    jamais une règle métier par défaut.
12. Ne pas assimiler automatiquement tout scénario à un produit — respecter la
    séparation scénario/produit existante, à analyser avant modification.
13. ZENER actuel doit continuer à fonctionner exactement comme avant si le
    multi-produit n'est pas activé.

**Tests attendus (M-1 à M-10)** :
- [ ] M-1 — legacy mono-produit ZENER (`modeMultiProduitActif=false`) = comportement identique à la baseline
- [ ] M-2 — multi-produit synthétique 2 produits : stock A indépendant du stock B
- [ ] M-3 — consommation : commande A ne modifie pas stock B
- [ ] M-4 — production : production A crédite uniquement A
- [ ] M-5 — stock global : somme(stockFiniParProduit) == niveauStock agrégé
- [ ] M-6 — JSON sans nouveaux champs : compatibilité descendante
- [ ] M-7 — JSON avec stockInitialParProduit : valeurs exactes restaurées
- [ ] M-8 — JSON avec stock global mais sans répartition : aucune multiplication du stock
- [ ] M-9 — politique autonome : rupture A ne déclenche pas artificiellement une production B
- [ ] M-10 — concurrence : aucune ConcurrentModificationException lors du parcours produit

**Statut** : **M.1 EN COURS** (audit + source de vérité + initialisation portés,
2026-09-17). M.2 (consommation/crédit complets), réapprovisionnement, UI restent à
faire.

### Bloc M.1 — audit, source de vérité, initialisation (2026-09-17)

**Rappel de séparation** : mission strictement Generic. `reference/dataco-multiproduct/`
n'est utilisée QUE comme référence technique pour des mécanismes multi-produit
génériques déjà éprouvés — aucune donnée/logique métier DataCo (Prophet,
Recalibrator, AutoCommande, catalogue SPORTS/CLOTHING/ELECTRONICS, calendrier 2017)
n'est importée. Contrôlé par grep DataCo après modification : 0 occurrence.

#### Tableau d'audit (avant modification)

| Mécanisme | Master Generic actuel | DataCo référence | Risque | Décision | Adaptation générique |
|---|---|---|---|---|---|
| `modeMultiProduitActif` | `false` par défaut, **jamais chargé depuis le JSON** (aucun `jsonBool(...)` correspondant) | Idem défaut, chargé via `jsonBool(pg,"modeMultiProduitActif",false)` | Faible | **PORTER** le chargement JSON (absent = comportement historique inchangé) | Identique |
| `rotationProduitsActive` | `false` par défaut, **jamais chargé depuis le JSON** | Idem, chargé via JSON | Faible | **PORTER** le chargement JSON | Identique |
| `stockInitialParProduit` | **Absent du master** | Présent : `LinkedHashMap<String,Double>` optionnelle, JSON `"stockInitialParProduit"` | Faible — nouveau champ additif, aucun ancien JSON ne le contient (comportement inchangé si absent) | **PORTER** tel quel (champ + chargement + sauvegarde) | Identique |
| `LigneCommandeProduit`, `listeProduits`, `catalogueProduits`, `lignesProduitParCommande` | Présents, **byte-identiques** au DataCo (mêmes champs, mêmes types) | Identiques | Aucun | Inchangés | — |
| `stockFiniParProduit` | Présent, structure identique | Identique | Aucun | Inchangé (seul son *contenu initial* était buggé, voir `initialiserStocksProduits()`) | — |
| `synchroniserListeProduits()` | Byte-identique au DataCo | Identique | Aucun | Inchangée | — |
| `choisirScenarioProduit()` | Byte-identique au DataCo | Identique | Aucun | Inchangée (réapprovisionnement/sélection produit = hors scope M.1) | — |
| `enregistrerLigneProduitCommande()` | Byte-identique au DataCo | Identique | Aucun | Inchangée | — |
| **`initialiserStocksProduits()`** | **BUG CONFIRMÉ** : `stockFiniParProduit.put(cle, Math.max(0.0, champStockInitialProduitFini))` pour **chaque** produit — un stock global de 18000 avec 3 produits donne 18000+18000+18000=54000. Déjà auto-documenté comme défaut connu par le commentaire C14.10/C14.12 du master lui-même (« si le mode multi-produit est un jour réactivé, il faudra ici synchroniser... aligner leurs bases initiales ») | **Déjà corrigée** : `modeMultiProduitActif ? stockInitialConfigurePourProduit(sc,n) : champStockInitialProduitFini`, puis `synchroniserStockFiniAgrege(null)` | **Élevé si activé tel quel** — c'est exactement le bug de duplication interdit par la mission | **PORTER** la version corrigée intégralement | Identique — c'est le cœur du correctif M.1 |
| **`stockFiniDisponiblePourScenario()`** | **Fuite d'isolation confirmée** : si la clé produit est absente de `stockFiniParProduit` en mode multi-produit, retombe sur `fallback.niveauStock` (le stock **agrégé** de toutes les références) — un produit pourrait alors utiliser le stock d'un autre | **Déjà corrigée** : retourne `0.0` (rien de disponible) au lieu de l'agrégat | Moyen — viole directement l'invariant « une référence ne consomme jamais le stock d'une autre » | **PORTER** le correctif (repli sur 0, jamais l'agrégat) | Identique |
| `consommerStockFiniProduit()` | Structure saine (branches mono/multi déjà correctement séparées), mais **n'appelle pas** de resynchronisation de l'agrégat après consommation (gap déjà auto-documenté par le master) | Identique + appel final à `synchroniserStockFiniAgrege(fallback)` | Faible, mais fait partie de la « logique complète de consommation » | **REPORTER au sous-bloc M suivant** (hors périmètre M.1, qui se limite à source de vérité + initialisation) ; commentaire du master mis à jour pour refléter l'état actuel (fonction disponible mais pas encore appelée ici) | — |
| **`crediterStockFiniProduit()`** | **Absent du master** — aucune fonction générique de crédit de stock par produit (la production crédite directement `niveauStock`, sans awareness multi-produit) | Présent : branche mono (crédite `fallback.niveauStock`) / multi (crédite `stockFiniParProduit` + `synchroniserStockFiniAgrege()`), log `[MULTI-PRODUIT][WARN]` si produit inconnu | Moyen — fonction de crédit, cœur de la « logique complète de consommation/crédit » | **REPORTER au sous-bloc M suivant** (hors périmètre M.1) | — |
| `verifierPolitiqueStockProduit()` | **Mono-scénario uniquement** — ne boucle sur aucun produit, ne référence même pas `modeMultiProduitActif` ; gère la politique (s,Q) d'un seul `scRef` (scénario nominal/premier) | Fonction équivalente non auditée en détail (hors périmètre M.1) | Élevé si étendu sans précaution — c'est le réapprovisionnement, explicitement exclu de M.1 | **REPORTER au sous-bloc M suivant** (« logique complète de consommation/crédit ; réapprovisionnement » explicitement exclus de M.1) | — |
| `new ArrayList<ScenarioFlux>(listeProduits)` (snapshot stable) | Pattern déjà utilisé ailleurs dans le master pour d'autres listes (ex. `listeProduits` snapshot antérieur au Bloc M, cf. commentaire C14.68 sur `listeProduits`) ; aucune boucle multi-produit encore assez développée pour risquer une `ConcurrentModificationException` à ce stade (M.1 n'ajoute que des fonctions de lecture/agrégat, aucune boucle réentrante) | `ConcurrentModificationException` déjà rencontrée et corrigée côté DataCo | Aucun risque introduit par M.1 (pas de nouvelle boucle réentrante) | **REPORTER** l'audit complet des boucles à risque au sous-bloc M suivant, quand la logique de consommation/réappro par produit sera portée | — |
| **ScenarioFlux ≠ Produit** | `estProduitEnregistrable(sc)` traite **tout** `ScenarioFlux` non marqué « cas de test » (`estScenarioCasTest()`) comme un produit catalogable. Il n'existe **aucune notion de SKU/Produit distincte** de `ScenarioFlux` dans ce mécanisme (le type `Produit`/`produitRegistry` vu dans `nombreProduitsRuntimeUniques()` est un concept **différent** : instances physiques runtime traversant la chaîne, pas le catalogue produit) | Convention identique côté DataCo | Conceptuel — ne pas transformer silencieusement chaque scénario de simulation en SKU commercial | **Documenté explicitement ici, aucun changement de convention en M.1** — un scénario de test (nomenclature de validation, ex. `SCENARIO DISTRIBUTION`, `ZENER CAS 1/2/3`) est déjà exclu via `estScenarioCasTest()` ; tout scénario NON marqué comme cas de test EST actuellement considéré comme un produit catalogable, y compris sur ZENER (un seul scénario nominal ⇒ un seul « produit » dans le catalogue, sans effet tant que `modeMultiProduitActif=false`) | — |

#### Ce qui a été porté (M.1)

**Fichier modifié** : `model/SCONTO_SVU_GENERIC_MASTER.alp`.

1. **`stockInitialParProduit`** : nouveau champ `LinkedHashMap<String,Double>` (Main),
   configuration JSON optionnelle des stocks initiaux par produit.
2. **`sommeStockFiniParProduit()`** : somme des valeurs de `stockFiniParProduit`
   (clamp négatif/NaN/Infini).
3. **`synchroniserStockFiniAgrege(PosteGenericAgent fallback)`** : synchronise
   `niveauStock` (tous les postes stock fini, ou le fallback) depuis la somme
   ci-dessus — **no-op tant que `modeMultiProduitActif=false`**, implémentant
   l'invariant demandé (mono-produit : `niveauStock` reste l'unique source de
   vérité ; multi-produit : `stockFiniParProduit` devient la source, `niveauStock`
   n'est plus qu'un agrégat de compatibilité, synchronisé **dans ce sens
   uniquement**, jamais l'inverse).
4. **`stockInitialConfigurePourProduit(ScenarioFlux sc, int nbProduits)`** : valeur
   explicite du JSON si configurée pour ce produit, sinon
   `champStockInitialProduitFini / nbProduits` (répartition équitable) — **jamais**
   une duplication du stock global.
5. **`initialiserStocksProduits()` corrigée** : chaque produit reçoit
   `stockInitialConfigurePourProduit()` en mode multi-produit (au lieu du stock
   global dupliqué N fois), ou le comportement historique inchangé en mono-produit ;
   appelle `synchroniserStockFiniAgrege(null)` en fin de fonction.
6. **`stockFiniDisponiblePourScenario()` corrigée** : une clé produit absente
   retourne `0.0` en mode multi-produit, plus jamais l'agrégat `fallback.niveauStock`
   (empêche qu'une référence "emprunte" le stock d'une autre).
7. **JSON générique** : `modeMultiProduitActif`, `rotationProduitsActive` et
   `stockInitialParProduit` sont désormais chargés (`jsonBool`/map optionnelle,
   valeurs par défaut = comportement historique) et sauvegardés
   (`parametresGlobaux`), symétriquement au chargement DataCo audité — **sans
   toucher à aucun autre champ JSON existant**.

#### Ce qui a été adapté

Aucune adaptation de logique n'a été nécessaire : les fonctions portées sont
**byte-identiques** à la référence DataCo (mécanismes génériques purs, aucune
dépendance à `stockFiniParProduit`/Prophet/Recalibrator/catalogue DataCo). Seul le
commentaire de `consommerStockFiniProduit()` a été réécrit pour refléter l'état
actuel (le gap qu'il documentait est partiellement outillé par M.1, mais pas encore
comblé — reporté explicitement).

#### Ce qui n'a pas été porté (et pourquoi) — reporté au sous-bloc M suivant

- **`crediterStockFiniProduit()`** : fonction de crédit générique par produit,
  absente du master — c'est la « logique complète de consommation/crédit »
  explicitement exclue de M.1.
- **Appel de `synchroniserStockFiniAgrege()` dans `consommerStockFiniProduit()`** :
  même raison — fait partie de la logique de consommation, pas de l'initialisation.
- **`verifierPolitiqueStockProduit()` par produit** : actuellement mono-scénario
  uniquement (ne boucle sur aucun produit) ; l'étendre est du réapprovisionnement,
  explicitement exclu de M.1.
- **Snapshot stable (`new ArrayList<>(listeProduits)`) avant boucles à risque** :
  aucune boucle multi-produit assez développée à ce stade pour introduire un risque
  de `ConcurrentModificationException` ; à auditer précisément quand la
  consommation/crédit/réappro par produit sera portée.
- **Distinction ScenarioFlux/Produit** : documentée dans le tableau ci-dessus, aucun
  changement de convention (portée hors scope d'une étape "source de vérité").

#### Validations statiques

- XML bien formé : OK.
- IDs AnyLogic : 1655/1655 uniques, inchangé (uniquement du code Java libre modifié/
  ajouté dans `AdditionalClassCode`, aucun élément `<Function>`/`<Variable>` AnyLogic
  ajouté).
- `git diff --check` : aucune erreur d'espace blanc.
- Grep DataCo (`DATACO_*|Prophet|Recalibrator|AutoCommande|dataco_calibration|2017-01-01`)
  sur `model/SCONTO_SVU_GENERIC_MASTER.alp` : 0 occurrence.
- Diff confiné à 2 zones : le scaffold multi-produit (~L6760-6960) et le
  chargement/sauvegarde JSON des paramètres globaux (~L14749/L14950) — **aucun
  changement** à `calculerPIGlobal()`, aux snapshots C14 de clôture de commande,
  aux états holoniques (Bloc A.5), à l'ordonnancement MTO, aux exports.
- **Compatibilité legacy vérifiée par lecture de code** : `modeMultiProduitActif`
  reste `false` par défaut et par absence dans le JSON ; tant qu'il est `false`,
  `synchroniserStockFiniAgrege()` est un no-op, `initialiserStocksProduits()`
  retombe sur `champStockInitialProduitFini` intégral (comportement identique
  à avant M.1), et `stockFiniDisponiblePourScenario()`/`consommerStockFiniProduit()`
  empruntent toujours la branche mono-produit inchangée (`fallback.niveauStock`
  uniquement) — le scénario ZENER mono-produit actuel n'est donc affecté par aucun
  des changements de ce bloc.
- **Build AnyLogic** : EN ATTENTE (utilisateur).
- **Run** : EN ATTENTE (utilisateur). Protocole suggéré : run ZENER standard
  (`modeMultiProduitActif` absent/false du JSON) — doit être **strictement
  identique** au comportement déjà validé en A.5 (test M-1 : legacy mono-produit).
  Aucun test multi-produit actif n'est encore pertinent tant que M.2 (consommation/
  crédit) n'est pas porté.
- **Commit** : voir SHA ci-dessous (message
  `feat(generic): establish multi-product stock source of truth`).

**PR reste DRAFT. Aucun merge vers `main`.**

## Bloc B — PI / SCOR
- [ ] Warm-up / amorçage
- [ ] Poids effectifs et données disponibles
- [ ] RL petits échantillons
- [ ] RS hyperbolique
- [ ] Proxies SCOR explicites
- [ ] Périmètre entreprise focale
- [ ] Build AnyLogic utilisateur
- [ ] Run court ZENER utilisateur

## Bloc C — retards
- [ ] Détection continue
- [ ] Engagement configurable
- [ ] Export/PI cohérent
- [ ] Build + run utilisateur

## Bloc D — moteur conflictuel
- [ ] Fonctions communes fusionnées une par une
- [ ] JSON générique préservé
- [ ] Export TTL/XLSX préservé
- [ ] Build + run utilisateur

## Bloc E — ordonnancement
- [ ] Analyse A/B
- [ ] Décision validée avant modification

## Validation finale
- [ ] ZENER nominal
- [ ] ZENER perturbé
- [ ] autre scénario générique
- [ ] aucune dépendance DataCo dans le noyau
- [ ] documentation mise à jour
