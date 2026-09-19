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

## Bloc M — Fondation multi-produit Generic (2026-09-16 ; M.1 TERMINÉ/FIGÉ 2026-09-17 ; M.2 EN COURS)

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

**Statut** : **M.1 TERMINÉ/FIGÉ** (audit + source de vérité + initialisation portés
et validés par l'utilisateur, 2026-09-17). **M.2 EN COURS** (consommation/crédit par
produit). Réapprovisionnement, politique autonome multi-produit, UI restent à faire
en M.3+.

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

### M.1-FIX — configuration partielle des stocks initiaux (2026-09-17)

**Origine** : revue du commit `30e17c2` — cas non couvert identifié dans
`stockInitialConfigurePourProduit()`.

**Bug confirmé** : la version M.1 initiale divisait systématiquement
`champStockInitialProduitFini` par le nombre **total** de produits, y compris ceux
déjà configurés explicitement dans `stockInitialParProduit` — contredisant
directement le commentaire selon lequel `champStockInitialProduitFini` représente
le TOTAL disponible. Exemple : `global=18000`, 3 produits, `{A: 10000}` seul
configuré → ancien code : `A=10000, B=6000, C=6000` (18000/3), **total=22000**
(création artificielle de 4000 unités).

**Politique implémentée** (dans `initialiserStocksProduits()`, calculée une seule
fois avant de remplir `stockFiniParProduit`, puis passée à
`stockInitialConfigurePourProduit()` sous forme d'une allocation par défaut déjà
calculée — solution retenue comme la plus simple/lisible, évite tout recalcul en
O(n²)) :
1. Parcourir `listeProduits` (les produits réellement catalogués uniquement — une
   clé de `stockInitialParProduit` ne correspondant à aucun produit catalogué est
   **ignorée** pour ce calcul, sans jamais consommer le reliquat d'un produit réel) ;
   calculer `sommeExplicite` (somme des valeurs configurées) et `nbConfigures`.
2. `nbNonConfigures = n - nbConfigures` ; `reliquat = max(0, stockGlobal - sommeExplicite)`.
3. `allocationParDefaut = nbNonConfigures > 0 ? reliquat / nbNonConfigures : 0`.
4. Si `sommeExplicite > stockGlobal` : log `[MULTI-PRODUIT][WARN]` explicite,
   **aucune réduction silencieuse** des valeurs explicites — le reliquat est alors
   nul (repli sur 0 pour les non configurés, jamais une valeur négative).
5. Chaque produit reçoit sa valeur explicite si configurée, sinon
   `allocationParDefaut`.

**Fichier modifié** : `model/SCONTO_SVU_GENERIC_MASTER.alp` — `stockInitialConfigurePourProduit()`
(signature changée : `int nbProduits` → `double allocationParDefaut`, déjà
calculée par l'appelant) et `initialiserStocksProduits()` (branche multi-produit
réécrite ; branche mono-produit strictement inchangée).

**Tests statiques vérifiés par relecture du code (non exécutables sans AnyLogic)** :

| Test | Entrée | Résultat attendu | Résultat du code |
|---|---|---|---|
| S-1 | `global=18000`, 3 produits, map vide | 6000/6000/6000, somme=18000 | `sommeExplicite=0, nbNonConfigures=3, reliquat=18000, allocation=6000` → conforme |
| S-2 | `global=18000`, `{A:6000,B:7000,C:5000}` | valeurs exactes, somme=18000 | tous configurés → valeurs explicites retournées telles quelles → conforme |
| S-3 | `global=18000`, `{A:10000}` seul | A=10000, B=4000, C=4000, somme=18000 | `sommeExplicite=10000, nbNonConfigures=2, reliquat=8000, allocation=4000` → conforme |
| S-4 | `global=18000`, `{A:15000,B:10000}`, C absent | A=15000, B=10000, C=0, somme=25000, WARN | `sommeExplicite=25000 > 18000` → WARN loggé ; `reliquat=max(0,18000-25000)=0` → `allocation=0` → C=0 → conforme |
| S-5 | clé fantôme `INCONNU=5000` (produit absent du catalogue) | ne réduit pas le reliquat des vrais produits | boucle de calcul limitée à `listeProduits` ; `INCONNU` jamais consulté → `sommeExplicite`/`nbConfigures` inchangés → conforme |
| S-6 | `modeMultiProduitActif=false` | comportement mono inchangé | branche `else` strictement identique à avant M.1 (`champStockInitialProduitFini` par entrée, jamais lu tant que le mode est off) → conforme |

### Audit complémentaire — `synchroniserStockFiniAgrege()` (2026-09-17, PAS DE MODIFICATION)

**Question posée** : les postes matchant `estPosteStockFini()` sont-ils traités
ailleurs comme des stocks physiques distincts (additifs) ou comme des miroirs du
même agrégat ?

**Preuve trouvée** : `stockProduitFiniDisponibleTotal()` (fonction `<Function>`
existante, utilisée notamment par `AM.3.45`/`AM.2.8` dans `valeurRuntimeMetriqueSCOR()`)
**somme** `p.niveauStock` sur **tous** les postes matchant `estPosteStockFini(p)` :
```java
for (PosteGenericAgent p : postes) {
    if (p != null && estPosteStockFini(p)) total += Math.max(0, p.niveauStock);
}
```
Cette fonction traite donc explicitement plusieurs postes stock-fini comme des
**stocks physiques distincts et additifs**. Or `synchroniserStockFiniAgrege()`
(Bloc M.1) écrit actuellement la **même** valeur `total` dans **tous** les postes
matchant `estPosteStockFini()` (traitement en **miroirs**, pas en stocks distincts).
**Ces deux fonctions ont des hypothèses logiquement incompatibles** : si plus d'un
poste matche `estPosteStockFini()` alors que `modeMultiProduitActif=true`,
`synchroniserStockFiniAgrege()` écrirait le même total N fois, et
`stockProduitFiniDisponibleTotal()` additionnerait ces N copies identiques —
double comptage démontré **par construction du code**, pas seulement supposé.

**Vérification empirique sur les scénarios actuellement fournis** (comptage des
postes matchant `estPosteStockFini()` — `typePoste==STOCKAGE` ou `codeSCOR`
commençant par `M1.5` ou nom contenant "PRODUITS FINIS") :
- `scenario_ZENER_SA_Togo_v39.json` : **1 poste** (`sM1.5.1`).
- `scenario_2_velo_urbain.json` : **0 poste**.
- `scenario_3_automobile_gx5.json` : **0 poste**.

**Conclusion** : sur les trois scénarios génériques actuellement fournis avec le
dépôt, `estPosteStockFini()` ne matche jamais plus d'un poste — **aucun double
comptage réel ne se produit aujourd'hui**. Le risque est **logique et latent**,
pas actuellement déclenché : il ne se matérialiserait que si un futur scénario
JSON définissait plusieurs postes de type `STOCKAGE`/`M1.5` (ex. un magasin
produits finis dédié par ligne de produit, dans une configuration multi-produit
avec stocks physiquement séparés). Conformément à la consigne (« ne modifier ce
mécanisme que si un double comptage réel est démontré »), **`synchroniserStockFiniAgrege()`
n'a PAS été modifiée** dans ce correctif. Le sujet est documenté ici pour
audit lors du sous-bloc M suivant, en particulier si une architecture à plusieurs
postes de stock fini physiquement distincts par produit est un jour envisagée
(auquel cas `synchroniserStockFiniAgrege()` devra être repensée pour écrire une
part du total par poste plutôt que le total complet sur chacun).

**Validations statiques (M.1-FIX)** :
- XML bien formé : OK.
- IDs AnyLogic : 1655/1655 uniques, inchangé.
- `git diff --check` : aucune erreur d'espace blanc.
- Grep DataCo : 0 occurrence.
- Diff confiné à `stockInitialConfigurePourProduit()`/`initialiserStocksProduits()`
  (~L6855-6926) — aucun changement à `synchroniserStockFiniAgrege()` (audité,
  non modifié), à `consommerStockFiniProduit()`, `crediterStockFiniProduit`
  (toujours absente), réapprovisionnement, politique autonome, PI/SCOR, exports,
  états holoniques, ordonnancement.
- **Build AnyLogic** : OK.
- **Run** : OK (run ZENER legacy, JSON sans `exportOnStop`).
- **Commit** : `3fed760` (message `fix(generic): preserve total stock with partial product config`).

### Validation utilisateur définitive — M.1 / M.1-FIX (2026-09-17)

Run analysé sur Excel final, CSV traces complet, CSV KPI, ABox TTL.

- **Non-régression mono-produit confirmée** : Tfinal Excel=1493,3s ; Historique
  Dashboard 51 snapshots/51 timestamps uniques, dernier=1493,3, PI final=8,03,
  Finished Stock final=8 ; Execution Brute 710 événements ; CSV complet cohérent
  (710 BRUT/204 AGG_MICRO/204 AGG_SCOR/63 AGG_MACRO/4 AGG_GLOBAL, dernier BRUT
  t=1484,907) ; CSV KPI `PI_GLOBAL=8,0297`. Source/Plan/Make/Deliver actifs, un
  vrai goulot Make observé (`M1.2` avgWaitTime≈732s, cohérent avec A.5). 0 erreur
  Excel.
- **TTL non final expliqué, pas une régression A.4** : `exportReason=ORDER_CLOSED_CMD_4`,
  `simulationTime=918`, `RawEvent=412` == 412 événements BRUT du CSV à t≤918 — le
  run a simplement continué après cette dernière clôture de commande, et le JSON
  utilisé pour ce test est le JSON legacy où `exportOnStop` est absent/false (cf.
  A.4-FIX-5A). **Aucun mécanisme ABox modifié pour cela.**
- **Note préexistante documentée (pas une régression M.1)** : en mono-produit, les
  feuilles "Multi-produit ZENER"/"Performance par produit" affichent encore le
  scaffold dormant (`SCENARIO DISTRIBUTION`, `SCENARIO DELIVER RETURN CLIENT`,
  stock=100 par référence) alors que le Finished Stock runtime réel vaut 8 — déjà
  présent avant M.1 (confirmé sur le run A.5). Présentation potentiellement
  trompeuse, mais pas un bug moteur (`modeMultiProduitActif=false`). **À documenter
  pour un futur sous-bloc UI/export multi-produit ; ne pas corriger en M.2 sauf si
  une modification M.2 le rend indispensable.**

**BLOC M.1 : audit = VALIDÉ ; source de vérité = VALIDÉ ; JSON legacy = VALIDÉ ;
M.1-FIX configuration partielle = VALIDÉ ; run legacy ZENER = VALIDÉ.**

**STATUT M.1 : TERMINÉ / FIGÉ.**

## Bloc M.2 — consommation + crédit par produit (2026-09-17)

**Objectif** : rendre opérationnel l'invariant `stockFiniParProduit` = source de
vérité en multi-produit / `niveauStock` = agrégat de compatibilité, en connectant
consommation, crédit de production, synchronisation agrégée et identité produit.
**Politique/réapprovisionnement par produit non touchés (M.3+).**

### Audit exhaustif des lecteurs/écrivains du stock produit fini

| Fonction / ligne | Lecture ou écriture | Rôle métier | Mono actuel | Risque multi | Décision M.2 | Reporté à M.3 ? |
|---|---|---|---|---|---|---|
| `PosteGenericAgent` onExit, ~L45063 (`niveauStock += 1`) | **Écriture** (crédit) | Toute entité réelle (non visuelle) atteignant un poste `STOCKAGE`/`M1.5` crédite le stock physique — **seul point de crédit de production existant** | Incrémente `niveauStock` du poste, quel qu'il soit | **Élevé (avant M.2)** : aveugle au produit, créditerait la même variable pour tous produits confondus | **MODIFIÉ** : crédit produit-conscient uniquement si `modeMultiProduitActif && estPosteStockFini(this)` ; sinon comportement exact inchangé (autres postes STOCKAGE : buffers/matières, non concernés) | Non |
| `consommerStockFiniProduit()` (`~L6980`) | **Écriture** (consommation) | Décrémente le stock lors d'une livraison MTS/directe | Décrémente `fallback.niveauStock` | Déjà isolé par produit depuis M.1, manquait la resynchro agrégat | **COMPLÉTÉ** : ajout de `synchroniserStockFiniAgrege(fallback)` en fin de branche multi | Non |
| `crediterStockFiniProduit()` (nouvelle, `~L7000`) | **Écriture** (crédit) | Pendant générique de `consommerStockFiniProduit()` pour le crédit | N/A (nouvelle fonction) | — | **AJOUTÉE**, portée de la référence DataCo avec une adaptation explicite (voir plus bas) | Non |
| `stockFiniDisponiblePourScenario()` (`~L6960`) | **Lecture** | Fournit le stock disponible pour la décision MTS d'un scénario donné | Lit `fallback.niveauStock` | Déjà corrigé en M.1 (isolation stricte) | Inchangé | Non |
| `stockProduitFiniDisponibleTotal()` (`~L20055`) | **Lecture** (agrégat) | KPI SCOR `AM.3.45`/`AM.2.8`, additionne tous les postes `estPosteStockFini()` | Somme correcte tant qu'1 seul poste existe | **Démontré en M.1-FIX** : additionnerait N fois le même total si plusieurs postes stock-fini existaient | **MODIFIÉ** : `if (modeMultiProduitActif) return sommeStockFiniParProduit();` sinon calcul legacy inchangé (solution minimale demandée) | Non |
| `capturerPointHistoriqueDashboard()` (`~L7210`, colonne "Finished Stock") | **Lecture** (agrégat) | Alimente l'historique Dashboard (Bloc A.4) | Même boucle dupliquée que `stockProduitFiniDisponibleTotal()` | Même risque latent | **MODIFIÉ** : délègue à `stockProduitFiniDisponibleTotal()` (déjà corrigée) au lieu de dupliquer la boucle | Non |
| Carte dashboard "Finished Stock" (`TextCode`, `~L30688`) | **Lecture** (agrégat) | Affichage temps réel | Même boucle dupliquée (stream/sum) | Même risque latent | **MODIFIÉ** : `(int) stockProduitFiniDisponibleTotal()` au lieu de dupliquer la boucle | Non |
| `calculerInventoryDaysOfSupply()` (`~L13084`, SCOR `AM.2.2`) | **Lecture** (agrégat) | Jours de couverture de stock | Somme `p.niveauStock` mais avec le prédicat **`typePoste==TypePoste.STOCKAGE` strict** (pas `estPosteStockFini()` — ne matche même pas `sM1.5.1` sur ZENER, qui est de type DELAI, cf. C14.67) | Non démontré : prédicat différent, portée probablement plus large que le seul stock produit fini (pourrait inclure du stock matière/tampon) | **NON MODIFIÉ** — prédicat et périmètre différents de "stock produit fini par référence" ; mélanger les deux serait une erreur conceptuelle, pas une correction | **Oui, à ré-auditer séparément si nécessaire** |
| `verifierPolitiqueStockProduit()` (`~L2586`) | **Lecture** (`stockFini.niveauStock`) | Politique de réapprovisionnement (s,Q) — mono-scénario uniquement, ne boucle sur aucun produit | Lit directement le poste de référence | Réapprovisionnement multi-produit non traité | **NON MODIFIÉ** | **Oui (M.3, réapprovisionnement)** |
| Logs/popups (`~L2597/2798/2813/12458/49843/49964`) | **Lecture** (cosmétique) | Messages `[MTS]`/popups affichant le stock restant | Lisent `stockFini.niveauStock` directement, à titre d'affichage | Aucun (affichage seulement, `niveauStock` reste synchronisé par `synchroniserStockFiniAgrege()`) | **NON MODIFIÉ** — purement cosmétique, correct tant qu'1 seul poste stock-fini existe (cas actuel) | Non (à revoir seulement si M.3 introduit plusieurs postes physiques) |

### Chaîne d'identité produit — démontrée avant tout portage

**Consommation** (`consommerStockFiniProduit()`, 2 sites d'appel) : l'identité est déjà
résolue proprement par l'appelant AVANT l'appel — `sc`/`scLivraison` (`ScenarioFlux`)
sont passés directement, sans devinette. **Aucun chaînon manquant.**

**Crédit** (production → magasin PF) : chaîne tracée explicitement avant portage :
```
CommandeAgent (idCommande, idScenario)
  -> lancerProductionCommandeOrchestree(cmd) crée, pour chaque unité :
       e.idFlux = cmd.idCommande + "_F_" + (++seqProduitRuntime)   [L5275]
  -> l'entité parcourt sa route Make (routeProductionMakeDepuisScenario(sc))
  -> arrive au poste magasin produits finis (onExit, estPosteStockFini(this)==true)
  -> identité résolue par fluxAppartientACommande(agent.idFlux, cmd.idCommande)
     pour cmd dans main.commandes -- LE MÊME mécanisme déjà validé au Bloc A.1
     (fix du bug CMD_4/CMD_44)
  -> cmd.idScenario (déjà la clé produit utilisée partout ailleurs :
     codeProduitCommande(), verifierPolitiqueStockProduit())
  -> crediterStockFiniProduit(cmd.idScenario, 1, this)
```
**Rejeté explicitement comme source d'identité** : `agent.typeProduit` — vérifié par
grep de tous ses points d'écriture (`.typeProduit =`) : ce champ sert de libellé de
trace/affichage avec des conventions **incompatibles selon le chemin de code**
(`"TRACE_VISUEL_SCOR"` pour les jetons visuels, `"LIVRAISON:"+nom`/`"APPRO:"+nom`
pour d'autres flux, `"Produit"` littéral générique pour le flux autonome "génération 1"
désactivé par défaut, `libelleTypeProduitTrace(cmd,sc)` — un libellé d'affichage, pas
garanti égal à la clé de catalogue `cleProduit(sc.typeProduit)`). Utiliser ce champ
aurait été deviner une identité non fiable ; `cmd.idScenario` via `idFlux` est la
seule voie démontrée et déjà validée.

**Chemin non couvert, documenté, non un chaînon manquant pour le périmètre actif** :
le flux autonome "génération 1" (événement `arrivee`, actif seulement si
`modePilotageParCommande=false` — **pas le mode utilisé par ZENER**, cf.
`Condition><![CDATA[modeExecution && !modePilotageParCommande]`) crée des entités
sans `CommandeAgent` associé (`e.idFlux = "F_" + seqFlux`, aucun `CMD_`). Si une
telle entité atteignait un jour le magasin PF en mode multi-produit,
`fluxAppartientACommande()` ne trouverait aucune correspondance,
`identiteProduit` resterait `null`, et `crediterStockFiniProduit()` journaliserait
un WARN sans créditer (comportement sûr, pas un crash, pas un vol de stock —
mais le stock ne serait alors pas comptabilisé). Documenté ici pour un futur bloc
si ce mode legacy est un jour combiné avec le multi-produit.

### Décision — produit inconnu (crediterStockFiniProduit())

**Adaptation explicite vs la référence DataCo** : DataCo réplie une identité
vide/nulle sur `nomProduitParDefaut` (`typeProduit != null && !typeProduit.trim().isEmpty()
? typeProduit : nomProduitParDefaut`). **Ce repli a été retiré ici** — conformément à
la consigne de ce bloc ("si l'identité produit est vide/inconnue/non cataloguée : WARN
explicite ; aucun transfert silencieux vers une autre référence"), une identité vide,
nulle, ou ne correspondant à aucune entrée de `catalogueProduits` déclenche
uniquement `[MULTI-PRODUIT][WARN] credit stock ignore : produit inconnu='...'`, sans
crédit nulle part. Une clé correspondant à un produit **réellement catalogué** mais
absente de `stockFiniParProduit` (cas limite, ex. juste après un rechargement JSON)
est en revanche initialisée proprement à 0 puis créditée (`avant = containsKey(cle)
? ... : 0.0`), pas traitée comme une erreur.

### rotationProduitsActive

Non touché par ce bloc — reste `false` par défaut, et `choisirScenarioProduit()`
(qui l'utilise) n'est appelé nulle part dans le chemin de crédit ajouté ici : le
crédit ne "devine" jamais un produit par rotation, uniquement par résolution
d'identité explicite via `idFlux`/`idScenario`.

### Fichier modifié

`model/SCONTO_SVU_GENERIC_MASTER.alp` — 5 zones : `consommerStockFiniProduit()` +
`crediterStockFiniProduit()` (~L6980-7025), `capturerPointHistoriqueDashboard()`
(~L7210), `stockProduitFiniDisponibleTotal()` (~L20055),  carte dashboard "Finished
Stock" (~L30688), `PosteGenericAgent` onExit (~L45063-45100).

### Ce qui a été porté

- `crediterStockFiniProduit(String typeProduit, double qte, PosteGenericAgent fallback)` :
  porté de la référence DataCo avec l'adaptation "pas de repli sur défaut" décrite
  ci-dessus.
- `consommerStockFiniProduit()` : appel `synchroniserStockFiniAgrege(fallback)`
  ajouté en fin de branche multi (comme prévu depuis le commentaire M.1).
- `stockProduitFiniDisponibleTotal()`, historique Dashboard, carte "Finished Stock" :
  basculent sur `sommeStockFiniParProduit()`/`stockProduitFiniDisponibleTotal()` en
  mode multi-produit (solution minimale demandée), calcul legacy strictement
  inchangé en mono.
- Crédit de production (`PosteGenericAgent` onExit) : identité résolue via
  `fluxAppartientACommande()` (Bloc A.1) + `cmd.idScenario`, jamais devinée.

### Ce qui a été adapté

`crediterStockFiniProduit()` diverge de la référence DataCo sur un seul point
(politique produit inconnu, voir ci-dessus) — changement délibéré, documenté,
demandé explicitement par ce bloc.

### Ce qui n'a pas été porté (et pourquoi) — reporté à M.3+

- `verifierPolitiqueStockProduit()` par produit (réapprovisionnement) — explicitement
  hors périmètre de M.2.
- `calculerInventoryDaysOfSupply()` — prédicat (`TypePoste.STOCKAGE` strict) et
  périmètre (inventaire large, pas spécifiquement "produit fini par référence")
  différents ; le modifier avec la même règle serait une erreur conceptuelle, pas
  une correction. À ré-auditer séparément si un besoin précis se présente.
- Flux autonome "génération 1" (`modePilotageParCommande=false`) combiné au
  multi-produit : chemin non actif pour ZENER, documenté comme limite connue
  (WARN sans crédit si jamais activé simultanément).
- `ConcurrentModificationException` / snapshot stable de `listeProduits` : la
  nouvelle boucle ajoutée (`for (CommandeAgent cmd : main.commandes)`) ne
  reconstruit ni ne synchronise `commandes` pendant son parcours (lecture seule,
  `break` dès la correspondance trouvée) — aucun risque introduit, snapshot non
  nécessaire ici.

### Validations statiques

- XML bien formé : OK.
- IDs AnyLogic : 1655/1655 uniques, inchangé (uniquement du code Java libre
  modifié/ajouté, aucun élément `<Function>`/`<Variable>` AnyLogic ajouté ; seul le
  `Body` de la `<Function>` `stockProduitFiniDisponibleTotal()` existante a été
  édité, sans changer sa signature/Id).
- `git diff --check` : aucune erreur d'espace blanc.
- Grep DataCo : 0 occurrence.
- Diff confiné aux 5 zones listées — **aucun changement** à `calculerPIGlobal()`,
  aux snapshots C14 de clôture de commande, aux états holoniques (Bloc A.5), à
  l'ordonnancement MTO, à `verifierPolitiqueStockProduit()`, aux exports Excel/ABox
  (hors les 2 lectures d'agrégat corrigées), au format JSON des scénarios.
- **Compatibilité legacy vérifiée par lecture de code** : tant que
  `modeMultiProduitActif=false` (défaut), le nouveau bloc `if` dans le crédit
  onExit tombe systématiquement dans la branche `else { niveauStock += 1; }`
  (comportement identique à avant M.2) ; `crediterStockFiniProduit()`/
  `consommerStockFiniProduit()` empruntent leur branche mono inchangée ;
  `stockProduitFiniDisponibleTotal()` garde son calcul legacy exact.
- **Build AnyLogic** : EN ATTENTE (utilisateur).
- **Run** : EN ATTENTE (utilisateur). Protocole suggéré : (1) run ZENER legacy
  (`modeMultiProduitActif` absent/false) — doit rester strictement identique aux
  runs déjà validés (A.5, M.1) ; (2) si une fixture multi-produit synthétique est
  disponible (2 `ScenarioFlux` A/B intentionnels, `modeMultiProduitActif=true`),
  vérifier les tests M2-1 à M2-10 listés par l'utilisateur (non exécutables sans
  AnyLogic depuis cet environnement).
- **Commit** : `5a46764` (message `feat(generic): wire per-product stock consumption and credit`).

### Validation utilisateur — M.2 legacy (2026-09-17)

- **Build AnyLogic** : **VALIDÉ** (0 erreur).
- **Run ZENER legacy** : **VALIDÉ** — `modeMultiProduitActif` absent/false ;
  commandes, Source, Plan, Make, Deliver, stock PF, états holoniques, exports :
  tous OK ; aucune exception observée.
- **M2-1 (legacy mono-produit)** : **VALIDÉ**.

**M.2 n'est PAS considéré entièrement validé** : le chemin multi-produit
(`modeMultiProduitActif=true`) n'a pas encore été testé en conditions réelles —
c'est l'objet du sous-bloc M.2-TEST ci-dessous.

## Bloc M.2-TEST — fixture synthétique A/B (2026-09-17)

**Sous-bloc de TEST uniquement.** Aucun code moteur modifié, aucune politique
autonome multi-produit implémentée, PI/SCOR non touché. Un seul livrable : une
fixture JSON dérivée d'un scénario Generic déjà validé, plus ce journal.

### 1. Schéma JSON audité (avant toute création de fixture)

| Champ / mécanisme | Chemin | Signification | Utilisé par | Valeur retenue pour la fixture |
|---|---|---|---|---|
| `scenarios[].typeProduit` | racine JSON | Identité d'un `ScenarioFlux` — devient la clé catalogue via `cleProduit()` | `synchroniserListeProduits()`, `estScenarioCasTest()`, `choisirScenarioProduit()`, `codeProduitCommande()`, `cmd.idScenario` | `"PRODUIT_A"` / `"PRODUIT_B"` (voir §2) |
| `scenarios[].sequence` | racine JSON | Liste ordonnée d'`idPoste` parcourus par ce produit | `routeProductionMakeDepuisScenario()`, `lancerProductionCommandeOrchestree()` | Copie exacte de la séquence `"SCENARIO DISTRIBUTION"` de ZENER (contient `sM1.5.1`, le magasin produits finis) |
| `scenarios[].nomenclature` | racine JSON | Matières consommées par unité produite | `consommerMatieresPour()`, `bilanMatierePourScenario()` | Copie exacte (GPL_VRAC, BOUTEILLE_VIDE_12KG, ACCESSOIRES_KIT) — matières **partagées** entre A et B, simplification documentée §5 |
| `scenarios[].debitParHeure`/`debitParHeureBase` | racine JSON | Débit nominal du scénario (utilisé par la sélection Poisson en mode NON piloté par commande, et comme référence de calibration) | `ajusterDebits()`, sélection légataire `arrivee` | `80` (identique à ZENER, inchangé) |
| `parametresGlobaux.modeMultiProduitActif` | `parametresGlobaux` | Active la branche multi-produit (Bloc M) | Toutes les fonctions du scaffold M.1/M.2 | `true` |
| `parametresGlobaux.rotationProduitsActive` | `parametresGlobaux` | Force une rotation round-robin déterministe entre produits catalogués | `choisirScenarioProduit()` | `true` (mécanisme déjà générique, activé uniquement pour ce test) |
| `parametresGlobaux.champStockInitialProduitFini` | `parametresGlobaux` | Stock global de référence (mono) / total nominal (multi, cf. M.1-FIX) | `initialiserStocksProduits()` | `100` (absent du JSON ZENER original → défaut Java 90.0 ; explicité ici pour un total rond) |
| `parametresGlobaux.stockInitialParProduit` | `parametresGlobaux` | Map optionnelle de stocks initiaux explicites par produit (Bloc M.1) | `stockInitialConfigurePourProduit()` | `{"PRODUIT_A": 60, "PRODUIT_B": 40}` — cas 2 de M.1-FIX (map complète, respectée exactement, somme=100) |
| `estScenarioCasTest(sc)` | code (`~L4207`) | `nomScenario(sc).toUpperCase().contains("ZENER CAS 1"/"2"/"3")` — **hardcodé littéralement sur ces 3 chaînes** (limite de généricité pré-existante, non introduite par ce bloc, non corrigée ici — hors périmètre) | `estProduitEnregistrable()`, `indexScenarioNominal()`, `genererCommande()` | Noms `PRODUIT_A`/`PRODUIT_B` ne matchent aucune de ces 3 chaînes → catalogables (voir §2) |
| `modePilotageParCommande` | **PAS dans le JSON** — champ Java sans binding JSON (vérifié par grep, aucun `jsonBool(...)` correspondant) | Sélectionne le pilotage par commande vs le flux autonome "génération 1" | `genererCommande()`, `traiterAlertesTactiques()`, événement `arrivee` | Défaut Java `true` — **déjà le mode actif**, aucune action requise |
| `nombreCommandesATester`/`limiterNombreCommandes` | **PAS dans le JSON** | Bornent la campagne de test | `genererCommande()`, `verifierPolitiqueStockProduit()` | Défauts Java `45`/`true` — suffisant pour observer plusieurs cycles A/B, réglable via l'UI si un run plus court est souhaité (non requis) |
| `quantiteCommandeFixeActive`/`quantiteCommandeFixe` | **PAS dans le JSON** | Fige la quantité de chaque commande | `quantitePourNouvelleCommande()` | Défaut Java `false`/`2` — quantités aléatoires par défaut ; documenté §4, réglable via l'UI si des deltas exacts sont souhaités |
| `champScenarioSelectionne` | **PAS dans le JSON** | Sélection manuelle courante (UI) | `choisirScenarioPourCommande()`, lu par `choisirScenarioProduit()` **seulement si `rotationProduitsActive=false`** | Sans effet ici : `rotationProduitsActive=true` court-circuite ce chemin (voir §4) |

**Aucun champ JSON inexistant n'a été inventé.** Les trois derniers champs listés
« PAS dans le JSON » sont des réglages runtime/UI, confirmés par grep exhaustif de
toutes les affectations `jsonBool`/`jsonDouble`/`jsonInt` correspondantes — aucune
trouvée pour `modePilotageParCommande`, `nombreCommandesATester`,
`limiterNombreCommandes`, `quantiteCommandeFixeActive`, `quantiteCommandeFixe`,
`champScenarioSelectionne` : ils ne peuvent être réglés que dans l'interface
AnyLogic (panneau « Contrôle commandes » évoqué dans les journaux précédents),
jamais dans un fichier de scénario.

### 2. Noms A/B retenus et pourquoi ils sont catalogables

`estProduitEnregistrable(sc)` exclut uniquement les scénarios pour lesquels
`estScenarioCasTest(sc)` est vrai, et cette dernière ne teste que la présence
littérale de `"ZENER CAS 1"`, `"ZENER CAS 2"` ou `"ZENER CAS 3"` (majuscules,
insensible à la casse) dans `nomScenario(sc)` (= `sc.typeProduit`). `"PRODUIT_A"`
et `"PRODUIT_B"` ne contiennent aucune de ces sous-chaînes → catalogables par
construction, sans dépendre d'une heuristique de nommage fragile. Leur nature
synthétique/test est documentée dans le **nom du fichier**
(`scenario_M2_multiproduit_AB.json`) et dans `meta.nomEntreprise`/
`parametresGlobaux.nomEntreprise` (suffixés `"(FIXTURE TEST M.2 MULTI-PRODUIT --
NON PRODUCTION)"`), pas dans `typeProduit` lui-même — précisément pour ne pas
risquer une exclusion involontaire par un futur ajustement du prédicat.

### 3. Fixture créée — dérivée de ZENER, ZENER non modifié

`scenario_M2_multiproduit_AB.json` (racine du dépôt, aux côtés des autres
scénarios Generic) est une copie complète de `scenario_ZENER_SA_Togo_v39.json`
(64 postes, 5 acteurs, 3 fiches matière — **byte-identiques**, vérifié
programmatiquement) dans laquelle **seuls** les `scenarios[]` et 5 champs de
`parametresGlobaux` diffèrent :

| Élément | ZENER original | Fixture |
|---|---|---|
| `scenarios[]` (5 entrées : Distribution, Deliver Return, Cas 1/2/3) | — | **Remplacés par 2 entrées** : `PRODUIT_A` et `PRODUIT_B`, chacune une copie exacte de `"SCENARIO DISTRIBUTION"` (séquence avec `sM1.5.1`, nomenclature 3 matières, débit 80) — seul `typeProduit` diffère |
| `parametresGlobaux.modeMultiProduitActif` | absent (défaut `false`) | `true` |
| `parametresGlobaux.rotationProduitsActive` | absent (défaut `false`) | `true` |
| `parametresGlobaux.champStockInitialProduitFini` | absent (défaut Java `90.0`) | `100` |
| `parametresGlobaux.stockInitialParProduit` | absent | `{"PRODUIT_A": 60, "PRODUIT_B": 40}` |
| `meta.nomEntreprise` / `parametresGlobaux.nomEntreprise` | `"ZENER SA Togo"` | suffixé `"(FIXTURE TEST M.2 MULTI-PRODUIT -- NON PRODUCTION)"` |
| `postes`, `acteurs`, `machines`, `fichesMatiere` | — | **Inchangés, byte-identiques** (vérifié par comparaison programmatique) |

**`scenario_ZENER_SA_Togo_v39.json` n'a subi aucune modification** — la fixture est
un fichier entièrement séparé.

### 4. Génération des commandes A/B — mécanisme vérifié, pas supposé

Audit de `genererCommande()` (`~L12646`) :
```java
ScenarioFlux scenarioCommande = modeMultiProduitActif
    ? choisirScenarioProduit(n)
    : choisirScenarioPourCommande();
...
if (scenarioCommande != null) {
    cmd.idScenario = scenarioCommande.typeProduit;
}
```
**Confirmé, pas supposé** : avec `modeMultiProduitActif=true` (fixture), chaque
commande appelle bien `choisirScenarioProduit(n)`, qui — puisque
`rotationProduitsActive=true` et `listeProduits.size()=2` — **court-circuite** la
sélection manuelle (`choisirScenarioPourCommande()`) et applique
`index = floorMod(n-1, 2)` : `CMD_1→PRODUIT_A, CMD_2→PRODUIT_B, CMD_3→PRODUIT_A,
CMD_4→PRODUIT_B, ...` (rotation strictement déterministe, confirmée par lecture de
code, `PRODUIT_A` étant le premier élément de `listeProduits` car premier dans
`scenarios[]`). `cmd.idScenario = scenarioCommande.typeProduit` assigne ensuite
l'identité exacte utilisée par tout le reste du moteur (`codeProduitCommande()`,
`performanceProduitRow()`, et par le crédit de production ajouté en M.2 via
`fluxAppartientACommande()`).

`rotationProduitsActive` n'est activé que dans cette fixture, uniquement pour
garantir un test déterministe — pas une règle métier par défaut (reste `false`
partout ailleurs, y compris dans le master lui-même).

### 5. Consommation — quantités réellement configurables

`quantiteCommandeFixeActive` (défaut `false`) n'a **aucun binding JSON** : les
quantités par commande suivront la distribution aléatoire par défaut de
`quantitePourNouvelleCommande()`, pas des valeurs fixes comme "10" ou "5". **Ceci
est documenté conformément à la consigne** plutôt que d'inventer un mécanisme de
fixation par JSON inexistant. Pour un test avec des deltas parfaitement
prévisibles, l'utilisateur peut activer manuellement "quantité fixe" dans le
panneau de contrôle AnyLogic avant de démarrer — non requis pour valider les
invariants d'isolation (M2-3/M2-4), qui tiennent quelle que soit la quantité
exacte tant qu'elle est positive.

**Simplification documentée** : PRODUIT_A et PRODUIT_B partagent la **même**
nomenclature/matières (copie de celle de `SCENARIO DISTRIBUTION`) — le test porte
sur l'isolation du **stock produit fini**, pas sur la contention de matières
premières entre références, qui reste hors périmètre de ce sous-bloc.

### 6. Politique autonome — ne peut pas être désactivée proprement, documenté sans y toucher

Audit de l'appelant de `verifierPolitiqueStockProduit()` : appelée
inconditionnellement depuis le cycle tactique périodique de l'acteur `sM`
(`~L51381`, `if ("sM".equals(idMacroProcessus)) { main.verifierPolitiqueStockProduit(); }`),
**sans aucun flag JSON ou paramètre d'activation/désactivation existant**. Elle
reste, comme documenté au Bloc M.2, **mono-scénario** (`scRef` = scénario nominal
unique, ne boucle sur aucun produit).

**Décision, conformément à la consigne** (« si elle ne peut pas être désactivée
sans code : STOP et documenter, ne pas implémenter M.3 pour faire fonctionner le
test ») : **non désactivée, non modifiée**. Impact documenté plutôt que corrigé :
`indexScenarioNominal()` retombera sur le "premier scénario non cas-test" (donc
`PRODUIT_A`, puisqu'il est en position 0 dans `scenarios[]`) si le stock **agrégé**
(A+B combinés, lu via le poste physique partagé) descend sous le point de
commande. Un REAPPRO autonome pourrait alors se déclencher, **mais uniquement sur
PRODUIT_A** (jamais B, puisque `declencherProductionAutonome(scRef, ...)` fixe
`cmd.idScenario = scRef.typeProduit` correctement). Cela n'invalide pas le test :
un tel REAPPRO créditerait A exclusivement, via le même chemin d'identité déjà
démontré en M.2 — sa présence dans les logs (`[STOCK] Production autonome
déclenchée : REAPPRO_x ...`) est à noter comme variable non contrôlée dans
l'interprétation des deltas exacts, pas comme un défaut du test.

### 7. Observabilité — exports existants confirmés fiables, aucune instrumentation ajoutée

Audit de la feuille Excel **"Performance par produit"** (`performanceProduitRow()`,
`~L7401`) : lit **directement** `stockFiniParProduit.get(cle)` (`~L7411`) pour la
colonne "Stock fini restant", et filtre `commandes` par `cleProduit(c.idScenario)`
pour "Nombre de commandes"/"Quantité commandée"/"Quantité livrée"/"Commandes en
retard" — **par produit**, déjà correct et déjà branché sur la source de vérité
multi-produit, sans dépendre d'aucun changement de M.2. La feuille "Multi-produit
ZENER" (`multiProduitConfigurationRows()`), en revanche, est purement
descriptive/configuration (nomenclature, statut d'intégration) — **pas un export
de stock runtime**, ne pas s'y fier pour les valeurs A/B.

L'agrégat (`stockProduitFiniDisponibleTotal()`, déjà corrigé en M.2 pour utiliser
`sommeStockFiniParProduit()` en mode multi) reste lisible via la carte dashboard
"Finished Stock" et la feuille "Dashboard Global".

**Conclusion : les exports existants sont fiables. Aucune instrumentation
`.alp` (log `[MULTI-STOCK]` ou autre) n'a été ajoutée** — conformément à la
consigne "si elles sont fiables : utiliser les exports existants" et "si
uniquement JSON + documentation sont nécessaires : ne modifie pas le .alp".
**Aucun fichier `.alp` n'a été modifié dans ce sous-bloc.**

### 8. Invariant à vérifier manuellement après le run (pas d'automatisation ajoutée)

Après le run avec la fixture :
1. Ouvrir la feuille "Performance par produit" : relever "Stock fini restant" pour
   `PRODUIT_A` et `PRODUIT_B`, les additionner.
2. Comparer à la valeur "Finished Stock" de la carte dashboard / feuille
   "Dashboard Global" (= `stockProduitFiniDisponibleTotal()` = `sommeStockFiniParProduit()`
   en mode multi, cf. M.2).
3. Les deux doivent être **strictement égales** (pas seulement proches — même
   source de calcul, aucune tolérance flottante attendue en pratique puisque
   `stockProduitFiniDisponibleTotal()` en mode multi *est* `sommeStockFiniParProduit()`).
4. Si un poste physique de compatibilité est observable (`sM1.5.1.niveauStock` via
   un log `[MTS]`/popup), il doit également correspondre à cette même somme,
   `synchroniserStockFiniAgrege()` l'écrivant explicitement à chaque
   consommation/crédit.

Aucun log `[MULTI-PRODUIT][ERROR]` de désaccord n'a été ajouté (pas nécessaire :
l'agrégat et la somme sont *la même valeur calculée*, pas deux valeurs
indépendantes à comparer avec tolérance — un écart ne peut résulter que d'un bug
de synchronisation, pas d'un artefact d'arrondi).

### 9. Concurrent modification — audité, aucun risque nouveau

Boucles potentiellement concernées auditées : `choisirScenarioProduit()`,
`stockFiniDisponiblePourScenario()`, `crediterStockFiniProduit()`,
`consommerStockFiniProduit()` appellent toutes `synchroniserListeProduits()` (qui
**reconstruit** `listeProduits`/`catalogueProduits` depuis `scenarios`, jamais
l'inverse) mais aucune ne boucle sur `listeProduits` PENDANT qu'une autre fonction
du même appel la reconstruit — chaque appel à `synchroniserListeProduits()` se
termine avant que le code appelant n'itère quoi que ce soit. La nouvelle boucle
de résolution d'identité ajoutée en M.2 (`for (CommandeAgent cmd : main.commandes)`)
ne touche ni ne reconstruit `commandes` ni `listeProduits` pendant son parcours.
**Aucune `ConcurrentModificationException` identifiée comme risque réel** pour ce
sous-bloc ; aucun snapshot stable ajouté (n'aurait rien protégé de plus).

### Fichier créé

`scenario_M2_multiproduit_AB.json` (racine du dépôt). **Aucun fichier `.alp`
modifié.**

### Protocole utilisateur — étape par étape

1. Ouvrir `model/SCONTO_SVU_GENERIC_MASTER.alp` dans AnyLogic (commit `5a46764`
   ou plus récent — aucun changement de code depuis ce commit n'est nécessaire
   pour ce test).
2. Build (vérifier 0 erreur).
3. Lancer une simulation, charger `scenario_M2_multiproduit_AB.json` (et non
   `scenario_ZENER_SA_Togo_v39.json`) via le mécanisme de chargement de scénario
   habituel.
4. Démarrer la simulation normalement (pilotage par commande déjà actif par
   défaut, aucun réglage supplémentaire requis).
5. Laisser tourner suffisamment pour observer plusieurs commandes des deux
   produits (au moins 4-6 commandes, réparties automatiquement en alternance
   A/B/A/B/... par la rotation).
6. Arrêter proprement via "Arreter et voir resultats" (finalise l'export, cf.
   Bloc A.4).
7. Ouvrir l'Excel exporté : feuille "Performance par produit" → noter le "Stock
   fini restant" de `PRODUIT_A` et `PRODUIT_B`, additionner.
8. Comparer à "Finished Stock" (carte dashboard / feuille "Dashboard Global").
   Les deux valeurs doivent être identiques (§8).
9. Vérifier dans "Performance par produit" que les commandes sont bien réparties
   entre les deux références (nombre de commandes > 0 pour A **et** B).
10. Chercher dans le journal des événements/logs d'éventuelles lignes
    `[MULTI-PRODUIT][WARN]` (produit inconnu — ne devrait apparaître que si un
    chemin hors pilotage par commande était atteint, cf. §6/limite documentée en
    M.2) et `[STOCK] Production autonome déclenchée : REAPPRO_...` (politique
    autonome, §6 — attendu occasionnellement sur PRODUIT_A uniquement, sans
    invalider le test).
11. Vérifier l'absence de toute exception dans la console/le journal.

**Résultat attendu** : A et B évoluent indépendamment (une commande PRODUIT_A ne
modifie jamais le stock PRODUIT_B et réciproquement), l'agrégat reste égal à la
somme à tout instant, chaque crédit de production est traçable à
`cmd.idScenario`, aucune exception.

**PR reste DRAFT. Aucun merge vers `main`.**

## Bloc M.2-TEST-FIX — écrasement post-initialisation du stock par produit (2026-09-17)

**Déclencheur** : run réel utilisateur de `scenario_M2_multiproduit_AB.json`
(global=100, A=60, B=40 configurés). Résultat observé : `Finished Stock`
au premier snapshot (t=50 s) = **200** au lieu de 100 ; bilan final
A=82/B=70 au lieu de A=42/B=10 attendus. La preuve par le bilan (voir message
utilisateur) montre que ces valeurs correspondent exactement à un
démarrage réel A=100/B=100 (100−30+12=82 ; 100−30=70), pas 60/40.

### Confirmation de la cause racine (audit avant modification)

`demarrerSimulation()` appelle, dans cet ordre exact (lignes ~11979-11980
avant ce correctif) :
```java
initialiserStocksProduits();
appliquerStocksInitiauxConfig();
```
`initialiserStocksProduits()` (Bloc M.1/M.1-FIX) construit correctement
`stockFiniParProduit` = {A=60, B=40} à partir de `stockInitialParProduit`
et du reliquat. Mais `appliquerStocksInitiauxConfig()`, juste après,
contenait (avant correctif) :
```java
if (champStockInitialProduitFini >= 0) {
    for (PosteGenericAgent p : postes) { ... p.niveauStock = Math.max(0, champStockInitialProduitFini); ... }
    synchroniserListeProduits();
    if (stockFiniParProduit != null) {
        for (ScenarioFlux produit : listeProduits) {
            stockFiniParProduit.put(cleProduit(produit.typeProduit), Math.max(0.0, champStockInitialProduitFini));
        }
    }
}
```
Ce bloc s'exécutait **inconditionnellement**, y compris en mode multi-produit,
et réinjectait le stock **global** (100) dans **chaque** produit de la map —
d'où A=100, B=100, agrégat=200. Confirmé par lecture directe du code (pas
supposé) : ce second appel avait bien été manqué par l'audit exhaustif M.2
(qui listait `consommerStockFiniProduit()`/`crediterStockFiniProduit()`/
`synchroniserStockFiniAgrege()` mais pas `appliquerStocksInitiauxConfig()`).

### Audit exhaustif complémentaire (tous les écrivains de stock fini)

Grep exhaustif de `stockFiniParProduit.put/clear/=` et
`niveauStock =/+=/-=` sur tout le master :

| Site | Classification | Verdict |
|---|---|---|
| `appliquerStocksInitiauxConfig()` L3775-3794 (avant fix) | initialisation | **BUG** — reconstruisait la map depuis le global en mode multi |
| `initialiserStocksProduits()` | initialisation | correct, source de vérité, non modifié |
| `consommerStockFiniProduit()` | consommation | correct (map → agrégat via `synchroniserStockFiniAgrege`), non modifié |
| `crediterStockFiniProduit()` | crédit | correct (map → agrégat), non modifié |
| `synchroniserStockFiniAgrege()` | compatibilité agrégée | correct, direction map→agrégat uniquement, non modifié |
| chargement JSON `postes[].niveauStock` (L~15263) | initialisation (par poste, avant tout calcul multi-produit) | hors périmètre, écrasé de toute façon par les 2 appels ci-dessus au démarrage du run |
| `PosteGenericAgent` Exit `onExit` (mono, `niveauStock += 1`) | crédit (mono uniquement) | correct, déjà audité en M.2, non modifié |

Confirmation : aucune autre fonction hors `initialiserStocksProduits()`,
`consommerStockFiniProduit()` et `crediterStockFiniProduit()` ne reconstruit
arbitrairement une valeur métier par produit. `synchroniserStockFiniAgrege()`
reste utilisée uniquement dans le sens map → agrégat.

### Correctif appliqué

`appliquerStocksInitiauxConfig()` sépare désormais explicitement les deux
modes :
- **Mono** (`!modeMultiProduitActif`) : logique legacy conservée à
  l'identique, ligne par ligne (aucun changement de comportement).
- **Multi** (`modeMultiProduitActif`) : ne touche plus jamais
  `stockFiniParProduit` (la map, déjà construite par
  `initialiserStocksProduits()` juste avant, reste la source de vérité) ;
  se contente d'appeler `synchroniserStockFiniAgrege(null)` pour
  resynchroniser `niveauStock` (agrégat de compatibilité) à partir de la
  map réelle. Direction strictement `map → agrégat`, jamais l'inverse.

### Tests statiques (raisonnement manuel, à confirmer par le run utilisateur)

| Test | Entrée | Attendu | Résultat du raisonnement sur le nouveau code |
|---|---|---|---|
| F-1 | global=100, A=60, B=40 (explicites) | A=60, B=40, agrégat=100 | reliquat=0 (sommeExplicite=100=global) → A=60, B=40 conservés ; `appliquerStocksInitiauxConfig()` ne touche plus la map ; agrégat resynchronisé=100. **Conforme** |
| F-2 | global=100, map vide, 2 produits | A=50, B=50, agrégat=100 | reliquat=100 réparti sur 2 non-configurés → 50/50 ; non ré-écrasé ensuite. **Conforme** |
| F-3 | global=100, A=80 explicite, B absent | A=80, B=20, agrégat=100 | reliquat=20 sur B seul (non configuré) → A=80, B=20 ; non ré-écrasé. **Conforme** |
| F-4 | global=100, A=80, B=50 (somme=130>global) | A=80, B=50, agrégat=130 (WARN, jamais ramené à 100) | `sommeExplicite(130) > stockGlobal(100)` → WARN loggé, reliquat=0, valeurs explicites conservées telles quelles ; `appliquerStocksInitiauxConfig()` ne force plus jamais niveauStock=global (100) — agrégat resynchronisé=130. **Conforme** |
| F-5 | Mono, `modeMultiProduitActif=false` | comportement legacy strictement inchangé | branche `if (!modeMultiProduitActif)` = code legacy identique, aucune ligne modifiée. **Conforme** |

### Régression M.2 — non affectée (confirmé)

Le run utilisateur apporte une preuve positive indépendante pour M.2 :
consommation isolée A/B fonctionnelle, crédit REAPPRO_1 exclusivement sur
PRODUIT_A fonctionnel, aucun crédit parasite sur B. Seule l'**initialisation**
était en cause — `consommerStockFiniProduit()`/`crediterStockFiniProduit()`
non modifiées dans ce correctif.

### Vues affichant la quantité de stock — mise à jour pour précision par produit

Demande complémentaire explicite de l'utilisateur : les vues montrant une
quantité de stock doivent désormais préciser la répartition par produit en
mode multi-produit (lecture seule, aucun impact sur le calcul du stock) :

- **Nouvelle fonction `detailStockFiniParProduit()`** (même principe que
  `detailStockMatiereParMatiere()` du Bloc A.3) : sérialise
  `stockFiniParProduit` en `"idProduit=valeur|idProduit=valeur|..."` ;
  chaîne vide en mono-produit (map non source de vérité dans ce mode).
- **Feuille Excel "Historique Dashboard"** : nouvelle colonne
  `"Finished Stock — détail par produit"` insérée juste après
  `"Finished Stock (Products)"` dans `historiqueDashboardColumns()` et
  `capturerPointHistoriqueDashboard()` (27 colonnes désormais, contre 26
  avant ce bloc). Purement additif — aucune colonne existante déplacée ou
  renommée.
- **Carte live du tableau de bord "Finished Stock"** : nouvelle fonction
  `stockFiniAffichageText()` remplace l'ancien
  `TextCode` `(int) stockProduitFiniDisponibleTotal()`. En mono-produit,
  rendu strictement identique (agrégat seul). En multi-produit, affiche
  `"<agrégat> (PRODUIT_A=60, PRODUIT_B=40)"`. À vérifier visuellement par
  l'utilisateur au prochain run : la largeur fixe du composant `Text`
  (`Width="200"`) n'a pas été agrandie — un nombre élevé de produits
  catalogués pourrait tronquer l'affichage (aucune régression fonctionnelle,
  uniquement un point de lisibilité à confirmer).
- La feuille Excel **"Performance par produit"** (existante, cf. Bloc
  M.2-TEST §6) restait déjà correcte et n'a pas été modifiée.

### Validations statiques

- XML bien formé (`xml.etree.ElementTree`) : OK
- IDs AnyLogic uniques : 1680/1680 (aucun doublon)
- `git diff --check` : aucune erreur (bruit de sauvegarde automatique
  AnyLogic pré-existant sur une ligne `<EmbeddedIcon>` hors périmètre de ce
  correctif, revenu à l'identique avant commit)
- Grep DataCo (`prophet|recalibrator|autocommande|dataco`, insensible à la
  casse) : 5 occurrences, toutes dans des commentaires pré-existants du
  Bloc M.2 documentant le portage technique depuis
  `reference/dataco-multiproduct/` (mécanisme uniquement, aucune donnée/logique
  DataCo réelle) — 0 nouvelle occurrence introduite par ce correctif
- `scenario_M2_multiproduit_AB.json` et `scenario_ZENER_SA_Togo_v39.json`
  inchangés (seul le `.alp` a été modifié)

**Commit** : `fix(generic): preserve per-product stock during run initialization`

**PR reste DRAFT. Aucun merge vers `main`. M.3 et Bloc B non commencés.**

## Bloc M.2-TEST-FIX-2 — vues multi-produit strictement read-only (2026-09-17)

**Déclencheur** : revue statique du commit `e41c4b5` par l'utilisateur.
`detailStockFiniParProduit()` était documentée "lecture seule" mais appelait
`synchroniserListeProduits()`, qui **reconstruit** `listeProduits` et
`catalogueProduits` — donc pas une lecture pure. La carte live appelant
`stockFiniAffichageText() → detailStockFiniParProduit() → synchroniserListeProduits()`
à chaque rafraîchissement graphique, un simple affichage pouvait ainsi
reconstruire des structures runtime, contraire à l'objectif d'une vue
d'observabilité.

### Correctif

Les deux fonctions lisent désormais **directement**
`stockFiniParProduit.keySet()` (copie triée pour un ordre déterministe),
sans plus jamais appeler `synchroniserListeProduits()` ni aucune autre
fonction d'écriture. `stockFiniAffichageText()` ne passe plus par
`detailStockFiniParProduit()` (suppression de l'aller-retour
sérialisation → split → re-parsing de doubles, cf. « option
simplification » demandée) : elle lit la map une seule fois, directement.

Vérifié par grep sur le corps des deux fonctions : 0 occurrence de
`synchroniserListeProduits` dans l'une ou l'autre.

Note sur le libellé affiché : la clé de `stockFiniParProduit` est déjà la
forme normalisée `cleProduit()` (trim + majuscules) — identique au nom
brut pour des identités déjà en majuscules comme `PRODUIT_A`/`PRODUIT_B`.
Aucun changement de rendu pour la fixture A/B actuelle.

`initialiserStocksProduits()`, `appliquerStocksInitiauxConfig()`,
`consommerStockFiniProduit()`, `crediterStockFiniProduit()`,
`stockProduitFiniDisponibleTotal()`, la fixture A/B, ZENER, le
réapprovisionnement et le PI/SCOR n'ont pas été touchés.

### Audit des deux modifications incidentes signalées dans `e41c4b5`

| Modification | Pourquoi elle apparaît | Origine | Nécessaire au fonctionnement | Existait dans une version précédente |
|---|---|---|---|---|
| `<Name>` : `SCONTO_SVU_FINAL_VALIDATED` → `SCONTO_SVU_GENERIC_MASTER` | Champ interne AnyLogic (identité du modèle dans l'IDE), déjà documenté comme oscillant entre ces deux valeurs à chaque session AnyLogic de l'utilisateur (cf. Bloc A, commit de dépôt du `ModelResources`) | Sauvegarde automatique AnyLogic — confirmé : `git show df8074d:...` (état juste avant cette session) avait encore `SCONTO_SVU_FINAL_VALIDATED`, changé en `GENERIC_MASTER` dans l'arbre de travail avant que je ne commence à éditer ce tour-ci (non détecté par mon `git diff --check`/grep DataCo, qui ne couvrent pas ce champ) | Non — purement cosmétique, aucun impact sur la compilation/exécution | Oui, `SCONTO_SVU_FINAL_VALIDATED` était la valeur committée à `df8074d` |
| **Décision explicite** : conservé à `SCONTO_SVU_GENERIC_MASTER`. Ce nom correspond au nom de fichier (`SCONTO_SVU_GENERIC_MASTER.alp`) et au rôle du fichier dans ce dépôt (master receiver de la lignée Generic, cf. CLAUDE.md) — le conserver élimine une incohérence nom-interne/nom-de-fichier plutôt que de la perpétuer. Ce n'est pas un maintien accidentel : c'est un choix motivé, documenté ici comme demandé. | | | | |
| Réapparition de `<ModelResources>` (25 `<Resource>`, `Location=FILE_SYSTEM`) | Manifeste des icônes de présentation du modèle | Sauvegarde automatique AnyLogic — même constat : absent à `df8074d` (0 occurrence), présent dans l'arbre de travail avant que je ne commence à éditer ce tour-ci | Probablement oui pour l'IDE AnyLogic (résolution des icônes `.png` par les formes de présentation), bien que l'audit précédent (commit `e32fbed`, avant cette session) ait vérifié que les références directes `<ClassName>`/`<Path>` par forme restent fonctionnelles même sans ce manifeste | Non — `e32fbed` l'avait explicitement supprimé après vérification, avant de réapparaître ici |
| **Décision explicite** : conservé cette fois (contrairement à `e32fbed`). Les 25 chemins référencés (`aiguillage.png`, `back-office.png`, `container.png`, etc. — vérifiés par lecture directe) correspondent exactement aux fichiers `.png` du dossier `model/` de ce dépôt (icônes de présentation légitimes, cf. inventaire CLAUDE.md), aucune trace DataCo. Le fait qu'AnyLogic régénère systématiquement ce manifeste à chaque sauvegarde IDE (constaté ici pour la 2e fois) indique qu'il s'agit d'un comportement de sérialisation propre à l'outil, pas d'un artefact fortuit isolé : le supprimer à nouveau ne ferait que recréer le même diff au prochain Build/Run de l'utilisateur. Décision : ne plus le supprimer par défaut à l'avenir, sauf demande explicite. | | | | |

Les deux artefacts proviennent donc de sessions AnyLogic de l'utilisateur
antérieures à ce tour (probablement lors du Build/Run ayant produit le
run réel du M.2-TEST-FIX), déjà présents dans l'arbre de travail avant que
je ne lise le fichier pour appliquer M.2-TEST-FIX — je ne les avais pas
détectés avant de committer `e41c4b5` faute d'avoir inspecté le diff complet
au-delà de `git diff --check`/grep DataCo/comptage d'IDs. Aucun des deux
n'affecte le correctif métier 60/40, qui reste exactement tel quel.

### Validations statiques

- XML bien formé : OK
- IDs AnyLogic uniques : 1680/1680 (inchangé — aucune structure `<Function>`
  XML ajoutée/retirée, seul du texte `AdditionalClassCode` modifié)
- `git diff --check` : aucune erreur
- 0 occurrence de `synchroniserListeProduits` (ni d'aucune autre fonction
  d'écriture) dans `detailStockFiniParProduit()`/`stockFiniAffichageText()`
- Grep DataCo : 5 occurrences, toutes des commentaires pré-existants
  documentant `reference/dataco-multiproduct/` (inchangées depuis `e41c4b5`)
- `scenario_M2_multiproduit_AB.json` et `scenario_ZENER_SA_Togo_v39.json`
  inchangés

**Commit** : `fix(generic): keep multi-product stock views read-only`

**PR reste DRAFT. Aucun merge vers `main`. M.3 non commencé.**

## VALIDATION UTILISATEUR DÉFINITIVE — M.1 + M.2 (2026-09-18)

Rejeu réel de `scenario_M2_multiproduit_AB.json` après `e41c4b5` + `596143a`.

**Initialisation** (t≈41,3 s) : `Finished Stock=100`, `PRODUIT_A=60`,
`PRODUIT_B=40`. **Consommation** isolée par référence confirmée sur les 2
premières commandes. **Bilan complet** : A (5 cmd, 50 livrées, stock final=13)
et B (4 cmd, 40 livrées, stock final=0) correspondent EXACTEMENT à
`A=60−50+3=13` / `B=40−40=0` avec 3 unités REAPPRO_1 (M1.5 count=3, toutes
créditées à PRODUIT_A). 9 commandes closes, PI_GLOBAL≈8.6237, aucune
exception, aucune erreur Excel.

**M.1 = TERMINÉ / FIGÉ. M.2 = TERMINÉ / FIGÉ.** Ne plus modifier
`initialiserStocksProduits()`, `appliquerStocksInitiauxConfig()`,
`consommerStockFiniProduit()`, `crediterStockFiniProduit()`,
`stockProduitFiniDisponibleTotal()` sauf bug runtime démontré.

## Bloc M.3 — réapprovisionnement autonome par produit (2026-09-18)

**Objectif** : `verifierPolitiqueStockProduit()` restait mono-scénario
(un seul `scRef` = `indexScenarioNominal()`, généralement le premier produit
catalogué) et son anti-doublon (`productionAutonomeEnCours`) était un flag
GLOBAL — un REAPPRO actif sur A bloquait à tort le déclenchement d'un REAPPRO
sur B, même si B était sous son propre seuil.

### Audit avant modification

| Mécanisme | Mono actuel | Risque multi | Décision M.3 |
|---|---|---|---|
| `verifierPolitiqueStockProduit()` | Sélectionne un seul `scRef` via `indexScenarioNominal()` (le scénario "DISTRIBUTION"/"ZENER", sinon le 1er non-test) | En multi, seul ce produit est jamais évalué — B n'est jamais réapprovisionné | Nouvelle branche multi : boucle sur `listeProduits` (snapshot), un appel par produit à une nouvelle fonction dédiée |
| `declencherProductionAutonome(sc, qte)` | Garde `productionAutonomeEnCours` (flag global) | Bloque un 2e produit tant qu'un 1er REAPPRO est ouvert, même sur un produit différent | Garde par produit en multi (`reapproActifPourProduit`), garde legacy inchangée en mono |
| `indexScenarioNominal()` | Retourne l'index d'UN SEUL scénario | Non réutilisable pour un déclenchement multi-produit | Non modifiée ; utilisée uniquement par la branche mono (inchangée) et par les fonctions hors périmètre M.3 (`scenarioPourCommande`, profils de test) |
| `stockFiniDisponiblePourScenario(sc, poste)` | Déjà correcte (branche mono/multi existante depuis M.1/M.2) | Aucun — déjà la bonne source de vérité en multi | Réutilisée telle quelle dans la nouvelle fonction par-produit (jamais `poste.niveauStock` directement) |
| `listeProduits`/`catalogueProduits` | Reconstruits par `synchroniserListeProduits()` | Boucler dessus pendant qu'une fonction interne les reconstruit = `ConcurrentModificationException` (déjà rencontré côté DataCo) ; confirmé que `stockFiniDisponiblePourScenario()` appelle elle-même `synchroniserListeProduits()` | Un seul appel à `synchroniserListeProduits()` avant la boucle, puis copie défensive (`produitsSnapshot`) jamais reconstruite pendant l'itération |
| `commandes` / statuts `CommandeAgent` | `SERVIE`/`EN_RETARD` = seuls statuts de clôture réellement utilisés (`EN_LIVRAISON`, `EN_COURS`, etc. = ouverts) ; confirmé par grep exhaustif de tous les `cmd.statut = "..."` du master — aucun `EXPIRED`/`CLOSE`/`TERMINEE` n'existe dans ce master | — | Anti-doublon fondé sur ces 2 seuls statuts de clôture, comme le fait déjà `lierCommandeAuReapproActif()` |
| `idScenario` | Déjà propagé correctement (`cmd.idScenario = sc.typeProduit`, Bloc A.1/M.2) | Aucun | Réutilisé tel quel comme identité produit du REAPPRO |
| Ordres `REAPPRO_*` | Prédicat `estOrdreReappro()` déjà existant (préfixe `"REAPPRO_"`) | Aucun | Réutilisé tel quel |
| `productionAutonomeEnCours` | Unique flag global, remis à `false` (a) au démarrage du run et (b) à la clôture Make d'un REAPPRO | Utilisé AUSSI par `calculerBesoinsNets()` (politique matière autonome, hors périmètre M.3) pour éviter un approvisionnement matière concurrent pendant qu'un REAPPRO gère sa propre analyse matière — ne peut pas être supprimé ni changé de type sans risquer de régresser ce mécanisme matière | Conservé tel quel comme signal global "au moins un REAPPRO ouvert" ; sa valeur à la clôture est recalculée exactement (`existeReapproOuvert()`) au lieu d'être figée à `false`, pour rester correcte quand un autre produit a encore un REAPPRO ouvert |
| Seuil / quantité de réappro | `champStockSecuriteProduit`, `champCoutLancementProduction`, `champCoutPossessionProduitAnnuel` : 3 scalaires GLOBAUX, sans aucun binding JSON (confirmé par grep) | — | Réutilisés identiquement pour CHAQUE produit (valeurs par défaut partagées) ; aucun champ JSON par produit inventé, conformément à l'instruction |
| Fréquence d'appel depuis `TacticalAgent` | `main.verifierPolitiqueStockProduit()` appelé au cycle tactique périodique + immédiatement après une commande MTS en attente (`analyserStockCommandeOrchestree()`) | Aucun changement de fréquence nécessaire | Les 2 call sites restent inchangés ; la boucle multi-produit s'exécute à chaque appel existant |

### Invariant MONO — vérifié par relecture ligne à ligne

`verifierPolitiqueStockProduit()` conserve sa branche originale **intacte,
caractère pour caractère** (seule différence : un `if (modeMultiProduitActif) { ...; return; }`
ajouté en tête de fonction, avant tout le code legacy). `declencherProductionAutonome()`
conserve sa garde `productionAutonomeEnCours` en mono ; le calcul de clôture
`existeReapproOuvert()` est mathématiquement identique à l'ancien `= false`
tant qu'un seul REAPPRO peut jamais être ouvert à la fois (garanti par la
garde mono elle-même). Confirmé par diff : les seules lignes **supprimées**
dans tout le commit sont les 3 gardes remplacées (`if (!modeExecution ||
productionAutonomeEnCours) return;`, `if (sc == null || quantite <= 0 ||
productionAutonomeEnCours) return;`, `productionAutonomeEnCours = false;`) —
aucune autre ligne de la branche mono n'a été touchée.

### Invariant MULTI

Nouvelle fonction `verifierPolitiqueStockPourUnProduit(ScenarioFlux scRef)`,
appelée une fois par produit catalogué (snapshot stable). Reproduit la
logique mono (délai de reconstitution, formule de Wilson bornée, garde
anti-REAPPRO parasite, garde de fin de campagne) avec 3 adaptations :
1. stock lu via `stockFiniDisponiblePourScenario(scRef, stockFini)` —
   jamais `stockFini.niveauStock` (agrégat de compatibilité uniquement).
2. Q* mis en cache PAR PRODUIT (`quantiteEconomiqueParProduit`, nouvelle
   map, même principe que `stockFiniParProduit`) au lieu du champ global
   `quantiteEconomiqueProduit` — gelé au premier calcul par produit
   (comportement C14.58/C14.66 reproduit indépendamment pour chaque
   référence). Le point de commande n'est pas mis en cache (il ne l'était
   déjà pas en mono : recalculé à chaque appel).
3. Anti-doublon via `reapproActifPourProduit(scRef.typeProduit)` — jamais
   le flag global.

Exemple validé par raisonnement (A stock=10, B stock=80, seuil=20) : A sous
le point de commande déclenche un REAPPRO ; B, au-dessus, ne déclenche rien.
Le stock agrégé A+B n'intervient à aucun moment dans la décision.

### Anti-doublon par produit

Nouvelles fonctions, strictement en lecture sur `commandes` (aucun nouveau
champ sur `CommandeAgent`) :
- `reapproActifPourProduit(String typeProduit)` : vrai si un ordre
  `REAPPRO_*` de ce produit (`idScenario`) est encore ouvert (statut ≠
  `SERVIE`/`EN_RETARD`). Utilisée par `declencherProductionAutonome()` en
  mode multi pour bloquer un doublon SUR LE MÊME produit tout en laissant
  passer un autre produit.
- `existeReapproOuvert()` : vrai si au moins un `REAPPRO_*` (tous produits
  confondus) est encore ouvert. Utilisée uniquement pour recalculer
  `productionAutonomeEnCours` à la clôture d'un REAPPRO, afin de ne jamais
  lever la garde à tort si un autre produit a encore un REAPPRO en cours
  (préservation du comportement `calculerBesoinsNets()`, hors périmètre).

Scénario validé par raisonnement : REAPPRO A en cours, A et B sous seuil →
A n'est pas redéclenché (déjà actif), B est déclenché (aucun REAPPRO B
actif). Une commande cliente réelle n'est jamais confondue avec un REAPPRO
autonome : `estOrdreReappro()` (préfixe `"REAPPRO_"`) reste le seul
prédicat de distinction, inchangé, utilisé partout où l'anti-doublon
s'applique.

### Déclenchement, identité, crédit

Chaîne inchangée et FIGÉE (M.2) : `declencherProductionAutonome(sc, qte)`
crée `cmd.idScenario = sc.typeProduit` (ligne déjà existante, non
modifiée) → unités `REAPPRO_x_F_n` → M1.5 → `crediterStockFiniProduit(cmd.idScenario, ...)`.
M.3 ne fait que décider QUAND et POUR QUEL produit déclencher ; le crédit
lui-même n'a pas été touché.

### Observabilité

Logs ajoutés, tous préfixés `[STOCK][<typeProduit>]`, uniquement sur les
2 événements réels (pas de log répété à chaque cycle si rien ne change) :
- `[STOCK][PRODUIT_A] Q* produit fini : ...` (une fois, au premier calcul
  du Q* de ce produit)
- `[STOCK][PRODUIT_A] sous seuil : stock=... seuil=...` (au moment du
  déclenchement effectif, juste avant `declencherProductionAutonome()`)

Le log "politique OK" suggéré en exemple par la consigne n'a volontairement
PAS été ajouté : il aurait fallu le logger à chaque cycle tactique pour
chaque produit au-dessus du seuil, ce qui contredit directement la consigne
« éviter un log à chaque cycle si rien ne change ». Aucune UI nouvelle.

### Tests M.3 à préparer (exécution utilisateur)

| Test | Attendu |
|---|---|
| M3-1 MONO | ZENER legacy, comportement strictement inchangé |
| M3-2 | A sous seuil / B OK → A seulement |
| M3-3 | B sous seuil / A OK → B seulement |
| M3-4 | A et B sous seuil → un REAPPRO A + un REAPPRO B |
| M3-5 | Cycle tactique suivant avant fin de production → aucun second REAPPRO A/B |
| M3-6 | Ordre produit clos et toujours sous seuil → nouveau REAPPRO autorisé |
| M3-7 | Chaque REAPPRO a `cmd.idScenario` exact |
| M3-8 | Sortie M1.5 d'un REAPPRO A → crédit A uniquement (idem B) |
| M3-9 | Somme map == Finished Stock |
| M3-10 | Aucune `ConcurrentModificationException` |

### Ce qui n'a PAS été modifié

`initialiserStocksProduits()`, `appliquerStocksInitiauxConfig()`,
`consommerStockFiniProduit()`, `crediterStockFiniProduit()`,
`stockProduitFiniDisponibleTotal()`, `indexScenarioNominal()`,
`estOrdreReappro()`, `lierCommandeEtReappro()`/`lierCommandeAuReapproActif()`/
`lierReapproAuxCommandesClientesEnAttente()`/`finaliserDependanceReappro()`,
`calculerBesoinsNets()` (politique matière), la fixture A/B, ZENER,
PI/SCOR, Blocs B/C/D/E.

### Validations statiques

- XML bien formé : OK
- IDs AnyLogic uniques : 1680/1680 (inchangé — uniquement du texte
  `AdditionalClassCode` modifié/ajouté)
- `git diff --check` : aucune erreur
- Grep DataCo : 6 occurrences (5 pré-existantes + 1 nouvelle, ma propre
  note de commentaire citant "la lignée DataCo" comme précédent du bug
  ConcurrentModification, exactement comme formulé par l'utilisateur) —
  toutes des commentaires de méthodologie, 0 logique/donnée DataCo importée
- Diff vérifié ligne par ligne : les 3 seules suppressions du commit sont
  les 3 gardes remplacées ; aucune autre ligne mono touchée
- `scenario_M2_multiproduit_AB.json` et `scenario_ZENER_SA_Togo_v39.json`
  inchangés

**Commit** : `feat(generic): make autonomous replenishment product-aware`

**PR reste DRAFT. Aucun merge vers `main`. Bloc B non commencé.**

## VALIDATION UTILISATEUR RUNTIME — M.3 MULTI (2026-09-18)

Rejeu réel de `scenario_M2_multiproduit_AB.json` après `f125bce`.

**Anti-blocage inter-produit** : `REAPPRO_1`/PRODUIT_A (origine
STOCK_AUTONOMOUS, qté=50, créé t=60, statut EN_COURS au snapshot) toujours
ouvert quand `REAPPRO_2`/PRODUIT_B est créé (STOCK_AUTONOMOUS, qté=50,
t=270, EN_COURS) — confirme qu'un REAPPRO actif sur A ne bloque plus le
déclenchement sur B.

**Anti-doublon par produit** : `REAPPRO_2` atteint P3.4/M1.1 à t=272 (qté
50) ; aucun `REAPPRO_3` observé sur ce run — aucun doublon créé tant que le
REAPPRO du même produit reste ouvert.

**Bilan quantitatif** : stock initial A=60/B=40, 3 commandes A×10 + 3
commandes B×10, M1.5 count=13 (crédits confirmés sur A uniquement à ce
stade — REAPPRO_2/B encore en cours dans Make à l'arrêt du run, donc son
crédit n'est pas encore attendu). Stock final A=43/B=10, total=53.
Bilan exact : `A = 60 − 30 + 13 = 43`, `B = 40 − 30 = 10`. Match exact.

**Tests M.3** : M3-2 ✅, M3-3 ✅, M3-4 ✅, M3-5 ✅, M3-7 ✅, M3-9 ✅, M3-10 ✅.
M3-6 (nouveau REAPPRO après clôture complète) non exercé par cette
campagne — limite de couverture de ce run, pas un blocage : le code de
`declencherProductionAutonome()`/`reapproActifPourProduit()` autorise par
construction un nouveau REAPPRO dès que le précédent atteint un statut
clos (`SERVIE`/`EN_RETARD`), mais aucun run n'a encore observé ce cas
précis en conditions réelles.

**M.3 MULTI = VALIDÉ.**

**Bloc M dans son ensemble reste EN ATTENTE** de la confirmation
utilisateur du run ZENER mono court (non-régression du comportement
legacy) avant d'être marqué TERMINÉ / FIGÉ. Bloc B non commencé.

## CONFIRMATION UTILISATEUR FINALE — CLÔTURE DU BLOC M (2026-09-18)

Run ZENER mono après `f125bce` : Build AnyLogic OK (0 erreur), scénario
ZENER mono OK, commandes OK, politique stock/REAPPRO OK, Make/Deliver OK,
comportement nominal OK, aucune exception, aucune régression constatée par
rapport au comportement legacy pré-Bloc M.

Combiné à la validation runtime M.3 multi-produit déjà enregistrée
ci-dessus (coexistence REAPPRO_1/PRODUIT_A et REAPPRO_2/PRODUIT_B,
anti-blocage inter-produit, anti-doublon, identité produit, agrégat
cohérent, chaîne Make fonctionnelle, aucune exception) :

**BLOC M = TERMINÉ / VALIDÉ / FIGÉ.**
- **M.1 = TERMINÉ / FIGÉ**
- **M.2 = TERMINÉ / FIGÉ**
- **M.3 = TERMINÉ / FIGÉ**

Ne plus modifier les mécanismes du Bloc M
(`initialiserStocksProduits()`, `appliquerStocksInitiauxConfig()`,
`consommerStockFiniProduit()`, `crediterStockFiniProduit()`,
`stockProduitFiniDisponibleTotal()`, `verifierPolitiqueStockProduit()`/
`verifierPolitiqueStockPourUnProduit()`, `declencherProductionAutonome()`,
`reapproActifPourProduit()`/`existeReapproOuvert()`) sauf bug runtime
réellement démontré.

**Limite de couverture documentée, non bloquante** : M3-6 (nouveau REAPPRO
du même produit après clôture complète du précédent) n'a pas été exercé
par un run réel à ce jour ; sa logique a été auditée statiquement
(`declencherProductionAutonome()`/`reapproActifPourProduit()` autorisent
par construction un nouveau REAPPRO dès que le précédent atteint un statut
clos `SERVIE`/`EN_RETARD`), mais reste à confirmer par un run futur si
l'occasion se présente.

## Bloc B — PI / SCOR

### Bloc B.1 — audit complet + fondations sûres (2026-09-18)

**Méthode** : lecture directe et comparaison ligne à ligne de `StrategicAgent.calculerPIGlobal()`,
`StrategicAgent.prevoirDemande()`, `Main.ajusterDebits()` entre `model/SCONTO_SVU_GENERIC_MASTER.alp`
(HEAD `85dfdfa`) et `reference/colleague/SCONTO_SVU_GENERIC10-4_COLLEAGUE.alp` — jamais les documents
`docs/merge/PHASE2_PI_SCOR_MERGE_NOTES.md`/`ANALYSE_FUSION_COLLEGUE_VS_MASTER.md`, conformément à la
consigne (le code final du collègue est la seule source technique prioritaire).

#### Tableau d'audit

| Élément | Master actuel | Collègue | Différence sémantique | Dépendances | Risque | Décision |
|---|---|---|---|---|---|---|
| `calculerPIGlobal()` | Périmètre = `board.kpiParMacro` (TOUTE la chaîne, y compris postes CLIENT/FOURNISSEUR) ; RL sur 4 métriques pondérées égales, jamais de garde d'échantillon ; RS sans focalisation entreprise ni décroissance lente ; CO utilise `nbTermines` (hybride) ; pas de warm-up ; agrégation finale sur poids bruts `w_RL..w_AM` (jamais de poids effectifs) | Périmètre reconstruit par entreprise focale (`ActeurSC.ENTREPRISE_FOCALE`) ; RL réduit à 1 métrique notée (RL.2.2) + garde `seuilMinEchantillonRL`, 3 autres en informatif poids 0 ; RS pondéré par passages réels (`unitesParMacro`/`nominalPondereParMacro`) + attente incluse ; CO utilise `unitesLivreesClients()` ; warm-up (`phaseAmorcagePI`) fige le PI à `ciblePIGlobal` tant que le périmètre n'est pas complet ; poids effectifs `wEff*` (famille sans donnée exclue de l'agrégation) | Réécriture profonde des 5 familles + de la boucle d'agrégation finale | `ActeurSC.ENTREPRISE_FOCALE`/`normaliserCategorieActeur()` (déjà présents), `dureeTraitementNominale()`/`majBorneCycleMacro()` (nouveaux), `nombreCommandesClosesFiabilite()`/`unitesLivreesClients()` (nouveaux), les 8 variables PI (nouvelles) | Élevé — fonction centrale, tout consommateur du PI est affecté | **REJET pour ce tour** ; **B.2** (RL/warm-up/poids effectifs) puis **B.3** (RS/périmètre focal, plus couplé à `majBorneCycleMacro()`) |
| `prevoirDemande()` | `debitActuel = main.nbTermines * 3600/time()` — **la PRÉVISION est calculée à partir de la PRODUCTION**, idem par produit via `nbTerminesParProduit` | `debitActuel` calculé depuis les **commandes CLIENTES créées** (`qteClientCreeeTotale`, exclut `REAPPRO_`), idem par produit via `idScenario`, garde de 2 commandes minimum + mesure depuis la 1re commande (pas depuis T=0) | **Boucle de rétroaction positive confirmée dans le master actuel** : plus `verifierPolitiqueStockProduit()`/`declencherProductionAutonome()` produisent (Bloc M.3), plus `nbTermines` monte, plus la prévision monte, plus `ajusterDebits()` vise un stock cible élevé, plus on produit — indépendamment du rythme réel des commandes clientes | Aucune (fonction autonome, ne lit que `commandes`/`scenarios`) | Confirmé, mais correction non triviale (garde d'échantillon, filtrage par produit) | **B.2** — priorité haute, cause racine identifiée et prouvée par lecture directe, mais nécessite un choix architectural (garde de démarrage, lissage) donc explicitement hors B.1 |
| `ajusterDebits()` | Boucle `for (ScenarioFlux sc : main.scenarios) { ... stockObserve = stockFini.niveauStock; ... }` — **lit l'agrégat `niveauStock` directement**, aucun plafond de sécurité sur `debitFinal` | Même structure, **plus un plafond** `plafond = sc.debitParHeureBase * plafondMultipleDebitBase; debitFinal = Math.min(debitFinal, plafond);` | **Bug multi-produit CONFIRMÉ par lecture de code (pas hypothétique)** : `trouverStockFiniPourScenario(sc)` renvoie le MÊME poste physique pour tous les scénarios dans les 3 scénarios groupés actuels (1 seul poste stock-fini par scénario) ; `stockFini.niveauStock` est l'AGRÉGAT de compatibilité (Bloc M, `synchroniserStockFiniAgrege()`) — en mode multi-produit à N produits, la boucle lit et somme ce MÊME agrégat N fois dans `totalStockObserve`, gonflant `stockFiniObserve` d'un facteur N ; `debitSouhaite`/`rattrapage` par produit utilisent aussi la mauvaise valeur (l'agrégat au lieu du stock du SEUL produit courant) | `stockFiniDisponiblePourScenario(sc, stockFini)` (Bloc M, déjà correcte et déjà utilisée ailleurs) | Confirmé et isolé (un seul point de lecture à corriger, ne touche à aucun mécanisme du Bloc M lui-même) mais modifie une fonction risquée/partagée | **B.2** — correctif ciblé et de faible ampleur (remplacer `stockFini.niveauStock` par `stockFiniDisponiblePourScenario(sc, stockFini)` dans la boucle), mais explicitement hors périmètre B.1 (B.1 n'autorise pas la modification de `ajusterDebits()`) |
| `codesProcessusPourMetriqueSCOR()`/`valeurRuntimeMetriqueSCOR()`/`sourceFormuleMetriqueSCOR()` | RL.2.1 → `tauxCommandesLivreesCloses()` (voir ligne suivante, fonction **dégénérée**) ; RL.2.2 → `verifierFillRate()` (fonction réellement correcte, malgré son nom) ; RL.3.32 → `verifierFillRate()` | RL.2.1/RL.2.2/RL.3.33/RL.3.35/RL.3.32 → tous `tauxCommandesLivreesCloses()` (sauf RL.3.32 → `verifierFillRate()` legacy, gardée pour compat) | **Collision de nommage entre master et collègue** (voir 2 lignes suivantes) — audité, non modifié | — | — | **Audité pour préparer B.3** (export SCOR), non modifié en B.1 comme demandé |
| `verifierFillRate()` | Renommée en interne ("ETAPE 3.1") : mesure en réalité RL.2.2 (ponctualité client), filtre `estCommandeClient()`, dénominateur = commandes CLIENTES **closes** (SERVIE+EN_RETARD) uniquement | Fonction legacy inchangée : `servies/commandes.size()` — dénominateur = **TOUTES** les commandes jamais créées (y compris en transit et REAPPRO_), bug déjà documenté par le collègue (C15.8) | **Le master a DÉJÀ corrigé indépendamment le bug que le collègue corrige aussi, mais sous un nom différent.** Master : `verifierFillRate()` = version corrigée. Collègue : `tauxCommandesLivreesCloses()` = version corrigée (nom différent) ; le `verifierFillRate()` du collègue reste l'ancienne version buguée, gardée uniquement pour RL.3.32 (legacy display) | — | Aucun changement de comportement requis ici : le master a déjà la bonne valeur, juste sous un nom qui ne correspond pas à celui du collègue | **REJET** (rien à porter — le master est déjà à parité fonctionnelle sur ce point précis, juste nommé différemment) |
| `tauxCommandesLivreesCloses()` | **Fonction dégénérée confirmée par lecture de code** : `if (SERVIE ou EN_RETARD) { closes++; livrees++; }` puis `return livrees/closes` — `livrees` est TOUJOURS égal à `closes`, donc la fonction renvoie **systématiquement 1.0** dès qu'une commande a clos, quel que soit le taux réel de retards. RL.2.1 (export SCOR) l'utilise directement : RL.2.1 affiche donc à tort "100%" en permanence dès la 1re commande close | Renommée avec la sémantique CORRECTE : `servies/(servies+enRetard+refusees+bloquees)`, exclut REAPPRO_, inclut les échecs terminaux (REFUSEE/BLOQUE_*) au dénominateur | **Bug réel, démontré par lecture de code, préexistant dans le master actuel** (indépendant de ce merge) : RL.2.1 ne discrimine jamais rien | Aucune (fonction autonome) | Moyen — corrige un export SCOR déjà visible utilisateur, mais touche une fonction nommée déjà utilisée ailleurs dans le master (mapping SCOR) | **B.3** (export SCOR) — documenté ici comme trouvaille B.1, correction proposée : soit renommer/réécrire `tauxCommandesLivreesCloses()` avec la sémantique collègue et réaffecter les mappings RL.2.1/RL.2.2 en conséquence, à valider explicitement avant toute écriture (renommage = risque de confusion avec l'existant) |
| `nombreCommandesClosesFiabilite()` | Absente | Présente, dépend de `cmd.retardConstate` (Bloc C, absent) | Nouvelle fonction | `estOrdreReappro`-like filtre (existe : `estOrdreStockAutonome`) | Faible — lecture seule sur `commandes` | **B.1 — PORTÉE**, adaptée (retire `\|\| cmd.retardConstate`, même précédent que A.2/A.4) |
| `unitesLivreesClients()` | Absente | Présente, aucune dépendance Bloc C | Nouvelle fonction | Aucune | Faible — lecture seule | **B.1 — PORTÉE** telle quelle |
| `dureeTraitementNominale()` | Absente | Présente, dépend de `LoiTemps.esperance()` (absente) | Nouvelle fonction | `LoiTemps.esperance()` (nouveau, pur, isolé) | Faible — lecture seule sur `PosteGenericAgent`/`LoiTemps` | **B.1 — PORTÉE**, avec `LoiTemps.esperance()` |
| `majBorneCycleMacro()` | Absente | Présente, dépend de `strategic.facteurToleranceCycleMacro` (absent) et construit un `NormalizationProfile` avec `decroissanceLente=true` | Nouvelle fonction, appelée UNIQUEMENT depuis la section RS.2.x de `calculerPIGlobal()` | `facteurToleranceCycleMacro` (nouveau), `NormalizationProfile.decroissanceLente` (porté en B.1, voir plus bas) | Moyen — seul appelant est `calculerPIGlobal()` (non modifié ce tour) | **REJET pour ce tour** (aucun appelant tant que RS.2.x n'est pas refondu) — **B.3** avec la refonte RS |
| `NormalizationProfile` / `decroissanceLente` | Classe présente (`score10()` = plancher linéaire PUIS coupure dure à 0 au-delà de `max`) | + champ `decroissanceLente` (défaut `false`, rétrocompatible), + constructeur 7 args, + branche hyperbolique `10*min/valeur` dans `score10()` si `decroissanceLente=true` | Purement additif : défaut `false` ⇒ AUCUN profil existant n'est affecté | Aucune | Faible — nouvelle branche jamais empruntée tant qu'aucun appelant ne construit `decroissanceLente=true` | **B.1 — PORTÉE** (mécanisme seul ; aucun appelant ne l'active encore, `majBorneCycleMacro()` différé à B.3) |
| `ActeurSC.ENTREPRISE_FOCALE` / `normaliserCategorieActeur()` | **Déjà présents** dans le master (utilisés massivement pour l'export ABox, `p.categorieActeurResponsable` déjà lu depuis le JSON) | Réutilisés dans `calculerPIGlobal()` pour reconstruire les bundles KPI par macro-processus filtrés à l'entreprise focale (C15.14) | Le master a déjà toute l'infrastructure de catégorisation d'acteur ; il manque seulement le CÂBLAGE dans `calculerPIGlobal()` | — | Faible techniquement (réutilisation), mais modifie `calculerPIGlobal()` | **B.3** (couplé à la refonte RS/périmètre, non isolable de `calculerPIGlobal()`) |
| 8 variables PI (`attributsPonderesPI`, `sommePoidsEffectifsPI`, `seuilMinEchantillonRL`, `perimetrePIDejaComplet`, `donneesRLPresentesPrecedent`, `donneesRSPresentesPrecedent`, `donneesAMPresentesPrecedent`, `dernierLogDetailSCOR`) | Absentes (confirmé par grep exhaustif avant ce bloc) | Présentes sur `StrategicAgent`, réinitialisées dans `demarrerSimulation()` | Nouvelles | Aucune (champs inertes tant que `calculerPIGlobal()` ne les lit/écrit pas) | Nul — déclarations seules | **B.1 — PORTÉES**, + reset dans `demarrerSimulation()` |
| `compteurCyclesExportExcel` / `verboseLogs` | Absent / présent (générique, déjà utilisé par `traceln()`) | Présents | Utilité confirmée hors Bloc B (export Excel = Bloc A.4 ; verbosité de logs = générique) | — | — | **REJET** (hors périmètre B, conformément à la consigne explicite) |
| `agregerN3()` / `poidsEffectifN3()` | Présents | Identiques caractère pour caractère (vérifié) | Aucune | — | Nul | **RAS** (déjà à parité) |

#### Point 1 — Périmètre entreprise focale
Le master dispose déjà de `ActeurSC.ENTREPRISE_FOCALE` et `normaliserCategorieActeur()`,
utilisés pour l'export ABox et l'assignation d'acteurs, mais **`calculerPIGlobal()` ne les
utilise pas** : il lit `board.kpiParMacro`, qui agrège TOUS les postes d'un macro-processus
sans filtrer par acteur responsable (un poste Source côté CLIENT ou FOURNISSEUR pèse
autant qu'un poste Source de l'entreprise focale). Le nom `ZENER` n'apparaît nulle part
dans ce mécanisme ni côté collègue ni côté master — le filtre repose uniquement sur
`categorieActeurResponsable` (donnée JSON), jamais sur un nom d'entreprise. Câblage
proposé pour B.3 : reconstruire des `KPIBundle` locaux filtrés comme le fait le collègue,
sans toucher à `board.kpiParMacro` (qui reste nécessaire ailleurs, ex. détection de goulots
sur la chaîne étendue).

#### Point 2 — Warm-up / amorçage
Condition de sortie exacte (collègue) : `perimetreComplet = (wEffRL>0 && wEffRS>0 &&
wEffAG>0 && wEffCO>0 && wEffAM>0)`, mémorisée une fois atteinte (`perimetrePIDejaComplet`,
jamais réévaluée à la baisse). Tant que non atteinte (et qu'un blocage structurel de CO
n'est pas détecté via `attenteImpossible`), le PI est maintenu à `ciblePIGlobal` (déjà
présent dans le master, valeur existante réutilisée). Aucun seuil arbitraire, aucun compte
de commandes ZENER hardcodé — la condition ne porte que sur la présence de poids effectifs
par famille SCOR.

#### Point 3 — Poids effectifs
Confirmé dans le code : chaque famille (RL/RS/AG/CO/AM) calcule `sommePoids{RL..AM}` =
somme des poids de ses métriques individuelles ; `wEff{RL..AM} = sommePoids>0 ? w_{RL..AM}
: 0`. `attributsPonderesPI` trace la liste des familles réellement incluses (ex.
"RL+AG+CO", jamais "RL+RS+AG+CO+AM" tant que RS ou AM manquent) ; `sommePoidsEffectifsPI`
est la somme de ces poids effectifs, permettant de recalculer le PI affiché à la main.
Aucune famille sans donnée n'est comptée comme performance nulle.

#### Point 4 — Reliability / RL
Code confirmé (pas les anciens documents) : seul **RL.2.2** est réellement pondéré dans le
PI côté collègue (`nRL=1`) ; RL.2.1/RL.3.33/RL.3.35 sont informatifs (poids 0), car ce
master ne simule ni erreur d'article ni erreur de quantité — les 4 indicateurs recopiaient
la même valeur sans être 4 mesures indépendantes. Seuil minimal : `seuilMinEchantillonRL`
(porté en B.1, défaut `1`, valeur du collègue — pas un hardcode ZENER). En dessous du
seuil, RL est exclu du PI (poids effectif 0) mais **reste affiché** avec une valeur
provisoire explicitement étiquetée hors-PI (`rlAffichage`, mention "provisoire, hors PI"),
jamais gonflé artificiellement à 10/10.

#### Point 5 — RS / Responsiveness
Chaîne collègue : temps de cycle macro = (temps de traitement CUMULÉ + temps d'ATTENTE
cumulé) / nombre d'unités entrées dans le macro (`unitesParMacro`), comparé à un nominal
lui-même pondéré par les mêmes passages réels (`nominalPondereParMacro`,
`dureeTraitementNominale()` × fréquence). La borne de normalisation devient un multiple
(`facteurToleranceCycleMacro`, défaut 10.0) du nominal pondéré, avec décroissance
hyperbolique (`decroissanceLente`) au lieu d'une coupure dure à 0 — un engorgement 56x
reste mesurablement pire qu'un engorgement 13x. Le mécanisme `NormalizationProfile`
correspondant est porté en B.1 ; `majBorneCycleMacro()` (l'appelant) est différé à B.3
car son seul point d'appel est la section RS.2.x de `calculerPIGlobal()`.

#### Point 6 — AG / AM et proxies
Confirmé : le collègue distingue explicitement `AG.3.32` (réelle) de
`PROXY.AG.SYSTEM_UTILIZATION` et renomme l'ancien `AG.1.1` (legacy master) en
`PROXY.AG.STABILITE_DEBIT` — même valeur (`coefficientAdaptabilite()`, identique dans les
2 modèles), mais présentée honnêtement comme proxy hors référentiel SCOR normatif. Idem
AM : `AM.3.9`/`PROXY.AM.DISPONIBILITE_MACHINE` — même valeur
(`calculerDisponibiliteMachinesMoyenne()`), renommée en proxy. `AM.2.2` (Inventory Days of
Supply) reste une métrique réelle des deux côtés. Ce renommage est purement une question
d'étiquetage de traçabilité SCOR (aucun changement de valeur) — couplé à la refonte
`calculerPIGlobal()`, donc différé à B.3.

#### Point 7 — Cost / CO
Confirmé : `unitesLivreesClients()` (porté en B.1) résout un biais réel — `nbTermines`
est un compteur HYBRIDE (incrémenté par unité en flux de production, mais une seule fois
par commande en livraison directe MTS), sous-estimant le CA d'un facteur proche de la
taille moyenne de commande en MTS pur (le mode nominal de ce master). REAPPRO_* déjà
exclus de `unitesLivreesClients()` (même filtre que `estOrdreStockAutonome()`/
`estCommandeClient()`, déjà existants dans le master). Câblage dans `CO.1.1` lui-même
différé à B.2/B.3 (modifie `calculerPIGlobal()`).

#### Point 8 — Prévision stratégique
**Bug de rétroaction confirmé dans le master actuel par lecture directe** :
`prevoirDemande()` calcule `debitActuel` à partir de `main.nbTermines` (production
terminée), pas des commandes clientes. Combiné au pilotage MTS de `ajusterDebits()`
(prévision → stock cible → décision de produire), ceci crée exactement la boucle que le
Bloc M.3 rend maintenant active et observable : plus le REAPPRO autonome produit, plus la
prévision monte, plus le stock cible monte, plus on produit. Le collègue calcule
`debitActuel` depuis les commandes CLIENTES créées (`cmd.tCreation`/`cmd.qte`, exclut
REAPPRO_), avec une garde de 2 commandes minimum et une mesure depuis la 1re commande
(pas depuis T=0). En multi-produit, le collègue filtre déjà correctement par
`cmd.idScenario` (`qteClientCreeeParProduit`), sans jamais utiliser le stock agrégé — le
Bloc M n'a pas besoin d'être rouvert pour porter ce correctif. **Priorité haute pour B.2**,
non portée ce tour car son intégration modifie une fonction consommée par
`calculerBesoinsNets()` (matière, hors périmètre) et nécessite un choix explicite sur le
comportement transitoire (garde d'échantillon, lissage) — non trivial au sens de la
consigne B.1.

#### Point 9 — Stock stratégique multi-produit
**Bug xN confirmé dans le MASTER ACTUEL (pas seulement dans l'ancien document Phase 2)** :
`ajusterDebits()` lit `stockFini.niveauStock` (l'agrégat de compatibilité du Bloc M) dans
une boucle `for (ScenarioFlux sc : main.scenarios)`. Avec les 3 scénarios groupés actuels,
chacun a son propre poste stock-fini physique (pas de partage), donc CE bug ne se
manifeste PAS aujourd'hui sur les scénarios fournis (vérifié) — mais **il se manifesterait
dès que 2 scénarios partageraient le même poste stock-fini physique** (exactement le cas
de la fixture `scenario_M2_multiproduit_AB.json`, où PRODUIT_A et PRODUIT_B partagent
`sM1.5.1`) : le même agrégat serait lu et sommé N fois dans `totalStockObserve`. Correctif
proposé (non appliqué ce tour) : remplacer `stockFini.niveauStock` par
`main.stockFiniDisponiblePourScenario(sc, stockFini)` (déjà existante, Bloc M, déjà
correcte) dans cette seule boucle de `ajusterDebits()`. Ceci ne modifie NI
`stockFiniParProduit` NI aucun mécanisme du Bloc M lui-même — uniquement ce que le
lecteur stratégique consomme. Différé à B.2 (hors liste des modifications autorisées en
B.1).

#### Point 10 — Exports SCOR
Audité sans modification, comme demandé. Trouvaille majeure documentée ci-dessus (tableau)
: `tauxCommandesLivreesCloses()` du master est une fonction dégénérée (retourne toujours
1.0 dès qu'une commande a clos) utilisée directement par le mapping RL.2.1 — un bug
préexistant, indépendant de ce merge, à corriger en B.3 avec le reste des exports SCOR.
`verifierFillRate()` du master est en réalité déjà correcte (renommage historique du
master, sans lien avec le nommage du collègue). Décision de renommage/réaffectation des
mappings SCOR différée à B.3, pour éviter de bundler cette correction avec les fondations
de ce tour.

### Fondations portées en B.1 (2026-09-18)

- `LoiTemps.esperance()` — espérance théorique de la loi de temps (pure, isolée).
- `NormalizationProfile.decroissanceLente` (champ, défaut `false`) + constructeur 7 args +
  branche hyperbolique dans `score10()` — rétrocompatible, aucun profil existant affecté.
- `Main.dureeTraitementNominale(PosteGenericAgent)` — lecture seule.
- `Main.nombreCommandesClosesFiabilite()` — adaptée (sans `cmd.retardConstate`, absent de
  ce master, même précédent que Bloc A.2/A.4).
- `Main.unitesLivreesClients()` — portée telle quelle.
- 8 variables PI sur `StrategicAgent` (`attributsPonderesPI`, `sommePoidsEffectifsPI`,
  `seuilMinEchantillonRL`, `perimetrePIDejaComplet`, `donneesRLPresentesPrecedent`,
  `donneesRSPresentesPrecedent`, `donneesAMPresentesPrecedent`, `dernierLogDetailSCOR`) +
  remise à zéro dans `demarrerSimulation()`.

**Aucune de ces fondations n'est encore consommée** : `calculerPIGlobal()`, `prevoirDemande()`,
`ajusterDebits()` et les exports SCOR restent strictement inchangés ce tour, conformément à
la consigne B.1. Les fondations sont donc du code mort jusqu'à B.2/B.3 — vérifié par grep
(aucune des 8 variables, ni `dureeTraitementNominale()`, ni `nombreCommandesClosesFiabilite()`,
ni `unitesLivreesClients()`, ni `decroissanceLente` n'apparaît en dehors de leurs propres
déclarations et du reset de `demarrerSimulation()`).

### Non touché en B.1
`calculerPIGlobal()`, `prevoirDemande()`, `ajusterDebits()`, `analyserEtat()`, tous les
exports SCOR (`codesProcessusPourMetriqueSCOR()`/`valeurRuntimeMetriqueSCOR()`/
`uniteMetriqueSCOR()`/`sourceFormuleMetriqueSCOR()`), `verifierFillRate()`,
`tauxCommandesLivreesCloses()`, `majBorneCycleMacro()`, tout mécanisme du Bloc A ou du
Bloc M, la fixture A/B, ZENER, le JSON/scénarios, les Blocs C/D/E.

### Validations statiques
- XML bien formé : OK
- IDs AnyLogic uniques : 1680/1680 (inchangé — uniquement du texte `AdditionalClassCode`
  ajouté, aucun nouvel élément `<Function>`/`<Variable>` XML)
- `git diff --check` : aucune erreur
- Grep DataCo (`prophet|recalibrator|autocommande|dataco`) : 6 occurrences, toutes
  pré-existantes (commentaires méthodologiques déjà présents avant ce bloc) — 0 nouvelle
  occurrence introduite par les fondations B.1
- Diff purement additif : 122 lignes ajoutées, 0 supprimée (confirmé par `git diff --stat`)
- Aucun changement JSON/scénario (`scenario_M2_multiproduit_AB.json`,
  `scenario_ZENER_SA_Togo_v39.json` inchangés)
- Aucun changement Bloc C/D/E

**Commit** : `feat(generic): prepare PI SCOR measurement foundations`

**PR reste DRAFT. Aucun merge vers `main`. B.2 non commencé.**

### Bloc B.2 — cœur PI/SCOR (2026-09-18)

Port du cœur fonctionnel : `prevoirDemande()`, `ajusterDebits()`,
`calculerPIGlobal()` (périmètre focal + RL + RS + AG + CO + AM + poids
effectifs + warm-up + traçabilité), + `majBorneCycleMacro()` et 2 nouvelles
variables de configuration statique (`facteurToleranceCycleMacro`,
`plafondMultipleDebitBase`). B.3 reste réservé aux mappings/export SCOR.

#### 1. `prevoirDemande()` — boucle de rétroaction corrigée

Portage intégral de la logique du donneur (aucune adaptation nécessaire,
toutes les dépendances existaient déjà) : la demande est désormais calculée
depuis les **commandes clientes créées** (`cmd.tCreation`/`cmd.qte`,
`REAPPRO_*` systématiquement exclus), plus jamais depuis `nbTermines`/
`nbTerminesParProduit` (production). Garde de démarrage portée telle
quelle : minimum 2 commandes clientes, mesure du débit depuis la 1ʳᵉ
commande (pas depuis T=0). En multi-produit, la demande par produit filtre
strictement par `cmd.idScenario` — jamais par stock agrégé. Lissage
exponentiel (`alpha=0.3`) préservé à l'identique.

#### 2. `ajusterDebits()` — lecture de stock multi-produit + plafond

Une seule ligne changée dans la boucle par scénario :
`stockObserve = stockFini.niveauStock` → `main.stockFiniDisponiblePourScenario(sc, stockFini)`
(déjà la source de vérité figée du Bloc M). Invariant vérifié : en mono,
`stockFiniDisponiblePourScenario()` retourne exactement `fallback.niveauStock`
(ou 0 si `stockFini==null`) — comportement historique byte-identique. En
multi, chaque produit lit sa propre entrée de `stockFiniParProduit`, plus
jamais l'agrégat. `stockFiniParProduit` lui-même n'est ni recalculé ni
modifié par ce changement. Ajout du plafond de sécurité (valeur exacte du
donneur, `plafondMultipleDebitBase=3.0`) : `debitFinal = min(debitFinal, sc.debitParHeureBase * plafondMultipleDebitBase)`.
`plafondMultipleDebitBase` et `facteurToleranceCycleMacro` sont des
configurations statiques (jamais mutées à l'exécution dans le donneur) :
**non réinitialisées** par `demarrerSimulation()`, contrairement aux 8
champs d'état du Bloc B.1.

#### 3. `calculerPIGlobal()` — périmètre focal + RL + RS + AG + CO + AM + poids effectifs + warm-up

**Périmètre entreprise focale** : les bundles `sP/sS/sM/sD/sR` sont
désormais reconstruits localement en n'agrégeant que les micro-activités
dont `normaliserCategorieActeur(p.categorieActeurResponsable) == ActeurSC.ENTREPRISE_FOCALE`
(infrastructure déjà présente dans ce master, simplement câblée ici pour la
première fois dans le calcul du PI). Aucun test sur un nom d'entreprise
(`ZENER` n'apparaît nulle part dans ce mécanisme). `board.kpiParMacro`
n'est pas muté — il continue d'alimenter les vues et la détection de
goulots sur la chaîne étendue.

**Adaptation documentée (écart volontaire par rapport au code donneur)** :
le donneur consolide tout RL sur sa fonction `tauxCommandesLivreesCloses()`.
Cette fonction existe déjà dans ce master **sous le même nom mais avec une
sémantique dégénérée** (retourne toujours 1.0 dès qu'une commande a clos —
confirmé par l'audit B.1). L'appeler aurait affiché RL à tort en
permanence à 10/10, ce qui aurait rendu tout le mécanisme de warm-up/poids
effectifs de ce bloc invérifiable (RL toujours "disponible et parfait").
`main.verifierFillRate()` de ce master calcule déjà exactement le ratio
recherché (commandes clientes livrées à temps parmi les commandes clientes
closes) sous un nom différent — **substitué à la place**, conformément au
principe "composer/réutiliser, ne pas dupliquer" établi en B.1.
`tauxCommandesLivreesCloses()` lui-même n'est **pas modifié** (reste
dégénéré, correction différée à B.3 avec les mappings RL, comme demandé).
La garde d'échantillon (`nombreCommandesClosesFiabilite()`/`seuilMinEchantillonRL=1`,
Bloc B.1) est en revanche portée exactement comme le donneur — **note
explicite** : avec seuil=1, la garde protège uniquement le cas n=0 ; elle
ne constitue **pas** une garantie de robustesse statistique sur petits
échantillons (n=1 n'est pas "statistiquement suffisant"), documenté tel
quel dans le code et ici, jamais présenté comme plus robuste qu'il ne
l'est.

**RL** : seule RL.2.2 pondérée (nRL=1) ; RL.2.1/RL.3.33/RL.3.35 informatives
(poids 0, mêmes proxies qu'avant, plus honnêtement étiquetées). Sous le
seuil d'échantillon, RL reste affichée en "provisoire, hors PI"
(`rlAffichage`), jamais gonflée à 10/10.

**RS** : temps de cycle macro = (traitement cumulé + attente cumulée) /
unités entrées dans le macro (`unitesParMacro`), nominal pondéré par les
mêmes passages réels (`nominalPondereParMacro` → `dureeTraitementNominale()`).
`majBorneCycleMacro()` (nouveau, Main) construit un `NormalizationProfile`
avec `decroissanceLente=true` **uniquement pour les 4 codes RS.2.x**
(`RS.2.1/RS.2.2/RS.2.3/RS.2.5`) — jamais activée globalement, jamais pour
RL/AG/CO/AM. `ltG`/`wtG` réutilisent les wrappers déjà existants et déjà
corrects de ce master (`main.orderFulfillmentLeadTimeGlobal()`,
`main.tempsAttenteGlobalCoherent()`), pas d'appel direct non gardé à
`board.kpiGlobal.avgLeadTime()`.

**AG** : `AG.3.32` (réelle) inchangée ; l'ancien `AG.1.1` est renommé
`PROXY.AG.STABILITE_DEBIT` — même valeur (`coefficientAdaptabilite()`),
étiquetage honnête uniquement, aucun changement de calcul.

**CO** : `unitesLivreesClients()` (Bloc B.1) remplace `main.nbTermines`
comme assiette de chiffre d'affaires estimé — corrige la sous-estimation
d'un facteur proche de la taille moyenne de commande en MTS pur. Formule
`ratio = coutTotal / (chiffreAffaireParUnite × unitésFacturables)`
inchangée, `REAPPRO_*` déjà exclus par `unitesLivreesClients()`.

**AM** : `AM.2.2` (réelle) inchangée, gardée par `debitObserve` (évite de
compter un "0 jour de stock" avant tout débit observé). L'ancien `AM.3.9`
est renommé `PROXY.AM.DISPONIBILITE_MACHINE` — même valeur
(`calculerDisponibiliteMachinesMoyenne()`), étiquetage honnête uniquement.

**Poids effectifs** : `sommePoids{RL..AM}` calculée par famille ;
`wEff{RL..AM} = sommePoids>0 ? w_{RL..AM} : 0`. Le PI final s'agrège
uniquement sur les `wEff*`, jamais sur les poids bruts. `attributsPonderesPI`
trace les familles réellement incluses ; `sommePoidsEffectifsPI` permet de
recalculer le PI affiché à la main.

**Warm-up** : `perimetreComplet = wEffRL>0 && wEffRS>0 && wEffAG>0 && wEffCO>0 && wEffAM>0`,
mémorisé une fois atteint (`perimetrePIDejaComplet`, jamais réévalué à la
baisse — ne revient plus artificiellement en amorçage sur une absence
ponctuelle ultérieure). Avant complétude (et hors blocage structurel de CO
via `attenteImpossible`), `pi = ciblePIGlobal`.

**Traçabilité** : logs de transition `[SCOR]` (une fois par famille, au
premier passage en données réelles) + `[SCOR-DETAIL]` throttlé à 5s via
`dernierLogDetailSCOR` (Bloc B.1) — aucun nouveau flag `verboseLogs`
introduit.

#### Ce qui n'a PAS été modifié en B.2

`codesProcessusPourMetriqueSCOR()`, `valeurRuntimeMetriqueSCOR()`,
`uniteMetriqueSCOR()`, `sourceFormuleMetriqueSCOR()`, `tauxCommandesLivreesCloses()`
(reste dégénérée, correction différée à B.3), `verifierFillRate()` (réutilisée
telle quelle), `Main.stockFiniParProduit`/mécanismes du Bloc M,
`initialiserStocksProduits()`, `appliquerStocksInitiauxConfig()`,
`consommerStockFiniProduit()`, `crediterStockFiniProduit()`,
`stockProduitFiniDisponibleTotal()`, `verifierPolitiqueStockProduit()`,
`verifierPolitiqueStockPourUnProduit()`, `declencherProductionAutonome()`,
la fixture A/B, ZENER, le JSON/scénarios, les Blocs C/D/E
(`retardConstate`, `modeEngagementClient`, `dureeClientAccumulee`,
`evaluerRetardsCommandesOuvertes()` non introduits).

#### Tests statiques B.2 (raisonnement sur le code, à confirmer par Build/run)

| Test | Vérification |
|---|---|
| B2-1 | `prevoirDemande()` ne contient plus aucun appel a `main.nbTermines`/`nbTerminesParProduit` (grep : seules 3 occurrences, toutes dans des commentaires expliquant le retrait) |
| B2-2 | Toutes les boucles de `prevoirDemande()` excluent `cmd.idCommande.startsWith("REAPPRO_")` |
| B2-3 | Demande par produit indexée sur `cmd.idScenario` (`qteClientCreeeParProduit`/`nbCommandesParProduit`/`tPremiereCommandeParProduit`) |
| B2-4 | Mono : `stockFiniDisponiblePourScenario()` retourne `fallback.niveauStock` à l'identique (lu dans son propre code, Bloc M, non modifié) |
| B2-5 | Multi : chaque produit lit sa propre entrée `stockFiniParProduit[cle]`, jamais l'agrégat (même fonction figée) |
| B2-6 | `plafond = sc.debitParHeureBase * plafondMultipleDebitBase` (3.0, valeur exacte du donneur), `debitFinal = Math.min(debitFinal, plafond)` |
| B2-7 | `wEff{RL..AM}` à 0 si `sommePoids{RL..AM}==0` ; PI agrégé uniquement sur les `wEff*` |
| B2-8 | `phaseAmorcagePI` maintient `pi = ciblePIGlobal` tant que `!perimetrePIDejaComplet && !perimetreComplet && !attenteImpossible` |
| B2-9 | `commandesClosesPresentes = nbCommandesClosesRL >= seuilMinEchantillonRL` ; poids RL forcé à 0 sous le seuil |
| B2-10 | `ctS/ctM/ctD/ctR = (sumCycleTime + sumWaitTime) / unités entrées`, nominal via `dureeTraitementNominale()` pondéré par passages réels |
| B2-11 | `unitesFacturables = main.unitesLivreesClients()`, utilisé pour `ratioCoutCA` |
| B2-12 | `estOrdreStockAutonome`/préfixe `REAPPRO_` exclu dans `verifierFillRate()`, `unitesLivreesClients()`, `nombreCommandesClosesFiabilite()`, `prevoirDemande()` |
| B2-13 | `PROXY.AG.SYSTEM_UTILIZATION`, `PROXY.AG.STABILITE_DEBIT`, `PROXY.AM.DISPONIBILITE_MACHINE` explicitement préfixés `PROXY.` |
| B2-14 | Grep de `ajusterDebits()` : 0 occurrence de code lisant `niveauStock` (seules des mentions en commentaire) |
| B2-15 | Grep DataCo sur le diff B.2 : 0 nouvelle occurrence (voir Validations) |

#### Validations statiques

- XML bien formé : OK
- IDs AnyLogic uniques : 1680/1680 (inchangé — uniquement des corps de
  `<Function>` existantes réécrits + texte `AdditionalClassCode` ajouté,
  aucun nouvel élément XML `<Function>`/`<Variable>`)
- `git diff --check` : aucune erreur
- Grep DataCo (`prophet|recalibrator|autocommande|dataco`) : 6 occurrences,
  toutes pré-existantes (inchangé depuis B.1)
- Diff : 374 insertions / 78 suppressions (les 78 suppressions correspondent
  aux corps remplacés de `prevoirDemande()`/`ajusterDebits()`/`calculerPIGlobal()`
  eux-mêmes, pas à une régression ailleurs)
- Fixture A/B (`scenario_M2_multiproduit_AB.json`) et ZENER
  (`scenario_ZENER_SA_Togo_v39.json`) inchangés
- Blocs A/M non touchés (vérifié par grep des noms de fonctions listés
  ci-dessus, absents du diff)
- Blocs C/D/E non commencés

**Commit** : `feat(generic): refactor PI SCOR core measurements`

**PR reste DRAFT. Aucun merge vers `main`. B.3 non commencé.**

## VALIDATION UTILISATEUR RUNTIME — B.2 + BLOC B.2-FIX (2026-09-18)

Deux runs réels après `34c5e5a` (ZENER mono : 8 commandes closes, PI≈7.682 ;
fixture A/B : 7 commandes closes, stock final A=33/B=10, REAPPRO_1→PRODUIT_A,
REAPPRO_2→PRODUIT_B) confirment : **`prevoirDemande()` VALIDÉE runtime**
(prévisions cohérentes avec le rythme des commandes clientes, mono≈165-166
ent/h, multi≈185-187 ent/h) ; **`ajusterDebits()` VALIDÉE runtime en multi**
(stock stratégique = Dashboard Finished Stock, plus de multiplication
agrégée : T=1320 stock=41=Dashboard 41) ; RS fini et discriminant
(RS.2.2≈1.5-1.9/10) ; CO actif (~9.5/10) ; aucune régression Bloc M.

Trois bugs runtime confirmés et corrigés dans ce même commit :

### 1. Proxies AG/AM non calibrés (score 0/F au lieu d'un score réel)

**Cause racine identifiée par lecture de code** : le renommage B.2
`AG.1.1 → PROXY.AG.STABILITE_DEBIT` / `AM.3.9 → PROXY.AM.DISPONIBILITE_MACHINE`
devait être un changement d'étiquetage honnête, sans impact numérique. Mais
`initialiserProfilsNormalisationDefaut()` n'enregistrait un profil que sous
les **anciens** codes — `scorePerformanceMetriqueSCOR()` ne trouvait donc
aucun profil pour les nouveaux codes, et son repli de secours (réservé aux
préfixes `RL./RS./AG./CO./AM.`, jamais `PROXY.`) retombait sur `Double.NaN`,
traité ensuite comme un grade F (score 0) par l'agrégation floue — alors que
les valeurs réelles (~0.94-0.95 dans les 2 runs) auraient dû scorer près de
10/10.

**Correctif** : alias exact des profils historiques (mêmes
direction/min/max/source, aucune nouvelle borne inventée) sous les nouveaux
codes — `PROXY.AG.STABILITE_DEBIT` reprend exactement le profil `AG.1.1`
(`BENEFIT`, 0.0→1.0), `PROXY.AM.DISPONIBILITE_MACHINE` reprend exactement le
profil `AM.3.9` (`BENEFIT`, 0.0→1.0). Les anciens codes `AG.1.1`/`AM.3.9`
restent enregistrés (compatibilité mappings legacy, non touchés en B.2/B.3).
Ancienne valeur numérique = nouvelle valeur numérique ; seul le code/libellé
devient honnêtement PROXY.

### 2. AM.2.2 (Inventory Days of Supply) retournait 0 malgré un stock et un débit non nuls

**Audit demandé avant toute modification** : `calculerInventoryDaysOfSupply()`
filtrait les postes via `p.typePoste == TypePoste.STOCKAGE`. Vérification
directe des 3 scénarios JSON fournis (ZENER, vélo urbain, automobile GX5) :
**tous les postes de stockage, y compris le poste produit fini
(`sM1.5.1`, "Transfert vers magasin produits finis"), sont typés `DELAI`,
jamais `STOCKAGE`.** Le filtre ne matchait donc structurellement AUCUN
poste dans ces scénarios ; `aDesStocks` restait faux et la fonction
retournait 0 avant même de lire un stock ou un débit. Ce n'était ni une
sentinelle "aucune donnée" ni une vraie rupture de stock : une mauvaise
source de lecture, confirmée par lecture directe des scénarios.

**Équation documentée** : `Inventory Days of Supply = stock fini pertinent
/ débit journalier pertinent` (jours). Stock : `stockProduitFiniDisponibleTotal()`
(Bloc M, déjà mono/multi-produit-safe). Débit : `nbTermines`/
`board.totalTerminees` ramené à un débit journalier (`× 86400 / time()`) —
**non modifié**, la cause démontrée du bug est uniquement le filtre de
stock, pas le débit.

**Correctif** : remplace le filtre `p.typePoste == TypePoste.STOCKAGE` par
`estPosteStockFini(p)` (même prédicat que le Bloc M : `TypePoste.STOCKAGE`
EN PLUS d'un repli codeSCOR/nom pour les postes `DELAI` comme M1.5) pour
détecter la présence d'un poste produit fini, et
`stockProduitFiniDisponibleTotal()` pour la valeur elle-même — au lieu de
resommer manuellement `p.niveauStock`, ce qui aurait pu réintroduire un
risque de double comptage multi-produit déjà corrigé ailleurs (Bloc M).
Aucune source de vérité du Bloc M n'est modifiée : uniquement son lecteur
côté AM.

### 3. Warm-up : premiers snapshots Historique Dashboard à PI=0 au lieu de PI=cible

**Audit de la cause** : `capturerPointHistoriqueDashboard()` (Bloc A.4) lit
`strategic.piGlobalCourant` **directement**, sans jamais appeler
`calculerPIGlobal()`. Ce champ démarre à `0` (valeur d'initialisation de la
`Variable`) et `demarrerSimulation()` ne le réinitialisait pas à
`ciblePIGlobal` au démarrage du run (contrairement aux 8 autres champs
PI/SCOR du Bloc B.1, qui le sont). La logique de warm-up de
`calculerPIGlobal()` elle-même (Bloc B.2, `pi = ciblePIGlobal` tant que le
périmètre est incomplet) n'a donc aucun effet sur ces tout premiers
snapshots, puisqu'elle n'a pas encore été exécutée à cet instant — pas un
défaut de la logique de warm-up elle-même, mais un champ affiché qui n'était
pas encore aligné dessus.

**Correctif** : `strategic.piGlobalCourant = strategic.ciblePIGlobal;`
ajouté au même bloc de remise à zéro par run que les 8 champs du Bloc B.1,
dans `demarrerSimulation()`. Aucun calcul prématuré de `calculerPIGlobal()`
n'est forcé — uniquement l'état affiché avant le premier calcul réel.

### Point documenté, non corrigé (dette assumée, hors périmètre de ce fix)

Run mono : un log stratégique à T=1740 montre `stock=185` alors que le
Finished Stock Dashboard ≈37 (le run multi, lui, est exact : T=1320
stock=41=Dashboard 41). Semble provenir de la logique legacy mono qui
parcourt plusieurs `ScenarioFlux` en lisant le même stock global — mais
l'invariant B.2 explicite est "mono = comportement legacy préservé", donc
**non corrigé dans ce fix sans audit architectural plus large**. Documenté
ici comme dette/point de revue future (Bloc D ou post-merge), pas comme
régression B.2.

### Ce qui n'a PAS été modifié

`prevoirDemande()`, la logique REAPPRO, la fixture A/B, le JSON ZENER, les
Blocs A/M (`estPosteStockFini()` réutilisée telle quelle, jamais modifiée),
les mappings d'export SCOR (différés à B.3 sauf les 2 lignes d'ajout de
profil strictement nécessaires à la calibration des proxies), les Blocs
C/D/E.

### Validations statiques

- XML bien formé : OK
- IDs AnyLogic uniques : 1680/1680 (inchangé)
- `git diff --check` : aucune erreur (bruit de sauvegarde automatique
  AnyLogic pré-existant sur une ligne `<EmbeddedIcon>`, hors périmètre de ce
  correctif, revenu à l'identique avant commit — même motif déjà rencontré
  et documenté dans les blocs précédents)
- Grep DataCo : 6 occurrences, toutes pré-existantes (inchangé depuis B.2)
- Blocs A/M non touchés (vérifié par grep des noms de fonctions listés
  ci-dessus)
- Fixture A/B et ZENER inchangés

**Commit** : `fix(generic): preserve proxy calibration and PI warmup semantics`

**PR reste DRAFT. Aucun merge vers `main`. B.3 non commencé.**

## VALIDATION UTILISATEUR RUNTIME — B.2/B.2-FIX (2026-09-18)

Deux nouveaux runs confirment les 3 corrections B.2-FIX : warm-up affiché
correctement (PI courant=cible=7.5 aux premiers snapshots) ; proxies
calibrés (`PROXY.AG.STABILITE_DEBIT` profil 0.000→1.000, score≈9.31-9.64 ;
`PROXY.AM.DISPONIBILITE_MACHINE` profil 0.000→1.000, score≈9.41) ; AM.2.2
quantitativement vérifié (mono : 40/(14.858×24)≈0.1122j match exact ;
multi : 30/(14.890×24)≈0.08395j match exact). PI final mono≈9.179, multi
9 commandes closes, aucune erreur Excel, aucune régression Bloc M.
**B.2 = VALIDÉ RUNTIME. B.2-FIX = VALIDÉ RUNTIME. Mécanismes B.2 FIGÉS**
sauf bug démontré.

## Bloc B.3 — alignement final PI / SCOR / exports (2026-09-18)

Dernier sous-bloc du Bloc B : aligne le catalogue/mappings d'export SCOR
(`codesProcessusPourMetriqueSCOR()`, `valeurRuntimeMetriqueSCOR()`,
`uniteMetriqueSCOR()`, `sourceFormuleMetriqueSCOR()`) et
`tauxCommandesLivreesCloses()` sur la sémantique déjà validée en runtime
par B.2/B.2-FIX. **`calculerPIGlobal()` n'a pas été modifiée** — audit
préalable a confirmé qu'aucune incohérence ne le nécessitait (voir
ci-dessous).

### Audit préalable — Pipeline SCOR vs Traçabilité performance

Vérifié par lecture de code que `n3ToN1Rows()` ("Pipeline SCOR vers PI")
et `piTraceabilityRows()` ("Traçabilité performance") lisent TOUTES LES
DEUX directement `strategic.detailN3` — la liste de `MetriqueN3` peuplée
par `calculerPIGlobal()` lui-même (valeur, unité, poids, score déjà
calculés). Elles ne recalculent JAMAIS ces valeurs indépendamment ; les
seuls appels externes par code qu'elles font sont
`normalizationProfiles.get(code)` (Bottom→Perfect, déjà corrigé en
B.2-FIX) et `sourceFormuleMetriqueSCOR(code)` (texte de preuve). **Ces deux
feuilles sont donc automatiquement cohérentes entre elles et avec le PI
par construction** — aucun risque de divergence introduit par ce bloc, et
c'est exactement pourquoi `calculerPIGlobal()` n'a pas besoin d'être
touchée pour corriger l'alignement.

Seule `catalogueMetriquesAHPRows()` (feuille séparée, catalogue des ~139
métriques SCOR officielles) appelle `valeurRuntimeMetriqueSCOR()`/
`uniteMetriqueSCOR()`/`sourceFormuleMetriqueSCOR()`/`statutMetriqueSCOR()`
indépendamment — c'est un audit de couverture SCOR générale (que peut-on
calculer pour CHAQUE code officiel), pas le pipeline live du PI ; les
codes legacy `AG.1.1`/`AM.3.9` y restent légitimement visibles comme codes
SCOR officiels, séparément des codes `PROXY.*` réellement actifs dans le
PI (voir point 8 ci-dessous).

### 1. `tauxCommandesLivreesCloses()` — corrigée, plus dégénérée

Ancienne implémentation : `closes++` et `livrees++` incrémentés pour
exactement les mêmes statuts → ratio toujours 1.0. Nouvelle sémantique,
conforme à la spécification donnée : mesure la **COMPLÉTUDE** (une
commande terminale a-t-elle été livrée en totalité, ce modèle ne simulant
aucune livraison partielle), **pas la ponctualité** (RL.2.2). Numérateur =
`SERVIE+EN_RETARD` ; dénominateur = `SERVIE+EN_RETARD+REFUSEE+BLOQUE_*`
(même population que `nombreCommandesClosesFiabilite()`, Bloc B.1,
réutilisée plutôt que redupliquée) ; `REAPPRO_*` exclus ; `NaN` si aucun
état terminal. **Non appelée depuis `calculerPIGlobal()`** (qui utilise
`verifierFillRate()` pour RL.2.2, décision B.2 déjà validée runtime,
inchangée) — cette correction n'affecte que les exports (RL.2.1, RL.3.33,
RL.3.35, RL.1.1 dans `valeurRuntimeMetriqueSCOR()`).

### 2. RL.2.1 vs RL.2.2 — sémantiques désormais distinctes et documentées

`sourceFormuleMetriqueSCOR("RL.2.1")` et `("RL.2.2")` documentent
explicitement la distinction complétude/ponctualité. RL.2.2 reste inchangé
(`verifierFillRate()`), confirmé comme "seule métrique RL réellement
pondérée dans le PI" dans son propre texte source — l'export reflète donc
exactement la source utilisée par le PI.

### 3. RL.3.33 / RL.3.35 — explicitement proxy, jamais présentées comme indépendantes

Textes mis à jour : "Proxy, aucune source de mesure indépendante
disponible... approximée par tauxCommandesLivreesCloses() (complétude)" —
jamais présentées comme des observations réelles indépendantes.

### 4/5. Proxies AG/AM — mappings corrigés (valeur, unité, source)

`valeurRuntimeMetriqueSCOR()` n'avait **aucune branche explicite** pour
`PROXY.AG.STABILITE_DEBIT`/`PROXY.AM.DISPONIBILITE_MACHINE` — confirmé par
lecture de code qu'un appel direct serait tombé au travers de tous les
`if` jusqu'au `return Double.NaN;` final. Ajoutées comme alias exacts des
codes legacy (`AG.1.1`→`coefficientAdaptabilite()`,
`AM.3.9`→`calculerDisponibiliteMachinesMoyenne()`, formules lues
directement dans le code, pas inventées). `uniteMetriqueSCOR()` avait le
même trou (aucun préfixe `AG.`/`AM.` ne matchant `PROXY.AG.`/`PROXY.AM.` →
repli sur `"-"` au lieu de `"ratio 0-1"`) — corrigé par une règle générique
`c.startsWith("PROXY.")` couvrant aussi `PROXY.AG.SYSTEM_UTILIZATION`
(même bug préexistant, corrigé au passage pour cohérence). Sources
détaillées ajoutées dans `sourceFormuleMetriqueSCOR()`, formules
reproduites exactement depuis le code des deux helpers, préfixe PROXY
conservé partout.

### 5bis. AG.3.32 — désalignement réel trouvé et corrigé

Audit demandé (point 5) a révélé une divergence réelle : `calculerPIGlobal()`
retient le max de 3 candidats (`board.totalTerminees`, `main.nbTermines`,
`board.kpiGlobal.count`) pour le débit, tandis que l'export
`valeurRuntimeMetriqueSCOR("AG.3.32")` n'en comparait que 2 (omettait
`board.kpiGlobal.count`). Corrigé pour utiliser exactement le même calcul
à 3 candidats.

### 6. AM.2.2 — source export alignée sur la vraie équation (B.2-FIX)

`sourceFormuleMetriqueSCOR("AM.2.2")` ne décrit plus une somme générique
de postes `STOCKAGE` (n'existe plus depuis B.2-FIX) : texte mis à jour sur
`stockProduitFiniDisponibleTotal() / débit journalier observé`, mention
explicite mono/multi-produit-safe. La valeur elle-même
(`valeurRuntimeMetriqueSCOR("AM.2.2")` → `calculerInventoryDaysOfSupply()`)
était déjà correcte (aucun changement de code nécessaire, seule la
documentation était obsolète).

### 7. Codes processus (`codesProcessusPourMetriqueSCOR()`) — non modifiée

Audité : les codes `PROXY.*` tombent déjà dans le repli `return "";`
(aucun rattachement processus), ce qui est le comportement correct et
sûr — un proxy système n'est pas rattaché à une étape SCOR précise, et
cette chaîne vide ne fait jamais dévier `valeurRuntimeMetriqueSCOR()` vers
le fallback générique `avgCycleTimeCodes(codes)` puisque les codes PROXY
ont désormais leurs propres branches explicites (point 4/5). Aucune
modification nécessaire.

### 8. Anciens codes legacy AG.1.1/AM.3.9 — jamais actifs dans le PI, clarifiés

Audité tous leurs usages (`valeurRuntimeMetriqueSCOR()`,
`sourceFormuleMetriqueSCOR()`, `initialiserProfilsNormalisationDefaut()`,
`codesProcessusPourMetriqueSCOR()`) : confirmé qu'aucun n'est utilisé par
`calculerPIGlobal()` depuis le Bloc B.2 (qui n'utilise que les codes
`PROXY.*`). Conservés explicitement comme **codes SCOR officiels legacy**
pour le catalogue des ~139 métriques et la compatibilité des profils de
normalisation historiques, avec un préfixe `[CODE LEGACY, non actif dans
le PI depuis le Bloc B.2 -- voir PROXY.*]` ajouté dans
`sourceFormuleMetriqueSCOR()` pour lever toute ambiguïté SCOR
normatif/PROXY/LEGACY.

### 9/10. Pipeline SCOR vers PI / Traçabilité performance

Confirmées cohérentes entre elles par construction (audit préalable
ci-dessus, source commune `strategic.detailN3`). Les corrections de ce
bloc (profils de normalisation B.2-FIX + `sourceFormuleMetriqueSCOR()`
B.3) améliorent leurs colonnes "Bottom→Perfect" et "Source / preuve" sans
changer leur mécanisme de lecture.

### 11. Dette mono — non touchée

Incohérence stock stratégique mono (log T=1740 stock=185 vs Dashboard
≈37) : toujours documentée, non corrigée, conformément à l'instruction
explicite. Reste une dette pour Bloc D / revue architecturale post-merge.

### Ce qui n'a PAS été modifié

`calculerPIGlobal()`, `prevoirDemande()`, `ajusterDebits()`,
`calculerInventoryDaysOfSupply()`, la logique warm-up, la logique REAPPRO,
le JSON/scénarios, la fixture A/B, ZENER, les Blocs A/M, `verifierFillRate()`
(réutilisée telle quelle), `codesProcessusPourMetriqueSCOR()` (auditée,
aucun changement nécessaire), les Blocs C/D/E.

### Tests statiques B.3 (raisonnement sur le code)

| Test | Vérification |
|---|---|
| B3-1 | `tauxCommandesLivreesCloses()` réécrite, ne peut plus retourner 1.0 systématiquement (numérateur ≠ dénominateur par construction dès qu'un REFUSEE/BLOQUE_* existe) |
| B3-2 | RL.2.1 (complétude) et RL.2.2 (ponctualité) ont des formules et des textes source distincts |
| B3-3 | RL.2.2 export = `verifierFillRate()`, identique à la source utilisée par `calculerPIGlobal()` (non modifiée) |
| B3-4 | RL.3.33/RL.3.35 explicitement qualifiées "Proxy, aucune source de mesure indépendante disponible" |
| B3-5 | `PROXY.AG.STABILITE_DEBIT` : branches ajoutées dans `valeurRuntimeMetriqueSCOR()`/`uniteMetriqueSCOR()`/`sourceFormuleMetriqueSCOR()`, formule reproduite exactement (`coefficientAdaptabilite()`) |
| B3-6 | `PROXY.AM.DISPONIBILITE_MACHINE` : idem (`calculerDisponibiliteMachinesMoyenne()`) |
| B3-7 | `sourceFormuleMetriqueSCOR("AM.2.2")` décrit désormais `stockProduitFiniDisponibleTotal() / débit journalier`, mono/multi-safe |
| B3-8 | Aucun code `PROXY.*` n'est présenté comme métrique SCOR normative (préfixe conservé partout, textes "Proxy explicite, hors référentiel SCOR normatif") |
| B3-9 | `AG.1.1`/`AM.3.9` marqués `[CODE LEGACY, non actif dans le PI depuis le Bloc B.2]`, jamais utilisés par `calculerPIGlobal()` (vérifié par grep) |
| B3-10 | Pipeline SCOR et Traçabilité performance confirmées cohérentes par construction (source commune `detailN3`, audit préalable) |

### Validations statiques

- XML bien formé : OK
- IDs AnyLogic uniques : 1680/1680 (inchangé — uniquement des corps de
  `<Function>` existantes réécrits, aucun nouvel élément XML)
- `git diff --check` : aucune erreur (même bruit `<EmbeddedIcon>`
  pré-existant reverté avant commit, motif déjà documenté dans les blocs
  précédents)
- Grep DataCo : 6 occurrences, toutes pré-existantes (inchangé depuis B.2)
- JSON/scénarios inchangés (fixture A/B, ZENER)
- Blocs A/M inchangés (vérifié par grep des noms de fonctions)
- B.2 inchangé (`calculerPIGlobal()`, `prevoirDemande()`, `ajusterDebits()`,
  `calculerInventoryDaysOfSupply()` non modifiées — seuls les 4 exports +
  `tauxCommandesLivreesCloses()` touchés)
- Blocs C/D/E non commencés

**Commit** : `feat(generic): align SCOR exports with PI semantics`

**PR reste DRAFT. Aucun merge vers `main`.**

## VALIDATION UTILISATEUR RUNTIME — B.3 (2026-09-18)

Run export réel comparé ligne à ligne entre Pipeline SCOR vers PI et
Traçabilité performance : **cohérents sur code/valeur/unité/Bottom→Perfect/
score/grades/poids/contribution/source**. RL.2.1 (complétude, poids 0),
RL.2.2 (ponctualité, poids 1 local), RL.3.33/RL.3.35 (proxy explicite),
`PROXY.AG.STABILITE_DEBIT` (0.967, profil 0→1, score 9.671),
`PROXY.AM.DISPONIBILITE_MACHINE` (0.941, profil 0→1, score 9.412), AM.2.2
(0.061 jour, source correcte) — tous confirmés corrects. **Pipeline ↔
Traçabilité = VALIDÉ.**

Un bug runtime confirmé sur la feuille séparée "Catalogue SCOR (139)" :
`CO.1.1` y affichait 0.476 (score≈5.240) contre 0.048 (score≈9.524) sur
Pipeline SCOR/PI live pour le même instant — facteur ×10, signature du
biais nbTermines déjà corrigé ailleurs.

## Bloc B.3-FIX FINAL — alignement catalogue / PI live (2026-09-19)

Correctif strictement scopé à 3 éléments, comme demandé :
`valeurRuntimeMetriqueSCOR("CO.1.1")`, `sourceFormuleMetriqueSCOR()` pour
`RS.2.1/2.2/2.3/2.5` et `AG.3.32`.

### 1. `CO.1.1` — Catalogue utilisait encore `nbTermines`

**Confirmé par lecture de code, caractère par caractère** :
`valeurRuntimeMetriqueSCOR("CO.1.1")` calculait `ca = chiffreAffaireParUnite * nbTermines`
(compteur hybride production/commande), alors que `calculerPIGlobal()`
utilise `unitesLivreesClients()` depuis le Bloc B.2. Le texte source
(`sourceFormuleMetriqueSCOR("CO.1.1")`, écrit en B.3) affirmait déjà à tort
la parité — seule la VALEUR n'avait pas suivi. Corrigé pour utiliser
exactement `unitesLivreesClients()` (REAPPRO_ exclus), mêmes gardes
(`chiffreAffaireParUnite<=0 || unitesFacturables<=0` → `NaN`) et même clamp
(`Math.min(1.0, couts[2]/ca)`) que `calculerPIGlobal()`. Catalogue CO.1.1
doit désormais valoir ≈0.048 (== Pipeline) sur le run rapporté, plus 0.476.

### 2. Source RS.2.1/RS.2.2/RS.2.3/RS.2.5 — description obsolète depuis B.2

Sans branche explicite, ces 4 codes tombaient dans le repli générique
"Moyenne des temps de traitement des postes SCOR [...]"
(`codesProcessusPourMetriqueSCOR()`) — une description exacte AVANT le
Bloc B.2, devenue fausse depuis : le temps de cycle macro n'est plus une
moyenne de traitement seul, ni agrégé sur toute la chaîne, mais
`(sumCycleTime + sumWaitTime) / unités entrées`, périmètre
ENTREPRISE_FOCALE, borne via `dureeTraitementNominale()` pondérée par les
passages réels et `majBorneCycleMacro()` (décroissance lente/hyperbolique).
4 branches explicites ajoutées, résolues avant le repli générique (même
principe que le commentaire C14.2.1 déjà présent pour RL). **Uniquement la
description de preuve modifiée — aucune valeur runtime ni
`calculerPIGlobal()` touchés.**

### 3. Source AG.3.32 — formule incomplète

L'ancien texte ("entités terminées × 3600 / temps") ne mentionnait pas les
3 candidats réellement comparés. Mis à jour :
`max(board.totalTerminees, main.nbTermines, board.kpiGlobal.count) × 3600 / time()`
— formule exacte lue dans le code des deux fonctions (déjà alignées entre
elles depuis le B.3-FIX précédent), désormais auto-explicative dans
l'export.

### Ce qui n'a PAS été modifié

`calculerPIGlobal()`, `prevoirDemande()`, `ajusterDebits()`,
`calculerInventoryDaysOfSupply()`, le warm-up, les valeurs RL runtime, les
proxies (valeurs), les Blocs A/M, le JSON/scénarios, la fixture A/B,
ZENER, les Blocs C/D/E. Diff purement scopé aux 3 éléments demandés (26
insertions / 4 suppressions, vérifié par `git diff`).

### Validations statiques

- XML bien formé : OK
- IDs AnyLogic uniques : 1680/1680 (inchangé)
- `git diff --check` : aucune erreur (aucun bruit `<EmbeddedIcon>`
  cette fois)
- Grep DataCo : 6 occurrences, toutes pré-existantes (inchangé)
- JSON/scénarios inchangés
- Blocs A/M/B.2 inchangés (vérifié : les 4 lignes supprimées sont
  exactement les 3 lignes de calcul `CO.1.1` erronées + 1 ligne de texte
  `AG.3.32` incomplet)
- Blocs C/D/E non commencés

**Commit** : `fix(generic): align SCOR catalogue with live PI`

**PR reste DRAFT. Aucun merge vers `main`.**

## VALIDATION UTILISATEUR RUNTIME — B.3-FIX (2026-09-19)

Run export comparé ligne à ligne : Pipeline SCOR vers PI ↔ Traçabilité
performance = **0 divergence sur 18 métriques communes** (valeur, unité,
Bottom→Perfect, score, grades fuzzy, poids, contribution, source).
**CO.1.1 aligné sur les 4 feuilles à 0.021** (Pipeline, Traçabilité,
Catalogue SCOR, Métriques SCOR calculables) — **B.3-FIX CO.1.1 VALIDÉ
runtime.** AG.3.32 et sources RS.2.x textuellement corrects. Aucune
erreur Excel.

## Bloc B.3-FIX2 — dernière incohérence valeurs RS.2.x du catalogue (2026-09-19)

### Bug confirmé

Même export, même instant : Pipeline/PI live donnait RS.2.1=5.000s,
RS.2.2=1103.464s, RS.2.3=1881.827s ; Catalogue SCOR donnait
RS.2.1=1.644s, RS.2.2=13.550s, RS.2.3=73.614s. Le texte source (déjà
corrigé au B.3-FIX précédent) décrivait la formule B.2
((sumCycleTime+sumWaitTime)/unités entrées, périmètre ENTREPRISE_FOCALE)
mais la **valeur** provenait encore de `avgCycleTimeMacro()` — l'ancien
calcul pré-B.2 (moyenne de temps de traitement seul, sur
`board.kpiParMacro`, toute la chaîne) — confirmé par lecture directe des 4
branches `valeurRuntimeMetriqueSCOR("RS.2.1"/"RS.2.2"/"RS.2.3"/"RS.2.5")`.

### Audit préalable (comme demandé)

- `catalogueMetriquesAHPRows()` et `metriquesSCORCalculablesRows()`
  appellent bien toutes les deux `valeurRuntimeMetriqueSCOR(code)` (une
  seule fonction à corriger pour les deux feuilles).
- **Ni l'une ni l'autre n'appelle `strategic.calculerPIGlobal()`** avant de
  lire — contrairement à `n3ToN1Rows()` (Pipeline) et
  `piTraceabilityRows()` (Traçabilité), qui le font explicitement en tête
  de fonction. Rien ne garantissait donc que `strategic.detailN3` soit à
  jour au moment de la génération de ces 2 feuilles.

### Solution retenue (celle privilégiée par la consigne)

Nouvelle fonction **read-only** `valeurRuntimePIDetail(String code)` (Main) :
force un calcul frais de `calculerPIGlobal()` (même principe déjà utilisé
par Pipeline/Traçabilité elles-mêmes), puis cherche dans
`strategic.detailN3` (RL/RS/AG/CO/AM) la `MetriqueN3` dont
`codeOfficielSCOR` correspond exactement au code demandé et retourne sa
`valeurBrute`. **Aucune reduplication de la formule de cycle macro B.2** —
une seule source de vérité numérique, celle effectivement utilisée par le
PI live. Les 4 branches `RS.2.1/RS.2.2/RS.2.3/RS.2.5` de
`valeurRuntimeMetriqueSCOR()` délèguent désormais à cette fonction.
`avgCycleTimeMacro()` n'est plus appelée par aucune de ces 4 branches
(fonction elle-même non supprimée, non modifiée, plus aucun appelant après
ce correctif).

**RS.2.5** : si Return n'est pas exécuté sur le run,
`calculerPIGlobal()` n'ajoute alors aucune `MetriqueN3` de code "RS.2.5" à
`detailN3` (gardée par `main.macroExecutee(sR)`) — `valeurRuntimePIDetail()`
ne trouve donc rien et retourne `NaN` automatiquement, sans cas particulier
à coder : "non calculé" reste "non calculé", jamais une valeur fabriquée.

### Ce qui n'a PAS été modifié

La formule mathématique B.2 elle-même (`calculerPIGlobal()`),
`prevoirDemande()`, `ajusterDebits()`, `CO.1.1`, RL, AG, AM, le warm-up,
les Blocs A/M, le JSON/scénarios, la fixture A/B, ZENER, les Blocs C/D/E.
Diff purement additif pour le nouveau helper + 4 lignes remplacées par un
seul bloc dans `valeurRuntimeMetriqueSCOR()` (53 insertions / 4
suppressions, vérifié par `git diff`).

### Tests statiques B.3-FIX2

| Test | Vérification |
|---|---|
| B3F2-1/2/3 | `valeurRuntimeMetriqueSCOR("RS.2.1"/"RS.2.2"/"RS.2.3")` délègue à `valeurRuntimePIDetail()`, qui lit `m.valeurBrute` depuis `detailN3` — même valeur que le PI live par construction |
| B3F2-4 | RS.2.5 non exécuté → aucune `MetriqueN3` "RS.2.5" dans `detailN3` → `NaN` automatique |
| B3F2-5 | `avgCycleTimeMacro(` n'apparaît plus dans aucune des 4 branches RS.2.x de `valeurRuntimeMetriqueSCOR()` (vérifié par grep) |
| B3F2-6 | `n3ToN1Rows()`/`piTraceabilityRows()` non modifiées |
| B3F2-7 | Branche `CO.1.1` non touchée par ce commit |

### Validations statiques

- XML bien formé : OK
- IDs AnyLogic uniques : 1680/1680 (inchangé)
- `git diff --check` : aucune erreur
- Grep DataCo : 6 occurrences, toutes pré-existantes (inchangé)
- JSON/scénarios inchangés
- Diff scopé exactement aux 4 lignes RS.2.x remplacées + le nouveau helper
  read-only (vérifié : aucune ligne de `calculerPIGlobal()`/`prevoirDemande()`/
  `ajusterDebits()`/`CO.1.1` supprimée)
- Blocs C/D/E non commencés

**Commit** : `fix(generic): align RS catalogue values with live PI`

**PR reste DRAFT. Aucun merge vers `main`.**

## CLÔTURE OFFICIELLE DU BLOC B — VALIDATION RUNTIME FINALE B.3-FIX2 (2026-09-19)

Dernier export utilisateur vérifié. Alignement confirmé sur les 4 surfaces
(Pipeline, Traçabilité, Catalogue SCOR, Métriques SCOR calculables) :

| Métrique | Pipeline | Traçabilité | Catalogue | Calculables |
|---|---|---|---|---|
| RS.2.1 | 5.000 | 5.000 | 5.000 | 5.000 |
| RS.2.2 | 996.721 | 996.721 | 996.721 | 996.721 |
| RS.2.3 | 4794.008 | 4794.008 | 4794.008 | 4794.008 |
| CO.1.1 | 0.047 | 0.047 | 0.047 | 0.047 |

**Catalogue RS.2.x == PI live. CO.1.1 reste parfaitement aligné.**

RS.2.5 : Return non exécuté sur ce run → Catalogue affiche "Non calculée",
absente de Métriques SCOR calculables — aucune valeur artificielle,
comportement attendu **VALIDÉ**.

**Pipeline ↔ Traçabilité** : 18 métriques communes comparées, 0 divergence
sur valeur brute / unité / Bottom→Perfect / score / grades fuzzy / poids /
contribution / source — **VALIDÉ runtime**.

**Sources/formules validées** : RS.2.1/2.2/2.3 (cycle macro
(traitement+attente)/unités, périmètre ENTREPRISE_FOCALE, nominal via
`dureeTraitementNominale()` pondéré + `majBorneCycleMacro()` + décroissance
lente), AG.3.32 (max des 3 candidats × 3600/time()), CO.1.1
(`unitesLivreesClients()`, REAPPRO exclus), AM.2.2
(`stockProduitFiniDisponibleTotal()` / débit journalier).

**Scan classeur final** : `#REF!`=0, `#DIV/0!`=0, `#VALUE!`=0, `#NAME?`=0,
`#N/A`=0.

### Statut final

- **B.1 = TERMINÉ / VALIDÉ / FIGÉ**
- **B.2 = TERMINÉ / VALIDÉ / FIGÉ**
- **B.2-FIX = TERMINÉ / VALIDÉ / FIGÉ**
- **B.3 = TERMINÉ / VALIDÉ / FIGÉ**
- **B.3-FIX = TERMINÉ / VALIDÉ / FIGÉ**
- **B.3-FIX2 = TERMINÉ / VALIDÉ / FIGÉ**

## **BLOC B — PI / SCOR = TERMINÉ / VALIDÉ / FIGÉ**

Ne plus modifier les mécanismes du Bloc B (`calculerPIGlobal()`,
`prevoirDemande()`, `ajusterDebits()`, `calculerInventoryDaysOfSupply()`,
`majBorneCycleMacro()`, `NormalizationProfile.decroissanceLente`,
`tauxCommandesLivreesCloses()`, `valeurRuntimePIDetail()`, les mappings
d'export SCOR) sauf bug runtime réellement démontré.

**Garanties apportées par le Bloc B** :
- demande cliente (`prevoirDemande()`) découplée de la production —
  élimine la boucle de rétroaction production→prévision→stock
  cible→production ;
- lecture stock multi-produit correcte dans `ajusterDebits()`
  (`stockFiniDisponiblePourScenario()`, jamais l'agrégat sommé N fois) ;
- périmètre du PI restreint à l'entreprise focale
  (`ActeurSC.ENTREPRISE_FOCALE`), plus d'agrégation aveugle de toute la
  chaîne étendue ;
- poids effectifs (absence de donnée ≠ score nul) et warm-up (PI maintenu
  à la cible tant que le périmètre de mesure n'est pas complet) ;
- RL.2.2 (ponctualité) réellement pondérée dans le PI ; RL.2.1/3.33/3.35
  (complétude/proxies) informatives, jamais confondues ;
- RS fondée sur temps de traitement + temps d'attente cumulés, pas la
  seule moyenne de traitement ;
- proxies AG/AM (`PROXY.AG.STABILITE_DEBIT`, `PROXY.AG.SYSTEM_UTILIZATION`,
  `PROXY.AM.DISPONIBILITE_MACHINE`) explicitement étiquetés, jamais
  présentés comme des métriques SCOR normatives ;
- CO fondé sur les unités réellement livrées aux clients
  (`unitesLivreesClients()`), pas un compteur hybride production/commande ;
- catalogue SCOR et exports (Pipeline, Traçabilité, Catalogue, Métriques
  calculables) alignés avec le PI live — une seule source de vérité
  numérique par métrique.

**Dette connue, non résolue, conservée pour référence future** :
incohérence du stock stratégique loggé en mode MONO dans certains logs
(stock loggé ≠ Finished Stock Dashboard, ex. log T=1740 stock=185 vs
Dashboard ≈37) — logique legacy mono, invariant "mono = comportement
préservé" du Bloc B respecté à dessein, à auditer dans le Bloc D ou une
revue architecturale post-merge.

**PR reste DRAFT. Aucun merge vers `main`. Bloc C non commencé.**

- [x] Bloc B — PI / SCOR : **TERMINÉ / VALIDÉ / FIGÉ**
- [ ] Dette documentée : incohérence stock stratégique mono (log T=1740 stock=185 vs Dashboard ≈37) — audit architectural futur, hors Bloc B

## Bloc C — retards

### C.1 — Audit sémantique des retards et de l'engagement client (2026-09-19)

**Bloc d'audit uniquement.** Aucune ligne de `.alp` modifiée, aucune variable
ni fonction ajoutée, `evaluerRetardsCommandesOuvertes()` non implémentée.
Méthode : lecture directe et grep exhaustif de `model/SCONTO_SVU_GENERIC_MASTER.alp`
(HEAD `ba74573`), jamais de suppositions.

#### 1. Inventaire

| Variable/fonction | Emplacement | Lecture/Écriture | Sémantique actuelle |
|---|---|---|---|
| `CommandeAgent.retardConstate` | **Absent du master** (3 mentions, toutes des commentaires documentant son absence, écrits lors des Blocs A.2/A.4/B.1) | — | N'existe pas. Champ du mécanisme de retard continu côté collègue, jamais porté |
| `modeEngagementClient` | **Absent du master** (0 occurrence) | — | N'existe pas encore, ni comme variable ni comme concept nommé |
| `dureeClientAccumulee` | **Absent du master** (0 occurrence) | — | N'existe pas sous ce nom exact — le concept le plus proche est `CommandeAgent.dureeReelleAccumulee` (voir plus bas) |
| `CommandeAgent.leadTimeClientReelSec` | `Variable` sur `CommandeAgent` ; écrit dans `actualiserRegistreTempsCommande()` (L2424-2433) ; lu dans `finaliserReceptionClientDirecte()` (L5751), `enregistrerFinCommandeGlobale()` (L6130), export ABox (L9437) | Écriture unique (1 fonction), lectures multiples | **LEAD TIME**, pas un retard : `dureeTraitementClientReelleSec + dureeAttenteStockReelleSec` (ou repli sur les paramètres `leadTimeRepli`/`waitTimeRepli` si l'accumulation explicite est absente) |
| `CommandeAgent.attenteStockOuverte` | `Variable` sur `CommandeAgent` ; écrit dans `ouvrirAttenteStockCommande()` (true, L2358-2359) et `finaliserDependanceReappro()` (false, L2414) ; lu dans `lierReapproAuxCommandesClientesEnAttente()` (L2400) | Écriture/lecture réparties sur 3 fonctions | **ATTENTE OPÉRATIONNELLE** (stock insuffisant en attente de réapprovisionnement), jamais un retard en soi — purement descriptif d'un état transitoire |
| `CommandeAgent.tDebutAttenteStock` / `tFinAttenteStock` | `Variable`s sur `CommandeAgent` ; écrits dans les 2 mêmes fonctions que `attenteStockOuverte` | idem | Horodatage de l'épisode d'attente stock (début/fin), `-1` = jamais commencé/jamais fini |
| `CommandeAgent.dureeAttenteStockReelleSec` | `Variable` sur `CommandeAgent` ; incrémenté dans `finaliserDependanceReappro()` (L2413) ; lu dans `actualiserRegistreTempsCommande()` (L2430), `enregistrerFinCommandeGlobale()` (L6131-6132) | Écriture cumulative (`+=`), potentiellement plusieurs fois si plusieurs REAPPRO couvrent la même commande | Durée réelle **cumulée** d'attente de stock, imputée depuis le(s) REAPPRO lié(s) — alimente le lead time, jamais un retard |
| `CommandeAgent.dureeReapproImputeeReelleSec` | `Variable` sur `CommandeAgent` ; incrémenté au même site que `dureeAttenteStockReelleSec` (L2412) ; lu uniquement par l'export ABox (`run:replenishmentImputedTimeSeconds`, L9438) | Écriture cumulative, lecture export uniquement | Même valeur numérique que `dureeAttenteStockReelleSec` à l'instant de l'écriture, mais un champ **distinct**, dédié à la traçabilité ontologique (provenance), pas au calcul runtime du lead time |
| `CommandeAgent.dureeReelleAccumulee` | `Variable` sur `CommandeAgent` ; incrémenté à 4 sites : `finaliserDependanceReappro()`-like L2531 (retry stock), L12856 (fin de production Make, calcul `time()-tDebutProduction`), L12913 (segment Deliver post-production), L13025 (segment Make) | Écriture cumulative sur plusieurs segments (Make + Deliver), jamais réinitialisé en cours de commande | Durée réelle **cumulée** de traitement physique tous segments confondus (Make + Deliver), volontairement additive (cf. commentaire C14.46 : sans le segment Deliver ajouté explicitement pour les commandes MTO/Cas2-3, leur lead time réel était artificiellement plus court que MTS) |
| `CommandeAgent.dureeTraitementClientReelleSec` | `Variable` sur `CommandeAgent` ; écrit une seule fois dans `actualiserRegistreTempsCommande()` (L2431, depuis `dureeReelleAccumulee` ou repli) | Écriture unique par appel, idempotente | Miroir de `dureeReelleAccumulee` au moment de la clôture, utilisé pour construire `leadTimeClientReelSec` |
| `CommandeAgent.tPromise` | `Variable` sur `CommandeAgent` ; écrit à la création de la commande (`genererCommande()`, L13183 et L13206 — 2 écritures successives redondantes mais harmless, `modeSCORActif()` ne change pas entre les deux) et à la création d'un REAPPRO (L2990, `delaiPromessePourMode("MTS")` fixe) | Écriture à la création uniquement, jamais réévaluée en cours de vie | **Seule référence d'engagement existant aujourd'hui** — voir §3 |
| `CommandeAgent.statut` | `Variable` sur `CommandeAgent`, vocabulaire complet confirmé par grep exhaustif (voir §6) | Écrit à de nombreux sites (création, avancement, clôture) | État métier de la commande ; `EN_RETARD` est un état **terminal**, jamais transitoire |
| `commandesRetardeesCount()` | Fonction Main (L7375) | Lecture seule sur `commandes` | Compte les commandes **déjà closes** en `EN_RETARD` (filtré `estCommandeClient()`) — alimente la colonne Dashboard "Delayed Orders (nb)" (Bloc A.4) |
| `nombreCommandesClosesFiabilite()` / `tauxCommandesLivreesCloses()` | Fonctions Main (Bloc B.1/B.3-FIX2) | Lecture seule sur `commandes` | Déjà établissent le prédicat "commande terminale" fiable (`SERVIE`/`EN_RETARD`/`REFUSEE`/`BLOQUE_*`), directement réutilisable pour le futur prédicat "commande ouverte" (négation de ce prédicat) |
| `verifierFillRate()` | Fonction Main (Bloc "ETAPE 3.1") | Lecture seule | Ratio de ponctualité (`SERVIE`/(`SERVIE`+`EN_RETARD`)) parmi les commandes clientes closes — seule métrique RL réellement pondérée dans le PI depuis le Bloc B.2 |
| `delaiPromessePourMode(String mode)` | Fonction Main (L8399) | Lecture seule, retourne une constante | `ETO`→3600s, `MTO`→1800s, sinon (`MTS`)→300s. **Constantes codées en dur**, aucune source JSON |
| `modeSCORActif()` | Fonction Main (L8395) | Lecture seule | `isETO`/`isMTO`/`isMTS` — un **mode de simulation global** (1 seul mode actif pour tout le run, configuré via `appliquerModeSimulationSCOR()`), pas une propriété par commande ni par client |

#### 2. Chaîne temporelle réelle (confirmée par lecture de code)

```
genererCommande() [L13178-13206]
  cmd.tCreation  = time()
  cmd.typeCommande = modeSCORActif()           <- mode de RUN global (MTS/MTO/ETO), pas un choix client
  cmd.tPromise   = time() + delaiPromessePourMode(cmd.typeCommande)   <- SEULE reference d'engagement
  cmd.statut     = "EN_ATTENTE"
        |
        v
  analyserStockCommandeOrchestree() : MTS servi depuis stock (immediat)
        OU
  attente stock insuffisant -> ouvrirAttenteStockCommande()
    cmd.attenteStockOuverte = true ; cmd.tDebutAttenteStock = time()
        |
        v  (si REAPPRO necessaire, Bloc M.3)
  finaliserDependanceReappro() a la cloture du REAPPRO lie
    cmd.dureeAttenteStockReelleSec += dureeReappro
    cmd.dureeReapproImputeeReelleSec += dureeReappro  (traçabilite ABox, meme valeur)
    cmd.attenteStockOuverte = false ; cmd.tFinAttenteStock = time()
        |
        v
  Production Make (si applicable) : cmd.dureeReelleAccumulee += ... (plusieurs segments)
        |
        v
  Livraison (finaliserReceptionClientDirecte() OU chemin post-production L12898)
    actualiserRegistreTempsCommande(cmd, ...)
      cmd.dureeTraitementClientReelleSec = traitement (depuis dureeReelleAccumulee)
      cmd.leadTimeClientReelSec = traitement + attente          <- LEAD TIME, jamais compare a tPromise ici
    cmd.statut = (time() <= cmd.tPromise) ? "SERVIE" : "EN_RETARD"   <- SEULE evaluation d'engagement, UNE FOIS, a la cloture
        |
        v
  cloturerOrderDepuisCommande() -> Order.cloturer("LIVREE" | "LIVREE_EN_RETARD", ...)  [ABox/VSM]
  enregistrerFinCommandeGlobale() -> board.notifierFin(leadTimeClientReelSec, ...)      [PI/SCOR RS]
```

**Constat central** : `tPromise` n'est comparé à `time()` qu'à **exactement 2
endroits** dans tout le master (`finaliserReceptionClientDirecte()` L5752 et
le chemin post-production L12898), tous deux **au moment de la clôture**.
Aucun timer, événement périodique ou fonction n'évalue jamais une commande
encore `EN_COURS`/`EN_ATTENTE`/`EN_LIVRAISON`/etc. par rapport à son
engagement pendant qu'elle est encore ouverte. Une commande peut donc
dépasser `tPromise` de plusieurs heures sans que rien ne le signale tant
qu'elle n'a pas encore été livrée.

#### 3. Source actuelle de l'engagement client (avec preuves)

L'engagement est **exclusivement** `cmd.tPromise = time() + delaiPromessePourMode(cmd.typeCommande)` :
- `delaiPromessePourMode()` (L8399-8402) retourne une **constante codée en
  dur** selon le mode : ETO=3600s, MTO=1800s, MTS=300s (repli par défaut).
- `cmd.typeCommande` provient de `modeSCORActif()` (L8395-8397), qui lit 3
  booléens **globaux au run** (`isMTS`/`isMTO`/`isETO`, positionnés une
  seule fois via `appliquerModeSimulationSCOR()` au démarrage/à la
  configuration) — **jamais** une propriété par commande, par client ou par
  scénario.
- Recherche exhaustive dans les 3 scénarios JSON fournis (ZENER, vélo
  urbain, automobile GX5) : **aucun champ** `delai*Client`, `promis*`,
  `engagement*`, `SLA*` ou `deadline*` lié à une livraison client
  n'existe. Les seuls champs "délai" trouvés sont `delaiPaiementJours`
  (conditions de paiement, hors sujet) et `delaiObtentionHeures`
  (délai fournisseur Source, pas un engagement client).

**Conclusion** : il n'existe aujourd'hui **aucune vraie source d'engagement
contractuel, par client ou par commande** — seulement une constante par
mode de production, appliquée uniformément à toutes les commandes d'un
même run.

#### 4. Sémantique actuelle des 5 éléments demandés

- **`retardConstate`** : n'existe pas. Concept vide dans ce master.
- **`modeEngagementClient`** : n'existe pas. Le mode de production
  (MTS/MTO/ETO) sert aujourd'hui implicitement de proxy à la durée
  d'engagement, mais rien ne nomme ni ne documente cela comme un
  "mode d'engagement" — c'est une conflation implicite entre mode
  industriel et promesse client, jamais explicitée dans le code.
- **`dureeClientAccumulee`** : n'existe pas sous ce nom. Le concept le
  plus proche, `dureeReelleAccumulee`, mesure le temps de traitement
  physique cumulé (Make+Deliver), pas une durée "client" au sens large
  (n'inclut pas l'attente stock, qui est un champ séparé).
- **`leadTimeClientReelSec`** : LEAD TIME total réel (traitement + attente
  stock), alimente RS (Responsiveness) via `enregistrerFinCommandeGlobale()`
  → `board.notifierFin()` → `board.kpiGlobal` → `orderFulfillmentLeadTimeGlobal()`/
  `tempsAttenteGlobalCoherent()` → `calculerPIGlobal()` (Bloc B.2). **Jamais
  comparé à `tPromise`** — orthogonal à la notion de retard.
- **`attenteStockOuverte`** : ATTENTE OPÉRATIONNELLE ponctuelle (stock
  insuffisant), état transitoire, jamais un retard en soi, contribue
  seulement à `dureeAttenteStockReelleSec` (donc au lead time).

#### 5. Incohérences détectées (non corrigées, documentées uniquement)

1. **Conflation mode industriel / engagement client** : `delaiPromessePourMode()`
   fait comme si "MTO" ou "ETO" impliquait mécaniquement un délai promis
   plus long — hypothèse implicite jamais justifiée ni configurable.
2. **Aucune détection de retard sur commande ouverte** : le seul signal de
   retard (`EN_RETARD`) n'apparaît qu'à la clôture ; une commande très en
   retard mais encore ouverte est indiscernable d'une commande à l'heure
   dans tous les tableaux de bord actuels (`commandesRetardeesCount()`,
   `verifierFillRate()`, `tauxCommandesLivreesCloses()` — tous ne comptent
   que les commandes **déjà closes**).
3. **Double écriture `dureeAttenteStockReelleSec`/`dureeReapproImputeeReelleSec`** :
   même valeur, deux champs, deux consommateurs différents (runtime vs
   ABox) — pas un bug, mais une duplication qui mériterait d'être
   clarifiée/documentée dans le code lui-même si le Bloc C réutilise l'un
   des deux comme brique du calcul de retard.
4. **Double écriture de `tPromise`** à la création (L13183 puis L13206,
   `genererCommande()`) — résultat identique (`modeSCORActif()` ne change
   pas entre les deux lignes), donc sans conséquence observable, mais une
   redondance de code pré-existante.

#### 6. Risques de double comptage

- `dureeReelleAccumulee` est incrémenté à 4 sites distincts (retry stock,
  fin Make, segment Deliver post-production, segment Make) : **additif par
  construction** (chaque segment représente une portion de temps physique
  réellement écoulée, jamais le même intervalle compté deux fois) — **aucun
  double comptage détecté**, cohérent avec le commentaire C14.9 déjà présent
  dans le code ("DOUBLE COMPTAGE CORRIGE" pour `nbMTS`/`sumLeadTimeMTS`,
  résolu en amont de ce merge).
- `dureeAttenteStockReelleSec` : protégé par `client.ordresReapproImputes.add(reappro.idCommande)`
  (un `Set`), qui empêche d'imputer deux fois la même durée depuis le même
  REAPPRO. Une commande couverte par **plusieurs** REAPPRO successifs
  accumule légitimement leurs durées respectives — comportement voulu, pas
  un bug.
- Aucun risque de double comptage identifié pour un futur mécanisme de
  retard continu, **à condition** qu'il lise l'état actuel (`time() - tPromise`)
  sans additionner un compteur à chaque cycle d'évaluation (piège classique
  d'un futur `evaluerRetardsCommandesOuvertes()` mal conçu — noté pour le
  sous-bloc d'implémentation, pas pour C.1).

#### 7. Relation avec SCOR / PI / VSM

- **RL (Reliability)** : `verifierFillRate()` (ponctualité, pondérée dans
  le PI) et `tauxCommandesLivreesCloses()` (complétude, informative,
  Bloc B.3-FIX2) lisent tous deux `cmd.statut` — donc indirectement
  `EN_RETARD`, donc indirectement `tPromise`. **Aucun** des deux ne
  considère les commandes encore ouvertes.
- **RS (Responsiveness)** : alimentée par `leadTimeClientReelSec` (lead
  time), **jamais** par un retard. Un retard et un lead time long sont
  deux signaux différents aujourd'hui : une commande peut avoir un lead
  time élevé sans jamais dépasser `tPromise` (si `tPromise` est lui-même
  large, ex. ETO=3600s), et inversement un `tPromise` très serré (MTS=300s)
  peut être dépassé même avec un lead time réel modeste.
- **VSM/ABox** : `cloturerOrderDepuisCommande()` exporte `"LIVREE"` ou
  `"LIVREE_EN_RETARD"` comme statut d'`Order` ontologique — reflet direct
  et fidèle de `cmd.statut`, aucune logique supplémentaire.
- **Aucune métrique actuelle ne mesure un retard EN COURS** (ampleur du
  dépassement pour une commande encore ouverte) — c'est précisément
  l'écart que le Bloc C est censé combler.

#### 8. Proposition de source de vérité pour le futur Bloc C (SANS implémentation)

Non appliqué dans ce commit — proposition documentée pour discussion avant
tout sous-bloc d'implémentation :
- **Engagement** : `cmd.tPromise` reste la référence unique et déjà
  existante — pas besoin d'un nouveau champ pour "quand la commande est
  due", seulement d'une manière de le **qualifier** (`modeEngagementClient`
  décrirait alors la MÉTHODE — "constante par mode de production" —, pas
  une nouvelle date).
- **Retard courant** (commande encore ouverte) :
  `retardCourantSec = Math.max(0.0, time() - cmd.tPromise)`, calculable à
  tout instant sans nouvel état cumulatif, en lisant uniquement `tPromise`
  et `time()` — pas de risque de double comptage puisque rien n'est
  accumulé.
- **Retard constaté** (à la clôture, si `Bloc C` veut le figer) :
  `retardConstateSec = Math.max(0.0, tInstantCloture - cmd.tPromise)`,
  calculé une seule fois au moment où `cmd.statut` devient terminal —
  cohérent avec le mécanisme de clôture déjà existant (2 sites identifiés
  en §2).
- **Prédicat "commande ouverte"** : négation exacte du prédicat déjà
  utilisé par `nombreCommandesClosesFiabilite()`/`tauxCommandesLivreesCloses()`
  (Bloc B, déjà validé runtime) — c'est-à-dire toute commande cliente
  (`estCommandeClient()`) dont le statut n'est PAS dans
  `{SERVIE, EN_RETARD, REFUSEE, BLOQUE_CONFIG, BLOQUE_MATIERE, BLOQUE_NOMENCLATURE}`.
  Réutiliser ce prédicat déjà éprouvé plutôt que d'en inventer un nouveau.

#### 9. Éléments à modifier dans les sous-blocs suivants (liste minimale, non exhaustive)

- Ajouter `CommandeAgent.retardConstate` (ou équivalent) — nouveau champ.
- Ajouter `modeEngagementClient` — nouvelle variable décrivant la méthode
  de calcul de l'engagement (pas une nouvelle date codée en dur).
- Implémenter `evaluerRetardsCommandesOuvertes()` — nouvelle fonction,
  utilisant le prédicat "commande ouverte" du §8, appelée depuis un timer/
  événement périodique (à définir).
- Décider si `retardCourantSec` doit être exposé dans une nouvelle
  métrique/colonne Dashboard, et si RL doit évoluer pour intégrer les
  commandes ouvertes en retard (actuellement invisibles).
- Ne pas toucher `tPromise`/`delaiPromessePourMode()`/`modeSCORActif()`
  sans décision explicite sur le point d'incohérence n°1 (§5).

#### 10. Verdict

**C.1 = AUDIT COMPLET.**

### Statut Bloc C

- [x] **C.1 — Audit sémantique retards / engagement client : TERMINÉ / AUDIT VALIDÉ**
- [ ] C.2+ — non commencés
- [ ] Détection continue
- [ ] Engagement configurable
- [ ] Export/PI cohérent
- [ ] Build + run utilisateur

**BLOC C = EN COURS.** Aucune modification du `.alp` dans ce commit (audit
uniquement). Le `.alp` contenait déjà, avant ce tour, un bruit de
sauvegarde automatique AnyLogic pré-existant (`<EmbeddedIcon>`) —
volontairement laissé non indexé, non commité, conformément à l'instruction.

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
