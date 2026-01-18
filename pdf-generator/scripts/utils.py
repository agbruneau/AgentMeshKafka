#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
utils.py — Utilitaires partagés pour la génération PDF

Ce module fournit des fonctions utilitaires pour :
- Chargement des configurations YAML
- Gestion des chemins
- Logging
- Manipulation de fichiers
"""

import os
import sys
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION DES CHEMINS
# ═══════════════════════════════════════════════════════════════════════════════

def get_project_root() -> Path:
    """Retourne le chemin racine du projet pdf-generator."""
    return Path(__file__).parent.parent


def get_monograph_root() -> Path:
    """Retourne le chemin racine de la monographie."""
    return get_project_root().parent


def get_config_dir() -> Path:
    """Retourne le chemin du répertoire de configuration."""
    return get_project_root() / "config"


def get_templates_dir() -> Path:
    """Retourne le chemin du répertoire des templates."""
    return get_project_root() / "templates"


def get_filters_dir() -> Path:
    """Retourne le chemin du répertoire des filtres Lua."""
    return get_project_root() / "filters"


def get_output_dir() -> Path:
    """Retourne le chemin du répertoire de sortie."""
    return get_project_root() / "output"


# ═══════════════════════════════════════════════════════════════════════════════
# CHARGEMENT DES CONFIGURATIONS
# ═══════════════════════════════════════════════════════════════════════════════

def load_yaml(file_path: Path) -> Dict[str, Any]:
    """Charge un fichier YAML et retourne son contenu."""
    if not file_path.exists():
        raise FileNotFoundError(f"Fichier de configuration non trouvé : {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_volumes_config() -> Dict[str, Any]:
    """Charge la configuration des volumes."""
    return load_yaml(get_config_dir() / "volumes.yaml")


def load_callouts_config() -> Dict[str, Any]:
    """Charge la configuration des callouts."""
    return load_yaml(get_config_dir() / "callouts.yaml")


def load_styles_config() -> Dict[str, Any]:
    """Charge la configuration des styles."""
    return load_yaml(get_config_dir() / "styles.yaml")


# ═══════════════════════════════════════════════════════════════════════════════
# STRUCTURES DE DONNÉES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Chapter:
    """Représente un chapitre de la monographie."""
    file: str
    number: str
    title: str
    path: Optional[Path] = None

    def __post_init__(self):
        if self.path is None and self.file:
            self.path = Path(self.file)


@dataclass
class Part:
    """Représente une partie d'un volume."""
    name: str
    chapters: List[Chapter]


@dataclass
class Volume:
    """Représente un volume de la monographie."""
    number: str
    title: str
    subtitle: str
    color: str
    directory: str
    chapter_count: int
    parts: List[Part]


def parse_volume_config(volume_id: str, config: Dict) -> Volume:
    """Parse la configuration d'un volume."""
    vol_config = config['volumes'].get(volume_id)
    if not vol_config:
        raise ValueError(f"Volume {volume_id} non trouvé dans la configuration")

    parts = []
    for part_config in vol_config.get('parts', []):
        chapters = [
            Chapter(
                file=ch['file'],
                number=ch.get('number', ''),
                title=ch.get('title', '')
            )
            for ch in part_config.get('chapters', [])
        ]
        parts.append(Part(name=part_config['name'], chapters=chapters))

    return Volume(
        number=volume_id,
        title=vol_config['title'],
        subtitle=vol_config['subtitle'],
        color=vol_config['color'],
        directory=vol_config['directory'],
        chapter_count=vol_config['chapter_count'],
        parts=parts
    )


# ═══════════════════════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════════════════════════

def setup_logging(verbose: bool = False, log_file: Optional[Path] = None) -> logging.Logger:
    """Configure le système de logging."""
    logger = logging.getLogger('pdf-generator')
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optionnel)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# ═══════════════════════════════════════════════════════════════════════════════
# MANIPULATION DE FICHIERS
# ═══════════════════════════════════════════════════════════════════════════════

def collect_markdown_files(volume: Volume, base_dir: Path) -> List[Path]:
    """Collecte tous les fichiers Markdown d'un volume dans l'ordre."""
    files = []
    volume_dir = base_dir / volume.directory

    for part in volume.parts:
        for chapter in part.chapters:
            file_path = volume_dir / chapter.file
            if file_path.exists():
                files.append(file_path)
            else:
                logging.warning(f"Fichier non trouvé : {file_path}")

    return files


def concatenate_markdown_files(files: List[Path], output_path: Path) -> Path:
    """Concatène plusieurs fichiers Markdown en un seul."""
    with open(output_path, 'w', encoding='utf-8') as out:
        for i, file_path in enumerate(files):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                out.write(content)

                # Ajouter un séparateur entre les fichiers
                if i < len(files) - 1:
                    out.write("\n\n---\n\n")

    return output_path


def ensure_directory(path: Path) -> Path:
    """Crée un répertoire s'il n'existe pas."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def clean_temp_files(temp_dir: Path) -> None:
    """Nettoie les fichiers temporaires."""
    import shutil
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


# ═══════════════════════════════════════════════════════════════════════════════
# VÉRIFICATION DES DÉPENDANCES
# ═══════════════════════════════════════════════════════════════════════════════

def check_pandoc() -> bool:
    """Vérifie si Pandoc est installé."""
    import subprocess
    try:
        result = subprocess.run(
            ['pandoc', '--version'],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def check_typst() -> bool:
    """Vérifie si Typst est installé."""
    import subprocess
    try:
        result = subprocess.run(
            ['typst', '--version'],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def get_pandoc_version() -> Optional[str]:
    """Retourne la version de Pandoc."""
    import subprocess
    try:
        result = subprocess.run(
            ['pandoc', '--version'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            # Première ligne contient la version
            return result.stdout.split('\n')[0]
    except FileNotFoundError:
        pass
    return None


def get_typst_version() -> Optional[str]:
    """Retourne la version de Typst."""
    import subprocess
    try:
        result = subprocess.run(
            ['typst', '--version'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except FileNotFoundError:
        pass
    return None


def check_dependencies() -> Dict[str, bool]:
    """Vérifie toutes les dépendances requises."""
    return {
        'pandoc': check_pandoc(),
        'typst': check_typst(),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# COULEURS ET FORMATAGE
# ═══════════════════════════════════════════════════════════════════════════════

# Configurer stdout pour UTF-8 sur Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class Colors:
    """Codes ANSI pour les couleurs dans le terminal."""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'


def colorize(text: str, color: str) -> str:
    """Applique une couleur à un texte (si le terminal le supporte)."""
    if sys.stdout.isatty():
        return f"{color}{text}{Colors.RESET}"
    return text


def print_header(text: str) -> None:
    """Affiche un en-tete formate."""
    line = "=" * 70
    print(colorize(line, Colors.CYAN))
    print(colorize(f"  {text}", Colors.BOLD + Colors.CYAN))
    print(colorize(line, Colors.CYAN))


def print_success(text: str) -> None:
    """Affiche un message de succes."""
    print(colorize(f"[OK] {text}", Colors.GREEN))


def print_error(text: str) -> None:
    """Affiche un message d'erreur."""
    print(colorize(f"[ERREUR] {text}", Colors.RED))


def print_warning(text: str) -> None:
    """Affiche un avertissement."""
    print(colorize(f"[ATTENTION] {text}", Colors.YELLOW))


def print_info(text: str) -> None:
    """Affiche une information."""
    print(colorize(f"[INFO] {text}", Colors.BLUE))


# ═══════════════════════════════════════════════════════════════════════════════
# GÉNÉRATION DES NOMS DE FICHIERS
# ═══════════════════════════════════════════════════════════════════════════════

def generate_output_filename(volume: Volume, extension: str = "pdf") -> str:
    """Génère le nom du fichier de sortie pour un volume."""
    # Nettoyer le titre pour le nom de fichier
    title_clean = volume.title.replace(" — ", "_").replace(" ", "_")
    title_clean = "".join(c for c in title_clean if c.isalnum() or c == "_")
    return f"Volume_{volume.number}_{title_clean}.{extension}"


def generate_consolidated_filename(extension: str = "pdf") -> str:
    """Génère le nom du fichier de sortie pour la monographie consolidée."""
    return f"LEntreprise_Agentique_Monographie_Complete.{extension}"


# ═══════════════════════════════════════════════════════════════════════════════
# TIMESTAMPS
# ═══════════════════════════════════════════════════════════════════════════════

def get_timestamp() -> str:
    """Retourne un timestamp formaté."""
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def get_date_string() -> str:
    """Retourne la date formatée pour l'affichage."""
    return datetime.now().strftime("%d %B %Y")
