# Structure interne du modèle AnyLogic (`SCONTO_SVU_GENERIC10-4.alp`)

> Analyse basée sur une lecture directe du XML du fichier `.alp` (52 912 lignes à l'origine). Le fichier a depuis été modifié à plusieurs reprises sur demande explicite de l'utilisateur — voir §6 "Journal des modifications" pour le détail.

## 1. Métadonnées du modèle

| Champ | Valeur |
|---|---|
| Nom du modèle | `SCONTO_SVU_GENERIC10-4` |
| Package Java | `sconto_vsm_generic` |
| Unité de temps | `Second` |
| AnyLogic version | `8.9.8.202602271015` |
| Format `.alp` | `8.9.7` |
| Moteur (`EngineVersion`) | `6` |

## 2. Agents / classes actives (`ActiveObjectClass`)

Le modèle est structuré autour d'une classe racine **`Main`** et de plusieurs types d'agents réutilisables (classes actives) référencés dans le canevas de simulation :

| Classe | Rôle déduit |
|---|---|
| `Main` | Agent racine : contient toute la logique métier, les tableaux de bord KPI, la génération de commandes, les exports Excel/RDF, la hiérarchie ISA-95, et héberge les instances des autres agents. |
| `PosteGenericAgent` | Représente un **poste** générique de la chaîne (poste de travail / processus élémentaire — VSM), avec ses propres files (`Queue`), délais (`Delay`), entrées/sorties (`Enter`/`Exit`), capacité, débit, type de contrôle qualité, etc. |
| `FluxEntity` | L'entité qui circule dans le modèle (flux physique/pièce en cours de traitement) — bibliothèque **Process Modeling** d'AnyLogic (`Movable`, `Queue`, `Delay`, `Enter`, `Exit` proviennent de `com.anylogic.libraries.processmodeling`). |
| `CommandeAgent` | Représente une commande client/fournisseur (génération de commandes, `generateurCommandes`, `tickAppro`). |
| `StrategicAgent`, `TacticalAgent`, `OperationalAgent` | Trois niveaux de la **hiérarchie de contrôle holonique inspirée d'ADACOR/PROSA** (voir §4), alignés sur les niveaux ISA-95 (`NIVEAU_STRATEGIC`, `NIVEAU_TACTICAL`, `NIVEAU_OPERATIONAL`, `NIVEAU_MACHINE`). |
| `CoordinatorAgent` | Coordonne/arbitre entre agents opérationnels (`arbitrerLocal`, `cycleArbitrage`, `cycleDecision`). |
| `BlackboardAgent` | Implémente un **pattern Blackboard** central : les agents publient et lisent des observations, indicateurs VSM et enregistrements de performance partagés (`publishesToBlackboard`, `readsFromBlackboard`, `computesVSMIndicator`, `storesPerformanceRecord`). Rejoué également dans l'export ontologique (individu `agent:BlackboardAgent` nommé `"SCONTO-SVU Blackboard"`). |

> Le code source Java embarqué dans `Main` dépasse **12 000+ lignes** (fonctions, event handlers, classes internes). Il n'a pas été lu ligne à ligne dans son intégralité ; l'inventaire ci-dessous couvre les zones les plus significatives repérées par recherche de motifs.

## 3. Domaines fonctionnels identifiés dans le code de `Main`

### a. VSM (Value Stream Mapping)
- `getRapportVSM` — génération du rapport VSM.
- `champTauxVA` — taux de valeur ajoutée.
- `kpiPCEbar`, `avgCycleTimeCodes/Macro`, `countCycleTimeCodes` — indicateurs de temps de cycle / Process Cycle Efficiency.
- `couvertureStockCibleHeures`, `stockCibleCalcule`, `stockDisponible`, `stockReserve`, `niveauStock`, `politiqueStock` — gestion des stocks (tampons VSM).
- `orderLeadTimeText` — délai de traitement de commande.

### b. SCOR (Supply Chain Operations Reference)
- Catalogue interne des micro-activités SCOR niveau 3, avec classification **PILOTAGE vs EXECUTION** (`CATALOGUE_SCOR_N3`), ex. : `S1.1` = *Schedule Product Deliveries* (PILOTAGE), `S1.2` = *Receive Product* (EXECUTION), `S1.3` = *Verify Product* (EXECUTION), `S1.5` = *Authorize Supplier Payment* (PILOTAGE).
- Codes de macro-processus SCOR : **S**ource, **M**ake, **D**eliver, **SR**/**DR** (Source/Deliver Return) — préfixés `s` dans les identifiants de poste (`sS1.1`, `sM1.2`, `sD1.3`, `sSR1.1`, etc.).
- 5 attributs de performance SCOR calculés et pondérés :
  - `scoreRL` (Reliability), `scoreRS` (Responsiveness), `scoreAG` (Agility), `scoreCO` (Cost), `scoreAM` (Asset Management).
  - Pondération configurable par scénario (`champPoidsRL/RS/AG/CO/AM`), avec validation (`getExperimentHost().showMessageDialog("Poids de performance invalides...")`).
  - `appliquerPoidsAttributsSCOR`, `poidsAHPPourCodeSCOR`, `scorerGoulotAHP` — pondération via **AHP (Analytic Hierarchy Process)**.
  - `calculerPIGlobal`, `kpiGlobal` — indice de performance global agrégé.
- Fonctions de reporting SCOR : `resumeMetriquesSCORGlobales`, `metriquesSCORCalculablesColumns/Rows`, `rapportPostesParCodeSCOR`, `getPostesParCodeSCOR`, `mapCodeSCORToType`, `libelleMacroProcessusSCOR`, `libelleCourtMetriqueSCOR`.

### c. Hiérarchie ISA-95 / alignement ontologique (section commentée `S2.1`)
- Classes internes `ISA95EquipmentNode` (id, nom, typeISA95, parentId, idActeur, refMachineId) et `ISA95ActivityAssignment` (idActeur, idPoste, idEquipment).
- Listes `isa95Hierarchy` et `isa95Assignments`, peuplées **depuis le JSON de scénario** (pas figées dans le modèle) pour rester générique au-delà du cas ZENER.

### d. Architecture multi-agents holonique (ADACOR/PROSA)
- Commentaire explicite : *"schema holonique ADACOR"* et *"couche metier PROSA/ADACOR"*.
- 4 niveaux d'agents (`StrategicAgent` > `TacticalAgent` > `OperationalAgent`, plus `CoordinatorAgent`) qui interagissent via un **`BlackboardAgent`** central.
- Fonctions de décision/arbitrage : `arbitrerLocal`, `cycleArbitrage`, `cycleDecision`, `decisionsHoloniquesColumns/Rows`.
- Le Blackboard est aussi exporté comme individu ontologique (`agent:BlackboardAgent`) avec des relations `publishesToBlackboard` / `readsFromBlackboard` / `computesVSMIndicator` / `storesObservation` / `storesPerformanceRecord`.

### e. Animation / communication inter-acteurs
- Système de file FIFO pour l'affichage cadencé des flux d'information échangés entre acteurs (`FluxInformationnelAnime`, `fileFluxInformationnelsAnimes`, `AnimationMessagesManager`), pour garder une animation lisible même quand la logique métier distribue les messages instantanément.
- Layout automatique des postes sur le canevas, paramétré par acteur et par chaîne indépendante (`positionnerPoste`, constantes `LAYOUT_X_START/STEP`, `LAYOUT_Y_BASE`, `LAYOUT_LANE_HEIGHT`, `LAYOUT_BAND_HEIGHT`) — jusqu'à 8 acteurs en parallèle.

### f. Import/config, export Excel, export RDF
- Import CSV : `Fichier attendu : config_<nomEntreprise>.csv` (message d'erreur trouvé dans le code — un mécanisme de chargement de configuration par entreprise existe en plus du JSON de scénario).
- `ExcelExportManager`, `champIntervalleExportExcel`, `exportExcelActif`, `nbExportsExcelRealises` — export périodique des résultats vers `.xlsx`.
- Export ontologique RDF/Turtle (section commentée `S2.2 C08 — EXPORT ABOX RUNTIME RDF/TURTLE`) : génère un graphe RDF nommé `run:...` par run de simulation, avec triple-génération via des fonctions internes (`aboxTriple`, `aboxUri`, `aboxLit`, `aboxDec`, `aboxIsoAt`). Voir `SCENARIOS_AND_DATA.md` pour le détail du format.

## 4. Expérience de simulation

Une seule expérience est déclarée dans le modèle :

| Élément | Valeur |
|---|---|
| Type | `SimulationExperiment` |
| Nom | `Simulation` |
| Titre affiché | *"SCONTO_VSM_Generic : Simulation"* |
| Bannière | *"SCONTO-SVU : GENERIC SIMULATION MODEL"* |
| Génération aléatoire | Graine fixe (`fixedSeed`, seed = 1) — **runs reproductibles par défaut** |
| Mode d'exécution | `realTimeScaled`, échelle 1.0 |
| Arrêt | `Never` (arrêt manuel) |
| Mémoire max | 512 Mo |

Pas d'expérience d'optimisation, de variation de paramètres ni de Monte Carlo définie dans ce fichier — toute l'exploration de scénarios se fait donc **en amont, via les fichiers JSON de scénario** rechargés dans la même expérience de simulation, plutôt que via le framework d'expériences d'AnyLogic.

## 5. Marqueurs internes de développement

Le code contient des commentaires de section du type `S1.x`, `S2.x`, `C08`, `C14` (ex. *"S2.2 C08 — EXPORT ABOX RUNTIME RDF/TURTLE"*, *"C14.6"*). Ce sont vraisemblablement des **repères de sprint/étape de développement interne**, à ne pas confondre avec les codes SCOR (`S1.1`, `M1.2`, `D1.3`...) qui désignent des micro-activités métier. *Signification exacte des codes `Sx.y`/`Cxx` à confirmer avec l'utilisateur — non documentée dans le fichier.*

## 6. Journal des modifications (session Claude Code)

Toutes les modifications ci-dessous ont été appliquées directement dans le XML du `.alp`, validées par un parse XML après chaque édition (`xml.etree.ElementTree`), et faites à la demande explicite de l'utilisateur suite à des observations sur des runs de simulation.

### a. Numérotation des commandes clients (`CMD_n`) — clarification d'affichage
- **Problème observé** : `CMD_n` était calculé via `commandes.size() + 1`, qui inclut aussi les ordres internes `REAPPRO_x` (réapprovisionnement autonome). Un `REAPPRO` inséré entre deux commandes clients décalait la numérotation (`CMD_1, CMD_2, CMD_4...`), donnant l'impression trompeuse que des commandes clients manquaient.
- **Fix** : ajout d'un compteur dédié `seqCommandeClient` (champ `Main`, initialisé à 0), incrémenté uniquement dans `genererCommande()` pour les commandes clients. `CMD_n` = `++seqCommandeClient`, indépendant du nombre total d'entrées dans `commandes`.
- Popups et logs `[DELIVER]` d'émission de commande mis à jour pour afficher explicitement "commande client N/limite" plutôt qu'un rang ambigu.

### b. `logBilanCommandes()` — séparation client / réapprovisionnement
- Le log `[BILAN]` affiche désormais, pour chaque catégorie (total, livrées, en cours/attente, bloquées, refusées), un sous-décompte `client=` et `reappro=` séparé, en plus du total global — pour éviter la confusion entre "commandes clients livrées" (compteur dashboard) et "toutes commandes confondues" (BILAN).

### c. Libellés dashboard clarifiés
- `"Order Mode"` → `"Order Mode (livrées)"`.
- `"Stock-Only Orders"` → `"Stock-Only Orders (livrées, hors réappro)"`.

### d. Bouton "Pic ponctuel (200 unités)" — extraction du dialogue puis repositionnement
- Initialement dans un `JButton` Swing à l'intérieur du dialogue modal `ouvrirParametresNombreCommandes()` (avec le bouton "Rafale").
- Extrait vers un `<Control Type="Button">` natif AnyLogic dédié (`btnPicPonctuel200`, `Id=1799900001050`) directement sur la vue d'exécution, pour un déclenchement en un clic sans ouvrir le dialogue. Le dialogue ne conserve que le bouton "Rafale" ; une ligne d'aide y renvoie vers le nouveau bouton.
- Position initiale : X=1120, Y=755 (zone vide à droite des contrôles "Contrôle commandes" / "Temps budget simulation").
- **Repositionné** à la demande de l'utilisateur : X=380, Y=1490 — sur la même ligne que le bouton "KPI par micro-activité" (`btnKpiPoste`, X=200, Y=1490, largeur 140), juste à sa droite, en respectant l'espacement de ~40px utilisé entre les autres boutons de cette rangée (`btnJournal1` "TABLE DES EXECUTIONS" à X=20 → `btnKpiPoste` à X=200).
- Comportement inchangé : `declencherPicPonctuelDemande(200)` génère une commande client exceptionnelle de 200 unités, avec message de confirmation ou d'échec (limite de commandes atteinte / simulation non démarrée).

### e. `ordonnancerProduction()` (dans `CoordinatorAgent`) — suppression de la porte d'ordonnancement MTO
- **Problème observé** : la commande de 200 unités (déclenchée via le bouton pic ponctuel) monopolisait la production et bloquait indéfiniment les commandes plus petites, avec accumulation croissante de commandes "en attente".
- **Cause** : la fonction ne libérait qu'un seul ordre du carnet MTO par cycle, sous condition d'une porte `GOULOT`/`PANNE` (`chargeDisponible`) — un ordonnancement conservateur inadapté à un pic de demande.
- **Fix final** (après un premier essai intermédiaire à 3 ordres/cycle, explicitement rejeté par l'utilisateur : *"Je ne veux même pas avoir de restriction sur le nombre d'ordre libéré... on ne doit pas bloquer les ordres parce qu'une commande de 200 est en cours"*) : réécriture complète de la fonction pour **libérer tout le carnet MTO à chaque cycle**, sans porte goulot/panne et sans plafond de nombre d'ordres. Le tri reste par priorité explicite (`priorite` : 1=urgente, 2=normale, 3=basse) puis par EDD (Earliest Due Date, `tPromise`) à égalité de priorité.
- **Limite physique restante (non corrigée, comportement volontairement conservé jusqu'à nouvel arbitrage)** : chaque commande passe unité par unité, en série, dans la chaîne Make (pas de parallélisme ni de traitement par lot détecté dans le fichier). Le temps total d'une commande reste donc à peu près proportionnel à sa quantité — une commande de 200 unités prend ~10× plus longtemps qu'une commande de 20 unités, et **rien n'est livré au client avant que la totalité de la commande soit terminée** (pas de livraison partielle/incrémentale). Deux pistes concrètes ont été proposées à l'utilisateur mais pas encore implémentées : (1) livraison par sous-lots dès qu'une tranche est prête, (2) capacité flexible déclenchée automatiquement au-delà d'un seuil de carnet MTO. Décision utilisateur en attente.

### f. Export Excel de l'historique du tableau de bord (nouvelle feuille "Historique Dashboard")
- **Besoin exprimé** : pouvoir retracer dans Excel les diagrammes du tableau de bord (les ~17 cartes KPI, le bar chart SCOR RL/RS/AG/CO/AM, et la courbe PI vs PI cible), pas seulement lire leur valeur instantanée.
- **Constat** : `exporterToutesLesTablesExcel()` existait déjà (25 feuilles environ, réutilisant les paires `*Columns()/*Rows()` des JTable Swing) mais n'écrivait que des **snapshots ponctuels** — suffisant pour le bar chart SCOR (déjà une photo instantanée) mais pas pour reconstituer une courbe temporelle. La courbe PI/PI cible du dashboard s'appuie elle-même sur des `Dataset` natifs AnyLogic (`dataset`/`dataset1` du `TimePlot`) limités à une fenêtre glissante de 100 échantillons (`SamplesToKeep=100`) — inexploitable pour tracer un run complet.
- **Ajout** : un champ `historiqueDashboard` (`ArrayList<Object[]>`) sur `Main`, alimenté par `capturerPointHistoriqueDashboard()` qui reprend exactement les mêmes expressions que les `TextCode` des cartes dashboard et du bar chart/TimePlot (ex. `wipReelSansJetonsVisuels()`, `tauxRemplissagePct()`, `strategic.scoreRL`, `strategic.piGlobalCourant`), pour une fidélité maximale. Une nouvelle feuille **"Historique Dashboard"** (25 colonnes : temps, les 17 KPI dashboard, RL/RS/AG/CO/AM, PI, PI cible) est écrite via le helper `ecrireFeuilleExcel()` déjà en place, sans nouvelle plomberie d'export.
- **Déclenchement automatique** : la capture est appelée à chaque cycle de l'événement périodique existant `ExcelExportManager` (cadence `champIntervalleExportExcel`, 30 s par défaut), plus une capture immédiate (t=0) dans `demarrerSimulation()` juste après l'activation de `modeExecution`.
- **Comportement demandé par l'utilisateur** : `historiqueDashboard.clear()` est appelé dans `demarrerSimulation()` — chaque nouveau run repart d'un historique vide et réécrit le **même fichier Excel** (`excelFileName()`, déjà en overwrite atomique), pour éviter l'accumulation de données entre runs et la multiplication de fichiers générés.

### g. Diagnostic complet de la vue hiérarchique holonique — 4 correctifs (C14.52 à C14.55)
- **Symptôme initial** : les pastilles `OperationalAgent` (grille "OperationalAgents — N actifs" de la vue hiérarchique) ne réagissaient pas de façon cohérente avec ce qui se passait réellement sur la vue des micro-activités.
- **C14.52 — commandes MTS jamais visibles côté Deliver** : une commande MTS ("servie depuis le stock") ne génère aucune entité métier réelle sur la chaîne Deliver — elle est uniquement animée via un jeton visuel (`lancerFluxVisuelDeliverClient()`, `typeProduit="TRACE_VISUEL_SCOR"`). `analyserEtat()` (OperationalAgent) exclut à raison ces jetons du calcul de goulot (fix historique C14.49/51), mais du coup ces agents restaient figés à `IDLE` (gris) même pendant qu'une commande réelle était visiblement en cours de livraison. Fix : un jeton visuel présent sur un poste du groupe fait désormais passer l'état à `WORKING` (vert) **de façon transitoire**, sans jamais pouvoir contribuer à `fileReelle`/`wtMoyen` (donc toujours incapable de déclencher `GOULOT`/`PANNE`).
- **C14.53 — popup `popupOperationalAgent()` incohérent avec le poste réel** : le popup affiché au clic sur une pastille marquait **tous** les postes du groupe "⚠️ GOULOT" dès que `p.goulot` (un flag *de groupe*, écrit identiquement sur tous les postes rattachés par `analyserEtat()`) était vrai — y compris des micro-activités n'ayant encore traité aucune unité. Fix : le popup recalcule maintenant un état **propre à chaque poste individuel** (file réelle + attente réelle de ce poste seul, mêmes seuils `seuilAlertFile`/`seuilGoulotWT`), et affiche l'ID du poste (`p.idPoste`, absent jusqu'ici) à côté de son nom.
- **C14.54 — Plan (P2-P5) totalement gelé** : `recalculerTousLesGroupesOperationnels()` crée un `OperationalAgent` (donc une pastille) pour **tous** les postes du modèle, Plan compris (`sP2.4.1`, `sP3.4.1`, `sP4.4.x`...). Mais `analyserEtat()` avait une porte supplémentaire qui ignorait silencieusement tout agent classé `ROLE_TACTIQUE` (le cas de tous les codes Plan `P2`-`P5`) — ces pastilles restaient donc figées sur `IDLE` à vie, quel que soit le flux réel (uniquement des jetons visuels de commande — planification, lancement production, approvisionnement). Porte supprimée : seul le garde `postesLies` non vide subsiste, cohérent avec le commentaire de `recalculerTousLesGroupesOperationnels()` ("1 OperationalAgent par couple (acteur, code SCOR N3), sur TOUS les postes du modèle").
- **C14.55 — popup `CoordinatorAgent` contredisant son propre pavé** : la couleur du pavé Coordinateur (`couleurSupervisorMacro`) était déjà calculée **en direct** (goulots réels + attente réelle du macro-processus), mais son popup (`popupSupervisor`) lisait un champ séparé `sv.etatAgent`, écrit uniquement par `traiterAlertesTactiques()` — fonction qui retourne dès sa 1ère ligne quand `realignementFluxHierarchiqueActif=true` (le routage "génération 2", actif par défaut). `sv.etatAgent` restait donc figé sur sa valeur d'initialisation (`"IDLE"` → *"Inactif / en attente"*) à vie, indépendamment de la couleur réelle affichée (ex. pavé rouge + popup "Inactif / en attente"). Même cause racine pour "Alertes traitées"/"Rééquilibrages"/"Dernier goulot" du même popup, alimentés par une chaîne de décision AHP "génération 1" (`recevoirAlerteGoulot`/`prendreDecisionAHP`) elle aussi jamais atteinte sous le routage actif — toujours 0/0/"—". Fix : logique extraite dans une fonction unique `etatCoordinateurMacro()`, utilisée à la fois par la couleur du pavé et par le popup (ne peuvent plus diverger) ; les 3 compteurs morts remplacés par les compteurs réellement alimentés en génération 2 (`nbMessagesHierarchiquesRecus` / dernier message reçu).
- **Vérifiés sains, sans correction nécessaire** : popups `TacticalAgent`, `StrategicAgent` et `BlackboardAgent` — dans les 3 cas, couleur du pavé et texte du popup dérivent déjà des mêmes champs/calculs (`board.kpiParMacro`+`ta.seuilEscalade` ; `strategic.facteurAjustement` ; `board.alertesPubliees`), donc intrinsèquement cohérents.
- **Limite résiduelle non corrigée (signalée à l'utilisateur, hors périmètre demandé)** : l'état `AJUSTEMENT` (orange) du Coordinateur dépend toujours de `sv.dernierReeq`, alimenté par la même chaîne AHP "génération 1" jamais exécutée sous le routage actif — en pratique le Coordinateur ne peut donc afficher que vert ou rouge, jamais orange, tant que ce mécanisme n'est pas repensé pour la génération 2.

### h. `calculerPIGlobal()` (`StrategicAgent`) — chaîne de correctifs PI/SCOR (2026-09-04/05)
- **Symptômes observés** : PI démarrant à 0 au lieu de la cible, crash juste après le démarrage, PI restant durablement sous la cible (`ciblePIGlobal`, codée en dur à 7.5).
- **Correctifs appliqués** (diagnostic itératif via un nouveau log `[SCOR-DETAIL]`, throttlé à 1/5s, décomposant RL/RS/AG/CO/AM à chaque calcul) :
  1. `piGlobalCourant` jamais seedé depuis `ciblePIGlobal` au démarrage + une famille SCOR sans donnée réelle (RS/CO avant toute commande close) notée "0 performance" au lieu d'être exclue → seed ajouté dans `demarrerSimulation()`, poids effectif forcé à 0 pour une famille sans échantillon.
  2. `tauxCommandesLivreesCloses()` comptait `livrees++` pour `SERVIE` **et** `EN_RETARD`, rendant le taux structurellement égal à 100% → restreint à `SERVIE` uniquement.
  3. Ajout de `seuilMinEchantillonRL` (défaut 5) : RL n'est pondéré dans le PI qu'à partir de 5 commandes closes réelles (sous ce seuil, un ratio sur 1-2 commandes est trop volatil).
  4. `prevoirDemande()` se basait sur `main.nbTermines` (toute production, MTS/REAPPRO inclus) au lieu de la vraie demande client — boucle de rétroaction positive non bornée (plus on produit, plus la "demande" prévue augmente). Réécrit pour utiliser `main.commandes` (hors `REAPPRO_`), avec un gate ≥2 commandes clientes et mesuré depuis le timestamp de la 1ère commande cliente.
  5. `couvertureStockCibleHeures` (24h) / `horizonRattrapageHeures` (4h à l'origine) créaient une amplification ×6 du débit MTS calculé → `horizonRattrapageHeures` relevé à 24h + plafond dur `plafondMultipleDebitBase` (×3 du débit nominal du scénario).
  6. `RL.2.2` utilisait une source différente et cassée (`verifierFillRate()` = servies / TOUTES commandes jamais créées, y compris en transit et REAPPRO) — RL (poids dominant) crashait à chaque nouvelle commande créée, avant même sa livraison. Unifié sur `tauxCommandesLivreesCloses()` + même garde `seuilMinEchantillonRL`.
- **Résiduel signalé, non corrigé (« ne rien changer pour l'instant »)** : `couvertureStockCibleHeures=24h` reste grand par rapport à la durée des runs de test (~5-10 min) → AG/CO transitoirement bas en début de run (politique de rampe, pas un bug). CO peut aussi tomber à 0 une fois le volume établi : reflet réel de l'économie du scénario `ZENER_SA_Togo` (61/71 postes ont un coût horaire de main-d'œuvre supérieur au `chiffreAffaireParUnite`) — question de config scénario, pas touchée.
- **Nouvel outil associé** : `generate_dashboard_charts.py` (racine du repo) — script Python autonome (nécessite `pip install openpyxl`) qui insère 9 graphiques Excel natifs dans une feuille "Graphiques Dashboard" à partir de la feuille "Historique Dashboard" d'un export déjà produit. À exécuter **après** la fin du run, fichier Excel fermé.

### i. `calculerPIGlobal()` — nettoyage de la redondance des sous-métriques RL (2026-09-06)
- **Constat** : `RL.3.33` (exactitude articles) et `RL.3.35` (exactitude quantités) n'ont aucune source de donnée indépendante dans le modèle (aucune erreur d'article/quantité n'est simulée — mono-produit) : elles recopiaient `tauxCommandesLivreesCloses()`, donnant l'illusion de 4 mesures SCOR indépendantes sous RL alors qu'il n'y en a qu'une seule réelle (le taux de ponctualité).
- **Fix** : `RL.3.33`/`RL.3.35` repassées à poids 0 (informatif, affichées pour traçabilité SCOR mais hors score), même traitement que `CO.3.13`/`CO.3.11`/`AM.3.18`. `nRL` passé de 4 à 2, `poidsRL = 1/2` réparti entre `RL.2.1` et `RL.2.2` (les 2 seules mesures réellement notées).
- **Effet** : aucun changement de la valeur de `scoreRL` (l'agrégation `FuzzyGradeSet.agregerMetriques()` est une moyenne pondérée normalisée — dupliquer une même valeur à poids égal ne change pas la moyenne) ; correction de rigueur méthodologique, pas un fix de la décroissance du PI.
### j. CO bloqué à 0, RL affiché à 0 et « Fill Rate » ambigu — 3 correctifs (C15.9, 2026-09-06)

Diagnostic mené sur données réelles (feuille "Historique Dashboard" du run `..._1788734997182.xlsx`, 130 points / 3840 s / 20 commandes / 903 unités livrées), après que l'utilisateur a signalé qu'un attribut SCOR bloqué à 0 fausse le PI et que le PI stabilisé reste sous sa cible.

**Constat de départ — le PI est exactement la moyenne pondérée linéaire des 5 attributs** : à t=3840 s, `0.40×10 (RL) + 0.20×6.202 (RS) + 0.10×6.531 (AG) + 0.15×0 (CO) + 0.15×9.651 (AM) = 7.341`, soit très exactement le PI affiché. Les poids proviennent de `scenario_ZENER_SA_Togo_v72.json` (`champPoidsRL=0.4`, `RS=0.2`, `AG=0.1`, `CO=0.15`, `AM=0.15`). **CO=0 était donc la seule et unique cause du déficit face à la cible de 7.5.**

- **C15.9.a — `CO.1.1` bloqué à 0 : bug d'unité sur le chiffre d'affaires (corrigé).** `calculerCoutsCumules()` accumule le coût main-d'œuvre par **unité** passée sur chaque poste (`k.sumCycleTime × coutHoraireMainOeuvre`), alors que le CA était estimé par `chiffreAffaireParUnite × main.nbTermines`. Or `nbTermines` est un compteur **hybride** : incrémenté par unité sur le flux de production (ligne ~11738) mais **une seule fois par commande** sur le chemin de livraison directe MTS (`finaliserReceptionClientDirecte()`, ligne ~5555) — le mode nominal de ce modèle. Sur le run analysé : coût total = 182 209 FCFA (46 800 M.O. + 135 409 matière) contre un CA estimé à `6500 × ~20 commandes ≈ 130 000 FCFA`, au lieu de `6500 × 903 unités livrées = 5 869 500 FCFA`. Le ratio coût/CA dépassait donc 1.0, était écrêté par `Math.min(1.0, …)`, et la normalisation `COST 0→1` donnait `score10 = 10×(1−1.0) = 0` en permanence. **Fix** : nouvelle fonction `unitesLivreesClients()` (somme des `qte` des commandes clientes closes, hors `REAPPRO_`, même périmètre que `tauxCommandesLivreesCloses()`), utilisée comme assiette du CA. Effet attendu sur ce run : ratio 0.031 → **CO ≈ 9.69** et **PI ≈ 8.79**, au-dessus de la cible.
- **C15.9.b — RL affiché à 0 pendant la phase d'amorçage (corrigé, affichage seulement).** Sous `seuilMinEchantillonRL` (5 commandes closes), les 2 métriques notées ont un poids 0 ; or `FuzzyGradeSet.agregerMetriques()` ignore les métriques à poids 0, donc `agregerN3()` renvoyait un grade vide et `scoreRL` retombait à **0**, affiché tel quel au dashboard, dans le bar chart SCOR et dans l'historique Excel. Sur le run analysé, RL restait ainsi à 0 pendant **930 s** alors que 100 % des commandes closes étaient livrées à temps. **Le PI n'était pas faussé** pour autant (`wEffRL=0` : RL est bien exclu de l'agrégation tant que `sommePoidsRL` vaut 0) — seul l'affichage mentait. **Fix** : quand le seuil n'est pas atteint mais qu'au moins une commande est close, `scoreRL` est recalculé sur les scores réels à poids nominaux (0.5/0.5) pour l'affichage, sans toucher aux poids qui gouvernent l'entrée de RL dans le PI (protection anti-volatilité conservée).
- **C15.9.c — « Fill Rate » : trois sources divergentes, harmonisées.** (1) La carte dashboard et la colonne Excel « Fill Rate (%) » n'affichaient **pas un fill rate** mais `tauxRemplissagePct()` = `nbTerminesProduction / (nbTerminesProduction + totalRebuts)`, un **taux de conformité qualité** (94,4 % sur le run = 100 − 5,6 % de scrap) — renommés en « Taux de conformité » / « Taux de conformité qualité (%) » (et le libellé de série correspondant mis à jour dans `generate_dashboard_charts.py`, qui référence la colonne par index, pas par nom). (2) Le panneau Deliver affichait `verifierFillRate()×100` sous le libellé « Taux de livraison à temps » — remplacé par `tauxCommandesLivreesCloses()`, avec un « — (aucune commande close) » explicite au lieu d'un faux 100 % quand rien n'est encore clos. (3) `valeurRuntimeMetriqueSCOR()` renvoyait encore `verifierFillRate()` pour `RL.2.2` (et `RL.1.1`) alors que `calculerPIGlobal()` utilise `tauxCommandesLivreesCloses()` depuis C15.8 : les tableaux SCOR affichaient donc une valeur différente de celle réellement pondérée dans le PI. Sources et chaîne de preuve (`preuveMetriqueSCOR`) harmonisées.

**Hypothèse précédente invalidée par les données** : le délai promis figé (`delaiPromessePourMode()` = 300 s MTS / 1800 s MTO / 3600 s ETO) n'a **pas** produit de dérive irréversible de RL sur ce run — `Delayed Orders` est resté à 0 du début à la fin et RL s'est stabilisé à 10/10 sur les 2900 dernières secondes. La « décroissance continue » observée auparavant était en réalité la phase d'amorçage (RL exclu + CO à 0) de runs trop courts pour en sortir.

### k. Traçabilité du périmètre du PI — 2 colonnes d'audit (C15.10, 2026-09-07)

Vérification du run `..._1788741374838.xlsx` (57 points) après les correctifs C15.9 : CO remonte à 9,53 (ratio coût/CA = 0,047 au lieu d'être écrêté à 1,0), RL s'affiche à 10/10 dès t=60 s au lieu de rester à 0 pendant 930 s, et le PI se stabilise à **8,71–8,77** contre une cible de 7,5 (la prédiction du fix était 8,79). Le recalcul manuel du PI sur les 57 points confirme la formule au millième près.

Ce contrôle a cependant révélé une **zone non auditable** : de t=60 s à t=810 s (14 % du run), RL est affiché à 10/10 mais son poids effectif est encore 0 (seuil `seuilMinEchantillonRL` non atteint), donc le PI est renormalisé sur les 4 autres attributs. Un recalcul naïf `0.40×RL + 0.20×RS + …` donnait 8,569 contre 7,614 affiché à t=690 s — un écart de 0,95 point inexplicable à partir des seules colonnes exportées. C'est le revers symétrique du correctif C15.9.b : le « RL=0 trompeur » a été remplacé par un « RL=10 affiché mais non pondéré ».

- **Ajout** : deux champs publics sur `StrategicAgent`, renseignés à chaque `calculerPIGlobal()` juste après le calcul des poids effectifs — `attributsPonderesPI` (String, ex. `"RS+AG+CO+AM"` puis `"RL+RS+AG+CO+AM"`) et `sommePoidsEffectifsPI` (double, le dénominateur de renormalisation). Deux colonnes correspondantes en **fin** de la feuille "Historique Dashboard" : « Attributs pondérés dans le PI » et « Somme des poids effectifs » (27 colonnes au lieu de 25).
- **Ajout en fin de tableau volontaire** : `generate_dashboard_charts.py` adresse les colonnes par **index** (PI en 24, PI cible en 25) — insérer ailleurs aurait décalé toutes ses séries. Aucune modification du script n'est nécessaire.
- **Usage** : le PI est désormais recalculable à la main sur toute la durée du run, y compris pendant la phase d'amorçage — `PI = Σ(poids_nominal × score) / « Somme des poids effectifs »`, en ne sommant que sur les attributs listés dans « Attributs pondérés dans le PI ». Les poids nominaux viennent du scénario JSON (`champPoidsRL=0.4`, `RS=0.2`, `AG=0.1`, `CO=0.15`, `AM=0.15`).
- **Réserve d'interprétation restante (non corrigée)** : les deux premiers points de chaque historique (avant le premier cycle de calcul réel) affichent `PI = 7.5`, qui est la valeur d'amorçage `ciblePIGlobal` et non une mesure — ils sont à exclure de toute lecture de tendance. La colonne « Attributs pondérés » les rend maintenant identifiables (`"aucun (PI non calcule)"`).

### l. Gel du PI pendant la phase d'amorçage (C15.11, 2026-09-07)

Réponse au problème de comparabilité temporelle identifié en §6.k : deux PI calculés sur des périmètres d'attributs différents ne sont pas comparables. Sur le run `..._1788741374838`, l'entrée de RL dans le calcul faisait passer le PI de 7,799 à 8,695 entre t=810 s et t=840 s — un saut qui se lit à tort comme un gain de performance alors que c'est un changement d'instrument de mesure.

- **Règle** : tant que les 5 attributs ne sont pas **tous** pondérés, `pi` est maintenu à `ciblePIGlobal` (7,5) ; il ne varie qu'à partir du moment où le périmètre est complet. Le PI publié porte donc toujours sur le même périmètre. Un champ `perimetrePIDejaComplet` mémorise le franchissement : une fois le périmètre complet atteint, le PI n'est plus jamais gelé (réinitialisé à chaque `demarrerSimulation()`, comme `attributsPonderesPI` et `sommePoidsEffectifsPI`).
- **Effet décisionnel vérifié — c'est une amélioration, pas seulement un habillage** : `ajusterDebits()` disposait déjà d'un mode « AMORCAGE » mais sur un critère bien plus faible (`nbTermines > 0`), si bien qu'il prenait des décisions RALENTIR/ACCELERER sur un PI à périmètre partiel. Comme `ciblePIGlobal` (7,5) est strictement comprise entre `seuilPI_bas` (5,0) et `seuilPI_haut` (8,0), le gel maintient la décision en « MAINTENIR » pendant toute la chauffe, au lieu de réagir à une valeur non comparable.
- **Garde-fou contre le gel permanent** : si `CO` ne peut structurellement jamais entrer (scénario sans `chiffreAffaireParUnite`), attendre le périmètre complet figerait le PI à la cible pendant tout le run. Dans ce cas (`attenteImpossible`), le gel ne s'applique pas et le PI reste renormalisé sur les attributs réellement disponibles — comportement antérieur conservé.
- **Traçabilité** : pendant le gel, la colonne « Attributs pondérés dans le PI » affiche `AMORCAGE (PI maintenu a la cible) | mesures: …`, de sorte que la phase de chauffe est explicitement identifiable dans l'export Excel et ne peut pas être confondue avec une mesure.
- **Lecture académique** : cela revient à écarter la période transitoire avant d'analyser le régime permanent — pratique standard en simulation à événements discrets (Law & Kelton). **À déclarer dans le mémoire** : la valeur 7,5 affichée pendant la chauffe est une **convention d'initialisation, pas une mesure** ; seuls les points où la colonne de traçabilité liste les 5 attributs constituent des observations exploitables.

### m. Scénario nominal ZENER — résultats de référence (2026-09-07)

Après la chaîne complète de correctifs C15.9 à C15.23, un run de référence a été produit pour valider les 5 attributs sur le scénario nominal (`scenario_ZENER_SA_Togo_v72.json`, demande réelle ZENER, non modifiée) : 37 commandes, 8430 s de simulation, run `..._1788797499526.xlsx`. Arithmétique du PI vérifiée exacte sur tout le run (`0.40×RL + 0.20×RS + 0.10×AG + 0.15×CO + 0.15×AM`).

**PI = 9,02/10, stable en régime permanent** (±0,03 sur les 25 derniers points). Après une phase transitoire (t=15 à ~700s, stock descendant de 100 à un minimum de 51-59), le système atteint un régime où le **stock fini oscille durablement entre 85 et 144 unités sans tendance à la baisse** — hypothèse de rupture de stock testée et invalidée sur ce run : le débit réel du goulot suffit à couvrir la demande nominale sur la durée, malgré une congestion interne sévère.

| Attribut | Score | Lecture |
|---|---|---|
| RL (poids 0,40) | **10,00** | 37/37 commandes livrées dans le délai d'engagement (24h), lead time réel moyen 4,8h. Stock jamais proche de la rupture. |
| RS (poids 0,20) | **7,49** | Source 9,98, Deliver 10,0, RS.1.1 8,00, RS.3.94 9,51 — mais **RS.2.2 Make = 0,00** : 427,8s de traversée pour un nominal pondéré de ~27-30s (facteur >14), structurel et constant sur tout le régime stabilisé. |
| AG (poids 0,10) | **6,62** | Débit 1,01 (16,2 ent/h vs borne 160, plombé par Make) ; occupation système 8,89 ; stabilité du débit (proxy hors SCOR) 9,93. |
| CO (poids 0,15) | **9,39** | Ratio coût/CA = 6,1% (160 972 FCFA M.O. + 289 849 FCFA matière). |
| AM (poids 0,15) | **9,65** | Disponibilité machine 94,1% ; couverture de stock 0,29 jour. |

**Interprétation retenue (validée avec l'utilisateur)** : le PI décrit fidèlement une chaîne qui satisfait pleinement ses clients (RL, CO, AM sains) tout en portant un défaut de production localisé et permanent — c'est la lecture hiérarchique attendue d'un indice SCOR : le niveau 1 dit "le client est bien servi", le niveau 2 (`RS.2.2`) dit "la ligne a un point de rupture précis" (poste de tare des bonbonnes, `sM1.3.1`, capacité simultanée = 1). Le goulot ne menace pas le service client à ce niveau de demande (confirmé par RL = 10,0 sur les 282 points du run, sans exception) mais coûte en débit de sortie, en irrégularité de production (WIP oscillant jusqu'à 135 unités) et en stock immobilisé.

**Réserves à formuler explicitement dans toute présentation de ce résultat** :
- `AG` mélange une vraie métrique SCOR (`AG.3.32`, poids 1/3) et deux proxies hors référentiel (occupation système, stabilité du débit) — voir §6.i/6.j/6.l et [[audit_scor_conformite]] pour le détail de chaque écart de définition.
- Intitulés SCOR 12 exacts de `AG.3.32`, `AM.3.9` et `RS.3.94` non encore confirmés par l'utilisateur depuis son exemplaire du référentiel — `AG.1.1` déjà traité (C15.23, ne revendique plus le code officiel).
- Les bornes de normalisation restent partiellement calibrées sur des heuristiques du modèle (délai d'engagement client, nominal pondéré des postes) plutôt que sur un benchmark sectoriel externe.

### n. Vérification SCOR 11/12 des codes AG.1.1, AG.3.32, AM.3.9, RS.3.94 — 2 corrigés, 2 confirmés (C15.24, 2026-09-07)

Les intitulés SCOR de ces 4 codes avaient été affirmés de mémoire au fil de l'audit (§6.i à §6.m), sans être vérifiés contre le texte du référentiel. À la demande de l'utilisateur (version SCOR 12 citée), une vérification a été menée en extrayant le texte intégral du document SCOR 11 (accès libre ; les codes de niveau 3 concernés sont anciens et stables dans le référentiel, mais la correspondance exacte avec l'édition SCOR 12 de l'utilisateur reste à confirmer par lui).

**Confirmés exacts, aucune modification** :
- `AG.3.32` = *Current Delivery Volume* — conforme à l'usage du modèle.
- `RS.3.94` = *Order Fulfillment Dwell Time* — conforme à l'usage du modèle.

**Invalidés et corrigés** :
- `AG.1.1` — déjà traité en C15.23 (§6.l) : SCOR distingue *Upside Supply Chain Flexibility* (AG.1.1, niveau 1) et *Upside Supply Chain Adaptability* (AG.1.2) ; le modèle calculait une stabilité de débit, sans rapport avec l'une ou l'autre.
- `AM.3.9` (**C15.24**) — le référentiel définit ce code comme *% of packaging/shipping materials reused (internally)*, un indicateur environnemental de recyclabilité des emballages, dans un groupe cohérent avec `AM.3.5`/`AM.3.6`/`AM.3.8`. Le modèle y calculait la disponibilité d'équipement (`MTBF/(MTBF+MTTR)`), un concept de maintenance industrielle (TPM) sans code SCOR natif trouvé dans le référentiel. Même traitement qu'`AG.1.1` : la grandeur reste calculée et pondérée dans AM (mesurable, informative) mais ne revendique plus le code officiel — renommée `PROXY.AM.DISPONIBILITE_MACHINE` dans les 7 points du code concernés (profil de normalisation, URI ABox, rattachement de processus, valeur runtime, unité, chaîne de preuve, métrique du PI). `AM.3.9` apparaît désormais comme non calculable dans les tableaux SCOR, plutôt que de renvoyer une mesure sous un code qui promet autre chose.

**Bilan** : sur les 4 codes vérifiés depuis le début de l'audit, 2 étaient corrects (`AG.3.32`, `RS.3.94`) et 2 étaient erronés (`AG.1.1`, `AM.3.9`) — un taux d'erreur d'un tiers sur les affirmations faites de mémoire, qui confirme la nécessité de vérifier chaque code SCOR contre le texte du référentiel plutôt que d'assumer sa conformité. AG et AM ne revendiquent donc plus qu'un seul vrai code SCOR chacun (`AG.3.32` et `AM.2.2` respectivement) ; le reste est explicitement proxy.

### o. Détection des retards en cours de route et campagne comparative (C15.25 à C15.29, 2026-09-09)

L'utilisateur a introduit une commande exceptionnelle de 200 unités pour observer la propagation d'une perturbation. Constat initial : ~500 unités non livrées, WIP à 471, et **RL imperturbable à 10,00/10** — la perturbation était totalement invisible pour le PI.

**Cause racine** : `evaluerPonctualiteMetier()` n'était appelée qu'à la livraison. Une commande bloquée en carnet conservait un statut transitoire (`CREE`/`EN_ATTENTE`/`EN_COURS`), que RL n'agrège pas — elle pouvait dépasser son engagement sans qu'aucun indicateur ne le signale.

- **C15.25 — détection en continu.** `evaluerRetardsCommandesOuvertes()`, appelée au bilan périodique (60 s), marque les commandes ouvertes ayant dépassé leur engagement. Un champ dédié `retardConstate` est utilisé plutôt qu'un écrasement de `cmd.statut` : `EN_ATTENTE` pilote la politique de stock et l'ordonnancement, le modifier casserait la production. La mesure repose sur `dureeMetierEcoulee()` = max(durée planifiée, temps écoulé) — l'accumulateur `dureeReelleAccumulee` ne progresse pas pendant l'attente en carnet, une détection fondée sur lui seul n'aurait donc jamais rien vu.
- **C15.26 — périmètre ZENER et engagement figé.** Deux corrections liées. (a) La part client (réception/vérification chez le client, postes `sS1.2.4`/`sS1.3.3` de catégorie CLIENT) est comptabilisée séparément (`dureeClientAccumulee`) et retirée de la mesure d'engagement : elle pesait 0,5 h à 6 h selon le tirage, rendant tout seuil discriminant impossible (distribution normale jusqu'à 8,40 h). Sans elle : 0,92 h / 1,65 h / 2,38 h (min/moy/max). (b) Le mode d'engagement est **figé à la création** (`modeEngagementClient`) : une commande MTS requalifiée en MTO faute de stock conserve son délai client — sinon elle gagnerait du délai précisément parce que ZENER n'a pas su la servir sur stock. **Seuils recalés : MTS 4 h, MTO 8 h, ETO 24 h.**
- **C15.27 — borne de `RS.1.1`.** L'abaissement de l'engagement à 4 h avait mis grandeur et borne en désaccord de périmètre : `RS.1.1` mesure le lead time **bout en bout** (définition SCOR) mais sa borne était devenue le périmètre ZENER seul, d'où un score plaqué à 0. La borne redevient un engagement bout en bout via `borneLeadTimeClientSecondes()` = engagement ZENER + réception client nominale (≈ 3,3 h), soit 26 280 s.
- **C15.28 — collision de sous-chaînes sur les identifiants (bug majeur).** Le rattachement d'une unité de production à sa commande se faisait par `refCommandeFlux.contains(cmd.idCommande)` : or `"CMD_44_F_12".contains("CMD_4")` est vrai. Les unités de `CMD_44` étaient créditées à `CMD_4`, parcourue en premier ; `CMD_44` ne complétait jamais son compte et restait figée en `EN_COURS` tout le run, jamais livrée, alors même que le stock fini débordait. Constat : **13 commandes bloquées, 33 livrées seulement**. Corrigé par `fluxAppartientACommande()` (égalité ou préfixe suivi d'un séparateur). Résultat après correction : **44 commandes livrées, 1 seule bloquée**. Le défaut n'apparaissait qu'avec assez de commandes pour que `CMD_N` et `CMD_NM` coexistent — invisible sur les runs courts.
- **C15.29 — trace diagnostique** `[DIAG-BLOQUEE]` : journalise, pour chaque commande encore en production, l'écart entre unités comptées et commandées. Ajoutée pour élucider l'anomalie résiduelle (voir ci-dessous).

**Campagne comparative (même version de code des deux côtés) — voir `RAPPORT_COMPARATIF_NOMINAL_PERTURBE.md` pour le détail complet :**

| | Nominal | Perturbé | Écart |
|---|---|---|---|
| PI | **8,789** | **7,589** | −1,200 |
| RL | 10,000 | 7,330 | −2,670 |
| RS | 6,438 | 5,655 | −0,783 |
| Mode de service | 45 MTS / 0 MTO | 22 MTS / 22 MTO | — |
| Commandes en retard | **0** | **12** | +12 |
| WIP moyen | 70,7 | 233,1 | ×3,3 |

**Validation critique : zéro faux retard en régime nominal** (RL = 10,00 sur 45 commandes) — la calibration du seuil à 4 h sur le périmètre ZENER est confirmée empiriquement. 89 % de l'écart de PI provient de RL ; CO et AM sont quasi inchangés, ce qui sert de contrôle de cohérence (une perturbation d'ordonnancement ne doit pas modifier l'économie unitaire ni la disponibilité machine).

**Anomalie résiduelle non élucidée** : un ordre de réapprovisionnement interne (`REAPPRO_11`, 135 unités) reste en `EN_COURS` en fin de run nominal. Sans effet sur le service client (45/45 commandes clients livrées) mais explique l'écart production/livraison. La trace `[DIAG-BLOQUEE]` doit permettre de trancher au prochain run.

- **Piste ouverte pour la décroissance continue du PI réel, non implémentée** : `cmd.statut` (SERVIE/EN_RETARD, source unique de tout RL) est fixé en comparant `time()` au moment de clôture à `cmd.tPromise = cmd.tCreation + delaiPromessePourMode(mode)`, où `delaiPromessePourMode()` renvoie un délai **fixe et codé en dur** (MTS=300s, MTO=1800s, ETO=3600s), indépendant du scénario JSON, de la charge système ou du WIP. Si le lead time réel du système augmente progressivement (accumulation de WIP, saturation de postes), une proportion croissante de commandes franchit ce seuil fixe et bascule en `EN_RETARD` — mécanisme structurellement capable de produire une décroissance continue et irréversible de RL (poids dominant dans le PI). Hypothèse à confirmer en comparant, dans un log `[SCOR-DETAIL]`/lead time réel récent, si `RS.1.1` (lead time global) croise ces seuils fixes au fil du run. Non vérifié ni corrigé à ce stade.

### p. Réponse à la relecture doctorale du chapitre 5 — Make Cycle Time, matières, carnet MTO, robustesse statistique (C15.30-C15.32, 2026-09-11/12)

Suite à l'analyse de `Correction_chap5.docx` (relecture externe du chapitre 5) et `SCONTO_Rapport_Comparatif_Nominal_Perturbe.docx`, quatre points relevant de l'utilisateur (§1.2, §1.4, §1.6 du document de correction) ont été traités dans l'ordre : d'abord des corrections **textuelles** dans une version antérieure de `RAPPORT_COMPARATIF_NOMINAL_PERTURBE.md` (AG recalculé sur fenêtre commune, REAPPRO_11 expliqué avec preuve RDF, stock matière rendu honnête) ; puis des corrections du **modèle** lui-même (C15.30-C15.32 ci-dessous) ; enfin une **régénération complète** de `RAPPORT_COMPARATIF_NOMINAL_PERTURBE.md` avec les runs post-correctifs, et un nouveau document `RAPPORT_CAMPAGNE_STATISTIQUE.md` répondant à §1.2. **Historique détaillé de la session (fichiers de run, hypothèses explorées) dans la mémoire de session : `correction_chap5_en_cours.md`.**

- **C15.30 — Make Cycle Time (et toute la famille `RS.2.x`) ne sature plus à 0.** `NormalizationProfile.score10()` était linéaire-puis-coupure-nette à 0 dès que la valeur dépassait `facteur×nominalPondéré` (facteur=10, cf. C15.22). Make étant à 13× le nominal en régime normal et 56× en perturbé — les deux au-delà du seuil — les deux régimes affichaient 0,000, indiscernables. Nouveau champ `boolean decroissanceLente` sur `NormalizationProfile` (défaut `false`, **aucun autre indicateur déjà audité n'est touché**) : quand actif (direction COST, `min>0`), remplace la coupure nette par `10×min/valeur` (décroissance hyperbolique, jamais de plancher dur). Activé uniquement sur `RS.2.1/2.2/2.3/2.5` dans `majBorneCycleMacro()`. Vérifié sur 3 runs réels : Make passe de 0,000/0,000 à des scores non saturés (0,713 nominal ; 0,204-0,213 selon les runs perturbés), effet en cascade sur RS/PI confirmé arithmétiquement exact à chaque fois.
- **Export du stock matière par article** : nouvelle colonne Excel/CSV `detailStockMatiereParMatiere()` (format `idMatiere=valeur|idMatiere=valeur`), en plus de l'agrégat existant qui reste affiché mais désormais explicitement caveaté comme somme hétérogène (kg de GPL + unités de bouteilles/kits). Vérifié fonctionnel sur 3 runs réels.
- **C15.31 — diagnostic corrigé, cause élucidée : ce n'est pas un bug de production.** La trace `DiagLancementProductionAtteint` (dans `lancerProductionCommandeOrchestree`) utilisait `board.logEvent()` — non exporté fiablement post-run (échantillon tronqué de la file « Decisions Holoniques »), contrairement à sa cousine `DiagCarnetEntree` qui utilisait déjà `tracerFluxHierarchique()` (AER, exhaustif). C'était l'erreur : la trace, corrigée pour utiliser `tracerFluxHierarchique()`, confirme que `ExecutionStart` est bien émis pour les commandes qui restent `EN_COURS` en fin de run — **la production démarre et progresse réellement** (unités observées traversant plusieurs postes Make jusqu'à la dernière seconde du run). Même cause que `REAPPRO_11` (§o) : une commande volumineuse créée tard dans le run n'a simplement pas le temps de s'écouler derrière le goulot avant la coupure. Phénomène observé sur des ordres `REAPPRO_*` **et, sur des runs ultérieurs, occasionnellement des commandes clientes** (`CMD_22` puis `CMD_29`/`CMD_41`) — décidé avec l'utilisateur comme non-impactant sur l'interprétation des résultats, non documenté comme réserve active ; à surveiller si la fréquence continue d'augmenter sur de futurs runs.
- **C15.32 — campagne de réplications statistiques (réponse à §1.2).** 3 réplications indépendantes par régime (6 runs), sans graine imposée — la variabilité naturelle de l'exécution en temps réel (deux runs nominaux à réglages identiques donnant des trajectoires de WIP nettement différentes) s'est révélée suffisante pour produire des runs indépendants, sans avoir à localiser/modifier le réglage de graine d'AnyLogic. Fenêtre d'observation déterminée automatiquement par la livraison complète des commandes clientes de chaque run, pas fixée à l'avance. Analyse par test t de Welch (groupes indépendants) : **7 indicateurs sur 12 significatifs à 5 %**, dont le PI global (p < 0,0001, d de Cohen = −82). Protocole, suivi et script dans `PROTOCOLE_CAMPAGNE_STATISTIQUE.md` / `SUIVI_CAMPAGNE_STATISTIQUE.csv` / `analyze_campagne_statistique.py` ; résultats complets dans `RAPPORT_CAMPAGNE_STATISTIQUE.md`. Répond formellement à la réserve doctorale sur la robustesse statistique : l'écart nominal/perturbé n'est plus seulement plausible, il est démontré.
