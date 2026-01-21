# Streaming de Données

## Introduction au Data Streaming

Le **Data Streaming** traite les données en flux continu, par opposition au traitement batch. Les événements CDC sont naturellement consommés en mode streaming.

## Architecture de Streaming

```
┌─────────────────────────────────────────────────────────┐
│              ARCHITECTURE STREAMING                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  PRODUCTEURS          BROKER           CONSOMMATEURS    │
│                                                          │
│  ┌─────────┐       ┌─────────┐       ┌─────────┐       │
│  │   CDC   │──────▶│         │──────▶│   DWH   │       │
│  │ Capture │       │         │       │  Loader │       │
│  └─────────┘       │         │       └─────────┘       │
│                    │  KAFKA  │                          │
│  ┌─────────┐       │   ou    │       ┌─────────┐       │
│  │   App   │──────▶│  BROKER │──────▶│Analytics│       │
│  │ Events  │       │         │       │ Engine  │       │
│  └─────────┘       │         │       └─────────┘       │
│                    │         │                          │
│  ┌─────────┐       │         │       ┌─────────┐       │
│  │   IoT   │──────▶│         │──────▶│ Alerting│       │
│  │ Sensors │       │         │       │ Service │       │
│  └─────────┘       └─────────┘       └─────────┘       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Concepts clés

### Topics et Partitions

```
┌─────────────────────────────────────────────────┐
│              TOPIC: policies.changes             │
├─────────────────────────────────────────────────┤
│                                                  │
│  Partition 0: [msg1] [msg4] [msg7] [msg10]      │
│  Partition 1: [msg2] [msg5] [msg8] [msg11]      │
│  Partition 2: [msg3] [msg6] [msg9] [msg12]      │
│                                                  │
│  Partitionnement par clé :                       │
│  • policy_id hash → partition                   │
│  • Garantit l'ordre par police                  │
│                                                  │
└─────────────────────────────────────────────────┘
```

### Consumer Groups

```
┌─────────────────────────────────────────────────┐
│             CONSUMER GROUPS                      │
├─────────────────────────────────────────────────┤
│                                                  │
│  Topic: policies.changes (3 partitions)          │
│                                                  │
│  Consumer Group A (DWH Loader)                   │
│  ├── Consumer 1 ← Partition 0                   │
│  ├── Consumer 2 ← Partition 1                   │
│  └── Consumer 3 ← Partition 2                   │
│                                                  │
│  Consumer Group B (Alerting)                     │
│  └── Consumer 1 ← Partitions 0,1,2              │
│                                                  │
│  → Chaque groupe reçoit tous les messages       │
│  → Au sein d'un groupe, parallélisation          │
│                                                  │
└─────────────────────────────────────────────────┘
```

## Modèles de traitement

### 1. At-most-once (au plus une fois)

```
Producer ──▶ Broker ──▶ Consumer
           ack avant
           traitement

Risque : Perte de message si crash après ack
Usage : Logs, métriques non critiques
```

### 2. At-least-once (au moins une fois)

```
Producer ──▶ Broker ──▶ Consumer
                      ack après
                      traitement

Risque : Duplication si crash après traitement
Usage : Cas où idempotence garantie
```

### 3. Exactly-once (exactement une fois)

```
Producer ──▶ Broker ──▶ Consumer
          Transaction
          atomique

Complexité : Haute, requiert support broker
Usage : Transactions financières
```

## Windowing (Fenêtrage)

Le fenêtrage permet d'agréger les événements sur des intervalles de temps.

```
┌─────────────────────────────────────────────────┐
│              TYPES DE FENÊTRES                   │
├─────────────────────────────────────────────────┤
│                                                  │
│  TUMBLING (fixes, sans chevauchement)            │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐                    │
│  │ W1 │ │ W2 │ │ W3 │ │ W4 │                    │
│  └────┘ └────┘ └────┘ └────┘                    │
│  |-----|-----|-----|-----|                      │
│  0     5     10    15    20 (minutes)           │
│                                                  │
│  HOPPING (avec chevauchement)                   │
│  ┌──────────┐                                   │
│  │    W1    │                                   │
│  └──────────┘                                   │
│       ┌──────────┐                              │
│       │    W2    │                              │
│       └──────────┘                              │
│            ┌──────────┐                         │
│            │    W3    │                         │
│            └──────────┘                         │
│                                                  │
│  SLIDING (par événement)                         │
│  Fenêtre recalculée à chaque événement          │
│                                                  │
│  SESSION (par activité)                          │
│  ┌────────┐     ┌──────────────┐    ┌────┐     │
│  │ Sess 1 │     │    Sess 2    │    │Ses3│     │
│  └────────┘     └──────────────┘    └────┘     │
│     gap           gap                 gap       │
│                                                  │
└─────────────────────────────────────────────────┘
```

## Exemple : Agrégation temps réel

```python
# Pseudo-code stream processing
stream = kafka.consume("claims.events")

aggregated = (
    stream
    .filter(lambda e: e.operation == "INSERT")
    .window(tumbling=timedelta(minutes=5))
    .group_by("policy_id")
    .aggregate(
        count=count(),
        total_amount=sum("amount")
    )
)

aggregated.sink("claims.aggregated.5min")
```
