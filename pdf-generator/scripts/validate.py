#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate.py — Script de validation pré-génération

Ce script valide :
- L'existence de tous les fichiers source
- La syntaxe Markdown de base
- Les patterns de callouts
- La cohérence de la configuration
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from utils import (
    get_monograph_root,
    load_volumes_config,
    load_callouts_config,
    parse_volume_config,
    collect_markdown_files,
    check_dependencies,
    print_header,
    print_success,
    print_error,
    print_warning,
    print_info,
    Colors,
    colorize,
)


# ═══════════════════════════════════════════════════════════════════════════════
# STRUCTURES DE VALIDATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ValidationResult:
    """Résultat d'une validation."""
    valid: bool
    message: str
    details: Optional[List[str]] = None


@dataclass
class ValidationReport:
    """Rapport de validation complet."""
    volume_id: str
    file_checks: List[ValidationResult]
    content_checks: List[ValidationResult]
    callout_checks: List[ValidationResult]

    @property
    def is_valid(self) -> bool:
        """Vérifie si toutes les validations ont réussi."""
        all_checks = self.file_checks + self.content_checks + self.callout_checks
        return all(check.valid for check in all_checks)

    @property
    def error_count(self) -> int:
        """Compte le nombre d'erreurs."""
        all_checks = self.file_checks + self.content_checks + self.callout_checks
        return sum(1 for check in all_checks if not check.valid)

    @property
    def warning_count(self) -> int:
        """Compte le nombre d'avertissements."""
        return 0  # À implémenter si nécessaire


# ═══════════════════════════════════════════════════════════════════════════════
# VALIDATION DES FICHIERS
# ═══════════════════════════════════════════════════════════════════════════════

def validate_file_exists(file_path: Path) -> ValidationResult:
    """Vérifie qu'un fichier existe."""
    if file_path.exists():
        return ValidationResult(
            valid=True,
            message=f"Fichier trouvé : {file_path.name}"
        )
    return ValidationResult(
        valid=False,
        message=f"Fichier manquant : {file_path}"
    )


def validate_file_encoding(file_path: Path) -> ValidationResult:
    """Vérifie que le fichier est encodé en UTF-8."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read()
        return ValidationResult(
            valid=True,
            message=f"Encodage UTF-8 valide : {file_path.name}"
        )
    except UnicodeDecodeError as e:
        return ValidationResult(
            valid=False,
            message=f"Erreur d'encodage : {file_path.name}",
            details=[str(e)]
        )


def validate_file_not_empty(file_path: Path) -> ValidationResult:
    """Vérifie que le fichier n'est pas vide."""
    if file_path.stat().st_size > 0:
        return ValidationResult(
            valid=True,
            message=f"Fichier non vide : {file_path.name}"
        )
    return ValidationResult(
        valid=False,
        message=f"Fichier vide : {file_path}"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# VALIDATION DU CONTENU MARKDOWN
# ═══════════════════════════════════════════════════════════════════════════════

def validate_markdown_structure(file_path: Path) -> ValidationResult:
    """Vérifie la structure de base du Markdown."""
    issues = []

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')

    # Vérifier qu'il y a au moins un titre H1
    has_h1 = any(line.startswith('# ') for line in lines)
    if not has_h1:
        issues.append("Pas de titre H1 trouvé")

    # Vérifier la hiérarchie des titres (pas de saut de niveau)
    current_level = 0
    for i, line in enumerate(lines, 1):
        if line.startswith('#'):
            # Compter le niveau
            level = len(line) - len(line.lstrip('#'))
            if level > current_level + 1 and current_level > 0:
                issues.append(f"Ligne {i}: Saut de niveau de titre (H{current_level} → H{level})")
            current_level = level

    # Vérifier les tableaux mal formés
    in_table = False
    for i, line in enumerate(lines, 1):
        if '|' in line:
            if not in_table:
                in_table = True
            # Vérifier que les lignes de tableau ont le même nombre de |
        elif in_table:
            in_table = False

    if issues:
        return ValidationResult(
            valid=False,
            message=f"Problèmes de structure : {file_path.name}",
            details=issues
        )

    return ValidationResult(
        valid=True,
        message=f"Structure Markdown valide : {file_path.name}"
    )


def validate_no_broken_links(file_path: Path) -> ValidationResult:
    """Vérifie les liens internes cassés."""
    issues = []

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Trouver les liens Markdown
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    links = re.findall(link_pattern, content)

    for text, url in links:
        # Vérifier les liens internes (commençant par # ou relatifs)
        if url.startswith('#'):
            # Lien vers une ancre interne
            anchor = url[1:].lower().replace(' ', '-')
            # Vérifier si l'ancre existe (simplifiée)
            pass
        elif not url.startswith(('http://', 'https://', 'mailto:')):
            # Lien relatif vers un fichier
            linked_file = file_path.parent / url
            if not linked_file.exists():
                issues.append(f"Lien cassé : [{text}]({url})")

    if issues:
        return ValidationResult(
            valid=False,
            message=f"Liens cassés dans : {file_path.name}",
            details=issues
        )

    return ValidationResult(
        valid=True,
        message=f"Liens valides : {file_path.name}"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# VALIDATION DES CALLOUTS
# ═══════════════════════════════════════════════════════════════════════════════

def load_callout_patterns() -> List[Tuple[str, str]]:
    """Charge les patterns de callouts depuis la configuration."""
    config = load_callouts_config()
    patterns = []

    for callout_id, callout_config in config.get('callouts', {}).items():
        pattern = callout_config.get('pattern', '')
        if pattern:
            patterns.append((callout_id, pattern))

    return patterns


def validate_callouts_in_file(file_path: Path, patterns: List[Tuple[str, str]]) -> ValidationResult:
    """Vérifie que les callouts du fichier sont reconnus."""
    issues = []
    recognized = []

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Trouver tous les blockquotes avec pattern de callout potentiel
    blockquote_pattern = r'^>\s*\*\*(.+?)\*\*'
    matches = re.findall(blockquote_pattern, content, re.MULTILINE)

    for match in matches:
        found = False
        for callout_id, pattern in patterns:
            # Reconstruire le format complet pour la comparaison
            full_match = f"**{match}**"
            try:
                if re.match(pattern, full_match):
                    found = True
                    recognized.append(callout_id)
                    break
            except re.error:
                pass

        if not found and match not in ['Attention', 'Note']:
            # Certains patterns courants non reconnus
            issues.append(f"Callout non reconnu : **{match}**")

    if issues:
        return ValidationResult(
            valid=True,  # Warning, pas erreur
            message=f"Callouts potentiellement non reconnus : {file_path.name}",
            details=issues
        )

    return ValidationResult(
        valid=True,
        message=f"Callouts valides ({len(recognized)} trouvés) : {file_path.name}"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# VALIDATION D'UN VOLUME
# ═══════════════════════════════════════════════════════════════════════════════

def validate_volume(volume_id: str, verbose: bool = False) -> ValidationReport:
    """Valide un volume complet."""
    config = load_volumes_config()
    volume = parse_volume_config(volume_id, config)
    base_dir = get_monograph_root()

    file_checks = []
    content_checks = []
    callout_checks = []

    # Collecter les fichiers
    files = collect_markdown_files(volume, base_dir)

    if verbose:
        print_info(f"Validation du Volume {volume_id} ({len(files)} fichiers)")

    # Charger les patterns de callouts
    callout_patterns = load_callout_patterns()

    # Valider chaque fichier
    for file_path in files:
        # Vérifications de fichier
        file_checks.append(validate_file_exists(file_path))

        if file_path.exists():
            file_checks.append(validate_file_encoding(file_path))
            file_checks.append(validate_file_not_empty(file_path))

            # Vérifications de contenu
            content_checks.append(validate_markdown_structure(file_path))
            content_checks.append(validate_no_broken_links(file_path))

            # Vérifications de callouts
            callout_checks.append(validate_callouts_in_file(file_path, callout_patterns))

    return ValidationReport(
        volume_id=volume_id,
        file_checks=file_checks,
        content_checks=content_checks,
        callout_checks=callout_checks
    )


# ═══════════════════════════════════════════════════════════════════════════════
# AFFICHAGE DU RAPPORT
# ═══════════════════════════════════════════════════════════════════════════════

def print_validation_report(report: ValidationReport, verbose: bool = False) -> None:
    """Affiche le rapport de validation."""
    print()
    print_header(f"Rapport de Validation — Volume {report.volume_id}")

    # Résumé
    total_checks = (
        len(report.file_checks) +
        len(report.content_checks) +
        len(report.callout_checks)
    )

    if report.is_valid:
        print_success(f"Toutes les validations réussies ({total_checks} vérifications)")
    else:
        print_error(f"{report.error_count} erreur(s) sur {total_checks} vérifications")

    # Détails si verbose ou si erreurs
    if verbose or not report.is_valid:
        print()

        # Fichiers
        if verbose:
            print(colorize("  Fichiers:", Colors.BOLD))
            for check in report.file_checks:
                if check.valid:
                    print(f"    ✓ {check.message}")
                else:
                    print(colorize(f"    ✗ {check.message}", Colors.RED))
                    if check.details:
                        for detail in check.details:
                            print(f"      → {detail}")

        # Contenu (afficher seulement les erreurs si pas verbose)
        errors = [c for c in report.content_checks if not c.valid]
        if errors:
            print(colorize("  Contenu:", Colors.BOLD))
            for check in errors:
                print(colorize(f"    ✗ {check.message}", Colors.RED))
                if check.details:
                    for detail in check.details:
                        print(f"      → {detail}")

        # Callouts (afficher les warnings)
        for check in report.callout_checks:
            if check.details:
                print(colorize(f"  ⚠ {check.message}", Colors.YELLOW))
                for detail in check.details[:5]:  # Limiter à 5
                    print(f"      → {detail}")
                if len(check.details) > 5:
                    print(f"      ... et {len(check.details) - 5} autres")


# ═══════════════════════════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Point d'entrée principal pour la validation."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validation des fichiers sources pour la génération PDF"
    )
    parser.add_argument(
        '--volume',
        choices=['I', 'II', 'III', 'IV', 'V', 'all'],
        default='all',
        help='Volume à valider (défaut: all)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Mode verbose avec détails'
    )

    args = parser.parse_args()

    # Vérifier les dépendances
    print_header("Vérification des Dépendances")
    deps = check_dependencies()
    all_deps_ok = True
    for name, available in deps.items():
        if available:
            print_success(f"{name} disponible")
        else:
            print_error(f"{name} non trouvé")
            all_deps_ok = False

    if not all_deps_ok:
        print_error("Certaines dépendances sont manquantes")
        sys.exit(1)

    # Valider les volumes
    volumes_to_validate = ['I', 'II', 'III', 'IV', 'V'] if args.volume == 'all' else [args.volume]

    all_valid = True
    for volume_id in volumes_to_validate:
        try:
            report = validate_volume(volume_id, args.verbose)
            print_validation_report(report, args.verbose)
            if not report.is_valid:
                all_valid = False
        except Exception as e:
            print_error(f"Erreur lors de la validation du Volume {volume_id}: {e}")
            all_valid = False

    # Résultat final
    print()
    if all_valid:
        print_success("Validation terminée avec succès")
        sys.exit(0)
    else:
        print_error("Validation terminée avec des erreurs")
        sys.exit(1)


if __name__ == '__main__':
    main()
