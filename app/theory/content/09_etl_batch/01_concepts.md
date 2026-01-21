# ETL et Traitement Batch

## Introduction

L'**ETL** (Extract-Transform-Load) est le pilier fondamental de l'intégration des données en entreprise. Ce pattern permet de déplacer et transformer des données entre systèmes, généralement en mode batch (traitement par lots).

## Définition

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   EXTRACT   │────▶│  TRANSFORM  │────▶│    LOAD     │
│             │     │             │     │             │
│ Sources de  │     │ Nettoyage   │     │ Destination │
│ données     │     │ Enrichment  │     │ cible       │
│             │     │ Agrégation  │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
```

### Les trois phases

| Phase | Objectif | Exemples |
|-------|----------|----------|
| **Extract** | Récupérer les données depuis les sources | Lecture base de données, fichiers, APIs |
| **Transform** | Nettoyer et enrichir les données | Validation, calculs, jointures, dédoublonnage |
| **Load** | Charger vers la destination | Insertion dans DWH, mise à jour, upsert |

## ETL vs ELT

L'**ELT** (Extract-Load-Transform) est une variante moderne où la transformation s'effectue après le chargement, directement dans le système cible.

| Critère | ETL | ELT |
|---------|-----|-----|
| **Transformation** | Sur serveur intermédiaire | Dans le système cible |
| **Performance** | Limitée par serveur ETL | Exploite puissance du DWH |
| **Cas d'usage** | DWH traditionnels | Data Lakes, Cloud DWH |
| **Outils typiques** | Talend, Informatica | dbt, Spark, Snowflake |

## Cas d'usage Assurance

Dans un écosystème d'assurance, l'ETL est utilisé pour :

- **Alimentation du DWH** : Consolidation quotidienne des polices, sinistres, factures
- **Reporting réglementaire** : Extraction mensuelle pour Solvency II
- **Calcul actuariel** : Agrégation des données de risque
- **MDM** : Synchronisation du référentiel clients
