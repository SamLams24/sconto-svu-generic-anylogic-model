# Cadrage technique C0 — Consolidation pré-E4

Passe de **décision de conception**, pas de correction. Aucun `.alp`
modifié pendant C0. Aucune anomalie AN-01…AN-12 corrigée. Aucune
implémentation E4. Réalisée sur `feature/pre-e4-consolidation`, créée
depuis `feature/experimentation-foundation` @ `90738dfa428aa25d683aa524766b0289a63eb27f`
(HEAD au moment de la création de branche, après le commit figeant
`POST_MERGE_COMPLETENESS_AUDIT.md`).

Ce document s'appuie sur `POST_MERGE_COMPLETENESS_AUDIT.md` (cité
directement plutôt que redérivé) et ajoute les vérifications
complémentaires nécessaires aux décisions demandées ici.

---

## 1. But de C0

Résoudre, avant toute consolidation ou implémentation E4 :
- l'architecture expérimentale E4 (Option A vs B) ;
- la disponibilité réelle de x1–x4 ;
- la définition correcte de x3 ;
- le scope fonctionnel exact d'E4 ;
- quelles anomalies (AN-01…AN-12) doivent réellement être corrigées avant
  E4, et lesquelles peuvent attendre.

Aucune valeur de grille expérimentale n'est fixée dans ce document.

---

## 2. Architecture E4 — audit de l'Option A (nouvelle instance par run)

*Méthode : vérification code-par-code de chaque point demandé, plus
connaissance du fonctionnement standard d'une expérience AnyLogic
Parameter Variation (fonctionnalité native, non spécifique à ce modèle).
Aucune expérience Parameter Variation n'a été créée.*

### 2.1. Paramètres accessibles avant chaque run — **obstacle réel découvert**

Vérification directe : `Main` (l'agent racine du modèle) **ne déclare
aucun `<Variable Class="Parameter">` à son propre niveau** (0 occurrence
trouvée entre le début de la classe `Main` et son bloc de fonctions).
Toutes les variables candidates à devenir des facteurs expérimentaux
(`seedExperiment`, `capaciteSimultanee`, `tailleLot`, les champs de
politique de stock) sont soit des `PlainVariable` internes à `Main`
(état/config UI), soit des `<Variable Class="Parameter">` déclarées sur
`PosteGenericAgent` — une classe **peuplée dynamiquement depuis le JSON
de scénario**, pas une structure fixe que l'expérience pourrait référencer
directement par un chemin stable.

**Conséquence concrète** : une expérience `Parameter Variation` AnyLogic
standard varie nativement les Paramètres déclarés de l'agent racine
qu'elle instancie. Puisque `Main` n'en déclare aucun aujourd'hui, il n'y a
**rien à brancher directement** sur un plan d'expérience natif tel quel.
Ce n'est pas un obstacle bloquant (AnyLogic permet à une expérience
Parameter Variation de définir ses **propres** paramètres d'expérience et
d'exécuter du code Java "avant chaque run" pour les pousser dans le modèle,
p. ex. `root.seedExperiment = valeurExperimentale;`), mais **ce n'est pas
non plus déjà prêt** : il faudrait soit (a) ajouter de véritables
Parameters à `Main` pour `seedExperiment` et les autres facteurs
scalaires, soit (b) écrire ce code d'injection dans l'expérience
elle-même. Les deux options sont des modifications futures (l'option (a)
touche le `.alp`, explicitement hors périmètre de C0).

### 2.2. Seed par réplication

**Compatible, sans obstacle** : `seedExperiment` est déjà un champ `long`
public sur `Main`, appliqué en tête de `demarrerSimulation()` via
`getDefaultRandomGenerator().setSeed(seedExperiment)` (EXP-0, revérifié
§6 de l'audit). Il suffit qu'une expérience Parameter Variation écrive
`root.seedExperiment = <valeur>;` avant chaque run pour contrôler la
graine par réplication — aucune modification de logique métier requise
pour ce point précis, seulement l'écriture (future) du code d'expérience
lui-même.

### 2.3. Création d'une nouvelle instance de `Main`

**Compatible, confirmé par le comportement runtime déjà observé** : c'est
exactement le Cycle C déjà validé empiriquement en EXP-0.4V/clôture
(`EXPERIMENTATION_FOUNDATION.md` §14.8) — une nouvelle exécution de
l'expérience recrée `Main` et toutes ses populations. Une expérience
Parameter Variation AnyLogic fonctionne nativement sur ce principe (une
instance de modèle par run de réplication) : **c'est exactement le
comportement déjà confirmé comme le seul actuellement accessible dans ce
modèle**, ce qui va dans le sens d'Option A plutôt que d'y faire obstacle.

### 2.4. Chargement scénario/JSON par réplication

**Obstacle réel non résolu, à documenter (pas à corriger ici)** : le
chargement du scénario JSON se fait aujourd'hui via une interaction
utilisateur explicite (sélection dans une liste déroulante UI, puis
validation) — `clearScenarioBeforeJsonLoad()` et les fonctions de parsing
associées existent (confirmé), mais **aucun point d'entrée programmatique
séparé du clic utilisateur n'a été identifié dans cette passe** pour
charger un scénario JSON donné depuis le code d'une expérience Parameter
Variation sans interaction manuelle. Pour 144+ configurations automatisées,
ce chargement devrait être piloté par code depuis l'expérience (appeler la
fonction de chargement JSON directement avec un chemin de fichier variable
par réplication) — techniquement plausible puisque la fonction existe et
est appelable, mais **non vérifié comme fonctionnant hors du flux UI
actuel** dans cette passe (aucun test effectué, code non lu ligne à ligne
pour confirmer l'absence de dépendance à un composant d'interface).

### 2.5. Exports individualisés

**Partiellement en place** : `aboxRunId` est généré automatiquement
(`"RUN_" + configured + "_" + wallClock`) si vide, remis à `""` au début
de `demarrerSimulation()` — chaque run produit donc déjà un identifiant
distinct par construction (basé sur l'horloge murale, pas sur un numéro de
réplication explicite). Les fichiers Excel/TTL exportés portent déjà ce
`runId` dans leur nom (confirmé par les conventions vues dans
`EXPERIMENTATION_FOUNDATION.md`/`RUN_REFERENCE.md` des passes précédentes,
motif `..._RUN_<t1>_<t2>`). **Manque identifié** : aucun champ export
actuel n'encode explicitement un « numéro de configuration » ou « numéro
de réplication » au sens d'un plan d'expérience E4 (144 configurations ×
N réplications) — seul l'horodatage et la graine (`experimentSeed`,
EXP-0) distinguent les runs aujourd'hui. À ajouter lors d'une future
implémentation E4, pas un obstacle pour C0.

### 2.6. Identification run/configuration/réplication

Voir §2.5 — la graine et l'horodatage identifient un run de façon unique
aujourd'hui, mais **pas la configuration factorielle** (quelles valeurs de
x1–x4 ont produit ce run) ni le **numéro de réplication** au sein d'une
même configuration. Lacune confirmée, à combler lors de l'implémentation
E4, pas bloquante pour la décision d'architecture elle-même.

### 2.7. Terminalité

**Aucun obstacle** : `etatTerminalOperationnelAtteint()` et
`generationDemandeTerminee()` sont des fonctions pures de l'état du modèle
(§5 de l'audit), indépendantes de la façon dont le run a été démarré —
fonctionnent identiquement sous Option A ou B.

### 2.8. Lancement de 144+ configurations

**Aucune expérience Parameter Variation n'existe aujourd'hui**
(`POST_MERGE_COMPLETENESS_AUDIT.md` §2.1/§14.2, reconfirmé) : c'est de
l'infrastructure **à créer intégralement**, pas un obstacle technique
dans le modèle lui-même. AnyLogic supporte nativement des plans
factoriels de cette taille dans une expérience Parameter Variation ; rien
dans le modèle actuel n'empêche structurellement d'en créer une (au-delà
des points §2.1/2.4 déjà signalés comme travail requis, pas comme
obstacle bloquant).

### 2.9. Plusieurs seeds par configuration (réplications)

**Compatible** : conséquence directe de §2.2 et §2.3 — chaque réplication
étant une nouvelle instance de `Main` avec sa propre valeur de
`seedExperiment` poussée avant le run, plusieurs réplications par
configuration ne posent pas de problème structurel supplémentaire.

### 2.10. Agrégation ultérieure des résultats

**Non auditée en détail dans cette passe** : les exports existent par run
(Excel/TTL individuels), mais aucun mécanisme d'agrégation multi-run
(across replications/configurations) n'a été recherché dans le `.alp`
lui-même — une agrégation post-traitement (hors modèle, sur les fichiers
exportés) est l'approche la plus probable et n'est pas structurellement
empêchée, mais ceci n'a pas fait l'objet d'une vérification de code dans
cette passe.

### 2.11. Conclusion — Option A recommandée, avec réserve documentée

**Aucun obstacle structurel qui invaliderait Option A n'a été trouvé.**
Le Cycle C (nouvelle instance par run) est déjà le seul mode de
fonctionnement confirmé possible aujourd'hui (§2.3), ce qui va dans le
sens d'Option A plutôt que d'y faire obstacle. **Mais deux points
concrets restent non triviaux et devront être traités lors de
l'implémentation d'E4, pas supposés déjà résolus** : (§2.1) `Main` ne
déclare aucun Parameter natif — un mécanisme d'injection devra être ajouté
(côté expérience, ou par ajout de Parameters `.alp`) ; (§2.4) le
chargement JSON par réplication devra être piloté par code, non vérifié
comme découplé de l'UI dans cette passe. **Recommandation : Option A
retenue comme architecture cible**, avec ces deux points comme travaux
identifiés (pas des obstacles rédhibitoires) à traiter lors de la
création effective de l'expérience E4 (hors périmètre de C0).

**Conséquence sur AN-02** : confirmée. Sous Option A, chaque réplication
crée une nouvelle instance de `Main`/`postes`/`opAgents` — l'état
`OperationalAgent` non reseté (`etatHolon` et dérivés) ne peut pas fuiter
d'un run à l'autre puisqu'aucun run ne réutilise les agents d'un
précédent. **AN-02 devient non bloquant pour E4 sous Option A.** Non
corrigé dans cette passe, conformément à la consigne.

---

## 3. Scope fonctionnel d'E4

*Méthode : relecture du scénario JSON ZENER de référence, de la politique
de stock associée, et rappel des objectifs d'optimisation déjà
documentés dans `REPONSES_ENCADREMENT_PROPHET_ALPHA_OPTIMISATION.tex`
(dépôt de documentation, passe antérieure) et `MERGE_PROGRESS.md`.*

Le Run 01 (seed 1001, preuve terminale déjà validée) a été exécuté sur un
scénario dont le comportement de fulfillment observé (livraison directe
depuis le stock + reconstitution autonome `REAPPRO_1`) est
caractéristique d'un flux **MTS pur**, cohérent avec le commentaire
C14.55 du code (« MTS PUR... seule la politique de stock autonome... décide
de produire »). La finalité historique d'E4, telle que formulée dans les
échanges antérieurs (« E4, optimisation ZENER » — variables de capacité de
poste critique, sous-lots, règle de priorité, politique de stock, 144
configurations, exploration factorielle + Pareto + AHP) porte sur
l'**optimisation du fonctionnement logistique/production**, pas sur une
comparaison de stratégies de fulfillment (MTS vs MTO vs ETO) — cette
dernière question a toujours été traitée séparément comme un axe de
robustesse du moteur générique (Bloc E du merge), pas comme un facteur
expérimental E4 explicitement demandé dans les spécifications d'E4 vues
jusqu'ici.

**Conclusion, sans supposer** : **le scénario E4 de référence est MTS**,
cohérent avec (a) le seul run réellement validé en runtime à ce jour
(Run 01), (b) le comportement du scénario ZENER tel qu'observé, et (c) le
fait qu'aucune spécification E4 antérieure n'a demandé explicitement de
varier le mode de fulfillment comme facteur. **`mode MTS/MTO/ETO` n'est
donc PAS retenu comme facteur expérimental E4**, faute de justification
présente dans les objectifs d'optimisation déjà documentés — à réévaluer
explicitement si une future spécification E4 le demande.

**Conséquence documentée explicitement** : l'absence de validation
runtime MTO/ETO (statut « À VÉRIFIER » dans la matrice de complétude,
audit §23) **ne bloque pas E4** sous ce scope MTS. **MTO/ETO devront
néanmoins recevoir des smoke tests génériques du master** (non liés à la
campagne E4 elle-même) avant toute utilisation future les impliquant —
voir §14 ci-dessous, classés « validation générique non bloquante E4 ».

---

## 4. Matrice réelle x1–x4 — vue d'ensemble

*Détail complet par facteur en §5–§9. Cette section résume les statuts.*

| Facteur | Variable(s) réelle(s) | Statut |
|---|---|---|
| x1 — capacité | `PosteGenericAgent.capaciteSimultanee` | **PARTIEL** — Parameter réel, mais au niveau poste (peuplé par JSON), pas exposé au niveau Main pour injection directe par une expérience |
| x2 — sous-lots | `PosteGenericAgent.tailleLot` | **PARTIEL** — mécanisme réel confirmé (pas cosmétique), même réserve d'exposition que x1 |
| x3 — règle de priorité | **Aucune variable réelle actuelle** | **INERTE** — le seul mécanisme prévu à cet effet (`carnetCommandesMTO`) n'est jamais alimenté ; tous les points de compétition réels sont FIFO strict |
| x4 — politique de stock | `pointCommandeProduit`/`quantiteEconomiqueProduit` (mono), `quantiteEconomiqueParProduit` (multi, M.3), `FicheMatiere.stockSecurite`/`pointCommande` (matières) | **AMBIGU** — paramètres réels et mutables, mais deux mécanismes coexistants (mono/multi) dont la prévalence n'est pas confirmée pour tous les cas d'usage |

---

## 5. Audit approfondi — x1 (capacité)

`capaciteSimultanee` (int, `Variable Class="Parameter"` sur
`PosteGenericAgent`, `ModificatorType="STATIC"`) signifie concrètement,
par lecture du code consommateur : **le nombre d'entités que le bloc
`delay` du poste peut traiter simultanément** — confirmé par l'usage déjà
vu en EXP-0.4 (`enPanne ? 0 : capaciteSimultanee`, la capacité tombe à 0
pendant une panne, sinon elle vaut `capaciteSimultanee`). C'est donc une
**capacité de poste** (micro-activité individuelle), pas une capacité de
ligne agrégée, pas une vitesse/temps de traitement (celui-ci est porté
séparément par `LoiTemps`/`dureeTraitement()`), et pas une capacité
Source/Deliver globale (chaque poste, quel que soit son rattachement SCOR,
porte son propre `capaciteSimultanee`).

**Interprétation scientifique univoque** : oui, à condition de fixer
explicitement **quel poste** est désigné comme « poste critique » avant de
faire varier x1 — la variable existe au niveau poste, pas au niveau
modèle global ; faire varier x1 pour la campagne suppose de cibler un
identifiant de poste précis (`idPoste`) et de modifier uniquement son
`capaciteSimultanee`, sans toucher aux autres postes, pour isoler l'effet.
Ceci est **techniquement possible** (population `postes` accessible,
`trouverPoste(idPoste)` existe déjà comme fonction utilitaire dans le
modèle, vue en §8 de l'audit) mais nécessite un point d'injection
(§2.1/2.4) qui n'existe pas encore sous une forme prête pour une
expérience automatisée.

**Preuve que modifier x1 change le comportement** : oui, par lecture directe
(`enPanne ? 0 : capaciteSimultanee` contrôle directement le débit du bloc
`delay` — un changement de cette valeur change mécaniquement le débit
maximal du poste, donc potentiellement le WIP, le lead time et le
throughput global) — **non vérifiée par un test runtime comparatif** dans
cette passe (aucune exécution avec deux valeurs différentes n'a été faite),
seulement déduite du code.

**Statut : PARTIEL** — variable réelle, univoque, effet attendu
démontrable par lecture de code, mais exposition (injection expérimentale)
non prête.

---

## 6. Audit approfondi — x2 (sous-lots)

Mécanisme réel confirmé, **pas cosmétique** : `tailleLot` (int, Parameter
sur `PosteGenericAgent`) est utilisé conjointement avec le champ
`lotEnCours: ArrayList<FluxEntity>` — un mécanisme de **jonction/batching
multi-amont** (confirmé par le commentaire EXP-0 vu en §7 de l'audit :
« Bloc de batching/jonction multi-amont, non couvert par le WIP affiché »).
Le code source à la ligne 12571 montre `p.tailleLot = nbParents;` dans un
contexte de réapprovisionnement, ce qui indique que la taille de lot peut
aussi être **dérivée dynamiquement** du nombre de parents dans certains
cas, pas uniquement lue statiquement depuis le JSON.

**Points à clarifier avant de retenir x2 tel quel comme facteur, non
résolus dans cette passe (audit ciblé, pas une relecture complète du
mécanisme de lot)** :
- Les unités sont-elles créées individuellement puis regroupées en lot au
  niveau du poste, ou le lot est-il l'unité de création elle-même ? — non
  tranché dans cette passe, nécessite une relecture complète de
  `lotEnCours`/de la fonction qui le peuple, au-delà des deux sites déjà
  vus.
- Plusieurs sous-lots d'une même commande peuvent-ils être concurrents
  (en cours simultanément sur des postes différents) ? — non vérifié.
- Le mécanisme influence-t-il réellement l'ordonnancement (ex. un lot
  complet avant de libérer le suivant) ou seulement l'affichage/le
  comptage du WIP ? — la mention explicite « non couvert par le WIP
  affiché » dans le commentaire EXP-0 suggère un **effet réel sur le
  comptage**, mais l'effet sur le **débit/l'ordonnancement** proprement
  dit n'a pas été confirmé par lecture complète dans cette passe.

**Conséquences sur WIP/throughput/lead time/capacité** : plausibles par
construction (un lot plus grand devrait réduire la fréquence de
changement de série et potentiellement augmenter le WIP instantané par
poste) mais **non quantifiées ni vérifiées en runtime**.

**Statut : PARTIEL** — mécanisme réel confirmé (pas une créature
d'affichage), mais sa portée exacte sur l'ordonnancement/le débit n'est
pas entièrement tracée dans cette passe ; à approfondir avant de fixer x2
comme facteur E4 définitif, sans quoi son interprétation scientifique
resterait incertaine.

---

## 7. Audit approfondi — x3 (règle de priorité) : le point critique

*Cartographie exhaustive des points de compétition réels du modèle,
construite en croisant §2–§7 de l'audit précédent avec de nouvelles
vérifications ciblées (files de postes, discipline de queue AnyLogic
native).*

| Point de compétition | Entité ordonnée | Ordre actuel | FIFO implicite/explicite | Concurrence possible | Priorité actuelle | Effet MTS | Effet MTO | Effet ETO | Effet REAPPRO |
|---|---|---|---|---|---|---|---|---|---|
| `commandes` (population) | `CommandeAgent` | Insertion (`add_commandes()`), jamais réordonné | Implicite (ordre de création) | Oui (plusieurs commandes ouvertes simultanément, confirmé) | **Aucune** | Détermine l'ordre d'analyse de stock si plusieurs commandes MTS patientent | Idem pour MTO | Idem pour ETO (même code que MTO) | Les REAPPRO sont dans la même population, même absence de priorité |
| `actionsMetierDifferees` | `ActionMetierDifferee` | FIFO strict par insertion (confirmé §16 de l'audit, source unique de l'ordonnancement réel) | **Explicite** (structure `ArrayList`, traitée dans l'ordre) | Oui | **Aucune** | Ordonne l'exécution de `ANALYSE_STOCK`, `LANCER_PRODUCTION`, etc. pour toutes les commandes en attente, MTS comme MTO/ETO/REAPPRO confondus | Idem | Idem | Idem — **aucune priorité commande cliente / REAPPRO** dans cette file |
| `p.queue`/`p.delay` (par poste) | `FluxEntity` | `ArrayList`, pas de bloc `Queue` AnyLogic natif avec discipline configurable (**confirmé : 0 occurrence de `QueueDisciplineType`/`PriorityCode` dans tout le fichier**) | Implicite (ordre d'ajout) | Oui | **Aucune** | Détermine l'ordre de traitement physique sur un poste partagé | Idem | Idem | Idem |
| `carnetCommandesMTO` | `CommandeAgent` | Trié par priorité/EDD **quand peuplé** (`Collections.sort`, vu ligne 49601 de l'audit) — mais **jamais peuplé** | Explicite dans le code, **inerte en pratique** | Prévu pour MTO uniquement (nom explicite) | **Prévue, non active** | **Non concerné** (mécanisme nommé MTO, jamais dans le chemin MTS) | Prévu, mais 0 alimentation | Non distingué de MTO dans le code (§3 de l'audit) | Non concerné |
| Événement simultané (moteur AnyLogic) | Événements de simulation | `<SelectionModeForSimultaneousEvents>LIFO</SelectionModeForSimultaneousEvents>` | Explicite, **LIFO** (pas FIFO) | Oui, en cas d'égalité de temps | N/A (mécanisme moteur, pas métier) | Effet marginal possible sur l'ordre exact en cas d'égalité stricte de temps | Idem | Idem | Idem |

**Réponse à la question posée — à quel niveau x3 doit agir pour un effet
réel en campagne E4 MTS/ZENER :**

Puisque le scope E4 retenu est **MTS** (§3), et que `carnetCommandesMTO`
est nommément et structurellement un mécanisme **MTO** (jamais dans le
chemin de traitement MTS d'`analyserStockCommandeOrchestree()`, confirmé
§3 de l'audit), **le réparer n'aurait aucun effet sur une campagne E4
MTS** — c'est la mise en garde explicitement demandée par l'énoncé,
confirmée par le code. Le seul point de compétition qui a un effet réel
et mesurable sur une campagne MTS est :

- **(A) priorité entre commandes**, via l'ordre d'insertion dans
  `commandes` et sa répercussion sur l'ordre d'appel à
  `analyserStockCommandeOrchestree()` — pertinent quand plusieurs
  commandes MTS patientent simultanément faute de stock (le cas MTS
  documenté en C14.55 : « la commande patiente simplement »).
- **(B) priorité entre lots** — non applicable en MTS pur au sens strict
  (le fulfillment MTS ne crée pas de lot de production par commande, il
  puise dans le stock existant reconstitué par la politique autonome ;
  les lots concernent la **reconstitution** via REAPPRO, pas la commande
  cliente elle-même). Pertinent uniquement si x3 visait la priorisation
  des lots de réapprovisionnement entre eux, pas les commandes clientes.
- **(C) priorité entre unités dans les files de postes** — techniquement
  possible (les files existent, §7 ci-dessus), mais **aucune notion de
  priorité par commande ne redescend aujourd'hui jusqu'au niveau
  unité/poste** : une entité physique (`FluxEntity`) ne porte pas de
  champ de priorité observé dans cette passe.
- **(D) priorité entre commande client et ordre autonome REAPPRO** —
  **le point le plus directement pertinent pour une campagne MTS/ZENER** :
  aujourd'hui, `actionsMetierDifferees` (le seul ordonnanceur réel actif)
  ne distingue pas une action liée à une commande cliente d'une action
  liée à un `REAPPRO_*` — elles se disputent le même FIFO. Une politique
  de stock optimisée (x4) pourrait vouloir que la reconstitution du stock
  (REAPPRO) soit traitée en priorité (ou au contraire en second plan)
  par rapport à l'analyse d'une nouvelle commande cliente, ce qui
  aujourd'hui **n'est pas configurable**.

**Conclusion x3, sans implémentation** : le niveau **(A) priorité entre
commandes** et **(D) priorité commande cliente vs REAPPRO** sont les deux
seuls niveaux ayant un effet réel démontrable sur une campagne MTS/ZENER.
(B) et (C) n'ont pas de prise directe sur ce scope. `carnetCommandesMTO`
ne doit **pas** devenir artificiellement le mécanisme x3 — voir décision
formelle en §10.

---

## 8. Sémantique possible de x3 (une fois le niveau déterminé)

*Inventaire des règles conceptuellement représentables avec les données
déjà présentes dans le modèle, sans inventer de donnée absente. Aucune
grille finale sélectionnée.*

| Règle envisageable | Donnée existante nécessaire | Disponible aujourd'hui ? |
|---|---|---|
| FIFO (référence/statu quo) | Ordre d'insertion dans `commandes`/`actionsMetierDifferees` | **Oui** — comportement actuel par défaut |
| Priorité explicite de commande | Un champ `priorite`/`niveauPriorite` sur `CommandeAgent` | **Non trouvé** dans cette passe — nécessiterait l'ajout d'un champ (hors C0) |
| Date promise la plus proche (EDD) | `CommandeAgent.tPromise` | **Oui** — champ réel confirmé (§7 de l'audit, Bloc C.8), déjà utilisé pour le calcul de retard ; réutilisable comme clé de tri sans donnée nouvelle |
| Temps de traitement le plus court (SPT) | Durée estimée par commande/poste | **Partiel** — `LoiTemps`/`dureeTraitement()` existent au niveau poste, pas de temps de traitement total pré-calculé par commande avant exécution ; nécessiterait une estimation dérivée, pas une donnée déjà agrégée |
| Ordre client avant réapprovisionnement (ou l'inverse) | Distinction commande cliente vs `REAPPRO_*` | **Oui** — `estOrdreStockAutonome(cmd)` fournit déjà ce booléen (§4 de l'audit), directement réutilisable comme clé de tri binaire |
| Quantité la plus faible/plus forte d'abord | `CommandeAgent.qte` | **Oui** — champ déjà existant |

**Règles techniquement représentables sans inventer de donnée** : FIFO
(déjà actif), EDD par `tPromise`, priorité client/REAPPRO par
`estOrdreStockAutonome()`, tri par quantité. La « priorité explicite de
commande » et le SPT nécessiteraient soit un nouveau champ, soit un calcul
dérivé non trivial — à exclure d'une première itération x3 si l'on veut
rester strictement dans les données déjà présentes.

---

## 9. Audit approfondi — x4 (politique de stock)

Paramètres actuels confirmés par lecture directe :

- **Produit fini, mono-produit (héritage)** : `pointCommandeProduit`
  (point de commande `s`, calculé dynamiquement), `quantiteEconomiqueProduit`
  (`Q`, calculée) — champs globaux sur `Main`, resetés par run
  (`reinitialiserPolitiquesStockPourRun()`, confirmé §7 de l'audit).
- **Produit fini, multi-produit (Bloc M.3)** : `quantiteEconomiqueParProduit:
  LinkedHashMap<String,Double>` — cache par identifiant produit, même
  fonction de reset.
- **Matières** : `FicheMatiere.stockSecurite` (stock de sécurité,
  configurable), `FicheMatiere.pointCommande` (calculé :
  `stockSecurite + previsionHoraireMatiere * delaiTotalHeures`, formule
  confirmée ligne 1183 du fichier).
- **Pas de `max`/plafond de stock trouvé** dans cette passe pour le
  produit fini ou les matières (seuls `s`/`stockSecurite` et `Q` sont
  présents) — à confirmer par une recherche plus large si un plafond
  existe sous un autre nom, non trouvée dans le temps disponible.

**x4 doit représenter quoi ?** Réponse fondée sur les faits : **le couple
`(s, Q)` (réponse C)**, pas `s` seul ni `Q` seul isolément, car les deux
sont **calculés et utilisés conjointement** par la même politique de
réapprovisionnement continue (`verifierPolitiqueStockProduit()`,
`declencherProductionAutonome()`) — faire varier l'un sans l'autre
romprait la cohérence de la politique telle qu'implémentée aujourd'hui
(pas une politique à deux leviers indépendants, mais une formule couplée).
Il n'existe **pas de politique alternative sélectionnable** (option D,
« multiplicateur d'une politique existante », écartée : une seule formule
de calcul de `s`/`Q` existe, pas plusieurs stratégies entre lesquelles
choisir).

**Risque de variation implicite de plusieurs facteurs non contrôlés** :
**réel et confirmé** — `pointCommandeProduit` n'est pas un paramètre
JSON statique modifiable isolément : c'est une **valeur calculée** à
partir d'autres entrées (prévision horaire, délai). Faire varier x4
« directement » (en écrasant `pointCommandeProduit` après son calcul)
court-circuiterait la formule et pourrait produire une valeur incohérente
avec les autres paramètres du scénario (délai fournisseur, prévision de
demande) — **une variation de x4 doit donc probablement agir sur les
paramètres D'ENTRÉE de la formule** (le stock de sécurité, le délai
considéré) plutôt que sur le résultat calculé directement, pour rester
dans une interprétation scientifiquement propre. Ce choix n'est pas
tranché ici (aucune grille fixée), seulement signalé comme un risque
concret à éviter.

**Statut : AMBIGU** — paramètres réels et mutables (le stock de sécurité
en entrée), mais la variable directement candidate (`pointCommandeProduit`)
est un résultat calculé, pas un paramètre d'entrée indépendant ; la
coexistence mono/multi-produit (AN-08) ajoute une seconde source
d'ambiguïté sur laquelle des deux variables prévaut pour un scénario
donné.

---

## 10. AN-01 — décision de consolidation

**Décision retenue : D — abandonner/redéfinir x3, car aucune
interprétation propre au sens du mécanisme `carnetCommandesMTO` n'est
compatible avec le scope E4 (MTS) retenu en §3.**

Justification, fondée strictement sur les faits ci-dessus (§7) : le
mécanisme existant est nommément et structurellement MTO
(`carnetCommandesMTO`), jamais présent dans le chemin de traitement MTS
(§3 de l'audit, revérifié §7 ici). Le réparer (option A) donnerait un
mécanisme actif mais **sans aucun effet sur la campagne E4 MTS
envisagée** — ce serait corriger un problème réel sans résoudre le besoin
qui motive x3. Il n'y a pas de mécanisme x3 caché ailleurs que l'audit
précédent aurait manqué (option C, écartée : la cartographie exhaustive
des points de compétition en §7 ne révèle aucun autre point de tri par
priorité dans tout le pipeline). Conserver `carnetCommandesMTO` comme
strictement legacy/MTO (option B) reste vrai en soi, mais ne répond pas à
la question posée par x3 pour une campagne MTS.

**x3, tel qu'envisagé initialement (adapté de MTO), est donc redéfini** :
s'il doit rester un facteur E4, il doit être reconstruit **à un nouveau
niveau** — priorité entre commandes (§7-A) et/ou priorité commande
cliente vs REAPPRO (§7-D) — en réutilisant les données déjà présentes
(§8 : `tPromise`, `estOrdreStockAutonome()`, `qte`), pas en réparant
`carnetCommandesMTO`. **Aucune implémentation n'est faite ici** — ceci est
une décision de conception, à concrétiser dans une future étape de
consolidation (voir §15, C3) ou explicitement abandonnée comme facteur E4
si jugée hors priorité.

---

## 11. AN-02 — reclassification conditionnelle

**Reclassifiée, conformément à la conclusion d'Option A (§2.11) :**
AN-02 (`OperationalAgent.etatHolon` et dérivés non resetés) **n'est plus
considérée comme bloquante pour E4**, sous réserve qu'Option A
(nouvelle instance de `Main` par réplication) soit effectivement
l'architecture retenue lors de l'implémentation. Statut final : **dette
run-scoped documentée, risque Option B uniquement**. À rouvrir
explicitement si une future décision d'implémentation choisit malgré
tout une architecture de réutilisation d'instance (Option B) pour tout ou
partie de la campagne. **Aucun reset ajouté dans cette passe.**

---

## 12. AN-03 / AN-04 / AN-05 — plan de correction (préparation uniquement)

### AN-03 — seed du Run Manifest

- **Localisation exacte** : ligne 2491 (table de mapping du manifeste
  legacy, `{"graineAleatoire", "NON_ACCESSIBLE_DANS_MAIN", ...}`) et ligne
  9585 (`exporterABoxRuntimeTTL()`, `run:randomSeed =
  aboxLit("NON_ACCESSIBLE_DANS_MAIN")`).
- **Comportement actuel** : valeur figée en dur, jamais réévaluée, alors
  que `run:experimentSeed`/`experimentSeedEffective`/`experimentSeedSource`
  (EXP-0, quelques lignes plus loin dans la même fonction) exportent la
  vraie valeur dans le même run.
- **Valeur générique cible** : remplacer la constante par
  `String.valueOf(seedExperimentEffective)` (ou équivalent), en cohérence
  avec les champs EXP-0 déjà présents dans le même export.
- **Impact sur compatibilité des exports existants** : faible — un
  consommateur externe lisant `run:randomSeed` verrait une vraie valeur au
  lieu d'une constante, ce qui est strictement une amélioration
  d'information, pas un changement de type/format.
- **Risque de casser ontologie/consommateurs externes** : faible ; le
  champ change de valeur, pas de type ni de prédicat RDF.
- **Stratégie de migration** : aucune migration nécessaire, changement de
  valeur seul.

### AN-04 — `run:modelArtifact` legacy

- **Localisation exacte** : ligne 9600, `run:modelArtifact =
  aboxLit("SCONTO_SVU_FINAL_VSM_FIX_CANDIDATE.alp")`.
- **Comportement actuel** : chaîne littérale figée, sans rapport avec le
  fichier `.alp` réellement exécuté.
- **Valeur générique cible** : un mécanisme dynamique (nom du fichier
  modèle réellement chargé, si l'API AnyLogic l'expose à l'exécution) ou,
  à défaut, un champ explicitement marqué comme non fiable
  (`"NON_DETERMINABLE_A_LEXECUTION"`) plutôt qu'un nom de fichier
  obsolète qui induit en erreur. **Le choix exact n'est pas tranché ici**
  (dépend de la disponibilité réelle d'une API AnyLogic donnant le nom du
  fichier `.alp` courant, non vérifiée dans cette passe).
- **Impact sur compatibilité** : faible, changement de valeur.
- **Risque** : faible.
- **Stratégie de migration** : aucune.

### AN-05 — noms ABox `kpiZener`/`zener_*`/`ZENER_ACT_4_ONLY`

- **Localisation exacte** : champ `board.kpiZener` (déclaration non
  relocalisée dans cette passe, usages confirmés lignes 7713, 9704-9706,
  13815 de l'audit) ; littéraux `"zener_process_time"`,
  `"zener_waiting_time"`, `"zener_estimated_pce"`, `"ZENER Process Time"`,
  etc. (lignes 9704-9708) ; `"ZENER_ACT_4_ONLY"` (ligne 9689) ; `ctxZener`
  (variable locale, ligne 9687).
- **Comportement actuel** : la *computation* résout l'entreprise focale
  par rôle (`ActeurSC.ENTREPRISE_FOCALE`), donc générique ; seuls les
  **identifiants de champ et libellés exportés** sont nommés ZENER en dur.
- **Valeur générique cible** : renommer en termes génériques, par exemple
  `kpiEntrepriseFocale`, `focal_process_time`/`focal_waiting_time`/
  `focal_estimated_pce`, `"Focal Enterprise Process Time"`,
  `"FOCAL_ENTERPRISE_ONLY"`, `ctxFocal`.
- **Impact sur compatibilité des exports existants** : **plus élevé que
  AN-03/AN-04** — ceci change des **identifiants de champ/URI** dans le
  TTL, pas seulement une valeur littérale ; tout consommateur externe déjà
  branché sur `zener_process_time`/`ZENER_ACT_4_ONLY` cesserait de
  trouver ces clés.
- **Risque de casser ontologie/consommateurs externes** : **réel**, à
  traiter avec précaution (voir migration ci-dessous), contrairement à
  AN-03/AN-04 qui sont des changements de valeur sans risque de rupture
  structurelle.
- **Stratégie de migration recommandée (à valider, pas appliquée ici)** :
  exporter **les deux jeux de champs en parallèle** pendant une période de
  transition (anciens noms ZENER conservés en plus des nouveaux noms
  génériques), plutôt qu'un remplacement sec — ou, si aucun consommateur
  externe n'existe encore en pratique (à confirmer auprès de
  l'utilisateur), un remplacement direct est plus simple et sans coût de
  double maintenance.

**Aucune correction appliquée pendant C0**, conformément à la consigne.

---

## 13. AN-06 — multiproduit

**Décision** : puisque le scope E4 retenu est **MTS/ZENER mono-produit**
(§3 — Run 01, seul run validé, est mono-produit ; aucune spécification E4
antérieure ne demande de comparer plusieurs produits simultanément dans
la campagne), **AN-06 est reporté après E4**. La métrique
`nbTerminesParProduit` morte/à clés mélangées (§14 de l'audit) n'a aucun
effet sur une campagne mono-produit, puisqu'elle ne serait de toute façon
pas consommée pour distinguer des produits qui n'existent pas dans le
scope retenu. **Non corrigé dans cette passe.** À rouvrir explicitement
si une future extension d'E4 ou une campagne E5 (DataCo, intrinsèquement
multi-produit) en fait un prérequis.

---

## 14. Tests runtime pré-E4 — matrice minimale proposée

### OBLIGATOIRE AVANT E4 (couvre uniquement ce qui influence directement la campagne MTS/ZENER retenue en §3)

| Test | Objet | Justification |
|---|---|---|
| MTS nominal | Run complet MTS, terminalité atteinte | Déjà couvert par Run 01 — **PASS confirmé**, à ne pas re-décider, seulement documenté comme prérequis satisfait |
| Source (matière) | Réapprovisionnement matière déclenché et clôturé | Couvert par Run 01 via REAPPRO — **PASS confirmé** |
| Make | Production déclenchée, WIP retombe à 0 | Couvert par Run 01 — **PASS confirmé** |
| Deliver | Livraison directe depuis stock | Couvert par Run 01 — **PASS confirmé** |
| Réappro autonome | `REAPPRO_*` clôture correctement, n'est jamais compté comme commande cliente | Couvert par Run 01 — **PASS confirmé** |
| x1 (capacité) | Un run avec `capaciteSimultanee` modifié sur le poste critique produit un comportement mesurablement différent (WIP/lead time) d'un run de référence | **Non fait** — nécessaire pour valider que x1 a un effet réel avant de fonder une campagne dessus (§5 : effet déduit du code, jamais mesuré) |
| x2 (sous-lots) | Un run avec `tailleLot` modifié produit un comportement mesurablement différent | **Non fait** — même besoin que x1, avec la réserve supplémentaire du §6 (portée du mécanisme pas entièrement tracée) |
| futur x3 | Selon la redéfinition retenue (§10) : si (A) ou (D) est implémenté, vérifier que l'ordre effectif de traitement change réellement selon la règle choisie | Non applicable tant que x3 n'est pas reconstruit — test à définir après implémentation, pas avant |
| x4 (politique de stock) | Un run avec `stockSecurite`/délai modifié en entrée produit un `pointCommandeProduit`/`Q` différent et un comportement de réapprovisionnement mesurablement différent | **Non fait** — nécessaire pour confirmer que la variation agit uniquement sur x4 sans effet de bord non contrôlé (risque signalé §9) |
| Terminalité | Confirmée à nouveau sur chaque configuration de test ci-dessus (pas seulement Run 01) | Garantit que la terminalité EXP-0.3 reste valide hors du scénario exact de Run 01 |
| Seed | Reproductibilité seed identique vs seed différente, sur le scénario MTS/ZENER retenu, avec x1/x2/x4 à leurs valeurs de référence | Déjà validé en EXP-0.2/0.3/0.4 sur ce même scénario — **PASS confirmé**, à revalider uniquement si le scénario JSON de référence change |

### VALIDATION GÉNÉRIQUE NON BLOQUANTE E4

| Test | Objet | Justification |
|---|---|---|
| MTO smoke test | Un run MTO minimal atteint la terminalité sans erreur | Robustesse générale du master (Bloc E), **hors scope E4 MTS**, mais recommandé avant toute utilisation future impliquant MTO |
| ETO smoke test | Idem, pour ETO | Idem — d'autant plus utile que §3 a confirmé qu'ETO partage le code MTO sans distinction fonctionnelle propre |
| Multiproduit smoke test | Un run avec ≥2 produits atteint la terminalité, stocks par produit cohérents | Hors scope E4 (§13), mais utile pour la robustesse générale et pour préparer une éventuelle campagne E5 |
| Multi-commandes concurrentes | Plusieurs commandes ouvertes simultanément sur des postes partagés, sans écrasement d'état | Statut « à vérifier » dans la matrice de complétude (audit §23) ; pertinent pour la robustesse générale de toute campagne à charge élevée, y compris E4 si le nombre de commandes/configurations génère de la concurrence réelle |
| Panne réelle en runtime | Un run suffisamment long pour observer au moins une panne, vérifier que `nbPannes`/`tempsArretCumule`/OEE évoluent correctement | Dynamique panne/réparation jamais exercée à ce jour (EXP-0.4 §13.6/§14.8) — pertinent si OEE/disponibilité devient un indicateur de sortie de la campagne E4 |

---

## 15. Plan de consolidation

*Familles adaptées aux faits de cette passe, pas imposées mécaniquement.
Chaque étape est indépendante et peut être validée/commitée séparément.*

### C1 — Corrections métadonnées/export sans impact métier
- **Anomalies traitées** : AN-03, AN-04.
- **Fichiers touchés** : `model/SCONTO_SVU_GENERIC_MASTER.alp` (fonction
  `exporterABoxRuntimeTTL()` et sa table de mapping manifeste legacy).
- **Risque** : faible (changement de valeur, pas de structure).
- **Test requis** : re-export ABox sur un run court, vérification visuelle
  des champs `run:randomSeed`/`run:modelArtifact`.
- **Commit séparé recommandé** : oui, un seul commit ciblé.

### C2 — Généricité ABox (renommage de schéma)
- **Anomalies traitées** : AN-05.
- **Fichiers touchés** : `model/SCONTO_SVU_GENERIC_MASTER.alp` (mêmes
  fonctions que C1, plus le champ `board.kpiZener` sur `BlackboardAgent`
  et ses ~4 sites de lecture, cf. audit §8/§12).
- **Risque** : **modéré** — renommage d'identifiants d'export, décision de
  migration à valider avec l'utilisateur avant d'exécuter (double export
  transitoire vs remplacement sec, §12).
- **Test requis** : re-export ABox, vérification que tous les sites de
  lecture de `kpiZener` sont mis à jour cohéremment (éviter une
  `NullPointerException` si un site est oublié — cf. AN-12).
- **Commit séparé recommandé** : oui, distinct de C1 (risque différent).

### C3 — Reconstruction de x3 au bon niveau (décision §10)
- **Anomalies traitées** : AN-01 (redéfini, pas « réparé »).
- **Fichiers touchés** : nouveau code dans `analyserStockCommandeOrchestree()`
  ou un point d'entrée dédié, selon le niveau retenu entre (A) priorité
  commandes et (D) priorité client/REAPPRO (§7-8) — **niveau exact non
  choisi dans ce document**, à décider avant d'écrire C3.
- **Risque** : **le plus élevé du plan** — touche l'ordonnancement réel du
  flux MTS, donc potentiellement tous les scénarios existants validés
  (Run 01 inclus).
- **Test requis** : re-jouer Run 01 (ou équivalent) avec la règle par
  défaut = FIFO explicite (doit reproduire exactement le comportement
  actuel), puis avec une règle alternative, pour confirmer un changement
  de comportement mesurable sans régression sur le cas FIFO.
- **Commit séparé recommandé** : oui, impérativement isolé des autres
  étapes vu son risque.

### C4 — Exposition sûre des paramètres x1/x2/x4 pour une expérience
- **Anomalies traitées** : aucune anomalie numérotée, mais résout les
  obstacles §2.1/§2.4/§9 (injection de valeurs par réplication).
- **Fichiers touchés** : `model/SCONTO_SVU_GENERIC_MASTER.alp` (ajout
  probable de champs d'override niveau `Main`, appliqués après le
  chargement JSON et avant `modeExecution=true`, sur le modèle du point
  d'insertion déjà utilisé pour le reset panne EXP-0.4).
- **Risque** : modéré — nouveau code, mais suit un patron déjà validé
  (EXP-0.4).
- **Test requis** : confirmer qu'un override appliqué produit exactement
  le même effet qu'une modification manuelle du JSON pour la même valeur.
- **Commit séparé recommandé** : oui.

### C5 — Smoke tests (exécution manuelle, pas de code)
- **Couvre** : la matrice complète du §14 (obligatoires + non bloquants).
- **Fichiers touchés** : aucun (exécution runtime uniquement) — sauf si
  un test révèle un bug réel, auquel cas une correction séparée serait
  nécessaire (hors du plan C1-C6 lui-même).
- **Risque** : nul pour le modèle (lecture seule des résultats).
- **Commit séparé recommandé** : documentation des résultats uniquement
  (mise à jour d'`EXPERIMENTATION_FOUNDATION.md` ou équivalent), pas de
  commit de code.

### C6 — Création de l'expérience E4 (Parameter Variation)
- **Dépend de** : C3 (x3 fonctionnel) et C4 (paramètres exposés)
  terminés et testés ; C5 passé pour les tests obligatoires.
- **Fichiers touchés** : `model/SCONTO_SVU_GENERIC_MASTER.alp` (nouvelle
  `<ParameterVariationExperiment>`), plus code d'injection
  seed/config/réplication (§2.1-2.6).
- **Risque** : élevé en volume (nouvelle infrastructure), faible en
  impact sur l'existant (une expérience supplémentaire n'affecte pas
  l'expérience `Simulation` actuelle).
- **Commit séparé recommandé** : oui, dernière étape, sur une branche
  dédiée à l'implémentation E4 elle-même (pas `feature/pre-e4-consolidation`).

**Ordre recommandé** : C1 → C2 → C5 (partiel, tests obligatoires
réexécutés après C1/C2 pour confirmer l'absence de régression
d'export) → C3 → C5 (tests x3) → C4 → C5 (tests x1/x2/x4) → C6. C2 peut
être différé après C6 si la décision de migration (§12) n'est pas encore
arrêtée, sans bloquer le reste du plan.

---

## 16. Critères objectifs d'entrée en E4

E4 ne doit commencer que lorsque :

1. **Architecture de réplication fixée** : Option A confirmée et
   implémentée (C6), avec le mécanisme d'injection de seed/paramètres
   opérationnel (C4).
2. **x1–x4 ont une sémantique réelle et univoque** : x1/x2 exposés au bon
   niveau (C4) et testés (C5) ; x3 reconstruit au niveau pertinent (C3)
   et testé ; x4 clarifié entre variation d'entrée (stock de sécurité/
   délai) et résultat calculé (§9), avec la coexistence mono/multi-produit
   (AN-08) résolue au moins pour le scope MTS retenu.
3. **Aucun facteur n'est inerte** : en particulier, x3 ne doit plus
   reposer sur `carnetCommandesMTO` non alimenté.
4. **Seed contrôlable par réplication** : mécanisme d'injection en place
   et testé (C4/C5), pas seulement le champ `seedExperiment` existant.
5. **État isolé entre runs** : garanti par construction sous Option A
   (§2.3) — condition déjà satisfaite dès lors qu'aucune régression vers
   une réutilisation d'instance n'est introduite.
6. **Terminalité fiable** : déjà confirmée (EXP-0.3/EXP-0.4, Run 01) sur
   le scope MTS — à reconfirmer sur les configurations x1/x2/x4 testées
   en C5.
7. **Exports identifient configuration + seed + réplication** : lacune
   confirmée en §2.5/2.6, à combler dans C6 (au minimum un numéro de
   configuration et un numéro de réplication explicites dans le nom de
   fichier ou les champs ABox).
8. **Smoke tests des facteurs PASS** : la ligne « OBLIGATOIRE AVANT E4 »
   du §14 entièrement passée, avec les nouveaux tests x1/x2/x4/x3 (pas
   seulement les tests déjà couverts par Run 01).
9. **Décision de migration AN-05 arrêtée** (même si C2 est différée
   après C6, la décision migration-transitoire-vs-remplacement-sec doit
   être prise avant de publier des résultats E4 exploitables par un
   consommateur externe de l'export ABox).
10. **Scope E4 (MTS, §3) explicitement reconfirmé** au moment de lancer la
    campagne, pour éviter qu'une dérive de scope (ex. ajout tardif de
    MTO/ETO comme facteur) ne soit introduite sans review.

---

## 17. Retour de synthèse

Voir réponse de fin de tour pour le format demandé en 19 points ; ce
document constitue le livrable complet (`PRE_E4_CONSOLIDATION_DESIGN.md`),
non commité à ce stade, conformément à la consigne.

---

## 18. Suivi C1 — corrections métadonnées/export

**AN-03 (seed) corrigée.** `graineAleatoire` (manifeste legacy) et
`run:randomSeed` (ABox) exportent désormais `seedExperimentEffective`
(`String.valueOf(long)`, sans passage par `double`, cohérent avec
`run:experimentSeedEffective` déjà présent), avec le même repli
`"NON_APPLICABLE"` que ce champ jumeau plutôt qu'une nouvelle constante.
Confirmé par lecture directe de `demarrerSimulation()` :
`seedExperimentEffective` est bien la variable écrite immédiatement après
`getDefaultRandomGenerator().setSeed(seedExperiment)`. `run:experimentSeed`,
`run:experimentSeedEffective` et `run:experimentSeedSource` n'ont pas été
touchés (déjà corrects).

**AN-04 (modelArtifact) corrigée.** Aucune API AnyLogic fiable pour le nom
du `.alp` courant n'a été trouvée (et une inférence via `getClass()` aurait
été une réflexion fragile, écartée). Stratégie retenue : **Option B**,
constante centralisée `MODEL_ARTIFACT_NAME = "SCONTO_SVU_GENERIC_MASTER.alp"`,
réutilisée par le manifeste legacy (`modeleCandidate`) et l'export ABox
(`run:modelArtifact`). Un troisième site contenant l'ancien littéral,
non documenté dans ce fichier lors du C0 (`modeleCandidate` dans
`manifesteRunRows()`), a été découvert pendant l'audit C1 et corrigé pour
la même raison qu'AN-04.

**Validation statique** : XML bien formé (reparsé avec succès), aucun
identifiant AnyLogic ajouté ou dupliqué (modification limitée au code Java
en CDATA), aucune variable non résolue, aucune occurrence résiduelle de
`NON_ACCESSIBLE_DANS_MAIN` ni de `SCONTO_SVU_FINAL_VSM_FIX_CANDIDATE.alp`
dans le master générique. Diff limité aux fonctions `manifesteRunRows()`
et `exporterABoxRuntimeTTL()` plus la nouvelle constante ; aucun `x1`–`x4`,
AN-05, AER, SCOR, KPI, stock, ordonnancement ou RNG touché.

**Runtime restant à vérifier.** AnyLogic 8.9 est installé localement, mais
aucune build/validation dans l'IDE n'a été effectuée pendant cette passe
(interaction GUI hors de portée de cet environnement d'exécution). **Le
test runtime (re-export ABox sur un run court, vérification visuelle des
champs `run:randomSeed`/`run:modelArtifact`) n'est pas marqué PASS** et
reste une étape manuelle à exécuter avant de considérer C1 clos.
