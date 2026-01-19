# kafka-eda-lab

**Simulation pédagogique d'architecture événementielle (EDA) avec Apache Kafka**

---

## Description

`kafka-eda-lab` est une application académique conçue pour apprendre et expérimenter les patrons d'architecture Event-Driven Architecture (EDA) dans un contexte d'interopérabilité d'entreprise.

### Domaine métier

La simulation utilise le domaine de l'**Assurance Dommages** avec trois systèmes :

| Système | Rôle |
|---------|------|
| **Quotation** | Génération de devis et calcul de prime |
| **Souscription** | Émission et gestion des contrats |
| **Réclamation** | Déclaration et traitement des sinistres |

### Patrons d'architecture couverts

1. **Producteur/Consommateur (Pub/Sub)** - Fondamentaux de Kafka
2. **Event Sourcing** - État reconstruit depuis les événements
3. **CQRS** - Séparation lecture/écriture
4. **Saga (Choreography)** - Transactions distribuées
5. **Dead Letter Queue** - Gestion des erreurs

---

## Prérequis

- **Docker Desktop** pour Windows
- **Go 1.21+** (optionnel, pour le développement)
- **Make** (optionnel, via Git Bash ou chocolatey)
- **8 Go de RAM** minimum recommandé

---

## Démarrage rapide

### 1. Cloner le projet

```bash
git clone https://github.com/agbru/kafka-eda-lab.git
cd kafka-eda-lab
```

### 2. Configurer l'environnement

```bash
cp .env.example .env
```

### 3. Démarrer l'infrastructure

```bash
# Avec Make
make up

# Ou directement avec Docker Compose
docker-compose up -d
```

### 4. Vérifier que tout fonctionne

```bash
make health
# ou
make status
```

---

## Accès aux services

| Service | URL | Description |
|---------|-----|-------------|
| **Dashboard** | http://localhost:8080 | Interface de contrôle de la simulation |
| **Grafana** | http://localhost:3000 | Dashboards et métriques |
| **Jaeger** | http://localhost:16686 | Tracing distribué |
| **Kafka UI** | http://localhost:8090 | Exploration Kafka |
| **Prometheus** | http://localhost:9090 | Métriques brutes |

---

## Commandes disponibles

### Build

```bash
make build          # Compile tous les services Go
make clean          # Nettoie les binaires
```

### Docker

```bash
make up             # Démarre l'environnement
make down           # Arrête l'environnement
make reset          # Réinitialise complètement
make logs           # Affiche les logs
make status         # État des conteneurs
```

### Tests

```bash
make test           # Tests unitaires
make test-integration  # Tests d'intégration
make test-load      # Tests de charge
make test-cover     # Tests avec couverture
```

### Diagnostics

```bash
make health         # Vérifie la santé des services
make topics         # Liste les topics Kafka
```

### Outils (ouvre le navigateur)

```bash
make dashboard      # Ouvre le Dashboard
make grafana        # Ouvre Grafana
make jaeger         # Ouvre Jaeger
make kafka-ui       # Ouvre Kafka UI
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Dashboard (8080)                          │
│                   Contrôle et Visualisation                      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Apache Kafka (KRaft)                         │
│                    + Schema Registry                             │
└─────────────────────────────────────────────────────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│   Quotation   │      │ Souscription  │      │  Réclamation  │
│    (8081)     │─────▶│    (8082)     │─────▶│    (8083)     │
│               │      │               │◀─────│               │
└───────────────┘      └───────────────┘      └───────────────┘
        │                       │                       │
        └───────────────────────┴───────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Observabilité                             │
│     Prometheus (9090) │ Grafana (3000) │ Loki │ Jaeger (16686)  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Structure du projet

```
kafka-eda-lab/
├── cmd/                    # Points d'entrée des services
│   ├── dashboard/
│   ├── quotation/
│   ├── souscription/
│   ├── reclamation/
│   └── simulator/
├── internal/               # Code interne
│   ├── kafka/              # Client Kafka
│   ├── models/             # Modèles de données
│   ├── database/           # Accès SQLite
│   ├── services/           # Logique métier
│   └── observability/      # Métriques, logs, tracing
├── web/                    # Interface Web
│   ├── templates/
│   ├── static/
│   └── handlers/
├── schemas/                # Schémas Avro
├── docker/                 # Configurations Docker
├── docs/                   # Documentation pédagogique
├── tests/                  # Tests
│   ├── integration/
│   └── load/
├── scripts/                # Scripts utilitaires
├── docker-compose.yml
├── Makefile
└── README.md
```

---

## Versions et Tags

| Tag | Phase | Description |
|-----|-------|-------------|
| `v1.0-infra` | 1 | Infrastructure de base |
| `v2.0-pubsub` | 2 | Patron Producteur/Consommateur |
| `v3.0-eventsourcing` | 3 | Event Sourcing |
| `v4.0-cqrs` | 4 | CQRS |
| `v5.0-saga` | 5 | Saga Choreography |
| `v6.0-dlq` | 6 | Dead Letter Queue |
| `v7.0-final` | 7 | Version finale |

Pour naviguer entre les versions :

```bash
git checkout v2.0-pubsub
```

---

## Troubleshooting

### Docker ne démarre pas

1. Vérifier que Docker Desktop est lancé
2. Vérifier les ressources allouées (8 Go RAM minimum)
3. Exécuter `docker-compose down -v` puis `docker-compose up -d`

### Kafka ne démarre pas

1. Vérifier les logs : `make logs-kafka`
2. Supprimer les volumes : `docker-compose down -v`
3. Redémarrer : `docker-compose up -d`

### Port déjà utilisé

1. Identifier le processus : `netstat -ano | findstr :PORT`
2. Modifier le port dans `.env`
3. Ou arrêter le processus conflictuel

---

## Documentation

La documentation pédagogique est disponible dans le dossier `docs/` :

- [Introduction](docs/00-introduction.md)
- [Producteur/Consommateur](docs/01-producteur-consommateur/README.md)
- [Event Sourcing](docs/02-event-sourcing/README.md)
- [CQRS](docs/03-cqrs/README.md)
- [Saga Choreography](docs/04-saga-choreography/README.md)
- [Dead Letter Queue](docs/05-dead-letter-queue/README.md)

---

## Licence

Projet académique - Usage éducatif

---

*Généré avec Claude Code*
