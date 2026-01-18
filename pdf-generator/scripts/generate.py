#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate.py — Script principal de génération PDF

Ce script génère des PDFs de la monographie "L'Entreprise Agentique" :
- Volumes individuels (I à V)
- Monographie consolidée complète

Usage:
    python generate.py --volume I
    python generate.py --volume all --parallel
    python generate.py --consolidated
"""

import argparse
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from utils import (
    get_project_root,
    get_monograph_root,
    get_templates_dir,
    get_filters_dir,
    get_output_dir,
    load_volumes_config,
    parse_volume_config,
    collect_markdown_files,
    concatenate_markdown_files,
    ensure_directory,
    check_dependencies,
    generate_output_filename,
    generate_consolidated_filename,
    setup_logging,
    print_header,
    print_success,
    print_error,
    print_warning,
    print_info,
    get_timestamp,
    Volume,
)


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

VOLUME_COLORS = {
    "I": "#1E3A5F",
    "II": "#2D5016",
    "III": "#8B4513",
    "IV": "#4A148C",
    "V": "#B8860B",
}


# ═══════════════════════════════════════════════════════════════════════════════
# GÉNÉRATION PANDOC
# ═══════════════════════════════════════════════════════════════════════════════

def run_pandoc(
    input_file: Path,
    output_file: Path,
    filters: List[Path],
    verbose: bool = False
) -> bool:
    """
    Exécute Pandoc pour convertir Markdown en Typst.

    Args:
        input_file: Fichier Markdown source
        output_file: Fichier Typst de sortie
        filters: Liste des filtres Lua à appliquer
        verbose: Mode verbose

    Returns:
        True si succès, False sinon
    """
    cmd = [
        'pandoc',
        str(input_file),
        '--to=typst',
        f'--output={output_file}',
        '--wrap=preserve',
    ]

    # Ajouter les filtres
    for filter_path in filters:
        cmd.extend(['--lua-filter', str(filter_path)])

    if verbose:
        print_info(f"Exécution : {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        if result.returncode != 0:
            print_error(f"Erreur Pandoc : {result.stderr}")
            return False

        if verbose and result.stderr:
            print_warning(f"Warnings Pandoc : {result.stderr}")

        return True

    except FileNotFoundError:
        print_error("Pandoc non trouvé. Veuillez l'installer.")
        return False
    except Exception as e:
        print_error(f"Erreur lors de l'exécution de Pandoc : {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# GÉNÉRATION TYPST
# ═══════════════════════════════════════════════════════════════════════════════

def create_volume_typst(
    volume: Volume,
    content_file: Path,
    output_file: Path,
    templates_dir: Path
) -> Path:
    """
    Crée le fichier Typst complet pour un volume.

    Args:
        volume: Configuration du volume
        content_file: Fichier avec le contenu converti
        output_file: Fichier Typst de sortie
        templates_dir: Répertoire des templates

    Returns:
        Chemin du fichier Typst créé
    """
    # Lire le contenu converti
    with open(content_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Créer le document Typst complet
    # Utiliser des chemins relatifs pour les templates (copiés dans le même répertoire)
    typst_document = f'''// Fichier généré automatiquement - {datetime.now().isoformat()}
// Volume {volume.number} — {volume.title}

#import "templates/callouts.typ": *
#import "templates/cover.typ": cover-page
#import "templates/toc.typ": custom-toc

// ═══════════════════════════════════════════════════════════════════════════════
// MÉTADONNÉES
// ═══════════════════════════════════════════════════════════════════════════════

#set document(
  title: [Volume {volume.number} — {volume.title}],
  author: "André-Guy Bruneau",
  keywords: ("entreprise agentique", "architecture", "transformation numérique"),
)

// ═══════════════════════════════════════════════════════════════════════════════
// PAGE DE COUVERTURE
// ═══════════════════════════════════════════════════════════════════════════════

#cover-page(
  volume-number: "{volume.number}",
  title: "{volume.title}",
  subtitle: "{volume.subtitle}",
  author: "André-Guy Bruneau",
  year: "2026",
  accent-color: rgb("{volume.color}"),
)

// ═══════════════════════════════════════════════════════════════════════════════
// CONFIGURATION DE PAGE
// ═══════════════════════════════════════════════════════════════════════════════

#set page(
  paper: "a4",
  margin: (top: 2.5cm, bottom: 2.5cm, left: 2cm, right: 2cm),
  header: context {{
    if counter(page).get().first() > 2 [
      #set text(size: 9pt, fill: rgb("#666666"))
      #grid(
        columns: (1fr, 1fr),
        align: (left, right),
        [Volume {volume.number} — {volume.title}],
        [],
      )
      #v(-4pt)
      #line(length: 100%, stroke: 0.5pt + rgb("#CCCCCC"))
    ]
  }},
  footer: context {{
    if counter(page).get().first() > 2 [
      #align(center)[
        #set text(size: 10pt, fill: rgb("#333333"))
        — #counter(page).display() —
      ]
    ]
  }},
  numbering: "1",
)

// ═══════════════════════════════════════════════════════════════════════════════
// TYPOGRAPHIE
// ═══════════════════════════════════════════════════════════════════════════════

#set text(
  font: ("Libertinus Serif", "Linux Libertine", "Times New Roman"),
  size: 11pt,
  lang: "fr",
  region: "CA",
  hyphenate: true,
)

#set par(
  justify: true,
  leading: 0.65em,
  first-line-indent: 0pt,
)

// Titres
#show heading.where(level: 1): it => {{
  pagebreak(weak: true)
  v(1cm)
  text(size: 24pt, weight: "bold", fill: rgb("{volume.color}"), it.body)
  v(0.5cm)
  line(length: 30%, stroke: 2pt + rgb("{volume.color}").lighten(50%))
  v(1cm)
}}

#show heading.where(level: 2): it => {{
  v(1cm)
  text(size: 18pt, weight: "bold", fill: rgb("#333333"), it.body)
  v(0.5cm)
}}

#show heading.where(level: 3): it => {{
  v(0.8cm)
  text(size: 14pt, weight: "bold", fill: rgb("#444444"), it.body)
  v(0.3cm)
}}

#show heading.where(level: 4): it => {{
  v(0.5cm)
  text(size: 12pt, weight: "bold", fill: rgb("#555555"), it.body)
  v(0.2cm)
}}

// Listes
#set list(
  marker: ([•], [◦], [▪], [▫]),
  indent: 20pt,
  body-indent: 8pt,
)

#set enum(
  indent: 20pt,
  body-indent: 8pt,
)

// Code inline
#show raw.where(block: false): box.with(
  fill: rgb("#F5F5F5"),
  inset: (x: 3pt, y: 0pt),
  outset: (y: 3pt),
  radius: 2pt,
)

// Blocs de code
#show raw.where(block: true): it => {{
  set text(font: ("Fira Code", "Consolas", "Monaco"), size: 9pt)
  block(
    width: 100%,
    fill: rgb("#F8F8F8"),
    inset: 12pt,
    radius: 4pt,
    stroke: (left: 3pt + rgb("#CCCCCC")),
    it,
  )
}}

// Tableaux
#set table(
  stroke: (x, y) => {{
    if y == 0 {{ (bottom: 2pt + rgb("#333333")) }}
    else {{ (bottom: 0.5pt + rgb("#E0E0E0")) }}
  }},
  fill: (x, y) => {{
    if y == 0 {{ rgb("#F5F5F5") }}
    else if calc.rem(y, 2) == 0 {{ rgb("#FAFAFA") }}
  }},
  inset: 8pt,
)

// Liens
#show link: it => {{
  text(fill: rgb("#1976D2"), it)
}}

// Règle horizontale (générée par Pandoc pour ---)
#let horizontalrule = line(length: 100%, stroke: 0.5pt + rgb("#CCCCCC"))

// ═══════════════════════════════════════════════════════════════════════════════
// TABLE DES MATIÈRES
// ═══════════════════════════════════════════════════════════════════════════════

#custom-toc(
  title: "Table des Matières",
  title-size: 24pt,
  accent-color: rgb("{volume.color}"),
  depth: 3,
)

// ═══════════════════════════════════════════════════════════════════════════════
// CONTENU
// ═══════════════════════════════════════════════════════════════════════════════

{content}
'''

    # Écrire le fichier
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(typst_document)

    return output_file


def run_typst(input_file: Path, output_file: Path, verbose: bool = False) -> bool:
    """
    Exécute Typst pour compiler le PDF.

    Args:
        input_file: Fichier Typst source
        output_file: Fichier PDF de sortie
        verbose: Mode verbose

    Returns:
        True si succès, False sinon
    """
    cmd = [
        'typst',
        'compile',
        str(input_file),
        str(output_file),
    ]

    if verbose:
        print_info(f"Exécution : {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        if result.returncode != 0:
            print_error(f"Erreur Typst : {result.stderr}")
            return False

        if verbose and result.stderr:
            print_warning(f"Warnings Typst : {result.stderr}")

        return True

    except FileNotFoundError:
        print_error("Typst non trouvé. Veuillez l'installer.")
        return False
    except Exception as e:
        print_error(f"Erreur lors de l'exécution de Typst : {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# GÉNÉRATION D'UN VOLUME
# ═══════════════════════════════════════════════════════════════════════════════

def generate_volume(volume_id: str, verbose: bool = False) -> Optional[Path]:
    """
    Génère le PDF d'un volume complet.

    Args:
        volume_id: Identifiant du volume (I, II, III, IV, V)
        verbose: Mode verbose

    Returns:
        Chemin du PDF généré ou None si erreur
    """
    print_info(f"Génération du Volume {volume_id}...")

    # Charger la configuration
    config = load_volumes_config()
    volume = parse_volume_config(volume_id, config)

    # Chemins
    monograph_root = get_monograph_root()
    templates_dir = get_templates_dir()
    filters_dir = get_filters_dir()
    output_dir = ensure_directory(get_output_dir() / "volumes")

    # Créer un répertoire temporaire
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # 1. Collecter les fichiers Markdown
        md_files = collect_markdown_files(volume, monograph_root)
        if not md_files:
            print_error(f"Aucun fichier trouvé pour le Volume {volume_id}")
            return None

        if verbose:
            print_info(f"  {len(md_files)} fichiers Markdown trouvés")

        # 2. Concaténer les fichiers
        combined_md = temp_path / "combined.md"
        concatenate_markdown_files(md_files, combined_md)

        if verbose:
            print_info(f"  Fichiers concaténés : {combined_md}")

        # 3. Convertir via Pandoc
        converted_typ = temp_path / "content.typ"
        filters = [
            filters_dir / "callouts.lua",
            filters_dir / "figures.lua",
            filters_dir / "cross-refs.lua",
        ]
        # Filtrer les filtres qui existent
        filters = [f for f in filters if f.exists()]

        if not run_pandoc(combined_md, converted_typ, filters, verbose):
            return None

        if verbose:
            print_info(f"  Conversion Pandoc terminée")

        # 4. Copier les templates dans le répertoire temporaire
        temp_templates = temp_path / "templates"
        shutil.copytree(templates_dir, temp_templates)

        # 5. Créer le document Typst complet
        final_typ = temp_path / "volume.typ"
        create_volume_typst(volume, converted_typ, final_typ, temp_templates)

        if verbose:
            print_info(f"  Document Typst créé")

        # 6. Compiler avec Typst
        output_filename = generate_output_filename(volume)
        output_pdf = output_dir / output_filename

        if not run_typst(final_typ, output_pdf, verbose):
            return None

    print_success(f"Volume {volume_id} généré : {output_pdf}")
    return output_pdf


# ═══════════════════════════════════════════════════════════════════════════════
# GÉNÉRATION CONSOLIDÉE
# ═══════════════════════════════════════════════════════════════════════════════

def generate_consolidated(verbose: bool = False) -> Optional[Path]:
    """
    Génère la monographie complète consolidée.

    Args:
        verbose: Mode verbose

    Returns:
        Chemin du PDF généré ou None si erreur
    """
    print_info("Génération de la monographie consolidée...")

    # Pour l'instant, générer tous les volumes puis les assembler
    # TODO: Implémenter une vraie consolidation avec le template consolidated.typ

    output_dir = ensure_directory(get_output_dir() / "consolidated")
    output_filename = generate_consolidated_filename()
    output_pdf = output_dir / output_filename

    # Générer chaque volume
    volume_pdfs = []
    for volume_id in ['I', 'II', 'III', 'IV', 'V']:
        pdf = generate_volume(volume_id, verbose)
        if pdf:
            volume_pdfs.append(pdf)
        else:
            print_error(f"Échec de la génération du Volume {volume_id}")
            return None

    # TODO: Fusionner les PDFs en un seul
    print_warning("La fusion des PDFs n'est pas encore implémentée")
    print_info(f"Les volumes individuels sont disponibles dans : {get_output_dir() / 'volumes'}")

    return output_pdf


# ═══════════════════════════════════════════════════════════════════════════════
# GÉNÉRATION PARALLÈLE
# ═══════════════════════════════════════════════════════════════════════════════

def generate_volumes_parallel(volume_ids: List[str], verbose: bool = False) -> List[Path]:
    """
    Génère plusieurs volumes en parallèle.

    Args:
        volume_ids: Liste des identifiants de volumes
        verbose: Mode verbose

    Returns:
        Liste des PDFs générés
    """
    results = []

    with ThreadPoolExecutor(max_workers=min(len(volume_ids), 4)) as executor:
        futures = {
            executor.submit(generate_volume, vid, verbose): vid
            for vid in volume_ids
        }

        for future in as_completed(futures):
            volume_id = futures[future]
            try:
                pdf = future.result()
                if pdf:
                    results.append(pdf)
            except Exception as e:
                print_error(f"Erreur pour Volume {volume_id}: {e}")

    return results


# ═══════════════════════════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description="Génération PDF — L'Entreprise Agentique",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python generate.py --volume I              # Générer le Volume I
  python generate.py --volume all            # Générer tous les volumes
  python generate.py --volume all --parallel # Génération parallèle
  python generate.py --consolidated          # Monographie complète
        """
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
        help='Génération parallèle (avec --volume all)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Mode verbose'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Valider sans générer'
    )

    args = parser.parse_args()

    # Vérifier qu'au moins une option est spécifiée
    if not args.volume and not args.consolidated:
        parser.print_help()
        sys.exit(1)

    # En-tête
    print_header("Génération PDF — L'Entreprise Agentique")
    print()

    # Vérifier les dépendances
    print_info("Vérification des dépendances...")
    deps = check_dependencies()
    if not all(deps.values()):
        for name, available in deps.items():
            if not available:
                print_error(f"  {name} non trouvé")
        sys.exit(1)
    print_success("Toutes les dépendances sont disponibles")
    print()

    # Mode validation
    if args.validate:
        from validate import main as validate_main
        sys.argv = ['validate.py', '--volume', args.volume or 'all']
        if args.verbose:
            sys.argv.append('--verbose')
        validate_main()
        return

    # Génération
    start_time = datetime.now()

    if args.consolidated:
        result = generate_consolidated(args.verbose)
        if result:
            print_success(f"Monographie générée avec succès")
        else:
            print_error("Échec de la génération")
            sys.exit(1)

    elif args.volume:
        if args.volume == 'all':
            volumes = ['I', 'II', 'III', 'IV', 'V']
            if args.parallel:
                results = generate_volumes_parallel(volumes, args.verbose)
                print()
                print_success(f"{len(results)}/{len(volumes)} volumes générés")
            else:
                for vid in volumes:
                    generate_volume(vid, args.verbose)
        else:
            result = generate_volume(args.volume, args.verbose)
            if not result:
                sys.exit(1)

    # Temps total
    elapsed = datetime.now() - start_time
    print()
    print_info(f"Temps total : {elapsed.total_seconds():.1f} secondes")


if __name__ == '__main__':
    main()
