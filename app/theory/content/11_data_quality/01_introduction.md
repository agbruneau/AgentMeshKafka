# Qualité et Gouvernance des Données

## Introduction

La **qualité des données** est un facteur critique de succès pour tout projet d'intégration. Des données de mauvaise qualité se propagent et amplifient les problèmes à travers l'écosystème.

## L'enjeu business

```
┌─────────────────────────────────────────────────┐
│          COÛT DE LA MAUVAISE QUALITÉ            │
├─────────────────────────────────────────────────┤
│                                                  │
│  "Garbage In, Garbage Out"                       │
│                                                  │
│  ┌─────────┐     ┌─────────┐     ┌─────────┐   │
│  │ Mauvaise│     │Décisions│     │  Perte  │   │
│  │ qualité │────▶│ erronées│────▶│  business│   │
│  │ données │     │         │     │         │   │
│  └─────────┘     └─────────┘     └─────────┘   │
│                                                  │
│  Impacts en assurance :                          │
│  • Tarification incorrecte (perte ou fraude)    │
│  • Non-conformité réglementaire (amendes)       │
│  • Mauvaise expérience client (churn)           │
│  • Reporting faux (mauvaises décisions)         │
│                                                  │
│  Règle du 1-10-100 :                            │
│  • Prévention : 1€                              │
│  • Correction : 10€                             │
│  • Échec : 100€                                 │
│                                                  │
└─────────────────────────────────────────────────┘
```

## Les 6 dimensions de la qualité

| Dimension | Question | Exemple |
|-----------|----------|---------|
| **Complétude** | Toutes les données sont-elles présentes ? | Email client manquant |
| **Exactitude** | Les données sont-elles correctes ? | Format téléphone invalide |
| **Cohérence** | Les données sont-elles cohérentes entre systèmes ? | Client "Jean" vs "JEAN" |
| **Validité** | Les données respectent-elles les règles métier ? | Prime négative |
| **Unicité** | Y a-t-il des doublons ? | Client en double |
| **Fraîcheur** | Les données sont-elles à jour ? | Adresse obsolète |

## Cycle de vie de la qualité

```
┌─────────────────────────────────────────────────┐
│        CYCLE DE VIE DATA QUALITY                │
├─────────────────────────────────────────────────┤
│                                                  │
│         ┌─────────────┐                         │
│         │   MESURER   │                         │
│         │  (Profiler) │                         │
│         └──────┬──────┘                         │
│                │                                │
│    ┌───────────┼───────────┐                    │
│    │           ▼           │                    │
│    │    ┌─────────────┐    │                    │
│    │    │  ANALYSER   │    │                    │
│    │    │(Root cause) │    │                    │
│    │    └──────┬──────┘    │                    │
│    │           │           │                    │
│    │           ▼           │                    │
│    │    ┌─────────────┐    │                    │
│    │    │ AMÉLIORER   │    │                    │
│    │    │ (Corriger)  │    │                    │
│    │    └──────┬──────┘    │                    │
│    │           │           │                    │
│    │           ▼           │                    │
│    │    ┌─────────────┐    │                    │
│    │    │ MONITORER   │    │                    │
│    │    │  (Alerter)  │    │                    │
│    │    └──────┬──────┘    │                    │
│    │           │           │                    │
│    └───────────┴───────────┘                    │
│         Cycle continu                           │
│                                                  │
└─────────────────────────────────────────────────┘
```

## Data Quality Framework

```
┌─────────────────────────────────────────────────┐
│          DATA QUALITY FRAMEWORK                  │
├─────────────────────────────────────────────────┤
│                                                  │
│  PEOPLE           PROCESS          TECHNOLOGY   │
│  ───────          ───────          ──────────   │
│                                                  │
│  • Data Owner     • Profiling      • DQ Tools   │
│  • Data Steward   • Cleansing      • MDM        │
│  • DQ Analyst     • Monitoring     • ETL        │
│  • Data Council   • Remediation    • Catalog    │
│                                                  │
│  GOVERNANCE                                      │
│  ───────────                                     │
│  • Politiques qualité                           │
│  • Standards et règles                          │
│  • Métriques et KPIs                            │
│  • Processus d'escalade                         │
│                                                  │
└─────────────────────────────────────────────────┘
```

## Cas d'usage Assurance

### Données critiques

| Domaine | Données | Enjeu qualité |
|---------|---------|---------------|
| **Client** | Nom, adresse, contact | Communication, conformité RGPD |
| **Police** | Garanties, primes | Tarification correcte |
| **Sinistre** | Montants, dates | Provisions, reporting |
| **Facturation** | Échéances, montants | Cash-flow, contentieux |

### Réglementations

- **RGPD** : Exactitude des données personnelles
- **Solvency II** : Qualité des données actuarielles
- **ACPR** : Reporting conforme
