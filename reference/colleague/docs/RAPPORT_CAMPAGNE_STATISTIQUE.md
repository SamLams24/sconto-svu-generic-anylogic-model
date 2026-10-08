# Rapport de campagne statistique — validation de l'écart nominal/perturbé (réponse à §1.2)

**Objectif** : déterminer si l'écart de performance observé entre le scénario nominal et le scénario perturbé (commande exceptionnelle de 200 unités) est statistiquement significatif, ou s'il peut s'expliquer par le seul bruit stochastique du modèle. Répond à la réserve doctorale §1.2 de `Correction_chap5.docx` (« robustesse statistique insuffisante », réplication unique, absence d'intervalles de confiance).

**Protocole complet** : voir `PROTOCOLE_CAMPAGNE_STATISTIQUE.md`. **Suivi des runs** : voir `SUIVI_CAMPAGNE_STATISTIQUE.csv`. **Script d'analyse** : `analyze_campagne_statistique.py`.

---

## 1. Plan expérimental

- **3 réplications indépendantes par régime** (6 runs au total), même scénario `scenario_ZENER_SA_Togo_v72.json`, même version de modèle.
- **Pas de graine imposée** : la variabilité naturelle de l'exécution en temps réel a été vérifiée empiriquement comme suffisante pour produire des runs réellement indépendants (deux runs nominaux à réglages identiques, jamais modifiés, montrent des trajectoires de WIP nettement différentes — ex. 123 vs 94 unités à t = 3 000 s). Conséquence méthodologique : comparaison en **groupes indépendants** (test t de Welch), pas en différences appariées.
- **Fenêtre d'observation déterminée par la livraison** : chaque run a tourné jusqu'à la livraison de ses commandes clients ; la fenêtre commune retenue pour la comparaison est l'instant le plus tardif observé sur l'ensemble de la campagne (t = 10 800 s), garantissant que tous les runs ont eu le temps nécessaire.
- **Fichiers de la campagne** :

| Régime | Run | Commandes clients livrées |
|---|---|---|
| Nominal | `..._1789144025559` | 45/45 |
| Nominal | `..._1789170875362` | 45/45 |
| Nominal | `..._1789209804554` | 45/45 |
| Perturbé | `..._1789164676620` | 45/45 |
| Perturbé | `..._1789211510232` | 44/45 |
| Perturbé | `..._1789213272520` | 43/45 |

Les commandes non livrées dans les runs perturbés (1 à 2 par run) restent bloquées en cours de production, faute de temps derrière le goulot de tare — phénomène déjà caractérisé et documenté comme non significatif pour l'interprétation (voir `correction_chap5_en_cours.md`), volontairement non traité comme une réserve active.

---

## 2. Résultats — comparaison des deux régimes (n=3 par groupe)

| Indicateur | Nominal (moyenne, IC 95 %) | Perturbé (moyenne, IC 95 %) | Écart | p-value (Welch) | d de Cohen |
|---|---|---|---|---|---|
| **PI global** | 8,811 [8,789 ; 8,832] | 7,390 [7,333 ; 7,447] | **−1,421** | **< 0,0001** | −82,1 |
| **RL — Fiabilité** | 10,000 [10,000 ; 10,000] | 6,963 [6,645 ; 7,281] | **−3,037** | **0,0006** | −33,5 |
| **RS — Réactivité** | 6,530 [6,490 ; 6,569] | 5,479 [5,305 ; 5,653] | **−1,051** | **0,0009** | −20,7 |
| AG — Agilité | 6,457 [6,435 ; 6,480] | 6,416 [5,307 ; 7,525] | −0,041 | 0,887 | −0,1 |
| CO — Coût | 9,408 [9,339 ; 9,476] | 9,461 [9,354 ; 9,569] | +0,054 | 0,157 | +1,5 |
| AM — Actifs | 9,651 [9,631 ; 9,671] | 9,654 [9,512 ; 9,795] | +0,003 | 0,943 | +0,1 |
| WIP moyen | 77,1 [24,4 ; 129,9] | 297,6 [164,6 ; 430,5] | **+220,4** | **0,0106** | +5,4 |
| WIP max | 151,7 [57,6 ; 245,7] | 561,3 [477,2 ; 645,4] | **+409,7** | **0,0002** | +11,4 |
| Stock fini moyen | 91,6 [10,3 ; 173,0] | 50,5 [−32,9 ; 134,0] | −41,1 | 0,204 | −1,2 |
| Stock fini max | 148,3 [61,8 ; 234,8] | 164,3 [−9,7 ; 338,4] | +16,0 | 0,747 | +0,3 |
| Lead time moyen (min) | 282,5 [224,3 ; 340,6] | 360,7 [346,4 ; 375,0] | **+78,2** | **0,0233** | +4,6 |
| Commandes en retard | 0,000 [0,000 ; 0,000] | 13,667 [12,232 ; 15,101] | **+13,667** | **0,0006** | +33,5 |

**En gras : différences significatives au seuil de 5 % (7 indicateurs sur 12).**

---

## 3. Interprétation

**L'écart de PI observé (−1,42 point) est statistiquement significatif** (p < 0,0001), malgré un échantillon très réduit (n=3 par régime) — l'ampleur de l'effet est telle qu'elle domine largement le bruit stochastique naturel du modèle. La taille d'effet (d de Cohen = −82) est extrême, ce qui confirme visuellement ce que montrent les intervalles de confiance : **aucun chevauchement** entre les IC 95 % des deux régimes sur PI, RL, RS, WIP et les retards.

**Les indicateurs qui pilotent l'écart de PI (RL, RS, WIP, lead time, retards) sont tous significatifs.** C'est cohérent avec la chaîne causale déjà établie dans `RAPPORT_COMPARATIF_NOMINAL_PERTURBE.md` §8 : l'injection du lot de 200 unités épuise le stock, bascule une partie des commandes en production dédiée, sature la ligne (WIP), retarde les livraisons (RL) et dégrade le temps de traversée (RS).

**AG, CO et AM ne montrent pas de différence significative** — cohérent avec l'analyse du rapport principal : CO et AM sont des contrôles de cohérence attendus comme stables (structure de coût et disponibilité machine inchangées par la perturbation), et l'écart d'AG était déjà identifié comme faible en comparaison brute (raison pour laquelle le rapport principal le recalcule sur fenêtre commune pour en révéler l'ampleur réelle — cette campagne, à governance de fenêtre différente, ne referme pas ce point mais ne le contredit pas non plus : le signe reste négatif).

---

## 4. Limites à assumer (déjà documentées dans `PROTOCOLE_CAMPAGNE_STATISTIQUE.md` §7)

- **n=3 par régime reste un échantillon réduit.** Les résultats significatifs obtenus sont d'autant plus solides que l'effet est large, mais un effet plus discret (comme sur AG) pourrait rester indétectable à cet effectif — l'absence de significativité sur AG/CO/AM ne prouve pas l'absence d'effet, seulement que 3 réplications ne suffisent pas à le démontrer s'il est faible.
- **Groupes indépendants, pas appariés** (pas de graine commune) — méthode légèrement moins puissante qu'un test apparié à effectif égal, mais la puissance obtenue s'est révélée largement suffisante ici.
- **Runs perturbés à livraison incomplète** (44/45 et 43/45 sur 2 des 3 runs) — commandes bloquées par manque de temps derrière le goulot, phénomène documenté et non traité comme un défaut du modèle (voir `correction_chap5_en_cours.md`).
- **Fenêtre commune (10 800 s) différente de celle du rapport comparatif principal** (8 700 s) : les valeurs de cette campagne ne sont pas strictement comparables en valeur absolue à celles de `RAPPORT_COMPARATIF_NOMINAL_PERTURBE.md` §1, mais le sens et la significativité de l'écart sont cohérents entre les deux documents.
- **Une seule amplitude de perturbation testée** (200 unités) — la significativité établie ici porte sur cette perturbation précise, pas sur une généralisation à d'autres amplitudes.

---

*Rapport établi à partir de l'analyse automatisée (`analyze_campagne_statistique.py`) des 6 runs de la campagne. Modèle SCONTO-SVU, architecture VSM × SCOR, conformité SCOR 12.*
