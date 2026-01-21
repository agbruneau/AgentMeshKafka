"""
Simulateur CDC (Change Data Capture) pour simulation d'intégration de données.

Fonctionnalités:
- Capture des changements (INSERT, UPDATE, DELETE)
- Publication des événements de changement
- Replay des changements depuis un timestamp
- Intégration avec le message broker
- Métriques et logging
"""
import asyncio
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, field


class ChangeOperation(Enum):
    """Types d'opérations de changement."""
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


@dataclass
class ChangeEvent:
    """Représente un événement de changement capturé."""
    id: str
    table: str
    operation: ChangeOperation
    timestamp: str
    sequence: int
    before: Optional[Dict] = None  # État avant le changement
    after: Optional[Dict] = None   # État après le changement
    primary_key: Dict = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convertit l'événement en dictionnaire."""
        return {
            "id": self.id,
            "table": self.table,
            "operation": self.operation.value,
            "timestamp": self.timestamp,
            "sequence": self.sequence,
            "before": self.before,
            "after": self.after,
            "primary_key": self.primary_key,
            "metadata": self.metadata
        }


class CDCSimulator:
    """
    Simulateur de Change Data Capture (CDC).

    Simule un système CDC type Debezium qui capture les changements
    de données en temps réel et les publie sous forme d'événements.

    Supporte:
    - Capture des INSERT, UPDATE, DELETE
    - Séquençage des événements
    - Replay depuis un point dans le temps
    - Publication vers handlers/broker
    - Filtrage par table
    """

    # Tables et données simulées
    TABLES = {
        "policies": {
            "primary_key": "id",
            "columns": ["id", "customer_id", "type", "premium", "status", "start_date", "end_date"]
        },
        "claims": {
            "primary_key": "id",
            "columns": ["id", "policy_id", "amount", "status", "date", "description"]
        },
        "customers": {
            "primary_key": "id",
            "columns": ["id", "name", "email", "phone", "segment", "address"]
        },
        "invoices": {
            "primary_key": "id",
            "columns": ["id", "policy_id", "amount", "status", "due_date", "paid_date"]
        }
    }

    def __init__(self, latency_ms: int = 50):
        """
        Initialise le simulateur CDC.

        Args:
            latency_ms: Latence simulée pour la capture en millisecondes
        """
        self.latency_ms = latency_ms
        self._events: List[ChangeEvent] = []
        self._sequence = 0
        self._handlers: List[Callable] = []
        self._subscriptions: Dict[str, List[Callable]] = {}  # Par table
        self._stats = {
            "events_captured": 0,
            "events_published": 0,
            "inserts": 0,
            "updates": 0,
            "deletes": 0
        }

        # État des tables (simulation de la base source)
        self._table_data: Dict[str, Dict[str, Dict]] = {
            table: {} for table in self.TABLES
        }

        # Initialise avec quelques données
        self._init_sample_data()

    def _init_sample_data(self):
        """Initialise des données d'exemple."""
        sample_data = {
            "policies": [
                {"id": "POL001", "customer_id": "C001", "type": "AUTO", "premium": 850.0, "status": "ACTIVE"},
                {"id": "POL002", "customer_id": "C002", "type": "HOME", "premium": 1200.0, "status": "ACTIVE"},
            ],
            "customers": [
                {"id": "C001", "name": "Jean Dupont", "email": "jean@email.com", "segment": "PREMIUM"},
                {"id": "C002", "name": "Marie Martin", "email": "marie@email.com", "segment": "STANDARD"},
            ],
            "claims": [
                {"id": "CLM001", "policy_id": "POL001", "amount": 1500.0, "status": "OPEN"},
            ]
        }

        for table, records in sample_data.items():
            pk_field = self.TABLES[table]["primary_key"]
            for record in records:
                pk = record[pk_field]
                self._table_data[table][pk] = record

    def _generate_id(self) -> str:
        """Génère un ID unique pour un événement."""
        return f"CDC-{uuid.uuid4().hex[:12].upper()}"

    def _get_next_sequence(self) -> int:
        """Retourne le prochain numéro de séquence."""
        self._sequence += 1
        return self._sequence

    async def _simulate_latency(self):
        """Simule la latence de capture."""
        if self.latency_ms > 0:
            import random
            actual = self.latency_ms * (0.8 + random.random() * 0.4)
            await asyncio.sleep(actual / 1000)

    async def simulate_change(
        self,
        table: str,
        operation: str,
        data: Dict[str, Any],
        before_data: Optional[Dict] = None
    ) -> ChangeEvent:
        """
        Simule un changement de données et capture l'événement.

        Args:
            table: Nom de la table
            operation: Type d'opération (INSERT, UPDATE, DELETE)
            data: Données du changement
            before_data: Données avant le changement (pour UPDATE/DELETE)

        Returns:
            L'événement de changement capturé
        """
        if table not in self.TABLES:
            raise ValueError(f"Table inconnue: {table}")

        await self._simulate_latency()

        # Convertit l'opération en enum
        op = ChangeOperation(operation.upper())

        # Détermine le primary key
        pk_field = self.TABLES[table]["primary_key"]
        pk_value = data.get(pk_field) or (before_data.get(pk_field) if before_data else None)

        # Prépare before/after selon l'opération
        before = None
        after = None

        if op == ChangeOperation.INSERT:
            after = data.copy()
            # Ajoute aux données de la table
            if pk_value:
                self._table_data[table][pk_value] = data.copy()
            self._stats["inserts"] += 1

        elif op == ChangeOperation.UPDATE:
            # Récupère l'état actuel comme before
            before = self._table_data[table].get(pk_value, {}).copy() if pk_value else before_data
            after = data.copy()
            # Met à jour les données
            if pk_value:
                if pk_value in self._table_data[table]:
                    self._table_data[table][pk_value].update(data)
                else:
                    self._table_data[table][pk_value] = data.copy()
            self._stats["updates"] += 1

        elif op == ChangeOperation.DELETE:
            # Récupère l'état actuel comme before
            before = self._table_data[table].get(pk_value, {}).copy() if pk_value else before_data
            # Supprime des données
            if pk_value and pk_value in self._table_data[table]:
                del self._table_data[table][pk_value]
            self._stats["deletes"] += 1

        # Crée l'événement
        event = ChangeEvent(
            id=self._generate_id(),
            table=table,
            operation=op,
            timestamp=datetime.now().isoformat(),
            sequence=self._get_next_sequence(),
            before=before,
            after=after,
            primary_key={pk_field: pk_value} if pk_value else {},
            metadata={
                "source": "cdc_simulator",
                "connector": "interop-learning-cdc"
            }
        )

        self._events.append(event)
        self._stats["events_captured"] += 1

        # Publie l'événement aux handlers
        await self._publish_event(event)

        return event

    async def _publish_event(self, event: ChangeEvent):
        """Publie un événement aux handlers enregistrés."""
        # Handlers globaux
        for handler in self._handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
                self._stats["events_published"] += 1
            except Exception:
                pass

        # Handlers par table
        if event.table in self._subscriptions:
            for handler in self._subscriptions[event.table]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception:
                    pass

    def on_change(self, handler: Callable, table: Optional[str] = None):
        """
        Enregistre un handler pour les événements de changement.

        Args:
            handler: Fonction appelée pour chaque événement
            table: Si spécifié, ne reçoit que les événements de cette table
        """
        if table:
            if table not in self._subscriptions:
                self._subscriptions[table] = []
            self._subscriptions[table].append(handler)
        else:
            self._handlers.append(handler)

    async def capture_since(self, sequence: int = 0) -> List[ChangeEvent]:
        """
        Récupère les événements depuis un numéro de séquence.

        Args:
            sequence: Numéro de séquence à partir duquel récupérer

        Returns:
            Liste des événements après ce numéro de séquence
        """
        await self._simulate_latency()
        return [e for e in self._events if e.sequence > sequence]

    def get_events(self, limit: int = 100, table: Optional[str] = None) -> List[Dict]:
        """
        Récupère les événements récents.

        Args:
            limit: Nombre maximum d'événements
            table: Filtrer par table

        Returns:
            Liste des événements
        """
        events = self._events
        if table:
            events = [e for e in events if e.table == table]
        return [e.to_dict() for e in events[-limit:]]

    def get_current_sequence(self) -> int:
        """Retourne le numéro de séquence actuel."""
        return self._sequence

    def get_table_state(self, table: str) -> Dict[str, Dict]:
        """Retourne l'état actuel d'une table."""
        if table not in self._table_data:
            return {}
        return self._table_data[table].copy()

    def get_stats(self) -> Dict:
        """Retourne les statistiques du CDC."""
        return {
            **self._stats,
            "current_sequence": self._sequence,
            "tables": list(self.TABLES.keys()),
            "events_stored": len(self._events)
        }

    def reset(self):
        """Réinitialise le simulateur."""
        self._events.clear()
        self._sequence = 0
        self._stats = {
            "events_captured": 0,
            "events_published": 0,
            "inserts": 0,
            "updates": 0,
            "deletes": 0
        }
        # Réinitialise les données des tables
        for table in self.TABLES:
            self._table_data[table] = {}
        self._init_sample_data()


# Instance singleton
_cdc_instance: Optional[CDCSimulator] = None


def get_cdc_simulator() -> CDCSimulator:
    """Retourne l'instance singleton du simulateur CDC."""
    global _cdc_instance
    if _cdc_instance is None:
        _cdc_instance = CDCSimulator()
    return _cdc_instance


def reset_cdc_simulator():
    """Réinitialise l'instance du simulateur."""
    global _cdc_instance
    if _cdc_instance:
        _cdc_instance.reset()
    _cdc_instance = CDCSimulator()
