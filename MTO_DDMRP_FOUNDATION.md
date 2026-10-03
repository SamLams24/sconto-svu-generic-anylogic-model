# MTO / DDMRP — Audit de fondation (MTO-0)

**Nature de ce document : audit et conception uniquement.** Aucun fichier
`.alp` et aucun fichier `.json` n'a été modifié pour le produire. Toutes
les citations `fonction (ligne N)` renvoient à
`model/SCONTO_SVU_GENERIC_MASTER.alp` sur la branche
`feature/mto-ddmrp-foundation`, créée depuis le commit de clôture C2
(`695ad0788927eca94ef2674cb261ba6c0bfabdec`). Ce chantier est
volontairement indépendant de C3/E4 : aucune dépendance n'est créée vers
le travail de consolidation pré-E4.

---

## 1. Audit exhaustif du path MTO actuel

Le modèle ne dispose pas d'un pipeline MTO linéaire unique : c'est un
orchestrateur événementiel à actions différées
(`actionsMetierDifferees`, `executerActionMetierDifferee()`, ligne 2629)
qui enchaîne les étapes. Trace réelle, étape par étape, d'une commande
MTO depuis sa génération jusqu'à sa clôture.

### 1.1 Génération et typage

**`genererCommande()`** (ligne 13836, fonction nommée). Crée
`cmd = add_commandes()`, `cmd.idCommande = "CMD_" + n`,
`cmd.statut = "EN_ATTENTE"`, puis fixe immédiatement
`cmd.typeCommande = modeSCORActif()` (ligne ~13880, re-confirmé une
seconde fois ligne ~13902 après résolution du scénario Cas 1/2/3).

**`modeSCORActif()`** (ligne 8521) :
```java
String modeSCORActif() { return isETO ? "ETO" : (isMTO ? "MTO" : "MTS"); }
```
**Constat central** : `typeCommande` n'est **pas** une décision prise
commande par commande en fonction du stock réel. C'est un **bascule
globale de run** (`isMTO`/`isETO`, des booléens de configuration). Pour
un run donné, **toutes** les commandes clientes générées par
`genererCommande()` portent le même `typeCommande`. Une fonction
`deciderTypeCommande(CommandeAgent cmd)` existe bien et implémente une
vraie décision par commande basée sur le stock réel (voir §1.2 et §3),
mais elle n'est **appelée nulle part** (`grep -n
"deciderTypeCommande("` ne retourne que sa propre déclaration, ligne
51465). C'est un résultat factuel, pas une supposition : zéro site
d'appel dans tout le fichier.

- Agent responsable : aucun agent-holon à ce stade ; code Main
  (génération de la demande).
- SCOR concerné : D1.1 (Process Inquiry/Quote implicite, non détaillé).
- Sortie : `CommandeAgent` créé, `typeCommande` et `statut` fixés,
  commande ajoutée à `commandes` (liste Main).
- Point d'action différée suivant : `planifierActionCommande` déclenche
  `traiterCommande()`/`analyserStockCommandeOrchestree()` via le
  dispatcher (ligne 2629 et suivantes).

### 1.2 La fonction orpheline `deciderTypeCommande()`

**`deciderTypeCommande(CommandeAgent cmd)`** (ligne 51465, classe
`StrategicAgent` déduite du contexte `HOLON-STRAT` et des champs
`main.supervisorsMacro`). Logique réelle et complète :

1. Résout le `ScenarioFlux` de la commande.
2. Si aucun poste `STOCKAGE` n'existe dans la chaîne → retourne `"MTO"`
   directement (ligne ~51503).
3. Sinon, calcule `dispo = stockFini.stockDisponible()` et
   `servableSurStock = (dispo >= cmd.qte)`.
4. Si **non** servable sur stock : vérifie
   `coordMake.carnetCommandesMTO.size() >= capaciteCarnetMax`
   (`coordMake` = le `CoordinatorAgent` dont
   `idAgentCoordinateur == "CA-sM2"`) ; si vrai, incrémente
   `nbCommandesRefusees`, fixe `cmd.statut = "REFUSEE"` et retourne
   `"REFUSEE"`.
5. Sinon retourne `"MTS"` ou `"MTO"` selon `servableSurStock`.

Le commentaire source dit explicitement : *« Remplace l'ancien tirage
aléatoire 70/30, qui ne correspondait à aucune décision d'agent »*
(ligne ~51473). C'est donc une fonction de **remplacement déjà écrite**
pour une faiblesse déjà identifiée par un auditeur précédent, mais dont
le branchement dans `genererCommande()` n'a jamais été fait. Elle
dépend elle-même de `carnetCommandesMTO`, qui n'est jamais alimenté
(§3) : même si elle était appelée aujourd'hui, sa branche `REFUSEE` ne
se déclencherait jamais (`size() >= capaciteCarnetMax` est toujours
`0 >= capaciteCarnetMax`, donc faux pour toute valeur positive de
`capaciteCarnetMax`).

### 1.3 Analyse stock (branche MTS court-circuit, puis MTO réel)

**`analyserStockCommandeOrchestree(cmd)`** (ligne 3039). Garde de
réentrance via `commandeEstTerminale()` (ligne 10164) et des statuts en
vol. Puis :

- Si `cmd.typeCommande == "MTS"` **et** stock fini suffisant : livraison
  directe (`consommerStockFiniProduit`, statut → `EN_LIVRAISON`,
  planifie `LIVRAISON_DIRECTE`). Chemin MTS pur, non MTO.
- Si `cmd.typeCommande == "MTS"` et stock insuffisant : la commande
  **attend** (`ouvrirAttenteStockCommande`,
  `planifierActionCommande("ANALYSE_STOCK", cmd, 30.0)`) ; c'est la
  politique de stock autonome (`verifierPolitiqueStockProduit()`,
  `declencherProductionAutonome()`) qui reconstitue le stock, pas la
  commande elle-même (commentaire C14.55, ligne ~3115 : *« la commande
  ne déclenche plus sa propre production »*).
- **Sinon** (donc pour tout `typeCommande` MTO ou ETO, puisque les deux
  branches MTS ci-dessus ont déjà retourné) : appel direct à
  `analyserMatiereCommandeOrchestree(cmd)` (ligne ~3180). C'est le
  **point d'entrée réel du chemin MTO**.
- Agent responsable : code Main (pas d'agent-holon dédié à cette
  bascule).
- SCOR concerné : S1/D1 préliminaire (consultation stock).

### 1.4 Analyse matière (le cœur du chemin MTO)

**`analyserMatiereCommandeOrchestree(cmd)`** (ligne 3184).

1. Résout `sc = scenarioPourCommande(cmd)`. Si `sc == null` →
   `cmd.statut = "BLOQUE_CONFIG"`, **terminal**, sortie.
2. Si `sc.nomenclature` vide → `cmd.statut = "BLOQUE_NOMENCLATURE"`,
   **terminal**, sortie (mode *fail-closed* assumé, commentaire
   explicite).
3. Calcule `matOK = matieresSuffisantesPourScenario(sc, cmd.qte)`
   (ligne 4836, simple lecture, **aucune réservation/décrément** à ce
   stade — voir §5 pour l'implication concurrence).
4. Trace hiérarchique AER complète (MakeFeasibilityCheck →
   CapacityCheckRequest/MaterialCheckRequest →
   MaterialAvailabilityResponse/MaterialShortageDetected, etc.),
   confirmation client (`OrderConfirmed`).
5. **Si matière insuffisante** : `cmd.statut = "EN_APPROVISIONNEMENT"`,
   `declencherApprovisionnementCommande(cmd, sc, cmd.qte)` (ligne 5404),
   puis `planifierAvecEchelle("FINALISER_APPROVISIONNEMENT", cmd,
   delaiApproReel)` — reprise différée après le délai fournisseur
   (éventuellement forcé par un test de retard).
6. **Si matière suffisante** : appel direct à
   `tracerEtPlanifierProductionCommande(cmd)` (ligne 3378).

- Données consommées : `ScenarioFlux.nomenclature`,
  `FicheMatiere.stockDisponible` (lecture seule).
- Données produites : `cmd.statut`, traces AER, popup métier.
- Agent responsable : code Main, avec traces attribuées aux agents
  virtuels Source/Make/Plan (AT-sP2/AT-sP3) pour la cohérence AER.
- SCOR concerné : P2.3/S1.1 (approvisionnement) ou M1.1 (lancement
  production).
- Sortie d'erreur : `BLOQUE_CONFIG`, `BLOQUE_NOMENCLATURE` (ligne
  3186-3200).

### 1.5 Approvisionnement (si matière manquante)

**`declencherApprovisionnementCommande(cmd, sc, qte)`** (ligne 5404) :
non relu en détail ligne par ligne dans cette passe (hors périmètre
strict du tracé principal, à auditer en détail en MTO-1 si nécessaire),
mais son rôle est confirmé par les appelants et les traces AER :
déclenche la commande fournisseur et programme les réceptions
attendues sur `FicheMatiere.receptionsAttendues`. Reprise via
l'action différée `FINALISER_APPROVISIONNEMENT` →
`finaliserApprovisionnementCommande(cmd)`, qui réanalyse (retour
probable vers `analyserMatiereCommandeOrchestree` ou directement vers
`tracerEtPlanifierProductionCommande`, à confirmer précisément en
MTO-1 — **non vérifié ligne à ligne dans cette passe, classé À TESTER
RUNTIME / À AUDITER PLUS PRÉCISÉMENT**).

### 1.6 Lancement production (chemin réellement actif, sans file)

**`tracerEtPlanifierProductionCommande(cmd)`** (ligne 3378) :
re-vérifie nomenclature et `matieresSuffisantesPourScenario` (double
contrôle défensif), trace AER (ProductionPlan → ProductionOrder →
ProductionTaskAssignment), fixe `cmd.statut = "PRODUCTION_PLANIFIEE"`,
puis **`planifierAvecEchelle("LANCER_PRODUCTION", cmd,
dureeReelleChaine(...))`** (ligne ~3412).

**Constat central n°2** : ce point planifie une action différée
**directement et individuellement pour chaque commande**, sans passer
par aucune structure de file ou de priorité partagée. Il n'y a
**aucun appel à `carnetCommandesMTO`** dans toute cette chaîne
(`genererCommande` → `analyserStockCommandeOrchestree` →
`analyserMatiereCommandeOrchestree` →
`tracerEtPlanifierProductionCommande`). Le carnet et son ordonnanceur
EDD+priorité (`ordonnancerProduction()`, §3) sont une structure
**parallèle et non connectée** au chemin réellement actif.

Action différée exécutée : `LANCER_PRODUCTION` →
`lancerProductionCommande(cmd)` (ligne 14078, fonction `Function`
nommée) → corps = `lancerProductionCommandeOrchestree(cmd);` (ligne
14088).

### 1.7 Lancement effectif et circulation Make

**`lancerProductionCommandeOrchestree(cmd)`** (ligne 5667) :
`cmd.tDebutProduction = time()` (si non déjà fixé), résout la
`routeBase` via `routeProductionMakeDepuisScenario(sc)`, puis pour
`i = 0..cmd.qte-1` crée un `FluxEntity` (`add_fluxEntites()`) avec sa
`feuilleDeRoute` et instancie un agent `Produit`
(`creerProduitAgentPourFlux`). Chaque unité circule ensuite
indépendamment sur les postes de la route (mécanisme AnyLogic standard,
non MTO-spécifique au-delà de ce point).

- Données consommées : `routeProductionMakeDepuisScenario(sc)`,
  `cmd.qte`.
- Données produites : `cmd.qte` entités `FluxEntity`/`Produit`,
  `cmd.tDebutProduction`.
- Agent responsable : Main (création), puis chaque `Produit`/poste
  individuellement.
- SCOR concerné : M1.2/M1.3 (exécution fabrication).

La consommation réelle de matière a lieu **ici**, pendant la
circulation, pas au moment de la vérification de disponibilité :
**`consommerMatieresPour(idProduit)`** (ligne 1288), appelée depuis un
poste marqué `consommeMatiere=true` (ligne 46492, dans le code d'agent
`PosteGenericAgent`), décrémente
`FicheMatiere.stockDisponible -= l.quantiteParUnite` pour chaque ligne
de nomenclature, **une unité à la fois**, au moment où l'unité termine
effectivement ce poste. Voir §5 pour l'implication critique de ce
décalage temporel.

### 1.8 Deliver et clôture

Progression suivie via `termines` (nombre d'unités `TERMINE`,
ligne ~13542). Quand `termines >= cmd.qte` :

- Si `cmd.idCommande` commence par `"REAPPRO_"` : clôture spécifique
  sans client (`cmd.statut = "SERVIE"`, ligne 13555) — chemin MTS
  autonome, pas MTO client.
- Sinon (commande cliente MTO ou MTS) : clôture via le chemin Deliver
  standard, terminant par
  `cmd.statut = (time() <= cmd.tPromise) ? "SERVIE" : "EN_RETARD"`
  (ligne 13606, et un second site identique ligne 5867 pour le chemin
  de livraison directe MTS).

`commandeEstTerminale(cmd)` (ligne 10164) centralise la définition :
`"SERVIE".equals(s) || "EN_RETARD".equals(s) || "REFUSEE".equals(s) ||
s.startsWith("BLOQUE")`.

### 1.9 Synthèse du chemin réellement actif

```
genererCommande()                         [typeCommande = mode GLOBAL de run]
  -> analyserStockCommandeOrchestree()    [MTS court-circuite ici si stock OK]
       -> (branche non-MTS) analyserMatiereCommandeOrchestree()
            -> matOK ? tracerEtPlanifierProductionCommande()
                      : EN_APPROVISIONNEMENT -> declencherApprovisionnementCommande()
                                              -> FINALISER_APPROVISIONNEMENT (différé)
                                              -> (retour vers production, non vérifié en détail)
       -> tracerEtPlanifierProductionCommande() [re-check matière, PRODUCTION_PLANIFIEE]
            -> LANCER_PRODUCTION (différé, individuel, sans file)
                 -> lancerProductionCommandeOrchestree()
                      -> FluxEntity x cmd.qte, circulation Make
                      -> consommerMatieresPour() par unité, par poste
                      -> clôture -> SERVIE / EN_RETARD / BLOQUE_* / REFUSEE (jamais atteint)
```

`carnetCommandesMTO` et `deciderTypeCommande()` existent, sont
fonctionnellement cohérents entre eux, mais **ne font pas partie de ce
chemin**.

---

## 2. Matrice de complétude MTO

| Capacité | Statut | Preuve |
|---|---|---|
| Génération MTO | **PARTIEL** | `typeCommande` fixé par bascule globale de run (`modeSCORActif()`, ligne 8521), pas par décision par commande ; `deciderTypeCommande()` (ligne 51465) existe et serait correcte mais n'est jamais appelée |
| Nomenclature | **COMPLET** | `ScenarioFlux.nomenclature` / `LigneNomenclature` lus et vérifiés à deux reprises (`analyserMatiereCommandeOrchestree`, `tracerEtPlanifierProductionCommande`) |
| Explosion des besoins | **PARTIEL** | Calcul ligne par ligne correct (`besoin = quantiteParUnite * qte`, ligne 4857) mais uniquement au niveau "suffisant oui/non" ; pas de besoin net agrégé multi-commandes (voir §5) |
| Disponibilité matière | **COMPLET** (lecture) | `matieresSuffisantesPourScenario()` (ligne 4836), lecture correcte de `FicheMatiere.stockDisponible` |
| Réservation matière | **ABSENT** | Aucune réservation formelle entre le contrôle et la consommation ; voir §5, risque de double engagement |
| Consommation matière | **COMPLET** | `consommerMatieresPour()` (ligne 1288), décrément correct par unité produite |
| Approvisionnement Source | **PARTIEL** | Chemin présent et tracé (`declencherApprovisionnementCommande`, ligne 5404) mais non relu ligne à ligne dans cette passe ; reprise post-réception non vérifiée précisément |
| Réception matière | **À TESTER RUNTIME** | `FicheMatiere.receptionsAttendues`/`traiterEcheances()` existent (ligne 55280) ; comportement non tracé jusqu'au bout dans cette passe |
| Reprise après approvisionnement | **À TESTER RUNTIME / À AUDITER (MTO-1)** | `finaliserApprovisionnementCommande()` non lu ligne à ligne |
| Production | **COMPLET** | `lancerProductionCommandeOrchestree()` (ligne 5667), création d'entités et route confirmées |
| Ordonnancement (structure dédiée) | **INERTE** | `carnetCommandesMTO` déclaré, trié, consommé par `ordonnancerProduction()` (ligne 49568, correctement gatée sur `CA-sM2`/`strategieRealisation="MTO"`, ligne 24040), mais **jamais alimenté** (`grep carnetCommandesMTO\.add` = 0 résultat) |
| Ordonnancement (réellement actif) | **PARTIEL** | Chaque commande est planifiée individuellement et indépendamment via action différée ; pas de priorité ni d'EDD entre commandes concurrentes (voir §4) |
| Multi-commandes | **À TESTER RUNTIME** | Le pipeline semble supporter N commandes en parallèle (actions différées indépendantes), mais le risque de concurrence matière (§5) n'a pas été observé en exécution dans cette passe |
| Concurrence postes | **À TESTER RUNTIME** | Mécanisme standard AnyLogic (files de postes) ; non audité spécifiquement MTO dans cette passe |
| Deliver | **COMPLET** | Chemin de clôture clientèle standard partagé avec MTS, confirmé ligne 13606 |
| Retard / tPromise | **COMPLET** | `resoudreEngagementClient()` (ligne 8548) et clôture SERVIE/EN_RETARD (ligne 13606) |
| KPI / VSM | **COMPLET** | `kpiEntrepriseFocale`/`kpiGlobal` alimentés indépendamment du type de commande (voir audit AN-05, non re-détaillé ici) |
| SCOR | **COMPLET** | Codes SCOR tracés à chaque étape via `tracerFluxHierarchique()` |
| Terminalité | **COMPLET** | `commandeEstTerminale()` (ligne 10164) centralise bien les 4 issues terminales |
| Export ABox/Excel | **COMPLET** | Export générique, non filtré par `typeCommande` (confirmé lors de l'audit AN-05) |

**Aucun élément n'est déclaré COMPLET sans la ligne de preuve
correspondante ci-dessus.**

---

## 3. `carnetCommandesMTO`

- **Déclaration** : champ `PlainVariable` de type
  `java.util.ArrayList<CommandeAgent>`, valeur initiale
  `new java.util.ArrayList<CommandeAgent>()` (ligne 48895-48905).
- **Propriétaire** : classe `CoordinatorAgent`
  (`ActiveObjectClass Name=CoordinatorAgent`, confirmé par
  l'`AdditionalClassCode` contenant `strategieRealisation` à la même
  classe, ligne 48600-48605). Chaque instance de `CoordinatorAgent` a
  donc son propre carnet (10 instances créées par
  `initSupervisorsMacro()`, ligne 24036, dont `CA-sM2` =
  coordinateur Make/MTO).
- **Sites de lecture** : `.size()` (lignes 23828, 49617/49640, 51521,
  51529), `.get(0)` (ligne 49617 dans `ordonnancerProduction()`),
  `.isEmpty()` (ligne 49588).
- **Sites d'écriture** : `.remove(0)` (ligne 49634, dans
  `ordonnancerProduction()`, après consommation). **`.add(` :
  zéro occurrence dans tout le fichier.**
- **Tri** : `java.util.Collections.sort(carnetCommandesMTO, new
  Comparator<CommandeAgent>() { ... })` (ligne 49610), critère à deux
  niveaux : `cmd.priorite` (1=urgente, 2=normale, 3=basse) puis EDD
  (`cmd.tPromise` croissant) à égalité de priorité.
- **Appels réels** : la fonction qui trie/consomme,
  `ordonnancerProduction()` (ligne 49568), est bien appelée depuis un
  `<Action>` (ligne 49051, probablement un événement périodique
  AnyLogic — non confirmé comme cyclique précis dans cette passe, mais
  la présence d'un appel actif est confirmée).
- **Relation avec `actionsMetierDifferees`** : aucune. Les deux
  mécanismes sont indépendants et ne se référencent jamais mutuellement
  dans ce fichier.
- **Relation avec les files de postes** : aucune ; `carnetCommandesMTO`
  est en amont de toute mise en circulation physique
  (`lancerProductionCommandeOrchestree` crée les `FluxEntity`
  directement, sans jamais consulter le carnet).

**Diagnostic formellement confirmé** : *« structure prévue pour
ordonnancement MTO mais jamais alimentée »* est **exact**. La preuve
est double et indépendante :
1. Zéro appel à `.add(` sur `carnetCommandesMTO` dans tout le fichier.
2. Le chemin réellement actif (`tracerEtPlanifierProductionCommande()`
   → `LANCER_PRODUCTION` différé) ne référence jamais
   `carnetCommandesMTO`, ni directement ni indirectement.

La logique de tri/consommation elle-même (`ordonnancerProduction()`)
est correcte et correctement gatée (`"sM".equals(idMacroProcessus) &&
"MTO".equals(strategieRealisation)`, vrai pour `CA-sM2` d'après
`initSupervisorsMacro()`, ligne 24040 : `{"CA-sM2", "sM", "sM2",
"MTO"}`). Ce n'est pas un bug de logique interne, c'est un défaut de
branchement en amont : rien n'alimente jamais la structure que cette
logique consomme.

Aucune correction appliquée, conformément à la consigne.

---

## 4. Ordre réel des commandes MTO

Le chemin actif (§1.6) planifie `LANCER_PRODUCTION` **individuellement
par commande**, via `planifierAvecEchelle(...)`, dès que sa propre
analyse matière aboutit. Il n'existe **aucun point de rendez-vous**
entre commandes MTO concurrentes avant leur lancement production : ce
n'est donc ni strictement FIFO, ni LIFO, ni EDD, ni une priorité
explicite au sens d'une file arbitrée — c'est une **concurrence libre
non arbitrée**. L'ordre effectif d'exécution dépend uniquement de
l'instant où chaque action différée individuelle arrive à échéance, qui
dépend lui-même de la vitesse à laquelle chaque commande franchit
`analyserMatiereCommandeOrchestree()` (immédiat si matière disponible,
ou décalé du délai fournisseur sinon).

- **Priorité commande** : le champ `cmd.priorite` existe et est utilisé
  par le comparateur mort de `carnetCommandesMTO`
  (`ordonnancerProduction()`), mais n'influence **rien** dans le
  chemin actif.
- **Priorité lot** : aucune structure identifiée au niveau du lot
  (chaque commande produit `cmd.qte` unités en une seule vague, sans
  sous-lots).
- **Priorité unité/poste** : gérée par le mécanisme standard de file
  AnyLogic au niveau de chaque poste physique (hors périmètre
  MTO-spécifique ; comportement standard, non audité en détail ici).

**Conséquence pratique** : deux commandes MTO créées à des instants
proches, avec de la matière disponible pour les deux au moment de leur
contrôle respectif, seront lancées en production dans l'ordre où leurs
actions différées `LANCER_PRODUCTION` arrivent à échéance — un ordre
proche d'un FIFO *de facto* dans le cas simple (aucun retard
d'approvisionnement), mais qui devient imprévisible dès qu'un
approvisionnement intervient pour l'une des commandes et pas l'autre,
puisque celle qui a dû attendre le fournisseur peut se retrouver
lancée après une commande créée plus tard mais immédiatement
servable. Ce comportement n'a pas été observé en exécution dans cette
passe (classé **À TESTER RUNTIME**, voir fixture MTO-C, §6).

---

## 5. Stock et matières MTO

Champs audités dans `FicheMatiere` (ligne 55244) : tous les champs
listés dans la demande sont présents et confirmés :
`stockDisponible`, `stockInitialConfigure`
(`stockInitialConfigureDefini` en complément),
`stockSecurite`, `pointCommande`, `quantiteEconomique`,
`receptionsAttendues` (`List<ReceptionAttendue>`),
`delaiObtentionHeures`, `idFournisseur`. `FicheMatiere` possède aussi
`traiterEcheances(maintenant)` (ligne 55280), qui bascule les
réceptions échues de `receptionsAttendues` vers `stockDisponible`.

**Séquence temporelle réelle** (reconstituée à partir de §1.4 et
§1.7) :

1. **Calcul du besoin** : à chaque appel de
   `analyserMatiereCommandeOrchestree()`, une seule fois par commande
   (sauf reprise après approvisionnement).
2. **Vérification du stock** : `matieresSuffisantesPourScenario()`
   (ligne 4836) — **lecture pure**, aucune écriture sur
   `FicheMatiere`.
3. **Réservation** : **absente**. Rien ne marque la matière comme
   "engagée" entre l'étape 2 et l'étape 4.
4. **Consommation réelle** : `consommerMatieresPour()` (ligne 1288),
   déclenchée **plus tard**, au moment où une unité physique termine
   effectivement un poste marqué `consommeMatiere=true` (ligne 46492).
   Entre la commande client (création de `cmd`) et ce point, il y a
   au minimum : l'analyse stock, l'analyse matière, la planification
   `LANCER_PRODUCTION` (délai `dureeReelleChaine(...)`, non nul), la
   création des `FluxEntity`, puis le temps de parcours jusqu'au
   premier poste consommateur de matière.

**Double engagement matière : structurellement possible.** Deux
commandes dont les fenêtres d'analyse matière se chevauchent (l'une
n'a pas encore atteint son poste consommateur quand l'autre fait son
contrôle de disponibilité) peuvent toutes les deux lire le même
`stockDisponible` suffisant et être toutes les deux autorisées à
produire, alors que le stock réel ne couvre qu'une seule des deux. Ce
risque est confirmé **par lecture du code** (absence de toute
réservation entre contrôle et consommation) mais son **impact observé
en exécution n'a pas été mesuré** dans cette passe — classé **À
CONFIRMER PAR RUNTIME**, fixture dédiée MTO-C (§6).

**Réceptions en cours** : `FicheMatiere.totalReceptionsAttendues()`
(ligne 55275) existe et additionne les réceptions en attente, mais
n'est **pas utilisée dans `matieresSuffisantesPourScenario()`**, qui
ne regarde que `stockDisponible`. Un besoin matière qui serait déjà
couvert par une réception attendue non encore arrivée n'est donc pas
anticipé : la commande déclenchera un **nouvel** approvisionnement même
si un approvisionnement suffisant est déjà en transit pour un autre
produit/commande. Ce point est directement pertinent pour DDMRP, dont
le concept *Open Supply* existe précisément pour agréger le stock
disponible et les réceptions en transit avant de décider d'un nouveau
réapprovisionnement (voir §7).

---

## 6. Fixtures runtime à préparer (conception uniquement, non exécutées)

### MTO-A — matière suffisante dès le départ
- Stocks initiaux : toutes les `FicheMatiere` de la nomenclature du
  scénario testé avec `stockDisponible` largement au-dessus du besoin
  d'une commande.
- Quantité commande : 1 commande, `qte` modérée (ex. 5).
- Nomenclature : celle du scénario nominal déjà chargé.
- Résultat attendu : `analyserMatiereCommandeOrchestree()` passe
  directement en production (`matOK = true`), aucun passage par
  `EN_APPROVISIONNEMENT`.
- Statuts attendus : `EN_ATTENTE` → `PRODUCTION_PLANIFIEE` → `SERVIE`
  ou `EN_RETARD` selon `tPromise`.
- Condition terminale : `commandeEstTerminale(cmd) == true`,
  `termines == cmd.qte`.

### MTO-B — matière insuffisante → Source → réception → Make
- Stocks initiaux : au moins une `FicheMatiere` de la nomenclature avec
  `stockDisponible` strictement inférieur au besoin.
- Quantité commande : 1 commande, `qte` fixée pour garantir
  l'insuffisance.
- Nomenclature : celle du scénario nominal.
- Résultat attendu : `cmd.statut = "EN_APPROVISIONNEMENT"`, reprise via
  `FINALISER_APPROVISIONNEMENT` après le délai fournisseur, puis
  production.
- Statuts attendus : `EN_ATTENTE` → `EN_APPROVISIONNEMENT` →
  `PRODUCTION_PLANIFIEE` → `SERVIE`/`EN_RETARD`.
- Condition terminale : idem MTO-A, avec vérification additionnelle que
  `FicheMatiere.receptionsAttendues` est bien vidée après réception
  (`traiterEcheances`).

### MTO-C — 2 ou 3 commandes MTO concurrentes avec matière limitée
- Stocks initiaux : `stockDisponible` suffisant pour **une seule** des
  commandes testées, insuffisant pour la somme des trois.
- Quantité commande : 2 à 3 commandes créées à des instants rapprochés
  (quelques secondes d'écart), même nomenclature.
- Résultat attendu : objectif de la fixture = **observer** si le
  double engagement matière décrit en §5 se produit réellement (deux
  commandes autorisées en production alors que le stock ne couvre
  qu'une seule), et si oui, quelle en est la conséquence visible
  (`stockDisponible` négatif tronqué à 0 par `Math.max(0, ...)` ligne
  1314, log d'alerte "Stock matiere insuffisant pendant la
  production").
- Statuts attendus : à déterminer par l'exécution — c'est le but de
  cette fixture, pas une prédiction.
- Condition terminale : les 3 commandes atteignent un statut terminal ;
  comparer l'ordre réel de clôture à l'ordre de création (test de la
  conclusion du §4).

### MTO-D — commande MTO avec retard fournisseur forcé
- Stocks initiaux : matière insuffisante, comme MTO-B.
- Quantité commande : 1 commande.
- Configuration additionnelle : utiliser le mécanisme de test de retard
  fournisseur déjà présent dans le modèle
  (`retardFournisseurTestActif`, `scenarioCompatibleRetardFournisseur`,
  `consommerRetardFournisseurPourScenario`, vus en §1.4/§1.5) pour
  forcer un délai d'approvisionnement anormalement long.
- Résultat attendu : `cmd.statut` reste `EN_APPROVISIONNEMENT`
  longtemps, `tPromise` est probablement dépassé avant la fin de
  production.
- Statuts attendus : clôture en `EN_RETARD` plutôt que `SERVIE`.
- Condition terminale : `commandeEstTerminale(cmd) == true` avec
  `statut == "EN_RETARD"`.

---

## 7. Audit DDMRP — mapping avec le modèle existant

Recherche exhaustive de vocabulaire DDMRP dans le `.alp` : **aucune**
occurrence de *Decoupling Point*, *ADU*, *Net Flow Position*,
*Qualified Demand*, *Order Spike*, *Buffer Profile* au sens DDMRP.
Les occurrences de « buffer » et « décou(plage/plée) » trouvées
(`grep -in "buffer\|decoupl"`) sont toutes des usages génériques
(buffers physiques de poste AnyLogic, ou « découplage » au sens
architecture logicielle — ex. ligne 7658 : *« DECOUPLE de l'ecriture
Excel »*), sans rapport avec DDMRP. **Le terrain est donc vierge : rien
à adapter, tout à construire.**

| Concept DDMRP | Structure actuelle disponible | Manque | Emplacement recommandé |
|---|---|---|---|
| Decoupling Point | Aucune notion de point de découplage de stock ; `PosteGenericAgent` de type `STOCKAGE` existe comme point physique de stock produit fini, et `FicheMatiere` comme point de stock matière, mais aucun n'est marqué comme "buffer stratégique" | Marqueur explicite par matière/poste | Nouveau champ booléen sur `FicheMatiere` (§8, Option 1 ou 2) |
| ADU / Average Daily Usage | Aucune moyenne glissante de consommation par matière. `consommerMatieresPour()` décrémente sans historiser. Il existe un historique de demande pour la prévision produit fini (`Prevision*` côté DataCo, hors périmètre générique) mais rien côté matière | Historisation de consommation par `FicheMatiere` + fenêtre de calcul | DDMRP-1/DDMRP-2 |
| Decoupled Lead Time | `FicheMatiere.delaiObtentionHeures` existe déjà et est directement réutilisable comme composant du DLT pour une matière achetée | Agrégation multi-niveaux si nomenclature imbriquée (non constatée dans ce modèle : nomenclature à un seul niveau, `LigneNomenclature` plate) | Réutiliser `delaiObtentionHeures` tel quel |
| Lead Time Factor | Absent | Facteur de zone par profil de buffer | DDMRP-1 (config) |
| Variability Factor | Absent | Idem | DDMRP-1 (config) |
| Red/Yellow/Green Zone, Top of Red/Yellow/Green | Absent ; `pointCommande`/`quantiteEconomique` (politique (s,Q) actuelle) jouent un rôle voisin mais ne sont pas des zones DDMRP | Calcul des trois zones à partir de ADU × DLT × facteurs | DDMRP-2, formule **à valider bibliographiquement** avant implémentation |
| On-hand | `FicheMatiere.stockDisponible` | — (déjà disponible) | Réutiliser tel quel |
| Open Supply | `FicheMatiere.totalReceptionsAttendues()` (ligne 55275) existe mais n'est **pas utilisé** dans le contrôle de disponibilité actuel (§5) | Rien à créer, mais à **connecter** | DDMRP-3 |
| Qualified Demand | Absent au sens DDMRP (demande significative à soustraire du Net Flow). Le modèle a bien `cmd.qte` par commande mais aucune notion de "demande qualifiée" agrégée par matière | Agrégation des besoins nets de commandes ouvertes par matière | DDMRP-3, formule à définir |
| Order Spike | Absent | Détection de pics > seuil | DDMRP-3, **à valider bibliographiquement** |
| Net Flow Position | Absent | `On-hand + Open Supply - Qualified Demand`, formule standard DDMRP, directement calculable une fois Open Supply et Qualified Demand connectés | DDMRP-3 |
| Replenishment Recommendation | Partiellement analogue à `declencherProductionAutonome()`/`declencherApprovisionnementCommande()`, mais ceux-ci réagissent à un seuil (s,Q) simple, pas à une position de flux net | Logique de décision DDMRP distincte, à ne pas fusionner silencieusement avec (s,Q) existant | DDMRP-4 |
| Buffer Status / Priority | Absent | Calcul de pénétration de zone pour prioriser les réapprovisionnements entre matières | DDMRP-4/DDMRP-5 |

Aucune formule DDMRP n'a été implémentée ou inventée dans cette passe.
Toute formule de zone, de facteur ou de seuil figure ci-dessus comme
« à valider bibliographiquement » et reste à spécifier avant DDMRP-2.

---

## 8. Point d'intégration DDMRP

| Critère | Option 1 — intégré dans `FicheMatiere` | Option 2 — `DDMRPBuffer` lié à `FicheMatiere` | Option 3 — moteur séparé (Main/TacticalAgent) |
|---|---|---|---|
| Séparation des responsabilités | Faible : `FicheMatiere` mélangerait état physique (s,Q) et état DDMRP | Bonne : DDMRP reste un objet dédié, `FicheMatiere` reste la source de vérité physique (`stockDisponible`, `receptionsAttendues`) | Bonne également, mais le moteur doit relire l'état de chaque `FicheMatiere` à chaque cycle, couplage implicite par convention plutôt que par référence directe |
| Testabilité | Faible : impossible de tester DDMRP sans instancier tout `FicheMatiere` | Bonne : `DDMRPBuffer` testable isolément avec des valeurs `FicheMatiere` simulées | Bonne, mais plus de code de câblage à tester (le moteur doit itérer sur toutes les matières) |
| Généricité | Risque de coupler DDMRP à chaque usage futur de `FicheMatiere` (y compris non-DDMRP) | Bonne : une `FicheMatiere` peut exister sans `DDMRPBuffer` (buffer optionnel) | Bonne, mais risque de dupliquer la logique de sélection "quelles matières sont bufferisées" |
| Compatibilité MTO/MTS | Neutre dans les trois options : DDMRP s'applique à la matière, pas au type de commande cliente (voir §10, distinction des deux priorités) | Neutre | Neutre |
| Impact JSON | Un nouveau bloc de config par matière dans le scénario JSON, dans les trois cas (voir §13) | Identique | Identique, mais potentiellement un bloc de config global en plus (paramètres de moteur) |
| Impact AnyLogic | Minime : nouveaux champs sur une classe Java existante | Minime : nouvelle classe Java simple (`DDMRPBuffer implements Serializable`), suit le patron déjà utilisé par `ReceptionAttendue` | Modéré : nouvel agent ou nouvelles fonctions sur `TacticalAgent` existant (`sP2` = Plan Source, déjà le bon holon SCOR pour piloter l'approvisionnement) |
| Dette technique | Élevée si DDMRP doit un jour être désactivable par matière (nécessiterait des champs conditionnels dans `FicheMatiere`) | Faible : activer/désactiver DDMRP = attacher ou non un `DDMRPBuffer` | Faible à modérée : le moteur peut ignorer les matières non configurées |

**Recommandation de conception (non codée)** : **Option 2**
(`DDMRPBuffer` comme structure liée à `FicheMatiere`, référencée
depuis `FicheMatiere` par un champ optionnel, ex.
`DDMRPBuffer ddmrpBuffer = null;`), avec le **calcul** des zones et de
la décision de réapprovisionnement porté par le `TacticalAgent` dont
`idMacroProcessus == "sS"` (déjà le holon de planification Source
existant, cohérent avec SCOR P2 — Plan Source). Cela suit le patron
déjà utilisé dans ce modèle pour `ReceptionAttendue` (petite classe
`Serializable` liée à `FicheMatiere`, logique de traitement portée par
une fonction séparée plutôt que par la classe de données elle-même) et
évite de coupler la décision DDMRP à la structure de données physique.

---

## 9. Pipeline cible MTO + DDMRP

```
Commande MTO
  -> besoin nomenclature                  (déjà existant, §1.4)
  -> demande qualifiée DDMRP              (DDMRP-3, nouveau : agrégation des besoins nets ouverts par matière)
  -> Net Flow Position                    (DDMRP-3, nouveau : On-hand + Open Supply - Qualified Demand)
  -> décision buffer                      (DDMRP-4, nouveau : zone de pénétration -> déclenche ou non un réapprovisionnement)
  -> Source si nécessaire                 (réutilise declencherApprovisionnementCommande(), adapté pour être déclenché par le buffer plutôt que par un seuil (s,Q) simple)
  -> réception                            (réutilise FicheMatiere.receptionsAttendues / traiterEcheances(), déjà existant)
  -> disponibilité matière                (réutilise matieresSuffisantesPourScenario(), à faire évoluer pour consulter Open Supply, §5)
  -> Make                                 (inchangé, §1.6-1.7)
  -> Deliver                              (inchangé, §1.8)
  -> clôture                              (inchangé, commandeEstTerminale(), §1.8)
```

**Décision explicite requise (non tranchée ici)** :

- **A.** DDMRP remplace uniquement la politique matière (s,Q)
  existante (`pointCommande`/`quantiteEconomique`), sans toucher à
  l'ordonnancement des commandes clientes.
- **B.** DDMRP remplace aussi l'ordonnancement MTO.
- **C.** DDMRP reste indépendant de l'ordonnancement client.

**Recommandation de conception** : **A + C combinés**. DDMRP, par
définition (Demand Driven **Material** Requirements Planning), porte
sur la décision de réapprovisionnement **matière**, pas sur l'ordre de
production des commandes clientes. Le remplacer par B mélangerait deux
décisions de nature différente (voir §10) et romprait la distinction
que DDMRP lui-même impose entre *Qualified Demand* (un signal agrégé
pour la matière) et la commande cliente individuelle (qui garde sa
propre logique de priorité/EDD, que ce soit l'actuelle absence
d'arbitrage constatée en §4, ou une future mise en service du carnet
existant, §3). Ceci n'est qu'une recommandation de conception ; aucune
implémentation n'a été faite.

---

## 10. Séparer deux priorités

**1. Priorité commande cliente MTO — « quelle commande produire
d'abord ? »** Candidats déjà présents dans le code mais non tous
actifs :
- FIFO : comportement *de facto* constaté en §4 en l'absence de tout
  retard fournisseur (non garanti, pas une règle explicite).
- `tPromise`/EDD : implémenté mais **inerte** dans le comparateur mort
  de `carnetCommandesMTO` (§3).
- Priorité explicite (`cmd.priorite`) : champ existant, également
  inerte pour la même raison.
- Retard courant : aucune règle de priorité basée sur un retard déjà
  constaté identifiée dans le chemin actif.

**2. Priorité DDMRP — « quel buffer/composant réapprovisionner
d'abord ? »** N'existe pas encore (DDMRP absent, §7). Serait calculée
à partir de la pénétration de zone (Buffer Status) de chaque
`DDMRPBuffer`, indépendamment de quelle commande cliente a généré le
besoin.

**Ces deux priorités ne doivent jamais être assimilées.** Une commande
cliente `priorite=1` (urgente) ne rend pas automatiquement sa matière
prioritaire dans l'arbitrage DDMRP inter-matières : DDMRP arbitre entre
*matières* en tension, pas entre *commandes* clientes. Si un jour une
commande urgente doit influencer DDMRP, cela doit être un signal
explicite et documenté (ex. contribution pondérée à la *Qualified
Demand*), jamais une confusion implicite des deux échelles.

---

## 11. ETO

Hors périmètre MTO-0, documenté sans modification. `modeSCORActif()`
(ligne 8521) traite `ETO` comme une troisième bascule globale de run,
au même niveau que `MTO`. `delaiPromessePourMode("ETO")` retourne
3600 s contre 1800 s pour `MTO` (ligne ~8528), seule différence de
traitement identifiée dans le chemin tracé en §1 : au-delà de ce délai
de promesse, MTO et ETO partagent exactement le même pipeline
opérationnel (`analyserStockCommandeOrchestree` → les deux
court-circuitent la branche MTS et tombent dans la même branche
`analyserMatiereCommandeOrchestree()`, §1.3). Aucune phase
d'ingénierie (conception, nomenclature spécifique au projet,
validation technique préalable) n'est représentée séparément : ETO
suit la nomenclature statique du `ScenarioFlux`, comme MTO. Non
modifié.

---

## 12. Architecture proposée (découpage futur)

- **MTO-1** — validation runtime du chemin actuel (exécuter MTO-A à
  MTO-D, §6 ; confirmer/infirmer §1.5 pour
  `declencherApprovisionnementCommande`/`finaliserApprovisionnementCommande`
  ligne à ligne).
- **MTO-2** — sécurisation matière/concurrence (traiter le risque de
  double engagement, §5 ; décider s'il faut une réservation explicite
  ou si DDMRP/Open Supply suffit à le couvrir).
- **MTO-3** — ordonnancement MTO réel (décider : réactiver
  `carnetCommandesMTO`/`ordonnancerProduction()` existants, ou les
  retirer si jugés obsolètes face à une solution DDMRP-driven).
- **DDMRP-1** — structures de données et configuration
  (`DDMRPBuffer`, champs JSON par matière, §13).
- **DDMRP-2** — calcul des buffers (zones, formules validées
  bibliographiquement avant codage).
- **DDMRP-3** — Net Flow Position / Qualified Demand (connexion à
  `totalReceptionsAttendues()` déjà existant, §7).
- **DDMRP-4** — génération d'approvisionnement piloté par buffer.
- **DDMRP-5** — dashboard/KPI/exports DDMRP.
- **MTO-DDMRP-TEST** — tests intégrés complets (rejouer MTO-A à MTO-D
  avec DDMRP actif, comparer aux résultats MTO-1).

Ce découpage est une proposition ; il sera corrigé par l'audit runtime
réel de MTO-1.

---

## 13. Impact JSON (paramètres futurs à évaluer, aucun JSON modifié)

Paramètres DDMRP probablement configurables **par matière**, à évaluer
lors de DDMRP-1 (aucun retenu définitivement ici) :

- `ddmrpEnabled` (booléen, active/désactive DDMRP pour cette matière —
  cohérent avec l'Option 2 du §8, buffer optionnel)
- `decouplingPoint` (booléen ou enum, marque la matière comme point de
  découplage stratégique)
- `aduMode` (enum, ex. moyenne simple vs. pondérée — à ne retenir que
  si une méthode de calcul est réellement justifiée)
- `aduWindow` (durée, fenêtre de calcul de l'ADU)
- `leadTimeFactor` (facteur de zone, dépend du profil DLT)
- `variabilityFactor` (facteur de zone, dépend de la variabilité de la
  demande/offre)
- `orderSpikeThreshold` (seuil de détection de pic de demande)
- `minimumOrderQuantity` (déjà partiellement couvert par
  `quantiteEconomique`, à clarifier : coexistence ou remplacement)
- `bufferProfile` (regroupement nommé de facteurs réutilisable entre
  matières similaires, pattern DDMRP standard)

Chacun de ces paramètres reste à justifier individuellement lors de
DDMRP-1 ; cette liste n'est qu'un point de départ d'évaluation.

---

## 14. Compatibilité avec l'existant

| Élément existant | Impact DDMRP envisagé | Conflit identifié |
|---|---|---|
| Politique (s,Q) actuelle (`pointCommande`/`quantiteEconomique`) | Coexistence pendant la transition, puis remplacement probable pour les matières bufferisées (DDMRP) uniquement | Si les deux politiques restent actives simultanément sur la même matière sans exclusion mutuelle explicite : double déclenchement de réapprovisionnement (voir risques, §15) |
| MRP existant (`matieresSuffisantesPourScenario`, `consommerMatieresPour`) | Ces fonctions restent le point de vérité physique (on-hand, consommation) ; DDMRP s'ajoute en amont pour la décision de réapprovisionnement, ne les remplace pas | Risque si `matieresSuffisantesPourScenario` n'est jamais mis à jour pour consulter Open Supply (§5) : DDMRP calculerait un Net Flow correct, mais la vérification de faisabilité commande continuerait de l'ignorer |
| Réapprovisionnement autonome MTS (`declencherProductionAutonome`, `verifierPolitiqueStockProduit`) | Distinct : porte sur le stock **produit fini**, pas sur le stock **matière**. DDMRP ne s'applique pas directement ici sauf extension future explicite | Aucun conflit direct identifié, périmètres différents (produit fini vs. matière première) |
| MTO (chemin §1) | Le déclenchement Source actuel (`declencherApprovisionnementCommande`) deviendrait un consommateur de la décision DDMRP plutôt qu'un déclencheur direct par seuil simple | Nécessite de faire évoluer `declencherApprovisionnementCommande` sans casser son rôle actuel de traçage AER (Source S1-S3) |
| `REAPPRO_*` (production autonome MTS) | Aucun changement direct attendu (DDMRP porte sur la matière, pas sur le produit fini) | Aucun si le périmètre reste strictement matière |
| `TacticalAgent` | Lieu d'intégration recommandé (§8, Option 2), `idMacroProcessus == "sS"` déjà existant | Aucun si le moteur DDMRP est ajouté comme nouvelles fonctions plutôt que modification des fonctions tactiques existantes |
| `BlackboardAgent` | Pourrait recevoir de nouveaux KPI DDMRP (DDMRP-5), suivant le patron `kpiGlobal`/`kpiEntrepriseFocale` déjà en place | Aucun si ajouté comme nouveaux champs, pas de modification des champs existants |
| SCOR Source | DDMRP s'inscrit naturellement dans P2 (Plan Source), déjà représenté par `TacticalAgent("sS")` | Aucun |
| KPI | Nouveaux KPI DDMRP à ajouter sans toucher aux KPI VSM existants (`kpiGlobal`/`kpiEntrepriseFocale`, hors périmètre de ce chantier) | Aucun si strictement additif |
| Terminalité | DDMRP ne doit influencer aucun statut terminal de commande (`commandeEstTerminale`, §1.8) — DDMRP porte sur la matière, pas sur le cycle de vie commande | Risque si une future implémentation couple par erreur un statut commande à un état de buffer DDMRP (voir risques, §15) |
| ABox | Nouveaux triples DDMRP à ajouter en suivant le patron d'export déjà en place (`aboxTriple`/`aboxUri`), sans toucher aux clés AN-05 déjà généralisées (`entreprise_focale_*`) | Aucun si additif |
| E4 | Aucun lien direct ; E4 porte sur x1-x4 et l'expérience Parameter Variation, hors périmètre matière. Ce chantier doit rester indépendant, conformément à la consigne | Aucun constaté |

---

## 15. Risques (P0/P1/P2)

**P0 — bloquants/critiques :**
- **Double réservation matière** (§5) : confirmé structurellement
  possible par lecture du code (absence de réservation entre contrôle
  et consommation) ; impact non mesuré en exécution. À confirmer par
  MTO-C avant toute implémentation DDMRP qui s'appuierait sur un état
  matière supposé fiable.
- **Double réapprovisionnement MRP + DDMRP** : si DDMRP est ajouté sans
  désactiver explicitement la politique (s,Q) existante sur les
  mêmes matières, les deux mécanismes pourraient déclencher des
  commandes fournisseur indépendantes pour le même besoin.
- **DDMRP qui modifie par erreur MTS** : le réapprovisionnement
  produit fini MTS (`declencherProductionAutonome`) et le futur
  réapprovisionnement matière DDMRP opèrent sur des objets différents
  (`PosteGenericAgent` de type STOCKAGE vs. `FicheMatiere`) ; un futur
  branchement incorrect qui ferait lire un buffer DDMRP matière comme
  s'il s'agissait d'un seuil produit fini casserait silencieusement la
  politique MTS actuelle.

**P1 — significatifs :**
- **Boucle de réapprovisionnement non terminale** : si Open Supply
  n'est jamais correctement vidé des réceptions déjà arrivées (erreur
  de synchronisation entre `traiterEcheances()` et un futur calcul
  DDMRP), un Net Flow Position pourrait rester artificiellement bas et
  redéclencher indéfiniment des commandes.
- **Interaction `simToRealSeconds`** (ligne 2168, échelle temps
  simulé/réel) : les futurs calculs DDMRP de type ADU (par jour) et
  DLT devront être exprimés dans la bonne échelle temporelle,
  cohérente avec `dureeReelleChaine()`/`simToRealSeconds` déjà utilisés
  ailleurs — un mélange d'échelles produirait des zones de buffer
  totalement incorrectes sans erreur visible.
- **Concurrence MTO** (§4) : absence d'arbitrage explicite entre
  commandes MTO concurrentes, déjà un risque indépendamment de DDMRP.
- **Confusion priorité buffer / priorité commande** (§10) : risque de
  conception si les deux échelles de priorité sont un jour fusionnées
  sans justification explicite.

**P2 — mineurs/à surveiller :**
- **Double comptage Open Supply** : si une réception attendue est un
  jour comptée à la fois dans `FicheMatiere.receptionsAttendues` et
  dans une structure DDMRP parallèle plutôt que par référence unique.
- **Buffer recalculé avec de mauvaises unités** : risque de confusion
  entre quantités par commande vs. quantités par jour/période lors du
  calcul de l'ADU.

---

## 16. Récapitulatif — aucune implémentation

Conformément à la consigne : `carnetCommandesMTO` n'a pas été
réparé, ETO n'a pas été modifié, DDMRP n'a pas été implémenté, C3/E4
n'a pas été touché, aucun `.alp` et aucun `.json` n'a été modifié pour
produire ce document.

---

## 17. Audit complémentaire — cycle de vie Source → Make

**Nature : audit uniquement, complète MTO-0 avant toute
implémentation.** Branche `feature/mto-ddmrp-foundation`, HEAD
`67105942e00c4d20cd0a13053512aa6d0ae1558b`. Aucun `.alp`/`.json`
modifié. Aucune campagne runtime exécutée dans cette passe.

### 17.1 Les cinq fonctions, lues intégralement

**`declencherApprovisionnementCommande(cmd, sc, qteCommande)`**
(ligne 5404-5471). Pour chaque `LigneNomenclature` de `sc` : calcule
`manque = besoin - f.stockDisponible` ; si `manque <= 0.0001`,
`continue` (rien à faire pour cette ligne). Sinon : **uniquement des
effets de traçabilité** — `ajouterSuiviDetailleHorodate()` (deux
appels, un immédiat, un décalé de 1 s pour « matière en transit »),
`enregistrerTraceSourceApprovisionnementCommande()`,
`lancerFluxVisuelSourceApprovisionnement()`,
`enregistrerFluxSupplyChainMetier()`, `emettreFluxLog()`. **Aucune
écriture sur `FicheMatiere` et aucune création de `ReceptionAttendue`
dans cette fonction.** C'est un déclencheur **narratif/visuel**, pas un
déclencheur d'approvisionnement physique.

**`finaliserApprovisionnementCommande(cmd)`** (ligne 3423-3506).
Appelée en différé après `delaiApprovisionnementReelMax(sc, cmd.qte)`
(ligne 5380, calculé **avant** l'appel à
`declencherApprovisionnementCommande()`, ligne 3371-3373 — c'est donc
une estimation figée au moment de la décision, pas une lecture du
délai réellement écoulé). Pour chaque ligne de nomenclature :
`manque = besoin - f.stockDisponible` recalculé, et **si
`manque > 0.0001` : `f.stockDisponible += manque` directement**
(ligne 3446). **Aucune lecture ni écriture de
`f.receptionsAttendues` dans cette fonction.** Après la boucle, re-vérifie
`configurationOK && matieresSuffisantesPourScenario(sc, cmd.qte)` ; si
faux → `cmd.statut = "BLOQUE_MATIERE"`, terminal, sortie. Si vrai :
trace AER (`MaterialReceived` → `OperationalReport` →
`ProcurementCompleted` → `MaterialAvailable`), `cmd.statut =
"MATIERES_DISPONIBLES"`, puis **appel direct à
`tracerEtPlanifierProductionCommande(cmd)`** (ligne 3506) — referme la
boucle vers la production décrite au §1.6 du présent document.

**`matieresSuffisantesPourScenario(sc, qte)`** (ligne 4836-4859,
relue intégralement, confirme la lecture du §1.4/§5) : lecture pure
de `FicheMatiere.stockDisponible`, aucune écriture, mode *fail-closed*
(scénario/nomenclature/ligne invalide → `false`).

**`consommerMatieresPour(idProduit)`** (ligne 1288-1318, relue
intégralement) : pour chaque ligne de nomenclature du premier
`ScenarioFlux` correspondant à `idProduit`, si
`f.stockDisponible < quantiteParUnite` → log d'alerte *« Stock matiere
insuffisant pendant la production »* (`ajouterSuiviDetaille`, ligne
~1297), **puis quoi qu'il arrive** :
`f.stockDisponible = Math.max(0, f.stockDisponible -
l.quantiteParUnite)` (ligne 1314). La consommation n'est donc jamais
bloquante : elle tronque à zéro plutôt que d'empêcher l'unité de
continuer son parcours.

**`traiterEcheances(maintenant)`** (méthode de `FicheMatiere`, ligne
55284-55295, relue intégralement) : itère `receptionsAttendues`,
crédite `stockDisponible += r.quantite` et retire l'élément
(`it.remove()`) pour chaque réception dont `dateArriveePrevue` est
atteinte. Traitement correct et idempotent par construction (une
réception traitée est immédiatement retirée de la liste, elle ne peut
pas être retraitée). Appelée depuis **une seule fonction**,
`calculerBesoinsNets()` (ligne 1121, appel à `f.traiterEcheances()`
ligne 1140), elle-même appelée depuis **un seul site**,
ligne 53079 (`main.calculerBesoinsNets();`), dans ce qui est, d'après
les commentaires adjacents (« cycle tactique sM », « 15s habituellement »,
lignes 1124 et 2368), un événement périodique du `TacticalAgent`.

### 17.2 Constat central : deux mécanismes d'approvisionnement matière indépendants

La lecture complète des cinq fonctions révèle que **`FicheMatiere`
est alimentée par deux chemins totalement disjoints, qui ne se
connaissent pas l'un l'autre** :

- **Mécanisme A — approvisionnement « ad hoc » déclenché par une
  commande** (`analyserMatiereCommandeOrchestree()` →
  `declencherApprovisionnementCommande()` [traçabilité seule] → délai
  `delaiApprovisionnementReelMax()` → `finaliserApprovisionnementCommande()`
  [crédite directement `f.stockDisponible` du montant manquant pour
  CETTE commande]). **N'utilise jamais `ReceptionAttendue` ni
  `receptionsAttendues`.** Emprunté à la fois par les commandes
  clientes MTO/ETO (§1.4-1.5) et par la production autonome REAPPRO_*
  (`declencherProductionAutonome()` appelle directement
  `analyserMatiereCommandeOrchestree()`, confirmé ligne ~3029).
- **Mécanisme B — politique (s,Q) périodique et autonome**
  (`calculerBesoinsNets()`, appelée toutes les ~15 s). Calcule un
  point de commande et une quantité économique par matière, **crée de
  vrais objets `ReceptionAttendue`** (ligne 1263) lorsque
  `stockProjete <= pointCommande`, et ne crédite le stock que plus
  tard, à l'échéance, via `traiterEcheances()`. Garde explicite : `if
  (productionAutonomeEnCours) return;` (ligne 1122) — **mais cette
  garde ne protège que contre une REAPPRO_* mono-produit en cours**
  (champ mis à `true`/`false` uniquement par
  `declencherProductionAutonome()`/sa clôture, lignes 3010/4064/13578).
  **Elle n'est jamais vérifiée ni modifiée par le chemin commande
  cliente MTO/ETO (Mécanisme A).**

**Conséquence directement vérifiable par lecture statique** : pour une
commande cliente MTO/ETO en pénurie d'une matière donnée, rien
n'empêche que, pendant la fenêtre où `cmd.statut ==
"EN_APPROVISIONNEMENT"` (entre `declencherApprovisionnementCommande()`
et `finaliserApprovisionnementCommande()`), le cycle périodique
`calculerBesoinsNets()` s'exécute au moins une fois sur la même
`FicheMatiere`, constate `stockProjete <= pointCommande` (ce qui est
probable puisque le stock est justement insuffisant) et **crée sa
propre `ReceptionAttendue` indépendante**, en plus du crédit direct que
`finaliserApprovisionnementCommande()` appliquera à l'échéance de son
propre délai. Les deux crédits s'additionnent sur le même
`stockDisponible`, sans qu'aucun des deux mécanismes ne consulte
l'état de l'autre. **Requalification (run final MTO-1, §20)** : la
lecture du code établit seulement que deux mécanismes de
réapprovisionnement indépendants peuvent agir sur la même situation
de pénurie, sans vue commune d'Open Supply. Le run final **n'a pas
observé de double crédit strict de la même quantité** : le
Mécanisme A a recalculé le manque à la réception et n'a crédité que
0/10/0. Le risque de décision non coordonnée est en revanche confirmé
en runtime. Distinct du double engagement déjà documenté au §5 (qui
portait sur deux commandes concurrentes utilisant le même Mécanisme A).

### 17.3 Réponses aux cinq questions posées

1. **Une réception attendue peut-elle être comptabilisée plusieurs
   fois ?** Non, pas au sein du Mécanisme B seul :
   `traiterEcheances()` retire chaque `ReceptionAttendue` de la liste
   au moment où elle est créditée (`it.remove()`, ligne 55293),
   traitement idempotent. **Démontré statiquement.**
2. **Une même matière peut-elle être réapprovisionnée deux fois pour
   un besoin déjà couvert ?** Oui, structurellement, par
   l'interaction non coordonnée entre le Mécanisme A (crédit direct
   par commande) et le Mécanisme B (politique (s,Q) périodique), comme
   démontré au §17.2. **Démontré statiquement** pour le mécanisme ;
   l'ampleur réelle (fréquence, quantité en excès) **nécessite un test
   runtime** (fixture MTO-C étendue, voir §17.5).
3. **Une commande peut-elle reprendre avant que la réception soit
   effectivement créditée ?** Non pour le Mécanisme A : le crédit
   (`f.stockDisponible += manque`) et la reprise
   (`tracerEtPlanifierProductionCommande(cmd)`) ont lieu **dans la
   même exécution synchrone** de `finaliserApprovisionnementCommande()`
   (lignes 3446 puis 3506) — aucune fenêtre entre les deux.
   **Démontré statiquement.** La question ne se pose pas pour le
   Mécanisme B de la même façon, puisqu'aucune commande n'attend
   directement sur lui (voir §17.2).
4. **Une consommation peut-elle conduire à un stock insuffisant ?**
   Oui : `consommerMatieresPour()` tronque à zéro
   (`Math.max(0, ...)`, ligne 1314) plutôt que de bloquer, après avoir
   journalisé une alerte si le stock était déjà insuffisant au moment
   de la consommation. **Démontré statiquement.** Le comportement
   aval (un poste qui continue de « produire » avec un stock matière à
   zéro, sans jamais être bloqué) n'a pas été observé en exécution
   dans cette passe — **nécessite un test runtime**.
   *Mise à jour : ce point est désormais confirmé en runtime, voir §19.4.*
5. **Une commande peut-elle rester indéfiniment en
   approvisionnement ?** Non, structurellement, pour le chemin normal :
   `finaliserApprovisionnementCommande()` crédite
   **inconditionnellement** le manque calculé pour la commande dès que
   son délai programmé (`delaiApprovisionnementReelMax`) s'écoule, sans
   dépendre d'un événement externe. Les seules sorties non terminales
   en boucle identifiées seraient une **erreur de configuration**
   répétée (nomenclature/ligne invalide), mais celles-ci aboutissent à
   `BLOQUE_NOMENCLATURE`/`BLOQUE_MATIERE`, qui sont **terminales**
   (`commandeEstTerminale()`, §1.8), pas à une attente infinie.
   **Démontré statiquement**, sous réserve qu'aucun autre site non
   identifié dans cette passe ne vienne remettre `cmd.statut` à
   `EN_APPROVISIONNEMENT` sans reprogrammer `FINALISER_APPROVISIONNEMENT`
   (non observé, mais une revue exhaustive de tous les sites
   d'assignation de `EN_APPROVISIONNEMENT` n'a pas été refaite dans
   cette passe au-delà du site déjà cité, ligne 3368).

### 17.4 Requalification de la matrice de complétude (§2)

La matrice du §2 reste globalement valide ; les lignes suivantes sont
précisées à la lumière de l'audit complémentaire :

| Capacité | Classification précédente (§2) | Classification requalifiée | Justification |
|---|---|---|---|
| Approvisionnement Source (chemin commande) | PARTIEL | **IMPLÉMENTÉ STATIQUEMENT, VÉRIFIÉ PAR LECTURE COMPLÈTE** — mais fonctionnellement un raccourci (crédit direct), pas un vrai MRP de commande | Les 3 fonctions (`declencherApprovisionnementCommande`, `finaliserApprovisionnementCommande`, `delaiApprovisionnementReelMax`) sont maintenant lues intégralement (§17.1) |
| Réception matière | À TESTER RUNTIME | **IMPLÉMENTÉ STATIQUEMENT (deux mécanismes distincts, §17.2) ; NON VÉRIFIÉ PAR RUNTIME** | Code lu intégralement, mais l'interaction réelle entre Mécanisme A et B n'a jamais été observée en exécution |
| Reprise après approvisionnement | À TESTER RUNTIME / À AUDITER | **IMPLÉMENTÉ STATIQUEMENT, VÉRIFIÉ PAR LECTURE COMPLÈTE** | `finaliserApprovisionnementCommande()` intégralement relue (§17.1), chaîne jusqu'à `tracerEtPlanifierProductionCommande()` confirmée sans ambiguïté |
| Réservation matière | ABSENT | **ABSENT, CONFIRMÉ PAR DEUX LECTURES INDÉPENDANTES** (§5 et §17.2) | Aucune des cinq fonctions auditées ici n'introduit de réservation ; le constat du §5 est renforcé, pas seulement répété |
| Double réapprovisionnement MRP + ad hoc | *(non distingué en §2)* | **DÉMONTRÉ STATIQUEMENT, NON VÉRIFIÉ PAR RUNTIME** | Nouveau constat de cette passe, §17.2-17.3 |

**Rappel de discipline** (demande explicite) : aucune fonction ci-dessus
n'est présentée comme une fonctionnalité validée de bout en bout tant
qu'un run réel n'a pas confirmé le comportement sous charge concurrente
(fixtures §17.5).

### 17.5 Fixtures MTO-A à MTO-D — version finalisée

Les quatre fixtures sont complétées avec les identifiants et
paramètres réellement présents dans le modèle. Aucune valeur n'est
inventée : les noms de matières et de scénarios cités sont ceux déjà
en usage dans ce run (`GPL_VRAC`, `BOUTEILLE_VIDE_12KG`,
`ACCESSOIRES_KIT`, cf. configuration du run C2) ; le détail exact des
lignes de nomenclature (quantité par unité pour chaque matière, par
scénario) n'a pas été extrait ligne à ligne dans cette passe — il
dépend du scénario JSON chargé au moment du test (`sc.nomenclature`,
propre à chaque `scenario_*.json`) et doit être lu dans le fichier de
scénario effectivement utilisé avant l'exécution, plutôt que supposé
ici.

**MTO-A — matière suffisante dès le départ**
- Matières : toutes les `idMatiere` référencées par la nomenclature du
  scénario testé (à lire dans le JSON du scénario sélectionné avant le
  run, ex. `GPL_VRAC` pour le scénario GPL).
- Quantités initiales : `FicheMatiere.stockDisponible` ≥
  `quantiteParUnite × qte` pour chaque ligne, avec une marge
  confortable (ex. ×3) pour exclure tout effet de bord du point de
  commande (s,Q) du Mécanisme B.
- Quantité commandée : 1 commande, `qte` modéré (cohérent avec
  `quantiteFixeCommande = 10` déjà utilisé lors de la clôture C2).
- Besoins calculés : `besoin = quantiteParUnite × qte` par ligne de
  nomenclature (formule confirmée ligne 4857 et 5409, identique dans
  les deux fonctions).
- Paramètres de retard : aucun (`retardFournisseurTestActif = false`).
- Statuts attendus : `EN_ATTENTE` → (pas de passage par
  `EN_APPROVISIONNEMENT`) → `PRODUCTION_PLANIFIEE` → `SERVIE` ou
  `EN_RETARD` selon `tPromise`.
- Assertions de terminalité : `commandeEstTerminale(cmd) == true` ;
  `termines == cmd.qte` ; **aucune `ReceptionAttendue` créée** pour la
  matière concernée pendant la durée du test. **Précision (relecture
  MTO-0.1)** : cette absence attendue n'est valide que **sous
  condition** — elle suppose que le stock projeté
  (`stockProjete = stockDisponible + receptionsAttendues`, calculé
  dans `calculerBesoinsNets()`, ligne 1231) reste au-dessus du point de
  commande `f.pointCommande` **pendant toute l'exécution, y compris
  après la consommation physique** par `consommerMatieresPour()`. La
  marge initiale (§ ci-dessus, ×3) doit donc être dimensionnée en
  tenant compte de la consommation réelle de la commande testée, pas
  seulement du besoin brut initial ; sinon le Mécanisme B peut se
  déclencher légitimement en cours de test sans que ce soit une
  anomalie.
- Données à examiner dans les exports : ABox `run:modelArtifact` et
  champs de clôture habituels (déjà validés en C1/C2) ; aucun champ
  DDMRP n'existe encore, donc rien de spécifique à vérifier côté
  export matière au-delà des logs `[STOCK]`/`[SOURCE]`.

**MTO-B — matière insuffisante → Source → réception → Make**
- Matières : au moins une `FicheMatiere` de la nomenclature du
  scénario testé.
- Quantités initiales : `stockDisponible` strictement inférieur au
  besoin d'une commande (ex. `stockDisponible = 0` pour isoler le cas
  le plus net).
- Quantité commandée : 1 commande, `qte` fixé pour garantir
  `manque > 0`.
- Besoins calculés : idem MTO-A, avec `manque = besoin -
  stockDisponible > 0` pour au moins une ligne.
- Paramètres de retard : aucun (le délai utilisé est
  `delaiApprovisionnementReelMax()`, dérivé de
  `FicheMatiere.delaiObtentionHeures`, déjà configuré dans le JSON du
  scénario — à lire tel quel, pas à fixer arbitrairement).
- Statuts attendus : `EN_ATTENTE` → `EN_APPROVISIONNEMENT` →
  `MATIERES_DISPONIBLES` (transitoire) → `PRODUCTION_PLANIFIEE` →
  `SERVIE`/`EN_RETARD`.
- Assertions de terminalité : `commandeEstTerminale(cmd) == true` ;
  vérifier spécifiquement que `f.stockDisponible` a été incrémenté de
  exactement `manque` au moment de `finaliserApprovisionnementCommande()`
  (log `[SOURCE] ... reception terminee`), **et** observer si
  `calculerBesoinsNets()` a créé une `ReceptionAttendue` concurrente
  pour la même matière pendant la fenêtre `EN_APPROVISIONNEMENT` (test
  direct de la question 17.3.2).
- Données à examiner : logs `[STOCK]` (Mécanisme B) et `[SOURCE]`
  (Mécanisme A) côte à côte, horodatés, pour confirmer ou infirmer le
  chevauchement.

**MTO-C — 2 ou 3 commandes MTO concurrentes avec matière limitée**
- Matières : une `FicheMatiere` partagée par au moins deux scénarios
  (ou un seul scénario, deux commandes).
- Quantités initiales : `stockDisponible` suffisant pour **une seule**
  des commandes testées (ex. couvrant exactement 1 commande sur 2-3).
- Quantité commandée : 2 à 3 commandes créées à quelques secondes
  d'écart (`genererCommande()` appelée plusieurs fois rapprochées, ou
  `nombreCommandesATester` ≥ 2 avec un délai court entre commandes).
- Besoins calculés : identiques par commande si même scénario ; à
  additionner pour vérifier le dépassement du stock total.
- Paramètres de retard : aucun, pour isoler l'effet de concurrence pur.
- Statuts attendus : non prédits à l'avance (c'est l'objet du test) ;
  observer si une commande est bloquée (`BLOQUE_MATIERE`) ou si les
  deux/trois sont servies malgré un stock initial insuffisant pour
  toutes (signe du double engagement/réapprovisionnement, §5/§17.2).
- Assertions de terminalité : les 2-3 commandes atteignent un statut
  terminal ; comparer l'ordre réel de clôture à l'ordre de création
  (test direct de la conclusion du §4) ; comparer la somme des crédits
  matière appliqués à la pénurie initiale réelle.
- Données à examiner : séquence complète des logs `[STOCK]`, `[SOURCE]`,
  `[MTO]`/`[MAKE]` pour les commandes concernées, export Excel/ABox de
  fin de run pour `stockDisponible` final de la matière testée.

**MTO-D — commande MTO avec retard fournisseur forcé**
- Matières : une `FicheMatiere` ciblée par le mécanisme de test déjà
  présent (`retardFournisseurCible`, `retardFournisseurTestActif`,
  confirmés existants au §1.4/§1.5 et réutilisés ici sans
  modification).
- Quantités initiales : `stockDisponible` insuffisant, comme MTO-B.
- Quantité commandée : 1 commande, `qte` cohérent avec un scénario
  compatible (`scenarioCompatibleRetardFournisseur()`, déjà existant,
  vérifié au §1.1 — refuse silencieusement avec popup si le scénario
  sélectionné ne consomme pas la matière cible).
- Besoins calculés : idem MTO-B.
- Paramètres de retard : `retardFournisseurTestActif = true`,
  `retardFournisseurCible = <idMatiere testé>`, délai effectif forcé
  via `delaiFournisseurConfigureEffectifHeures()`/
  `delaiFournisseurEffectifHeures()` (déjà existants, non modifiés).
- Statuts attendus : `EN_ATTENTE` → `EN_APPROVISIONNEMENT` (durée
  anormalement longue) → `MATIERES_DISPONIBLES` → `PRODUCTION_PLANIFIEE`
  → statut terminal. **Correction (relecture MTO-0.1)** : `EN_RETARD`
  n'est **pas** un résultat garanti par construction — la règle
  réellement codée (ligne 13606/5867, §1.8) est
  `cmd.statut = (time() <= cmd.tPromise) ? "SERVIE" : "EN_RETARD"`. Le
  test doit donc **comparer l'instant réel de clôture (`tClose`,
  l'instant où `commandeEstTerminale(cmd)` devient vrai) à
  `cmd.tPromise`**, et ne considérer `EN_RETARD` comme attendu que si
  le retard fournisseur forcé fait effectivement dépasser `tPromise`
  (`tClose > tPromise`). Si le retard forcé reste inférieur à la marge
  disponible avant `tPromise`, un résultat `SERVIE` est correct et ne
  doit pas être interprété comme un échec du test.
- Assertions de terminalité : `commandeEstTerminale(cmd) == true` ;
  vérifier `enregistrerRetardFournisseurForce()` (ligne ~1243) a bien
  été appelée une seule fois pour ce test (`retardFournisseurConsomme`,
  déjà un garde-fou existant d'après le nom du champ, non audité ligne
  à ligne dans cette passe) ; calculer `tClose - tPromise` et confirmer
  que le signe de cet écart correspond exactement au statut obtenu
  (`SERVIE` si `tClose <= tPromise`, `EN_RETARD` sinon).
- Données à examiner : log `[STOCK]` portant `delai effectif=` très
  supérieur à `delai nominal=` ; `cmd.statut` final ; `cmd.tPromise` et
  l'instant de clôture réel, pour calculer l'écart ci-dessus.

### 17.6 Frontière MTO / DDMRP (précision du §8-§9)

La découverte du §17.2 renforce, plutôt qu'elle ne contredit, la
recommandation du §8-§9 : elle montre concrètement **pourquoi** les
responsabilités suivantes doivent rester séparées, avec une base de
code précise pour chacune :

- **Réservation et consommation physique** : doit rester portée par
  `FicheMatiere`/`consommerMatieresPour()`, qui reste le point unique
  de consommation physique (§17.1). **Correction (relecture
  MTO-0.1)** : ce n'est pas un mécanisme « déjà correct dans son rôle
  propre » — `consommerMatieresPour()` ne bloque pas la production
  lorsque le stock matière est insuffisant (il tronque à zéro,
  `Math.max(0, ...)`, ligne 1314, §17.1/§17.3.4). Son comportement
  d'insuffisance reste à valider, voire à corriger, après observation
  runtime (MTO-1, §18). Ni DDMRP ni le Mécanisme A ne doivent dupliquer
  son rôle de point unique de consommation, mais cela ne présume pas
  que son comportement actuel face à l'insuffisance soit correct.
- **Calcul de disponibilité** : doit rester `matieresSuffisantesPourScenario()`-like
  (lecture de `stockDisponible`), mais **devra être étendu** pour
  consulter l'Open Supply (ligne suivante) avant qu'une nouvelle
  implémentation DDMRP ne soit ajoutée — sinon un futur Mécanisme C
  (DDMRP) répéterait exactement l'erreur d'indépendance démontrée en
  §17.2 pour les Mécanismes A et B.
- **Open Supply** : doit devenir la **vue unique et partagée** des
  quantités déjà engagées (aujourd'hui, seul le Mécanisme B peuple
  `receptionsAttendues`/`totalReceptionsAttendues()` ; le Mécanisme A
  n'y contribue jamais, §17.1). Une implémentation DDMRP qui
  consulterait uniquement `receptionsAttendues` sans tenir compte des
  crédits directs du Mécanisme A resterait aveugle à une partie réelle
  de l'engagement matière en cours.
- **Qualified Demand** : doit être calculée à partir des commandes
  ouvertes (`commandes`, hors `REAPPRO_*` ou les incluant selon la
  décision de conception, à trancher explicitement, pas par défaut),
  indépendamment du mécanisme qui a généré leur besoin (A ou B).
- **Décision de réapprovisionnement** : c'est le point précis où
  Mécanisme A et Mécanisme B devront converger ou être explicitement
  arbitrés l'un contre l'autre si DDMRP est introduit — **ne pas
  ajouter un troisième mécanisme indépendant** (la recommandation du
  §8, Option 2, reste valide, mais seulement si son introduction
  **remplace** le Mécanisme B pour les matières bufferisées, plutôt que
  de s'y superposer comme un Mécanisme C).
- **Priorité des commandes clientes** : reste hors du périmètre matière
  (§10, inchangé par cet audit complémentaire).

La recommandation `DDMRPBuffer` lié à `FicheMatiere` (§8) **reste une
hypothèse de conception, non tranchée**. Cet audit complémentaire ne la
confirme ni ne l'infirme ; il précise seulement les mécanismes
existants qu'elle devra remplacer ou absorber pour éviter d'ajouter un
troisième système de réapprovisionnement indépendant.

### 17.7 Lacunes restantes après cet audit complémentaire

- Impact quantitatif réel du double réapprovisionnement (§17.2) : non
  mesuré, nécessite MTO-B/MTO-C exécutées.
- Comportement d'un poste consommateur face à un `stockDisponible`
  tombé à zéro par `consommerMatieresPour()` (§17.3.4) : non observé en
  exécution.
- Revue exhaustive de tous les sites assignant
  `cmd.statut = "EN_APPROVISIONNEMENT"` au-delà du site déjà cité
  (ligne 3368) : non refaite dans cette passe.
- Comportement exact de `enregistrerRetardFournisseurForce()`/
  `retardFournisseurConsomme` sous plusieurs commandes successives
  visant la même matière cible (pertinent pour MTO-D répétée) : non
  audité ligne à ligne.
- Toute mesure runtime listée au §17.5 : aucune campagne n'a été
  exécutée dans cette passe, conformément à la consigne.

---

## 18. MTO-1 — Runtime Baseline (fixtures MTO-A et MTO-B)

**Nature : préparation de fixtures et procédure de run manuel.**
Branche `feature/mto-ddmrp-foundation`, base
`b5fdbf15aa80c551351de82686fe90adfb46d855`. Aucune campagne n'a été
exécutée automatiquement dans cette passe (environnement non outillé
pour piloter l'IDE AnyLogic). Aucun bug n'est corrigé ici ;
`carnetCommandesMTO`, la réservation matière et DDMRP ne sont pas
touchés ; ETO et C3/E4 ne sont pas concernés.

### 18.1 Pourquoi aucune instrumentation `.alp` n'a été ajoutée

Les logs déjà présents dans le modèle couvrent, sans ambiguïté,
l'intégralité des observations demandées pour MTO-A et MTO-B :

- `[MODE SCOR] Mode sélectionné=... | isMTS=... | isMTO=... | isETO=...`
  (ligne 8609) — confirme le mode réellement actif.
- `[DELIVER] Commande <id> type=<typeCommande> qte=<qte> | ...`
  (ligne 13979) — confirme `cmd.typeCommande` au moment de la
  génération de chaque commande.
- `[STOCK] ...` (`calculerBesoinsNets()`, lignes ~1137-1261) — chaque
  réception créditée par le Mécanisme B, chaque nouvelle
  `ReceptionAttendue` créée (quantité, point de commande, stock
  projeté).
- `[SOURCE] <id> en attente de reception matiere ; production suspendue
  pendant ...` (déclenchement du Mécanisme A, dans
  `analyserMatiereCommandeOrchestree()`, proche de la ligne 3376) et
  `[SOURCE] <id> : reception terminee, lancement Make autorise.`
  (ligne 3503) — bornes exactes de la fenêtre `EN_APPROVISIONNEMENT`.
- `[ERREUR MATIERE] ...`/`[DEBUG CAS] ...` (dans
  `analyserMatiereCommandeOrchestree()`/`matieresSuffisantesPourScenario()`)
  — bilan matière à chaque analyse.

Ces logs suffisent à reconstituer la chronologie demandée au §18.3 sans
ajouter de `System.out`/log supplémentaire. **Aucune instrumentation
`.alp` n'a donc été nécessaire** ; si une étape précise de la
chronologie manquait de preuve une fois les logs du run réellement
collectés, cela sera signalé explicitement plutôt que comblé par une
instrumentation ajoutée a posteriori.

### 18.2 Préparation commune aux deux fixtures

- Scénario : `scenario_ZENER_SA_Togo_v39.json` (fichier déjà
  présent dans le dépôt, non modifié). Nomenclature utilisée :
  `"SCENARIO DISTRIBUTION"` — `GPL_VRAC` (12,5/unité),
  `BOUTEILLE_VIDE_12KG` (1/unité), `ACCESSOIRES_KIT` (1/unité) ;
  `fichesMatiere` du JSON : `GPL_VRAC` (stockDisponible=600,
  stockSecurite=150, delaiObtentionHeures=6, fournisseur=ACT_1),
  `BOUTEILLE_VIDE_12KG` (stockDisponible=250, stockSecurite=60,
  delaiObtentionHeures=10, fournisseur=ACT_2), `ACCESSOIRES_KIT`
  (stockDisponible=300, stockSecurite=80, delaiObtentionHeures=5,
  fournisseur=ACT_3). Valeurs lues directement dans le fichier JSON,
  aucune inventée.
- Chargement : bouton **« Rafraîchir la liste »** puis sélectionner
  `scenario_ZENER_SA_Togo_v39.json` dans la liste déroulante, puis
  bouton **« Charger le scénario sélectionné »**
  (`chargerScenarioJSONDepuisSelection()`, ligne 24271) — ne pas
  utiliser le bouton « Charger config JSON » seul, car il recalcule le
  nom de fichier depuis `nomEntreprise` (défaut `"ZENER_SA_Togo"`,
  ligne 11144) et chercherait `scenario_ZENER_SA_Togo.json` (sans
  `_v39`), qui n'existe pas dans `model/`.
- Mode de simulation : à l'ouverture, la boîte de dialogue **« Mode de
  simulation SCOR »** apparaît automatiquement (`StartupCode` de
  `Main`, ligne 10598). Sélectionner impérativement
  **« MTO — Make/Source/Deliver to Order (occurrence 2) »**. Ce choix
  fixe `isMTO=true` et fait que `modeSCORActif()` (ligne 8521) retourne
  `"MTO"` pour toute commande générée ensuite — c'est la condition
  nécessaire et suffisante pour que `analyserStockCommandeOrchestree()`
  court-circuite la branche MTS (§1.3) et entre dans le chemin MTO
  tracé au §1.
- Nombre de commandes : bouton **« Contrôle commandes »**
  (`ouvrirParametresNombreCommandes()`, ligne 4404) → cocher **« Limiter
  les commandes automatiques »**, champ nombre = **1**, cocher
  **« Utiliser une quantité fixe »**, champ quantité = **10** (valeur
  déjà utilisée et documentée lors de la clôture runtime C2, §21 du
  présent document — pas une valeur nouvelle inventée pour ce test).
  Avec `qte=10`, les besoins par matière sont : `GPL_VRAC` = 125,
  `BOUTEILLE_VIDE_12KG` = 10, `ACCESSOIRES_KIT` = 10 (calcul :
  `quantiteParUnite × qte`, formule confirmée §17.5).
- Seed : utiliser **`seedExperiment = 1001`** (champ existant, déjà
  utilisé en C1/C2, voir §18 et §21), identique pour MTO-A et MTO-B,
  afin d'isoler l'effet de la seule configuration matière entre les
  deux runs. En cas d'impossibilité technique constatée au runtime
  d'utiliser exactement 1001, documenter précisément la valeur
  réellement utilisée dans le rapport de run, mais elle doit rester
  **identique entre MTO-A et MTO-B** ; une valeur de seed différente
  entre les deux runs invaliderait la comparaison recherchée au §18.4.

### 18.3 Procédure exacte — MTO-A (matière suffisante)

**Configuration additionnelle** : **aucune**. Ne pas ouvrir le bouton
« Stocks initiaux » : les valeurs par défaut du JSON (§18.2) couvrent
déjà largement le besoin (125/10/10 contre 600/250/300 disponibles) et
constituent la fixture la plus simple et la plus fidèle au modèle tel
qu'il est configuré, sans valeur inventée.

**Déroulement attendu** (à confirmer par les logs du run, pas supposé
à l'avance) :
1. Démarrer la simulation (bouton Démarrer, après la boîte de dialogue
   Mode SCOR).
2. Laisser la commande unique se générer (`genererCommande()`).
3. Relever le log `[DELIVER] Commande CMD_1 type=MTO qte=10 | ...`.
4. Relever l'absence de tout log `[SOURCE] ... en attente de reception
   matiere` pour `CMD_1` (signe que `matOK=true` dès le premier
   passage et que la commande n'est jamais passée par
   `EN_APPROVISIONNEMENT`).
5. Laisser la production se terminer, relever la clôture (`SERVIE` ou
   `EN_RETARD` selon `tPromise`, les deux sont des résultats valides
   ici — seul un statut `BLOQUE_*`/`REFUSEE` serait anormal).
6. Exporter Excel/ABox de fin de run (même procédure que C1/C2).

**Preuves à conserver** :
- `cmd.typeCommande` réellement `"MTO"` : log `[DELIVER] ... type=MTO ...`.
- Absence de `EN_APPROVISIONNEMENT` : absence des logs `[SOURCE] ...
  en attente ...` pour `CMD_1` dans toute la durée du run.
- Absence de nouvelle `ReceptionAttendue` pour `GPL_VRAC`,
  `BOUTEILLE_VIDE_12KG`, `ACCESSOIRES_KIT` : absence des logs `[STOCK]
  ... -> ordre de Q*=...` pour ces trois matières pendant la durée du
  test. **Rappel (correction §17.6)** : ceci n'est garanti que si le
  stock projeté reste au-dessus du point de commande après
  consommation — si un tel log apparaît malgré tout, ce n'est pas
  nécessairement une anomalie, cela doit être interprété à la lumière
  du point de commande réellement calculé (visible dans le même log
  `[STOCK]`), pas rejeté par principe.
- Passage à `PRODUCTION_PLANIFIEE` puis statut terminal : à défaut de
  log dédié à `PRODUCTION_PLANIFIEE` (non trouvé dans le code,
  confirmé §17.1), inférer la fenêtre entre la dernière trace Make
  (`tracerFluxHierarchique(..., "Make", ...)`) et le début de
  circulation des `FluxEntity` ; le statut terminal est directement lu
  dans l'export Excel/ABox de fin de run.
- Quantité produite/terminée cohérente : `termines == 10` (compteur
  interne déjà utilisé au §1.8).
- Stock matière avant/après : relevé manuel de
  `FicheMatiere.stockDisponible` via le dernier log `[STOCK]` de
  chaque matière avant le run (valeurs par défaut, §18.2) et après
  clôture (export Excel final).
- Compteurs ouverts/WIP terminaux propres : mêmes champs que la
  clôture C1/C2 (`demandGenerationFinished`, `terminalReached`,
  `openCustomerOrders`, `openReplenishments`,
  `entitiesInProcessAtPosts`, `pendingBusinessActions`, calculés par
  `diagnosticEtatTerminal()`, ligne 9614).

### 18.4 Procédure exacte — MTO-B (matière insuffisante)

**Configuration additionnelle** : bouton **« Stocks initiaux »**
(`ouvrirParametresStockInitial()`, ligne 4267) → champ **« Override
global matière (toutes fiches) »** = **0**, valider. Ceci applique
`f.stockDisponible = 0` aux trois `FicheMatiere` simultanément
(`appliquerStocksInitiauxConfig()`, confirmé ligne 4218) — c'est le
seul mécanisme déjà existant dans l'interface pour forcer une pénurie
sans éditer le fichier JSON, et il satisfait « au moins une matière à
0 » en l'appliquant aux trois par construction de ce contrôle. Avec
`qte=10`, le manque est alors : `GPL_VRAC`=125, `BOUTEILLE_VIDE_12KG`=10,
`ACCESSOIRES_KIT`=10 (égal au besoin brut, puisque le stock de départ
est nul).

**Ne pas activer** `retardFournisseurTestActif` : le délai utilisé est
celui, nominal, de `delaiApprovisionnementReelMax()` (§17.1, dérivé de
`delaiObtentionHeures` : 6h/10h/5h selon la matière, converti par
`dureeEchelle()`). **Ne pas désactiver ni modifier le cycle (s,Q)** :
c'est précisément son interaction avec le Mécanisme A qui doit être
observée.

**Chronologie à capturer** (horodatage simulé `time()` pour chaque
point, à relever directement depuis les logs, pas recalculé a
posteriori) :

| # | Événement | Source exacte |
|---|---|---|
| 1 | Création de `CMD_1` | log `[DELIVER] Commande CMD_1 type=MTO qte=10 ...` (ligne 13979) |
| 2 | Besoin matière exact | calculable (`quantiteParUnite × 10`, §18.2) ou lu dans `[DEBUG CAS] ... bilan=...` (`analyserMatiereCommandeOrchestree()`) |
| 3 | Stock initial | 0 pour les trois matières (configuration §18.4) |
| 4 | Passage à `EN_APPROVISIONNEMENT` | log `[SOURCE] CMD_1 en attente de reception matiere ; production suspendue pendant Xs` (déclenché depuis `analyserMatiereCommandeOrchestree()`, proche ligne 3376) |
| 5 | Délai calculé par `delaiApprovisionnementReelMax()` | même log que (4), valeur `Xs` (déroulé) et `Xh` (réel) annoncée dans le message |
| 6 | Chaque exécution pertinente de `calculerBesoinsNets()` touchant `GPL_VRAC`/`BOUTEILLE_VIDE_12KG`/`ACCESSOIRES_KIT` | log `[STOCK] <idMatiere> : stock projete=... <= point de commande=... -> ordre de Q*=... (delai nominal=...h, delai effectif=...h)` (ligne ~1255) ; **noter chaque occurrence**, pas seulement la première |
| 7 | Création de `ReceptionAttendue` (Mécanisme B) | même log que (6) — `quantite = Q*` annoncée, `dateArrivee` non loguée directement mais déductible (`maintenant + dureeEchelle(delaiReelTotal)`, §17.1) ; si possible, consulter directement `f.receptionsAttendues` via le débogueur AnyLogic au moment du log pour la date exacte |
| 8 | Crédit direct par `finaliserApprovisionnementCommande()` (Mécanisme A) | log `[SOURCE] CMD_1 : reception terminee, lancement Make autorise.` (ligne 3503) et les logs de détail associés (`reception.toString()`, quantité reçue par matière) |
| 9 | Crédit ultérieur éventuel par `traiterEcheances()` (Mécanisme B) | log `[MRP] Reception matiere <idMatiere> : +X (stock=...)` (ligne ~1138) — **si ce log apparaît pour une matière déjà créditée en (8), c'est la preuve directe du double crédit (§17.2)** |
| 10 | Stock final | dernier `stockDisponible` de chaque matière, lu dans le dernier log `[STOCK]` et/ou l'export Excel/ABox de fin de run |
| 11 | Passage en production | trace AER `MaterialAvailable` (§17.1) ; ou simplement la reprise de circulation des `FluxEntity` |
| 12 | Statut terminal de `CMD_1` | export Excel/ABox de fin de run |

**Calcul à produire dans le rapport de run** :
```
stock_final_theorique_sans_double_credit (par matière)
    = 0 (stock initial, §18.4)
    + manque crédité par finaliserApprovisionnementCommande()  [étape 8]
    - quantiteParUnite × 10 (consommation Make, consommerMatieresPour())

stock_final_observe (par matière)
    = valeur réellement lue à l'étape 10

écart = stock_final_observe - stock_final_theorique_sans_double_credit
```
Un écart strictement positif, corrélé à l'apparition d'un log `[MRP]
Reception matiere ...` (étape 9) pour la même matière pendant la
fenêtre `EN_APPROVISIONNEMENT` de `CMD_1`, constitue la preuve runtime
directe du double réapprovisionnement déjà démontré statiquement en
§17.2.

### 18.5 Ce qu'il faut renvoyer après le run manuel

- Le journal complet des événements (`board.logEvent`), pas seulement
  les lignes filtrées ci-dessus — pour permettre de vérifier qu'aucun
  événement pertinent n'a été omis par les filtres `[...]` proposés.
- L'export Excel et l'export ABox TTL de fin de run, pour chaque
  fixture (MTO-A et MTO-B séparément, deux runs distincts).
- La valeur de seed utilisée pour chaque run.
- La confirmation du mode sélectionné dans la boîte de dialogue de
  démarrage (capture du log `[MODE SCOR] ...` suffit).
- Pour MTO-B spécifiquement : le tableau rempli du §18.4 (les 12
  points) et le calcul d'écart du même paragraphe.

### 18.6 Limite assumée de cette préparation

Le détail exact de `dureeEchelle()`/`simToRealSeconds` (lignes 2168 et
alentours) n'a pas été recalculé ici pour convertir précisément les
délais de 6h/10h/5h réels en secondes simulées — la valeur exacte
apparaîtra directement dans les logs `[SOURCE]`/`[STOCK]` du run
(`Xs (deroule) / Xh (reel)`), il n'était donc pas nécessaire de la
précalculer pour préparer la fixture.

---

## 19. Premier run MTO-B — enregistrement runtime (exploratoire)

**Statut de ce run : exploratoire, contaminé, mais probant sur plusieurs
invariants.** Il ne constitue **pas** le MTO-B contrôlé final : la
fixture a modifié plus d'une variable à la fois (stock produit fini et
stock matière), ce qui le rend inutilisable pour isoler l'interaction
A+B. Aucun code n'a été modifié ; aucune logique métier n'est corrigée
dans cette section.

### 19.1 Configuration effective du run

- `CMD_1` : type **MTO**, quantité **10**, seed **1001**, aucun retard
  fournisseur forcé.
- Stock produit fini initial : **0**. Dans MTO-A, il était de **100**.
  La fixture a donc modifié la variable « produit fini » en plus de la
  variable « matière » : ce n'est pas un MTO-B contrôlé.
- Stocks matière initiaux : **GPL_VRAC = 0 / BOUTEILLE_VIDE_12KG = 0 /
  ACCESSOIRES_KIT = 0**.
- Besoin matière de `CMD_1` (10 unités) : **125 / 10 / 10**.

### 19.2 Chronologie observée (temps simulé `time()`)

| t (simulé) | Événement |
|---|---|
| 49 | `CMD_1` créée (MTO, qte 10) |
| 53 | Pénurie détectée : manque **125 GPL / 10 bouteilles / 10 accessoires** |
| 53 | Chaîne Source lancée pour `CMD_1` (`EN_APPROVISIONNEMENT`) |
| 60.2 | **`REAPPRO_1` créé en stratégie MTS** pendant que `CMD_1` est encore en approvisionnement |
| 60.2 → | `REAPPRO_1` constate lui aussi le besoin **125 / 10 / 10** |
| 116 | `MaterialReceived` de `CMD_1` : **+125 / +10 / +10** (crédit direct, Mécanisme A) |
| 118 | Make de `CMD_1` démarré |
| 123 | `MaterialReceived` de `REAPPRO_1` : **reçu = 0 / 0 / 0**, car le stock est déjà à 125 / 10 / 10 grâce au crédit de `CMD_1` |
| 125 | **`REAPPRO_1` démarre Make malgré l'absence de matière nouvellement reçue** |
| 1060.6 | `CMD_1` = 10/10, **SERVIE** |
| 1857.9 | `REAPPRO_1` atteint 10/10 |

### 19.3 Constat de conservation de la matière

- Matière effectivement créditée au total : **125 / 10 / 10**, soit
  exactement la matière correspondant à **10 unités** (`CMD_1`
  seul ; `REAPPRO_1` n'a rien reçu).
- Unités produites au total : **20** (10 pour `CMD_1` + 10 pour
  `REAPPRO_1`).
- Matière théoriquement requise pour 20 unités : **250 / 20 / 20**.
- Déficit de matière non couvert : **125 / 10 / 10**, soit la matière
  de 10 unités.
- Historique observé : le stock matière passe de **125 / 10 / 10** à
  **0 / 0 / 0** après environ 10 consommations ; les deux productions
  continuent ensuite jusqu'à **20 unités terminées**.

**Conclusion : violation de conservation de la matière, confirmée en
runtime.** Les unités produites au-delà de la 10ᵉ ont été fabriquées
sans matière disponible, sans que le système ne bloque la production.

### 19.4 Requalification du risque `consommerMatieresPour()`

Le risque statique identifié en §17.3.4 et §17.1 devient un **défaut
runtime confirmé** :

1. stock matière insuffisant au moment de la consommation ;
2. alerte éventuelle journalisée (`Stock matiere insuffisant pendant
   la production`), mais **production non bloquée** ;
3. troncature à zéro (`Math.max(0, ...)`, ligne 1314) ;
4. **possibilité de fabriquer sans matière disponible**, comme observé
   ci-dessus (unités 11 à 20).

Ce défaut est classé **bloqueur de validité matière avant toute
implémentation DDMRP** : tant qu'une unité peut être terminée sans
matière réellement disponible, aucun indicateur de stock matière (y
compris les futurs buffers DDMRP) ne reflète la réalité physique du
modèle.

### 19.5 Interférence autonome (MTO client vs REAPPRO_*)

- `REAPPRO_1` (MTS autonome) a été déclenché pendant que `CMD_1`
  attendait sa matière, et a constaté le même besoin 125 / 10 / 10.
- Le crédit de `CMD_1` a satisfait ce besoin ; le `MaterialReceived`
  de `REAPPRO_1` (t=123) n'a donc rien ajouté (0 / 0 / 0), mais
  `REAPPRO_1` a néanmoins lancé Make à t=125.
- **Statut : concurrence MTO client / REAPPRO autonome, confirmée en
  runtime.** Elle aboutit à la production de 20 unités pour 10 unités
  de matière créditée (cf. §19.3).

### 19.6 Stocks remontés après REAPPRO_1 — non interprétés comme preuve A+B

Après la fin de `REAPPRO_1`, les stocks remontent progressivement
jusqu'à environ **250 / 70 / 90** via le mécanisme (s,Q) (Mécanisme B).
**Cette remontée ne doit pas être présentée comme preuve d'un double
crédit MTO ad hoc + (s,Q) pendant `EN_APPROVISIONNEMENT`** : la
chronologie montre que ces réceptions sont postérieures à la
production autonome (t=123 et après), donc hors de la fenêtre
`EN_APPROVISIONNEMENT` de `CMD_1` (t=53 → t=116). L'interaction A+B
reste **à tester dans une fixture propre** (§19.8).

### 19.7 Statuts à enregistrer

| Point | Statut |
|---|---|
| MTO-B cœur Source → Make pour `CMD_1` (chaîne customer nominale) | **PASS** |
| Interaction A+B (double crédit ad hoc + (s,Q) pendant `EN_APPROVISIONNEMENT`) | **INCONCLUSIVE** |
| Concurrence MTO client / REAPPRO autonome | **Runtime confirmé** |
| Violation de conservation de la matière | **Runtime confirmé** |
| Défaut `consommerMatieresPour()` (fabrication sans matière disponible) | **Observé dans le run exploratoire, contaminé par `REAPPRO_1` ; non reproduit dans le run final contrôlé (§20). Voir §20.4 avant de le classer comme bloqueur.** |

### 19.8 Répétition contrôlée à préparer

Fixture propre, à exécuter manuellement, pour isoler la seule variable
« matière » entre les deux conditions :

- stock produit fini initial : **100** (identique à MTO-A) ;
- stocks matière initiaux : **GPL_VRAC = 0 / BOUTEILLE_VIDE_12KG = 0 /
  ACCESSOIRES_KIT = 0** ;
- mode : **MTO** (occurrence 2 de la boîte « Mode de simulation SCOR ») ;
- une seule commande, quantité **10** ;
- seed **1001** ;
- **aucun retard fournisseur forcé** ;
- procédure de chargement et de contrôle identique à §18.2-§18.4.

**Limite à garder en tête** : même avec cette fixture, le `REAPPRO_1`
autonome peut encore apparaître (il dépend de la politique MTS, pas de
la seule commande). Si c'est le cas, le run reste un test de la
concurrence MTO/REAPPRO, et doit être relu comme tel, pas comme un MTO-B
isolé. Le relevé du run devra donc distinguer explicitement
« `REAPPRO_*` présent ou absent ».

### 19.9 Ce qui reste à faire après ce run

- Ne corriger **aucun** code dans cette phase : la correction de
  `consommerMatieresPour()` et de la politique de blocage est une étape
  ultérieure, à décider après validation de la répétition contrôlée.
- Documenter la conservation de matière sur la répétition (matière
  créditée vs matière consommée vs unités terminées).
- Ne pas démarrer DDMRP tant que le défaut de §19.4 n'est pas traité ou
  explicitement accepté comme exception.

---

## 20. MTO-1 — Clôture du runtime baseline

**Run final corrélé : `RUN_1773129600000_1791048428560`.** Branche
`feature/mto-ddmrp-foundation`, HEAD de départ vérifié
`eda90ef17667214caa935972ae8835729e73b8aa`. Aucun `.alp`, aucun `.json`,
aucune correction métier.

### 20.1 Statuts de clôture

| Point | Statut |
|---|---|
| MTO-A runtime baseline | **PASS** |
| MTO-B customer Source → Make | **PASS** |
| A vs (s,Q) interaction | **RUNTIME CONFIRMED** |
| Double crédit strict de la même quantité | **NOT OBSERVED** |
| Replenishment non coordonné / Open Supply fragmenté | **RUNTIME CONFIRMED** |
| MTO-1 | **CLOSED** |

### 20.2 Configuration

- Stock produit fini initial : **100**.
- Matières initiales : **GPL_VRAC 0 / BOUTEILLE_VIDE_12KG 0 /
  ACCESSOIRES_KIT 0**.
- Stratégie : **MTO**. Nombre de commandes : **1**. Quantité : **10**.
- Seed : **1001**. Retard fournisseur : **désactivé**.
- `REAPPRO_1` : **absent** de ce run.

### 20.3 Chronologie observée

| t (simulé) | Événement |
|---|---|
| 84 | Création de `CMD_1`, stratégie MTO, quantité 10 |
| 85 | Validation de la commande |
| 88 | Déclenchement du chemin Source, besoin : GPL 125, bouteilles 10, accessoires 10 |
| avant finalisation A | La politique (s,Q) a déjà commencé à créditer les matières |
| 150 | Snapshot : GPL = 125, bouteilles = 0, accessoires = 10 |
| ≈151 | `MaterialReceived` de `CMD_1` : `GPL_VRAC recu=0.0 stock=125.0`, `BOUTEILLE_VIDE_12KG recu=10.0 stock=10.0`, `ACCESSOIRES_KIT recu=0.0 stock=10.0` |
| 153 | Planification Make |
| 270 | Stocks alimentés par (s,Q) jusqu'à environ 250 / 70 / 90, avant consommation significative |
| — | Consommation Make : GPL 125, bouteilles 10, accessoires 10 |
| — | `CMD_1` terminée, **SERVIE** |

**Lecture du crédit final** : `finaliserApprovisionnementCommande()`
recalcule le manque à la réception (ligne 3446). Le mécanisme (s,Q)
ayant déjà couvert GPL et accessoires, le mécanisme ad hoc ne crédite
que les 10 bouteilles restantes. C'est un comportement correct, prouvé
ici par le log.

### 20.4 Bilan matière

- Départ : **0 / 0 / 0**.
- Consommation Make : **125 / 10 / 10**.
- Stock final : **250 / 70 / 90**.
- Crédits totaux observables pendant le run : **375 / 80 / 100**.
  - dont mécanisme A (`finaliserApprovisionnementCommande()`) :
    **0 / 10 / 0** (preuve directe dans le `MaterialReceived`) ;
  - dont mécanisme (s,Q) : **375 / 70 / 100**.

**Conservation** : la consommation (125/10/10) est couverte par les
crédits ; le stock final excède le besoin de la commande. Le run final
ne reproduit donc **pas** la violation de conservation observée dans le
run exploratoire §19 (20 unités pour 10 unités de matière). Cette
violation est attribuée au run exploratoire, contaminé par
`REAPPRO_1` ; sa reproduction isolée reste à établir. Le défaut
`consommerMatieresPour()` (troncature à zéro sans blocage) reste
**statiquement réel** (§17.1), mais son classement comme bloqueur
(§19.4) n'est **pas confirmé** par le run final et doit être réévalué.

### 20.5 Requalification de l'interaction A + (s,Q)

Ce que le runtime démontre :

- deux mécanismes de réapprovisionnement indépendants agissent
  simultanément sur la même situation de pénurie ;
- ils ne partagent pas de vue commune d'Open Supply ;
- le mécanisme (s,Q) peut couvrir une partie du besoin pendant que
  l'approvisionnement ad hoc MTO est encore en cours ;
- `finaliserApprovisionnementCommande()` recalcule le manque et évite
  ici un double crédit strict pour GPL et accessoires ;
- malgré cela, le mécanisme (s,Q) poursuit ses propres réceptions et
  conduit à un stock final largement supérieur au besoin de la
  commande ;
- la décision de réapprovisionnement reste donc non coordonnée.

Ce que le runtime **ne démontre pas** : un double crédit strict de la
même quantité (**NOT OBSERVED**).

### 20.6 Dette de cohérence Source / Open Supply

Le chemin Source de `CMD_1` trace à t=88 un approvisionnement physique
de **125 / 10 / 10**, alors que le `MaterialReceived` final de cette
commande ne crédite réellement que **0 / 10 / 0**. Cette divergence
entre flux narré et crédit physique est conservée comme **dette de
cohérence Source / Open Supply**, à traiter avant toute implémentation
DDMRP qui s'appuierait sur les traces Source comme source de vérité.

### 20.7 Limites de cette clôture

- Un seul run final ; pas de répétition avec seed différent.
- La violation de conservation du run §19 n'a pas été reproduite
  isolément.
- Le lien causal exact entre la politique (s,Q) et la réception
  anticipée de GPL/accessoires avant t=150 n'a été établi que par la
  chronologie des logs, pas par un test contrôlé.

### 20.8 Suite

MTO-1 est clos. La suite (correction des défauts, décision DDMRP) n'est
pas engagée dans cette passe. Aucune correction de code n'a été
lancée.
