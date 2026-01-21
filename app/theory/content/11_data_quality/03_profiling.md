# Data Profiling

## Qu'est-ce que le Data Profiling ?

Le **Data Profiling** est l'analyse exploratoire des données pour comprendre leur structure, contenu et qualité avant tout traitement.

## Objectifs du profiling

```
┌─────────────────────────────────────────────────┐
│         OBJECTIFS DU DATA PROFILING             │
├─────────────────────────────────────────────────┤
│                                                  │
│  1. DÉCOUVERTE                                   │
│     • Structure des données                     │
│     • Types de colonnes                         │
│     • Cardinalité                               │
│                                                  │
│  2. ÉVALUATION                                   │
│     • Taux de complétude                        │
│     • Distribution des valeurs                  │
│     • Détection d'anomalies                     │
│                                                  │
│  3. DOCUMENTATION                                │
│     • Métadonnées                               │
│     • Dictionnaire de données                   │
│     • Règles métier identifiées                 │
│                                                  │
└─────────────────────────────────────────────────┘
```

## Types de profiling

### 1. Column Profiling (par colonne)

```
┌─────────────────────────────────────────────────┐
│        PROFIL COLONNE: customers.email          │
├─────────────────────────────────────────────────┤
│                                                  │
│  Statistiques générales                          │
│  ─────────────────────                           │
│  Total records:        10,000                    │
│  Non-null count:       9,523 (95.23%)           │
│  Null count:           477 (4.77%)              │
│  Distinct values:      9,498                    │
│  Unique values:        9,480                    │
│  Duplicate values:     18                       │
│                                                  │
│  Pattern analysis                                │
│  ────────────────                                │
│  Pattern              Count    %                 │
│  xxx@xxx.com          7,234    76.0%            │
│  xxx@xxx.fr           1,891    19.9%            │
│  xxx@xxx.org          312      3.3%             │
│  Invalid              86       0.9%             │
│                                                  │
│  Top 5 domains                                   │
│  ─────────────                                   │
│  gmail.com            3,421    35.9%            │
│  yahoo.fr             1,234    13.0%            │
│  orange.fr            987      10.4%            │
│  hotmail.com          765      8.0%             │
│  outlook.com          543      5.7%             │
│                                                  │
└─────────────────────────────────────────────────┘
```

### 2. Table Profiling (niveau table)

```
┌─────────────────────────────────────────────────┐
│          PROFIL TABLE: policies                  │
├─────────────────────────────────────────────────┤
│                                                  │
│  Structure                                       │
│  ─────────                                       │
│  Columns:         12                             │
│  Rows:            50,000                         │
│  Size:            15.2 MB                        │
│                                                  │
│  Colonnes                                        │
│  ────────                                        │
│  ┌────────────────────────────────────────────┐ │
│  │ Column      │ Type    │ Null% │ Distinct  │ │
│  ├────────────────────────────────────────────┤ │
│  │ id          │ VARCHAR │ 0%    │ 50,000    │ │
│  │ customer_id │ VARCHAR │ 0%    │ 32,000    │ │
│  │ type        │ VARCHAR │ 0%    │ 3         │ │
│  │ premium     │ DECIMAL │ 0%    │ 4,523     │ │
│  │ status      │ VARCHAR │ 0%    │ 4         │ │
│  │ start_date  │ DATE    │ 0%    │ 365       │ │
│  │ end_date    │ DATE    │ 2%    │ 370       │ │
│  │ created_at  │ DATETIME│ 0%    │ 45,000    │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
└─────────────────────────────────────────────────┘
```

### 3. Cross-column Profiling (relations)

```
┌─────────────────────────────────────────────────┐
│        ANALYSE RELATIONS ENTRE COLONNES         │
├─────────────────────────────────────────────────┤
│                                                  │
│  Corrélations détectées                          │
│  ─────────────────────                           │
│  • customer_id → policies (1:N)                 │
│  • policy_id → claims (1:N)                     │
│  • policy_id → invoices (1:N)                   │
│                                                  │
│  Règles fonctionnelles découvertes               │
│  ─────────────────────────────────               │
│  • IF type = 'AUTO' THEN premium IN [200-5000]  │
│  • IF type = 'HOME' THEN premium IN [300-8000]  │
│  • IF status = 'ACTIVE' THEN end_date > NOW()   │
│                                                  │
│  Anomalies cross-column                          │
│  ─────────────────────                           │
│  • 23 polices: start_date > end_date            │
│  • 5 polices: status='ACTIVE' mais end_date<NOW│
│                                                  │
└─────────────────────────────────────────────────┘
```

## Statistiques de profiling

### Numériques

```python
# Métriques pour colonnes numériques
{
    "min": 200.00,
    "max": 15000.00,
    "mean": 850.45,
    "median": 720.00,
    "std_dev": 534.23,
    "q1": 450.00,      # 25th percentile
    "q3": 1100.00,     # 75th percentile
    "outliers": 45,    # Hors IQR × 1.5
    "zeros": 0,
    "negatives": 0
}
```

### Textuelles

```python
# Métriques pour colonnes texte
{
    "min_length": 2,
    "max_length": 150,
    "avg_length": 24.5,
    "empty_strings": 12,
    "patterns": [
        {"pattern": "^[A-Z][a-z]+$", "count": 8500},
        {"pattern": "^[A-Z]+$", "count": 1200}
    ],
    "top_values": [
        {"value": "Dupont", "count": 234},
        {"value": "Martin", "count": 198}
    ]
}
```

### Dates

```python
# Métriques pour colonnes date
{
    "min_date": "2020-01-01",
    "max_date": "2024-12-31",
    "most_common_day": "Monday",
    "most_common_month": "January",
    "future_dates": 12,    # Anomalie potentielle
    "null_dates": 45
}
```

## Workflow de profiling

```
┌─────────────────────────────────────────────────┐
│           WORKFLOW DATA PROFILING               │
├─────────────────────────────────────────────────┤
│                                                  │
│  1. CONNEXION                                    │
│     └─ Accès aux sources de données             │
│                                                  │
│  2. SCAN                                         │
│     └─ Analyse automatique de toutes colonnes   │
│                                                  │
│  3. ANALYSE                                      │
│     └─ Calcul statistiques et patterns          │
│                                                  │
│  4. RAPPORT                                      │
│     └─ Génération profil complet                │
│                                                  │
│  5. RÈGLES                                       │
│     └─ Définition des seuils de qualité         │
│                                                  │
│  6. MONITORING                                   │
│     └─ Suivi continu des métriques              │
│                                                  │
└─────────────────────────────────────────────────┘
```

## Outils de profiling

| Outil | Type | Usage |
|-------|------|-------|
| **Great Expectations** | Open Source | Python, Data Pipelines |
| **dbt tests** | Open Source | SQL, Analytics |
| **Pandas Profiling** | Open Source | Python, Exploration |
| **Informatica DQ** | Commercial | Enterprise |
| **Talend DQ** | Commercial | ETL intégré |
| **Monte Carlo** | SaaS | Data Observability |
