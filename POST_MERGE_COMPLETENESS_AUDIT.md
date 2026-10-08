# Audit de complétude post-merge — master générique SCONTO-SVU

Audit statique uniquement. Aucun fichier `.alp`, Java ou JSON n'a été
modifié pendant cette passe. Aucune correction appliquée. E4/E5 non
implémentés. Aucune branche fusionnée.

**Objectif** : déterminer si `model/SCONTO_SVU_GENERIC_MASTER.alp`, à l'état
où EXP-0 le laisse, est suffisamment cohérent, complet et propre pour
devenir la base expérimentale d'une future campagne E4.

**Méthode et limite assumée** : audit par lecture ciblée (`grep`/lecture de
fonctions complètes), pas une relecture linéaire des ~56 000 lignes du
fichier — conforme à la pratique déjà établie sur ce dépôt. Certaines
sections ont fait l'objet d'une vérification exhaustive par lecture de
code (indiqué explicitement), d'autres d'une confirmation ciblée par motif
(indiqué explicitement), et une minorité reste à approfondir avant de
servir de preuve pour une décision de correction (indiqué explicitement).
Aucun statut « COMPLET »/« PASS » n'est utilisé sans preuve directe issue
du code ou d'un test runtime déjà documenté.

---

## 1. Contexte Git

- **Branche active** : `feature/experimentation-foundation`.
- **HEAD audité** : `fb450cd56c3305c846b94c060f469d48e00e3ab2`.
- **État Git** : arbre de travail propre sur les fichiers suivis (le seul
  diff observé avant cette passe était le bruit de resave AnyLogic habituel
  — tabulations/espaces ajoutés en fin de ligne sur trois balises XML sans
  aucun changement de logique — stashé sans être interprété comme un
  changement métier, conformément à la pratique déjà établie ; 5 entrées de
  stash cumulées depuis le début d'EXP-0, aucune n'a été poppée/droppée).
- **Diff réel `ba05f34..fb450cd`** : 7 commits.

| Commit | Modifie le `.alp` | Nature |
|---|---|---|
| `56f763f` feat(experiment): add deterministic seed and terminal-state foundation | Oui | A — fondation EXP-0 |
| `82f60d2` fix(experiment): tighten seed and terminal-state semantics | Oui | A — EXP-0.1 |
| `e94f5ec` fix(experiment): rephase business events from run start | Oui | A — EXP-0.2 |
| `a35a438` fix(experiment): decouple demand completion from execution state | Oui | A — EXP-0.3 |
| `c553da3` fix(experiment): reset failure state between runs | Oui | A — EXP-0.4 |
| `70c7b5e` docs(experiment): audit AnyLogic lifecycle for EXP-0.4 validation | Non | C — documentation seule |
| `fb450cd` docs(experiment): close EXP-0 after terminal runtime validation | Non | C — documentation seule |

**A/B/C demandé** :
- **A — modèle post-merge stable** : `integration/claude-generic-merge` @
  `ba05f348729ec607ae4716abf97db1f7b4a7cce6`, artefact
  `model/SCONTO_SVU_GENERIC_MASTER.alp`. Non modifié depuis (confirmé : la
  branche distante `integration/claude-generic-merge` reste à `ba05f34`
  tout au long d'EXP-0, revérifié à chaque commit).
- **B — fondation expérimentale EXP-0** : les 5 commits modifiant
  réellement le `.alp` ci-dessus (`56f763f`→`c553da3`), cumul
  `+356/-1` lignes sur le fichier modèle.
- **C — documentation** : `EXPERIMENTATION_FOUNDATION.md` (les 2 derniers
  commits) et ce document.

**Dernier commit ayant réellement modifié le `.alp`** : `c553da3`, confirmé.

---

## 2. Architecture réelle (inventaire des composants)

*Profondeur : vérification exhaustive par grep sur les mécanismes de
population AnyLogic (`add_*`/`remove_*`, `<EmbeddedObject>`), et par
recherche de chaque nom de classe candidat comme `ClassName`/`<Name>` XML.*

### 2.1. Populations et objets répliqués réellement gérés par AnyLogic

| Nom | Mécanisme | Classe d'agent | Créé/détruit par |
|---|---|---|---|
| `postes` | Population (`add_postes`/`remove_postes`) | `PosteGenericAgent` | `clearScenarioBeforeJsonLoad()` uniquement (jamais par `demarrerSimulation()`) |
| `opAgents` | Population (`add_opAgents`/`remove_opAgents`) | `OperationalAgent` | Idem `postes`, même fonction, même section du code |
| `tacticals` | Population (`add_tacticals`/`remove_tacticals`) | `TacticalAgent` | Recréée à **chaque** `demarrerSimulation()` |
| `supervisorsMacro` | Population (`add_supervisorsMacro`/`remove_supervisorsMacro`) | `CoordinatorAgent` | Recréée à **chaque** `demarrerSimulation()` |
| `fluxEntites` | Population (`add_fluxEntites`/`remove_fluxEntites`) | `FluxEntity` | Cycle normal du flux (créées/détruites en continu pendant le run) |
| `stationsAnimation` | Population (`remove_stationsAnimation`, recréées via `creerStationsAnimation()`) | (objet d'animation) | Recréée à chaque `demarrerSimulation()` |
| `commandes` | **Objet répliqué** (`<EmbeddedObject ReplicationFlag="true">`, `add_commandes()`, **aucun `remove_commandes()` trouvé**) | `CommandeAgent` | Jamais détruit individuellement ni en masse par `demarrerSimulation()` : **la liste des commandes s'accumule pour toute la durée de vie de `Main`**, y compris les `REAPPRO_*`. Le tri ouvert/clos, client/réappro se fait exclusivement par filtrage en lecture (`commandeEstTerminale()`, `estOrdreStockAutonome()`), jamais par suppression. Cohérent avec Cycle C (§14 EXPERIMENTATION_FOUNDATION.md) : sur une nouvelle instance de modèle, cette accumulation repart de zéro par construction. |

**Singleton** : `strategic` (instance unique de `StrategicAgent`, champ
direct sur `Main`, pas une population).

### 2.2. Classes réellement présentes comme `ActiveObjectClass` (agents AnyLogic)

Confirmé par recherche de `ClassName`/`<Name>` XML pour chaque candidat :
`CommandeAgent`, `PosteGenericAgent`, `TacticalAgent`, `CoordinatorAgent`,
`OperationalAgent`, `StrategicAgent`, `BlackboardAgent`, `FluxEntity`.
**Huit classes d'agent au total.**

### 2.3. Classes attendues par l'énoncé de cette passe mais absentes du modèle

| Nom attendu | Résultat | Réalité constatée |
|---|---|---|
| `ProduitAgent` | **Absent** (0 occurrence comme classe) | Les produits sont des objets `Produit` (classe Java simple, `implements Serializable`, non-Agent) tenus dans `produitRegistry: LinkedHashMap<String,Produit>`, et leur configuration provient de `ScenarioFlux` (classe Java simple également) tenue dans `listeProduits`/`catalogueProduits`. Aucun agent AnyLogic par produit : le multiproduit est porté par des structures indexées par identifiant produit (String), pas par une population d'agents. |
| `OperationalPilotAgent` / `OperationalExecutionAgent` | **Absents** (0 occurrence) | Un seul `OperationalAgent` existe. Les listes `agentsSuperviseurs`/`agentsExecution` vues dans le code sont des **vues dérivées/filtrées** de la population unique `opAgents`, pas des populations ou classes distinctes. La distinction pilotage/exécution, si elle existe fonctionnellement, est portée par un champ de rôle sur `OperationalAgent`, pas par deux classes séparées. |
| `SupervisorAgent` (legacy) | **Absent** (0 occurrence) | Aucune trace d'une classe `SupervisorAgent` distincte, historique ou active. |

### 2.4. Classes Java simples (`<JavaClass>`, non-Agent) confirmées

`SimpleJsonWriter`, `SimpleJsonParser`, `TypePoste`, `LoiTemps`,
`RegleAiguillage`, `ScenarioFlux`, `LigneNomenclature`, `ReceptionAttendue`,
`FicheMatiere`, `KPIBundle`, `FuzzyGradeSet`, `MetriqueN3`, `AERMessage`,
`ActeurSC`, `FluxLog`, `TraceData`, `MicroResponsabilite`, `MachineSim`
(18 classes). `Produit` et `ActionMetierDifferee` sont des classes Java
définies inline dans le code additionnel de `Main` (pas des `<JavaClass>`
séparées, d'où leur absence de cette liste malgré leur existence réelle).

### 2.5. Rôle, réutilisation et reset — résumé par famille

| Famille | Rôle actuel | Legacy ou active | Reset par run | Export |
|---|---|---|---|---|
| `Main` | Orchestrateur unique, porte `demarrerSimulation()`/`arreterSimulation()`, toute la config scénario | Active | N/A (recréé en Cycle C) | Point d'entrée de tous les exports |
| `CommandeAgent` (`commandes`) | Commandes clientes ET ordres `REAPPRO_*` (même classe, distingués par préfixe `idCommande`) | Active | Jamais vidée, accumule (voir §2.1) | Oui (Excel/TTL) |
| `Produit`/`ScenarioFlux` (non-Agent) | Catalogue produit, nomenclature, politique de stock | Active | `listeProduits.clear()` en tête de rechargement scénario | Oui |
| `PosteGenericAgent` (`postes`) | Micro-activité (poste), MTBF/MTTR, files/traitement | Active | **Partiellement** : état runtime de panne reseté depuis EXP-0.4 ; population elle-même jamais recréée par run | Oui |
| `TacticalAgent` (`tacticals`) | Arbitrage tactique par macro-processus SCOR | Active | Recréée intégralement chaque run | Oui (dashboard) |
| `CoordinatorAgent` (`supervisorsMacro`) | Coordination par macro-processus, ordonnancement (`carnetCommandesMTO`, voir §14) | Partiellement legacy (voir §14) | Recréée intégralement chaque run | Oui (dashboard) |
| `OperationalAgent` (`opAgents`) | Agent opérationnel par poste/groupe, détection goulot/panne, escalade AER | Active | **Non resetée** (population jamais recréée par run ; `etatHolon` etc. non remis à zéro — EXP-0.4V, hors périmètre de correction ici) | Oui (dashboard, AER) |
| `StrategicAgent` (`strategic`) | PI/SCOR global, décisions stratégiques | Active | Partiellement resetée en tête de `demarrerSimulation()` (voir Bloc B.1) | Oui |
| `BlackboardAgent` (`board`) | Canal AER partagé, logs, KPI bundles (`kpiGlobal`, `kpiZener`), compteurs d'export | Active | `board.reset()` appelé en tête de `demarrerSimulation()` | Central à tous les exports |
| `FluxEntity` (`fluxEntites`) | Jeton physique/visuel circulant sur les postes | Active | Cycle de vie normal du flux | Non (interne) |

---

## 3. Audit fonctionnel — MTS / MTO / ETO

*Profondeur : lecture complète des fonctions `analyserStockCommandeOrchestree()`
et `analyserMatiereCommandeOrchestree()` (chemin d'entrée canonique
commun), recherche exhaustive de `"ETO"` dans tout le fichier.*

**Chemin commande → clôture, retracé sans hypothèse :**

```
genererCommande() [garde peutGenererNouvelleCommande()]
  → analyserStockCommandeOrchestree(cmd)
      si cmd.typeCommande == "MTS" :
        si stock fini suffisant → livraison directe (planifierAvecEchelle LIVRAISON_DIRECTE)
        sinon → attente + verifierPolitiqueStockProduit() + replanifie ANALYSE_STOCK (30s)
      sinon (MTO ou ETO, code IDENTIQUE pour les deux) :
        → analyserMatiereCommandeOrchestree(cmd)
            scénario/nomenclature invalides → BLOQUE_CONFIG / BLOQUE_NOMENCLATURE (terminal)
            matière suffisante → production directe
            matière insuffisante → déclencherApprovisionnementCommande() puis reprise via FINALISER_APPROVISIONNEMENT
  → Deliver (chemin commun, générique)
  → réception client / clôture via finDeParcours(), tPromise (Bloc C)
  → SERVIE / EN_RETARD / REFUSEE / BLOQUE_*
```

**Constat principal, non intentionnel s'il n'est pas documenté ailleurs
comme un choix délibéré** : **MTO et ETO partagent exactement le même code
de traitement de commande** dès `analyserStockCommandeOrchestree()` — il
n'existe **aucune branche fonctionnelle propre à ETO** dans le pipeline de
traitement de commande. La distinction ETO n'existe qu'à trois autres
niveaux, tous confirmés par grep : un indicateur `isETO`/`isMTO` (booléens
sur objet de configuration), une classification SCOR de niveau (P/S/M/D
"3" pour ETO contre "2" pour MTO, via `codeGroupeL3()`/`extraireNiveau()`),
et des groupes tactiques/coordinateurs dédiés dans la table de mapping SCOR
(`{"CA-sS3","sS","sS3","ETO"}`, etc.), plus une constante de délai
(`3600.0` si `"ETO"`). **Ce n'est donc pas une absence de généricité
(aucun hardcoding ZENER/DataCo dans cette logique), mais une simplification
fonctionnelle réelle** : le modèle ne représente pas de phase
d'ingénierie/personnalisation propre à ETO avant production — à documenter
explicitement comme une limitation si ETO doit être un facteur E4
distinctif, faute de quoi une campagne variant MTO vs ETO produirait des
résultats identiques sur le chemin de traitement, seule la classification
SCOR et le coût de délai théorique différeraient.

**Aucun chemin mort identifié** dans les trois branches MTS/MTO/ETO
elles-mêmes (au-delà du mécanisme d'ordonnancement dédié inactif, voir §14
— qui n'est pas dans ce chemin commande normal).

**Références ZENER dans une logique censée être générique** : deux chaînes
de log/popup en dur dans `analyserStockCommandeOrchestree()` (« ZENER
vérifie le magasin... », « ZENER ne dispose pas... ») — texte affiché à
l'utilisateur, sans effet sur la logique métier elle-même (voir §13).

---

## 4. Audit fonctionnel — Stock / réapprovisionnement autonome

*Profondeur : relecture ciblée des fonctions déjà auditées lors d'EXP-0.1
(§4bis d'`EXPERIMENTATION_FOUNDATION.md`), complétée par grep sur les
doublons et l'état terminal.*

- `estOrdreStockAutonome(CommandeAgent)` (utilisée par le terminal EXP-0 et
  la politique de stock) et `estOrdreReappro(CommandeAgent)` (fonction plus
  ancienne) **coexistent toujours**, avec le même filtre
  (`idCommande.startsWith("REAPPRO_")`) — duplication déjà identifiée en
  EXP-0.1, toujours présente, sans divergence de comportement constatée
  (les deux fonctions produisent le même résultat sur le même prédicat).
  Dette technique, pas un bug.
- Un ordre `REAPPRO_*` n'est **jamais compté comme commande cliente** :
  `nombreCommandesOuvertes()` (Bloc C.4) exclut explicitement
  `estOrdreStockAutonome(cmd)` avant de compter — confirmé par lecture
  directe du code (déjà vérifié en EXP-0.1, revérifié ici, inchangé).
- Un ordre `REAPPRO_*` **peut empêcher la terminalité** tant qu'il reste
  ouvert, via `nombreReapprovisionnementsOuverts() > 0` dans
  `etatTerminalOperationnelAtteint()` — confirmé, comportement voulu et
  vérifié en runtime sur Run 01 (`openReplenishments=0` à la clôture).
- Un ordre `REAPPRO_*` passe par le **même chemin Source → Make → clôture**
  que les commandes MTO/ETO : `declencherProductionAutonome()` appelle
  directement `analyserMatiereCommandeOrchestree()`, le même point d'entrée
  canonique que pour une commande cliente MTO/ETO (déjà documenté dans le
  commentaire E.2-FIX du code, confirmé en §3 ci-dessus).
- **Prévention des doublons** : la garde de réentrance étendue en E.2-FIX
  (statuts `EN_LIVRAISON`/`EN_APPROVISIONNEMENT`/`PRODUCTION_PLANIFIEE`/
  `EN_COURS` exclus d'une réanalyse) s'applique identiquement aux
  `REAPPRO_*` et aux commandes clientes, car elle est dans le point d'entrée
  commun `analyserStockCommandeOrchestree()`.

---

## 5. Audit fonctionnel — Terminalité

*Profondeur : exhaustive, ces fonctions ont été lues intégralement à
plusieurs reprises pendant EXP-0.1/0.3/0.4 ; revérifiées ici pour confirmer
l'absence de régression et l'absence de prédicat concurrent.*

Fonctions réellement présentes, une seule définition de chaque concept :

- `commandeEstTerminale(cmd)` — prédicat canonique unique
  (`SERVIE`/`EN_RETARD`/`REFUSEE`/`BLOQUE_*`), réutilisé par
  `nombreCommandesOuvertes()`, `nombreReapprovisionnementsOuverts()`,
  `analyserStockCommandeOrchestree()` (garde de réentrance), et les
  exports. **Aucun second prédicat de terminalité de commande trouvé.**
- `nombreCommandesOuvertes()` — commandes clientes ouvertes uniquement
  (REAPPRO exclu).
- `nombreReapprovisionnementsOuverts()` — REAPPRO ouverts uniquement.
- `nombreEntitesEnTraitementPostes()` — occupations `queue`/`delay`/
  `lotEnCours` sur `postes` (documenté comme occupations, pas garanti
  agents uniques — EXP-0.1, §7bis).
- `nombreActionsMetierDiffereesPertinentes()` — actions différées hors
  `GENERER_COMMANDE`/`ANIM_RETOUR_VEHICULE`.
- `generationDemandeTerminee()` — depuis EXP-0.3, dépend uniquement de
  `modePilotageParCommande`/`limiterNombreCommandes`/quota, plus de
  `modeExecution`.
- `etatTerminalOperationnelAtteint()` — ET logique des cinq fonctions
  ci-dessus. **Une seule définition, aucun concurrent trouvé.**

**Invariants du Run 01 confirmés runtime** (pas seulement statiquement) :
`openCustomerOrders=0`, `openReplenishments=0`, `entitiesInProcessAtPosts=0`,
`pendingBusinessActions=0` → `terminalReached=OUI`,
`demandGenerationFinished=OUI`, `terminalDiagnosticText="Etat terminal
operationnel atteint."` — cohérent avec le code relu ci-dessus.

**Cas pouvant produire un faux terminal ou une impossibilité de
terminer**, identifiés par lecture (aucun n'a été observé en runtime,
raisonnement statique) :
- Une campagne en **mode continu** (`!modePilotageParCommande` ou
  `!limiterNombreCommandes`) ne peut, par construction, **jamais** atteindre
  `generationDemandeTerminee()==true` — comportement voulu (documenté
  EXP-0.3, cas D), mais à garder en tête pour un futur harness E4 qui
  s'attendrait à un run borné.
- `nombreEntitesEnTraitementPostes()` compte des **occupations**, pas des
  entités garanties uniques (EXP-0.1, §7bis) : si un même poste pouvait un
  jour présenter une entité simultanément dans deux des trois structures
  (`queue`/`delay`/`lotEnCours`), le compteur resterait non nul sans qu'il
  y ait réellement plusieurs entités distinctes bloquées — situation non
  observée mais dont l'exclusion n'est pas formellement prouvée dans cette
  passe (audit ciblé, pas une preuve exhaustive de non-chevauchement).

---

## 6. Audit RNG / EXP-0

*Profondeur : exhaustive, grep sur l'ensemble du fichier pour toute source
de hasard alternative.*

- `Math.random` : **0 occurrence**.
- `new Random(`/`new java.util.Random(` : **1 seule occurrence**, dans la
  configuration native `<SimulationExperiment><CustomGeneratorCode>new
  Random()</CustomGeneratorCode>` — fallback natif AnyLogic inchangé, actif
  uniquement si `seedExperiment=-1` (comportement déjà documenté §2 de
  `EXPERIMENTATION_FOUNDATION.md`).
- `getDefaultRandomGenerator()` : 16 appels, tous vers le même générateur
  unique de l'expérience (par définition de cette API AnyLogic — il n'existe
  qu'un seul générateur par défaut par expérience).
- Distributions `Utilities.uniform(...)`/`Utilities.triangular(...)`
  utilisées dans `LoiTemps.echantillon(Random rng)` : le paramètre `rng`
  est systématiquement injecté par l'appelant depuis
  `getDefaultRandomGenerator()` (confirmé par lecture des sites d'appel
  antérieurs, EXP-0/EXP-0.1) — **aucun second flux aléatoire** créé
  localement dans ces fonctions.
- **Aucune source aléatoire supplémentaire détectée** au-delà de celles déjà
  inventoriées en EXP-0 (§1 d'`EXPERIMENTATION_FOUNDATION.md`) : traitement
  des postes (`LoiTemps.echantillon`), pannes (`gererPanne()`,
  exponentielle MTBF/MTTR), et les tirages de quantité/routage déjà
  documentés.
- Intégration EXP-0 confirmée toujours cohérente : `seedExperiment`/
  `seedExperimentEffective`/`seedExperimentSource` appliqués en tête de
  `demarrerSimulation()`, avant `synchroniserListeProduits()`/
  `validerConfig()` ; précision JSON en `String`/`Long.parseLong` (EXP-0.1) ;
  rephasage des 8 événements métier (EXP-0.2) ; reset panne avant
  `modeExecution=true` et avant `verifierPanne.restart()` (EXP-0.4) ; cycle
  `FINISHED` documenté et confirmé runtime comme Cycle C (EXP-0.4V/clôture).

---

## 7. Audit des états run-scoped

*Profondeur : exhaustive pour `PosteGenericAgent`/`OperationalAgent`
(travail direct d'EXP-0.4/EXP-0.4V) ; ciblée pour le reste.*

| État | Agent/porteur | Classe | Reset par run ? |
|---|---|---|---|
| `enPanne`, `tProchainePanne`, `tFinPanne`, `nbPannes`, `tempsArretCumule`, `tDebutPanneCourante` | `PosteGenericAgent` | RUN-SCOPED | **Oui, depuis EXP-0.4** |
| `mtbfHeures`, `mttrHeures` | `PosteGenericAgent` | CONFIGURATION | N/A (rechargé au scénario, jamais réécrit ailleurs) |
| `etatHolon`, `tEntreeEtatCourant`, `nbGoulotsDetectes`, `nbAlertesEmises` | `OperationalAgent` | RUN-SCOPED (partagé avec détection goulot, pas exclusivement panne) | **Non** — identifié, explicitement hors périmètre EXP-0.4, reporté au choix d'architecture E4 |
| `runFinalise` | `Main` | RUN-SCOPED | Oui (`= false` en tête de `demarrerSimulation()`) |
| `commandesGenereesDepuisDemarrage`, `messageLimiteCommandesDejaAffiche` | `Main` | RUN-SCOPED | Oui |
| `pointCommandeProduit`, `quantiteEconomiqueProduit`, `productionAutonomeEnCours`, `seqCommandeAutonome`, `dernierCalculBesoinNet`, `quantiteEconomiqueParProduit` | `Main` | RUN-SCOPED | Oui (`reinitialiserPolitiquesStockPourRun()`) |
| `FicheMatiere.pointCommande/quantiteEconomique/receptionsAttendues/derniers*` | `FicheMatiere` (non-Agent, tenu dans une liste `Main`) | RUN-SCOPED | Oui (même fonction que ci-dessus) |
| `commandes` (accumulation complète, y compris REAPPRO) | `Main`/population | CUMULATIF VOLONTAIRE (pour la durée du run) | Non par construction — voir §2.1 ; sans impact en Cycle C |
| `nbTerminesParProduit` | `Main` | INCERTAIN — voir §14 (jamais lu, clé mélangée entre deux domaines différents) | Non resetée explicitement (mais jamais lue non plus) |
| `strategic.piGlobalCourant`, `donneesRLPresentesPrecedent`, etc. (Bloc B.1) | `StrategicAgent` (singleton) | RUN-SCOPED | Oui, liste explicite en tête de `demarrerSimulation()` |
| `carnetCommandesMTO` | `CoordinatorAgent` | UI/DIAGNOSTIC (jamais peuplée, voir §14) | Non applicable (toujours vide) |
| `historiqueDashboard`, `dernierTempsCaptureHistoriqueDashboard` | `Main` | UI/DIAGNOSTIC | Oui (`clear()`/`=-1.0`) |
| `aboxRunId`, `dernierFichierABox` | `Main` | RUN-SCOPED | Oui (`=""`) |

**Pour le choix d'architecture E4 (rappel, déjà conclu en EXP-0.4V)** :
sous Cycle C (confirmé runtime), toute cette table est sans impact — chaque
run repart sur un `Main` neuf. Si une future implémentation E4 choisissait
malgré tout une boucle scriptée réutilisant les mêmes agents, les lignes
« Non » de cette table (`etatHolon` et dérivés) devraient être auditées et
resetées avant la campagne.

---

## 8. Audit SCOR / KPI / PI

*Profondeur : ciblée — structure et points d'entrée du pipeline confirmés
par grep, pas une relecture ligne à ligne de `calculerPIGlobal()`.*

Pipeline confirmé : `traces`/événements → `MetriqueN3` (valeur brute,
unité, poids, niveau SCOR, grades flous via `FuzzyGradeSet`) →
agrégation par attribut (`scoreRL`, `scoreRS`, `scoreAG`, `scoreCO`,
`scoreAM`, calculés via `agregerN3(...)`) → `calculerPIGlobal()`
(StrategicAgent) → PI 0..10 avec cible (`ciblePIGlobal`).

- **Phase d'amorçage** confirmée existante (Bloc B.2, déjà documenté dans
  `MERGE_PROGRESS.md` et revérifié : `strategic.piGlobalCourant` forcé à
  `ciblePIGlobal` tant que le périmètre PI n'est pas complet — correctif
  C.14.45/B.2-FIX déjà en place, pas de régression détectée).
- **Codes SCOR vs proxies** : les proxies non officiels sont explicitement
  préfixés `PROXY.` (ex. `PROXY.AM.DISPONIBILITE_MACHINE`, déjà documenté
  avec sa justification textuelle dans le code lui-même
  — `"Proxy explicite, hors référentiel SCOR normatif..."`). Aucune
  confusion trouvée entre un code SCOR officiel et un proxy présenté comme
  tel.
- **OEE** : `oee() = oeeDisponibilite() * oeePerformance() * oeeQualite()`,
  `oeeDisponibilite() → calculerDisponibiliteMachinesOEE()` (utilise l'état
  runtime de panne, désormais reseté par run depuis EXP-0.4 — §7 ci-dessus
  et EXP-0.4 §13.5). `calculerDisponibiliteMachinesMoyenne()` (AM.3.9,
  proxy) est une fonction **distincte**, fondée uniquement sur
  `MachineSim.disponibiliteTheorique()` (formule MTBF/(MTBF+MTTR) pure,
  aucun état runtime) — **deux fonctions de « disponibilité » coexistent
  avec des sources différentes**, à ne pas confondre lors d'une lecture
  rapide du dashboard (risque de confusion documentaire, pas un bug de
  calcul).
- **Ordres stock exclus des métriques clientes** : confirmé — le
  commentaire C.14.60/C.14.68 documente explicitement l'exclusion des
  REAPPRO du Takt Time et des compteurs de commandes (§3/§4 ci-dessus).
- **`board.kpiZener` sans garde nulle à plusieurs sites d'appel** (lignes
  citées en §13) : si l'acteur `ENTREPRISE_FOCALE` n'est pas résolu pour un
  scénario donné, ces appels (`board.kpiZener.avgCycleTime()` etc., export
  ABox) risquent un `NullPointerException` non anticipé par un `try/catch`
  local — **non vérifié en runtime dans cette passe** (aucun run n'a
  exercé un scénario sans entreprise focale), signalé comme risque
  potentiel, pas comme bug confirmé.
- **Unités 0..1 vs 0..10 vs 0..100** : cohabitent par construction du
  domaine (scores SCOR normalisés 0..10, ratios OEE/disponibilité 0..1,
  pourcentages d'affichage ×100 explicites dans le formatage) — aucune
  confusion d'unité détectée dans les points vérifiés, mais **pas d'audit
  exhaustif de toutes les conversions** dans cette passe (voir §11 pour la
  même réserve côté VSM).

---

## 9. Audit AER / architecture multi-agents

*Profondeur : ciblée — existence et chaînage des fonctions confirmés,
pas une relecture exhaustive de chaque message AER.*

Chaîne confirmée : `StrategicAgent` → `TacticalAgent` (arbitrage par
macro-processus) → `CoordinatorAgent` (par macro-processus SCOR) →
`OperationalAgent` (par poste/groupe, un seul niveau — pas de distinction
Pilot/Execution en classes séparées, voir §2.3). Canal partagé :
`BlackboardAgent.journaliserAER()`/`publierAlerte()`, structure
`AERMessage` (POJO, types `REPORT`/etc.).

- **Aucun `SupervisorAgent` legacy actif ou résiduel trouvé.**
- **Aucun agent déclaré mais jamais appelé** parmi les 8 classes d'agent
  confirmées (§2.2) — toutes ont des populations non vides dans un run
  normal et des sites d'appel actifs.
- **`realignerArchitectureAgents()`** existe et est appelée à chaque
  `demarrerSimulation()` (§2.1) : son rôle exact (réalignement de quoi vers
  quoi) n'a pas été retracé ligne à ligne dans cette passe — **à
  approfondir avant de garantir qu'elle ne masque pas une incohérence
  d'architecture**, cette fonction n'ayant été vue que par son point
  d'appel, pas par son corps complet.
- **Collision d'identité** : non auditée exhaustivement dans cette passe
  (nécessiterait de tracer la génération de tous les identifiants d'agents
  AER — hors du temps disponible pour cette passe).

---

## 10. Audit SCOR N1-N4

*Profondeur : ciblée.*

`niveauSCOR` (champ sur `MetriqueN3`, extrait de `codeOfficielSCOR` via
`extraireNiveau()`) et l'export ABox assertent explicitement
`core:hasSCORLevel` (niveaux "2" et "3" vus dans le code). Le mapping
MTS/MTO/ETO → niveau 1/2/3 est confirmé au §3. Les groupes tactiques/
coordinateurs (`CA-sS3`, `CA-sM3`, `CA-sD3` pour ETO, etc.) sont
paramétriques par macro-processus SCOR (`sS`/`sM`/`sD`), pas câblés en dur
sur un scénario particulier. **Aucune référence hardcodée à ZENER trouvée
dans cette table de mapping SCOR elle-même** (contrairement aux chaînes de
log/popup du §3). Le niveau 4 (micro-activités) n'a pas été spécifiquement
recherché comme distinct dans cette passe — **à vérifier plus précisément**
si une granularité N4 explicite est attendue au-delà des micro-activités
déjà couvertes par `PosteGenericAgent.codeSCOR`.

---

## 11. Audit VSM / mesures temporelles

*Profondeur : ciblée — indicateurs identifiés dans l'export ABox (§9683-9714
du fichier), pas une vérification exhaustive de chaque conversion
d'unité dans le code de calcul.*

Indicateurs confirmés existants et exportés : `order_processing_time`,
`order_waiting_time`, `order_fulfillment_lead_time` (contexte commande
cliente uniquement, `CUSTOMER_ORDER_CMD_ONLY`), et un second jeu
(`zener_process_time`, `zener_waiting_time`, `zener_estimated_pce`, contexte
`ZENER_ACT_4_ONLY`, voir §13) pour l'entreprise focale. Toutes les valeurs
temporelles vues sont en secondes de simulation (`"s"` explicite dans
l'export), cohérent avec les fonctions internes déjà revues ailleurs
(`avgLeadTime()/60.0` pour la conversion en minutes à l'affichage,
documentée A.4-FIX-1). **Aucune double conversion détectée dans les points
vérifiés.** Cette passe **n'a pas vérifié exhaustivement** la cohérence
d'unité sur l'ensemble des indicateurs VSM (WIP, débit, temps de cycle
détaillés par poste) — audit ciblé sur les points d'export ABox
uniquement, pas sur le calcul interne complet.

---

## 12. Audit des exports

*Profondeur : ciblée pour les deux anomalies déjà connues (revérifiées
avec leurs lignes exactes), plus une découverte nouvelle dans cette passe.*

Exports actifs confirmés : ABox/TTL (`exporterABoxRuntimeTTL`, 3 sites
d'appel : clôture de commande ×2, `RUN_FINALIZED`), Excel
(`exporterToutesLesTablesExcel`, appelée depuis `finaliserRunEtExporter()`),
CSV (`supervisor.exporterCSV(...)`, bouton dédié), Dashboard/historique
(`historiqueDashboard`), logs (`board.logEvent`).

**A. Anomalie déjà connue — graine non reflétée dans le manifeste legacy**
(reconfirmée) : ligne 2491 (`"graineAleatoire", "NON_ACCESSIBLE_DANS_MAIN"`)
et ligne 9585 (`run:randomSeed = "NON_ACCESSIBLE_DANS_MAIN"`), alors que
`run:experimentSeed`/`experimentSeedEffective`/`experimentSeedSource`
(EXP-0) exportent désormais la vraie valeur dans le même run. **Non
corrigé.**

**B. Anomalie déjà connue — nom d'artefact obsolète** (reconfirmée) : ligne
9600, `run:modelArtifact = "SCONTO_SVU_FINAL_VSM_FIX_CANDIDATE.alp"`, alors
que l'artefact réel est `model/SCONTO_SVU_GENERIC_MASTER.alp`. **Non
corrigé.**

**C. Nouvelle observation — double flux KPI nommé « ZENER »** dans l'export
ABox lui-même (`zener_process_time`, `zener_waiting_time`,
`zener_estimated_pce`, contexte `ZENER_ACT_4_ONLY`) : la **computation**
est générique (résout l'acteur par rôle `ENTREPRISE_FOCALE`, pas par nom),
mais les **identifiants de métrique et labels exportés** sont
nommés/brandés ZENER — voir §13 pour la classification complète.

**Autres métadonnées vérifiées et jugées cohérentes** : `modelName =
"SCONTO_VSM_Generic"` et le titre d'expérience `"SCONTO_VSM_Generic :
Simulation"` sont internes, génériques dans leur formulation, et mutuellement
cohérents — pas une anomalie, juste une convention de nommage différente
du nom de fichier `.alp` actuel.

**Sources potentiellement divergentes pour une même information** :
`calculerDisponibiliteMachinesOEE()` vs `calculerDisponibiliteMachinesMoyenne()`
(§8) — deux définitions de « disponibilité » avec des sources différentes,
exportées séparément (l'une dans l'OEE, l'autre en AM.3.9), risque de
confusion si les deux apparaissent côte à côte sans étiquetage clair de
leur source respective.

---

## 13. Audit généricité

*Profondeur : exhaustive sur la recherche des motifs demandés
(`ZENER`/`DataCo`/`SCONTO_SVU_FINAL`/`CANDIDATE`), classification manuelle
de chaque occurrence trouvée en dehors des commentaires.*

- **DataCo** (`Prophet`, `Recalibrator`, `AutoCommande`,
  `genererCommandeDataCoPourDate`, `recalibrerPrevisionPourDate`,
  `DATACO_SPORTS/CLOTHING/ELECTRONICS`) : **0 occurrence confirmée** dans
  le master générique. Séparation DataCo/générique intacte.
- **`SCONTO_SVU_FINAL`/`CANDIDATE`** (anciens noms de fichier) : trouvés
  uniquement dans le champ d'export legacy `run:modelArtifact` (§12.B) —
  pas dans la logique métier.
- **ZENER**, 56 occurrences hors commentaires, classées :

| Occurrence | Classe | Justification |
|---|---|---|
| `estScenarioCasTest()` : `n.contains("ZENER CAS 1"/"2"/"3")` | **A — légitime** | Compare le NOM du scénario réellement chargé (dépendant du JSON), pas une constante métier indépendante du scénario. |
| `acteurCourtF()` : `if (nu.contains("ZENER")) return "ZENER";` (+ GPL/BOUTEILLE/ACCESSOIRE) | **B — acceptable mais à nettoyer** | Fonction d'affichage uniquement (préfixe court), documentée dans son propre commentaire (C14.28) comme un raccourci pour les acteurs connus du scénario ZENER, **avec repli générique explicite** (troncature) pour tout acteur non reconnu — ne casse pas la généricité fonctionnelle, mais un moteur pleinement générique n'aurait idéalement pas ce mapping en dur dans le cœur (candidat à un déplacement vers une config JSON de libellés). |
| Chaînes de log/popup (« ZENER vérifie... », « ZENER SA Togo », « ZENER SA Togo / AO-sD1.12 », etc.) | **B — acceptable mais à nettoyer** | Texte narratif affiché à l'utilisateur uniquement, sans effet sur la logique. Resterait affiché tel quel pour un scénario non-ZENER, ce qui est trompeur pour l'utilisateur final mais n'altère aucun calcul. |
| `board.kpiZener` (champ), `zener_process_time`/`zener_waiting_time`/`zener_estimated_pce`, `ZENER_ACT_4_ONLY`, `ctxZener` | **C — hardcoding de nommage dans le schéma d'export** | La *computation* résout l'entreprise focale par rôle (générique), mais l'identifiant de champ (`kpiZener`), les clés de métrique exportées et le libellé de scope (`ZENER_ACT_4_ONLY`) sont eux-mêmes nommés ZENER en dur dans le schéma ABox — un consommateur externe de l'export verrait "ZENER Process Time" même pour un scénario dont l'entreprise focale ne s'appelle pas ZENER. C'est le seul point classé C (véritable hardcoding empêchant une lecture propre de l'export pour un scénario non-ZENER), mais il **n'empêche pas** le calcul lui-même d'être générique — la correction, si retenue, serait un renommage de schéma, pas une réécriture de logique. |

**Conclusion généricité** : aucun hardcoding de catégorie C n'a été trouvé
dans la **logique métier** ; le seul C confirmé est un **nommage de champ
d'export**. Cohérent avec l'interdiction du `CLAUDE.md` du dépôt (ne pas
injecter de connaissance métier DataCo/ZENER codée dans le moteur) — cette
règle est respectée pour la logique, avec une réserve documentée sur le
nommage des exports.

---

## 14. Audit code mort / doublons / legacy

*Profondeur : ciblée sur les candidats déjà connus (confirmation) et sur
un candidat nouvellement découvert (`nbTerminesParProduit`) ; pas un
balayage exhaustif de toutes les fonctions du fichier.*

- **`carnetCommandesMTO`/`ordonnancerProduction()`** (déjà documenté dans
  `MERGE_PROGRESS.md`, Bloc E.1/E.2-FIX) : **reconfirmé** dans cette passe
  — 12 occurrences, **aucun `.add(` trouvé nulle part**, uniquement des
  lectures (`size()`, `isEmpty()`, `get(0)`, `remove(0)`, tri, comparaison
  de capacité à la ligne 51512). Ordonnanceur dédié réellement inerte,
  confirmé code mort fonctionnel (jamais exécuté utilement), cohérent avec
  la clôture déjà actée de ce point dans le master post-merge — **pas une
  régression nouvelle**, juste reconfirmé.
- **`nbTerminesParProduit`** (nouvelle observation de cette passe) :
  `HashMap<String,Long>`, alimentée à **deux endroits avec des clés de
  domaines différents** — ligne 6252, clé = `cmd.typeCommande` (donc
  `"MTS"`/`"MTO"`/`"ETO"`) ; ligne 13785, clé = `e.typeProduit` (identifiant
  produit réel). **Jamais lue** (`0` occurrence de `.get(`/`.keySet(`/
  `.entrySet(` sur ce champ dans tout le fichier). Deux domaines de clés
  incompatibles alimentent silencieusement la même map — sans impact
  aujourd'hui puisque la map n'est jamais consommée, mais un piège si elle
  était un jour exportée telle quelle en pensant obtenir un « nombre
  d'unités terminées par produit ».
- **Duplication `estOrdreStockAutonome`/`estOrdreReappro`** : reconfirmée
  (§4), dette technique sans impact fonctionnel.
- **Vérification des « appels AnyLogic implicites »** demandée par
  l'énoncé : les fonctions liées à des `ActionCode` de bouton
  (`demarrerSimulation`, `arreterSimulation`, export CSV, etc.) et aux
  `Body` d'événements (`Timeout`) ont été prises en compte comme des sites
  d'appel réels dans cette passe (pas traitées comme « jamais appelées »
  simplement parce qu'aucun appel Java direct n'existe) — cohérent avec la
  méthode déjà appliquée pendant EXP-0.2 pour l'inventaire des 22
  événements cycliques.
- **Pas de balayage exhaustif supplémentaire** des fonctions
  jamais-appelées au-delà de ces candidats connus/découverts dans cette
  passe — un balayage complet (comparaison de chaque nom de fonction
  déclarée contre ses sites d'appel dans tout le fichier) n'a pas été
  effectué, faute de temps dans le format de cette passe ; à prévoir comme
  point de suivi si une exhaustivité totale est requise avant E4.

---

## 15. Audit des événements périodiques

*Réutilise intégralement l'inventaire déjà produit et documenté en EXP-0.2
(`EXPERIMENTATION_FOUNDATION.md`, §11.3) : 22 événements cycliques métier
recensés, classés rephasés/non-rephasés avec justification pour chacun.
Revérifié dans cette passe : aucun nouvel événement cyclique n'a été
ajouté au modèle depuis EXP-0.2 (aucun commit entre `e94f5ec` et `fb450cd`
ne touche de nouvelle définition `<Function Name="on-timeout">` ou
équivalent — seuls des ajouts de fonctions Main déjà revus en §2/§5/§7 ont
été faits). Le tableau complet (propriétaire, période, activation, effet
métier, rephasé ou non, raison) n'est donc pas reproduit ici : se référer
à `EXPERIMENTATION_FOUNDATION.md` §11.3, toujours à jour.*

---

## 16. Audit des actions différées

*Profondeur : ciblée, structure déjà confirmée en EXP-0 (§5
d'`EXPERIMENTATION_FOUNDATION.md`), revérifiée ici sans nouvelle
découverte.*

`ActionMetierDifferee` (classe inline, `tExecution`/`type`/`idCommande`),
liste unique `actionsMetierDifferees` (FIFO par insertion), 9 types
confirmés (`GENERER_COMMANDE`, `ANIM_RETOUR_VEHICULE` exclus du comptage
terminal ; `RECEPTION_COMMANDE`, `ANALYSE_STOCK`, `ANALYSE_MATIERE`,
`FINALISER_APPROVISIONNEMENT`, `LANCER_PRODUCTION`, `LIVRAISON_DIRECTE`,
`RECEPTION_CLIENT_DIRECTE` comptés). Vidée en tête de `demarrerSimulation()`
(`actionsMetierDifferees.clear();`, déjà vu §7). Le comptage
`pendingBusinessActions` (export EXP-0) est directement
`nombreActionsMetierDiffereesPertinentes()`, confirmé cohérent avec le
Run 01 (`pendingBusinessActions=0` à la clôture). **Aucun chemin
d'action orpheline détecté** dans les points vérifiés (le filtrage exclut
les deux types sans effet métier, et la garde de réentrance E.2-FIX
empêche une action liée à une commande déjà en cours de traitement d'être
reprogrammée en double) — **pas une preuve exhaustive** que
`FINALISER_APPROVISIONNEMENT`/`LANCER_PRODUCTION` ne peuvent jamais être
laissées associées à une commande déjà `commandeEstTerminale()` par un
chemin non retracé dans cette passe.

---

## 17. Audit multiproduit

*Profondeur : ciblée sur la présence/absence des couches demandées, pas
une vérification exhaustive de chaque calcul par produit.*

| Fonctionnalité | Support réel | Limitation |
|---|---|---|
| Plusieurs produits définis | **Oui** | `listeProduits`/`catalogueProduits` (`LinkedHashMap<String,ScenarioFlux>`), indexés par identifiant produit string |
| Plusieurs commandes de produits différents | **Oui** | `CommandeAgent` porte une référence produit (`codeProduitCommande(cmd)`), pas de limitation à un seul produit trouvée |
| Production concurrente (plusieurs produits en parallèle) | **Oui, avec réserve** | La garde de réentrance E.2-FIX est par commande, pas par produit — deux commandes de produits différents peuvent progresser en parallèle sur des postes distincts ; le partage d'un même poste entre produits n'a pas été vérifié en détail dans cette passe |
| Stocks PF par produit | **Oui** | `stockFiniParProduit: LinkedHashMap<String,Double>` |
| Matières par produit | **Oui** | `FicheMatiere` par matière, nomenclature (`LigneNomenclature`) par produit via `ScenarioFlux.nomenclature` |
| Politique de stock par produit | **Oui, partiellement** | `quantiteEconomiqueParProduit` (cache par produit, Bloc M.3) confirmé ; `pointCommandeProduit`/`quantiteEconomiqueProduit` au singulier existent aussi (mono-produit hérité) — **les deux coexistent**, la variante par-produit est la plus récente (M.3) et prioritaire dans les points vus, mais l'audit n'a pas confirmé que TOUS les appelants utilisent la version multi-produit plutôt que la version mono historique |
| Routage par produit | **Oui** | Nomenclature/`ScenarioFlux` par produit pilote le routage matière |
| KPI par produit | **Partiel, avec anomalie** | `nbTerminesParProduit` existe mais n'est jamais lu (§14) — **aucun KPI par produit réellement exposé/exporté confirmé** dans cette passe au-delà des stocks (`stockFiniParProduit`, bien exporté via `detailStockFiniParProduit()`) |
| Agrégation globale | **Oui** | `kpiGlobal`/`nbTermines` agrègent tous produits confondus, cohérent avec le Run 01 (single-produit dans ce run, donc pas de preuve runtime de l'agrégation multi-produit elle-même) |

**Conclusion, conforme à la consigne de ne pas surclasser** : le master
supporte une architecture multi-produit réelle au niveau configuration/
stock/nomenclature (confirmé), mais **le KPI par produit n'est pas
réellement exposé** (dead metric, §14), et le Run 01 n'a testé qu'un
scénario mono-produit — **le multiproduit n'a donc pas été validé en
runtime dans cette passe**, seulement au niveau structure de données.

---

## 18. Audit concurrence / multi-commande

*Profondeur : ciblée.*

Aucun bloc `synchronized` trouvé lié à la logique métier (5 occurrences
totales dans le fichier, à vérifier si elles concernent un autre sujet non
métier — non approfondi dans cette passe). Le modèle AnyLogic étant
mono-thread pour l'exécution événementielle du moteur (hors threads
d'affichage/timer UI comme `suiviTempsReelTimer`), l'absence de
`synchronized` sur la logique métier n'est pas en soi anormale — le risque
de concurrence en AnyLogic est structurel (ordre des événements), pas un
risque de threads Java classiques. La garde de réentrance E.2-FIX (§3/§4)
est le mécanisme réel de protection contre un double traitement de la même
commande. **Aucune variable globale non protégée par cette garde et
susceptible d'être écrasée par une commande différente n'a été identifiée
dans les points vérifiés** — mais cette recherche n'a pas couvert
l'ensemble des fonctions manipulant `commandes`, seulement les points déjà
audités en §3-§5.

---

## 19. Audit du Run 01 comme preuve de cohérence

*Le Run 01 a servi de fil conducteur à plusieurs sections ci-dessus (§4,
§5, §6, §17). Il n'est pas réinterprété ici comme un benchmark de
performance, conformément à la consigne.*

Confirmé par le Run 01 (`seedExperiment=1001`, déjà documenté en détail
dans `EXPERIMENTATION_FOUNDATION.md` §14.8) :
- **MTS nominal fonctionne** : le run a atteint la terminalité, ce qui
  implique que le chemin MTS (stock/attente/reconstitution) a fonctionné
  de bout en bout sans blocage.
- **Reconstitution autonome fonctionne** : `openReplenishments=0` à la
  clôture, dernière unité `REAPPRO_1_F_50` tracée jusqu'à son étape
  finale (sM1.6.1, T=4764.595).
- **Source, Make, Deliver fonctionnent** : le WIP retombe naturellement à
  0 (`entitiesInProcessAtPosts=0`), Finished Stock=130 à la clôture — les
  postes ont traité leur charge sans blocage visible.
- **Client close, REAPPRO close, terminalité atteinte** : confirmé par les
  quatre invariants à zéro (§5).
- **Aucune anomalie structurelle nouvelle révélée par le Run 01
  lui-même** au-delà de ce qui est déjà documenté (absence de panne
  observée, expliquée statistiquement, EXP-0.4 §13.6/§14.8) — le run ne
  couvrait qu'un scénario mono-produit MTS/REAPPRO, donc **ne constitue
  pas une preuve runtime pour MTO, ETO, ni le multiproduit** (voir §3,
  §17).

---

## 20. Préparation E4 — variables candidates (audit seulement)

*Profondeur : ciblée sur l'existence, le type et la mutabilité de chaque
candidat ; aucune grille de valeurs fixée.*

| Variable | Emplacement | Type | Scope | Mutable avant run | Dépendances | Besoin de reset | Compat. Parameter Variation | Compat. boucle scriptée |
|---|---|---|---|---|---|---|---|---|
| **x1 — capacité poste critique** | `PosteGenericAgent.capaciteSimultanee` | `int` | Par poste | Oui, via JSON (`champCapacite`/`jsonInt(pm,"capaciteSimultanee",1)`) ou édition manuelle avant `demarrerSimulation()` | Aucune dépendance croisée identifiée dans cette passe au-delà du calcul de capacité du `delay` lui-même | Non (config, pas runtime) | Oui — un run = une valeur, agents neufs | Oui, si modifié avant chaque `demarrerSimulation()` |
| **x2 — taille des sous-lots** | `PosteGenericAgent.tailleLot` | `int` | Par poste | Oui, via JSON (`tailleLot`) | Lié au mécanisme de lot/jonction multi-amont (`lotEnCours`) | Non (config) | Oui | Oui |
| **x3 — règle de priorité** | **Non wiré actuellement** | — | — | — | Le seul mécanisme de tri par priorité/EDD existe dans `ordonnancerProduction()`, **confirmé inactif** (§14) : `carnetCommandesMTO` n'est jamais peuplé, donc aucune règle de priorité n'a d'effet observable aujourd'hui sur le flux réel (le flux réel suit l'ordre FIFO d'insertion dans `actionsMetierDifferees`) | **Bloquant si x3 est requis tel quel** — nécessiterait soit de réactiver/raccorder `ordonnancerProduction()`, soit d'introduire un nouveau point de variation sur l'ordre `actionsMetierDifferees` | Non applicable tant que non wiré | Non applicable tant que non wiré |
| **x4 — politique de stock** | `Main.pointCommandeProduit`/`quantiteEconomiqueProduit` (mono) et `quantiteEconomiqueParProduit` (multi, Bloc M.3) ; `FicheMatiere.stockSecurite`/`pointCommande` (matières) | `double` | Global ou par produit selon le champ | Les **paramètres** (seuils, sécurité) sont configurables via JSON ; mais une seule **formule** de politique existe (revue continue implicite avec point de commande calculé) — **pas de politique alternative (ex. révision périodique) à sélectionner** | `reinitialiserPolitiquesStockPourRun()` | **Oui, déjà en place** (§7) | Oui pour les paramètres ; **non pour un facteur catégoriel « type de politique »**, qui n'existe pas encore comme choix discret dans le code | Idem |

**Conclusion §20** : x1 et x2 sont prêts à devenir des facteurs E4
immédiatement (valeurs numériques configurables, reset non nécessaire car
ce sont des configurations). x3 n'est **pas disponible** comme facteur
expérimental réel aujourd'hui — le mécanisme existant qui porterait cette
idée est mort. x4 est disponible seulement comme **facteur continu** sur
les seuils d'une politique unique, pas comme facteur **catégoriel** entre
plusieurs politiques.

---

## 21. Comparaison des architectures E4 (sans implémentation)

*Reprend et complète la comparaison déjà esquissée en EXP-0.4V §14.6,
avec les critères demandés ici.*

| Critère | Option A — Parameter Variation / nouvelle instance par run | Option B — boucle scriptée, même instance |
|---|---|---|
| Reproductibilité | Élevée — chaque run est indépendant, `seedExperiment` appliqué au démarrage de chaque instance | Élevée en théorie (même mécanisme de graine), mais dépend entièrement de la fiabilité du reset entre runs |
| Isolation d'état | **Garantie par construction** — confirmé, c'est le Cycle C déjà validé en runtime (EXP-0.4V/clôture) | **Non garantie** — dépend d'un audit exhaustif des états run-scoped (§7), dont au moins un point n'est pas encore couvert (`OperationalAgent`, §7/§9) |
| Seed | Direct, un `seedExperiment` par run | Direct également, mais nécessite de s'assurer qu'aucun tirage ne fuit d'un run au suivant (déjà démontré une fois avec la panne avant EXP-0.4 — risque de classe similaire pour tout futur état non audité) |
| Coût de reset | **Nul** — géré par la recréation native de l'instance | Non nul — chaque nouvel état run-scoped découvert doit être ajouté manuellement au reset (maintenance continue) |
| Facilité d'export | Standard AnyLogic (résultats par run consolidés nativement par l'expérience) | Manuel — dépend entièrement du code d'export déjà en place (`exporterABoxRuntimeTTL`/Excel), qui fonctionne mais n'a pas de notion native de « campagne » |
| 144+ configurations/réplications | **Cas d'usage natif** de Parameter Variation | Possible mais demande un harnais de pilotage (boucle Java ou script externe) non existant aujourd'hui dans le modèle |
| Simplicité | Plus simple à mettre en œuvre (fonctionnalité AnyLogic standard) | Plus complexe (nécessite un mécanisme de pilotage inexistant + audit run-scoped complet) |
| Risque de contamination | **Nul par construction** | Réel, proportionnel au nombre d'états run-scoped non encore identifiés (au minimum 4 champs `OperationalAgent` déjà connus comme non resetés) |
| Compatibilité avec le modèle actuel | **Aucune expérience Parameter Variation n'existe encore dans le `.alp`** (§14.2 d'`EXPERIMENTATION_FOUNDATION.md`, confirmé à nouveau ici) — à créer entièrement | Compatible avec le code actuel tel quel (rien n'empêche d'appeler `demarrerSimulation()`/`arreterSimulation()` en boucle), mais **le cycle de vie réel confirmé en runtime (EXP-0.4V) montre que le bouton Run reste grisé après `FINISHED`** — une boucle scriptée devrait donc piloter le moteur par un autre mécanisme que les boutons UI actuels (probablement via l'API d'expérience elle-même, non explorée dans cette passe) |

**Conclusion, fondée sur les faits ci-dessus (pas un choix arbitraire)** :
**l'option A (Parameter Variation) est techniquement préférable** sur
tous les critères sauf un — elle nécessite de créer une infrastructure
d'expérience qui n'existe pas encore, alors que l'option B réutilise le
code actuel tel quel mais devrait contourner une limite déjà confirmée
runtime (bouton Run grisé après FINISHED, EXP-0.4V) et porte un risque de
contamination réel et déjà partiellement matérialisé une fois (pannes,
avant EXP-0.4). Cette préférence reste un compromis technique à valider
par l'utilisateur, pas une décision prise ici.

---

## 22. Anomalies classées

| ID | Priorité | Fichier/Agent/Fonction | Preuve | Impact | Scénario d'apparition | Correction conceptuelle | Dépendances | Risque de correction |
|---|---|---|---|---|---|---|---|---|
| **AN-01** | **P1** | `Main.ordonnancerProduction()` / `carnetCommandesMTO` | 0 appel `.add()` trouvé sur `carnetCommandesMTO` (§14) | x3 (règle de priorité) indisponible comme facteur E4 réel ; toute future dépendance à un ordonnancement par priorité serait un no-op silencieux | Toute tentative d'utiliser x3 comme facteur E4 sans corriger ce point d'abord | Raccorder `carnetCommandesMTO` à un point d'alimentation réel, ou documenter explicitement que l'ordonnancement réel est FIFO par `actionsMetierDifferees` et retirer x3 des facteurs E4 envisagés | Risque de WIP si le carnet est activé sans contrôle (déjà signalé dans `MERGE_PROGRESS.md`, Bloc E) | Modéré — toucher à l'ordonnancement peut changer le comportement de tous les scénarios existants |
| **AN-02** | **P1** | `Main` / `OperationalAgent.etatHolon` et 3 champs associés | 0 reset dans `demarrerSimulation()`, même mécanisme de non-recréation que `PosteGenericAgent` (§7, EXP-0.4V) | Contamination inter-run possible **si et seulement si** une future architecture E4 réutilise la même instance (Option B, §21) | Option B uniquement — sans impact sous Option A | Étendre `reinitialiserEtatPannePourNouveauRun()`-like reset à `opAgents`, ou créer une passe dédiée, **avant** toute campagne Option B | Toucher à `OperationalAgent` touche potentiellement l'AER/l'ordonnancement — scope explicitement exclu d'EXP-0.4 | Faible techniquement (même patron qu'EXP-0.4) mais nécessite un nouvel audit exhaustif avant application |
| **AN-03** | **P2** | `exporterABoxRuntimeTTL()` (manifeste legacy) | `run:randomSeed="NON_ACCESSIBLE_DANS_MAIN"` coexistant avec `run:experimentSeed=1001` (§12.A) | Incohérence de traçabilité pour un consommateur externe de l'export lisant le mauvais champ | Tout export ABox à partir de maintenant | Harmoniser les deux champs (sans décider ici lequel doit changer) | Aucune dépendance fonctionnelle (champ d'export pur) | Faible |
| **AN-04** | **P2** | `exporterABoxRuntimeTTL()` (`run:modelArtifact`) | Valeur figée `SCONTO_SVU_FINAL_VSM_FIX_CANDIDATE.alp` (§12.B) | Induit en erreur sur l'identité du fichier réellement exécuté (déjà documenté comme non fiable dans l'audit DataCo précédent) | Tout export ABox | Rendre ce champ dynamique ou le documenter comme obsolète | Aucune | Faible |
| **AN-05** | **P2** | `exporterABoxRuntimeTTL()` (`kpiZener`, `zener_*`, `ZENER_ACT_4_ONLY`) | Nommage ZENER en dur dans le schéma d'export malgré une résolution générique de l'entreprise focale (§13, catégorie C) | Export trompeur pour un scénario dont l'entreprise focale n'est pas ZENER (label incorrect, pas de calcul incorrect) | Tout export ABox sur un scénario non-ZENER | Renommer les identifiants de champ/schéma en termes génériques (`kpiEntrepriseFocale`, `focal_process_time`, `FOCAL_ENTERPRISE_ONLY`) | Aucune dépendance fonctionnelle (renommage de schéma) | Faible, mais casse la compatibilité de tout consommateur externe déjà branché sur les noms actuels |
| **AN-06** | **P2** | `Main.nbTerminesParProduit` | Deux domaines de clés différents alimentent la même map (`cmd.typeCommande` vs `e.typeProduit`), jamais lue (§14) | Aucun impact aujourd'hui (métrique morte) ; deviendrait un bug silencieux si exploitée telle quelle | Si un futur export/KPI par produit s'appuie sur ce champ sans le corriger d'abord | Séparer en deux maps distinctes (par type de commande, par produit), ou supprimer si non nécessaire | Aucune | Faible |
| **AN-07** | **P2** | `estOrdreStockAutonome()`/`estOrdreReappro()` | Deux fonctions identiques, doublon déjà connu (§4) | Dette de lisibilité uniquement, comportement identique confirmé | N/A | Fusionner en une seule fonction, remplacer les appels | Vérifier tous les sites d'appel avant fusion | Faible |
| **AN-08** | **P2** | `Main.pointCommandeProduit`/`quantiteEconomiqueProduit` (mono) coexistant avec `quantiteEconomiqueParProduit` (multi, M.3) | Deux mécanismes de politique de stock, portée différente, coexistants (§17/§20) | Risque de confusion sur quelle politique s'applique réellement pour un scénario multiproduit — **non confirmé comme un bug actif dans cette passe**, seulement une coexistence observée | Scénario multiproduit avec politique de stock active | Clarifier/documenter lequel prévaut dans quel cas, ou unifier | À vérifier avant de fixer x4 comme facteur E4 | Modéré — touche au calcul de réapprovisionnement |
| **AN-09** | **P3** | Chaînes de log/popup « ZENER » dans `analyserStockCommandeOrchestree()` et ailleurs (§13, catégorie B) | Texte affiché à l'utilisateur, sans effet logique | Cosmétique pour un scénario non-ZENER | Tout scénario non-ZENER | Génériciser le texte (utiliser le nom de l'entreprise focale réelle) | Aucune | Faible |
| **AN-10** | **P3** | `acteurCourtF()` mapping ZENER en dur (§13, catégorie B) | Fonction d'affichage avec repli générique déjà en place | Cosmétique, dégrade proprement pour un scénario non-ZENER | Tout scénario non-ZENER avec acteurs non reconnus | Déplacer vers une config JSON de libellés si une propreté totale est requise | Aucune | Faible |
| **AN-11** | **P3** | `calculerDisponibiliteMachinesOEE()` vs `calculerDisponibiliteMachinesMoyenne()` (§8/§12) | Deux définitions de « disponibilité », sources différentes, coexistantes | Risque de confusion documentaire/lecture du dashboard, pas un bug de calcul | Lecture croisée OEE vs AM.3.9 | Documenter clairement la différence dans le dashboard/l'export | Aucune | Faible |
| **AN-12** | **P2** | `board.kpiZener.*` sans garde nulle à plusieurs sites d'export (§8) | Appels directs sans `try/catch` ni test de nullité à certains sites (contrairement à un site voisin qui, lui, protège) | Risque de `NullPointerException` sur l'export si l'entreprise focale n'est pas résolue — **non observé en runtime dans cette passe** | Scénario sans acteur `ENTREPRISE_FOCALE` correctement configuré | Ajouter une garde nulle cohérente à tous les sites, ou garantir `kpiZener` toujours non-null par construction | Aucune | Faible |

**Aucune anomalie P0 identifiée dans cette passe.** Aucun élément trouvé
ne bloque un run manuel ni n'invalide directement les résultats déjà
obtenus sur Run 01 (scénario mono-produit MTS/REAPPRO, Cycle C).
L'absence de P0 est spécifiquement conditionnée aux zones réellement
auditées en profondeur (§3, §4, §5, §6, §7) — les zones à profondeur
ciblée ou non exhaustive (§8 à §19 pour leurs réserves respectives) ne
peuvent pas être garanties totalement exemptes de P0 sur cette seule
base ; c'est précisément la raison de la conclusion C en §24.

---

## 23. Matrice de complétude

*Statuts strictement fondés sur les preuves ci-dessus. « COMPLET » n'est
utilisé que lorsqu'une preuve directe (code + éventuellement runtime)
existe sans réserve connue ; sinon PARTIEL/À VÉRIFIER/LEGACY/ABSENT,
conformément à la consigne de ne jamais utiliser PASS sans preuve
runtime.*

| Domaine | Statut | Preuve | Lacune | Bloquant E4 ? |
|---|---|---|---|---|
| MTS | PARTIEL | Code tracé intégralement (§3) ; Run 01 valide MTS en runtime | Aucune identifiée | Non |
| MTO | À VÉRIFIER | Code tracé statiquement (§3), **jamais exercé en runtime** (Run 01 est MTS/REAPPRO) | Pas de preuve runtime | Non bloquant, mais à tester avant de fonder une campagne dessus |
| ETO | À VÉRIFIER | Code tracé statiquement (§3), partage le code MTO, **jamais exercé en runtime**, pas de phase d'ingénierie distincte modélisée | Distinction fonctionnelle ETO limitée | **Oui si ETO doit être un facteur E4 distinctif** |
| Source | PARTIEL | Tracé via matière/nomenclature (§3/§4), non testé isolément en runtime au-delà de Run 01 | — | Non |
| Make | PARTIEL | Tracé (§3), validé WIP→0 sur Run 01 | — | Non |
| Deliver | PARTIEL | Tracé (§3), validé sur Run 01 (livraison directe MTS) | Chemin MTO/ETO Deliver non exercé en runtime | Non |
| Return | À VÉRIFIER | Mentionné dans l'architecture AER (§9, flux AMENDMENT/EXECUTION/REPORT) mais non spécifiquement audité dans cette passe | Pas de trace directe auditée ici | À vérifier |
| Stock PF | PARTIEL | `stockFiniParProduit`, exporté (§17), validé Run 01 | — | Non |
| Matières | PARTIEL | `FicheMatiere`, nomenclature, reset confirmé (§7) | — | Non |
| Réappro autonome | PARTIEL | Tracé intégralement (§4), validé Run 01 (clôture propre) | — | Non |
| Multi-commandes | À VÉRIFIER | Garde de réentrance confirmée (§3/§18), pas de test runtime multi-commandes simultanées dans cette passe | Pas de preuve runtime de concurrence réelle | À vérifier avant campagne à forte charge |
| Multiproduit | PARTIEL | Structures de données confirmées (§17) | KPI par produit mort (AN-06), politique de stock à deux mécanismes coexistants (AN-08), **jamais testé en runtime** (Run 01 mono-produit) | **Oui si multiproduit est requis pour E4/E5** |
| RNG | COMPLET | Audit exhaustif §6, source unique confirmée, cohérent avec EXP-0 à EXP-0.4 | — | Non |
| Terminalité | COMPLET | Audit exhaustif §5, validé runtime Run 01 | — | Non |
| Pannes | PARTIEL | Reset validé runtime (Run 01, `[PANNE-RESET]` vierge) ; dynamique panne→réparation **non exercée** en runtime (aucune panne survenue, EXP-0.4 §13.6/§14.8) | Séquence panne complète non testée | Non bloquant pour Option A ; à tester avant Option B |
| OEE | À VÉRIFIER | Formule tracée (§8), dépend de l'état panne (reseté depuis EXP-0.4), **jamais observée avec une panne réelle en runtime** | Pas de preuve runtime avec panne | Non bloquant, à tester si OEE est un indicateur E4 |
| SCOR | PARTIEL | Pipeline tracé (§8/§10), proxies documentés | Audit N4 non approfondi | Non |
| VSM | PARTIEL | Indicateurs d'export tracés (§11) | Pas d'audit exhaustif de toutes les conversions d'unité internes | Non |
| PI | PARTIEL | Amorçage/agrégation confirmés (§8) | Pas de relecture ligne à ligne de `calculerPIGlobal()` dans cette passe | Non |
| AER | PARTIEL | Chaîne confirmée (§9) | `realignerArchitectureAgents()` non tracée en détail | Non |
| SMA | PARTIEL | 8 classes d'agent confirmées (§2), architecture holonique confirmée | — | Non |
| ISA-95 | À VÉRIFIER | Non spécifiquement audité dans cette passe (hors budget de temps) | Aucune vérification directe | À vérifier |
| Exports | PARTIEL | Excel/CSV/TTL/Dashboard confirmés actifs (§12) | 2 anomalies connues + 1 nouvelle (AN-03/04/05) | Non bloquant pour un run manuel, à corriger avant une campagne dont les résultats seraient publiés tels quels |
| ABox | PARTIEL | Structure tracée en détail (§12), cohérente | Anomalies de nommage (AN-03/04/05) | Non |
| Run manifest | LEGACY | Champ `graineAleatoire`/`modelArtifact` confirmés obsolètes (AN-03/04) | — | Non bloquant, mais à corriger avant publication de résultats E4 |
| Généricité | PARTIEL | Audit exhaustif des motifs demandés (§13), DataCo=0, ZENER classé | 1 hardcoding de nommage d'export confirmé (AN-05) | Non |
| Reset | COMPLET | Audit exhaustif §7 pour la panne (EXP-0.4), validé runtime | — | Non |
| État run-scoped | PARTIEL | Table complète produite (§7) | `OperationalAgent` non reseté (AN-02) — sans impact sous Cycle C/Option A confirmé | **Oui si Option B est retenue pour E4, sinon Non** |

---

## 24. Décision de sortie de l'audit

**Conclusion retenue : C — MASTER NÉCESSITE UNE PASSE DE CONSOLIDATION AVANT E4.**

**Fondement, strictement lié aux anomalies P0/P1** : aucune anomalie P0
n'a été trouvée (rien n'invalide Run 01 ni ne bloque un run manuel
aujourd'hui), mais **deux P1 existent et sont directement structurants
pour la conception d'E4** :

- **AN-01** rend indisponible, tel quel, l'un des quatre facteurs
  expérimentaux envisagés (x3, règle de priorité) — un choix de conception
  E4 (retenir x3 ou l'abandonner/le remplacer) doit être fait AVANT
  d'écrire un plan d'expérience, pas pendant.
- **AN-02** ne bloque rien sous l'option d'architecture aujourd'hui jugée
  préférable (Option A, Parameter Variation, §21), mais **bloquerait une
  campagne fiable sous Option B** sans un audit de reset complémentaire —
  et le choix A/B lui-même n'est pas encore arrêté par l'utilisateur.

À cela s'ajoute une réserve de méthode plus large : plusieurs domaines
directement pertinents pour une campagne E4 (**MTO, ETO, multiproduit,
multi-commandes concurrentes**) sont statutés **À VÉRIFIER**, faute de
preuve runtime — seul un scénario MTS/REAPPRO mono-produit a été exercé
via Run 01. Une campagne E4 fondée sur `x1`/`x2`/`x4` seuls, en régime MTS
mono-produit, pourrait démarrer sans consolidation lourde ; mais toute
extension à MTO/ETO/multiproduit sans validation runtime préalable
exposerait la campagne au même type de risque que celui déjà rencontré
trois fois pendant EXP-0 (bugs réels détectés uniquement par un run
manuel, jamais par la seule lecture du code).

**Ceci n'est pas une conclusion B** (le master n'a pas besoin de
« corrections ciblées » ponctuelles avant de servir de base — les P1
identifiés sont plus des **décisions de conception** à trancher que des
bugs à corriger) et **pas une conclusion A** (le master n'est pas encore
prêt tel quel : au minimum, le statut de x3 et le choix d'architecture
A/B doivent être arrêtés en amont).

---

**Aucune correction n'a été appliquée pendant cette passe.**
