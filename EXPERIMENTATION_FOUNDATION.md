# EXP-0 — Fondation expérimentale (graine + condition terminale)

Branche `feature/experimentation-foundation`, créée à partir de
`integration/claude-generic-merge` @ `ba05f348729ec607ae4716abf97db1f7b4a7cce6`.
Fichier modifié : `model/SCONTO_SVU_GENERIC_MASTER.alp`.

Cette passe ne touche ni Prophet, ni DataCo, ni E4/E5. Elle prépare le socle
commun (graine reproductible, condition terminale opérationnelle,
diagnostic, traçabilité export) requis avant toute campagne d'optimisation.

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
  le modèle.
- N'agit **que** sur `getDefaultRandomGenerator()`. Aucune règle SCOR,
  MTS/MTO/ETO, planification, KPI, stock ou AER n'est modifiée par ce
  paramètre — vérifié par relecture de chaque site d'insertion.

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
run:entitiesInProcessAtPosts    -- entier
run:pendingBusinessActions      -- entier
run:terminalDiagnosticText      -- texte, cause(s) si non terminal
```

Aucun calcul de PI, de KPI SCOR, de WIP affiché ou de coût n'a été modifié.

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
