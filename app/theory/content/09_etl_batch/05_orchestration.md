# Orchestration des Pipelines ETL

## Concepts d'orchestration

L'orchestration gère l'exécution coordonnée des jobs ETL : planification, dépendances, monitoring et gestion des erreurs.

## DAG (Directed Acyclic Graph)

Un pipeline ETL est généralement représenté comme un graphe orienté acyclique.

```
                    ┌─────────────┐
                    │   START     │
                    └──────┬──────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
    ┌───────────┐    ┌───────────┐    ┌───────────┐
    │  Extract  │    │  Extract  │    │  Extract  │
    │ Customers │    │ Policies  │    │  Claims   │
    └─────┬─────┘    └─────┬─────┘    └─────┬─────┘
          │                │                │
          └────────────────┼────────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  Transform  │
                    │   & Join    │
                    └──────┬──────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
    ┌───────────┐    ┌───────────┐    ┌───────────┐
    │   Load    │    │   Load    │    │   Load    │
    │    DWH    │    │  DataMart │    │ Reporting │
    └───────────┘    └───────────┘    └───────────┘
```

## Planification (Scheduling)

### Types de déclencheurs

| Type | Description | Exemple |
|------|-------------|---------|
| **Time-based** | Cron expression | `0 2 * * *` (2h du matin) |
| **Event-based** | Sur événement | Fichier déposé, API appelée |
| **Dependency** | Fin d'un autre job | Job B après Job A |
| **Manual** | Déclenchement manuel | À la demande |

### Expressions Cron

```
┌───────────── minute (0-59)
│ ┌─────────── heure (0-23)
│ │ ┌───────── jour du mois (1-31)
│ │ │ ┌─────── mois (1-12)
│ │ │ │ ┌───── jour de la semaine (0-6)
│ │ │ │ │
* * * * *

Exemples :
0 2 * * *     → Tous les jours à 2h
0 */4 * * *   → Toutes les 4 heures
0 0 1 * *     → Le 1er de chaque mois
0 6 * * 1-5   → 6h, du lundi au vendredi
```

## Gestion des dépendances

```python
# Pseudo-code définition de dépendances
pipeline = Pipeline("daily_etl")

extract_customers = Task("extract_customers")
extract_policies = Task("extract_policies")
transform = Task("transform_data")
load = Task("load_dwh")

# Définition des dépendances
transform.depends_on(extract_customers)
transform.depends_on(extract_policies)
load.depends_on(transform)

pipeline.add_tasks([
    extract_customers,
    extract_policies,
    transform,
    load
])
```

## États des jobs

```
┌─────────────────────────────────────────────────┐
│            CYCLE DE VIE D'UN JOB                │
├─────────────────────────────────────────────────┤
│                                                  │
│  PENDING ──▶ RUNNING ──▶ SUCCESS                │
│     │           │                               │
│     │           ▼                               │
│     │       FAILED ──▶ RETRY ──▶ RUNNING        │
│     │           │                               │
│     ▼           ▼                               │
│  SKIPPED    CANCELLED                           │
│                                                  │
└─────────────────────────────────────────────────┘
```

## Monitoring et alerting

### Métriques clés

| Métrique | Description | Seuil d'alerte |
|----------|-------------|----------------|
| **Duration** | Temps d'exécution | > 2x moyenne |
| **Records** | Volume traité | < 80% attendu |
| **Errors** | Nombre d'erreurs | > 1% rejetés |
| **SLA** | Heure de fin | Après 6h du matin |

### Dashboard

```
┌─────────────────────────────────────────────────┐
│            ETL MONITORING DASHBOARD              │
├─────────────────────────────────────────────────┤
│                                                  │
│  Jobs Today: 12/15    Success Rate: 93%         │
│                                                  │
│  ┌─────────────────────────────────────────┐    │
│  │ Job Name          Status    Duration    │    │
│  ├─────────────────────────────────────────┤    │
│  │ daily_customers   ✅ OK     00:12:34    │    │
│  │ daily_policies    ✅ OK     00:23:45    │    │
│  │ daily_claims      ⚠️ SLOW   01:45:00    │    │
│  │ daily_billing     ❌ FAILED  --:--:--   │    │
│  └─────────────────────────────────────────┘    │
│                                                  │
│  Alertes actives: 1                              │
│  • daily_billing a échoué à 03:45               │
│                                                  │
└─────────────────────────────────────────────────┘
```

## Backfill et Rejeu

```
Backfill = Exécution pour des dates passées

Cas d'usage :
• Correction d'un bug de transformation
• Ajout d'une nouvelle source
• Recalcul après correction de données

Commande type :
> run_etl --start-date 2024-01-01 --end-date 2024-01-31
```

## Outils d'orchestration

| Outil | Type | Usage |
|-------|------|-------|
| **Apache Airflow** | Open source | Standard industrie |
| **dbt** | Transform-focused | Modern data stack |
| **Azure Data Factory** | Cloud managed | Écosystème Azure |
| **AWS Step Functions** | Serverless | Écosystème AWS |
| **Prefect** | Modern Python | Alternative Airflow |
