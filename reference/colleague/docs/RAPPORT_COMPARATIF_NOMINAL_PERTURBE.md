# Rapport de simulation comparatif — SCONTO-SVU
## Scénario nominal vs scénario perturbé (commande exceptionnelle de 200 unités)

**Modèle :** `SCONTO_SVU_GENERIC10-4.alp` — architecture VSM × SCOR, agents holoniques
**Scénario :** `scenario_ZENER_SA_Togo_v72.json` — demande réelle ZENER SA Togo
**Version de code :** identique pour les deux runs, **postérieure aux correctifs C15.9 à C15.32** (Make Cycle Time non saturé, export du stock matière par article, diagnostic de production fiabilisé)
**Référentiel de conformité :** SCOR 12
**Documents complémentaires :** `RAPPORT_CAMPAGNE_STATISTIQUE.md` (validation statistique de l'écart nominal/perturbé sur 3 réplications par régime), `PROTOCOLE_CAMPAGNE_STATISTIQUE.md` (méthode)

| | Run nominal | Run perturbé |
|---|---|---|
| Fichier source | `..._1789144025559.xlsx` | `..._1789164676620.xlsx` |
| Données brutes (CSV) | `_run_nominal.csv` | `_run_perturbe.csv` |
| Durée simulée | 10 140 s | 8 700 s |
| Points d'historique | 339 | 291 |
| Perturbation | aucune | 1 commande exceptionnelle de 200 unités |

> **Validité de la comparaison.** Les deux runs ont été produits avec exactement la même version du modèle et le même scénario. Les écarts observés sont donc imputables à la seule perturbation, et non à une évolution du code entre les deux exécutions. Les emplacements de graphiques sont balisés `[GRAPHIQUE #]` avec les colonnes à tracer.

---

## 1. Résultat d'ensemble

| Attribut | Poids | **Nominal** | **Perturbé** | Écart | Contribution à l'écart de PI |
|---|---|---|---|---|---|
| **RL** — Fiabilité | 0,40 | **10,000** | **7,111** | −2,889 | **−1,156** |
| **RS** — Réactivité | 0,20 | **6,518** | **5,400** | −1,118 | **−0,224** |
| **AG** — Agilité | 0,10 | **6,450** | **5,909** | −0,541 | **−0,054** |
| **CO** — Coût | 0,15 | **9,393** | **9,470** | +0,077 | +0,012 |
| **AM** — Actifs | 0,15 | **9,648** | **9,662** | +0,014 | +0,002 |
| **PI global** | — | **8,805** | **7,385** | **−1,420** | **−1,420** |

**L'effet mesuré de la perturbation est de 1,42 point de PI**, dont **81 % proviennent de la fiabilité (RL)** et 16 % de la réactivité (RS). Coût et gestion d'actifs sont quasi inchangés — cohérent : un lot exceptionnel ne modifie ni l'économie unitaire ni la disponibilité des équipements.

**Différence notable par rapport à l'analyse précédente** : cette fois, **les cinq attributs vont tous dans le sens attendu** dès la comparaison brute (aucune inversion de signe à corriger sur AG) — voir §5 pour le détail.

**Cet écart est statistiquement validé**, pas seulement observé sur ce run unique : une campagne de 3 réplications indépendantes par régime confirme sa significativité (p < 0,0001 sur le PI) — voir `RAPPORT_CAMPAGNE_STATISTIQUE.md` et §9 réserve 1.

`[GRAPHIQUE 1 — Courbes de PI superposées]`
**Type :** courbe double. **Axe X :** colonne « Temps simulation (s) » des deux CSV. **Séries :** PI du run nominal et PI du run perturbé. **Ligne de référence :** PI cible = 7,5. **Titre :** « Performance Index — nominal vs perturbé ».

`[GRAPHIQUE 2 — Profil des attributs]`
**Type :** barres groupées ou radar. **Catégories :** RL, RS, AG, CO, AM. **Séries :** nominal, perturbé (valeurs du tableau ci-dessus). **Titre :** « Profil de performance SCOR — l'impact se concentre sur la fiabilité ».

---

## 2. Méthode de calcul (rappel)

### 2.1 Formule du PI

```
PI = 0,40 × RL + 0,20 × RS + 0,10 × AG + 0,15 × CO + 0,15 × AM
```

**Vérification sur le run nominal :**
```
0,40 × 10,000 = 4,0000
0,20 ×  6,518 = 1,3036
0,10 ×  6,450 = 0,6450
0,15 ×  9,393 = 1,4090
0,15 ×  9,648 = 1,4472
                ───────
          PI  = 8,8048   →  valeur affichée : 8,805 ✓
```

**Vérification sur le run perturbé :**
```
0,40 ×  7,111 = 2,8444
0,20 ×  5,400 = 1,0800
0,10 ×  5,909 = 0,5909
0,15 ×  9,470 = 1,4205
0,15 ×  9,662 = 1,4493
                ───────
          PI  = 7,3851   →  valeur affichée : 7,385 ✓
```

L'égalité a été vérifiée sur la trace de calcul finale des deux runs (feuille « Traçabilité performance » des exports Excel), qui recoupe exactement l'historique périodique (feuille « Historique Dashboard »).

### 2.2 Chaîne d'agrégation

Méthode Theeranuphattana / Chan & Qi, en quatre étapes : mise à l'échelle 0-10 entre une borne « performance nulle » et une borne « parfaite » ; conversion en grades flous A→F de centres 10/8/6/4/2/0 ; agrégation pondérée par attribut ; défuzzification par centre de gravité `(10A+8B+6C+4D+2E)/(A+…+F)`.

### 2.3 Convention d'amorçage

Tant que les cinq attributs ne sont pas tous mesurables, le PI est maintenu à sa cible (7,5). **Ce n'est pas une mesure** — la colonne « Attributs pondérés dans le PI » de l'export permet d'identifier ces points et de les exclure de toute analyse.

---

## 3. RL — Fiabilité : le cœur de l'impact

| | Nominal | Perturbé |
|---|---|---|
| Score | **10,000** | **7,111** |
| Valeur brute (taux de ponctualité) | 1,000 | 0,711 |
| Commandes clients closes | 45 | 45 |
| Commandes en retard | **0** | **13** |
| Taux de service affiché | 100 % | 71,1 % |

### 3.1 Formule appliquée

`RL.2.2` — *Delivery Performance to Customer Commit Date* — est l'unique indicateur pondéré (poids local 1,0) :

```
              Commandes livrées dans le délai d'engagement
RL.2.2  =  ─────────────────────────────────────────────────────
           Commandes closes + commandes en retard constaté
```

Le dénominateur inclut les échecs terminaux (`REFUSEE`, `BLOQUE_*`) **et** les commandes dont le retard a été constaté alors qu'elles étaient encore en attente — une commande n'a pas besoin d'être livrée pour être comptée en retard.

**Délai d'engagement : 4 heures en MTS**, mesuré sur le **périmètre ZENER** (hors réception et vérification chez le client, qui échappent au contrôle de l'entreprise). Ce délai est **figé à la création** de la commande : une commande requalifiée en MTO faute de stock conserve l'engagement qu'elle avait aux yeux du client.

### 3.2 Interprétation

En nominal, les 45 commandes clients sont closes **32 en MTS pur stock + 0 basculement en production dédiée** (voir §8), et respectent toutes le délai. En perturbé, 24 commandes basculent en MTO faute de stock, et 13 dépassent le délai d'engagement — non parce que la ligne est plus lente en soi, mais parce qu'elles doivent attendre la libération de la capacité monopolisée par le lot de 200 unités.

`[GRAPHIQUE 3 — RL et retards]`
**Type :** courbe double axe. **Axe X :** temps. **Série 1 (axe gauche) :** SCOR RL des deux runs. **Série 2 (axe droit) :** « Delayed Orders (nb) » du run perturbé. **Titre :** « Fiabilité et accumulation des retards ».

---

## 4. RS — Réactivité

| | Nominal | Perturbé |
|---|---|---|
| **Score RS** | **6,518** | **5,400** |

### 4.1 Décomposition (cinq indicateurs à poids égal 0,20)

| Code | Indicateur | Nominal | Perturbé | Borne |
|---|---|---|---|---|
| `RS.2.1` | Source Cycle Time | 2 586 s → **10,000** | 2 276 s → **10,000** | nominal pondéré |
| `RS.2.2` | **Make Cycle Time** | 441 s → **0,713** | 2 043 s → **0,161** | 35 s (nominal pondéré) |
| `RS.2.3` | Deliver Cycle Time | 4 699 s → **10,000** | 5 930 s → **10,000** | nominal pondéré |
| `RS.1.1` | Order Fulfillment Cycle Time | 17 111 s → **3,489** | 26 691 s → **0,000** | 26 280 s |
| `RS.3.94` | Order Fulfillment Dwell Time | 4 233 s → **8,389** | 8 302 s → **6,841** | 26 280 s |

### 4.2 Correction apportée — `RS.2.2` (Make Cycle Time) ne sature plus

**C'est le point corrigé le plus visible de ce rapport.** Auparavant, `RS.2.2` affichait **0,000 dans les deux régimes** (459 s nominal contre 1 963 s perturbé, un facteur ×4 pourtant totalement invisible), parce que la fonction de normalisation coupait net à zéro dès que la valeur dépassait 10× le nominal pondéré — les deux régimes étaient au-delà de ce seuil.

La fonction a été remplacée, pour cette famille d'indicateurs (`RS.2.1/2.2/2.3/2.5`), par une décroissance hyperbolique sans plancher dur (`10 × min / valeur` au lieu d'une coupure nette). Résultat : **0,713 en nominal contre 0,161 en perturbé** — l'aggravation du goulot (facteur 12,6× le nominal pondéré, contre 58,4× en perturbé) est désormais mesurée, pas seulement signalée par un score à zéro.

Le poste responsable reste la **tare des bonbonnes** (`sM1.3.1`), de capacité simultanée 1 pour un temps de traitement de 4 à 6 s.

### 4.3 Méthode de mesure

Les temps de cycle par macro-processus mesurent le **temps de traversée réel** — traitement **et** attente en file — sur le **périmètre de l'entreprise focale uniquement**, rapporté au nombre d'unités entrées dans le macro-processus. Ils sont comparés à un **temps de cycle nominal pondéré par la fréquence de passage réelle** de chaque poste, calculé depuis les lois de temps du scénario.

`RS.1.1` et `RS.3.94` conservent leur définition SCOR **de bout en bout** — délai réellement perçu par le client, réception incluse — et sont normalisés sur une borne cohérente avec ce périmètre : engagement ZENER (4 h) plus réception client nominale (≈ 3,3 h), soit 26 280 s.

### 4.4 Interprétation

L'écart entre les deux runs vient principalement de deux sources désormais toutes deux visibles : `RS.2.2` (0,713 → 0,161, le goulot s'aggrave d'un facteur ~4,6) et `RS.1.1` (3,489 → 0,000, le délai bout en bout dépasse la borne de 26 280 s et sature au plancher). `RS.1.1` reste le composant le plus sensible ; contrairement à `RS.2.2`, il n'utilise pas la décroissance hyperbolique (réservée aux quatre codes de cycle macro-processus) et peut donc encore saturer à 0 — point à surveiller si le délai bout en bout continue de se dégrader sur de futurs runs plus longs.

`[GRAPHIQUE 4 — RS comparé]`
**Type :** courbe double. **Séries :** SCOR RS des deux runs. **Titre :** « Réactivité — dégradation sous perturbation ».

`[GRAPHIQUE 5 — Décomposition RS]`
**Type :** barres groupées. **Catégories :** Source, Make, Deliver, Lead Time global, Dwell Time. **Séries :** scores nominal et perturbé (tableau §4.1). **Titre :** « Où RS perd ses points ».

---

## 5. AG — Agilité

| Indicateur | Statut SCOR | Nominal | Perturbé |
|---|---|---|---|
| Débit de sortie (`AG.3.32`) | **seul vrai code SCOR** | 15,96 ent/h → 0,997 | 18,62 ent/h → 1,164 |
| Taux d'occupation | proxy hors référentiel | 0,237 → 8,419 | 0,484 → 6,770 |
| Stabilité du débit | proxy hors référentiel | 0,993 → 9,934 | 0,979 → 9,793 |
| **Score AG (valeur finale)** | | **6,450** | **5,909** |

**Contrairement à l'analyse précédente, la comparaison brute des valeurs finales va déjà dans le bon sens** (AG baisse de 6,450 à 5,909 sous perturbation, −0,541) — plus d'inversion de signe à corriger sur ce point. Le débit réel mesuré en fin de perturbé (18,62 ent/h) est même légèrement supérieur au nominal (15,96 ent/h) à cet instant précis : le carnet perturbé, plus court (8 700 s contre 10 140 s), se termine sur une phase de rattrapage à débit élevé — c'est pourquoi une lecture plus rigoureuse sur fenêtre commune reste nécessaire (§5.1).

### 5.1 Recalcul sur fenêtre d'observation commune

Les deux runs n'ont pas la même durée (10 140 s vs 8 700 s). Pour écarter tout effet de phase de trajectoire, AG est recalculé sur la portion commune aux deux runs, `[0, 8 700 s]` (291 points communs, échantillonnage identique de 30 s) :

| | Nominal (fenêtre commune) | Perturbé (durée totale) |
|---|---|---|
| AG moyen sur `[0, 8 700 s]` | **6,290** | **4,586** |
| Écart | — | **−1,704** |

**Le recalcul confirme et amplifie la dégradation** : sur une base de temps identique, l'écart est de −1,704 (contre −0,541 en comparaison brute) — la comparaison sur valeurs finales sous-estimait l'ampleur réelle de la dégradation de l'agilité, parce que le run nominal continue encore 1 440 s après la fin du run perturbé, période où son WIP et son occupation système fluctuent normalement. **Aucune inversion de signe n'est nécessaire cette fois** (contrairement au run précédent) : les deux méthodes de calcul s'accordent sur le sens de la dégradation, seule l'ampleur diffère.

Le tableau §1 conserve la convention « valeur finale du run », identique pour les cinq attributs et pour les deux runs — c'est la convention la plus simple à vérifier point par point, et celle qui a servi à établir le PI affiché de 7,385. Le recalcul ci-dessus est une **analyse de robustesse complémentaire**, pas une révision du PI global affiché.

`[GRAPHIQUE 5bis — AG sur fenêtre commune]`
**Type :** courbe double, tronquée à t ≤ 8 700 s pour les deux runs. **Titre :** « Agilité à durée d'observation identique ».

---

## 6. CO — Coût et AM — Actifs : stables

| | Nominal | Perturbé |
|---|---|---|
| `CO.1.1` ratio coût/CA | 6,1 % → **9,393** | 5,3 % → **9,470** |
| `AM.2.2` jours de stock | 0,347 j → **9,884** (composant) | 0,266 j → **9,911** (composant) |
| Disponibilité machine (proxy) | 94,1 % → 9,412 | 94,1 % → 9,412 |

Ces deux attributs sont **quasi identiques dans les deux régimes**, ce qui est le résultat attendu : la perturbation modifie l'ordonnancement et les délais, pas la structure de coût unitaire ni la fiabilité des équipements. Leur stabilité constitue un **contrôle de cohérence** du modèle — si l'un d'eux avait bougé fortement, cela aurait signalé un couplage indésirable.

---

## 7. Dynamique opérationnelle comparée

| Grandeur | Nominal (min / moy / max) | Perturbé (min / moy / max) |
|---|---|---|
| Encours WIP (unités) | 0 / 67,3 / 135 | 0 / **355,5** / **537** |
| Stock fini (unités) | 19 / 113,6 / 178 | 0 / 48,3 / 154 |
| Lead time moyen (min) | 0 / 309,4 / 404,2 | 0 / **365,5** / 445,2 |
| PCE (%) | 0 / 75,3 / 90,0 | 0 / 71,4 / 90,0 |
| Taux de rebut (%) | 0 / 4,42 / 6,5 | 0 / 4,64 / 5,8 |
| Taux de reprise (%) | 19,5 / 22,0 / 60,0 | 0 / 19,1 / 50,0 |

**Le WIP moyen quintuple** (67,3 → 355,5) et culmine à 537 unités contre 135. C'est la signature physique de l'engorgement : le lot de 200 unités bloque la ligne, les ordres s'accumulent derrière lui.

### 7.1 Stock matière — décomposition par article (correctif apporté)

**Point corrigé.** Le modèle exporte désormais le détail du stock matière par article (`detailStockMatiereParMatiere()`), au lieu d'une seule somme agrégeant directement des kilogrammes et des unités hétérogènes. Les trois matières suivies par le scénario ZENER, avec leur unité propre :

| Matière | Unité | Nominal (min / moy / max) | Perturbé (min / moy / max) |
|---|---|---|---|
| GPL vrac (`GPL_VRAC`) | **kilogrammes** | 116,2 / 306,9 / 830,0 | 150,0 / 506,0 / **2 475,0** |
| Bouteilles vides 12 kg (`BOUTEILLE_VIDE_12KG`) | **unités** | 55,6 / 72,4 / 126,4 | 59,4 / 87,2 / 222,0 |
| Kits d'accessoires (`ACCESSOIRES_KIT`) | **unités** | 77,0 / 90,9 / 126,4 | 78,7 / 99,1 / 198,0 |

**Interprétation** : la matière la plus sollicitée par la perturbation est très clairement le GPL vrac, dont le stock monte jusqu'à 2 475 kg (contre un maximum de 830 kg en nominal) — cohérent avec une réponse de réapprovisionnement proportionnellement plus forte sur l'intrant volumique du produit que sur les composants d'assemblage (bouteilles, kits), dont les stocks maximaux restent dans un rapport plus contenu (×1,8 et ×1,6 respectivement, contre ×3,0 pour le GPL).

**Ce correctif clôt la réserve précédente sur ce point** : le stock matière est désormais interprétable en valeur absolue, par article et dans son unité propre — plus seulement en tendance relative sur une somme composite sans signification physique. L'agrégat brut (ex. 2 895 unités en pointe perturbée, toutes matières confondues sans conversion) reste disponible dans l'export mais n'a plus besoin d'être utilisé pour l'analyse : la ligne ci-dessus le remplace.

`[GRAPHIQUE 6 — WIP comparé]`
**Type :** courbe double. **Séries :** « Work In Process (Products) » des deux runs. **Titre :** « Encours de production — l'engorgement causé par le lot exceptionnel ».

`[GRAPHIQUE 7 — Stock matière par article]`
**Type :** courbes multiples (une par matière), un graphique par run ou en panels côte à côte. **Titre :** « Consommation matière par article — nominal vs perturbé ».

---

## 8. Chaîne causale de la perturbation

Le mécanisme est entièrement traçable dans les données, étape par étape :

| Étape | Marqueur mesuré | Nominal | Perturbé |
|---|---|---|---|
| 1. Injection du lot exceptionnel | quantité commandée | — | 200 unités en une commande |
| 2. Épuisement du stock fini | mode de service des commandes | **45 MTS / 0 MTO** | **21 MTS / 24 MTO** |
| 3. Bascule en production dédiée | commandes closes | 45/45 sans délai | 45/45 closes, 13 en retard |
| 4. Saturation de la ligne | WIP moyen | 67,3 | **355,5** |
| 5. Dépassement des délais | commandes en retard | **0** | **13** |
| 6. Chute de la fiabilité | RL | 10,000 | **7,111** |
| 7. Aggravation du goulot Make | `RS.2.2` (score) | 0,713 | **0,161** |
| 8. Impact sur l'indice global | PI | 8,805 | **7,385** |

**Le marqueur le plus parlant est l'étape 2** : en nominal, la totalité des commandes est servie sur stock ; en perturbé, plus de la moitié (24/45) bascule en production dédiée. C'est l'épuisement du stock provoqué par le lot de 200 qui déclenche toute la cascade.

---

## 9. Réserves méthodologiques

1. **Réplication unique par scénario — RÉSOLU par une campagne statistique dédiée.** Le tableau §1 ci-dessus repose sur un seul run par régime (le point de méthode le plus simple à vérifier arithmétiquement point par point). Une campagne séparée de 3 réplications indépendantes par régime (6 runs, sans graine imposée — la variabilité naturelle de l'exécution en temps réel s'est révélée suffisante pour produire des runs indépendants) a établi, par test t de Welch, que **l'écart de PI est statistiquement significatif** (p < 0,0001, d de Cohen = −82), de même que RL, RS, WIP moyen/max, lead time et nombre de commandes tardives (7 indicateurs sur 12 significatifs à 5 %). Détail complet — protocole, données et résultats — dans `RAPPORT_CAMPAGNE_STATISTIQUE.md` et `PROTOCOLE_CAMPAGNE_STATISTIQUE.md`. **Nuance à conserver** : n=3 par régime reste un petit échantillon (une différence réelle mais discrète, comme celle observée sur AG, peut ne pas atteindre la significativité à cet effectif — non significatif n'équivaut pas à absent) ; la fenêtre d'observation de cette campagne (déterminée par la livraison complète des commandes, ~10 800 s) diffère de celle du tableau §1 (8 700 s), donc les valeurs ne sont pas strictement comparables terme à terme, seul le sens et la significativité de l'écart le sont.

2. **Durées de run différentes** (10 140 s vs 8 700 s, le run perturbé étant cette fois **plus court** car le carnet a été absorbé plus vite que sur de précédents runs). Les indicateurs sensibles à la durée d'observation — en particulier AG — en sont affectés ; **corrigé en §5.1** par un recalcul sur fenêtre d'observation commune `[0, 8 700 s]`, qui confirme et amplifie la dégradation de l'agilité (−1,704 au lieu de −0,541 en comparaison brute).

3. **Bornes de normalisation partiellement heuristiques.** Elles sont indexées sur des grandeurs métier du modèle (nominal pondéré des postes, engagement client) et non plus sur des constantes arbitraires, mais elles ne proviennent pas d'un benchmark sectoriel externe. Les valeurs absolues du PI sont donc à interpréter **en comparaison relative**, ce qui est précisément l'usage fait ici.

4. **Proxies hors référentiel SCOR.** Sur les trois composants de AG, un seul (`AG.3.32`) porte un vrai code SCOR ; idem pour AM (`AM.2.2`). Les autres sont des proxies explicitement déclarés — vérifiés contre le texte du référentiel et renommés en conséquence.

5. **Délai d'engagement non contractuel.** Le seuil de 4 h en MTS est calé sur la distribution observée des temps de traitement, pas sur un engagement commercial documenté de ZENER SA Togo. À recaler si cette donnée devient disponible.

---

## Annexe A — Trajectoires échantillonnées

### A.1 Run nominal (1 point sur 21)

| t (s) | RL | RS | AG | CO | AM | **PI** | WIP | Stock | Retards |
|---|---|---|---|---|---|---|---|---|---|
| 19,6 | 0,000 | 0,000 | 1,000 | 0,000 | 0,000 | **7,500** | 0 | 100 | 0 |
| 690 | 10,000 | 5,910 | 5,192 | 9,602 | 9,687 | **8,595** | 59 | 56 | 0 |
| 1 350 | 10,000 | 5,945 | 6,473 | 9,550 | 9,697 | **8,723** | 98 | 27 | 0 |
| 2 040 | 10,000 | 6,171 | 6,612 | 9,493 | 9,693 | **8,773** | 132 | 36 | 0 |
| 2 700 | 10,000 | 6,147 | 6,435 | 9,424 | 9,675 | **8,738** | 32 | 78 | 0 |
| 3 390 | 10,000 | 6,204 | 6,346 | 9,380 | 9,672 | **8,733** | 63 | 79 | 0 |
| 4 050 | 10,000 | 6,282 | 6,496 | 9,369 | 9,650 | **8,759** | 103 | 128 | 0 |
| 4 740 | 10,000 | 6,372 | 6,665 | 9,384 | 9,658 | **8,797** | 135 | 117 | 0 |
| 5 400 | 10,000 | 6,459 | 6,461 | 9,368 | 9,642 | **8,789** | 36 | 148 | 0 |
| 6 090 | 10,000 | 6,466 | 6,435 | 9,388 | 9,654 | **8,793** | 75 | 124 | 0 |
| 6 750 | 10,000 | 6,454 | 6,611 | 9,375 | 9,643 | **8,805** | 128 | 144 | 0 |
| 7 440 | 10,000 | 6,479 | 6,555 | 9,370 | 9,636 | **8,802** | 21 | 160 | 0 |
| 8 100 | 10,000 | 6,521 | 6,514 | 9,385 | 9,646 | **8,810** | 93 | 138 | 0 |
| 8 790 | 10,000 | 6,512 | 6,658 | 9,375 | 9,632 | **8,819** | 0 | 167 | 0 |
| 9 450 | 10,000 | 6,506 | 6,415 | 9,383 | 9,639 | **8,796** | 45 | 151 | 0 |
| 10 140 | 10,000 | 6,512 | 6,456 | 9,384 | 9,648 | **8,803** | 79 | 131 | 0 |

**PI : min 8,390 (hors amorçage) · max 8,974 · moyenne 8,760 · écart-type 0,086**

### A.2 Run perturbé (1 point sur 21)

| t (s) | RL | RS | AG | CO | AM | **PI** | WIP | Stock | Retards |
|---|---|---|---|---|---|---|---|---|---|
| 21,1 | 0,000 | 0,000 | 1,000 | 0,000 | 0,000 | **7,500** | 0 | 100 | 0 |
| 570 | 8,000 | 6,447 | 3,216 | 9,682 | 9,699 | **7,718** | 279 | 25 | 1 |
| 1 170 | 8,750 | 6,437 | 5,038 | 9,610 | 9,700 | **8,188** | 383 | 18 | 1 |
| 1 740 | 9,091 | 6,194 | 4,609 | 9,558 | 9,700 | **8,225** | 369 | 18 | 1 |
| 2 310 | 8,667 | 6,209 | 4,894 | 9,512 | 9,698 | **8,079** | 319 | 22 | 2 |
| 2 910 | 7,143 | 5,987 | 4,760 | 9,622 | 9,699 | **7,429** | 436 | 19 | 6 |
| 3 480 | 7,200 | 6,030 | 4,524 | 9,591 | 9,697 | **7,432** | 389 | 26 | 7 |
| 4 050 | 7,333 | 6,005 | 4,271 | 9,581 | 9,699 | **7,454** | 460 | 19 | 8 |
| 4 650 | 7,273 | 5,845 | 4,104 | 9,575 | 9,704 | **7,380** | 482 | 6 | 9 |
| 5 220 | 6,757 | 5,697 | 4,100 | 9,557 | 9,702 | **7,141** | 506 | 12 | 12 |
| 5 790 | 6,829 | 5,692 | 4,146 | 9,548 | 9,703 | **7,172** | 440 | 9 | 13 |
| 6 390 | 6,829 | 5,585 | 4,647 | 9,529 | 9,695 | **7,197** | 348 | 32 | 13 |
| 6 960 | 6,829 | 5,571 | 5,103 | 9,498 | 9,663 | **7,230** | 260 | 114 | 13 |
| 7 530 | 6,905 | 5,533 | 4,946 | 9,481 | 9,652 | **7,233** | 307 | 142 | 13 |
| 8 130 | 7,045 | 5,408 | 5,393 | 9,475 | 9,658 | **7,309** | 215 | 127 | 13 |
| 8 700 | 7,111 | 5,400 | 5,903 | 9,471 | 9,662 | **7,385** | 128 | 119 | 13 |

**PI : min 7,049 · max 8,929 · moyenne 7,526 · écart-type 0,425**

**Lecture de la trajectoire perturbée :** le PI chute dès les premières centaines de secondes, atteint son minimum vers t = 5 220 s (**7,141**) quand le WIP culmine à 506-536 unités et que les retards s'accumulent (12-13 commandes), puis remonte progressivement à mesure que le carnet se vide — sans jamais revenir au niveau nominal, puisque les retards déjà constatés sont définitifs.

À comparer avec la trajectoire nominale, qui reste dans une bande étroite de 8,39 à 8,97 sur tout le run (écart-type de 0,086 contre 0,425) — une variabilité intra-run près de 5 fois plus faible en régime nominal, autre signature de l'engorgement provoqué par la perturbation.

---

## Annexe B — Fichiers de données

| Fichier | Contenu |
|---|---|
| `_run_nominal.csv` | 339 points × 28 colonnes — run nominal |
| `_run_perturbe.csv` | 291 points × 28 colonnes — run perturbé |

Format français : séparateur point-virgule, virgule décimale, encodage UTF-8 avec BOM — ouverture directe dans Excel sans manipulation.

**Colonnes utiles pour les graphiques :** A « Temps simulation (s) » · D « Work In Process » · E « Finished Stock » · J « Delayed Orders » · R « Raw Material Stock — détail par matière » (format `idMatiere=valeur|idMatiere=valeur`) · T à X (scores SCOR RL/RS/AG/CO/AM) · Y « PI » · Z « PI cible » · AA « Attributs pondérés dans le PI » (permet d'identifier et d'exclure la phase d'amorçage).

---

*Rapport établi à partir de l'analyse directe des classeurs de résultats et des exports ontologiques des deux runs. Modèle SCONTO-SVU, architecture VSM × SCOR, conformité SCOR 12.*
