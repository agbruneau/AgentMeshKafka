# Introduction à kafka-eda-lab

## Présentation

**kafka-eda-lab** est une simulation pédagogique conçue pour apprendre et expérimenter les patrons d'architecture **Event-Driven Architecture (EDA)** avec Apache Kafka.

## Objectifs

À l'issue de cette simulation, vous serez capable de :

1. **Maîtriser les concepts fondamentaux de Kafka**
   - Topics, partitions, offsets
   - Producteurs et consommateurs
   - Consumer groups
   - Garanties de livraison

2. **Comprendre et implémenter les patrons EDA**
   - Producteur/Consommateur (Pub/Sub)
   - Event Sourcing
   - CQRS
   - Saga (Choreography)
   - Dead Letter Queue

3. **Concevoir une architecture d'interopérabilité**
   - Flux événementiels entre systèmes
   - Découplage des services
   - Résilience et tolérance aux pannes

4. **Exploiter l'observabilité**
   - Métriques avec Prometheus/Grafana
   - Logs centralisés avec Loki
   - Tracing distribué avec Jaeger

## Domaine métier

La simulation utilise le domaine de l'**Assurance Dommages** avec trois systèmes :

```
┌─────────────┐         ┌──────────────┐         ┌──────────────┐
│  QUOTATION  │────────▶│ SOUSCRIPTION │────────▶│  RÉCLAMATION │
│   (Devis)   │         │  (Contrats)  │◀────────│  (Sinistres) │
└─────────────┘         └──────────────┘         └──────────────┘
```

| Système | Rôle |
|---------|------|
| **Quotation** | Génération de devis et calcul de prime |
| **Souscription** | Émission et gestion des contrats |
| **Réclamation** | Déclaration et traitement des sinistres |

## Progression pédagogique

Le projet est organisé en **7 phases** progressives :

| Phase | Patron | Tag Git |
|-------|--------|---------|
| 1 | Infrastructure | `v1.0-infra` |
| 2 | Producteur/Consommateur | `v2.0-pubsub` |
| 3 | Event Sourcing | `v3.0-eventsourcing` |
| 4 | CQRS | `v4.0-cqrs` |
| 5 | Saga Choreography | `v5.0-saga` |
| 6 | Dead Letter Queue | `v6.0-dlq` |
| 7 | Version finale | `v7.0-final` |

Chaque phase s'appuie sur les précédentes et ajoute une nouvelle couche de complexité.

## Prérequis techniques

- Docker Desktop pour Windows
- 8 Go de RAM minimum
- Connaissance de base de la ligne de commande

## Pour commencer

1. Clonez le projet
2. Exécutez `docker-compose up -d`
3. Accédez au dashboard : http://localhost:8080

Bonne exploration !
