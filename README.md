# Interop Learning

**Plateforme d'apprentissage de l'interopérabilité en écosystème d'entreprise**

Une application interactive et complète pour apprendre les patterns d'intégration d'entreprise dans un contexte d'assurance dommage. Entièrement offline, sans dépendances externes (Redis, Kafka, etc.).

---

## Vue d'ensemble

Interop Learning enseigne les **trois piliers de l'intégration** à travers 16 modules théoriques et 24 scénarios pratiques interactifs :

| Pilier | Description | Modules |
|--------|-------------|---------|
| **Applications** | REST APIs, Gateway, BFF, Composition, ACL | 3-5 |
| **Événements** | Messaging, Event Sourcing, CQRS, Saga, Outbox | 6-8 |
| **Données** | ETL, CDC, MDM, Data Quality, Lineage | 9-11 |

Plus des **patterns transversaux** : Circuit Breaker, Retry, Observabilité, Sécurité (Modules 12-14).

---

## Démarrage rapide

### Prérequis

- Python 3.11+
- pip

### Installation

```bash
# Cloner le projet
git clone https://github.com/votre-repo/interop-learning.git
cd interop-learning

# Créer l'environnement virtuel
python -m venv venv

# Activer (Windows)
venv\Scripts\activate

# Activer (Linux/Mac)
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### Lancement

```bash
python run.py
```

L'application démarre sur `http://localhost:8000`

---

## Stack Technique

| Composant | Technologie |
|-----------|-------------|
| **Backend** | FastAPI 0.109+, Python 3.11+ |
| **Base de données** | SQLite (aiosqlite) |
| **Frontend** | Jinja2, Tailwind CSS, HTMX |
| **Visualisation** | D3.js (force-directed graphs) |
| **Temps réel** | Server-Sent Events (SSE) |
| **Tests** | pytest, pytest-asyncio, httpx |

---

## Architecture

```
interop-learning/
├── app/
│   ├── main.py                 # Application FastAPI
│   ├── config.py               # Configuration (16 modules)
│   ├── database.py             # SQLite + schéma
│   │
│   ├── mocks/                  # 8 services d'assurance simulés
│   │   ├── quote_engine.py     # Calcul de devis
│   │   ├── policy_admin.py     # Gestion des polices
│   │   ├── claims.py           # Gestion des sinistres
│   │   ├── billing.py          # Facturation
│   │   ├── customer_hub.py     # Référentiel clients
│   │   ├── document_mgmt.py    # GED
│   │   ├── notifications.py    # Notifications
│   │   └── external_rating.py  # API tarification externe
│   │
│   ├── integration/
│   │   ├── applications/       # Pilier 1: Gateway, BFF, ACL
│   │   ├── events/             # Pilier 2: Broker, Saga, CQRS
│   │   ├── data/               # Pilier 3: ETL, CDC, MDM
│   │   └── cross_cutting/      # Circuit Breaker, Retry, Security
│   │
│   ├── theory/
│   │   ├── renderer.py         # Markdown → HTML
│   │   └── content/            # 16 modules × 4-5 sections
│   │
│   ├── sandbox/
│   │   └── scenarios/          # 24 scénarios interactifs
│   │
│   ├── api/                    # Routes REST
│   ├── docs/                   # Glossaire, patterns, cheatsheets
│   └── templates/              # Templates Jinja2
│
├── static/
│   ├── js/
│   │   ├── flow-visualizer.js  # Visualisation D3.js
│   │   └── decision-matrix.js  # Matrice de décision
│   └── css/
│
├── data/
│   ├── learning.db             # Progression utilisateur
│   └── mock_data/              # Données de test JSON
│
├── tests/                      # 23 suites de tests
├── requirements.txt
├── run.py
├── PRD.md                      # Spécifications (lecture seule)
└── progress.md                 # Backlog et statuts
```

---

## Les 8 Services Mock

Tous les services simulent un SI d'assurance avec latence configurable et injection de pannes :

| Service | Latence | Description |
|---------|---------|-------------|
| Quote Engine | 50ms | Calcul de devis automobile/habitation |
| Policy Admin | 30ms | CRUD polices d'assurance |
| Claims | 40ms | Déclaration et suivi des sinistres |
| Billing | 30ms | Facturation et prélèvements |
| Customer Hub | 20ms | Référentiel client unifié |
| Document Mgmt | 60ms | Gestion électronique de documents |
| Notifications | 20ms | SMS, email, push |
| External Rating | 200ms | API externe de tarification |

---

## Patterns Implémentés

### Pilier Applications
- **API Gateway** : Routing, rate limiting (Token Bucket)
- **BFF** (Backend for Frontend) : Mobile vs Courtier
- **API Composition** : Vue 360° client agrégée
- **Anti-Corruption Layer** : Transformation legacy
- **Strangler Fig** : Migration progressive

### Pilier Événements
- **Message Broker** : Queues P2P, Topics Pub/Sub
- **Event Sourcing** : Append-only log + replay
- **CQRS** : Séparation lecture/écriture
- **Saga Orchestrator** : Transactions distribuées avec compensation
- **Outbox Pattern** : Publication atomique
- **Dead Letter Queue** : Gestion des erreurs

### Pilier Données
- **ETL Pipeline** : Extract, Transform, Load
- **CDC** (Change Data Capture) : Capture incrémentale
- **MDM** (Master Data Management) : Golden Record, matching
- **Data Quality** : Validation, anomaly detection
- **Data Lineage** : Traçabilité des transformations

### Cross-Cutting
- **Circuit Breaker** : États CLOSED → OPEN → HALF_OPEN
- **Retry** : Exponential backoff + jitter
- **Observability** : Logging structuré, tracing distribué
- **Security** : JWT, API Keys, RBAC

---

## Scénarios Sandbox

24 scénarios pratiques couvrant tous les patterns :

| Catégorie | Scénarios | Exemples |
|-----------|-----------|----------|
| **INTRO** | 2 | Explorer l'écosystème, cartographie des flux |
| **APP** | 5 | API REST, Gateway, BFF, Vue 360°, Strangler Fig |
| **EVT** | 7 | Pub/Sub, Event Sourcing, Saga, CQRS, DLQ |
| **DATA** | 7 | ETL batch, CDC temps réel, MDM, Data Quality |
| **CROSS** | 4 | Circuit Breaker, Tracing, Security, Intégration complète |

---

## Documentation Intégrée

- **27 fiches patterns** avec : problème, solution, quand utiliser, anti-patterns
- **53 termes de glossaire** avec tooltips
- **Cheat sheets** par pilier
- **Recherche full-text** sur tout le contenu

---

## Tests

```bash
# Exécuter tous les tests
pytest tests/ -v

# Tests d'une feature spécifique
pytest tests/test_feature_3_1.py -v

# Avec couverture
pytest --cov=app --cov-report=html
```

**Métriques actuelles** :
- 251+ tests passants
- ~80% couverture de code
- 23 suites de tests

---

## API Endpoints Principaux

### Théorie
```
GET  /api/theory/modules          # Liste des 16 modules
GET  /api/theory/modules/{id}     # Contenu d'un module
POST /api/theory/modules/{id}/complete  # Marquer complété
GET  /api/progress                # Progression globale
```

### Sandbox
```
GET  /api/sandbox/scenarios       # Liste des scénarios
GET  /api/sandbox/scenarios/{id}  # Détail d'un scénario
POST /api/sandbox/scenarios/{id}/execute  # Exécuter
```

### Documentation
```
GET  /api/docs/search?q={term}    # Recherche
GET  /api/docs/patterns           # Catalogue patterns
GET  /api/docs/glossary           # Glossaire complet
```

### Services Mock
```
GET/POST/PUT/DELETE /mocks/quotes
GET/POST/PUT/DELETE /mocks/policies
GET/POST/PUT/DELETE /mocks/claims
...
```

---

## Configuration

Variables dans `app/config.py` :

```python
APP_NAME = "Interop Learning"
DATABASE_PATH = "data/learning.db"
MODULES_COUNT = 16
DEFAULT_LATENCY_MS = 50
FAILURE_RATE = 0.0  # 0-1, pour injection de pannes
```

---

## Contribuer

1. Consulter `progress.md` pour les tâches disponibles
2. Ne pas modifier `PRD.md` (source de vérité)
3. Mettre à jour `progress.md` après chaque tâche
4. Exécuter les tests avant de commit
5. Commits atomiques par tâche

---

## Licence

MIT

---

## Auteur

Projet développé avec Claude Code (Anthropic)

*Dernière mise à jour : 2026-01-21 - Phase 6 complétée*
