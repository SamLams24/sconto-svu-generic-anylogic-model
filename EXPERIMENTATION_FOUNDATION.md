# EXP-0 — Fondation expérimentale (graine + condition terminale)

Branche `feature/experimentation-foundation`, créée à partir de
`integration/claude-generic-merge` @ `ba05f348729ec607ae4716abf97db1f7b4a7cce6`.
Fichier modifié : `model/SCONTO_SVU_GENERIC_MASTER.alp`.

Cette passe ne touche ni Prophet, ni DataCo, ni E4/E5. Elle prépare le socle
commun (graine reproductible, condition terminale opérationnelle,
diagnostic, traçabilité export) requis avant toute campagne d'optimisation.

**EXP-0.1 (micro-passe de vérification, même branche)** a audité trois
ambiguïtés avant le build manuel : la sémantique exacte de
`nombreCommandesOuvertes()` (§4), la couverture de `generationDemandeTerminee()`
pour le scénario E2/E4 et la garde anti-dépassement de quota (§4bis), et la
précision de la persistance JSON de la graine (§3, corrigée). Aucune de ces
vérifications n'a nécessité d'implémenter E4/E5 ni de modifier une règle
métier.

## 1. Sources d'aléatoire trouvées

Une seule source réelle : le générateur par défaut du moteur AnyLogic,
`getDefaultRandomGenerator()`. Vérifié par recherche exhaustive
(`normal|uniform|triangular|exponential|poisson|random|bernoulli|...`,
`java.util.Random`, `Math.random()`) : **tous** les tirages stochastiques du
modèle passent par cet unique générateur, sans exception :

| Emplacement | Rôle | Générateur |
|---|---|---|
| `LoiTemps.echantillon(Random rng)` (classe Java, temps de traitement des postes) | durée de traitement d'un poste | `getDefaultRandomGenerator()`, passé explicitement par l'appelant (2 sites d'appel) |
| Pannes machine (`tProchainePanne`, MTBF) et réparation (MTTR) | disponibilité machine | `main.getDefaultRandomGenerator()` |
| Probabilités de déclenchement / retour (`declenche = ... < p`, `retour = ... < pRetour`) | branchements probabilistes | `getDefaultRandomGenerator()` |
| Quantité de commande aléatoire (`quantitePourNouvelleCommande()`), délais métier aléatoires (`delaiAleatoireCourt()`) | génération de commande | `getDefaultRandomGenerator()` |
| Inter-arrivée exponentielle inline (bloc Source, propriété `<Code>`) | cadence d'arrivée | `getDefaultRandomGenerator()` |
| Sélection pondérée (routage / répartition) | aiguillage | `getDefaultRandomGenerator()` |

Aucune source stochastique indépendante (pas de second `java.util.Random`,
pas de `Math.random()`) n'a été trouvée. Conséquence directe : il n'y a
qu'un seul point de contrôle à maîtriser pour rendre tout le modèle
reproductible.

## 2. Mécanisme de graine AnyLogic retenu

Le modèle disposait déjà, au niveau `<SimulationExperiment>` du `.alp`,
d'un mécanisme natif :

```xml
<RandomNumberGenerationType>fixedSeed</RandomNumberGenerationType>
<CustomGeneratorCode>new Random()</CustomGeneratorCode>
<SeedValue>1</SeedValue>
```

C'est le mécanisme le plus simple et le plus sûr (principe demandé) : il
seed directement le générateur que 100 % des tirages consomment déjà. Il
n'a pas été modifié — il reste la graine par défaut si aucune graine
explicite n'est fournie.

Limite native : `SeedValue` est une propriété XML de l'expérience, non
lisible depuis le code Java de `Main` (confirmé — c'est exactement pourquoi
le champ d'export `run:randomSeed` existant valait déjà, avant cette passe,
le littéral `"NON_ACCESSIBLE_DANS_MAIN"`), et non modifiable sans rouvrir
le `.alp` dans l'IDE. Ce n'était donc pas suffisant pour piloter des
campagnes par configuration (« Seed 1001 », « Seed 2001 ») sans édition
manuelle répétée du XML.

## 3. Paramètre ajouté

Un paramètre expérimental **additif**, au même niveau que les champs déjà
existants du même type (`simToRealSeconds`, etc.) :

```java
public long seedExperiment = -1;          // -1 = non renseignée
public long seedExperimentEffective = -1; // valeur réellement appliquée pour CE run
public String seedExperimentSource = "NON_INITIALISEE";
```

- `seedExperiment >= 0` → appliqué par `getDefaultRandomGenerator().setSeed(seedExperiment)`
  en toute première instruction de `demarrerSimulation()`, avant tout reset
  de timer/générateur et avant `modeExecution = true`.
- `seedExperiment == -1` (défaut) → comportement strictement inchangé, le
  `SeedValue` natif de l'expérience continue de s'appliquer.
- Persisté dans le scénario JSON (`parametresGlobaux.seedExperiment`), pour
  permettre « Configuration A / Seed 1001 » puis « Configuration B / Seed
  1001 » par simple édition/duplication de fichier JSON, sans reconstruire
  le modèle. **EXP-0.1** : sérialisé via `String.valueOf(seedExperiment)`
  et relu via `jsonString(...)` + `Long.parseLong(...)` (repli sur un parse
  `double` pour compatibilité avec un JSON écrit par une version antérieure
  du champ) — un aller-retour par `(double) seedExperiment` /
  `jsonDouble(...)` perdrait la précision entière au-delà de 2^53 ; aucun
  helper `jsonLong` n'existe dans ce modèle (seuls `jsonString`,
  `jsonDouble`, `jsonInt`, `jsonBool`, `jsonStringList`).
- N'agit **que** sur `getDefaultRandomGenerator()`. Aucune règle SCOR,
  MTS/MTO/ETO, planification, KPI, stock ou AER n'est modifiée par ce
  paramètre — vérifié par relecture de chaque site d'insertion.
- **EXP-0.1 — preuve qu'aucun tirage n'a lieu avant `setSeed()`.** Audité :
  le `<StartupCode>` racine de `Main` (exécuté une fois au lancement de
  l'expérience, avant tout clic sur « Démarrer ») ne contient aucun appel à
  `getDefaultRandomGenerator()`/`Random`/`genererCommande()` — uniquement de
  la mise en place d'interface (messages, vues, listes de combo-box).
  L'événement périodique `verifierPanne` (qui déclenche `gererPanne()`,
  seul site hors `LoiTemps`/génération de commande consommant le générateur
  pour les pannes machine) porte la condition explicite
  `((Main) getOwner()).modeExecution` : il ne s'exécute donc jamais tant que
  `modeExecution` est `false`. Or `demarrerSimulation()` force
  `modeExecution = false` dès son entrée (juste après l'injection de la
  graine) et ne le repasse à `true` que plus loin dans la même fonction,
  après l'injection de la graine. Aucun chemin de code trouvé ne permet un
  tirage stochastique métier avant `getDefaultRandomGenerator().setSeed(...)`.

## 4. Condition terminale — définition exacte

Deux notions distinctes, comme demandé :

```java
generationDemandeTerminee()       // (A) plus aucune nouvelle commande externe ne sera générée
etatTerminalOperationnelAtteint() // (B) (A) ET aucun encours métier identifié
```

`etatTerminalOperationnelAtteint()` = **ET logique** de :

1. `generationDemandeTerminee()` — génération pilotée par commande, bornée
   (`limiterNombreCommandes`), et quota atteint (`commandesGenereesDepuisDemarrage
   >= nombreCommandesATester`). Une génération continue (non bornée) n'est
   jamais terminée par construction.
2. `nombreCommandesOuvertes() == 0` — fonction canonique **déjà existante**,
   réutilisée telle quelle.
3. `nombreReapprovisionnementsOuverts() == 0` — même filtre exact que
   `existeReapproOuvert()` (déjà existante), exposé en compteur.
4. `nombreEntitesEnTraitementPostes() == 0` — somme, sur tous les postes
   (`postes: ArrayList<PosteGenericAgent>`), de `p.queue.size() +
   p.delay.size() + p.lotEnCours.size()` — même source que le calcul de WIP
   déjà utilisé ailleurs dans le modèle (`wip = p.queue.size()+p.delay.size()`),
   complétée par `lotEnCours` (mécanisme de lot/jonction multi-amont, non
   couvert par le WIP affiché).
5. `nombreActionsMetierDiffereesPertinentes() == 0` — voir §5.

Volontairement **fondé sur l'état du système**, jamais sur `time() > X`.

### 4bis. EXP-0.1 — `nombreCommandesOuvertes()` et couverture de E2/E4

**Sémantique exacte de `nombreCommandesOuvertes()` (lue dans le code, pas
déduite du nom) :**

```java
public int nombreCommandesOuvertes() {
    int n = 0;
    for (CommandeAgent cmd : commandes) {
        if (cmd == null || estOrdreStockAutonome(cmd)) continue;
        if (!commandeEstTerminale(cmd)) n++;
    }
    return n;
}
```

`estOrdreStockAutonome(cmd)` (préfixe `REAPPRO_`) est explicitement exclu
avant le comptage : cette fonction ne compte **que** les commandes
clientes ouvertes (cas A de l'audit demandé), exactement le périmètre
attendu de `run:openCustomerOrders`. Aucun doublon créé : `diagnosticEtatTerminal()`
continue d'utiliser `nombreCommandesOuvertes()` tel quel pour
`commandesClientesOuvertes`, et `etatTerminalOperationnelAtteint()` vérifie
déjà séparément `nombreCommandesOuvertes() == 0` (clientes) ET
`nombreReapprovisionnementsOuverts() == 0` (REAPPRO), donc aucune commande
n'est ni oubliée ni comptée deux fois entre ces deux compteurs.

**Génération de E2 (baseline de E4) — mécanisme réel.** Aucun identifiant
littéral « E2 »/« E4 » n'existe dans le `.alp` (les campagnes E1-E5 sont une
numérotation de documentation, pas un objet codé). Le mécanisme de
perturbation identifié est le déclenchement manuel d'un « choc de demande »
(`declencherPicPonctuelDemande(int)` — pic ponctuel, appelle `genererCommande()`
directement — et `declencherRafaleCommandes(int,double)` — rafale, planifie
des actions différées `GENERER_COMMANDE`). Dans les deux cas, la commande
supplémentaire passe par `genererCommande()`, dont la toute première ligne
est :

```java
if (!peutGenererNouvelleCommande()) return;
```

et `peutGenererNouvelleCommande()` applique exactement les mêmes conditions
que `generationDemandeTerminee()` (`modeExecution`, `modePilotageParCommande`,
`limiterNombreCommandes`, `nombreCommandesATester`). Il n'existe donc aucun
chemin — normal ou choc de demande — qui crée une commande cliente hors de
ce garde unique.

**Conclusion : la définition actuelle couvre E4.** Sous réserve que la
campagne E2/E4 soit paramétrée en mode borné (`modePilotageParCommande=true`,
`limiterNombreCommandes=true`, `nombreCommandesATester` fixé) — condition
déjà nécessaire pour qu'une campagne soit comparable/répétable, et déjà la
convention observée sur toutes les campagnes existantes (ZENER Cas 1/2/3,
campagnes DataCo 365 commandes). `generationDemandeTerminee()` n'a donc pas
été généralisée ni modifiée.

**Garde `GENERER_COMMANDE` au-delà du quota (audit demandé au point 3) :**
le garde exact est `peutGenererNouvelleCommande()`, appelé en tête de
`genererCommande()` — identifié ci-dessus. Une action différée
`GENERER_COMMANDE` exécutée après que le quota est atteint aboutit donc à un
`genererCommande()` qui retourne immédiatement sans créer de commande.
Aucune commande supplémentaire n'est possible au-delà du quota par ce
chemin. L'exclusion de `GENERER_COMMANDE` du compteur
`nombreActionsMetierDiffereesPertinentes()` (§5) reste donc correcte et n'a
pas été modifiée.

## 5. Structures vérifiées par le terminal, et exclusions justifiées

| Structure | Participe au terminal ? | Justification |
|---|---|---|
| `commandes` (commandes clientes, via `commandeEstTerminale()`) | Oui | prédicat canonique existant, réutilisé sans modification |
| `commandes` (ordres `REAPPRO_*`, via `estOrdreStockAutonome()`) | Oui | même filtre que `existeReapproOuvert()` existant |
| `postes[].queue` / `postes[].delay` | Oui | source déjà utilisée pour le WIP affiché |
| `postes[].lotEnCours` | Oui | lot en cours de constitution = travail engagé non relâché |
| `actionsMetierDifferees` (types `RECEPTION_COMMANDE`, `ANALYSE_STOCK`, `ANALYSE_MATIERE`, `FINALISER_APPROVISIONNEMENT`, `LANCER_PRODUCTION`, `LIVRAISON_DIRECTE`, `RECEPTION_CLIENT_DIRECTE`) | Oui | étapes d'orchestration liées à une commande réelle encore ouverte |
| `actionsMetierDifferees` (type `GENERER_COMMANDE`) | **Non** | relève de la génération de demande (§4.1), pas d'un encours de traitement |
| `actionsMetierDifferees` (type `ANIM_RETOUR_VEHICULE`) | **Non** | animation de présentation, sans effet métier |
| Pannes machine planifiées (`tProchainePanne`, MTBF/MTTR) | **Non** | risque stochastique futur sur la capacité, pas un encours déjà engagé |
| Événements périodiques (timers de recalcul KPI, monitoring) | **Non** | activité de suivi, continue par construction, ne représente aucun travail métier en attente |
| `EN_LIVRAISON` (statut de commande) | Oui, indirectement | déjà non-terminal via `commandeEstTerminale()` (seuls `SERVIE`/`EN_RETARD`/`REFUSEE`/`BLOQUE_*` sont terminaux) ; aucune vérification séparée nécessaire |

Aucune collection inexistante n'a été inventée : chaque champ ci-dessus a
été localisé et vérifié dans le modèle avant d'être utilisé.

## 6. Diagnostic ajouté

```java
diagnosticEtatTerminal()      // Map<String,Object> : les 5 compteurs + terminalAtteint
diagnosticEtatTerminalTexte() // rendu texte listant la ou les causes de non-terminalité
```

Ne recalcule rien : assemble les fonctions du §4/§5.

## 7. Champs ajoutés à l'export (`exporterABoxRuntimeTTL`)

Additifs uniquement — aucun champ existant renommé ni supprimé
(`run:randomSeed` reste tel quel) :

```
run:experimentSeed              -- valeur du paramètre seedExperiment (ou "NON_RENSEIGNEE")
run:experimentSeedEffective     -- valeur réellement appliquée par setSeed() pour ce run (ou "NON_APPLICABLE")
run:experimentSeedSource        -- "PARAMETRE_EXPLICITE_seedExperiment" | "SEEDVALUE_NATIF_EXPERIENCE_ANYLOGIC"
run:demandGenerationFinished    -- OUI/NON
run:terminalReached             -- OUI/NON
run:openCustomerOrders          -- entier
run:openReplenishments          -- entier
run:entitiesInProcessAtPosts    -- entier (voir EXP-0.1 ci-dessous : nombre d'occupations, pas garanti comme un compte d'agents uniques)
run:pendingBusinessActions      -- entier
run:terminalDiagnosticText      -- texte, cause(s) si non terminal
```

Aucun calcul de PI, de KPI SCOR, de WIP affiché ou de coût n'a été modifié.

### 7bis. EXP-0.1 — sémantique de `entitiesInProcessAtPosts`

Audité : pour un même poste, le code de `lotEnCours` (`lotEnCours.add(agent)`)
n'intervient qu'après que l'entité a quitté le traitement du `delay` de ce
poste (commentaire du modèle : « elle a bien été traitée par CE poste, mais
n'est pas encore relâchée vers la suite ») — `queue`, `delay` et `lotEnCours`
représentent donc des états séquentiels, pas concurrents, **pour un même
poste**. Une entité de flux (`FluxEntity`) ne peut par ailleurs se trouver
que sur un seul poste à la fois dans le graphe de flux (routage séquentiel
d'un poste au suivant). Ces deux observations rendent un double comptage
peu probable, mais aucune preuve exhaustive (à l'échelle de tout le modèle,
tous chemins de routage/duplication compris) n'a été produite dans le temps
de cette micro-passe. Le champ `entitiesInProcessAtPosts` est donc décrit
et documenté comme **un nombre d'occupations/présences** dans les
structures de traitement des postes (`queue`+`delay`+`lotEnCours`), et non
présenté comme un nombre d'agents métier uniques garanti — conformément au
principe de prudence demandé.

## 8. Protocole de reproductibilité (à exécuter manuellement dans AnyLogic)

**TEST A — même graine.** `seedExperiment=1001` sur une configuration
identique, deux runs A1/A2. Attendu : mêmes tirages stochastiques
pertinents et mêmes résultats déterministes du run (`export_DataCo
Global.csv`/KPI identiques à tolérance numérique près).

**TEST B — graine différente.** Même configuration, `seedExperiment=1002`.
Attendu : au moins une trajectoire stochastique différente de TEST A.

**TEST C — configurations différentes, même graine.** Deux configurations
distinctes (ex. futurs réglages E4), toutes deux `seedExperiment=1001`.
Attendu : les deux consomment la même source de hasard **jusqu'au premier
point de divergence comportementale**.

### Limite connue des nombres aléatoires communs (CRN)

Le modèle utilise **un seul flux aléatoire partagé** pour tous les
mécanismes stochastiques (§1), consommé dans l'ordre d'exécution des
événements. Deux configurations qui déclenchent un nombre différent
d'événements stochastiques avant un point donné (capacité différente →
nombre de décisions de routage différent ; taille de lot différente →
timing de déclenchement différent ; politique de stock différente →
nombre de réapprovisionnements différent) **désynchronisent le flux
aléatoire au-delà de ce point**, même en partant de la même graine. Ce
n'est pas un appariement CRN classique par flux dédié (un `Random`
indépendant par mécanisme) : TEST C montre un alignement initial correct,
pas une garantie d'alignement flux par flux sur toute la durée du run dès
que les configurations comparées divergent structurellement. Une
séparation en générateurs dédiés par mécanisme resterait à faire si un
appariement CRN strict devenait nécessaire — hors périmètre de EXP-0.

## 9. Protocole de test terminal (à exécuter manuellement)

**CAS 1** — demande encore en cours de génération → `generationDemandeTerminee()=false`
→ `etatTerminalOperationnelAtteint()=false`, `diagnosticEtatTerminalTexte()`
signale « génération de la demande non terminée ».

**CAS 2** — génération terminée, mais commandes/réappro/postes/actions
encore ouverts → `generationDemandeTerminee()=true`,
`etatTerminalOperationnelAtteint()=false`, le diagnostic texte énumère
précisément les compteurs non nuls.

**CAS 3** — génération terminée, aucun encours → `etatTerminalOperationnelAtteint()=true`,
diagnostic = « Etat terminal opérationnel atteint. »

## 10. Limites connues

- L'exécution AnyLogic (parse/build/run) n'a pas pu être lancée depuis cet
  environnement (pas d'outil de build headless dans cette distribution
  PLE) : validée uniquement par analyse statique (XML bien formé, chaque
  bloc Java inséré vérifié équilibré accolade par accolade et parenthèse
  par parenthèse). Build/run manuel requis avant toute fusion, conformément
  à la convention du dépôt.
- `seedExperimentEffective`/`run:experimentSeedEffective` ne peuvent
  documenter que la valeur appliquée par `seedExperiment` explicite ; la
  valeur native `SeedValue` de l'expérience, quand elle est utilisée par
  défaut, reste non lisible depuis `Main` (limite du moteur AnyLogic, pas
  de cette implémentation).
- Voir §8 pour la limite structurelle des nombres aléatoires communs sur
  un flux partagé.
- E4 et E5 ne sont pas implémentés par cette passe : aucune variable de
  décision, aucun espace de 144 configurations, aucune boucle Pareto/AHP
  n'a été ajoutée.
