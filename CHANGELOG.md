# Changelog

Toutes les modifications notables de ce projet sont documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/).

---

## [v1.0-infra] - 2026-01-18

### Phase 1 : Infrastructure de base

Mise en place de l'infrastructure complète pour la simulation EDA.

### Ajouté

#### Kafka
- Apache Kafka 3.7.0 en mode KRaft (sans Zookeeper)
- Confluent Schema Registry 7.6.0
- 9 topics préconfigurés :
  - `quotation.devis-genere`
  - `quotation.devis-expire`
  - `souscription.contrat-emis`
  - `souscription.contrat-modifie`
  - `souscription.contrat-resilie`
  - `reclamation.sinistre-declare`
  - `reclamation.sinistre-evalue`
  - `reclamation.indemnisation-effectuee`
  - `dlq.errors`
- Kafka UI pour l'exploration

#### Observabilité
- Prometheus 2.50.0 pour les métriques
- Grafana 10.3.0 avec provisioning automatique
- Loki 2.9.4 pour les logs centralisés
- Jaeger 1.54 pour le tracing distribué
- Dashboard Grafana "Kafka Overview"

#### Structure du projet
- Module Go initialisé
- Arborescence complète des dossiers
- Makefile avec commandes utilitaires
- Configuration Docker Compose
- Scripts de health-check

#### Documentation
- README.md complet
- Introduction au projet
- Documentation du patron Producteur/Consommateur

### URLs d'accès

| Service | URL |
|---------|-----|
| Kafka UI | http://localhost:8090 |
| Grafana | http://localhost:3000 |
| Jaeger | http://localhost:16686 |
| Prometheus | http://localhost:9090 |

---

## [v2.0-pubsub] - 2026-01-18

### Phase 2 : Patron Producteur/Consommateur

Implémentation complète du patron Pub/Sub avec les trois services métier.

### Ajouté

#### Services métier

##### Quotation (Port 8081)
- Création de devis d'assurance (AUTO, HABITATION, AUTRE)
- Calcul automatique des primes
- Gestion des expirations (30 jours)
- Événements: `DevisGenere`, `DevisExpire`
- API REST complète avec métriques Prometheus

##### Souscription (Port 8082)
- Conversion automatique des devis en contrats
- Gestion des modifications (avenants)
- Résiliation des contrats
- Événements: `ContratEmis`, `ContratModifie`, `ContratResilie`
- Consumer Kafka pour `devis-genere`

##### Réclamation (Port 8083)
- Déclaration de sinistres
- Évaluation automatique (simulation)
- Indemnisation
- Événements: `SinistreDeclare`, `SinistreEvalue`, `IndemnisationEffectuee`
- Consumer Kafka pour `contrat-emis`, `contrat-resilie`

#### Dashboard (Port 8080)
- Interface HTMX + Go Templates
- Événements temps réel via SSE
- Diagramme de flux animé
- Statistiques par service
- Documentation intégrée

#### Simulateur
- Génération automatique d'événements
- Taux configurable (défaut: 1 evt/sec)
- Support de tous les types d'événements
- Statistiques de simulation

#### Infrastructure
- Producteur Kafka avec Sarama
- Consumer Kafka avec Consumer Groups
- Repository SQLite pour chaque service
- Métriques Prometheus par service

### URLs d'accès

| Service | URL |
|---------|-----|
| Dashboard | http://localhost:8080 |
| Quotation API | http://localhost:8081 |
| Souscription API | http://localhost:8082 |
| Réclamation API | http://localhost:8083 |

### Fichiers créés

```
internal/
├── database/
│   ├── sqlite.go
│   ├── quotation_repository.go
│   ├── contrat_repository.go
│   └── sinistre_repository.go
├── kafka/
│   ├── config.go
│   ├── producer.go
│   └── consumer.go
├── models/
│   ├── quotation.go
│   ├── contrat.go
│   ├── sinistre.go
│   └── events.go
└── services/
    ├── quotation/
    ├── souscription/
    └── reclamation/

cmd/
├── dashboard/
├── quotation/
├── souscription/
├── reclamation/
└── simulator/
```

---

## [Unreleased]

### À venir dans v3.0-event-sourcing
- Event Store avec snapshots
- Reconstruction d'état
- Replay des événements
