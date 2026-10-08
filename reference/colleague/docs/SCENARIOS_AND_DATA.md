# Données du projet : scénarios JSON, base HSQLDB, export ontologique RDF/Turtle

> Analyse basée sur `scenario_ZENER_SA_Togo_v72.json`, `database/db.script` et `SCONTO_SVU_ABOX_ZENER_SA_Togo_RUN_1773129600000_1788040520740.ttl`. Aucun fichier de données n'a été modifié.

## 1. Schéma des scénarios JSON (`scenario_<Client>_v<N>.json`)

Chaque fichier scénario est l'unique source de configuration métier chargée par le modèle générique (au lieu de coder l'entreprise étudiée en dur). Structure de premier niveau :

```json
{
  "meta": { "schemaVersion", "modelName", "javaPackageName", "createdAt", "updatedAt",
            "nomEntreprise", "nbActeurs", "nbPostes", "nbScenarios", "nbResponsabilites", "nbMachines" },
  "parametresGlobaux": { ... },
  "acteurs": [ ... ],
  "postes": [ ... ],
  "scenarios": [ ... ],
  "machines": [ ... ],
  "fichesMatiere": [ ... ]
}
```

### `parametresGlobaux`
Paramètres économiques et de pondération SCOR au niveau de l'entreprise focale : `nomEntreprise`, `champDebit`, `chiffreAffaireParUnite`, `champCoutHoraireMainOeuvre`, `champCoutMatierePremiereParUnite`, `champValeurActifFixe`, `champDelaiPaiementJours`, et les 5 poids d'attributs SCOR `champPoidsRL/RS/AG/CO/AM` (doivent être ≥ 0, somme > 0). Compteurs de séquence (`seqFlux`, `seqResponsabilite`, `seqMachineSim`, `seqTrace`) pour la génération d'identifiants.

### `acteurs[]`
Un acteur = un intervenant de la chaîne (fournisseur, entreprise focale, client...). Champs clés : `idActeur`, `nom`, `categorie` (ex. `FOURNISSEUR`, `ENTREPRISE_FOCALE`), `description`, `delaiPaiementJours`, `politiqueAppro` (ex. `PERIODIQUE`), `intervalleAppro`, `quantiteParAppro`, `idsMicroActivites` (liste de codes SCOR niveau 3 assignés à cet acteur, ex. `["sD1.2.2","sP4.4.1","sS1.4.1", ...]`), `modeApproMRP`.

### `postes[]`
Un poste = un nœud VSM/processus élémentaire de la chaîne (71 dans le cas ZENER). Champs clés : `idPoste`, `nom`, `codeSCOR`, `typePoste`, `loiTemps` (loi de distribution du temps de traitement), `capaciteSimultanee`, `niveauStock`, `chainesPrecedents` (liens amont), `idActeurResponsable`, `regleAiguillage`, `niveauISA95`, `politiqueStock`, `tauxVA` (valeur ajoutée), coûts (`coutHoraireMainOeuvre`, `coutMatierePremiereParUnite`, `valeurActifFixe`), `idsResponsabilites`, `idsOperationalAgents`, `idsMachines`, `estPointEclatement` (point de divergence de flux).

### `scenarios[]`
Variantes de débit/produit à simuler (5 dans le cas ZENER) : `typeProduit`, `sequence`, `debitParHeure`, `debitParHeureBase`, `nomenclature`.

### `machines[]`
Ressources physiques (1 dans le cas ZENER) : `idMachine`, `nom`, `idMicroActivite`, `type`, `capacite`, `cycleTime`, `mtbf`, `mttr` (fiabilité/maintenabilité), `active`.

### `fichesMatiere[]`
Fiches d'approvisionnement matière (3 dans le cas ZENER) : `idMatiere`, `stockDisponible`, `stockSecurite`, `delaiObtentionHeures`, `idFournisseur`.

> Une fonctionnalité de **chargement CSV complémentaire** existe aussi dans le modèle (`config_<nomEntreprise>.csv`), en plus du JSON — voir `MODEL_STRUCTURE.md` §3f. Son rôle exact par rapport au JSON n'a pas été creusé ici.

## 2. Base de données HSQLDB (`database/`)

Fichiers : `db.data`, `db.lck` (verrou), `db.log`, `db.properties`, `db.script`. C'est la base **embarquée standard générée automatiquement par AnyLogic** pour la journalisation ("DB Logging") d'une simulation — toutes les tables trouvées dans `db.script` portent le suffixe `_RAW_LOG` et sont **générées par AnyLogic lui-même**, pas par une logique métier custom :

| Table | Contenu |
|---|---|
| `AGENT_TYPES_RAW_LOG` / `AGENTS_RAW_LOG` / `AGENT_ELEMENTS_RAW_LOG` | Référentiel des types d'agents, instances d'agents créées, et leurs éléments internes (paramètres, variables). |
| `DESTROYED_AGENTS_RAW_LOG` | Agents détruits pendant la simulation. |
| `AGENT_PARAMETERS_RAW_LOG` | Valeurs de paramètres par agent. |
| `AGENT_TYPE_STATECHARTS_RAW_LOG` / `STATECHART_STATES_RAW_LOG` / `STATECHART_TRANSITIONS_RAW_LOG` | Journalisation des machines à états (statecharts) — états traversés, transitions. |
| `TRACE_RAW_LOG` | Messages de trace textuels horodatés par agent. |
| `EVENTS_RAW_LOG` | Déclenchements d'événements. |
| `AGENT_MOVEMENT_RAW_LOG` | Déplacements d'agents animés (vitesse, dates). |
| `AGENT_MESSAGES_RAW_LOG` | Messages échangés entre agents (émetteur/destinataire). |
| `FLOWCHART_ENTRIES_RAW_LOG` / `FLOWCHART_PROCESS_STATES_RAW_LOG` | Passages dans les blocs de la bibliothèque Process Modeling (postes/files/délais). |
| `STATISTICS_RAW_LOG`, `DATASETS_RAW_LOG`, `HISTOGRAMS_RAW_LOG` | Statistiques agrégées, séries de données, histogrammes. |
| `RESOURCE_UNIT_STATES_RAW_LOG`, `RESOURCE_POOL_UTILIZATION_RAW_LOG`, `RESOURCE_UNIT_UTILIZATION_RAW_LOG` | Utilisation des ressources (machines/opérateurs). |
| `FLUID_*_RAW_LOG` | Journalisation de flux continus (si des blocs "Fluid" sont utilisés). |

**Aucune table métier custom** (SCOR/VSM) n'a été trouvée dans `db.script` — la persistance métier propre au modèle passe par les exports Excel et RDF, pas par des tables SQL dédiées. Cette base sert donc uniquement au **logging technique standard AnyLogic**, activable/désactivable via les propriétés de logging de la simulation.

## 3. Export ontologique RDF/Turtle (ABox par run)

Chaque run de simulation exporte un fichier `SCONTO_SVU_ABOX_<Client>_RUN_<t1>_<t2>.ttl` :
- `t1` = timestamp (ms epoch) fixe identifiant le **scénario/run logique** (`1773129600000` pour tous les runs ZENER observés — probablement la date de début simulée).
- `t2` = timestamp (ms epoch) de **génération du fichier** (varie à chaque export, ex. déclenché par un événement métier comme `ORDER_CLOSED_CMD_48`).

### En-tête et ontologies importées
```turtle
@prefix core:  <http://www.sconto-vsm.org/core#> .
@prefix agent: <http://www.sconto-vsm.org/agent-extension#> .
@prefix aer:   <http://www.sconto-vsm.org/aer-extension#> .
@prefix run:   <urn:sconto-svu:runtime:RUN_<t1>_<t2>#> .
```
Trois modules d'ontologie sont importés et versionnés indépendamment :
- **Core** (v4.3.0) — concepts métier VSM/SCOR de base.
- **Agent Extension** (v1.1.2) — modélisation multi-agents/holonique.
- **AER Extension** (v1.1.2) — "Agent Execution/Exchange Reporting"(?) — protocole de messages entre agents. *Signification exacte de l'acronyme AER à confirmer avec l'utilisateur.*

### Classes principales rencontrées (avec nombre d'individus dans un run représentatif)
| Classe | Rôle |
|---|---|
| `core:RawEvent` (le plus nombreux, ~5000/run) | Événement brut de simulation. |
| `agent:AgentObservation`, `agent:AgentExecutionTrace` | Observations et traces d'exécution par agent. |
| `agent:HolonAgent`, `agent:OperationalExecutionAgent`, `agent:OperationalPilotAgent`, `agent:CoordinatorAgent`, `agent:TacticalAgent`, `agent:StrategicAgent`, `agent:BlackboardAgent`, `agent:MachineAgent` | Hiérarchie d'agents holoniques (cf. `MODEL_STRUCTURE.md` §4). |
| `aer:AERMessage`, `aer:ExecutionMessage`, `aer:OperationalOrderMessage`, `aer:ReportingMessage`, `aer:AmendmentMessage`, `aer:AERConversation` | Messages/protocole de communication inter-agents (typés par étape du cycle de commande). |
| `core:CustomerOrder`, `core:WorkInProcess`, `core:MicroActivity`, `core:FinishedProduct`, `core:Supplier`, `core:CycleTime` | Concepts métier VSM/chaîne logistique. |
| `core:SCORLevel`, `core:SCORMetricN` | Modélisation SCOR (niveaux de processus, métriques). |
| `core:FuzzyPerformanceGradeSet`, `core:AggregationRule`, `core:NormalizationRule` | Logique floue / agrégation / normalisation des métriques de performance (AHP + logique floue combinées). |
| `agent:AgentPerformanceRecord`, `agent:AgentCoordination`, `agent:AgentDecision` | Décisions et performances des agents, coordination inter-agents. |

### Propriétés notables
- Communication : `aer:sentByAgent`, `aer:sentToAgent`, `aer:hasMessageType/Priority/Status/Subject/Timestamp`, `aer:belongsToConversation`, `aer:usesCommunicationProtocol`.
- Blackboard : `agent:publishesToBlackboard`, `agent:readsFromBlackboard`, `agent:computesVSMIndicator`, `agent:storesObservation`, `agent:storesPerformanceRecord`.
- Hiérarchie/holonique : `agent:coordinatesAgent`, `agent:coordinatesProcess`, `agent:isSupervisedByAgent`, `agent:hasAgentLevel`, `agent:hasAgentRole`, `agent:hasAgentState` (`agent:Active` / `agent:Idle`), `run:holonicScope`.
- Métriques : `agent:computesSCORMetric`, `agent:contributesToPerformanceAttribute`, `agent:decisionBasedOnMetric`, `agent:hasDecisionScore`, `agent:hasPerformanceValue`/`hasPerformanceUnit`.
- Métadonnées de run : `run:exportReason` (raison du déclenchement de l'export, ex. `ORDER_CLOSED_CMD_48`), `run:simulationTimeSeconds`, `run:generatedAt`, `run:coreOntologyVersion`, `run:agentOntologyVersion`, `run:aerOntologyVersion`, `run:agentIdentityPolicy` (ex. `ACTOR_SCOPED_OPERATIONAL_V1`), `run:legacyOperationalIdCollisionsResolved`, `run:legacyPilotWithoutExecutionCount`, `run:legacyExecutionWithoutPilotCount` (compteurs de qualité/cohérence du mapping legacy → holonique).

### Convention de nommage des fichiers de run
```
SCONTO_SVU_ABOX_<NomClient>_RUN_<t1>_<t2>.ttl     ← individus RDF du run
SCONTO_SVU_RESULTS_<NomClient>_RUN_<t1>_<t2>.xlsx ← résultats tabulaires du même run (mêmes t1/t2)
```
Les paires `.ttl`/`.xlsx` partageant les mêmes `t1_t2` proviennent du même run de simulation et doivent être analysées ensemble.

## 4. Points à clarifier avec l'utilisateur

- Signification exacte des acronymes **SCONTO** et **SVU**.
- Signification exacte de **AER** (Agent Extension Reporting ? Agent Exchange/Execution Reporting ?) dans `aer-extension`.
- Rôle précis du fichier `config_<nomEntreprise>.csv` par rapport au JSON de scénario (redondant, complémentaire, ou hérité d'une version antérieure ?).
- Signification des marqueurs internes `S1.x`/`S2.x`/`C08`/`C14` dans les commentaires du code Java (repères de sprint de développement, à ne pas confondre avec les codes SCOR).
