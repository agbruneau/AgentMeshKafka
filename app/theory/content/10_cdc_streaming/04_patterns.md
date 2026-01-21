# Patterns CDC et Streaming

## 1. Outbox Pattern (revisité)

Le pattern Outbox garantit la cohérence entre les modifications en base et la publication d'événements.

```
┌─────────────────────────────────────────────────┐
│              OUTBOX PATTERN + CDC               │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌─────────────┐                                │
│  │ Application │                                │
│  └──────┬──────┘                                │
│         │ Transaction                           │
│         │                                       │
│  ┌──────▼──────────────────────────────┐       │
│  │           DATABASE                   │       │
│  │  ┌────────────┐  ┌────────────────┐ │       │
│  │  │  POLICIES  │  │    OUTBOX      │ │       │
│  │  │  (table)   │  │    (table)     │ │       │
│  │  └────────────┘  └───────┬────────┘ │       │
│  └──────────────────────────│──────────┘       │
│                             │                   │
│                     ┌───────▼───────┐           │
│                     │  CDC Capture  │           │
│                     │  (Debezium)   │           │
│                     └───────┬───────┘           │
│                             │                   │
│                     ┌───────▼───────┐           │
│                     │ Message Broker│           │
│                     └───────────────┘           │
│                                                  │
│  Atomicité garantie :                            │
│  • Commit DB = Event publié                     │
│  • Rollback DB = Pas d'event                    │
│                                                  │
└─────────────────────────────────────────────────┘
```

## 2. Event Sourcing avec CDC

```
┌─────────────────────────────────────────────────┐
│         EVENT SOURCING + CDC REPLAY             │
├─────────────────────────────────────────────────┤
│                                                  │
│  Command ──▶ Event Store ──▶ CDC ──▶ Projections│
│                                                  │
│  Event Store (source of truth)                   │
│  ├── PolicyCreated                              │
│  ├── PolicyUpdated                              │
│  ├── PremiumChanged                             │
│  └── PolicyCancelled                            │
│                                                  │
│  CDC capture tous les événements                │
│        │                                        │
│        ├──▶ Read Model (requêtes)               │
│        ├──▶ Analytics (reporting)               │
│        ├──▶ Notification (alertes)              │
│        └──▶ Audit (compliance)                  │
│                                                  │
│  Replay possible :                               │
│  • Reconstruction de projections               │
│  • Migration de données                         │
│  • Debugging temporel                           │
│                                                  │
└─────────────────────────────────────────────────┘
```

## 3. Database per Service avec CDC

```
┌─────────────────────────────────────────────────┐
│       MICROSERVICES DATA SYNC via CDC           │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────────┐         ┌──────────────┐     │
│  │   Policy     │         │   Claims     │     │
│  │   Service    │         │   Service    │     │
│  └──────┬───────┘         └───────┬──────┘     │
│         │                         │             │
│  ┌──────▼───────┐         ┌───────▼──────┐     │
│  │   Policy     │         │   Claims     │     │
│  │   Database   │         │   Database   │     │
│  └──────┬───────┘         └───────┬──────┘     │
│         │                         │             │
│         │   CDC                   │   CDC       │
│         │                         │             │
│         └─────────┬───────────────┘             │
│                   │                             │
│           ┌───────▼───────┐                     │
│           │ Message Broker │                    │
│           └───────┬───────┘                     │
│                   │                             │
│         ┌─────────┼─────────┐                   │
│         │         │         │                   │
│         ▼         ▼         ▼                   │
│   [Policy     [Claims    [Reporting             │
│    Replica]   Enriched]  Aggregated]            │
│                                                  │
└─────────────────────────────────────────────────┘
```

## 4. CQRS avec CDC

```
┌─────────────────────────────────────────────────┐
│              CQRS + CDC ARCHITECTURE            │
├─────────────────────────────────────────────────┤
│                                                  │
│          COMMANDS                QUERIES         │
│              │                       │          │
│              ▼                       │          │
│       ┌──────────┐                   │          │
│       │ Command  │                   │          │
│       │ Handler  │                   │          │
│       └────┬─────┘                   │          │
│            │                         │          │
│       ┌────▼─────┐              ┌────▼─────┐   │
│       │  Write   │    CDC       │   Read   │   │
│       │   DB     │─────────────▶│   DB     │   │
│       │(source)  │              │(replica) │   │
│       └──────────┘              └──────────┘   │
│                                                  │
│  Write DB : Optimisé écriture (normalized)      │
│  Read DB  : Optimisé lecture (denormalized)     │
│                                                  │
│  CDC maintient la synchronisation               │
│  • Latence milliseconds                         │
│  • Eventually consistent                         │
│                                                  │
└─────────────────────────────────────────────────┘
```

## 5. Audit Trail automatique

```
┌─────────────────────────────────────────────────┐
│           AUDIT TRAIL via CDC                    │
├─────────────────────────────────────────────────┤
│                                                  │
│  Application ──▶ Database ──▶ CDC ──▶ Audit Log │
│                                                  │
│  CDC Event:                                      │
│  {                                               │
│    "table": "policies",                          │
│    "operation": "UPDATE",                        │
│    "timestamp": "2024-01-15T10:30:00Z",         │
│    "user": "agent_123",                         │
│    "before": {"status": "DRAFT"},               │
│    "after": {"status": "ACTIVE"}                │
│  }                                               │
│                                                  │
│  Audit Log:                                      │
│  • Who: agent_123                               │
│  • What: Changed policy status                  │
│  • When: 2024-01-15T10:30:00Z                   │
│  • Before/After: Full state captured            │
│                                                  │
│  Compliance :                                    │
│  • RGPD : Traçabilité accès données            │
│  • SOX : Audit trail financier                  │
│  • Solvency II : Historique polices            │
│                                                  │
└─────────────────────────────────────────────────┘
```

## Best Practices

1. **Idempotence** : Consommateurs doivent gérer les duplications
2. **Ordering** : Utiliser clé de partition pour garantir l'ordre
3. **Schema Evolution** : Gérer les changements de schéma (Avro, Protobuf)
4. **Monitoring** : Surveiller lag des consommateurs
5. **Dead Letter** : Prévoir queue pour messages non traitables
