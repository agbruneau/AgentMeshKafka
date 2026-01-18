# PDF Generator — L'Entreprise Agentique

Génération de publications PDF professionnelles pour la monographie "L'Entreprise Agentique".

---

## Table des Matières

1. [Aperçu](#aperçu)
2. [Prérequis](#prérequis)
3. [Structure des Fichiers](#structure-des-fichiers)
4. [Génération des PDFs](#génération-des-pdfs)
5. [Workflow Détaillé](#workflow-détaillé)
6. [Personnalisation](#personnalisation)
7. [Dépannage](#dépannage)

---

## Aperçu

Cette application génère des publications PDF à partir des 81 chapitres Markdown de la monographie, répartis en 5 volumes :

| Volume | Titre | Chapitres | Pages | Couleur |
|--------|-------|-----------|-------|---------|
| **I** | Fondations de l'Entreprise Agentique | 28 | 226 | Bleu marine |
| **II** | Infrastructure Agentique | 15 | 351 | Vert forêt |
| **III** | Apache Kafka — Guide de l'Architecte | 12 | 426 | Brun |
| **IV** | Apache Iceberg — Le Lakehouse Moderne | 18 | 550 | Violet |
| **V** | Le Développeur Renaissance | 10 | 239 | Bordeaux |

### Sorties Disponibles

- **5 volumes individuels** : Un PDF par volume avec couverture, TOC et chapitres
- **Monographie consolidée** : PDF unique de 1 795 pages avec couverture globale et navigation

---

## Prérequis

### Logiciels Requis

| Logiciel | Version | Installation Windows |
|----------|---------|----------------------|
| **Python** | 3.10+ | `winget install Python.Python.3.12` |
| **Pandoc** | 3.0+ | `winget install jgm.Pandoc` |
| **Typst** | 0.11+ | `winget install Typst.Typst` |

### Vérification des Versions

```bash
python --version    # Doit afficher 3.10+
pandoc --version    # Doit afficher 3.0+
typst --version     # Doit afficher 0.11+
```

### Dépendances Python

```bash
pip install pypdf pyyaml
```

---

## Structure des Fichiers

```
pdf-generator/
├── output/
│   ├── volumes/                          # PDFs individuels
│   │   ├── Volume_I_Fondations_Entreprise_Agentique.pdf
│   │   ├── Volume_II_Infrastructure_Agentique.pdf
│   │   ├── Volume_III_Apache_Kafka_Guide_Architecte.pdf
│   │   ├── Volume_IV_Apache_Iceberg_Lakehouse.pdf
│   │   └── Volume_V_Le_Développeur_Renaissance.pdf
│   │
│   └── consolidated/                     # Monographie complète
│       └── Entreprise_Agentique_Monographie_Complete.pdf
│
├── templates/                            # Templates Typst
│   ├── volume.typ                        # Template principal
│   ├── cover.typ                         # Page de couverture
│   └── callouts.typ                      # Styles des encadrés
│
├── config/                               # Configuration
│   ├── volumes.yaml                      # Métadonnées des volumes
│   ├── callouts.yaml                     # Types de callouts
│   └── styles.yaml                       # Styles visuels
│
├── filters/                              # Filtres Pandoc Lua
│   ├── callouts.lua                      # Transformation blockquotes
│   └── figures.lua                       # Gestion tableaux
│
└── README.md                             # Ce fichier
```

---

## Génération des PDFs

### Méthode Rapide — Script Complet

Pour régénérer tous les PDFs, exécuter les commandes suivantes depuis la racine du projet :

```bash
# 1. Générer un volume individuel (exemple: Volume IV)
cd FondationEntepriseAgentique

# Convertir Markdown → Typst
pandoc Volume_IV_Apache_Iceberg_Lakehouse/Partie_*/**/*.md \
       Volume_IV_Apache_Iceberg_Lakehouse/Annexes/*.md \
       -t typst -o temp_content.typ

# Ajouter la définition horizontalrule au début du fichier
# (voir section Workflow Détaillé)

# Compiler Typst → PDF
typst compile Volume_IV_Main.typ pdf-generator/output/volumes/Volume_IV.pdf
```

### Génération Complète avec Python

```python
from pypdf import PdfReader, PdfWriter
from pathlib import Path

# Fusionner les 5 volumes
volumes = [
    "Volume_I_Fondations_Entreprise_Agentique.pdf",
    "Volume_II_Infrastructure_Agentique.pdf",
    "Volume_III_Apache_Kafka_Guide_Architecte.pdf",
    "Volume_IV_Apache_Iceberg_Lakehouse.pdf",
    "Volume_V_Le_Développeur_Renaissance.pdf",
]

writer = PdfWriter()
for vol in volumes:
    reader = PdfReader(f"pdf-generator/output/volumes/{vol}")
    for page in reader.pages:
        writer.add_page(page)

with open("pdf-generator/output/consolidated/Monographie.pdf", "wb") as f:
    writer.write(f)
```

---

## Workflow Détaillé

### Étape 1 : Conversion Markdown → Typst

Pour chaque volume, convertir les fichiers Markdown en Typst avec Pandoc :

```bash
pandoc \
  "Volume_I_.../Introduction.md" \
  "Volume_I_.../Partie_1/.../Chapitre_I.1_....md" \
  "Volume_I_.../Partie_1/.../Chapitre_I.2_....md" \
  # ... tous les chapitres dans l'ordre
  -t typst \
  -o volume_content.typ
```

### Étape 2 : Ajouter la Fonction horizontalrule

Pandoc génère des appels à `#horizontalrule` pour les séparateurs `---`. Ajouter cette définition au début du fichier `.typ` :

```typst
// Fonctions Pandoc requises
#let horizontalrule = {
  v(0.5em)
  line(length: 100%, stroke: 0.5pt + luma(200))
  v(0.5em)
}
```

### Étape 3 : Créer le Document Principal

Créer un fichier `Volume_X_Main.typ` avec le style et la structure :

```typst
// Configuration
#let theme-color = rgb("#1E3A5F")  // Couleur du volume

#set document(title: "Volume I — Titre", author: "Auteur")
#set page(paper: "a4", margin: (top: 2.5cm, bottom: 2.5cm, left: 2.5cm, right: 2cm))
#set text(font: "Libertinus Serif", size: 11pt, lang: "fr")

// Styles des titres
#show heading.where(level: 1): it => {
  pagebreak(weak: true)
  block(fill: theme-color.lighten(90%), inset: 1em, radius: 4pt, width: 100%,
    text(size: 20pt, weight: "bold", fill: theme-color)[#it.body])
}

// ... autres styles ...

// Page de couverture
// ... (voir templates/cover.typ)

// Table des matières
#outline(title: "Table des Matières", indent: 1.5em, depth: 3)

// Contenu
#include "volume_content.typ"
```

### Étape 4 : Compiler avec Typst

```bash
typst compile Volume_X_Main.typ output/volumes/Volume_X.pdf
```

### Étape 5 : Fusionner pour la Monographie Consolidée

```python
from pypdf import PdfReader, PdfWriter

writer = PdfWriter()

# Ajouter couverture et TOC
reader_cover = PdfReader("cover_toc.pdf")
for page in reader_cover.pages:
    writer.add_page(page)

# Ajouter les 5 volumes
for vol_file in volume_files:
    reader = PdfReader(vol_file)
    for page in reader.pages:
        writer.add_page(page)

# Ajouter les signets de navigation
writer.add_outline_item("Volume I", 3)
writer.add_outline_item("Volume II", 229)
# ...

with open("Monographie_Complete.pdf", "wb") as f:
    writer.write(f)
```

---

## Personnalisation

### Couleurs des Volumes

| Volume | Code Couleur | Nom |
|--------|--------------|-----|
| I | `#1E3A5F` | Bleu marine |
| II | `#2D5016` | Vert forêt |
| III | `#8B4513` | Brun |
| IV | `#4A0080` | Violet |
| V | `#8B0000` | Bordeaux |

### Styles des Callouts

Les callouts sont stylisés via `#show quote` dans Typst :

```typst
#show quote: it => {
  block(
    fill: luma(248),
    inset: (left: 1em, right: 0.8em, top: 0.6em, bottom: 0.6em),
    radius: 4pt,
    stroke: (left: 3pt + theme-color),
    width: 100%,
    text(size: 10.5pt)[#it.body]
  )
}
```

### Types de Callouts par Volume

**Universels** : `> **Définition formelle**`, `> **Perspective stratégique**`, `> **Exemple concret**`

**Volume II** : `> **Note technique**`, `> **Bonnes pratiques**`, `> **Attention**`

**Volume III** : `> **Note de terrain**`, `> **Décision architecturale**`, `> **Anti-patron**`

**Volume IV** : `> **Étude de cas : [Nom]**`, `> **Migration : [Titre]**`, `> **Performance**`

**Volume V** : `> **Figure historique : [Nom]**`, `> **Réflexion**`, `> **Manifeste**`

---

## Dépannage

### Erreur : `unknown variable: horizontalrule`

**Cause** : Le fichier Typst généré par Pandoc utilise `#horizontalrule` mais la fonction n'est pas définie.

**Solution** : Ajouter au début du fichier `.typ` :
```typst
#let horizontalrule = {
  v(0.5em)
  line(length: 100%, stroke: 0.5pt + luma(200))
  v(0.5em)
}
```

### Erreur : `maximum show rule depth exceeded`

**Cause** : Une règle `show` crée une récursion infinie (ex: `show line` qui appelle `line`).

**Solution** : Ne pas utiliser `show line` pour styliser les lignes. Utiliser une fonction personnalisée à la place.

### Caractères Spéciaux Mal Affichés

**Cause** : Problème d'encodage UTF-8.

**Solution** :
1. Vérifier que tous les fichiers Markdown sont en UTF-8
2. Utiliser `lang: "fr", region: "CA"` dans la configuration Typst

### PDF Trop Petit (quelques Ko)

**Cause** : Le template Pandoc n'inclut pas correctement le contenu.

**Solution** : Utiliser l'approche en deux étapes :
1. Convertir Markdown → Typst brut (`pandoc -t typst`)
2. Créer un fichier principal qui `#include` le contenu

### Polices Non Trouvées

**Cause** : Les polices spécifiées ne sont pas installées.

**Solution** : Installer les polices ou utiliser des alternatives :
- `Libertinus Serif` → Alternative : `Linux Libertine`
- `Consolas` → Alternative : `Fira Code`, `JetBrains Mono`

---

## Fichiers de Sortie Actuels

### Volumes Individuels

| Fichier | Taille | Pages |
|---------|--------|-------|
| `Volume_I_Fondations_Entreprise_Agentique.pdf` | 1.6 Mo | 226 |
| `Volume_II_Infrastructure_Agentique.pdf` | 2.4 Mo | 351 |
| `Volume_III_Apache_Kafka_Guide_Architecte.pdf` | 2.8 Mo | 426 |
| `Volume_IV_Apache_Iceberg_Lakehouse.pdf` | 3.6 Mo | 550 |
| `Volume_V_Le_Développeur_Renaissance.pdf` | 1.7 Mo | 239 |

### Monographie Consolidée

| Fichier | Taille | Pages |
|---------|--------|-------|
| `Entreprise_Agentique_Monographie_Complete.pdf` | 12 Mo | 1 795 |

**Contenu** :
- Page 1 : Couverture principale
- Pages 2-3 : Table des matières avec liens
- Pages 4-1795 : Les 5 volumes avec signets de navigation

---

## Technologies Utilisées

- **[Pandoc](https://pandoc.org/)** : Conversion Markdown → Typst
- **[Typst](https://typst.app/)** : Composition et génération PDF
- **[pypdf](https://pypdf.readthedocs.io/)** : Manipulation et fusion des PDFs
- **Python 3** : Scripts d'automatisation

---

*Dernière mise à jour : Janvier 2026*
