# SCONTO-SVU Generic — Merge Workspace

Ce dépôt de travail sert **uniquement à la version générique SCONTO-SVU**.

## Règle de séparation

- `model/SCONTO_SVU_GENERIC_MASTER.alp` = **modèle générique maître**, destiné à fonctionner avec des scénarios JSON variés (ZENER et autres).
- `reference/colleague/SCONTO_SVU_GENERIC10-4_COLLEAGUE.alp` = **version donneuse** du collègue, à analyser et porter sélectivement.
- Les fonctions spécifiques au cas DataCo (Prophet 2017, Recalibrator DataCo, AutoCommande DataCo, vues DataCo, ressources Excel DataCo, bornage 2017) **ne doivent pas être introduites dans ce dépôt générique**.
- La variante DataCo reste une adaptation distincte, maintenue séparément à partir du noyau générique.

## Méthode de travail

1. Lire `CLAUDE.md`.
2. Lire les documents dans `reference/colleague/docs/` dans l'ordre indiqué.
3. Lire `docs/merge/ANALYSE_FUSION_COLLEGUE_VS_MASTER.md` et les notes de phases.
4. Travailler uniquement sur `model/SCONTO_SVU_GENERIC_MASTER.alp`.
5. Ne jamais remplacer le master par le fichier donneur complet.
6. Porter les changements par blocs fonctionnels, un commit par bloc.
7. Après chaque bloc : vérifier XML, IDs, références et produire un journal clair.
8. Le Build AnyLogic final est validé manuellement par l'utilisateur.
