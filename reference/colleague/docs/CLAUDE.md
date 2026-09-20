# CLAUDE.md — SCONTO-SVU (VSM × SCOR simulation model)

Ce dépôt n'est **pas** un projet de code applicatif classique (pas de build, pas de tests unitaires, pas de dépendances npm/pip). C'est un **projet de simulation AnyLogic** combinant VSM (Value Stream Mapping) et SCOR (Supply Chain Operations Reference), avec une architecture multi-agents holonique (ADACOR/PROSA) et un export vers une ontologie RDF/OWL.

**Avant toute analyse ou modification, lire dans l'ordre :**
1. `PROJECT_OVERVIEW.md` — vue d'ensemble, objectif métier, flux de données.
2. `MODEL_STRUCTURE.md` — structure interne du modèle AnyLogic (agents, fonctions clés, expérience).
3. `SCENARIOS_AND_DATA.md` — schéma des scénarios JSON, base HSQLDB, format RDF/Turtle exporté.

## Inventaire des fichiers par catégorie

| Catégorie | Fichiers | Format |
|---|---|---|
| Modèle AnyLogic (le plus récent en premier) | `SCONTO_SVU_GENERIC10-4.alp`, `-3.alp`, `-2.alp` | XML (AnyLogic `.alp`) |
| Base de données embarquée (logging technique AnyLogic) | `database/db.*` | HSQLDB |
| Scénarios d'entrée (config métier par cas client) | `scenario_*.json` | JSON |
| Résultats d'un run de simulation | `SCONTO_SVU_RESULTS_<Client>_RUN_<t1>_<t2>.xlsx`, `export_<Client>.xlsx` | Excel |
| Export ontologique d'un run de simulation | `SCONTO_SVU_ABOX_<Client>_RUN_<t1>_<t2>.ttl` | RDF/Turtle |
| Icônes de présentation du modèle | `*.png` (racine) | Image |
| Sans lien avec le modèle | `Rapport journalier PAYZY-10 août 2026.pdf` | PDF |

## Points d'attention

- `SCONTO_SVU_GENERIC10-4.alp` est un **fichier XML unique de ~2,2 Mo / 53 000 lignes** — pour l'explorer, préférer `Grep`/recherche ciblée par motif (`Name><![CDATA[...`, `ClassName><![CDATA[...`, noms de fonctions) plutôt qu'une lecture linéaire complète.
- Le modèle est **générique** : toute la configuration métier (acteurs, postes, poids SCOR, hiérarchie ISA-95) vient des JSON de scénario, pas du code du modèle. Modifier un scénario JSON n'exige donc pas de modifier le `.alp`.
- Les paires de fichiers de résultats `.ttl` / `.xlsx` partageant le même suffixe `RUN_<t1>_<t2>` proviennent du **même run** et doivent être croisées ensemble.
- Plusieurs acronymes métier restent à confirmer avec l'utilisateur : **SCONTO**, **SVU**, **AER** (voir §4 de `SCENARIOS_AND_DATA.md`) — ne pas les développer de façon définitive sans confirmation.
- Ne pas modifier `database/db.*`, les `.ttl`, les `.xlsx` ou le `.alp` sans demande explicite : ce sont des artefacts de simulation générés, pas du code source à refactorer.
