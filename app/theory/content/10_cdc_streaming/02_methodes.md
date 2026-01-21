# Méthodes de Change Data Capture

## Vue d'ensemble des méthodes

```
┌─────────────────────────────────────────────────┐
│           MÉTHODES DE CAPTURE CDC               │
├─────────────────────────────────────────────────┤
│                                                  │
│  1. Log-based CDC (Transaction Log)              │
│     └─ Lit le journal de transactions           │
│                                                  │
│  2. Trigger-based CDC                            │
│     └─ Triggers sur INSERT/UPDATE/DELETE        │
│                                                  │
│  3. Timestamp-based CDC                          │
│     └─ Colonne updated_at                       │
│                                                  │
│  4. Diff-based CDC                               │
│     └─ Comparaison snapshots                    │
│                                                  │
└─────────────────────────────────────────────────┘
```

## 1. Log-based CDC

La méthode la plus performante et non-intrusive.

```
┌───────────────────────────────────────────────┐
│               LOG-BASED CDC                    │
├───────────────────────────────────────────────┤
│                                                │
│  ┌─────────────┐     ┌─────────────┐          │
│  │  Database   │     │  Transaction│          │
│  │  (Source)   │────▶│     Log     │          │
│  │             │     │   (WAL)     │          │
│  └─────────────┘     └──────┬──────┘          │
│                             │                  │
│                     ┌───────▼───────┐          │
│                     │  CDC Connector│          │
│                     │  (Debezium)   │          │
│                     └───────┬───────┘          │
│                             │                  │
│                     ┌───────▼───────┐          │
│                     │ Message Broker│          │
│                     │   (Kafka)     │          │
│                     └───────────────┘          │
│                                                │
│  Avantages :                                   │
│  • Zéro impact sur la source                   │
│  • Capture toutes les opérations               │
│  • Capture l'ordre exact                       │
│  • Supporte les transactions                   │
│                                                │
│  Inconvénients :                               │
│  • Setup complexe                              │
│  • Dépend du SGBD                              │
│                                                │
└───────────────────────────────────────────────┘
```

### Support par base de données

| Base | Log | Outil CDC |
|------|-----|-----------|
| **PostgreSQL** | WAL (Write-Ahead Log) | Debezium |
| **MySQL** | Binlog | Debezium |
| **SQL Server** | Transaction Log | Debezium, Native CDC |
| **Oracle** | Redo Log | Oracle GoldenGate, Debezium |
| **MongoDB** | Oplog | Debezium |

## 2. Trigger-based CDC

```sql
-- Exemple de trigger CDC
CREATE TABLE cdc_changes (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100),
    operation VARCHAR(10),
    old_data JSON,
    new_data JSON,
    changed_at TIMESTAMP DEFAULT NOW()
);

CREATE TRIGGER trg_policies_cdc
AFTER INSERT OR UPDATE OR DELETE ON policies
FOR EACH ROW
EXECUTE FUNCTION capture_change();

CREATE FUNCTION capture_change() RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO cdc_changes (table_name, operation, old_data, new_data)
    VALUES (
        TG_TABLE_NAME,
        TG_OP,
        row_to_json(OLD),
        row_to_json(NEW)
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

| Avantages | Inconvénients |
|-----------|---------------|
| Simple à implémenter | Impact performance (overhead) |
| Fonctionne sur tous SGBD | Maintenance des triggers |
| Contrôle granulaire | Ne capture pas les bulk operations |

## 3. Timestamp-based CDC

```sql
-- Schéma avec timestamp
CREATE TABLE policies (
    id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20),
    premium DECIMAL(10,2),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index sur updated_at pour performance
CREATE INDEX idx_policies_updated ON policies(updated_at);

-- Requête CDC
SELECT * FROM policies
WHERE updated_at > :last_sync_timestamp
ORDER BY updated_at;
```

| Avantages | Inconvénients |
|-----------|---------------|
| Très simple | Ne capture pas les DELETE |
| Aucune infrastructure | Requiert colonne timestamp |
| Facile à déboguer | Manque les opérations rapides |

## 4. Diff-based CDC

```
┌─────────────────────────────────────────────────┐
│              DIFF-BASED CDC                      │
├─────────────────────────────────────────────────┤
│                                                  │
│  Snapshot T1          Snapshot T2               │
│  ───────────          ───────────               │
│  A: {v1}             A: {v2}      → UPDATE      │
│  B: {v1}             B: {v1}      → (no change) │
│  C: {v1}             (absent)     → DELETE      │
│  (absent)            D: {v1}      → INSERT      │
│                                                  │
│  Processus :                                     │
│  1. Snapshot complet de la source               │
│  2. Comparaison avec snapshot précédent         │
│  3. Identification des différences              │
│  4. Génération des événements de changement     │
│                                                  │
└─────────────────────────────────────────────────┘
```

## Comparatif des méthodes

| Méthode | Performance | Complexité | Exhaustivité | Cas d'usage |
|---------|-------------|------------|--------------|-------------|
| **Log-based** | ⭐⭐⭐ | ⭐ | ⭐⭐⭐ | Production, temps réel |
| **Trigger** | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ | Petits volumes |
| **Timestamp** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ | Sync simple |
| **Diff** | ⭐ | ⭐⭐ | ⭐⭐ | Legacy, batch |
