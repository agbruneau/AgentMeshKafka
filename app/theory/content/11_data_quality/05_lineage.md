# Data Lineage

## Qu'est-ce que le Data Lineage ?

Le **Data Lineage** (lignage des données) trace le parcours des données depuis leur origine jusqu'à leur utilisation finale, à travers toutes les transformations.

## Pourquoi le Data Lineage ?

```
┌─────────────────────────────────────────────────┐
│          VALEUR DU DATA LINEAGE                 │
├─────────────────────────────────────────────────┤
│                                                  │
│  1. CONFORMITÉ RÉGLEMENTAIRE                     │
│     └─ "D'où viennent ces données ?"            │
│     └─ RGPD, SOX, Solvency II                   │
│                                                  │
│  2. IMPACT ANALYSIS                              │
│     └─ "Quoi impacte si je modifie X ?"         │
│     └─ Changements de schéma, migration         │
│                                                  │
│  3. ROOT CAUSE ANALYSIS                          │
│     └─ "Pourquoi ce chiffre est faux ?"         │
│     └─ Debugging, audit                         │
│                                                  │
│  4. DATA TRUST                                   │
│     └─ "Puis-je faire confiance ?"              │
│     └─ Transparence, documentation              │
│                                                  │
└─────────────────────────────────────────────────┘
```

## Types de Lineage

### Lineage technique

Trace les transformations au niveau système.

```
┌─────────────────────────────────────────────────┐
│           LINEAGE TECHNIQUE                      │
├─────────────────────────────────────────────────┤
│                                                  │
│  Source                Transformations    Target │
│  ──────                ───────────────    ────── │
│                                                  │
│  crm.customers ──┐                              │
│                  │                              │
│                  ├──▶ ETL_JOIN ──▶ dwh.dim_customer│
│                  │                              │
│  billing.accounts ┘                             │
│                                                  │
│  Métadonnées capturées :                         │
│  • Table/colonne source                         │
│  • Transformation appliquée                     │
│  • Table/colonne cible                          │
│  • Timestamp                                    │
│                                                  │
└─────────────────────────────────────────────────┘
```

### Lineage business

Trace le sens métier des données.

```
┌─────────────────────────────────────────────────┐
│           LINEAGE BUSINESS                       │
├─────────────────────────────────────────────────┤
│                                                  │
│  Concept: "Chiffre d'affaires mensuel"          │
│                                                  │
│  Composants :                                    │
│  ├── Primes encaissées                          │
│  │   └── Source: facturation.paiements          │
│  ├── Frais de gestion                           │
│  │   └── Source: comptabilité.écritures         │
│  └── Commissions                                │
│      └── Source: apporteurs.commissions         │
│                                                  │
│  Formule :                                       │
│  CA = Primes + Frais - Commissions              │
│                                                  │
│  Responsable: Direction Financière              │
│  Certification: Validé par DAF                  │
│                                                  │
└─────────────────────────────────────────────────┘
```

## Granularité du Lineage

```
┌─────────────────────────────────────────────────┐
│         NIVEAUX DE GRANULARITÉ                  │
├─────────────────────────────────────────────────┤
│                                                  │
│  COARSE-GRAINED (Table → Table)                  │
│  ─────────────────────────────                   │
│  policies ──▶ ETL ──▶ dim_policies              │
│                                                  │
│  • Simple à implémenter                         │
│  • Moins précis                                 │
│                                                  │
│  FINE-GRAINED (Colonne → Colonne)                │
│  ─────────────────────────────────               │
│  policies.premium ──┐                           │
│                     ├──▶ fact.premium_ttc       │
│  policies.tax_rate ─┘                           │
│                                                  │
│  • Très précis                                  │
│  • Complexe à maintenir                         │
│                                                  │
│  ROW-LEVEL (Ligne → Ligne)                       │
│  ─────────────────────────                       │
│  policy_id=P001 ──▶ transforms ──▶ fact_id=F001 │
│                                                  │
│  • Audit complet                                │
│  • Coût stockage élevé                          │
│                                                  │
└─────────────────────────────────────────────────┘
```

## Capture du Lineage

### Méthodes de capture

| Méthode | Description | Pros/Cons |
|---------|-------------|-----------|
| **Parsing SQL** | Analyse des requêtes | Automatique, limité aux SQL |
| **API/SDK** | Instrumentation code | Précis, effort développement |
| **Log analysis** | Analyse des logs | Passif, moins précis |
| **Metadata harvesting** | Scan des métadonnées | Large couverture, statique |

### Exemple de capture

```python
# Pseudo-code instrumentation lineage
@track_lineage
def transform_policies(source_df):
    # Lineage automatiquement capturé
    result = (
        source_df
        .filter(status='ACTIVE')
        .select('policy_id', 'customer_id', 'premium')
        .with_column('premium_ttc', col('premium') * 1.2)
    )
    return result

# Lineage généré :
# source.policies.status → filter
# source.policies.policy_id → target.fact.policy_id
# source.policies.customer_id → target.fact.customer_id
# source.policies.premium → transform → target.fact.premium_ttc
```

## Visualisation du Lineage

```
┌─────────────────────────────────────────────────┐
│         GRAPHE DE LINEAGE                        │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌─────────────┐                                │
│  │ CRM System  │                                │
│  │ customers   │                                │
│  └──────┬──────┘                                │
│         │                                       │
│         ▼                                       │
│  ┌─────────────┐     ┌─────────────┐           │
│  │   ETL Job   │────▶│   Staging   │           │
│  │  Customer   │     │    Area     │           │
│  └─────────────┘     └──────┬──────┘           │
│                             │                   │
│         ┌───────────────────┼───────────┐      │
│         │                   │           │      │
│         ▼                   ▼           ▼      │
│  ┌───────────┐      ┌───────────┐ ┌─────────┐ │
│  │    DWH    │      │  DataMart │ │ Reporting│ │
│  │dim_customer│     │  Claims   │ │ BI Tool  │ │
│  └───────────┘      └───────────┘ └─────────┘ │
│                                                  │
│  Clic sur un nœud → détails + impact           │
│                                                  │
└─────────────────────────────────────────────────┘
```

## Impact Analysis

```
┌─────────────────────────────────────────────────┐
│         ANALYSE D'IMPACT                         │
├─────────────────────────────────────────────────┤
│                                                  │
│  Question: "Que se passe-t-il si je modifie     │
│             la colonne policies.premium ?"       │
│                                                  │
│  Downstream Impact (aval):                       │
│  ├── stg_policies.premium                       │
│  ├── dwh.dim_policies.premium                   │
│  ├── dwh.fact_premiums.amount                   │
│  ├── datamart.monthly_revenue                   │
│  ├── report.financial_dashboard                 │
│  └── ⚠️ 3 jobs ETL à modifier                   │
│      ⚠️ 2 rapports à valider                    │
│                                                  │
│  Upstream Analysis (amont):                      │
│  Question: "D'où vient fact.total_premium ?"    │
│  ├── dwh.fact_premiums (SUM)                    │
│  │   └── stg_policies.premium                   │
│  │       └── source.policies.premium            │
│  └── Origine: Policy Admin System               │
│                                                  │
└─────────────────────────────────────────────────┘
```

## Outils de Data Lineage

| Outil | Type | Focus |
|-------|------|-------|
| **Apache Atlas** | Open Source | Hadoop ecosystem |
| **DataHub** | Open Source | Modern data stack |
| **OpenLineage** | Standard | Interopérabilité |
| **Collibra** | Commercial | Enterprise governance |
| **Alation** | Commercial | Data catalog + lineage |
| **Monte Carlo** | SaaS | Data observability |
