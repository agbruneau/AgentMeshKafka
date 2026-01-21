# Phase Transform - Transformation des données

## Objectifs de la transformation

La phase Transform applique les règles métier et techniques pour convertir les données brutes en données exploitables.

## Types de transformations

### 1. Nettoyage (Data Cleansing)

```
Données brutes                      Données nettoyées
─────────────                       ─────────────────
"  Jean DUPONT "          ──▶       "Jean Dupont"
"jean@email"              ──▶       NULL (invalide)
"01/15/2024"              ──▶       "2024-01-15"
"M" / "Masculin" / "H"    ──▶       "M"
```

| Opération | Description | Exemple |
|-----------|-------------|---------|
| **Trim** | Suppression espaces | "  texte  " → "texte" |
| **Case** | Normalisation casse | "DUPONT" → "Dupont" |
| **Null handling** | Gestion valeurs nulles | NULL → valeur par défaut |
| **Type casting** | Conversion types | "123" → 123 |
| **Date parsing** | Standardisation dates | "15/01/24" → "2024-01-15" |

### 2. Validation

```python
# Règles de validation
validation_rules = {
    "email": {
        "pattern": r"^[\w.-]+@[\w.-]+\.\w+$",
        "action": "quarantine"  # reject | quarantine | default
    },
    "premium": {
        "range": (0, 100000),
        "action": "reject"
    },
    "policy_status": {
        "allowed": ["ACTIVE", "CANCELLED", "EXPIRED"],
        "action": "default",
        "default_value": "UNKNOWN"
    }
}
```

### 3. Enrichissement

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Données   │     │   Données   │     │   Données   │
│   sources   │  +  │ référence   │  =  │  enrichies  │
│             │     │             │     │             │
│ customer_id │     │ Région      │     │ + région    │
│ postal_code │     │ Segment     │     │ + segment   │
│             │     │             │     │ + scoring   │
└─────────────┘     └─────────────┘     └─────────────┘
```

### 4. Agrégation

```sql
-- Agrégation des sinistres par police
SELECT
    policy_id,
    COUNT(*) as claim_count,
    SUM(amount) as total_amount,
    AVG(amount) as avg_amount,
    MAX(date) as last_claim_date
FROM claims
GROUP BY policy_id
```

### 5. Jointures et dénormalisation

```
┌─────────────┐                      ┌──────────────────┐
│  POLICIES   │                      │   FACT_POLICIES  │
├─────────────┤                      ├──────────────────┤
│ policy_id   │──┐                   │ policy_id        │
│ customer_id │  │                   │ customer_name    │
│ product_id  │  │  Dénormalisation  │ customer_segment │
└─────────────┘  │  ═══════════════▶ │ product_name     │
                 │                   │ product_category │
┌─────────────┐  │                   │ premium          │
│  CUSTOMERS  │  │                   │ start_date       │
├─────────────┤──┘                   └──────────────────┘
│ customer_id │
│ name        │
│ segment     │
└─────────────┘
```

## Slowly Changing Dimensions (SCD)

Les SCD gèrent l'historisation des changements dans les dimensions.

### Type 1 : Écrasement

```sql
-- Nouvelle valeur écrase l'ancienne
UPDATE dim_customer SET segment = 'PREMIUM' WHERE id = 1
```

### Type 2 : Historisation complète

```
customer_id | name   | segment  | valid_from | valid_to   | is_current
────────────┼────────┼──────────┼────────────┼────────────┼───────────
1           | Dupont | STANDARD | 2023-01-01 | 2024-01-15 | false
1           | Dupont | PREMIUM  | 2024-01-15 | 9999-12-31 | true
```

### Type 3 : Valeur précédente

```
customer_id | name   | current_segment | previous_segment
────────────┼────────┼─────────────────┼─────────────────
1           | Dupont | PREMIUM         | STANDARD
```

## Best Practices

1. **Idempotence** : Même résultat si exécuté plusieurs fois
2. **Logging** : Tracer toutes les transformations
3. **Validation en amont** : Rejeter tôt les données invalides
4. **Tests unitaires** : Valider chaque règle de transformation
