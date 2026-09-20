# Arbre de calcul du Performance Index

**Modèle SCONTO-SVU — architecture VSM × SCOR**

Structure du Performance Index : les cinq attributs SCOR qui le composent, leurs pondérations, et la définition de chaque indicateur retenu.

---

## 1. Formule d'ensemble

Le Performance Index est la moyenne pondérée des cinq attributs de performance SCOR, exprimée sur une échelle de 0 à 10.

```
PI = 0,40 × RL  +  0,20 × RS  +  0,10 × AG  +  0,15 × CO  +  0,15 × AM
```

| Attribut | Intitulé | Nature | Poids |
|---|---|---|---|
| **RL** | Reliability — Fiabilité | Orienté client | 0,40 |
| **RS** | Responsiveness — Réactivité | Orienté client | 0,20 |
| **AG** | Agility — Agilité | Orienté client | 0,10 |
| **CO** | Cost — Coût | Interne | 0,15 |
| **AM** | Asset Management — Gestion des actifs | Interne | 0,15 |

---

## 2. Arbre des indicateurs

```
                          PERFORMANCE INDEX
                            échelle 0 → 10
                                  │
        ┌──────────────┬──────────┼──────────┬──────────────┐
        │              │          │          │              │
       RL             RS         AG         CO             AM
      0,40           0,20       0,10       0,15           0,15
   Fiabilité      Réactivité   Agilité     Coût          Actifs
        │              │          │          │              │
   RL.2.1  ½      RS.1.1        AG.3.32  ⅓  CO.1.1  %    AM.2.2  ½
   RL.2.2  ½      RS.2.1        AG.1.1   ⅓                AM.3.9  ½
                  RS.2.2        Occup.   ⅓
                  RS.2.3
                  RS.2.5
                  RS.3.94
```

---

## 3. RL — Reliability (Fiabilité)

**Poids dans le PI : 0,40** — 2 indicateurs, poids local ½ chacun.

### RL.2.1 — Percentage of Orders Delivered in Full
*Commandes livrées complètes*

Proportion des commandes pour lesquelles la totalité des articles commandés a été livrée dans les quantités demandées.

```
        Nombre de commandes livrées en totalité
       ─────────────────────────────────────────  × 100
          Nombre total de commandes livrées
```

> Une commande est comptée comme « livrée en totalité » uniquement si l'ensemble
> des lignes qui la composent est servi intégralement ; une livraison partielle
> compte pour zéro.

### RL.2.2 — Delivery Performance to Customer Commit Date
*Commandes livrées à la date convenue*

Proportion des commandes livrées à la date d'engagement convenue avec le client.

```
     Nombre de commandes livrées à la date convenue
    ────────────────────────────────────────────────  × 100
          Nombre total de commandes livrées
```

> La date de référence est la date d'engagement communiquée au client, et non la
> date souhaitée initialement par celui-ci. Une livraison hors délai compte pour
> zéro, quelle que soit l'ampleur du retard.

---

## 4. RS — Responsiveness (Réactivité)

**Poids dans le PI : 0,20** — poids local égal entre indicateurs.

### RS.1.1 — Order Fulfillment Cycle Time
*Délai de traitement d'une commande*

Durée moyenne écoulée entre la réception d'une commande client et sa livraison effective.

```
    Somme des délais réels de traitement des commandes livrées
   ───────────────────────────────────────────────────────────
              Nombre total de commandes livrées
```

> Le délai est mesuré en continu, jours calendaires inclus, du moment où la
> commande est reçue jusqu'à sa réception par le client.

### RS.2.1 — Source Cycle Time
*Temps de cycle Approvisionnement*

Durée moyenne d'exécution des activités d'approvisionnement : commande fournisseur, réception, vérification et mise à disposition de la matière.

```
    Somme des durées d'exécution du processus Source
   ─────────────────────────────────────────────────
       Nombre d'occurrences du processus Source
```

### RS.2.2 — Make Cycle Time
*Temps de cycle Production*

Durée moyenne d'exécution des activités de production, de l'ordonnancement jusqu'à la mise à disposition du produit fini.

```
    Somme des durées d'exécution du processus Make
   ───────────────────────────────────────────────
       Nombre d'occurrences du processus Make
```

### RS.2.3 — Deliver Cycle Time
*Temps de cycle Livraison*

Durée moyenne d'exécution des activités de livraison : préparation, chargement, expédition et transport jusqu'au client.

```
    Somme des durées d'exécution du processus Deliver
   ──────────────────────────────────────────────────
       Nombre d'occurrences du processus Deliver
```

### RS.2.5 — Return Cycle Time
*Temps de cycle Retour*

Durée moyenne d'exécution des activités de retour, de l'autorisation du retour jusqu'à sa prise en charge complète.

```
    Somme des durées d'exécution du processus Return
   ─────────────────────────────────────────────────
       Nombre d'occurrences du processus Return
```

### RS.3.94 — Order Fulfillment Dwell Time
*Temps d'attente dans le cycle*

Part du délai total pendant laquelle la commande est en attente, sans qu'aucune activité ne soit exécutée sur elle.

```
    Délai total de traitement  −  Temps de traitement effectif
```

> Cet indicateur isole le temps sans valeur ajoutée à l'intérieur du cycle :
> files d'attente, attentes de ressource, temps de transit non productifs.

---

## 5. AG — Agility (Agilité)

**Poids dans le PI : 0,10** — 3 indicateurs, poids local ⅓ chacun.

### AG.3.32 — Current Delivery Volume
*Volume livré et débit de sortie*

Volume effectivement livré sur la période courante, rapporté à une unité de temps.

```
    Nombre d'unités livrées sur la période
   ────────────────────────────────────────
          Durée de la période observée
```

> Sert de base de référence au calcul des indicateurs d'adaptabilité : c'est le
> volume courant par rapport auquel une variation à la hausse ou à la baisse est
> exprimée.

### AG.1.1 — Upside Supply Chain Adaptability
*Adaptabilité à la hausse*

Augmentation de quantité livrée que la chaîne est capable d'absorber de façon soutenable, dans un délai déterminé et sans coût unitaire supplémentaire significatif.

```
    Volume maximal soutenable  −  Volume courant
   ──────────────────────────────────────────────  × 100
                  Volume courant
```

> Le délai de référence usuel est de trente jours. La contrainte de soutenabilité
> impose que le volume accru puisse être maintenu, et non atteint ponctuellement.

### Taux d'occupation du système

Charge en cours dans le système rapportée à la capacité de traitement simultanée disponible.

```
    Encours moyen présent dans le système
   ───────────────────────────────────────
      Capacité simultanée totale déclarée
```

> Un taux proche de 1 indique un système fonctionnant à sa capacité nominale ;
> au-delà, la chaîne accumule un encours qu'elle ne peut absorber, ce qui réduit
> sa marge de manœuvre face à une variation de la demande.

---

## 6. CO — Cost (Coût)

**Poids dans le PI : 0,15** — 1 indicateur, poids local 1.

### CO.1.1 — Total Supply Chain Management Cost
*Coût total de gestion de la chaîne*

Somme des coûts engagés pour faire fonctionner la chaîne d'approvisionnement, rapportée au chiffre d'affaires qu'elle génère.

```
       Coût total de gestion de la chaîne
      ────────────────────────────────────  × 100
            Chiffre d'affaires généré

   avec  Coût total = coûts de planification
                    + coûts d'approvisionnement
                    + coûts de production
                    + coûts de livraison
                    + coûts de retour
```

> Les coûts de production regroupent la main-d'œuvre directe, la matière
> consommée et les frais indirects affectés aux activités. Le ratio est exprimé
> en pourcentage du chiffre d'affaires : plus il est faible, plus la chaîne est
> performante.

---

## 7. AM — Asset Management (Gestion des actifs)

**Poids dans le PI : 0,15** — 2 indicateurs, poids local ½ chacun.

### AM.2.2 — Inventory Days of Supply
*Jours de couverture de stock*

Nombre de jours de consommation que le stock détenu permet de couvrir.

```
              Stock détenu
   ──────────────────────────────────
     Consommation journalière moyenne
```

> Mesure l'immobilisation de trésorerie sous forme de stock : plus la couverture
> est longue, plus le capital immobilisé est important, au prix d'une meilleure
> protection contre la rupture.

### AM.3.9 — Asset Availability
*Disponibilité des équipements*

Part du temps pendant laquelle un équipement est disponible pour produire, rapportée au temps total considéré.

```
                 Temps moyen entre pannes
   ──────────────────────────────────────────────────────
    Temps moyen entre pannes  +  Temps moyen de réparation
```

> La disponibilité combine la fiabilité de l'équipement, mesurée par l'intervalle
> moyen entre deux défaillances, et sa maintenabilité, mesurée par la durée
> moyenne de remise en service.

---

## 8. Méthode d'agrégation

Les indicateurs sont exprimés dans des unités hétérogènes — pourcentages, durées, ratios financiers, jours de stock. Leur agrégation suit une méthode en quatre étapes.

**Étape 1 — Mise à l'échelle.**
Chaque valeur est ramenée sur une échelle commune de 0 à 10, par interpolation entre une valeur plancher et une valeur de performance idéale, selon que l'indicateur se maximise ou se minimise.

**Étape 2 — Conversion en grades.**
Le score obtenu est traduit en appartenance à six grades de performance, de A à F, dont les centres valent 10, 8, 6, 4, 2 et 0. Entre deux centres, l'appartenance se répartit linéairement et sa somme vaut 1.

**Étape 3 — Agrégation par attribut.**
Les grades des indicateurs d'un même attribut sont combinés selon leurs pondérations locales, ce qui donne le profil de performance de l'attribut.

**Étape 4 — Indice final.**
Les cinq attributs sont combinés selon leurs pondérations, puis ramenés à une valeur unique sur l'échelle 0 à 10 par calcul du centre de gravité des grades :

```
    (10 × A) + (8 × B) + (6 × C) + (4 × D) + (2 × E)
   ──────────────────────────────────────────────────
              A + B + C + D + E + F
```

---

*Pondérations des attributs issues de la configuration du scénario.*
