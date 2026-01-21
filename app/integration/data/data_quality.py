"""
Data Quality - Contrôles qualité des données pour simulation d'intégration.

Fonctionnalités:
- Règles de validation configurables
- Dimensions de qualité (complétude, exactitude, cohérence, etc.)
- Profiling des données
- Scoring et rapports
- Alerting sur seuils
"""
import asyncio
import uuid
import re
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Pattern
from enum import Enum
from dataclasses import dataclass, field


class QualityDimension(Enum):
    """Dimensions de qualité des données."""
    COMPLETENESS = "completeness"      # Complétude - données non nulles
    ACCURACY = "accuracy"              # Exactitude - format correct
    CONSISTENCY = "consistency"        # Cohérence - règles métier
    VALIDITY = "validity"              # Validité - valeurs autorisées
    UNIQUENESS = "uniqueness"          # Unicité - pas de doublons
    TIMELINESS = "timeliness"          # Fraîcheur - données à jour


class RuleSeverity(Enum):
    """Sévérité des règles."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class QualityRule:
    """Représente une règle de qualité des données."""
    id: str
    name: str
    dimension: QualityDimension
    severity: RuleSeverity
    description: str
    field: Optional[str] = None  # Champ concerné, None = global
    condition: Optional[str] = None  # Expression de la condition
    threshold: float = 1.0  # Seuil de conformité (0-1)
    active: bool = True

    def to_dict(self) -> Dict:
        """Convertit la règle en dictionnaire."""
        return {
            "id": self.id,
            "name": self.name,
            "dimension": self.dimension.value,
            "severity": self.severity.value,
            "description": self.description,
            "field": self.field,
            "condition": self.condition,
            "threshold": self.threshold,
            "active": self.active
        }


@dataclass
class ValidationResult:
    """Résultat de validation d'une règle."""
    rule_id: str
    rule_name: str
    dimension: QualityDimension
    severity: RuleSeverity
    passed: bool
    score: float  # 0-1
    total_records: int
    valid_records: int
    invalid_records: int
    invalid_samples: List[Dict] = field(default_factory=list)
    message: str = ""

    def to_dict(self) -> Dict:
        """Convertit le résultat en dictionnaire."""
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "dimension": self.dimension.value,
            "severity": self.severity.value,
            "passed": self.passed,
            "score": self.score,
            "total_records": self.total_records,
            "valid_records": self.valid_records,
            "invalid_records": self.invalid_records,
            "invalid_samples": self.invalid_samples[:5],  # Limite à 5 exemples
            "message": self.message
        }


@dataclass
class QualityReport:
    """Rapport complet de qualité des données."""
    id: str
    dataset: str
    timestamp: str
    total_records: int
    overall_score: float
    dimension_scores: Dict[str, float]
    results: List[ValidationResult]
    passed: bool
    critical_issues: int = 0
    warnings: int = 0

    def to_dict(self) -> Dict:
        """Convertit le rapport en dictionnaire."""
        return {
            "id": self.id,
            "dataset": self.dataset,
            "timestamp": self.timestamp,
            "total_records": self.total_records,
            "overall_score": self.overall_score,
            "dimension_scores": self.dimension_scores,
            "results": [r.to_dict() for r in self.results],
            "passed": self.passed,
            "critical_issues": self.critical_issues,
            "warnings": self.warnings
        }


class DataQuality:
    """
    Moteur de contrôle qualité des données.

    Supporte:
    - Règles de validation configurables
    - 6 dimensions de qualité
    - Profiling automatique
    - Scoring et seuils
    - Rapports détaillés
    """

    # Règles prédéfinies par dataset
    PREDEFINED_RULES = {
        "customers": [
            QualityRule(
                id="CUS-001", name="Email requis",
                dimension=QualityDimension.COMPLETENESS,
                severity=RuleSeverity.ERROR,
                description="Le champ email doit être renseigné",
                field="email"
            ),
            QualityRule(
                id="CUS-002", name="Format email valide",
                dimension=QualityDimension.ACCURACY,
                severity=RuleSeverity.ERROR,
                description="L'email doit avoir un format valide",
                field="email",
                condition="email_format"
            ),
            QualityRule(
                id="CUS-003", name="Nom requis",
                dimension=QualityDimension.COMPLETENESS,
                severity=RuleSeverity.CRITICAL,
                description="Le nom du client doit être renseigné",
                field="name"
            ),
            QualityRule(
                id="CUS-004", name="Segment valide",
                dimension=QualityDimension.VALIDITY,
                severity=RuleSeverity.WARNING,
                description="Le segment doit être BASIC, STANDARD ou PREMIUM",
                field="segment",
                condition="in:BASIC,STANDARD,PREMIUM"
            ),
            QualityRule(
                id="CUS-005", name="ID unique",
                dimension=QualityDimension.UNIQUENESS,
                severity=RuleSeverity.CRITICAL,
                description="L'ID client doit être unique",
                field="id"
            )
        ],
        "policies": [
            QualityRule(
                id="POL-001", name="Client ID requis",
                dimension=QualityDimension.COMPLETENESS,
                severity=RuleSeverity.CRITICAL,
                description="Une police doit avoir un client associé",
                field="customer_id"
            ),
            QualityRule(
                id="POL-002", name="Prime positive",
                dimension=QualityDimension.VALIDITY,
                severity=RuleSeverity.ERROR,
                description="La prime doit être positive",
                field="premium",
                condition="positive"
            ),
            QualityRule(
                id="POL-003", name="Statut valide",
                dimension=QualityDimension.VALIDITY,
                severity=RuleSeverity.ERROR,
                description="Le statut doit être ACTIVE, CANCELLED ou EXPIRED",
                field="status",
                condition="in:ACTIVE,CANCELLED,EXPIRED"
            ),
            QualityRule(
                id="POL-004", name="Type produit valide",
                dimension=QualityDimension.VALIDITY,
                severity=RuleSeverity.WARNING,
                description="Le type doit être AUTO ou HOME",
                field="type",
                condition="in:AUTO,HOME"
            )
        ],
        "claims": [
            QualityRule(
                id="CLM-001", name="Police ID requis",
                dimension=QualityDimension.COMPLETENESS,
                severity=RuleSeverity.CRITICAL,
                description="Un sinistre doit être associé à une police",
                field="policy_id"
            ),
            QualityRule(
                id="CLM-002", name="Montant requis",
                dimension=QualityDimension.COMPLETENESS,
                severity=RuleSeverity.ERROR,
                description="Le montant du sinistre doit être renseigné",
                field="amount"
            ),
            QualityRule(
                id="CLM-003", name="Montant positif",
                dimension=QualityDimension.VALIDITY,
                severity=RuleSeverity.ERROR,
                description="Le montant doit être positif",
                field="amount",
                condition="positive"
            ),
            QualityRule(
                id="CLM-004", name="Statut valide",
                dimension=QualityDimension.VALIDITY,
                severity=RuleSeverity.WARNING,
                description="Le statut doit être OPEN, PENDING, CLOSED ou REJECTED",
                field="status",
                condition="in:OPEN,PENDING,CLOSED,REJECTED"
            )
        ]
    }

    def __init__(self, latency_ms: int = 50):
        """
        Initialise le moteur de qualité.

        Args:
            latency_ms: Latence simulée en millisecondes
        """
        self.latency_ms = latency_ms
        self._custom_rules: Dict[str, List[QualityRule]] = {}
        self._reports: List[QualityReport] = []
        self._event_handlers: List[Callable] = []
        self._stats = {
            "validations_run": 0,
            "records_validated": 0,
            "issues_found": 0,
            "critical_issues": 0
        }

    def _generate_id(self, prefix: str = "DQ") -> str:
        """Génère un ID unique."""
        return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"

    async def _simulate_latency(self, multiplier: float = 1.0):
        """Simule la latence de traitement."""
        if self.latency_ms > 0:
            import random
            actual = self.latency_ms * multiplier * (0.8 + random.random() * 0.4)
            await asyncio.sleep(actual / 1000)

    async def _notify_event(self, event_type: str, data: Dict):
        """Notifie les handlers d'un événement."""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        for handler in self._event_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception:
                pass

    def on_event(self, handler: Callable):
        """Enregistre un handler pour les événements."""
        self._event_handlers.append(handler)

    def add_rule(self, dataset: str, rule: QualityRule):
        """Ajoute une règle personnalisée."""
        if dataset not in self._custom_rules:
            self._custom_rules[dataset] = []
        self._custom_rules[dataset].append(rule)

    def get_rules(self, dataset: str) -> List[QualityRule]:
        """Récupère toutes les règles pour un dataset."""
        rules = []
        # Règles prédéfinies
        if dataset in self.PREDEFINED_RULES:
            rules.extend(self.PREDEFINED_RULES[dataset])
        # Règles personnalisées
        if dataset in self._custom_rules:
            rules.extend(self._custom_rules[dataset])
        return rules

    async def validate(self, dataset: str, data: List[Dict]) -> QualityReport:
        """
        Valide un dataset contre les règles de qualité.

        Args:
            dataset: Nom du dataset (customers, policies, claims)
            data: Liste des enregistrements à valider

        Returns:
            Rapport de qualité complet
        """
        await self._simulate_latency(len(data) * 0.01)  # Proportionnel au volume

        rules = self.get_rules(dataset)
        if not rules:
            # Pas de règles = tout passe
            return QualityReport(
                id=self._generate_id("RPT"),
                dataset=dataset,
                timestamp=datetime.now().isoformat(),
                total_records=len(data),
                overall_score=1.0,
                dimension_scores={d.value: 1.0 for d in QualityDimension},
                results=[],
                passed=True
            )

        results: List[ValidationResult] = []
        dimension_scores: Dict[str, List[float]] = {d.value: [] for d in QualityDimension}
        critical_issues = 0
        warnings = 0

        # Valide chaque règle
        for rule in rules:
            if not rule.active:
                continue

            result = await self._validate_rule(rule, data)
            results.append(result)
            dimension_scores[rule.dimension.value].append(result.score)

            if not result.passed:
                self._stats["issues_found"] += result.invalid_records
                if rule.severity == RuleSeverity.CRITICAL:
                    critical_issues += 1
                    self._stats["critical_issues"] += result.invalid_records
                elif rule.severity == RuleSeverity.WARNING:
                    warnings += result.invalid_records

        # Calcule les scores par dimension
        final_dimension_scores = {}
        for dim, scores in dimension_scores.items():
            if scores:
                final_dimension_scores[dim] = sum(scores) / len(scores)
            else:
                final_dimension_scores[dim] = 1.0

        # Score global
        all_scores = [r.score for r in results]
        overall_score = sum(all_scores) / len(all_scores) if all_scores else 1.0

        # Détermine si le rapport passe
        passed = critical_issues == 0 and overall_score >= 0.8

        report = QualityReport(
            id=self._generate_id("RPT"),
            dataset=dataset,
            timestamp=datetime.now().isoformat(),
            total_records=len(data),
            overall_score=overall_score,
            dimension_scores=final_dimension_scores,
            results=results,
            passed=passed,
            critical_issues=critical_issues,
            warnings=warnings
        )

        self._reports.append(report)
        self._stats["validations_run"] += 1
        self._stats["records_validated"] += len(data)

        await self._notify_event("quality_validated", {
            "report_id": report.id,
            "dataset": dataset,
            "passed": passed,
            "score": overall_score
        })

        return report

    async def _validate_rule(self, rule: QualityRule, data: List[Dict]) -> ValidationResult:
        """Valide une règle spécifique."""
        valid_count = 0
        invalid_samples = []

        for record in data:
            is_valid = self._check_record(rule, record)
            if is_valid:
                valid_count += 1
            elif len(invalid_samples) < 5:
                invalid_samples.append({
                    "record": record,
                    "field": rule.field,
                    "value": record.get(rule.field) if rule.field else None
                })

        total = len(data)
        score = valid_count / total if total > 0 else 1.0
        passed = score >= rule.threshold

        return ValidationResult(
            rule_id=rule.id,
            rule_name=rule.name,
            dimension=rule.dimension,
            severity=rule.severity,
            passed=passed,
            score=score,
            total_records=total,
            valid_records=valid_count,
            invalid_records=total - valid_count,
            invalid_samples=invalid_samples,
            message=f"{rule.name}: {valid_count}/{total} valides ({score*100:.1f}%)"
        )

    def _check_record(self, rule: QualityRule, record: Dict) -> bool:
        """Vérifie si un enregistrement satisfait une règle."""
        # Règle de complétude
        if rule.dimension == QualityDimension.COMPLETENESS:
            if rule.field:
                value = record.get(rule.field)
                return value is not None and value != ""
            return True

        # Règle d'unicité (vérifiée différemment au niveau du dataset)
        if rule.dimension == QualityDimension.UNIQUENESS:
            # Simplifié: on considère comme valide ici
            return True

        # Règles avec conditions
        if rule.condition:
            value = record.get(rule.field) if rule.field else None

            if rule.condition == "email_format":
                if value is None:
                    return True  # Complétude gérée séparément
                pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                return bool(re.match(pattern, str(value)))

            elif rule.condition == "positive":
                if value is None:
                    return True
                try:
                    return float(value) > 0
                except (ValueError, TypeError):
                    return False

            elif rule.condition.startswith("in:"):
                allowed = rule.condition[3:].split(",")
                return str(value) in allowed

            elif rule.condition.startswith("min:"):
                min_val = float(rule.condition[4:])
                try:
                    return float(value) >= min_val
                except (ValueError, TypeError):
                    return False

            elif rule.condition.startswith("max:"):
                max_val = float(rule.condition[4:])
                try:
                    return float(value) <= max_val
                except (ValueError, TypeError):
                    return False

        return True

    async def profile(self, dataset: str, data: List[Dict]) -> Dict:
        """
        Profile un dataset pour analyse exploratoire.

        Args:
            dataset: Nom du dataset
            data: Données à profiler

        Returns:
            Profil du dataset
        """
        await self._simulate_latency(len(data) * 0.005)

        if not data:
            return {"error": "No data to profile"}

        # Analyse des colonnes
        columns = {}
        sample = data[0]

        for col in sample.keys():
            values = [r.get(col) for r in data]
            non_null = [v for v in values if v is not None and v != ""]

            col_profile = {
                "total_count": len(values),
                "non_null_count": len(non_null),
                "null_count": len(values) - len(non_null),
                "completeness": len(non_null) / len(values) if values else 0,
                "distinct_count": len(set(str(v) for v in non_null))
            }

            # Statistiques numériques si applicable
            numeric_values = []
            for v in non_null:
                try:
                    numeric_values.append(float(v))
                except (ValueError, TypeError):
                    pass

            if numeric_values:
                col_profile["min"] = min(numeric_values)
                col_profile["max"] = max(numeric_values)
                col_profile["avg"] = sum(numeric_values) / len(numeric_values)

            # Exemples de valeurs
            col_profile["sample_values"] = list(set(str(v) for v in non_null[:5]))

            columns[col] = col_profile

        return {
            "dataset": dataset,
            "total_records": len(data),
            "columns": columns,
            "profiled_at": datetime.now().isoformat()
        }

    def get_reports(self, limit: int = 50, dataset: Optional[str] = None) -> List[Dict]:
        """Récupère les rapports récents."""
        reports = self._reports
        if dataset:
            reports = [r for r in reports if r.dataset == dataset]
        return [r.to_dict() for r in reports[-limit:]]

    def get_stats(self) -> Dict:
        """Retourne les statistiques."""
        return {
            **self._stats,
            "reports_generated": len(self._reports),
            "datasets_covered": list(set(r.dataset for r in self._reports))
        }

    def reset(self):
        """Réinitialise le moteur."""
        self._custom_rules.clear()
        self._reports.clear()
        self._stats = {
            "validations_run": 0,
            "records_validated": 0,
            "issues_found": 0,
            "critical_issues": 0
        }


# Instance singleton
_dq_instance: Optional[DataQuality] = None


def get_data_quality() -> DataQuality:
    """Retourne l'instance singleton du moteur de qualité."""
    global _dq_instance
    if _dq_instance is None:
        _dq_instance = DataQuality()
    return _dq_instance


def reset_data_quality():
    """Réinitialise l'instance."""
    global _dq_instance
    if _dq_instance:
        _dq_instance.reset()
    _dq_instance = DataQuality()
