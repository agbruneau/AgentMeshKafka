# Patron Producteur/Consommateur (Pub/Sub)

## Théorie

Le patron **Producteur/Consommateur** (ou **Publish/Subscribe**) est le fondement de l'architecture événementielle avec Kafka.

### Principes

1. **Découplage** : Le producteur ne connaît pas les consommateurs
2. **Asynchrone** : Les messages sont traités de manière asynchrone
3. **Persistance** : Les messages sont stockés et peuvent être rejoués

### Composants Kafka

```
┌──────────────┐     ┌─────────────────────────────┐     ┌──────────────┐
│  PRODUCTEUR  │────▶│         TOPIC               │────▶│ CONSOMMATEUR │
│              │     │  ┌───┬───┬───┬───┬───┐      │     │              │
│              │     │  │ P0│ P1│ P2│...│ Pn│      │     │              │
│              │     │  └───┴───┴───┴───┴───┘      │     │              │
└──────────────┘     └─────────────────────────────┘     └──────────────┘
```

#### Topic
- Canal de communication pour un type d'événement
- Divisé en **partitions** pour le parallélisme
- Les messages sont ordonnés au sein d'une partition

#### Partition
- Unité de parallélisme
- Chaque message a un **offset** unique
- Une partition ne peut être lue que par un seul consommateur d'un groupe

#### Consumer Group
- Groupe de consommateurs partageant la charge
- Chaque partition est assignée à un seul consommateur du groupe

## Implémentation dans kafka-eda-lab

### Topics

| Topic | Producteur | Description |
|-------|------------|-------------|
| `quotation.devis-genere` | Quotation | Nouveau devis créé |
| `quotation.devis-expire` | Quotation | Devis non converti |
| `souscription.contrat-emis` | Souscription | Nouveau contrat |
| `souscription.contrat-modifie` | Souscription | Avenant au contrat |
| `souscription.contrat-resilie` | Souscription | Fin de contrat |
| `reclamation.sinistre-declare` | Réclamation | Nouveau sinistre |
| `reclamation.sinistre-evalue` | Réclamation | Expertise terminée |
| `reclamation.indemnisation-effectuee` | Réclamation | Paiement effectué |

### Flux

```
Quotation                 Souscription              Réclamation
    │                          │                         │
    │   DevisGenere            │                         │
    │─────────────────────────▶│                         │
    │                          │                         │
    │                          │   ContratEmis           │
    │                          │────────────────────────▶│
    │                          │                         │
    │                          │   ContratResilie        │
    │                          │────────────────────────▶│
    │                          │                         │
    │                          │◀────────────────────────│
    │                          │   SinistreDeclare       │
    │                          │                         │
    │                          │◀────────────────────────│
    │                          │   IndemnisationEffectuee│
```

## Points d'attention

### Bonnes pratiques

1. **Idempotence** : Un message peut être traité plusieurs fois
2. **Ordre** : L'ordre n'est garanti qu'au sein d'une partition
3. **Taille des messages** : Éviter les messages trop volumineux

### Pièges courants

1. **Consumer Lag** : Retard de traitement des messages
2. **Rebalancing** : Redistribution des partitions lors de changements
3. **Duplicate processing** : Messages traités plusieurs fois

## Exercices

### Exercice 1 : Observer le flux
1. Démarrez la simulation
2. Ouvrez Kafka UI (http://localhost:8090)
3. Observez les messages dans chaque topic

### Exercice 2 : Consumer Lag
1. Augmentez la vitesse de simulation
2. Observez le consumer lag dans Grafana
3. Que se passe-t-il quand un consommateur est plus lent ?

### Exercice 3 : Arrêt d'un service
1. Arrêtez le service Souscription
2. Continuez à générer des devis
3. Redémarrez Souscription
4. Observez le traitement des messages en attente

## Ressources

- [Documentation Apache Kafka](https://kafka.apache.org/documentation/)
- [Kafka: The Definitive Guide](https://www.confluent.io/resources/kafka-the-definitive-guide/)
