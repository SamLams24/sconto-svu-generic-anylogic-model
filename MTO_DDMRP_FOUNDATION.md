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
