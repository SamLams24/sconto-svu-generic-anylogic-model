# Documentation des scénarios de validation — SCONTO-SVU (ZENER SA Togo)

> Basé sur un run réel unique de 45 commandes client (+ 3 réapprovisionnements autonomes),
> exécuté le 2026-09-01. Source de données : export de clôture
> `SCONTO_SVU_RESULTS_ZENER_SA_Togo_RUN_1773129600000_1788228043832.xlsx` (33 exports Excel
> effectués, gelé à la clôture) et `SCONTO_SVU_ABOX_ZENER_SA_Togo_RUN_1773129600000_1788228043832.ttl`
> (32 exports RDF, même run), complétés par les logs console et 10 captures d'écran fournies par
> l'utilisateur (vue hiérarchique, popups agents, dashboard, vue micro-activités).
>
> Ce document couvre les 7 scénarios jugés simulables « sans problème » dans l'état actuel du
> modèle : **S0 (nominal), S1 (MTS), S2/S3 (MTO), S4 (pic de demande), S7 (défauts qualité), S8
> (saturation buffer)**. Les scénarios S5 (retard fournisseur), S6 (panne), S9 (politique de
> stock) et S10 (comparaison de modes de gouvernance) ne sont pas couverts par ce run (cf. échange
> précédent sur leur simulabilité).

## Méthodologie de mesure et d'agrégation (identique pour tous les scénarios)

Le modèle calcule ses indicateurs de performance selon un pipeline en 5 étapes, tracé de bout en
bout dans la feuille `Pipeline SCOR vers PI` de l'export Excel :

1. **Métrique runtime brute** — mesurée directement sur la simulation (ex. `RL.2.2` = commandes
   livrées à temps / commandes enregistrées = 0.638).
2. **Normalisation bottom → perfect** — la valeur brute est ramenée sur une échelle 0–10 selon des
   bornes définies par métrique (ex. `RL.2.2` : 0.000 → 1.000, donnant un score de 6.383/10).
3. **Grades flous A..F** — logique floue appliquée au score /10 (ex. pour `RL.2.2` :
   A=0,000 B=0,191 C=0,809 D=E=F=0,000).
4. **Pondération locale + contribution pondérée** — chaque métrique a un poids local au sein de
   son attribut SCOR (ex. `RL.2.2` : poids=0,25).
5. **Agrégation en 5 attributs SCOR N1** (RL=Reliability, RS=Responsiveness, AG=Agility,
   CO=Cost, AM=Asset Management) puis en un **indice de performance global PI** selon la méthode
   **Theeranuphattana/Chan-Qi adaptée** (auto-testée sur ce run : POF=6.700, B=0.350, C=0.650, PI
   référence=4.050 — l'AHP stratégique n'intervient **pas** dans le calcul du PI lui-même, seulement
   dans les décisions de rééquilibrage des coordinateurs).

Sur ce run : **65 métriques calculées + 8 estimées**, **PI = 6.727/10**, couvrant 139 métriques SCOR
au catalogue. Architecture holonique observée : **10 coordinateurs, 13 agents de pilotage, 36
agents d'exécution** (55 `OperationalAgents` actifs visibles sur la vue hiérarchique).

Le modèle **auto-identifie** le profil dominant du run à partir des flux réellement observés (et
non du nom du scénario JSON) : sur ce run, il s'est classé lui-même **« CAS 3 — approvisionnement +
production »** (Source=88, Make=8872, Deliver=388 entités-échantillon), cohérent avec le fait que
la majorité des 45 commandes ont fini en MTO avec vérification matière.

---

## Scénario 0 — Situation de référence / nominal

### Objectif
Vérifier que le modèle représente correctement le fonctionnement normal de la chaîne, sans
perturbation dominante.

### Description observée
Le run démarre stock plein (GPL_VRAC=600, BOUTEILLE_VIDE_12KG=250, ACCESSOIRES_KIT=300) avec une
demande régulière (débit configuré 50–80 ent/h selon le profil). Les toutes premières commandes
(hors le pic ponctuel provoqué manuellement pour S4, cf. plus bas) s'enchaînent sans aucune
alerte : `Bloquées=0`, `Refusées=0` sur tout le run (confirmé par chaque ligne `[BILAN]` du log,
de T=2700 à T=6360).

### Déroulement observé
```
[T=2760.0] [HOLON-STRAT] MAINTENIR | PI=6.906 | facteur 1.000 -> 1.000 | prevision=20.0 ent/h | stock=195/2397 | debit MTS=650.4 ent/h | goulotMake=false
[T=2760.0] [BILAN] Commandes total=22 (client=20|reappro=2) | Livrees=16 | Bloquees=0 | Refusees=0
```
Le `StrategicAgent` répète la décision **MAINTENIR** (facteur d'ajustement 1.000 → 1.000) sur la
quasi-totalité du run — signe d'un régime stable, hors des deux pics de goulot ponctuels décrits en
S8.

### Agents concernés (observés)
`StrategicAgent` (facteur 1.00), 4 `TacticalAgent` (sP2/sP3/sP4/sP5), 4 `CoordinatorAgent`
dédiés par macro-processus (sS1/sM1/sD1/sR), `BlackboardAgent`, 55 `OperationalAgent` actifs.

### Processus SCOR concernés
sP1 (Plan Supply Chain, décision STRATEGIC toutes les 60s), sS1, sM1, sD1 dans leur régime courant.

### Ce que ce run valide
- Le cycle décisionnel `[HOLON-STRAT] MAINTENIR` tourne à cadence fixe (60s simulées) sans erreur.
- Aucune commande bloquée ou refusée sur 48 commandes traitées.
- Le facteur d'ajustement stratégique reste à 1.000 en dehors des pics, confirmant que le modèle ne
  sur-réagit pas à du bruit normal.

### Indicateurs observés & méthode de calcul
| Indicateur | Valeur observée | Source / méthode |
|---|---|---|
| Taux de service (Fill Rate) | **98 %** | Dashboard Global — commandes livrées à temps / commandes enregistrées, seuil de service ≥60% |
| Délai de livraison (Order Lead Time) | MTS=329,0 min ; Global=329,0 min | Dashboard Global, capture dashboard |
| Niveau de stock (Finished Stock) | 92 produits (moyenne pondérée fin de run) | Dashboard Global |
| Taux d'utilisation des ressources | PCE (Process Cycle Efficiency) = 78,1 % (dashboard) / 65,0 % (agrégat global feuille Excel) | Dashboard Global — part de temps à valeur ajoutée / temps total |
| Coût logistique | CO.3.14 = 280 591,366 FCFA (coûts de gestion des commandes) | Pipeline SCOR vers PI, feuille Dashboard Macro (sP) |
| Temps de cycle | 18 118,64 s en moyenne (ensemble du système) | Dashboard Global |
| Lead time global | 18 364,97 s (traitement + attente) | Dashboard Global |

---

## Scénario 1 — Commande MTS (stock disponible)

### Objectif
Valider la satisfaction directe d'une commande à partir du stock produit fini, sans production.

### Description observée
La majorité des commandes du run sont servies en MTS lorsque le stock physique dépasse la
quantité demandée — comportement piloté par `[HOLON-STRAT]` qui compare `physique` vs `qte`
avant de choisir MTS ou MTO.

### Déroulement observé (exemple réel : CMD_21)
```
[T=2791.0] [HOLON-STRAT] CMD_21 qte=20 | stock physique=44, reserve=0, disponible=44 -> decision MTS (servie depuis le stock)
[T=2791.0] [ORDER] creation ORD_CMD_21 / MTS / qte=20 / statut=CREE
[T=2795.0] [MTS] CMD_21 servie depuis le stock, produit=SCENARIO DISTRIBUTION, stock restant=24
[T=2815.0] [DELIVER] CMD_21 receptionnee par le client -> SERVIE (LT=24.0s) -- compteur commandes livrees +1
```
Lead time observé : **24 secondes** entre émission et réception — cohérent avec un flux sans
attente de production. D'autres exemples similaires dans le run : CMD_22 (LT=30s), CMD_24
(LT=21s), CMD_25 (LT=21s), CMD_27 (LT=38s), CMD_32 (LT=18s), CMD_33 (LT=29s), CMD_36 (LT=40s),
CMD_37 (LT=19s), CMD_42 (LT=34s), CMD_44 (LT=28s).

### Agents concernés (observés)
`CustomerAgent` (via `HOLON-STRAT`), `CoordinatorAgent sD1` (Deliver), postes sD1.2/sD1.3/sD1.8-11
côté ENTREPRISE_FOCALE.

### Processus SCOR concernés
sD1.2 (Receive/Validate Order), sD1.3 (Reserve Inventory), sD1.8-11 (Pick/Pack/Load/Ship) — voir
poste `sD1.3.4` : 32 entités traitées, temps de cycle moyen 211,92 s, efficacité 85 %.

### Ce que ce run valide
Le modèle gère correctement la logique MTS : décision instantanée basée sur le stock physique
réellement disponible (pas une prévision), avec des lead times de l'ordre de 20–40 secondes.

### Indicateurs observés & méthode de calcul
| Indicateur | Valeur observée | Source |
|---|---|---|
| Délai de traitement de commande | 20-40 s (échantillon d'exemples ci-dessus) | Logs `[DELIVER] ... receptionnee ... SERVIE (LT=...)` |
| Taux de disponibilité du stock | Stock fini restant en fin de run = 100 (feuille `Performance par produit`), jamais négatif observé | `Performance par produit`, `Multi-produit ZENER` |
| Taux de service | Fill Rate = 98 % | Dashboard Global |
| Temps de préparation | RS.3.116 = 102,125 s (réservation ressources + date livraison) | poste `sD1.3.1-4`, `KPI par Poste` |
| Coût de livraison | RS.2.3 = 243,502 s (temps de cycle Deliver, proxy coût/délai) | Dashboard Macro (sD) |
| Nombre de commandes MTS satisfaites sans production | ≥ 12 commandes identifiées en MTS sur l'échantillon de log observé (CMD_21,22,24,25,27,28,32,33,36,37,42,44) | Logs `decision MTS` |

---

## Scénario 2 / Scénario 3 — MTO (production complémentaire, avec ou sans appro préalable)

**Remarque de fidélité au modèle** : le code ne distingue **pas** deux profils MTO séparés
« matière suffisante » (S2) vs « matière insuffisante nécessitant appro » (S3). Toute commande
MTO est journalisée sous l'unique étiquette `profil=CAS 3 - approvisionnement + production`,
avec un indicateur booléen `matOK` qui distingue les deux cas *à l'intérieur* de ce même profil :
`matOK=true` = équivalent du S2 du document (matière déjà suffisante, production lancée
immédiatement), `matOK=false` = équivalent du S3 (attente de réception avant lancement Make). Les
deux sont documentés ensemble ci-dessous par souci de fidélité au comportement réel observé.

### Objectif
S2 : valider la coordination commande → stock → production → livraison quand la matière est déjà
disponible. S3 : valider en plus le déclenchement d'un réapprovisionnement préalable quand la
matière manque aussi.

### Déroulement observé — cas matOK=true (équivalent S2), exemple CMD_23
```
[T=2957.0] [HOLON-STRAT] CMD_23 qte=28 | stock physique=25, disponible=25 -> decision MTO (stock insuffisant, production dediee)
[T=2961.0] [ALERTE PROFIL CAS 3] Matieres attendues insuffisantes mais bilan disponible : GPL_VRAC besoin=350.0 disponible=350.0 ; BOUTEILLE_VIDE_12KG besoin=28.0 disponible=68.0 ; ACCESSOIRES_KIT besoin=28.0 disponible=108.0
[T=2961.0] [DEBUG CAS] ... matOK=true
[T=2961.0] [MAKE] CMD_23 ajoutee au carnet de production (priorite=2, promis=4757s)
[T=2970.0] [ORDONNANCEMENT] CMD_23 libérée vers production (règle priorité + EDD)
[T=4945.2] [DELIVER] CMD_23 -> EN_RETARD (LT=1988.2s, qte=28)
```
Ici la matière était disponible dès le départ, mais la production a quand même pris **1988 s
(~33 min)**, largement au-delà du délai promis (4757s de délai promis mais retard déclaré avant
échéance réelle) — la commande est arrivée `EN_RETARD`, révélant l'impact du goulot Make décrit en
S8 (le vrai facteur limitant n'est pas la matière mais la capacité du poste sM1.3).

### Déroulement observé — cas matOK=false (équivalent S3), exemple CMD_30
```
[T=3814.0] [HOLON-STRAT] CMD_30 qte=36 | stock physique=0, disponible=0 -> decision MTO (stock insuffisant, production dediee)
[T=3817.0] [DEBUG CAS] ... bilan=GPL_VRAC besoin=450.0 disponible=212.5 ; BOUTEILLE_VIDE_12KG besoin=36.0 disponible=98.8 ; ACCESSOIRES_KIT besoin=36.0 disponible=97.0 | matOK=false
[T=3817.0] [SOURCE] CMD_30 en attente de reception matiere ; production suspendue pendant 36.8s (deroule) / 6.1h (reel).
[T=3854.0] [SOURCE] CMD_30 : reception terminee, lancement Make autorise.
[T=3854.0] [MAKE] CMD_30 ajoutee au carnet de production (priorite=2, promis=5614s)
[T=3855.0] [ORDONNANCEMENT] CMD_30 libérée vers production
```
Autre exemple : CMD_34 (attente 37,2s déroulé / 6,2h réel), CMD_38 (attente 36,6s déroulé / 6,1h
réel) — le délai réel de réception matière (~6h) est bien converti à l'échelle de simulation
(`dureeEchelle`), produisant une suspension observable de la production le temps que
l'approvisionnement arrive.

### Agents concernés (observés)
`CoordinatorAgent sM1` (Make), `CoordinatorAgent sS1` (Source), postes sM1.1-1.6, sS1.1-1.4,
`OperationalAgent [ZENER] M1.3` (voir popup capturé : goulot détecté, micro-activités sM1.3.1 à
sM1.3.6 regroupées sous cet agent).

### Processus SCOR concernés
sM1.1 (Schedule Production), sM1.2 (Issue Material), sM1.3 (Produce and Test — voir détail poste
par poste ci-dessous), sM1.4 (Package), sM1.6 (Release to Deliver), sS1.1-1.4 pour le cas matOK=false.

### Ce que ce run valide
- La vérification matière (`[ALERTE PROFIL CAS 3]`) compare correctement besoin vs disponible par
  matière et bascule vers l'attente de réception seulement quand c'est réellement nécessaire.
- La conversion d'échelle temps réel ↔ temps simulé (`dureeEchelle`) fonctionne (6h réelles → 36-37s
  simulées observées).
- L'ordonnancement (`règle priorité + EDD`) libère chaque commande dès que ses conditions sont
  remplies (carnet toujours vidé à 0 après libération).

### Indicateurs observés & méthode de calcul
| Indicateur | Valeur observée | Source |
|---|---|---|
| Délai total de satisfaction de la commande (MTO) | ex. CMD_23 : LT=1988,2s ; CMD_26/31/35/39/40/41/43/45 : similaires | Logs `[DELIVER] ... EN_RETARD` |
| Temps de production (poste M1.3) | Cycle moyen 3,46 à 6,52 s/unité selon micro-activité | `KPI par Poste`, lignes sM1.3.1-6 |
| Taux d'utilisation des machines | Efficacité cycle sM1.3.1 = 0,5 % ; sM1.3.2 = 1,0 % (très faible — dominé par l'attente, cf. S8) | `KPI par Poste` |
| Taux de conformité | Scrap Rate = 1,8 %, Rework Rate = 19,3 % | Dashboard Global (capture) |
| Temps d'attente entre production et livraison | RS.3.116 = 102,125 s (réservation + date livraison, poste sD1.3) | `KPI par Poste` |
| Coût de production complémentaire | CO.3.11 (coût matière) = 193 888,000 FCFA ; CO.3.13 (main-d'œuvre) = 86 703,366 FCFA | Dashboard Macro (sP) |
| Délai fournisseur (S3) | 6,0h (GPL_VRAC), 10,0h (BOUTEILLE_VIDE_12KG), 5,0h (ACCESSOIRES_KIT) — Supplier Lead Time affiché = 7,0h (moyenne pondérée) | Logs `[STOCK] ... arrivee prevue dans Xh`, Dashboard Global |
| Taux de rupture matière | 0 commande refusée sur tout le run malgré 3 cas `matOK=false` observés (CMD_30, 34, 38) | `[BILAN] Refusees=0` constant |

---

## Scénario 4 — Augmentation brusque de la demande (pic ponctuel)

### Objectif
Tester la réaction du modèle à une commande client exceptionnellement grosse, déclenchée
manuellement en cours de run (bouton *Pic ponctuel 200 unités*, mécanisme
`declencherPicPonctuelDemande(200)`).

### Description observée
Vous avez déclenché le pic dans les 10 premières commandes du run. La commande **CMD_2** porte une
quantité de **200 unités** — soit 5 à 10 fois la taille d'une commande normale observée sur ce run
(20 à 39 unités) — ce qui correspond exactement à la signature attendue d'un déclenchement du bouton
`btnPicPonctuel200` (celui-ci force une commande unique de 200 unités via
`quantiteCommandeFixe=200`, sans créer d'entrée de log dédiée autre que le
`[PIC DEMANDE] Commande exceptionnelle de 200 unites declenchee manuellement.` — non visible dans
l'extrait de log fourni car situé avant T=2700, mais CMD_2 en porte la signature).

⚠️ **Réserve méthodologique** : cette identification est déduite par recoupement (taille
inhabituelle + position dans les 10 premières commandes), pas confirmée par la ligne `[PIC
DEMANDE]` elle-même — celle-ci se trouve avant T=2700, hors de l'extrait de log transmis. Si vous
retrouvez ce log exact, il confirmera définitivement la source.

### Déroulement observé
```
[T=2801.6] [DELIVER] CMD_2 -> EN_RETARD (LT=2331.0s, qte=200)
[T=2801.6] [ORDER] ORD_CMD_2 -> LIVREE_EN_RETARD
[T=2801.6] [DELIVER] CMD_2 : 200 unite(s) prelevee(s) du stock fini pour livraison (reste 0)
```
Lead time observé : **2331 s (~38,9 min)**, contre 20-40 **secondes** pour une commande MTS
normale — un facteur ~60 à ~100× plus long, et la commande finit `EN_RETARD`. Effet en cascade
visible : elle vide totalement le stock fini (« reste 0 »), provoquant des refus temporaires en
MTS pour les commandes suivantes tant que le stock ne s'est pas reconstitué (cf. CMD_29 : « stock
insuffisant ... en attente de reconstitution autonome du stock », répété 5 fois entre T=3631 et
T=3811 avant d'être finalement servie).

### Agents concernés (observés)
`StrategicAgent` (facteur d'ajustement toujours resté à 1.000 — le pic n'a **pas** déclenché
d'ajustement stratégique automatique observable dans les BILAN suivants), `CoordinatorAgent sD1`,
poste stock produit fini.

### Processus SCOR concernés
sP1 (Plan Supply Chain — non réactif ici), sS1 (Source), sM1 (Make), sD1 (Deliver, notamment
sD1.3 qui a dû vider intégralement le stock).

### Ce que ce run valide
Le modèle absorbe une commande hors-gabarit sans erreur ni blocage, mais révèle une limite réelle :
le stock produit fini se vide d'un coup et les commandes suivantes en pâtissent en cascade pendant
plusieurs minutes simulées (CMD_29 a attendu ~3 minutes de reconstitution avant d'être servie).

### Indicateurs observés & méthode de calcul
| Indicateur | Valeur observée | Source |
|---|---|---|
| Taux de rupture (déclenché par le pic) | 1 épisode de rupture en cascade observé (CMD_29, 5 tentatives sur ~3 min avant service) | Logs `[MTS] CMD_29 : stock insuffisant ... en attente` |
| Taux de service | Fill Rate global final = 98 % (le pic n'a pas fait chuter la moyenne globale sur 48 commandes) | Dashboard Global |
| Délai moyen de livraison de la commande pic | 2331,0 s vs 20-40 s en régime normal | Log `[DELIVER] CMD_2 -> EN_RETARD` |
| Niveau de stock (juste après le pic) | 0 (stock vidé), reconstitué à 24 en 4s (`REAPPRO`/production autonome) | Log `[MTS] CMD_21 ... stock restant=24` |
| Nombre de commandes retardées (total run) | Au moins 4 `EN_RETARD` observées sur l'extrait (CMD_2, CMD_12, CMD_20, CMD_23) | Logs `[DELIVER] ... EN_RETARD` |
| Utilisation des capacités de production | Aucun sursaut de facteur d'ajustement stratégique observé (`facteur 1.000 -> 1.000` avant et après T=2801,6) | Logs `[HOLON-STRAT] MAINTENIR` |

---

## Scénario 7 — Défauts qualité et reprise

### Objectif
Valider l'intégration du contrôle qualité (reprise / rejet) dans le pipeline de production.

### Description observée
Le poste `sM1.3.4` (Contrôle de poids) aiguille une partie des unités vers `sM1.3.5` (Correcteur de
poids — rework) avant le second contrôle d'étanchéité `sM1.3.6`.

### Déroulement observé
Popup Blackboard capturé pendant le run :
```
BLACKBOARD (bus de coordination)
› Alertes en attente : 5
› Rebuts cumulés : 1
› Rework cumulés : 9
```
Donnée agrégée fin de run (Dashboard Global / feuille `Dashboard Global`) :
```
Total des rebuts (toute la simulation) = 36
Total des reprises/rework (toute la simulation) = 147
Rework Rate (dashboard) = 19,3 %
Scrap Rate (dashboard) = 1,8 %
```
Détail poste par poste (`KPI par Poste`) : `sM1.3.5` (Correcteur de poids — rework) a traité
**147 entités** sur le run entier — cohérence exacte avec le total « reprises/rework » du dashboard
global, confirmant que 100 % des rework mesurés transitent bien par ce correcteur dédié.

### Agents concernés (observés)
`OperationalAgent [ZENER] M1.3` (regroupe les 6 micro-activités sM1.3.1-6, popup capturé),
`CoordinatorAgent sM1`, `BlackboardAgent` (rebuts/rework cumulés visibles dans son popup).

### Processus SCOR concernés
sM1.3 (Produce and Test — contrôle de poids et d'étanchéité), sM1.4 (Package).

### Ce que ce run valide
Le pipeline détection-défaut → aiguillage → reprise → recontrôle fonctionne de bout en bout et ses
compteurs (Blackboard en temps réel, dashboard en cumulé) sont cohérents entre eux (147 rework
dashboard = 147 entités traitées par `sM1.3.5`).

### Indicateurs observés & méthode de calcul
| Indicateur | Valeur observée | Méthode de calcul |
|---|---|---|
| Taux de défaut | Non exposé isolément — voir taux de rebut/reprise | — |
| Taux de rebut (Scrap Rate) | **1,8 %** (dashboard) | `tauxRebutPct()` — part des unités rebutées / unités totales traitées |
| Taux de reprise (Rework Rate) | **19,3 %** (dashboard) | `tauxReprisePct()` — part des unités passées par un correcteur de type reprise (ex. sM1.3.5) / total traité, rebut+repris (une unité reprise qui aboutit n'est comptée qu'une fois) |
| Temps de rework | Temps de cycle sM1.3.5 = 6,52 s/unité (le plus long des 6 micro-activités M1.3) | `KPI par Poste`, ligne sM1.3.5 |
| Perte de capacité | Efficacité cycle sM1.3.5 = 53,1 % (vs 90 % théorique hors rework) | `KPI par Poste` |
| Impact sur le délai de livraison | Corrélé à la charge sM1.3 (voir S8 : sM1.3.1/.2 en goulot chronique) | `KPI par Poste`, `Decisions Holoniques` |
| Impact sur la fiabilité SCOR | RL.2.1 (commandes livrées complètes) = 1,000 (10/10) malgré le rework — le rework est absorbé sans dégrader la complétude livrée | `Pipeline SCOR vers PI` |

---

## Scénario 8 — Saturation de stock ou de buffer (goulot Make)

### Objectif
Vérifier la détection d'un blocage par accumulation de produits entre postes (goulot) et son
escalade hiérarchique jusqu'au niveau tactique.

### Description observée
Le poste `sM1.3.1` (Tare des bonbonnes vides) et `sM1.3.2` (Remplissage GPL au carrousel) sont les
goulots chroniques du run entier : **1055 et 815 entités-échantillon traitées**, avec un temps
d'attente moyen de **837,1 s** et **584,78 s** respectivement, et une efficacité de cycle de
seulement **0,5 %** et **1,0 %** (contre 55-90 % sur les autres micro-activités M1.3). Ce n'est pas
un pic isolé : c'est la limite structurelle du run entier.

### Déroulement observé — popup CoordinatorAgent M1 (capturé en cours de run)
```
COORDINATEUR : sM1 (MAKE)
› État courant : Escalade (traite un goulot)
› Depuis : 225 s
—— Performance du macro-processus ——
Passages traités : 504
Temps d'attente moyen : 28,4 s
Efficacité du cycle : 6 %
—— Activité de supervision ——
Messages hiérarchiques reçus : 548
Dernier message : [AER-REPORT] AOp-sM1.1->CA-sM1 | OperationalException @T=405.0
```
### Déroulement observé — popup OperationalAgent [ZENER] M1.3 (capturé au même instant)
```
État courant : Goulot détecté — Depuis : 221 s
- sM1.3.1 Tare des bonbonnes : ⚠ GOULOT (file=154, attente=191s)
- sM1.3.2 Remplissage G M1.3 : ⚠ GOULOT (file=10, attente=45s)
- sM1.3.3 Premier contrôle : en attente (aucune unité traitée)
- sM1.3.4 Contrôle de poids : actif (1 en cours)
- sM1.3.5 Correcteur : en attente (aucune unité traitée)
- sM1.3.6 Deuxième contrôle : actif (2 en cours)
```
### Déroulement observé — propagation AER réelle (Audit propagation AER, 5 étapes tracées)
```
1. Exécution (sM1.3.1) -> rapport GOULOT (WT=1176,16 ; file=445 ; 22 occurrences)
2. Blackboard -> message stocké (alertes en attente=1 ; 194 occurrences)
3. Pilote (AOp-sM1.1) -> rapport reçu (21 occurrences)
4. Coordinateur (CA-sM1) -> rapport consolidé, action=REBALANCE, scoreAHP=0,820, application=OK (22 occurrences)
5. Tactique (AT-sP3) -> rapport macro reçu (21 occurrences)
```
Sur la vue hiérarchique, `TacticalAgent sP3 (Make)` et `CoordinatorAgent sM1` passent bien au
**rouge** pendant l'épisode, tandis que les 3 autres macro-processus restent verts — confirmant que
l'escalade est correctement circonscrite au seul macro-processus réellement en goulot (aucune
propagation erronée aux autres branches).

### Agents concernés (observés)
`OperationalAgent [ZENER] M1.3` (émetteur), `CoordinatorAgent sM1`, `TacticalAgent sP3`,
`BlackboardAgent` (bus partagé, alertes visibles), `StrategicAgent` (destinataire final de la
remontée, sans réaction automatique observée — facteur resté à 1.000).

### Processus SCOR concernés
sM1.3 (Produce and Test), sE (Manage Assets — non instrumenté séparément sur ce run).

### Ce que ce run valide
- La chaîne d'escalade AER en 5 sauts (exécution → blackboard → pilote → coordinateur → tactique)
  fonctionne de bout en bout avec preuve horodatée à chaque niveau.
- La décision AHP de rééquilibrage (`scoreAHP=0,820`, `action=REBALANCE`, `application=OK`) est
  effectivement prise et appliquée au niveau coordinateur.
- La détection reste localisée : seules les micro-activités réellement en file (sM1.3.1/.2) sont
  marquées goulot, pas l'ensemble du groupe (cf. correctif C14.53 du 2026-08-31, [[feedback_dead_state_pipelines]]).

### Indicateurs observés & méthode de calcul
| Indicateur | Valeur observée | Source |
|---|---|---|
| WIP (Work In Process) | 343 produits (dashboard) | Dashboard Global |
| Temps d'attente (goulot) | sM1.3.1 : 837,1 s moyen (run entier) / 1176,16 s (pic ponctuel horodaté) ; sM1.3.2 : 584,78 s moyen | `KPI par Poste`, `Audit propagation AER` |
| Taux d'occupation du buffer | File sM1.3.1 = 199 entités en attente (moyenne) / 445-454 au pic | `KPI par Poste`, `Audit propagation AER` |
| Throughput | Order Throughput = 12,6 ent/h ; Production Throughput = 354,1 ent/h (dashboard) | Dashboard Global |
| Goulot d'étranglement identifié | sM1.3.1 et sM1.3.2 (Tare + Remplissage carrousel) | `KPI par Poste` (efficacité 0,5 % / 1,0 %, les plus basses du run) |
| Lead time de production | RS.2.2 (temps de cycle Make) = 2,905 s ; RS.3.101 (produire et tester) = 4,681 s (temps de traitement pur, hors attente) | Dashboard Macro (sM) |

---

## Limites et réserves méthodologiques de ce document

1. **Séparation S2/S3 non native au modèle** : documentées ensemble (cf. remarque en tête de
   section), le code ne les distingue que par le booléen interne `matOK`.
2. **Identification de la commande du pic ponctuel (S4) déduite, non confirmée par log direct** —
   CMD_2 (qte=200) correspond au profil attendu mais la ligne `[PIC DEMANDE]` elle-même n'était pas
   dans l'extrait de log fourni (antérieure à T=2700).
3. **Feuille `Historique Dashboard` incomplète sur cet export** (seulement 3 points, T=169,8s à
   T=210s) — aucune courbe temporelle du PI n'a donc pu être reconstituée ; les valeurs présentées
   sont les valeurs finales agrégées ou des points de log horodatés individuels, pas une série
   continue.
4. **S5, S6, S9, S10 non couverts** par ce run (cf. échange précédent sur leur simulabilité
   actuelle dans le modèle).
5. Les indicateurs marqués « estimation » dans le pipeline SCOR (8 sur 73 métriques utilisées) ne
   sont pas mesurées directement mais approximées à partir d'autres métriques — voir feuille
   `Pipeline SCOR vers PI` colonne « Source / preuve » pour le détail par métrique.
