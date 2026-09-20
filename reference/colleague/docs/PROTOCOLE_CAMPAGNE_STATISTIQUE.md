# Protocole — campagne de réplications statistiques (réponse à §1.2 de `Correction_chap5.docx`)

**Objectif** : passer d'une comparaison nominal/perturbé sur une seule exécution stochastique chacun à une comparaison sur **3 réplications par régime (6 runs)**, avec fenêtre d'observation commune et intervalles de confiance — le minimum praticable pour un test statistique formel (en dessous de 3 points, aucun écart-type/IC exploitable).

**Révision du 2026-09-12 (deux changements par rapport à la version initiale)** :
1. **Pas de graine à régler.** Deux runs nominaux produits avec les réglages par défaut (jamais touchés) montrent déjà des trajectoires nettement différentes (WIP à t=3000s : 123 vs 94 unités) — la variabilité naturelle de l'exécution en temps réel suffit à produire des runs indépendants. On ne cherche donc pas le champ « Seed value » dans AnyLogic ; **aucune manipulation de réglage n'est nécessaire**, il suffit de relancer le run normalement. Consequence méthodologique : les runs ne sont plus appariés par graine commune — l'analyse compare **deux groupes indépendants** (test t de Welch), pas des différences appariées.
2. **Fenêtre commune déterminée automatiquement, pas fixée à l'avance.** Chaque run doit aller jusqu'à la **livraison des 45 commandes clients** (pas d'arrêt anticipé arbitraire). Le script d'analyse détecte lui-même, pour chaque run, l'instant où les commandes sont livrées, et retient comme fenêtre commune le plus tardif de ces instants sur l'ensemble des runs de la campagne — ainsi tous les runs sont comparés à un instant où ils ont chacun terminé leur livraison.

**Aucune modification du modèle n'a été faite pour ce protocole.**

**Réserve à assumer explicitement dans le mémoire** : n=3 est un échantillon très réduit. Les intervalles de confiance seront larges et la puissance statistique faible — un effet réel mais modéré pourrait ne pas atteindre le seuil de significativité à 5 %. C'est un compromis délibéré entre rigueur et temps de calcul disponible, à énoncer clairement plutôt qu'à laisser deviner.

---

## 1. Plan de la campagne

| # | Régime | Run |
|---|---|---|
| 1 | nominal | **fait** (`..._1789144025559`, run de référence du rapport principal) |
| 2 | nominal | **fait** (`..._1789170875362`) |
| 3 | nominal | à produire |
| 1 | perturbé | **fait** (`..._1789164676620`, run de référence du rapport principal) |
| 2 | perturbé | à produire |
| 3 | perturbé | à produire |

**Il reste 3 runs à produire : 1 nominal + 2 perturbés.** Chaque run doit tourner jusqu'à ce que les 45 commandes clients soient livrées (comptable sur le dashboard, cartes « Order Mode — MTS/MTO (nb) », ou simplement en laissant tourner sans intervention jusqu'à ce que le bilan périodique `[BILAN]` affiche 45 commandes clients livrées). D'après les runs déjà produits, cela prend entre 8 400 s et 10 300 s de temps simulé — donc, à l'échelle temps réel 1:1, **entre 2h20 et 2h50 réel par run**. Pour les 3 runs restants, compter environ **7-8 heures de calcul cumulé**.

## 2. Lancer un run (rien à régler)

Ouvrir AnyLogic, lancer l'expérience `Simulation` normalement (bouton Run habituel) — **aucun réglage à modifier au préalable**. Ne pas chercher le champ « Seed value » : ce n'est plus nécessaire (voir révision du 2026-09-12 en tête de ce document).

## 3. Règle d'arrêt — livraison complète des 45 commandes clients

Laisser chaque run tourner jusqu'à ce que les **45 commandes clients** soient livrées (visible sur le dashboard, cartes « Order Mode — MTS/MTO (nb) » dont la somme doit atteindre 44-45 ; ou dans le log périodique `[BILAN]`, compteur « Livrees (client) »). D'après les runs déjà produits, cela survient entre t=8 400 s et t=10 300 s.

Ne pas couper le run trop tôt : si toutes les commandes ne sont pas encore livrées, le script d'analyse le signale explicitement (`!! JAMAIS ATTEINT 44/45`) et exclura ce run d'une comparaison fiable. Un léger dépassement après la livraison complète n'est en revanche pas grave (le script détermine lui-même l'instant exact de livraison dans chaque fichier, indépendamment de la durée totale du run).

## 4. Déclenchement de la perturbation (runs perturbés uniquement)

Cliquer sur le bouton « Pic ponctuel (200 unités) » assez tôt dans le run (t ≈ 500-1000 s, comme sur les runs de référence déjà produits) pour laisser le temps au système d'absorber le choc avant la fin naturelle du run. L'instant exact n'a pas besoin d'être précis à quelques secondes près — il n'est plus utilisé pour définir une fenêtre commune (celle-ci est désormais déterminée par la livraison complète, cf. §3), seulement noté pour archivage.

## 5. Ce qu'il faut archiver pour chaque run

Ajouter une ligne au fichier `SUIVI_CAMPAGNE_STATISTIQUE.csv` (créé à côté de ce protocole) immédiatement après chaque run :

- régime (nominal / perturbé)
- nom des fichiers `.xlsx` et `.ttl` générés (le suffixe `RUN_<t1>_<t2>` suffit)
- instant approximatif de déclenchement du pic ponctuel (runs perturbés — pour archivage, pas critique)
- toute anomalie observée pendant le run (crash, blocage, livraison incomplète, etc.)

**Ne pas recalculer les indicateurs à la main** — le script d'analyse (`analyze_campagne_statistique.py`, livré avec ce protocole) les extrait automatiquement de chaque `.xlsx` une fois les 6 runs disponibles.

## 6. Analyse une fois les 6 runs produits

Placer tous les fichiers `SCONTO_SVU_RESULTS_ZENER_SA_Togo_RUN_*.xlsx` de la campagne dans le dossier du projet (à côté des runs déjà existants — aucun besoin de les isoler), renseigner `SUIVI_CAMPAGNE_STATISTIQUE.csv` avec le nom de chaque fichier et son régime, puis exécuter :

```
python analyze_campagne_statistique.py
```

Le script :
- détecte automatiquement, pour chaque run, l'instant de livraison complète des commandes clients, et retient comme fenêtre commune le plus tardif de ces instants sur l'ensemble de la campagne ;
- calcule moyenne, écart-type et intervalle de confiance à 95 % pour **PI, RL, RS, AG, CO, AM, WIP moyen, WIP max, lead time moyen, nombre de commandes en retard, stock fini moyen/max** — par régime (groupes indépendants, pas de graine commune) ;
- compare les deux régimes par **test t de Welch** (groupes indépendants) et calcule une taille d'effet (d de Cohen) — la réponse directe à « l'écart de PI est-il statistiquement significatif ? ».

---

## 7. Limites à assumer dans le mémoire (même avec ce protocole)

- **n=3 par régime est un échantillon très réduit** (le minimum praticable pour un IC/test t, pas un échantillon confortable). Les intervalles de confiance seront larges, et un effet réel mais modéré pourrait ne pas atteindre la significativité à 5 % — ce n'est pas la preuve que l'effet n'existe pas, seulement que 3 réplications ne suffisent pas à le démontrer formellement. C'est un compromis assumé entre rigueur et temps de calcul disponible (~7-8 h cumulées restantes) — à indiquer explicitement dans le mémoire, avec la possibilité d'ajouter des runs supplémentaires plus tard si le jury l'exige (le script accepte n'importe quel nombre de runs ≥ 2 par régime).
- **Pas de graine commune entre nominal et perturbé** : contrairement au plan initial, les runs ne sont plus appariés (impossible sans manipuler un réglage qui s'est révélé introuvable/non nécessaire). L'analyse utilise donc un test de groupes indépendants (Welch), légèrement moins puissant à échantillon égal qu'un test apparié — encore une raison pour laquelle une différence réelle mais modeste pourrait ne pas ressortir comme significative à n=3.
- **Fenêtre d'observation déterminée par la livraison, variable d'un run à l'autre** (t=8 400 à 10 300 s sur les runs déjà produits) : plus longue que la fenêtre de 8 700 s du rapport comparatif principal dans certains cas — les valeurs de cette campagne ne sont donc pas nécessairement identiques à celles du rapport §1, mais **plus complètes** (livraison intégrale garantie), ce qui est le choix retenu avec l'utilisateur.
- **Une seule perturbation testée** (200 unités). La campagne valide la robustesse statistique de *cette* comparaison précise, pas la généralisation à d'autres amplitudes de perturbation — hors périmètre de §1.2.
