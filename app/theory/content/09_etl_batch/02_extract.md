# Phase Extract - Extraction des données

## Principes de l'extraction

L'extraction est la première phase du pipeline ETL. Elle consiste à récupérer les données depuis les systèmes sources de manière fiable et performante.

## Types d'extraction

### Extraction complète (Full Extract)

```
┌─────────────┐                    ┌─────────────┐
│   Source    │═══════════════════▶│   Staging   │
│   (100%)    │   Tous les         │   Area      │
│             │   enregistrements  │             │
└─────────────┘                    └─────────────┘
```

**Avantages** : Simple, données complètes
**Inconvénients** : Lent, coûteux en ressources

### Extraction incrémentale (Delta Extract)

```
┌─────────────┐                    ┌─────────────┐
│   Source    │──────────────────▶│   Staging   │
│  (Delta Δ)  │   Uniquement les   │   Area      │
│             │   modifications    │             │
└─────────────┘                    └─────────────┘

Méthodes de détection :
├── Timestamp (updated_at > last_run)
├── Numéro de séquence (id > last_id)
├── Hash de colonne
└── CDC (Change Data Capture)
```

## Patterns d'extraction

### 1. Query-based extraction

```sql
-- Extraction par timestamp
SELECT * FROM policies
WHERE updated_at > :last_extraction_timestamp

-- Extraction par flag
SELECT * FROM claims
WHERE etl_processed = 0
```

### 2. File-based extraction

```
Sources fichiers courantes :
├── CSV / TSV
├── Excel (.xlsx)
├── JSON / XML
├── Parquet (optimisé analytics)
└── Fichiers EDI (B2B assurance)
```

### 3. API-based extraction

```python
# Pseudo-code extraction API
def extract_from_api(endpoint, params):
    data = []
    page = 1
    while True:
        response = api.get(endpoint, page=page, **params)
        if not response.items:
            break
        data.extend(response.items)
        page += 1
    return data
```

## Staging Area

La **Staging Area** est une zone intermédiaire où les données brutes sont stockées temporairement avant transformation.

```
┌─────────────────────────────────────────────────┐
│              STAGING AREA                        │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐         │
│  │ STG_    │  │ STG_    │  │ STG_    │         │
│  │CUSTOMERS│  │POLICIES │  │ CLAIMS  │         │
│  └─────────┘  └─────────┘  └─────────┘         │
│                                                  │
│  Caractéristiques :                              │
│  • Données brutes (non transformées)             │
│  • Schéma identique à la source                  │
│  • Vidée après chaque run ETL                    │
│  • Permet le rejeu en cas d'erreur              │
│                                                  │
└─────────────────────────────────────────────────┘
```

## Gestion des erreurs

| Erreur | Stratégie |
|--------|-----------|
| Source indisponible | Retry avec backoff, alerte |
| Timeout | Extraction par chunks |
| Données corrompues | Logging, quarantaine |
| Changement de schéma | Détection automatique, alerte |
