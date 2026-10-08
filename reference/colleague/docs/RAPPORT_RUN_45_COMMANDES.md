# Rapport de simulation — Scénario nominal ZENER SA Togo
## Run de référence à 45 commandes clients

**Fichier source :** `SCONTO_SVU_RESULTS_ZENER_SA_Togo_RUN_1773129600000_1788801137005.xlsx`
**Modèle :** `SCONTO_SVU_GENERIC10-4.alp` — architecture VSM × SCOR, agents holoniques
**Scénario :** `scenario_ZENER_SA_Togo_v72.json` — demande réelle ZENER, non modifiée
**Durée simulée :** 12 930 secondes (3 h 35 min de temps métier)
**Points d'historique capturés :** 431 (échantillonnage toutes les 30 s)
**Nombre de commandes clients :** 45 (100 % livrées, 0 refusée, 0 en retard)

> Ce document sert de base à la rédaction d'un rapport Word illustré. Les emplacements de graphiques sont signalés par `[GRAPHIQUE #]` avec le détail des séries et de l'axe à tracer. Les données complètes (431 points, 27 colonnes) sont disponibles dans le fichier `_run45_export.csv` généré à partir de la feuille « Historique Dashboard » du classeur source, pour tracer les courbes directement.

---

## 1. Résultat global

| Indicateur | Valeur |
|---|---|
| **PI final** | **9,043 / 10** |
| PI cible du scénario | 7,500 / 10 |
| PI moyen sur tout le run | 9,000 |
| PI moyen en régime permanent (1500 s – 10 500 s) | 9,000 (écart-type 0,010) |
| PI minimal (hors amorçage) | 8,734 (t = 480 s, phase transitoire) |
| PI maximal | 9,472 |

**Vérification arithmétique :** l'égalité `PI = 0,40×RL + 0,20×RS + 0,10×AG + 0,15×CO + 0,15×AM` a été vérifiée point par point sur l'intégralité du run. Elle est exacte à moins de 0,02 près sur 430 des 431 points ; le seul écart concerne le tout premier point (t = 30,9 s), qui correspond à l'état d'initialisation avant le premier calcul réel — la colonne « Attributs pondérés dans le PI » y indique explicitement qu'aucun attribut n'est encore mesuré.

`[GRAPHIQUE 1 — Courbe maîtresse]`
**Type :** courbe simple. **Axe X :** Temps simulation (s), colonne A du CSV. **Série :** PI (indice de performance courant), colonne X. **Ligne horizontale de référence :** PI cible = 7,5, colonne Y. **Titre suggéré :** « Évolution du Performance Index — scénario nominal, 45 commandes ».

---

## 2. Méthode de calcul du PI

### 2.1 Formule d'ensemble

Le Performance Index agrège cinq attributs SCOR par une moyenne pondérée, les poids étant des paramètres du scénario (issus d'un jugement d'expert saisi dans `scenario_ZENER_SA_Togo_v72.json`) :

```
PI = 0,40 × RL  +  0,20 × RS  +  0,10 × AG  +  0,15 × CO  +  0,15 × AM
```

| Attribut | Intitulé SCOR | Poids | Nature |
|---|---|---|---|
| RL | Reliability (Fiabilité) | 0,40 | Orienté client |
| RS | Responsiveness (Réactivité) | 0,20 | Orienté client |
| AG | Agility (Agilité) | 0,10 | Orienté client |
| CO | Cost (Coût) | 0,15 | Interne |
| AM | Asset Management (Gestion des actifs) | 0,15 | Interne |

### 2.2 Chaîne d'agrégation (méthode Theeranuphattana / Chan & Qi)

1. **Mise à l'échelle** — chaque indicateur brut est ramené sur une échelle 0-10 par interpolation linéaire entre une borne « performance nulle » et une borne « performance parfaite », selon que l'indicateur se maximise (type BENEFIT) ou se minimise (type COST).
2. **Conversion en grades flous** — le score 0-10 devient une appartenance répartie sur six grades A à F, de centres 10/8/6/4/2/0, avec interpolation linéaire entre deux centres.
3. **Agrégation par attribut** — les grades des indicateurs d'un même attribut sont combinés selon leur poids local (ex. RS : 5 indicateurs à 0,20 chacun).
4. **Défuzzification finale** — les cinq attributs sont combinés par leurs poids, puis ramenés à une valeur scalaire par centre de gravité : `(10A + 8B + 6C + 4D + 2E) / (A+B+C+D+E+F)`.

Cette mécanique est validée par un auto-test intégré au modèle, qui rejoue l'exemple numérique publié dans la littérature de référence (POF=6,700 → grades B=0,350/C=0,650 → PI=4,050) et confirme la conformité de l'implémentation.

### 2.3 Phase d'amorçage (warm-up)

Tant que les cinq attributs ne sont pas tous mesurables — RL exige au moins une commande client close — le PI est **maintenu à sa valeur cible (7,5)** plutôt que calculé sur un périmètre partiel. C'est une convention d'initialisation destinée à éviter qu'un changement de périmètre de mesure (un attribut qui devient soudainement mesurable) ne se lise à tort comme une variation de performance. Sur ce run, la phase d'amorçage dure de t = 0 à t ≈ 90 s.

---

## 3. RL — Reliability (Fiabilité)

**Score final : 10,00 / 10 — poids 0,40 — contribution au PI : 4,000 points**

### 3.1 Définition et formule

`RL.2.2` — *Delivery Performance to Customer Commit Date* — est l'unique indicateur pondéré de cet attribut (poids local 1,0). Il mesure la proportion de commandes livrées dans le délai d'engagement convenu avec le client :

```
RL.2.2 = Nombre de commandes livrées dans le délai d'engagement
         ────────────────────────────────────────────────────────
         Nombre total de commandes closes (livrées + en retard + refusées + bloquées)
```

Une commande est comptée « à temps » si sa **durée métier réelle accumulée** (somme des temps de traitement réels des postes traversés, indépendante de la vitesse d'animation de la simulation) ne dépasse pas le **délai d'engagement client** : 24 heures en mode MTS (mode de ce scénario), 72 h en MTO, 168 h en ETO.

Le dénominateur inclut les échecs de service définitifs (`REFUSEE`, `BLOQUE_MATIERE`, `BLOQUE_NOMENCLATURE`, `BLOQUE_CONFIG`) : une commande jamais servie compte contre la fiabilité, conformément à la définition SCOR.

### 3.2 Indicateurs affichés à titre informatif (poids 0)

| Code | Intitulé | Valeur | Statut |
|---|---|---|---|
| `RL.2.1` | Commandes livrées complètes | 1,00 (10,0/10) | Non mesurable : le modèle ne simule pas de livraison partielle, cet indicateur vaudrait 1,0 par construction |
| `RL.3.33` | Exactitude des articles livrés | 1,00 (10,0/10) | Proxy — aucune donnée d'erreur d'article n'est simulée |
| `RL.3.35` | Exactitude des quantités livrées | 1,00 (10,0/10) | Proxy — aucune donnée de sous-livraison n'est simulée |

### 3.3 Résultat observé sur ce run

**44 commandes closes sur les 45 créées, 0 en retard, 0 refusée, 0 bloquée** (la 45ᵉ commande, CMD_45, a été livrée à t = 10 990 s, dernier événement client du run). Les délais de traitement observés dans les traces (20 à 45 secondes de temps de simulation par commande MTS servie depuis le stock, converti en durée métier réelle via l'accumulateur dédié) restent très largement inférieurs au délai d'engagement de 24 heures.

**RL reste plat à 10,00/10 sur l'intégralité des 431 points**, sans aucune exception — y compris pendant les phases où le stock fini descend jusqu'à 14 unités (voir §7). Le seul épisode de tension (t ≈ 10 765 s, CMD_44 avec stock insuffisant) s'est résolu par une bascule automatique du mode de service (MTS → MTO, production dédiée), sans dépasser le délai d'engagement.

`[GRAPHIQUE 2 — RL dans le temps]`
**Type :** courbe simple ou aire. **Axe X :** Temps simulation (s). **Série :** SCOR RL (Reliability), colonne S du CSV. **Échelle Y fixe 0–10** pour visualiser l'absence totale de variation après l'amorçage. **Titre suggéré :** « RL — fiabilité de livraison, stable à 10/10 ».

---

## 4. RS — Responsiveness (Réactivité)

**Score final : 7,475 / 10 — poids 0,20 — contribution au PI : 1,495 point**
**Moyenne sur le run : 7,489 — écart-type : 0,439 — régime permanent : 7,467 ± 0,015**

### 4.1 Composition — cinq indicateurs à poids égal (0,20 chacun)

Chaque temps de cycle macro-processus est mesuré comme le **temps de traversée réel** (temps de traitement **et** temps d'attente en file, sur le périmètre de l'entreprise focale ZENER uniquement — les postes des catégories CLIENT et FOURNISSEUR sont exclus du calcul), rapporté au nombre d'unités entrées dans le macro-processus. Il est comparé à un **temps de cycle nominal**, calculé de la même façon à partir des lois de temps déclarées dans le scénario pour ces mêmes postes, pondérées par leur fréquence de passage réelle.

L'échelle de notation retenue : **tenir son temps nominal vaut 10/10 ; atteindre 10 fois son temps nominal (soit un taux de valeur ajoutée de 10 %, seuil reconnu en gestion lean) vaut 0/10.**

| Code | Intitulé | Valeur observée | Nominal pondéré | Ratio observé/nominal | Score |
|---|---|---|---|---|---|
| `RS.2.1` | Source Cycle Time | 2615,9 s | 2614,5 s | 1,00× | **9,999** |
| **`RS.2.2`** | **Make Cycle Time** | **429,5 s** | **32,9 s** | **13,05×** | **0,000** |
| `RS.2.3` | Deliver Cycle Time | 4699,3 s | 7039,5 s | 0,67× | **10,000** |
| `RS.1.1` | Order Fulfillment Cycle Time (lead time global client) | 18 253,3 s (5,07 h) | borne 86 400 s (24 h, délai d'engagement) | 21,1 % du délai promis | **7,887** |
| `RS.3.94` | Order Fulfillment Dwell Time (temps d'attente) | 4426,1 s | dérivé du PCE réel mesuré | — | **9,488** |

### 4.2 Diagnostic — le goulot de production

**`RS.2.2 Make` est l'unique point de défaillance de cet attribut, et il est structurel.** Le poste responsable est la tare des bonbonnes (référence modèle `sM1.3.1`), dont la capacité simultanée est de 1 unité à la fois pour un temps de traitement de 4 à 6 secondes. Ce poste accumule des files d'attente pouvant dépasser 300 secondes par unité, faisant grimper le temps de traversée réel de Make à 429,5 s pour un nominal théorique de 32,9 s — un facteur 13.

Ce résultat est **cohérent avec les deux runs précédents** de cette campagne : facteur 14,3× sur 37 commandes, 13,0× sur ce run à 45 commandes. La reproductibilité du phénomène d'un run à l'autre, malgré l'aléa de simulation, confirme qu'il s'agit d'une propriété structurelle du système et non d'un artefact statistique isolé.

**Source et Deliver sont sains** : Source colle exactement à son nominal (ratio 1,00), Deliver tourne même 33 % plus vite que son nominal pondéré. `RS.1.1` (5,07 h réelles sur 24 h d'engagement) confirme, à l'échelle du lead time client complet, la même lecture que RL : la chaîne tient largement son engagement malgré le goulot interne.

`[GRAPHIQUE 3 — RS et ses composants]`
**Type :** courbe multi-séries. **Axe X :** Temps simulation (s). **Séries :** SCOR RS (Responsiveness), colonne T. Si le détail par macro-processus est souhaité, ces valeurs ne sont disponibles qu'au point final dans la feuille « Pipeline SCOR vers PI » du classeur Excel (pas d'historique temporel par sous-indicateur) — utiliser alors un diagramme à barres statique avec les 5 valeurs du tableau ci-dessus. **Titre suggéré :** « RS — décomposition en 5 temps de cycle, goulot Make visible ».

`[GRAPHIQUE 4 — Barres, décomposition RS au point final]`
**Type :** diagramme à barres horizontales. **Catégories :** Source, Make, Deliver, Lead Time global, Dwell Time. **Valeurs :** scores 0-10 du tableau §4.1. **Couleur :** faire ressortir la barre Make (0,00) en rouge/alerte, les autres en couleur neutre. **Titre suggéré :** « Where does RS lose points? — Make au plancher, seul indicateur défaillant ».

---

## 5. AG — Agility (Agilité)

**Score final : 6,796 / 10 — poids 0,10 — contribution au PI : 0,680 point**
**Moyenne sur le run : 6,402 — écart-type : 0,669**

### 5.1 Composition — trois indicateurs à poids égal (1/3 chacun)

| Indicateur | Code / statut SCOR | Valeur | Score |
|---|---|---|---|
| Débit de sortie (Current Delivery Volume) | `AG.3.32` — seul vrai code SCOR de cet attribut | 12,25 ent/h (borne 0–160) | **0,766** |
| Taux d'occupation du système | `PROXY.AG.SYSTEM_UTILIZATION` — proxy, hors référentiel SCOR | 3,5 % (borne 0–150 %) | 9,765 |
| Stabilité du débit observé | `PROXY.AG.STABILITE_DEBIT` — proxy, hors référentiel SCOR (vérifié contre le texte SCOR : ne correspond ni à `AG.1.1` Upside Flexibility ni à `AG.1.2` Upside Adaptability) | 0,986 (1 − coefficient de variation) | 9,863 |

### 5.2 Diagnostic

**Le débit de sortie est directement plombé par le même goulot que `RS.2.2`** : Make limite mécaniquement le rythme auquel des unités finies sortent de la ligne, quel que soit le reste du système. C'est la trace, au niveau agilité, du même phénomène physique déjà identifié en RS — les deux indicateurs pointent vers la même cause racine par deux chemins de mesure indépendants, ce qui renforce la fiabilité du diagnostic.

Les deux proxies restent élevés parce que le système, bien qu'engorgé localement sur un poste, ne sature jamais sa capacité globale déclarée et ne devient pas erratique : il produit peu, mais de façon régulière.

**Tendance de fin de run** : AG progresse de 6,26 (creux vers t ≈ 3000 s) à 6,81 en toute fin de run — cet effet est un artefact de la fin de la demande : une fois la dernière commande livrée (t = 10 990 s), le système entre en régime d'attente et le calcul du débit se stabilise sur une fenêtre sans nouvelle perturbation.

`[GRAPHIQUE 5 — AG dans le temps]`
**Type :** courbe simple. **Axe X :** Temps simulation (s). **Série :** SCOR AG (Agility), colonne U. **Annotation suggérée :** marquer le point t ≈ 10 990 s (fin des commandes) où la courbe change de régime. **Titre suggéré :** « AG — agilité limitée par le débit de sortie ».

---

## 6. CO — Cost (Coût)

**Score final : 9,425 / 10 — poids 0,15 — contribution au PI : 1,414 point**
**Moyenne sur le run : 9,387 — écart-type : 0,459**

### 6.1 Composition

| Code | Intitulé | Valeur | Poids |
|---|---|---|---|
| `CO.1.1` | Coût total / Chiffre d'affaires estimé (TSCMC ratio) | **5,8 %** | 1,0 (seul indicateur noté) |
| `CO.3.13` | Coût main-d'œuvre cumulé | 179 777,80 FCFA | 0 (informatif) |
| `CO.3.11` | Coût matière cumulé | 302 360,00 FCFA | 0 (informatif) |

```
CO.1.1 = Coût total (main-d'œuvre + matière)
         ─────────────────────────────────────  = 5,8 %
         Chiffre d'affaires (CA unitaire × unités livrées aux clients)
```

### 6.2 Diagnostic

Économie saine : la chaîne dépense 5,8 % de son chiffre d'affaires en coûts opérationnels directs, sur un total de **2330 unités livrées à 45 commandes clients**. Résultat cohérent avec le run précédent (6,1 % à 37 commandes) — la légère amélioration s'explique par l'effet d'échelle (les coûts fixes/semi-fixes se répartissent sur un volume plus grand).

`[GRAPHIQUE 6 — CO dans le temps]`
**Type :** courbe simple. **Axe X :** Temps simulation (s). **Série :** SCOR CO (Cost), colonne V. **Titre suggéré :** « CO — ratio coût/chiffre d'affaires, économie stable ».

---

## 7. AM — Asset Management (Gestion des actifs)

**Score final : 9,697 / 10 — poids 0,15 — contribution au PI : 1,455 point**
**Moyenne sur le run : 9,642 — écart-type : 0,465**

### 7.1 Composition

| Code | Intitulé | Valeur | Score | Poids |
|---|---|---|---|---|
| `PROXY.AM.DISPONIBILITE_MACHINE` | Disponibilité machine (MTBF/(MTBF+MTTR)) — proxy, hors référentiel SCOR (vérifié : `AM.3.9` officiel désigne un indicateur de recyclabilité d'emballage, sans rapport) | 94,1 % | 9,412 | 0,5 |
| `AM.2.2` | Inventory Days of Supply — seul vrai code SCOR de cet attribut | 0,054 jour | 9,982 | 0,5 |
| `AM.3.18` | Valeur des actifs fixes déclarés | 192 800 000 FCFA | — | 0 (informatif) |

### 7.2 Diagnostic

Couverture de stock extrêmement courte (moins de 1,5 heure de consommation en stock), cohérente avec un système MTS à rotation rapide où la production est déclenchée par une politique de point de commande réactive. La disponibilité machine élevée reflète un modèle de fiabilité d'équipement stable sur la durée du run.

`[GRAPHIQUE 7 — AM dans le temps]`
**Type :** courbe simple. **Axe X :** Temps simulation (s). **Série :** SCOR AM (Asset Management), colonne W. **Titre suggéré :** « AM — disponibilité et rotation de stock ».

---

## 8. Dynamique opérationnelle sous-jacente

Ces indicateurs ne pèsent pas directement dans le PI mais expliquent ses variations.

| Indicateur | Min | Max | Moyenne (tout le run) | Moyenne (régime permanent 1500–10500 s) |
|---|---|---|---|---|
| Débit de sortie (ent/h) | 0,0 | 60,0 | 14,7 | — |
| Encours de production — WIP (unités) | 0,0 | 125,0 | 43,1 | 53,6 |
| Stock fini (unités) | 14,0 | 167,0 | 87,1 | 106,3 |
| PCE — Process Cycle Efficiency (%) | 0,0 | 86,3 | 75,8 | — |
| Temps d'attente moyen mesuré (s) | 1539,7 | 4818,8 | 4363,4 | — |
| Stock matière première (unités) | 274,5 | 716,2 | 486,4 | — |

**Le WIP oscille fortement (0 à 125 unités) tout au long du régime permanent** — c'est la signature d'un système qui fonctionne par à-coups : la production se déclenche par lots (politique de point de commande, non continue), et le goulot de la tare crée une accumulation temporaire à chaque lancement, résorbée progressivement jusqu'au lot suivant.

**Le stock fini ne s'approche jamais de la rupture avant la fin naturelle de la demande** (minimum observé : 14 unités, uniquement lors du transitoire de démarrage à t ≈ 480 s). C'est ce tampon qui explique pourquoi RL reste à 10/10 malgré un goulot de production sévère et permanent : le client ne perçoit jamais la congestion interne.

`[GRAPHIQUE 8 — Dynamique interne]`
**Type :** courbe multi-séries, deux axes Y. **Axe X :** Temps simulation (s). **Série 1 (axe Y gauche) :** Work In Process (Products), colonne D. **Série 2 (axe Y gauche) :** Finished Stock (Products), colonne E. **Série 3 (axe Y droit, optionnel) :** PI (indice de performance courant), colonne X, pour superposer la dynamique interne et son effet sur le PI. **Titre suggéré :** « Encours et stock fini — le tampon qui protège RL ».

---

## 9. Phases du run — lecture chronologique

| Phase | Intervalle | PI | Description |
|---|---|---|---|
| **Amorçage** | 0 – 90 s | 7,500 (convention) | Aucun attribut mesurable ; PI maintenu à la cible par construction, pas une mesure |
| **Transitoire de démarrage** | 90 – 1500 s | 8,73 → 9,01 | Montée en régime ; RS et AG progressent à mesure que le système atteint son point de fonctionnement ; stock fini au plus bas (creux à 14 unités vers t ≈ 480 s) |
| **Régime permanent** | 1500 – 10 500 s | 8,98 – 9,04 (écart-type 0,010) | Oscillation étroite et stable ; WIP et stock fini oscillent fortement en phase avec le rythme des lots de production, sans dérive de tendance |
| **Fin de demande** | 10 500 – 10 990 s | → 9,043 | Livraison des dernières commandes clients (CMD_43, 44, 45) ; dernier événement métier à t = 10 990 s |
| **Régime d'attente** | 10 990 – 12 930 s | 9,043 (plat) | Plus aucune commande client ; stock fini stabilisé à 16 unités, WIP à 0, stock matière figé à 576,1 unités ; le modèle continue de tourner (recalculs périodiques visibles dans les logs) mais sans nouvel événement métier — fin naturelle de l'horizon de simulation, pas une dérive du système |

---

## 10. Comparaison avec le run de référence précédent (37 commandes)

| | Run à 37 commandes | Run à 45 commandes (ce rapport) | Écart |
|---|---|---|---|
| PI final | 9,016 | 9,043 | +0,027 |
| RL | 10,00 | 10,00 | = |
| RS | 7,493 | 7,475 | −0,018 |
| AG | 6,623 | 6,796 | +0,173 |
| CO | 9,386 | 9,425 | +0,039 |
| AM | 9,648 | 9,697 | +0,049 |
| Make — ratio observé/nominal | 14,3× | 13,05× | amélioration légère |
| CO.1.1 — ratio coût/CA | 6,1 % | 5,8 % | amélioration légère |

**La convergence entre ces deux runs indépendants constitue un argument de robustesse.** Le goulot de production, l'absence de rupture de stock côté client, le niveau général du PI (9,0-9,05) et le classement relatif des cinq attributs (RL >> AM ≈ CO >> RS > AG) sont reproduits à l'identique sur deux exécutions distinctes de la simulation. Ce n'est pas un hasard de tirage aléatoire isolé : c'est le comportement structurel du système sous la demande nominale de ce scénario.

`[GRAPHIQUE 9 — Comparaison des deux runs]`
**Type :** diagramme à barres groupées. **Catégories :** RL, RS, AG, CO, AM, PI. **Séries :** run 37 commandes, run 45 commandes (valeurs du tableau ci-dessus). **Titre suggéré :** « Reproductibilité du profil de performance entre deux runs indépendants ».

---

## 11. Réserves méthodologiques à formuler explicitement

Ces points doivent être mentionnés dans toute présentation ou publication de ces résultats.

1. **Réplication unique par scénario.** Ce rapport décrit un seul run stochastique. Sans réplications multiples et intervalle de confiance, un écart entre deux scénarios ne peut pas être distingué du bruit aléatoire de la simulation (pannes, variabilité des lois de temps). La convergence observée en §10 est encourageante mais ne remplace pas une analyse de réplications formelle.
2. **Bornes de normalisation partiellement heuristiques.** Les bornes de `RS.2.x` (nominal pondéré du scénario) et de `RS.1.1`/`RS.3.94` (délai d'engagement client) sont désormais indexées sur des grandeurs métier du modèle, mais restent des heuristiques internes plutôt qu'un benchmark sectoriel externe validé. Les valeurs absolues du PI (« 9,04/10 ») ne sont donc rigoureusement interprétables qu'en **comparaison relative** entre scénarios partageant les mêmes bornes.
3. **Proxies hors référentiel SCOR, déclarés explicitement.** Sur les trois métriques de AG, une seule (`AG.3.32`) porte un vrai code SCOR. Sur les trois métriques notées de AM, une seule (`AM.2.2`) porte un vrai code SCOR. Les autres sont des proxies informatifs, vérifiés contre le texte du référentiel et renommés en conséquence pour ne pas revendiquer une conformité qu'ils n'ont pas.
4. **Délai d'engagement client non calibré sur donnée contractuelle.** Le délai de 24 heures (mode MTS) utilisé pour juger RL et normaliser `RS.1.1`/`RS.3.94` est un ordre de grandeur de distribution posé par défaut, à recaler avec l'engagement commercial réel de ZENER SA Togo si disponible.
5. **Périmètre de mesure : entreprise focale ZENER seule.** Les temps de cycle RS et les coûts CO n'incluent que les postes de catégorie `ENTREPRISE_FOCALE` du scénario — les activités des fournisseurs et du client final (réception, contrôle) sont exclues du calcul de performance de ZENER, conformément à la pratique VSM standard (périmètre = entreprise focale).
6. **Dilution volontaire des poids de niveau 1.** Un indicateur de niveau 2 entièrement défaillant (`RS.2.2` à 0/10) ne peut réduire le PI que d'au maximum `poids attribut × 1/n indicateurs` — ici 0,20 × 1/5 = 0,04, soit 0,4 point sur 10. C'est un choix méthodologique assumé : le PI est un indice stratégique agrégé, le diagnostic fin se lit au niveau des indicateurs de niveau 2/3, pas au niveau du score global.

---

## Annexe A — Échantillon de la série temporelle complète (1 point / 15, soit ~450 s)

| t (s) | RL | RS | AG | CO | AM | **PI** | WIP | Stock fini | Débit (ent/h) |
|---|---|---|---|---|---|---|---|---|---|
| 30,9 | 0,00 | 0,00 | 1,00 | 0,00 | 0,00 | **7,500** | 0 | 100 | 0,0 |
| 480 | 10,00 | 7,798 | 3,029 | 9,468 | 9,676 | **8,734** | 87 | 66 | 15,0 |
| 930 | 10,00 | 7,487 | 6,138 | 9,347 | 9,658 | **8,962** | 18 | 107 | 15,5 |
| 1380 | 10,00 | 7,531 | 6,407 | 9,426 | 9,664 | **9,010** | 125 | 60 | 13,0 |
| 1830 | 10,00 | 7,505 | 6,289 | 9,412 | 9,660 | **8,991** | 58 | 91 | 13,8 |
| 2280 | 10,00 | 7,476 | 6,514 | 9,403 | 9,678 | **9,009** | 121 | 58 | 14,2 |
| 2730 | 10,00 | 7,436 | 6,350 | 9,410 | 9,663 | **8,983** | 52 | 89 | 14,5 |
| 3180 | 10,00 | 7,432 | 6,507 | 9,401 | 9,662 | **8,997** | 113 | 94 | 14,7 |
| 3630 | 10,00 | 7,456 | 6,358 | 9,396 | 9,660 | **8,985** | 44 | 98 | 14,9 |
| 4080 | 10,00 | 7,444 | 6,606 | 9,380 | 9,652 | **9,004** | 0 | 114 | 14,1 |
| 4530 | 10,00 | 7,437 | 6,448 | 9,384 | 9,654 | **8,988** | 68 | 83 | 14,3 |
| 4980 | 10,00 | 7,459 | 6,619 | 9,371 | 9,646 | **9,006** | 0 | 125 | 14,5 |
| 5430 | 10,00 | 7,475 | 6,455 | 9,370 | 9,646 | **8,993** | 65 | 126 | 14,6 |
| 5880 | 10,00 | 7,465 | 6,602 | 9,339 | 9,624 | **8,998** | 0 | 135 | 14,1 |
| 6330 | 10,00 | 7,477 | 6,537 | 9,364 | 9,639 | **9,000** | 96 | 137 | 14,2 |
| 6780 | 10,00 | 7,477 | 6,479 | 9,361 | 9,637 | **8,993** | 26 | 143 | 14,3 |
| 7230 | 10,00 | 7,473 | 6,570 | 9,374 | 9,648 | **9,005** | 111 | 121 | 14,4 |
| 7680 | 10,00 | 7,471 | 6,397 | 9,359 | 9,631 | **8,982** | 40 | 151 | 14,1 |
| 8130 | 10,00 | 7,472 | 6,629 | 9,376 | 9,647 | **9,011** | 0 | 122 | 14,2 |
| 8580 | 10,00 | 7,471 | 6,498 | 9,362 | 9,651 | **8,996** | 82 | 109 | 13,8 |
| 9030 | 10,00 | 7,471 | 6,558 | 9,387 | 9,655 | **9,006** | 12 | 106 | 14,4 |
| 9480 | 10,00 | 7,474 | 6,495 | 9,391 | 9,658 | **9,002** | 81 | 100 | 14,4 |
| 9930 | 10,00 | 7,477 | 6,557 | 9,391 | 9,670 | **9,010** | 10 | 74 | 14,5 |
| 10 380 | 10,00 | 7,470 | 6,667 | 9,409 | 9,679 | **9,024** | 0 | 56 | 14,6 |
| 10 830 | 10,00 | 7,470 | 6,725 | 9,420 | 9,693 | **9,033** | 25 | 27 | 14,3 |
| 11 280 | 10,00 | 7,475 | 6,808 | 9,425 | 9,698 | **9,044** | 0 | 16 | 14,0 |
| 11 730 | 10,00 | 7,475 | 6,799 | 9,425 | 9,698 | **9,043** | 0 | 16 | 13,5 |
| 12 180 | 10,00 | 7,475 | 6,790 | 9,425 | 9,697 | **9,042** | 0 | 16 | 13,0 |
| 12 630 | 10,00 | 7,475 | 6,796 | 9,425 | 9,697 | **9,043** | 0 | 16 | 12,5 |
| 12 930 | 10,00 | 7,475 | 6,796 | 9,425 | 9,697 | **9,043** | 0 | 16 | 12,3 |

*Table complète (431 points) disponible dans `_run45_export.csv`, colonnes A (temps), S-W (scores SCOR), X (PI), D/E (WIP/stock fini), B (débit).*

## Annexe B — Détail des commandes clients (extrait des journaux d'exécution)

| Commande | Quantité | Mode | Lead time (temps simulé) | Statut |
|---|---|---|---|---|
| CMD_31 | 28 | MTS | 29,0 s | SERVIE |
| CMD_32 | 38 | MTS | 34,0 s | SERVIE |
| CMD_33 | 23 | MTS | 33,0 s | SERVIE |
| CMD_34 | 31 | MTS | 37,0 s | SERVIE |
| CMD_35 | 32 | MTS | 38,0 s | SERVIE |
| CMD_36 | 38 | MTS | 29,0 s | SERVIE |
| CMD_37 | 24 | MTS | 39,0 s | SERVIE |
| CMD_38 | 35 | MTS | 20,0 s | SERVIE |
| CMD_39 | 40 | MTS | 20,0 s | SERVIE |
| CMD_40 | 23 | MTS | 39,0 s | SERVIE |
| CMD_41 | 28 | MTS | 45,0 s | SERVIE |
| CMD_42 | 27 | MTS | 39,0 s | SERVIE |
| CMD_43 | 34 | MTS | 32,0 s | SERVIE |
| **CMD_44** | **30** | **MTO** (stock produit fini insuffisant → bascule automatique en production dédiée) | 12 565 s promis (temps simulé), production lancée à t = 10 770 s | SERVIE |
| CMD_45 | 34 | MTS | 23,0 s | SERVIE (dernière commande du run) |

**Épisode notable (t ≈ 10 765 s) :** au moment de créer CMD_44, le stock de produit fini disponible n'était plus que de 22 unités pour une commande de 30 — le système a détecté l'insuffisance et basculé automatiquement le mode de service en MTO (production dédiée), après vérification de la disponibilité de la matière première (GPL vrac, bouteilles vides, accessoires — bilan matière confirmé suffisant dans les logs). La commande a néanmoins été livrée dans le délai d'engagement, sans passer en `EN_RETARD`.

---

*Rapport généré à partir de l'analyse du fichier `SCONTO_SVU_RESULTS_ZENER_SA_Togo_RUN_1773129600000_1788801137005.xlsx` et des journaux d'exécution associés. Modèle SCONTO-SVU, architecture VSM × SCOR.*
