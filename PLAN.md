# PLAN.md — Plan d'Implémentation

## Application de Génération PDF « L'Entreprise Agentique »

---

**Version** : 1.0
**Date** : Janvier 2026
**Référence** : PDR.md (Spécifications)

---

## Table des Matières

1. [Vue d'Ensemble](#1-vue-densemble)
2. [Phases de Développement](#2-phases-de-développement)
3. [Phase 1 : Infrastructure](#3-phase-1--infrastructure)
4. [Phase 2 : Templates Typst](#4-phase-2--templates-typst)
5. [Phase 3 : Filtres Lua](#5-phase-3--filtres-lua)
6. [Phase 4 : Scripts Python](#6-phase-4--scripts-python)
7. [Phase 5 : Génération Volumes](#7-phase-5--génération-volumes)
8. [Phase 6 : Consolidation](#8-phase-6--consolidation)
9. [Risques et Mitigations](#9-risques-et-mitigations)
10. [Checklist de Validation](#10-checklist-de-validation)

---

## 1. Vue d'Ensemble

### 1.1 Résumé du Projet

| Aspect | Détail |
|--------|--------|
| **Objectif** | Générer 5 PDFs de volumes + 1 PDF consolidé |
| **Sources** | 89 fichiers Markdown |
| **Stack** | Python + Pandoc + Lua + Typst |
| **Livrables** | Application fonctionnelle `pdf-generator/` |

### 1.2 Jalons Principaux

```
Phase 1 ──▶ Phase 2 ──▶ Phase 3 ──▶ Phase 4 ──▶ Phase 5 ──▶ Phase 6
Infra       Templates   Filtres     Scripts     Volumes     Consolidé
```

---

## 2. Phases de Développement

### 2.1 Tableau Récapitulatif

| Phase | Nom | Livrables | Dépendances |
|-------|-----|-----------|-------------|
| **1** | Infrastructure | Répertoires, YAML configs | Aucune |
| **2** | Templates Typst | 5 fichiers .typ | Phase 1 |
| **3** | Filtres Lua | 3 fichiers .lua | Phase 1 |
| **4** | Scripts Python | 3 fichiers .py | Phases 2, 3 |
| **5** | Génération Volumes | 5 PDFs testés | Phase 4 |
| **6** | Consolidation | PDF complet + finalisation | Phase 5 |

### 2.2 Ordre d'Exécution

```
[Phase 1: Infrastructure]
         │
         ├──────────────────┐
         ▼                  ▼
[Phase 2: Templates]  [Phase 3: Filtres]
         │                  │
         └────────┬─────────┘
                  ▼
        [Phase 4: Scripts]
                  │
                  ▼
        [Phase 5: Volumes]
                  │
                  ▼
        [Phase 6: Consolidé]
```

---

## 3. Phase 1 : Infrastructure

### 3.1 Objectifs

- Créer la structure de répertoires `pdf-generator/`
- Configurer les fichiers YAML
- Préparer l'environnement

### 3.2 Tâches Détaillées

| ID | Tâche | Fichier(s) | Statut |
|----|-------|------------|--------|
| 1.1 | Créer arborescence répertoires | `pdf-generator/` | ⬜ |
| 1.2 | Créer `volumes.yaml` | `config/volumes.yaml` | ⬜ |
| 1.3 | Créer `callouts.yaml` | `config/callouts.yaml` | ⬜ |
| 1.4 | Créer `styles.yaml` | `config/styles.yaml` | ⬜ |
| 1.5 | Créer README.md | `pdf-generator/README.md` | ⬜ |

### 3.3 Structure à Créer

```
Monographie/pdf-generator/
├── config/
│   ├── volumes.yaml
│   ├── callouts.yaml
│   └── styles.yaml
├── templates/
├── filters/
├── scripts/
├── assets/
│   └── fonts/
├── output/
│   ├── volumes/
│   └── consolidated/
└── README.md
```

### 3.4 Critères de Validation Phase 1

- [ ] Tous les répertoires existent
- [ ] Fichiers YAML valides (syntaxe)
- [ ] Configuration des 5 volumes présente
- [ ] Configuration des 15+ callouts présente

---

## 4. Phase 2 : Templates Typst

### 4.1 Objectifs

- Créer les templates de mise en page
- Définir les styles visuels
- Implémenter les callouts

### 4.2 Tâches Détaillées

| ID | Tâche | Fichier(s) | Statut |
|----|-------|------------|--------|
| 2.1 | Template callouts | `templates/callouts.typ` | ⬜ |
| 2.2 | Template couverture | `templates/cover.typ` | ⬜ |
| 2.3 | Template TOC | `templates/toc.typ` | ⬜ |
| 2.4 | Template volume principal | `templates/volume.typ` | ⬜ |
| 2.5 | Template consolidé | `templates/consolidated.typ` | ⬜ |

### 4.3 Spécifications `callouts.typ`

```typst
// Imports requis
#import "@preview/showybox:2.0.4": showybox

// 15+ fonctions de callout à implémenter :
// - callout-definition
// - callout-strategic
// - callout-example
// - callout-technical
// - callout-best-practices
// - callout-warning
// - callout-field-note
// - callout-decision
// - callout-antipattern
// - callout-case-study
// - callout-migration
// - callout-performance
// - callout-historical
// - callout-reflection
// - callout-manifesto
```

### 4.4 Spécifications `cover.typ`

```typst
// Fonction principale
#let cover-page(
  volume-number,   // "I", "II", etc.
  title,           // Titre du volume
  subtitle,        // Sous-titre
  author,          // Auteur
  year,            // Année
  accent-color     // Couleur thématique
) = { ... }
```

### 4.5 Spécifications `volume.typ`

```typst
// Configuration document
#set document(
  title: [Titre],
  author: "André-Guy Bruneau"
)

#set page(
  paper: "a4",
  margin: (
    top: 2.5cm,
    bottom: 2.5cm,
    left: 2cm,
    right: 2cm
  ),
  header: [...],
  footer: [...]
)

// Import composants
#import "callouts.typ": *
#import "cover.typ": cover-page
#import "toc.typ": custom-toc
```

### 4.6 Critères de Validation Phase 2

- [ ] Compilation Typst sans erreur pour chaque template
- [ ] Rendu visuel des 15+ callouts validé
- [ ] Page de couverture esthétique
- [ ] TOC avec hyperliens fonctionnels

---

## 5. Phase 3 : Filtres Lua

### 5.1 Objectifs

- Transformer les blockquotes Markdown en callouts Typst
- Gérer les tableaux et figures
- Implémenter les références croisées

### 5.2 Tâches Détaillées

| ID | Tâche | Fichier(s) | Statut |
|----|-------|------------|--------|
| 3.1 | Filtre callouts | `filters/callouts.lua` | ⬜ |
| 3.2 | Filtre figures | `filters/figures.lua` | ⬜ |
| 3.3 | Filtre cross-refs | `filters/cross-refs.lua` | ⬜ |

### 5.3 Spécifications `callouts.lua`

```lua
-- Patterns de détection des callouts
local patterns = {
  { pattern = "^%*%*Définition formelle%*%*",
    func = "callout-definition" },
  { pattern = "^%*%*Perspective stratégique%*%*",
    func = "callout-strategic" },
  { pattern = "^%*%*Exemple concret%*%*",
    func = "callout-example" },
  -- ... 12 autres patterns
}

-- Fonction principale
function BlockQuote(el)
  local first = pandoc.utils.stringify(el.content[1])

  for _, p in ipairs(patterns) do
    if first:match(p.pattern) then
      return transform_to_typst(el, p.func)
    end
  end

  return el
end
```

### 5.4 Gestion des Callouts Structurés

Pour les callouts avec champs nommés (Note de terrain, Décision architecturale, etc.) :

```lua
-- Exemple: Note de terrain
-- Input Markdown:
-- > **Note de terrain**
-- >
-- > *Contexte* : Description...
-- > *Défi* : Problème...
-- > *Solution* : Approche...
-- > *Leçon* : Enseignement...

-- Output Typst:
-- #callout-field-note(
--   contexte: [Description...],
--   defi: [Problème...],
--   solution: [Approche...],
--   lecon: [Enseignement...]
-- )
```

### 5.5 Critères de Validation Phase 3

- [ ] Tous les 15+ types de callouts détectés
- [ ] Callouts structurés parsés correctement
- [ ] Callouts avec titre dynamique (Étude de cas : X)
- [ ] Pas de régression sur blockquotes normales

---

## 6. Phase 4 : Scripts Python

### 6.1 Objectifs

- Script de génération CLI complet
- Validation pré-génération
- Gestion des erreurs

### 6.2 Tâches Détaillées

| ID | Tâche | Fichier(s) | Statut |
|----|-------|------------|--------|
| 4.1 | Module utilitaires | `scripts/utils.py` | ⬜ |
| 4.2 | Script validation | `scripts/validate.py` | ⬜ |
| 4.3 | Script génération | `scripts/generate.py` | ⬜ |

### 6.3 Spécifications `generate.py`

```python
#!/usr/bin/env python3
"""
Script principal de génération PDF.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

def parse_args():
    parser = argparse.ArgumentParser(
        description="Génération PDF - L'Entreprise Agentique"
    )
    parser.add_argument(
        '--volume',
        choices=['I', 'II', 'III', 'IV', 'V', 'all'],
        help='Volume à générer'
    )
    parser.add_argument(
        '--consolidated',
        action='store_true',
        help='Générer la monographie complète'
    )
    parser.add_argument(
        '--parallel',
        action='store_true',
        help='Génération parallèle'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validation uniquement'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Mode verbose'
    )
    return parser.parse_args()

def main():
    args = parse_args()
    # ...

if __name__ == '__main__':
    main()
```

### 6.4 Pipeline de Génération

```python
def generate_volume(volume_id: str, config: dict) -> Path:
    """Pipeline complet pour un volume."""

    # 1. Collecter les fichiers Markdown
    md_files = collect_markdown_files(volume_id, config)

    # 2. Concaténer en un seul fichier
    combined_md = concatenate_markdown(md_files)

    # 3. Convertir via Pandoc + filtres Lua
    typst_content = run_pandoc(combined_md)

    # 4. Injecter dans le template
    final_typst = inject_into_template(typst_content, volume_id)

    # 5. Compiler avec Typst
    pdf_path = run_typst(final_typst)

    return pdf_path
```

### 6.5 Critères de Validation Phase 4

- [ ] CLI fonctionnel avec toutes les options
- [ ] Validation détecte les erreurs
- [ ] Génération d'un volume unique réussie
- [ ] Logs clairs et informatifs

---

## 7. Phase 5 : Génération Volumes

### 7.1 Objectifs

- Générer les 5 volumes individuels
- Valider visuellement chaque PDF
- Corriger les problèmes détectés

### 7.2 Tâches Détaillées

| ID | Tâche | Volume | Statut |
|----|-------|--------|--------|
| 5.1 | Générer et valider Volume I | 28 chapitres | ⬜ |
| 5.2 | Générer et valider Volume II | 15 chapitres | ⬜ |
| 5.3 | Générer et valider Volume III | 12 chapitres | ⬜ |
| 5.4 | Générer et valider Volume IV | 18 chapitres | ⬜ |
| 5.5 | Générer et valider Volume V | 10 chapitres | ⬜ |

### 7.3 Checklist de Validation par Volume

Pour chaque volume :

- [ ] PDF généré sans erreur
- [ ] Couverture correcte (titre, sous-titre, numéro)
- [ ] Table des matières complète
- [ ] Tous les chapitres présents
- [ ] Callouts rendus correctement
- [ ] Tableaux formatés
- [ ] Blocs de code lisibles
- [ ] Numérotation des pages
- [ ] En-têtes/pieds de page

### 7.4 Commandes de Test

```bash
# Générer chaque volume individuellement
python scripts/generate.py --volume I --verbose
python scripts/generate.py --volume II --verbose
python scripts/generate.py --volume III --verbose
python scripts/generate.py --volume IV --verbose
python scripts/generate.py --volume V --verbose

# Vérifier les fichiers générés
ls -la output/volumes/
```

### 7.5 Critères de Validation Phase 5

- [ ] 5 fichiers PDF créés dans `output/volumes/`
- [ ] Chaque PDF < 15 MB
- [ ] Temps de génération < 60s par volume
- [ ] Inspection visuelle validée

---

## 8. Phase 6 : Consolidation

### 8.1 Objectifs

- Générer la monographie complète
- Pagination continue
- Navigation inter-volumes
- Documentation finale

### 8.2 Tâches Détaillées

| ID | Tâche | Fichier(s) | Statut |
|----|-------|------------|--------|
| 6.1 | Template consolidé | `templates/consolidated.typ` | ⬜ |
| 6.2 | Génération PDF complet | `output/consolidated/` | ⬜ |
| 6.3 | Validation finale | — | ⬜ |
| 6.4 | Documentation README | `pdf-generator/README.md` | ⬜ |

### 8.3 Spécifications PDF Consolidé

- **Page de titre globale** : "L'Entreprise Agentique - Monographie Complète"
- **TOC générale** : 81 chapitres avec liens
- **Séparateurs de volume** : Pages de transition
- **Pagination** : Continue sur l'ensemble
- **Signets PDF** : Navigation hiérarchique

### 8.4 Commande de Test

```bash
# Générer la monographie complète
python scripts/generate.py --consolidated --verbose

# Vérifier le fichier généré
ls -la output/consolidated/
```

### 8.5 Critères de Validation Phase 6

- [ ] PDF consolidé généré
- [ ] 81 chapitres présents
- [ ] Pagination continue correcte
- [ ] Navigation PDF fonctionnelle
- [ ] README complet

---

## 9. Risques et Mitigations

### 9.1 Risques Identifiés

| ID | Risque | Probabilité | Impact | Mitigation |
|----|--------|-------------|--------|------------|
| R1 | Callouts non reconnus | Moyenne | Élevé | Tests unitaires par type |
| R2 | Performance Pandoc | Faible | Moyen | Mode parallèle |
| R3 | Incompatibilité Typst | Faible | Élevé | Fixer version Typst |
| R4 | Encodage caractères | Moyenne | Moyen | UTF-8 forcé partout |
| R5 | Tableaux complexes | Moyenne | Moyen | Simplification si nécessaire |

### 9.2 Plan de Contingence

**R1 - Callouts non reconnus** :
- Créer un fichier de test avec tous les patterns
- Valider chaque pattern individuellement
- Log des callouts non détectés

**R4 - Encodage caractères** :
- Forcer UTF-8 dans Pandoc
- Vérifier les caractères spéciaux français
- Tester : é, è, ê, ë, à, ù, ç, œ, «, »

---

## 10. Checklist de Validation

### 10.1 Checklist Globale

#### Infrastructure
- [ ] Arborescence `pdf-generator/` créée
- [ ] `volumes.yaml` valide et complet
- [ ] `callouts.yaml` avec 15+ types
- [ ] `styles.yaml` configuré

#### Templates Typst
- [ ] `callouts.typ` compile sans erreur
- [ ] `cover.typ` génère couvertures correctes
- [ ] `volume.typ` template principal fonctionnel
- [ ] `consolidated.typ` prêt

#### Filtres Lua
- [ ] `callouts.lua` détecte tous les types
- [ ] Callouts structurés fonctionnels
- [ ] `figures.lua` numérote tableaux

#### Scripts Python
- [ ] `generate.py` CLI complet
- [ ] `validate.py` détecte erreurs
- [ ] Mode parallèle fonctionnel

#### PDFs Volumes
- [ ] Volume I généré et validé
- [ ] Volume II généré et validé
- [ ] Volume III généré et validé
- [ ] Volume IV généré et validé
- [ ] Volume V généré et validé

#### PDF Consolidé
- [ ] Monographie complète générée
- [ ] 81 chapitres présents
- [ ] Navigation fonctionnelle

#### Documentation
- [ ] README.md complet
- [ ] Instructions d'installation
- [ ] Exemples d'utilisation

### 10.2 Commandes de Validation Finale

```bash
# 1. Valider tous les volumes
python scripts/generate.py --validate --volume all

# 2. Générer tous les volumes en parallèle
python scripts/generate.py --volume all --parallel

# 3. Générer la monographie consolidée
python scripts/generate.py --consolidated

# 4. Vérifier les sorties
ls -la output/volumes/
ls -la output/consolidated/

# 5. Ouvrir et inspecter visuellement
# (Windows)
start output\volumes\Volume_I_Fondations_Entreprise_Agentique.pdf
start output\consolidated\LEntreprise_Agentique_Monographie_Complete.pdf
```

---

## Annexe A — Commandes Utiles

### Installation des Dépendances

```bash
# Python
pip install pyyaml

# Vérification versions
python --version   # >= 3.10
pandoc --version   # >= 3.0
typst --version    # >= 0.11
```

### Test Pandoc + Lua

```bash
# Tester un filtre Lua sur un fichier
pandoc test.md \
  --lua-filter=filters/callouts.lua \
  --to=typst \
  -o test.typ
```

### Test Typst

```bash
# Compiler un fichier Typst
typst compile test.typ test.pdf

# Mode watch (développement)
typst watch test.typ
```

---

## Annexe B — Structure Fichiers Finale

```
Monographie/
├── pdf-generator/
│   ├── config/
│   │   ├── volumes.yaml        ✅
│   │   ├── callouts.yaml       ✅
│   │   └── styles.yaml         ✅
│   │
│   ├── templates/
│   │   ├── callouts.typ        ✅
│   │   ├── cover.typ           ✅
│   │   ├── toc.typ             ✅
│   │   ├── volume.typ          ✅
│   │   └── consolidated.typ    ✅
│   │
│   ├── filters/
│   │   ├── callouts.lua        ✅
│   │   ├── figures.lua         ✅
│   │   └── cross-refs.lua      ✅
│   │
│   ├── scripts/
│   │   ├── generate.py         ✅
│   │   ├── validate.py         ✅
│   │   └── utils.py            ✅
│   │
│   ├── output/
│   │   ├── volumes/
│   │   │   ├── Volume_I_*.pdf  ✅
│   │   │   ├── Volume_II_*.pdf ✅
│   │   │   ├── Volume_III_*.pdf ✅
│   │   │   ├── Volume_IV_*.pdf ✅
│   │   │   └── Volume_V_*.pdf  ✅
│   │   │
│   │   └── consolidated/
│   │       └── LEntreprise_Agentique_Monographie_Complete.pdf ✅
│   │
│   └── README.md               ✅
│
├── PDR.md                      ✅
├── PLAN.md                     ✅ (ce document)
└── TOC.md
```

---

*Fin du Plan d'Implémentation — Version 1.0*
