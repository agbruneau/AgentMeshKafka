# PDR — Plan de Développement et Réalisation

## Application de Génération PDF « L'Entreprise Agentique »

---

**Version** : 1.0
**Date** : Janvier 2026
**Auteur** : André-Guy Bruneau
**Statut** : En développement

---

## Table des Matières

1. [Contexte et Objectifs](#1-contexte-et-objectifs)
2. [Architecture Technique](#2-architecture-technique)
3. [Spécifications Fonctionnelles](#3-spécifications-fonctionnelles)
4. [Configuration des Volumes](#4-configuration-des-volumes)
5. [Système de Callouts](#5-système-de-callouts)
6. [Templates Typst](#6-templates-typst)
7. [Filtres Pandoc Lua](#7-filtres-pandoc-lua)
8. [Scripts de Génération](#8-scripts-de-génération)
9. [Critères d'Acceptation](#9-critères-dacceptation)
10. [Dépendances et Prérequis](#10-dépendances-et-prérequis)

---

## 1. Contexte et Objectifs

### 1.1 Description du Projet

L'application **pdf-generator** a pour mission de produire des publications PDF professionnelles à partir de la monographie « L'Entreprise Agentique ». Cette monographie comprend :

- **5 volumes** distincts
- **81 chapitres** au total
- **89 fichiers Markdown** sources
- **15+ types de callouts** spécialisés

### 1.2 Objectifs de Production

| Mode | Description | Sortie |
|------|-------------|--------|
| **Volume individuel** | Générer un PDF par volume | 5 fichiers PDF |
| **Volume consolidé** | Générer la monographie complète | 1 fichier PDF |
| **Chapitre unique** | Générer un chapitre spécifique | 1 fichier PDF |

### 1.3 Style Cible

Le design s'inspire du package [modern-technique-report](https://typst.app/universe/package/modern-technique-report) avec :

- Couverture professionnelle avec titre et sous-titre
- Table des matières automatique avec hyperliens
- En-têtes et pieds de page cohérents
- Encadrés colorés (callouts) pour différents types de contenu
- Typographie académique (Libertinus Serif, Fira Code)

---

## 2. Architecture Technique

### 2.1 Choix Technologique — Scénario Hybride Pandoc + Typst

**Justification** :

1. **Pandoc** gère le parsing Markdown complexe (tableaux, listes imbriquées, code)
2. **Filtres Lua** transforment les blockquotes en callouts Typst natifs
3. **Typst** compile rapidement (~27x plus rapide que XeLaTeX)
4. **Maintenance raisonnable** (~500-700 lignes de code total)

### 2.2 Flux de Génération

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Fichiers .md   │────▶│  Pandoc + Lua   │────▶│   Fichier .typ  │
│  (89 sources)   │     │  (filtres)      │     │   (intermédiaire)│
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   Fichier PDF   │◀────│     Typst       │
                        │   (final)       │     │   (compilation) │
                        └─────────────────┘     └─────────────────┘
```

### 2.3 Structure des Répertoires

```
Monographie/
├── pdf-generator/
│   ├── config/
│   │   ├── volumes.yaml        # Métadonnées des 5 volumes
│   │   ├── callouts.yaml       # 15+ types de callouts
│   │   └── styles.yaml         # Couleurs, polices, marges
│   │
│   ├── templates/
│   │   ├── volume.typ          # Template principal par volume
│   │   ├── cover.typ           # Page de couverture
│   │   ├── callouts.typ        # Définitions des encadrés
│   │   ├── toc.typ             # Table des matières
│   │   └── consolidated.typ    # Template monographie complète
│   │
│   ├── filters/
│   │   ├── callouts.lua        # Transformation blockquotes → Typst
│   │   ├── figures.lua         # Gestion tableaux/figures
│   │   └── cross-refs.lua      # Références inter-volumes
│   │
│   ├── scripts/
│   │   ├── generate.py         # Script principal CLI
│   │   ├── validate.py         # Validation pré-génération
│   │   └── utils.py            # Utilitaires partagés
│   │
│   ├── assets/
│   │   └── fonts/              # Polices (optionnel si système)
│   │
│   ├── output/
│   │   ├── volumes/            # PDFs individuels
│   │   └── consolidated/       # PDF complet
│   │
│   └── README.md               # Documentation utilisateur
│
├── PDR.md                      # Ce document
├── PLAN.md                     # Plan d'implémentation
└── TOC.md                      # Table des matières source
```

---

## 3. Spécifications Fonctionnelles

### 3.1 Interface en Ligne de Commande (CLI)

```bash
# Générer un volume spécifique
python scripts/generate.py --volume I

# Générer tous les volumes
python scripts/generate.py --volume all

# Générer en parallèle (multi-threading)
python scripts/generate.py --volume all --parallel

# Générer la monographie consolidée
python scripts/generate.py --consolidated

# Générer un chapitre spécifique
python scripts/generate.py --chapter III.1

# Mode verbose avec logs détaillés
python scripts/generate.py --volume I --verbose

# Validation sans génération
python scripts/generate.py --validate --volume I
```

### 3.2 Options CLI Détaillées

| Option | Description | Valeurs |
|--------|-------------|---------|
| `--volume` | Volume(s) à générer | `I`, `II`, `III`, `IV`, `V`, `all` |
| `--consolidated` | Mode monographie complète | Flag booléen |
| `--chapter` | Chapitre spécifique | Format `VOL.NUM` (ex: `III.1`) |
| `--parallel` | Génération multi-thread | Flag booléen |
| `--validate` | Validation uniquement | Flag booléen |
| `--verbose` | Logs détaillés | Flag booléen |
| `--output` | Répertoire de sortie | Chemin personnalisé |
| `--draft` | Mode brouillon (filigrane) | Flag booléen |

### 3.3 Sorties Attendues

**Mode Volume Individuel** :
```
output/volumes/
├── Volume_I_Fondations_Entreprise_Agentique.pdf
├── Volume_II_Infrastructure_Agentique.pdf
├── Volume_III_Apache_Kafka_Guide_Architecte.pdf
├── Volume_IV_Apache_Iceberg_Lakehouse.pdf
└── Volume_V_Developpeur_Renaissance.pdf
```

**Mode Consolidé** :
```
output/consolidated/
└── LEntreprise_Agentique_Monographie_Complete.pdf
```

---

## 4. Configuration des Volumes

### 4.1 Structure `volumes.yaml`

```yaml
# Configuration des 5 volumes de la monographie

monograph:
  title: "L'Entreprise Agentique"
  author: "André-Guy Bruneau"
  year: 2026
  language: "fr"

volumes:
  I:
    title: "Fondations de l'Entreprise Agentique"
    subtitle: "De l'Interopérabilité à l'Intelligence Distribuée"
    color: "#1E3A5F"  # Bleu profond
    directory: "Volume_I_Fondations_Entreprise_Agentique"
    parts:
      - name: "Introduction"
        chapters:
          - file: "Introduction_Metamorphose.md"
            title: "Métamorphose"
      - name: "Partie 1 : La Crise de l'Intégration"
        chapters:
          - file: "Partie_1_Crise_Integration/Chapitre_I.1_Crise_Integration_Systemique.md"
            title: "Crise de l'Intégration Systémique"
          - file: "Partie_1_Crise_Integration/Chapitre_I.2_Fondements_Dimensions_Interoperabilite.md"
            title: "Fondements et Dimensions de l'Interopérabilité"
          - file: "Partie_1_Crise_Integration/Chapitre_I.3_Cadres_Reference_Standards_Maturite.md"
            title: "Cadres de Référence et Modèles de Maturité"
      # ... autres parties et chapitres
    chapter_count: 28

  II:
    title: "Infrastructure Agentique"
    subtitle: "Concevoir et Opérer le Maillage d'Événements Intelligent"
    color: "#2D5016"  # Vert forêt
    directory: "Volume_II_Infrastructure_Agentique"
    chapter_count: 15

  III:
    title: "Apache Kafka — Guide de l'Architecte"
    subtitle: "Maîtriser la Plateforme de Streaming Événementiel"
    color: "#8B4513"  # Brun Kafka
    directory: "Volume_III_Apache_Kafka_Guide_Architecte"
    chapter_count: 12

  IV:
    title: "Apache Iceberg — Le Lakehouse Moderne"
    subtitle: "Architecture, Conception et Opérations du Data Lakehouse"
    color: "#4A148C"  # Violet Iceberg
    directory: "Volume_IV_Apache_Iceberg_Lakehouse"
    chapter_count: 18  # 16 chapitres + 2 annexes

  V:
    title: "Le Développeur Renaissance"
    subtitle: "Capital Humain et Excellence à l'Ère de l'IA"
    color: "#B8860B"  # Or Renaissance
    directory: "Volume_V_Developpeur_Renaissance"
    chapter_count: 10
```

### 4.2 Métadonnées par Volume

Chaque volume inclut :

- **Titre et sous-titre** : Affichés sur la couverture
- **Couleur thématique** : Utilisée pour les accents visuels
- **Répertoire source** : Chemin relatif depuis `Monographie/`
- **Structure des parties** : Organisation hiérarchique des chapitres
- **Nombre de chapitres** : Pour validation

---

## 5. Système de Callouts

### 5.1 Types de Callouts

#### Callouts Universels (tous volumes)

| Type | Syntaxe Markdown | Couleur | Icône |
|------|------------------|---------|-------|
| Définition formelle | `> **Définition formelle**` | Bleu (#E3F2FD) | 📖 |
| Perspective stratégique | `> **Perspective stratégique**` | Vert (#E8F5E9) | 🎯 |
| Exemple concret | `> **Exemple concret**` | Orange (#FFF3E0) | 💡 |

#### Callouts Volume II (Infrastructure)

| Type | Syntaxe Markdown | Couleur | Icône |
|------|------------------|---------|-------|
| Note technique | `> **Note technique**` | Gris (#ECEFF1) | ⚙️ |
| Bonnes pratiques | `> **Bonnes pratiques**` | Vert clair (#C8E6C9) | ✅ |
| Attention | `> **Attention**` | Rouge (#FFEBEE) | ⚠️ |

#### Callouts Volume III (Kafka)

| Type | Syntaxe Markdown | Structure |
|------|------------------|-----------|
| Note de terrain | `> **Note de terrain**` | Contexte / Défi / Solution / Leçon |
| Décision architecturale | `> **Décision architecturale**` | Contexte / Analyse / Décision / Justification |
| Anti-patron | `> **Anti-patron**` | Description de l'erreur et alternative |

#### Callouts Volume IV (Iceberg)

| Type | Syntaxe Markdown | Structure |
|------|------------------|-----------|
| Étude de cas : [Nom] | `> **Étude de cas : [Nom]**` | Secteur / Défi / Solution / Résultats |
| Migration : [Titre] | `> **Migration : [Titre]**` | De / Vers / Stratégie / Résultats |
| Performance : [Titre] | `> **Performance : [Titre]**` | Métriques et benchmarks |

#### Callouts Volume V (Renaissance)

| Type | Syntaxe Markdown | Structure |
|------|------------------|-----------|
| Figure historique : [Nom] | `> **Figure historique : [Nom]**` | Époque / Domaines / Contribution / Leçon |
| Réflexion | `> **Réflexion**` | Question introspective |
| Manifeste | `> **Manifeste**` | Principe directeur |

### 5.2 Structure `callouts.yaml`

```yaml
# Configuration des 15+ types de callouts

defaults:
  border_radius: 4pt
  padding: 12pt
  margin_top: 8pt
  margin_bottom: 8pt

callouts:
  # ═══════════════════════════════════════════════════════════
  # CALLOUTS UNIVERSELS (tous volumes)
  # ═══════════════════════════════════════════════════════════

  definition_formelle:
    pattern: "^\\*\\*Définition formelle\\*\\*"
    title: "Définition formelle"
    icon: "📖"
    colors:
      background: "#E3F2FD"
      border: "#1976D2"
      title: "#0D47A1"
    structured: false

  perspective_strategique:
    pattern: "^\\*\\*Perspective stratégique\\*\\*"
    title: "Perspective stratégique"
    icon: "🎯"
    colors:
      background: "#E8F5E9"
      border: "#388E3C"
      title: "#1B5E20"
    structured: false

  exemple_concret:
    pattern: "^\\*\\*Exemple concret\\*\\*"
    title: "Exemple concret"
    icon: "💡"
    colors:
      background: "#FFF3E0"
      border: "#F57C00"
      title: "#E65100"
    structured: false

  # ═══════════════════════════════════════════════════════════
  # CALLOUTS VOLUME II (Infrastructure)
  # ═══════════════════════════════════════════════════════════

  note_technique:
    pattern: "^\\*\\*Note technique\\*\\*"
    title: "Note technique"
    icon: "⚙️"
    colors:
      background: "#ECEFF1"
      border: "#607D8B"
      title: "#37474F"
    structured: false

  bonnes_pratiques:
    pattern: "^\\*\\*Bonnes pratiques\\*\\*"
    title: "Bonnes pratiques"
    icon: "✅"
    colors:
      background: "#C8E6C9"
      border: "#4CAF50"
      title: "#2E7D32"
    structured: false

  attention:
    pattern: "^\\*\\*Attention\\*\\*"
    title: "Attention"
    icon: "⚠️"
    colors:
      background: "#FFEBEE"
      border: "#F44336"
      title: "#C62828"
    structured: false

  # ═══════════════════════════════════════════════════════════
  # CALLOUTS VOLUME III (Kafka)
  # ═══════════════════════════════════════════════════════════

  note_de_terrain:
    pattern: "^\\*\\*Note de terrain\\*\\*"
    title: "Note de terrain"
    icon: "🏗️"
    colors:
      background: "#FFF8E1"
      border: "#FFA000"
      title: "#FF6F00"
    structured: true
    fields:
      - "Contexte"
      - "Défi"
      - "Solution"
      - "Leçon"

  decision_architecturale:
    pattern: "^\\*\\*Décision architecturale\\*\\*"
    title: "Décision architecturale"
    icon: "🏛️"
    colors:
      background: "#E8EAF6"
      border: "#3F51B5"
      title: "#1A237E"
    structured: true
    fields:
      - "Contexte"
      - "Analyse"
      - "Décision"
      - "Justification"

  anti_patron:
    pattern: "^\\*\\*Anti-patron\\*\\*"
    title: "Anti-patron"
    icon: "🚫"
    colors:
      background: "#FCE4EC"
      border: "#E91E63"
      title: "#880E4F"
    structured: false

  # ═══════════════════════════════════════════════════════════
  # CALLOUTS VOLUME IV (Iceberg)
  # ═══════════════════════════════════════════════════════════

  etude_de_cas:
    pattern: "^\\*\\*Étude de cas\\s*:\\s*(.+?)\\*\\*"
    title_template: "Étude de cas : {1}"
    icon: "📊"
    colors:
      background: "#E1F5FE"
      border: "#03A9F4"
      title: "#01579B"
    structured: true
    fields:
      - "Secteur"
      - "Défi"
      - "Solution"
      - "Résultats"

  migration:
    pattern: "^\\*\\*Migration\\s*:\\s*(.+?)\\*\\*"
    title_template: "Migration : {1}"
    icon: "🔄"
    colors:
      background: "#F3E5F5"
      border: "#9C27B0"
      title: "#4A148C"
    structured: true
    fields:
      - "De"
      - "Vers"
      - "Stratégie"
      - "Résultats"

  performance:
    pattern: "^\\*\\*Performance\\s*:\\s*(.+?)\\*\\*"
    title_template: "Performance : {1}"
    icon: "📈"
    colors:
      background: "#E0F7FA"
      border: "#00BCD4"
      title: "#006064"
    structured: false

  # ═══════════════════════════════════════════════════════════
  # CALLOUTS VOLUME V (Renaissance)
  # ═══════════════════════════════════════════════════════════

  figure_historique:
    pattern: "^\\*\\*Figure historique\\s*:\\s*(.+?)\\*\\*"
    title_template: "Figure historique : {1}"
    icon: "🎨"
    colors:
      background: "#FFF9C4"
      border: "#FBC02D"
      title: "#F57F17"
    structured: true
    fields:
      - "Époque"
      - "Domaines"
      - "Contribution"
      - "Leçon pour aujourd'hui"

  reflexion:
    pattern: "^\\*\\*Réflexion\\*\\*"
    title: "Réflexion"
    icon: "🤔"
    colors:
      background: "#F5F5F5"
      border: "#9E9E9E"
      title: "#424242"
    structured: false

  manifeste:
    pattern: "^\\*\\*Manifeste\\*\\*"
    title: "Manifeste"
    icon: "📜"
    colors:
      background: "#EFEBE9"
      border: "#795548"
      title: "#3E2723"
    structured: false
```

---

## 6. Templates Typst

### 6.1 Template Principal (`volume.typ`)

Le template principal gère :

- **Métadonnées du document** : Titre, auteur, date
- **Configuration de page** : Format A4, marges, numérotation
- **Import des composants** : Callouts, couverture, TOC
- **Styles typographiques** : Titres, paragraphes, code

### 6.2 Template Couverture (`cover.typ`)

La couverture inclut :

- Logo ou élément graphique (optionnel)
- Titre du volume
- Sous-titre
- Auteur
- Numéro de volume (I à V)
- Année de publication

### 6.3 Template Callouts (`callouts.typ`)

Basé sur le package **showybox** 2.0.4 :

```typst
#import "@preview/showybox:2.0.4": showybox

#let callout-definition(body) = showybox(
  frame: (
    border-color: rgb("#1976D2"),
    thickness: 1.5pt,
    radius: 4pt
  ),
  title-style: (
    color: rgb("#0D47A1"),
    weight: "bold"
  ),
  body-style: (
    color: black
  ),
  shadow: (
    offset: 2pt
  ),
  title: [📖 Définition formelle],
  body
)
```

### 6.4 Template Consolidé (`consolidated.typ`)

Pour la monographie complète :

- Page de titre globale
- Table des matières générale
- Séparateurs entre volumes
- Numérotation de page continue
- Index global (optionnel)

---

## 7. Filtres Pandoc Lua

### 7.1 Filtre `callouts.lua`

**Responsabilités** :

1. Détecter les blockquotes avec pattern de callout
2. Extraire le type et le contenu
3. Générer le code Typst correspondant
4. Gérer les callouts structurés (champs nommés)

**Algorithme** :

```lua
function BlockQuote(el)
  -- 1. Extraire le premier paragraphe
  local first_para = el.content[1]

  -- 2. Vérifier si c'est un callout connu
  local callout_type = detect_callout_type(first_para)

  if callout_type then
    -- 3. Extraire le contenu (sans la ligne de titre)
    local content = extract_content(el.content)

    -- 4. Générer le RawBlock Typst
    return pandoc.RawBlock('typst',
      generate_typst_callout(callout_type, content))
  end

  return el
end
```

### 7.2 Filtre `figures.lua`

**Responsabilités** :

1. Numéroter automatiquement les tableaux
2. Gérer les légendes
3. Créer des références croisées

### 7.3 Filtre `cross-refs.lua`

**Responsabilités** :

1. Détecter les références inter-volumes (`Volume I`, `Chapitre III.5`)
2. Générer des hyperliens internes
3. Maintenir un registre des références

---

## 8. Scripts de Génération

### 8.1 Script Principal (`generate.py`)

```python
#!/usr/bin/env python3
"""
generate.py - Script principal de génération PDF

Usage:
    python generate.py --volume I
    python generate.py --volume all --parallel
    python generate.py --consolidated
"""

import argparse
import subprocess
import yaml
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

class PDFGenerator:
    def __init__(self, config_dir: Path):
        self.config = self.load_config(config_dir)

    def generate_volume(self, volume_id: str) -> Path:
        """Génère un PDF pour un volume spécifique."""
        pass

    def generate_consolidated(self) -> Path:
        """Génère la monographie complète."""
        pass

    def validate(self, volume_id: str) -> bool:
        """Valide la structure d'un volume."""
        pass
```

### 8.2 Script de Validation (`validate.py`)

Vérifie avant génération :

- Existence de tous les fichiers référencés
- Syntaxe Markdown valide
- Callouts reconnus
- Cohérence des références croisées

---

## 9. Critères d'Acceptation

### 9.1 Critères Fonctionnels

| ID | Critère | Vérification |
|----|---------|--------------|
| F1 | Génération des 5 volumes individuels | 5 PDFs créés sans erreur |
| F2 | Génération de la monographie consolidée | 1 PDF avec tous les volumes |
| F3 | Table des matières fonctionnelle | Hyperliens vers chapitres |
| F4 | Tous les callouts rendus correctement | Inspection visuelle |
| F5 | Tableaux Markdown convertis | Mise en forme correcte |
| F6 | Blocs de code avec coloration | Syntaxe highlighting |
| F7 | En-têtes et pieds de page | Titre volume + numéro page |

### 9.2 Critères de Qualité

| ID | Critère | Seuil |
|----|---------|-------|
| Q1 | Temps de génération par volume | < 60 secondes |
| Q2 | Taille PDF par volume | < 15 MB |
| Q3 | Résolution des images | 300 DPI minimum |
| Q4 | Accessibilité PDF | Tags de structure présents |

### 9.3 Critères Techniques

| ID | Critère | Vérification |
|----|---------|--------------|
| T1 | Pas d'erreur Pandoc | Exit code 0 |
| T2 | Pas d'erreur Typst | Exit code 0 |
| T3 | Logs de génération | Fichier de log créé |
| T4 | Mode verbose fonctionnel | Logs détaillés affichés |

---

## 10. Dépendances et Prérequis

### 10.1 Logiciels Requis

| Logiciel | Version Minimum | Usage |
|----------|-----------------|-------|
| **Python** | 3.10+ | Scripts de génération |
| **Pandoc** | 3.0+ | Conversion Markdown |
| **Typst** | 0.11+ | Compilation PDF |
| **PyYAML** | 6.0+ | Lecture configuration |

### 10.2 Packages Typst

| Package | Version | Usage |
|---------|---------|-------|
| **showybox** | 2.0.4 | Encadrés callouts |

### 10.3 Installation

```bash
# Windows (avec winget)
winget install Python.Python.3.12
winget install jgm.Pandoc
winget install Typst.Typst

# Vérification
python --version    # 3.10+
pandoc --version    # 3.0+
typst --version     # 0.11+

# Dépendances Python
pip install pyyaml
```

### 10.4 Polices Recommandées

- **Libertinus Serif** : Corps de texte
- **Fira Code** : Blocs de code
- **Noto Sans** : Sans-serif (titres)

---

## Annexe A — Mapping Callouts Markdown → Typst

| Markdown Source | Fonction Typst |
|-----------------|----------------|
| `> **Définition formelle**` | `#callout-definition()` |
| `> **Perspective stratégique**` | `#callout-strategic()` |
| `> **Exemple concret**` | `#callout-example()` |
| `> **Note technique**` | `#callout-technical()` |
| `> **Note de terrain**` | `#callout-field-note()` |
| `> **Décision architecturale**` | `#callout-decision()` |
| `> **Anti-patron**` | `#callout-antipattern()` |
| `> **Étude de cas : X**` | `#callout-case-study("X")` |
| `> **Migration : X**` | `#callout-migration("X")` |
| `> **Performance : X**` | `#callout-performance("X")` |
| `> **Figure historique : X**` | `#callout-historical("X")` |
| `> **Réflexion**` | `#callout-reflection()` |
| `> **Manifeste**` | `#callout-manifesto()` |

---

## Annexe B — Exemple de Sortie Typst

```typst
#import "callouts.typ": *

= Chapitre III.1 — Découvrir Kafka en tant qu'Architecte

== III.1.1 La Perspective de l'Architecte sur Kafka

L'architecte pose des questions d'un ordre différent...

#callout-definition[
  La *perspective architecturale* sur une technologie se distingue
  de la perspective d'implémentation par son horizon temporel
  (années plutôt que sprints), son périmètre (système d'information
  global plutôt que composant isolé)...
]

#callout-field-note(
  contexte: "FinServ, entreprise de services financiers, 3 000 employés",
  defi: "Architecture d'intégration vieillissante basée sur IBM MQ",
  solution: "Modernisation via Apache Kafka",
  lecon: "La dette cognitive est systématiquement sous-estimée"
)
```

---

*Fin du PDR — Version 1.0*
