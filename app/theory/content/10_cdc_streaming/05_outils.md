# Outils et Technologies CDC/Streaming

## Apache Kafka

Le standard de facto pour le streaming de données en entreprise.

```
┌─────────────────────────────────────────────────┐
│              ÉCOSYSTÈME KAFKA                    │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌─────────────────────────────────────────┐    │
│  │           KAFKA CLUSTER                  │    │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐   │    │
│  │  │ Broker 1│ │ Broker 2│ │ Broker 3│   │    │
│  │  └─────────┘ └─────────┘ └─────────┘   │    │
│  │                                         │    │
│  │  Topics: policies, claims, customers    │    │
│  └─────────────────────────────────────────┘    │
│                                                  │
│  Composants :                                   │
│  ├── Kafka Connect (intégration sources/sinks) │
│  ├── Kafka Streams (stream processing)         │
│  ├── ksqlDB (SQL sur streams)                  │
│  └── Schema Registry (gestion schémas)         │
│                                                  │
└─────────────────────────────────────────────────┘
```

### Caractéristiques clés

| Aspect | Spécification |
|--------|---------------|
| **Throughput** | Millions messages/sec |
| **Latence** | Milliseconds |
| **Rétention** | Configurable (jours, semaines) |
| **Réplication** | Factor configurable |
| **Partitioning** | Scalabilité horizontale |

## Debezium

Plateforme CDC open source qui capture les changements depuis les logs de transactions.

```
┌─────────────────────────────────────────────────┐
│              DEBEZIUM ARCHITECTURE              │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌───────────────────────────────────────────┐  │
│  │        DEBEZIUM CONNECTORS                │  │
│  │                                           │  │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  │  │
│  │  │ MySQL   │  │Postgres │  │  SQL    │  │  │
│  │  │Connector│  │Connector│  │ Server  │  │  │
│  │  └────┬────┘  └────┬────┘  └────┬────┘  │  │
│  │       │            │            │        │  │
│  │       └────────────┼────────────┘        │  │
│  │                    │                     │  │
│  │                    ▼                     │  │
│  │           ┌─────────────┐               │  │
│  │           │   Kafka     │               │  │
│  │           │   Connect   │               │  │
│  │           └──────┬──────┘               │  │
│  │                  │                       │  │
│  │                  ▼                       │  │
│  │           ┌─────────────┐               │  │
│  │           │   Kafka     │               │  │
│  │           │   Cluster   │               │  │
│  │           └─────────────┘               │  │
│  └───────────────────────────────────────────┘  │
│                                                  │
└─────────────────────────────────────────────────┘
```

### Configuration Debezium

```json
{
  "name": "policies-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "db.example.com",
    "database.port": "5432",
    "database.user": "debezium",
    "database.password": "***",
    "database.dbname": "insurance",
    "table.include.list": "public.policies,public.claims",
    "topic.prefix": "cdc",
    "snapshot.mode": "initial"
  }
}
```

## Alternatives Cloud

### AWS

```
┌─────────────────────────────────────────────────┐
│              AWS STREAMING STACK                │
├─────────────────────────────────────────────────┤
│                                                  │
│  Sources:                                        │
│  • DMS (Database Migration Service) - CDC       │
│  • Kinesis Data Streams                         │
│                                                  │
│  Processing:                                     │
│  • Kinesis Data Analytics (SQL/Flink)          │
│  • Lambda                                       │
│                                                  │
│  Sinks:                                         │
│  • Kinesis Firehose → S3/Redshift              │
│  • EventBridge                                  │
│                                                  │
└─────────────────────────────────────────────────┘
```

### Azure

```
┌─────────────────────────────────────────────────┐
│             AZURE STREAMING STACK               │
├─────────────────────────────────────────────────┤
│                                                  │
│  Sources:                                        │
│  • Azure Data Factory (CDC)                     │
│  • Event Hubs                                   │
│                                                  │
│  Processing:                                     │
│  • Azure Stream Analytics                       │
│  • Azure Functions                              │
│                                                  │
│  Sinks:                                         │
│  • Synapse Analytics                            │
│  • Cosmos DB                                    │
│                                                  │
└─────────────────────────────────────────────────┘
```

### GCP

```
┌─────────────────────────────────────────────────┐
│              GCP STREAMING STACK                │
├─────────────────────────────────────────────────┤
│                                                  │
│  Sources:                                        │
│  • Datastream (CDC)                             │
│  • Pub/Sub                                      │
│                                                  │
│  Processing:                                     │
│  • Dataflow (Apache Beam)                       │
│  • Cloud Functions                              │
│                                                  │
│  Sinks:                                         │
│  • BigQuery                                     │
│  • Cloud Storage                                │
│                                                  │
└─────────────────────────────────────────────────┘
```

## Comparatif outils CDC

| Outil | Type | Open Source | Cloud | Usage |
|-------|------|-------------|-------|-------|
| **Debezium** | Log-based | ✅ | ❌ | Standard open source |
| **Kafka Connect** | Framework | ✅ | ❌ | Intégration Kafka |
| **AWS DMS** | Managed | ❌ | AWS | Migration/CDC |
| **Azure Data Factory** | Managed | ❌ | Azure | ETL/CDC |
| **GCP Datastream** | Managed | ❌ | GCP | CDC temps réel |
| **Fivetran** | SaaS | ❌ | Multi | CDC as a Service |
| **Airbyte** | ELT | ✅ | Multi | Alternative Fivetran |

## Choix technologique

```
Critères de décision :
├── Volume de données → Kafka si > millions/jour
├── Latence requise → Log-based si < seconds
├── Compétences équipe → Cloud managed si DevOps limité
├── Budget → Open source si contraintes
└── Écosystème existant → Cohérence avec stack
```
