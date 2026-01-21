"""
Pipeline ETL (Extract-Transform-Load) pour simulation d'intégration de données.

Fonctionnalités:
- Pipeline multi-étapes configurable
- Phases Extract, Transform, Load distinctes
- Gestion des erreurs et rollback
- Métriques et logging
- Simulation de latence réaliste
"""
import asyncio
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, field


class ETLStatus(Enum):
    """Statuts possibles d'un pipeline ETL."""
    PENDING = "pending"
    RUNNING = "running"
    EXTRACTING = "extracting"
    TRANSFORMING = "transforming"
    LOADING = "loading"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ETLStep:
    """Représente une étape dans le pipeline ETL."""
    id: str
    name: str
    phase: str  # extract, transform, load
    status: ETLStatus = ETLStatus.PENDING
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    records_processed: int = 0
    records_failed: int = 0
    error: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convertit l'étape en dictionnaire."""
        return {
            "id": self.id,
            "name": self.name,
            "phase": self.phase,
            "status": self.status.value,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "records_processed": self.records_processed,
            "records_failed": self.records_failed,
            "error": self.error,
            "metadata": self.metadata
        }


@dataclass
class ETLJob:
    """Représente un job ETL complet."""
    id: str
    name: str
    source: str
    destination: str
    status: ETLStatus = ETLStatus.PENDING
    steps: List[ETLStep] = field(default_factory=list)
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    total_records: int = 0
    processed_records: int = 0
    failed_records: int = 0
    error: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convertit le job en dictionnaire."""
        return {
            "id": self.id,
            "name": self.name,
            "source": self.source,
            "destination": self.destination,
            "status": self.status.value,
            "steps": [s.to_dict() for s in self.steps],
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "total_records": self.total_records,
            "processed_records": self.processed_records,
            "failed_records": self.failed_records,
            "error": self.error
        }


class ETLPipeline:
    """
    Simulateur de pipeline ETL (Extract-Transform-Load).

    Supporte:
    - Extraction depuis sources simulées (claims, policies, customers)
    - Transformations configurables
    - Chargement vers destinations (dwh, datamart, datalake)
    - Métriques détaillées
    - Gestion d'erreurs
    """

    # Données sources simulées
    MOCK_DATA = {
        "claims": [
            {"id": "CLM001", "policy_id": "POL001", "amount": 1500.0, "status": "OPEN", "date": "2024-01-15"},
            {"id": "CLM002", "policy_id": "POL002", "amount": 3200.0, "status": "CLOSED", "date": "2024-01-20"},
            {"id": "CLM003", "policy_id": "POL001", "amount": 800.0, "status": "PENDING", "date": "2024-02-01"},
            {"id": "CLM004", "policy_id": "POL003", "amount": 5000.0, "status": "OPEN", "date": "2024-02-10"},
            {"id": "CLM005", "policy_id": "POL002", "amount": 2100.0, "status": "CLOSED", "date": "2024-02-15"},
        ],
        "policies": [
            {"id": "POL001", "customer_id": "C001", "type": "AUTO", "premium": 850.0, "status": "ACTIVE"},
            {"id": "POL002", "customer_id": "C002", "type": "HOME", "premium": 1200.0, "status": "ACTIVE"},
            {"id": "POL003", "customer_id": "C001", "type": "HOME", "premium": 950.0, "status": "ACTIVE"},
            {"id": "POL004", "customer_id": "C003", "type": "AUTO", "premium": 720.0, "status": "CANCELLED"},
        ],
        "customers": [
            {"id": "C001", "name": "Jean Dupont", "email": "jean.dupont@email.com", "segment": "PREMIUM"},
            {"id": "C002", "name": "Marie Martin", "email": "marie.martin@email.com", "segment": "STANDARD"},
            {"id": "C003", "name": "Pierre Durant", "email": "pierre.durant@email.com", "segment": "BASIC"},
        ],
        "invoices": [
            {"id": "INV001", "policy_id": "POL001", "amount": 850.0, "status": "PAID", "due_date": "2024-01-31"},
            {"id": "INV002", "policy_id": "POL002", "amount": 1200.0, "status": "PENDING", "due_date": "2024-02-15"},
            {"id": "INV003", "policy_id": "POL003", "amount": 950.0, "status": "OVERDUE", "due_date": "2024-01-15"},
        ]
    }

    def __init__(self, latency_ms: int = 100):
        """
        Initialise le pipeline ETL.

        Args:
            latency_ms: Latence simulée par opération en millisecondes
        """
        self.latency_ms = latency_ms
        self._jobs: Dict[str, ETLJob] = {}
        self._destinations: Dict[str, List[Dict]] = {}
        self._event_handlers: List[Callable] = []
        self._stats = {
            "jobs_total": 0,
            "jobs_completed": 0,
            "jobs_failed": 0,
            "records_extracted": 0,
            "records_transformed": 0,
            "records_loaded": 0
        }

    def _generate_id(self, prefix: str = "ETL") -> str:
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

    async def run(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exécute un pipeline ETL complet.

        Args:
            config: Configuration du job
                - source: Source des données (claims, policies, customers)
                - destination: Destination (dwh, datamart, datalake)
                - transforms: Liste de transformations optionnelles
                - filters: Filtres optionnels

        Returns:
            Résultat du job avec statut et métriques
        """
        source = config.get("source", "claims")
        destination = config.get("destination", "dwh")
        transforms = config.get("transforms", [])
        filters = config.get("filters", {})

        # Crée le job
        job = ETLJob(
            id=self._generate_id(),
            name=f"ETL_{source}_to_{destination}",
            source=source,
            destination=destination,
            started_at=datetime.now().isoformat()
        )
        self._jobs[job.id] = job
        self._stats["jobs_total"] += 1

        await self._notify_event("etl_started", {"job": job.to_dict()})

        try:
            # Phase EXTRACT
            job.status = ETLStatus.EXTRACTING
            extract_step = ETLStep(
                id=self._generate_id("EXT"),
                name=f"Extract from {source}",
                phase="extract",
                started_at=datetime.now().isoformat()
            )
            job.steps.append(extract_step)

            extracted_data = await self._extract(source, filters)
            extract_step.records_processed = len(extracted_data)
            extract_step.status = ETLStatus.COMPLETED
            extract_step.completed_at = datetime.now().isoformat()
            job.total_records = len(extracted_data)
            self._stats["records_extracted"] += len(extracted_data)

            await self._notify_event("etl_extract_complete", {
                "job_id": job.id,
                "records": len(extracted_data)
            })

            # Phase TRANSFORM
            job.status = ETLStatus.TRANSFORMING
            transform_step = ETLStep(
                id=self._generate_id("TRF"),
                name="Transform data",
                phase="transform",
                started_at=datetime.now().isoformat()
            )
            job.steps.append(transform_step)

            transformed_data = await self._transform(extracted_data, transforms)
            transform_step.records_processed = len(transformed_data)
            transform_step.status = ETLStatus.COMPLETED
            transform_step.completed_at = datetime.now().isoformat()
            self._stats["records_transformed"] += len(transformed_data)

            await self._notify_event("etl_transform_complete", {
                "job_id": job.id,
                "records": len(transformed_data)
            })

            # Phase LOAD
            job.status = ETLStatus.LOADING
            load_step = ETLStep(
                id=self._generate_id("LDR"),
                name=f"Load to {destination}",
                phase="load",
                started_at=datetime.now().isoformat()
            )
            job.steps.append(load_step)

            loaded_count = await self._load(transformed_data, destination)
            load_step.records_processed = loaded_count
            load_step.status = ETLStatus.COMPLETED
            load_step.completed_at = datetime.now().isoformat()
            job.processed_records = loaded_count
            self._stats["records_loaded"] += loaded_count

            await self._notify_event("etl_load_complete", {
                "job_id": job.id,
                "records": loaded_count
            })

            # Job terminé avec succès
            job.status = ETLStatus.COMPLETED
            job.completed_at = datetime.now().isoformat()
            self._stats["jobs_completed"] += 1

            await self._notify_event("etl_completed", {"job": job.to_dict()})

            return {
                "status": "completed",
                "job_id": job.id,
                "source": source,
                "destination": destination,
                "total_records": job.total_records,
                "processed_records": job.processed_records,
                "failed_records": job.failed_records,
                "duration_ms": self._calculate_duration(job),
                "steps": [s.to_dict() for s in job.steps]
            }

        except Exception as e:
            # Job échoué
            job.status = ETLStatus.FAILED
            job.error = str(e)
            job.completed_at = datetime.now().isoformat()
            self._stats["jobs_failed"] += 1

            await self._notify_event("etl_failed", {
                "job_id": job.id,
                "error": str(e)
            })

            return {
                "status": "failed",
                "job_id": job.id,
                "error": str(e)
            }

    async def _extract(self, source: str, filters: Dict = None) -> List[Dict]:
        """
        Extrait les données depuis la source.

        Args:
            source: Nom de la source
            filters: Filtres à appliquer

        Returns:
            Liste des enregistrements extraits
        """
        await self._simulate_latency(1.5)  # Extraction plus lente

        # Récupère les données de la source simulée
        if source not in self.MOCK_DATA:
            raise ValueError(f"Source inconnue: {source}")

        data = self.MOCK_DATA[source].copy()

        # Applique les filtres si fournis
        if filters:
            for key, value in filters.items():
                data = [d for d in data if d.get(key) == value]

        return data

    async def _transform(self, data: List[Dict], transforms: List[str] = None) -> List[Dict]:
        """
        Transforme les données.

        Args:
            data: Données à transformer
            transforms: Liste des transformations à appliquer

        Returns:
            Données transformées
        """
        await self._simulate_latency(1.0)

        result = []
        for record in data:
            transformed = record.copy()

            # Ajoute des métadonnées de traitement
            transformed["_etl_timestamp"] = datetime.now().isoformat()
            transformed["_etl_source"] = "etl_pipeline"

            # Applique les transformations demandées
            if transforms:
                for transform in transforms:
                    if transform == "uppercase_names":
                        if "name" in transformed:
                            transformed["name"] = transformed["name"].upper()
                    elif transform == "calculate_totals":
                        if "amount" in transformed:
                            transformed["amount_with_tax"] = transformed["amount"] * 1.2
                    elif transform == "normalize_dates":
                        if "date" in transformed:
                            # Format ISO8601
                            transformed["date_normalized"] = transformed["date"] + "T00:00:00Z"
                    elif transform == "enrich_segment":
                        if "segment" in transformed:
                            segments = {"PREMIUM": 3, "STANDARD": 2, "BASIC": 1}
                            transformed["segment_score"] = segments.get(transformed["segment"], 0)

            result.append(transformed)

        return result

    async def _load(self, data: List[Dict], destination: str) -> int:
        """
        Charge les données vers la destination.

        Args:
            data: Données à charger
            destination: Nom de la destination

        Returns:
            Nombre d'enregistrements chargés
        """
        await self._simulate_latency(2.0)  # Chargement plus lent

        # Initialise la destination si nécessaire
        if destination not in self._destinations:
            self._destinations[destination] = []

        # Charge les données
        for record in data:
            self._destinations[destination].append(record)

        return len(data)

    def _calculate_duration(self, job: ETLJob) -> int:
        """Calcule la durée du job en millisecondes."""
        if job.started_at and job.completed_at:
            start = datetime.fromisoformat(job.started_at)
            end = datetime.fromisoformat(job.completed_at)
            return int((end - start).total_seconds() * 1000)
        return 0

    def get_job(self, job_id: str) -> Optional[Dict]:
        """Récupère un job par son ID."""
        job = self._jobs.get(job_id)
        return job.to_dict() if job else None

    def get_jobs(self, limit: int = 50) -> List[Dict]:
        """Récupère la liste des jobs récents."""
        jobs = list(self._jobs.values())[-limit:]
        return [j.to_dict() for j in jobs]

    def get_destination_data(self, destination: str, limit: int = 100) -> List[Dict]:
        """Récupère les données d'une destination."""
        if destination not in self._destinations:
            return []
        return self._destinations[destination][-limit:]

    def get_stats(self) -> Dict:
        """Retourne les statistiques du pipeline."""
        return {
            **self._stats,
            "destinations": list(self._destinations.keys()),
            "total_records_in_destinations": sum(
                len(data) for data in self._destinations.values()
            )
        }

    def reset(self):
        """Réinitialise le pipeline."""
        self._jobs.clear()
        self._destinations.clear()
        self._stats = {
            "jobs_total": 0,
            "jobs_completed": 0,
            "jobs_failed": 0,
            "records_extracted": 0,
            "records_transformed": 0,
            "records_loaded": 0
        }


# Instance singleton
_etl_instance: Optional[ETLPipeline] = None


def get_etl_pipeline() -> ETLPipeline:
    """Retourne l'instance singleton du pipeline ETL."""
    global _etl_instance
    if _etl_instance is None:
        _etl_instance = ETLPipeline()
    return _etl_instance


def reset_etl_pipeline():
    """Réinitialise l'instance du pipeline."""
    global _etl_instance
    if _etl_instance:
        _etl_instance.reset()
    _etl_instance = ETLPipeline()
