# CLAUDE.md - Instructions pour Claude Code

## Contexte Projet

Ce projet est une **application d'apprentissage de l'interopérabilité en écosystème d'entreprise**, simulant un environnement d'assurance dommage. L'application enseigne les trois piliers de l'intégration : Applications, Événements et Données.

## Documents de Référence

- **PRD.md** : Spécifications complètes du produit (lecture seule, ne pas modifier)
- **progress.md** : Backlog des features et tâches à implémenter (mettre à jour les statuts)

## Conventions de Travail

### Structure des Commandes

Quand je demande d'implémenter une feature, utilise ce format :

```
/feature [ID]  - Implémenter la feature spécifiée dans progress.md
/test [ID]     - Exécuter les tests de validation de la feature
/status        - Afficher l'état actuel du backlog
```

### Workflow d'Implémentation

1. **Lire** la feature dans `progress.md`
2. **Implémenter** les tâches séquentiellement
3. **Tester** avec les tests de validation fournis
4. **Mettre à jour** le statut dans `progress.md` (`[ ]` → `[x]`)

### Conventions de Code

- **Backend** : Python 3.11+, FastAPI, SQL brut (pas d'ORM)
- **Frontend** : HTML/Jinja2, Tailwind CSS, HTMX, D3.js
- **Tests** : pytest avec pytest-asyncio
- **Style** : Code simple, pas de sur-ingénierie, commentaires en français

### Arborescence Cible

```
interop-learning/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── api/
│   ├── mocks/
│   ├── integration/
│   ├── theory/
│   └── templates/
├── static/
├── data/
├── tests/
├── requirements.txt
├── run.py
├── CLAUDE.md
├── PRD.md
└── progress.md
```

## Commandes Utiles

```bash
# Installation
python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt

# Lancement
python run.py

# Tests
pytest tests/ -v
pytest tests/test_feature_X_Y.py -v  # Feature spécifique
pytest --cov=app --cov-report=html   # Couverture
```

## Règles Importantes

1. **Ne jamais modifier PRD.md** - C'est la source de vérité
2. **Toujours mettre à jour progress.md** après chaque tâche complétée
3. **Exécuter les tests** avant de marquer une feature comme terminée
4. **Commits atomiques** - Un commit par tâche ou groupe de tâches liées
