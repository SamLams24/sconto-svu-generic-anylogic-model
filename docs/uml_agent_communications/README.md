# Communications inter-agents SCONTO-SVU — documentation UML

Document technique présentant, sous forme de diagrammes UML d'activités et
de séquence, les communications réellement implémentées entre les agents
du modèle générique SCONTO-SVU (`model/SCONTO_SVU_GENERIC_MASTER.alp`).

## Contenu

- `SCONTO_SVU_UML_Communications_Agents.tex` — source LaTeX (XeLaTeX).
- `SCONTO_SVU_UML_Communications_Agents.pdf` — document compilé.
- `figures/` — sources TikZ de chaque diagramme (`uml-style.tex` = style
  partagé ; `NN-nom.tex` = contenu de la figure ; `standalone-NN-nom.tex` =
  wrapper pour export individuel, utilisé pour produire
  `UML_EXPORTS_SUPERVISION/`).

## Compilation

```
xelatex -interaction=nonstopmode SCONTO_SVU_UML_Communications_Agents.tex
xelatex -interaction=nonstopmode SCONTO_SVU_UML_Communications_Agents.pdf
```

(deux passes pour la table des matières et les renvois).

## Sources de vérité

Voir §2 du document. Aucun diagramme n'a été inventé : chaque message et
chaque identifiant d'agent provient de `tracerFluxHierarchique()` dans
`model/SCONTO_SVU_GENERIC_MASTER.alp`, de `POST_MERGE_COMPLETENESS_AUDIT.md`,
d'`EXPERIMENTATION_FOUNDATION.md`, ou de l'annexe déjà publiée
`documentation/appendices/g-messages-flux-global.tex` (dépôt de
documentation), elle-même auditée contre un export ABox d'un run réel.

## Portée

Ce dossier ne modifie aucun `.alp`, aucun code Java, aucun JSON de
scénario. Il est indépendant des travaux de consolidation E4/E5 en cours
sur `feature/pre-e4-consolidation`.
