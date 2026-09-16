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
- [x] Diagnostic commandes bloquées — **PORTÉ** (2026-09-16, commit `0363b6b`, Build/run nominal utilisateur OK ; test fonctionnel forcé [DIAG-BLOQUEE] À TESTER ULTÉRIEUREMENT)
- [x] Stock matière détaillé — **PORTÉ** (2026-09-16, commit `d52d431`, Build AnyLogic utilisateur OK ; validation fonctionnelle différée au Bloc A.4, où la fonction sera consommée pour la première fois)
- [ ] Historique Dashboard / Excel
- [ ] États holoniques cohérents
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

**Commit administratif** : voir SHA en tête de la prochaine section (message
`chore(anylogic): track model runtime resources`).

## Bloc M — Fondation multi-produit Generic (2026-09-16, PLANIFIÉ — NON COMMENCÉ)

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

**Statut** : PLANIFIÉ. Aucune implémentation commencée. Audit détaillé de la fondation
existante et de la référence donneuse à réaliser en ouverture du bloc.

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
