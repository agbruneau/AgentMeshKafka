# Phase Load - Chargement des données

## Stratégies de chargement

### 1. Insert (Append)

```sql
-- Ajout simple des nouvelles données
INSERT INTO fact_claims (claim_id, policy_id, amount, date)
SELECT claim_id, policy_id, amount, date
FROM stg_claims
```

**Usage** : Tables de faits, logs, événements

### 2. Truncate-Insert

```sql
-- Vidage puis rechargement complet
TRUNCATE TABLE dim_products;

INSERT INTO dim_products
SELECT * FROM stg_products;
```

**Usage** : Petites dimensions, données de référence

### 3. Upsert (Merge)

```sql
-- Insertion ou mise à jour selon existence
MERGE INTO dim_customers AS target
USING stg_customers AS source
ON target.customer_id = source.customer_id
WHEN MATCHED THEN
    UPDATE SET
        name = source.name,
        segment = source.segment,
        updated_at = CURRENT_TIMESTAMP
WHEN NOT MATCHED THEN
    INSERT (customer_id, name, segment)
    VALUES (source.customer_id, source.name, source.segment);
```

**Usage** : Dimensions, données de référence évolutives

### 4. Delete-Insert

```sql
-- Suppression puis réinsertion
DELETE FROM fact_daily_metrics
WHERE date = :processing_date;

INSERT INTO fact_daily_metrics
SELECT * FROM stg_daily_metrics
WHERE date = :processing_date;
```

**Usage** : Données recalculables, partitions

## Optimisation du chargement

### Bulk Loading

```
┌─────────────────────────────────────────────────┐
│           TECHNIQUES DE BULK LOAD                │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌─────────────┐    ┌─────────────┐             │
│  │   INSERT    │    │    BULK     │             │
│  │  row by row │    │    LOAD     │             │
│  │  ~1000/sec  │    │ ~100000/sec │             │
│  └─────────────┘    └─────────────┘             │
│                                                  │
│  Optimisations :                                 │
│  • Désactivation des index pendant le load      │
│  • Désactivation des contraintes FK             │
│  • Chargement par partition                     │
│  • Parallel loading                             │
│                                                  │
└─────────────────────────────────────────────────┘
```

### Partitionnement

```
┌─────────────────────────────────────────────────┐
│               FACT_CLAIMS                        │
├─────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐              │
│  │ 2024-01     │  │ 2024-02     │  ...         │
│  │ (Partition) │  │ (Partition) │              │
│  └─────────────┘  └─────────────┘              │
│                                                  │
│  Avantages :                                     │
│  • Chargement ciblé par partition               │
│  • Purge facile des anciennes données           │
│  • Requêtes optimisées (partition pruning)      │
│                                                  │
└─────────────────────────────────────────────────┘
```

## Gestion des erreurs

### Error Handling Patterns

```
┌─────────────────────────────────────────────────┐
│         STRATÉGIES DE GESTION D'ERREURS         │
├─────────────────────────────────────────────────┤
│                                                  │
│  1. All-or-Nothing (Transaction)                 │
│     Tout réussit ou tout échoue                 │
│     → Données critiques                          │
│                                                  │
│  2. Skip-on-Error                                │
│     Continue malgré les erreurs                 │
│     → Logs, métriques                            │
│                                                  │
│  3. Quarantine                                   │
│     Isole les erreurs pour analyse              │
│     → Données à retraiter                        │
│                                                  │
└─────────────────────────────────────────────────┘
```

### Table de rejet

```sql
CREATE TABLE etl_rejected_records (
    id SERIAL PRIMARY KEY,
    source_table VARCHAR(100),
    record_data JSON,
    error_type VARCHAR(50),
    error_message TEXT,
    rejected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reprocessed BOOLEAN DEFAULT FALSE
);
```

## Vérification post-chargement

```sql
-- Contrôles de cohérence
-- 1. Comptage
SELECT COUNT(*) FROM fact_claims WHERE load_date = :today;

-- 2. Sommes de contrôle
SELECT SUM(amount) FROM fact_claims WHERE load_date = :today;

-- 3. Intégrité référentielle
SELECT COUNT(*) FROM fact_claims f
LEFT JOIN dim_policies p ON f.policy_id = p.policy_id
WHERE p.policy_id IS NULL;
```

## Notification de fin

```python
# Pseudo-code notification
def notify_load_complete(job_id, stats):
    message = {
        "job_id": job_id,
        "status": "completed",
        "records_loaded": stats["loaded"],
        "records_rejected": stats["rejected"],
        "duration_seconds": stats["duration"]
    }
    publish("etl.completed", message)
```
