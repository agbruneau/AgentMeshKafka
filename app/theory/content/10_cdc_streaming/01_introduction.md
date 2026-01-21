# CDC et Streaming de Données

## Introduction au Change Data Capture

Le **CDC** (Change Data Capture) est une technique qui capture les changements de données en temps réel ou quasi temps réel, permettant une synchronisation continue entre systèmes.

## Pourquoi le CDC ?

### Limites de l'ETL batch

```
┌─────────────────────────────────────────────────┐
│            ETL BATCH vs CDC                      │
├─────────────────────────────────────────────────┤
│                                                  │
│  ETL Batch (T+1)                                │
│  ═══════════════                                │
│  Source ──[nuit]──▶ DWH                         │
│  • Latence: heures                              │
│  • Données: état à T-1                          │
│  • Charge: pic nocturne                         │
│                                                  │
│  CDC (temps réel)                               │
│  ════════════════                               │
│  Source ──[continu]──▶ DWH                      │
│  • Latence: secondes                            │
│  • Données: à jour                              │
│  • Charge: répartie                             │
│                                                  │
└─────────────────────────────────────────────────┘
```

### Cas d'usage

| Cas d'usage | Besoin | Solution CDC |
|-------------|--------|--------------|
| **Reporting temps réel** | Dashboards à jour | CDC → Data Warehouse |
| **Sync systèmes** | Cohérence inter-systèmes | CDC → Event Bus |
| **Audit trail** | Historique complet | CDC → Event Store |
| **Cache invalidation** | Cache à jour | CDC → Cache service |
| **Microservices** | Database per Service | CDC → Event propagation |

## Architecture CDC

```
┌─────────────────────────────────────────────────┐
│              ARCHITECTURE CDC                    │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐│
│  │  Source  │     │   CDC    │     │  Target  ││
│  │ Database │────▶│ Capture  │────▶│ Systems  ││
│  │          │     │ Engine   │     │          ││
│  └──────────┘     └──────────┘     └──────────┘│
│       │                │                        │
│       │                │                        │
│       ▼                ▼                        │
│  Transaction      Change Events                 │
│  Log (WAL)       (INSERT/UPDATE/DELETE)        │
│                                                  │
└─────────────────────────────────────────────────┘
```

## Types de changements capturés

| Opération | Description | Event Type |
|-----------|-------------|------------|
| **INSERT** | Nouvelle ligne | `create` |
| **UPDATE** | Modification | `update` (before + after) |
| **DELETE** | Suppression | `delete` (before state) |
| **TRUNCATE** | Vidage table | `truncate` |
| **DDL** | Changement schéma | `schema_change` |

## Format d'un événement CDC

```json
{
  "id": "CDC-001",
  "table": "policies",
  "operation": "UPDATE",
  "timestamp": "2024-01-15T10:30:00Z",
  "sequence": 12345,
  "before": {
    "id": "POL001",
    "status": "DRAFT",
    "premium": 800.00
  },
  "after": {
    "id": "POL001",
    "status": "ACTIVE",
    "premium": 850.00
  },
  "primary_key": {"id": "POL001"}
}
```

## Avantages du CDC

1. **Latence minimale** : Changements propagés en secondes
2. **Charge réduite** : Pas de full scan, uniquement les deltas
3. **Historique complet** : Capture de tous les états intermédiaires
4. **Découplage** : Source ignorante des consommateurs
5. **Scalabilité** : Distribution via message brokers
