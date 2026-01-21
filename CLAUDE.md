# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Contexte Projet

**Interop Learning** est une plateforme d'apprentissage de l'interopérabilité en écosystème d'entreprise, simulant un environnement d'assurance dommage. Application 100% offline sans dépendances externes (pas de Kafka, Redis, etc.).

### Les Trois Piliers d'Intégration

| Pilier | Modules | Patterns Clés |
|--------|---------|---------------|
| 🔗 **Applications** | 3-5 | API Gateway, BFF, Composition, ACL |
| ⚡ **Événements** | 6-8 | Broker In-Memory, Event Store, CQRS, Saga |
| 📊 **Données** | 9-11 | ETL, CDC, MDM, Data Quality, Lineage |

## Documents de Référence

- **PRD.md** : Spécifications complètes (lecture seule, ne jamais modifier)
- **progress.md** : Backlog des features (mettre à jour les statuts après chaque tâche)

## Commandes

```bash
# Installation
python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt

# Lancement (ouvre automatiquement http://localhost:8000)
python run.py

# Tests
pytest tests/ -v                           # Tous les tests
pytest tests/test_feature_3_1.py -v        # Feature spécifique
pytest tests/test_message_broker.py -v     # Composant spécifique
pytest --cov=app --cov-report=html         # Avec couverture (~80%)
```

## Architecture

### Flux de Données Principal

```
Browser (HTMX/D3.js) ──HTTP/SSE──▶ FastAPI (main.py)
                                       │
          ┌────────────────────────────┼────────────────────────────┐
          ▼                            ▼                            ▼
    api/*.py                  integration/                    mocks/*.py
  (REST routes)                    │                         (8 services)
                    ┌──────────────┼──────────────┐
                    ▼              ▼              ▼
              applications/    events/         data/
              gateway.py      broker.py      etl_pipeline.py
              bff.py          saga.py        cdc_simulator.py
              composition.py  event_store.py mdm.py
              acl.py          cqrs.py        data_quality.py
```

### Composants Clés

| Fichier | Responsabilité |
|---------|----------------|
| `app/main.py` | Point d'entrée FastAPI, SSE broadcaster, montage des routers |
| `app/config.py` | Constantes: 16 modules, couleurs piliers, latences services |
| `app/database.py` | Init SQLite, schéma (learner_progress, sandbox_sessions) |
| `app/integration/events/broker.py` | Message broker in-memory (queues P2P, topics pub/sub, DLQ) |
| `app/integration/events/saga.py` | Orchestration transactions distribuées avec compensation |
| `app/integration/applications/gateway.py` | API Gateway avec rate limiting (Token Bucket) |
| `static/js/flow-visualizer.js` | Visualisation D3.js force-directed avec animation SSE |

### 8 Services Mock (app/mocks/)

Tous héritent de `MockService` avec latence configurable et injection de pannes:
- Quote Engine (50ms) - Calcul devis
- Policy Admin (30ms) - CRUD polices
- Claims (40ms) - Gestion sinistres
- Billing (30ms) - Facturation
- Customer Hub (20ms) - Référentiel client
- Document Mgmt (60ms) - GED
- Notifications (20ms) - Alertes
- External Rating (200ms) - API externe

## Conventions de Code

- **Backend** : Python 3.11+, FastAPI, SQL brut (pas d'ORM)
- **Frontend** : HTML/Jinja2, Tailwind CSS (dark theme), HTMX, D3.js
- **Tests** : pytest avec pytest-asyncio, httpx pour les tests API
- **Style** : Code simple, commentaires en français, pas de sur-ingénierie
- **Temps réel** : SSE (Server-Sent Events), pas de WebSocket

## Workflow d'Implémentation

1. **Lire** la feature dans `progress.md`
2. **Implémenter** les tâches séquentiellement
3. **Tester** avec les tests de validation fournis
4. **Mettre à jour** le statut dans `progress.md` (`[ ]` → `[x]`)

## Règles Importantes

1. **Ne jamais modifier PRD.md** - Source de vérité
2. **Toujours mettre à jour progress.md** après chaque tâche complétée
3. **Exécuter les tests** avant de marquer une feature comme terminée
4. **Commits atomiques** - Un commit par tâche ou groupe de tâches liées

## API Endpoints Principaux

```
GET  /api/theory/modules           # 16 modules
GET  /api/theory/modules/{id}      # Contenu module
POST /api/theory/modules/{id}/complete
GET  /api/progress                 # Progression globale

GET  /api/sandbox/scenarios        # 24 scénarios
POST /api/sandbox/scenarios/{id}/execute

GET  /api/docs/search?q={term}     # Recherche full-text
GET  /api/docs/patterns            # 27 fiches patterns

GET  /events/stream                # SSE temps réel
```
