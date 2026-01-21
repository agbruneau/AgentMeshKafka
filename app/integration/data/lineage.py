"""
Data Lineage - Traçabilité des données pour simulation d'intégration.

Fonctionnalités:
- Graphe de lignage (origine → transformations → destinations)
- Traçabilité bout-en-bout
- Impact analysis (amont/aval)
- Visualisation du parcours des données
"""
import asyncio
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set
from enum import Enum
from dataclasses import dataclass, field


class NodeType(Enum):
    """Types de nœuds dans le graphe de lignage."""
    SOURCE = "source"           # Source de données
    TRANSFORMATION = "transformation"  # Transformation
    DESTINATION = "destination"  # Destination
    DATASET = "dataset"         # Dataset intermédiaire
    PIPELINE = "pipeline"       # Pipeline ETL/CDC


class EdgeType(Enum):
    """Types de liens dans le graphe."""
    DATA_FLOW = "data_flow"      # Flux de données
    DERIVES_FROM = "derives_from"  # Dérivation
    TRANSFORMS = "transforms"    # Transformation
    LOADS_TO = "loads_to"        # Chargement


@dataclass
class LineageNode:
    """Nœud dans le graphe de lignage."""
    id: str
    name: str
    type: NodeType
    metadata: Dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    properties: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convertit le nœud en dictionnaire."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "properties": self.properties
        }


@dataclass
class LineageEdge:
    """Lien entre deux nœuds du graphe."""
    id: str
    source_id: str
    target_id: str
    type: EdgeType
    metadata: Dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        """Convertit le lien en dictionnaire."""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "type": self.type.value,
            "metadata": self.metadata,
            "created_at": self.created_at
        }


@dataclass
class LineageTrace:
    """Trace de lignage complète pour un élément."""
    element_id: str
    element_name: str
    upstream: List[Dict]    # Nœuds en amont
    downstream: List[Dict]  # Nœuds en aval
    full_path: List[Dict]   # Chemin complet
    depth: int              # Profondeur du graphe

    def to_dict(self) -> Dict:
        """Convertit la trace en dictionnaire."""
        return {
            "element_id": self.element_id,
            "element_name": self.element_name,
            "upstream": self.upstream,
            "downstream": self.downstream,
            "full_path": self.full_path,
            "depth": self.depth
        }


class DataLineage:
    """
    Système de traçabilité des données (Data Lineage).

    Maintient un graphe dirigé représentant:
    - Les sources de données
    - Les transformations appliquées
    - Les destinations finales
    - Les relations entre éléments

    Permet:
    - Traçabilité bout-en-bout
    - Impact analysis
    - Root cause analysis
    """

    def __init__(self, latency_ms: int = 20):
        """
        Initialise le système de lignage.

        Args:
            latency_ms: Latence simulée en millisecondes
        """
        self.latency_ms = latency_ms
        self._nodes: Dict[str, LineageNode] = {}
        self._edges: Dict[str, LineageEdge] = {}
        self._adjacency: Dict[str, Set[str]] = {}  # node_id -> set(connected_node_ids)
        self._reverse_adjacency: Dict[str, Set[str]] = {}  # Pour la recherche amont
        self._event_handlers: List[Callable] = []
        self._stats = {
            "nodes_created": 0,
            "edges_created": 0,
            "traces_computed": 0
        }

        # Initialise le graphe avec des données d'exemple
        self._init_sample_lineage()

    def _init_sample_lineage(self):
        """Initialise un graphe de lignage d'exemple."""
        # Sources
        sources = [
            ("SRC-CRM", "CRM System", {"system": "Salesforce", "entity": "customers"}),
            ("SRC-PAS", "Policy Admin", {"system": "Guidewire", "entity": "policies"}),
            ("SRC-CLAIMS", "Claims System", {"system": "ClaimCenter", "entity": "claims"}),
            ("SRC-BILLING", "Billing System", {"system": "SAP", "entity": "invoices"})
        ]

        for src_id, name, props in sources:
            self._add_node(LineageNode(
                id=src_id, name=name, type=NodeType.SOURCE, properties=props
            ))

        # Transformations ETL
        transforms = [
            ("ETL-CUSTOMER", "Customer ETL", {"type": "etl", "schedule": "daily"}),
            ("ETL-POLICY", "Policy ETL", {"type": "etl", "schedule": "hourly"}),
            ("ETL-CLAIMS", "Claims ETL", {"type": "etl", "schedule": "daily"}),
            ("CDC-POLICY", "Policy CDC", {"type": "cdc", "mode": "streaming"})
        ]

        for t_id, name, props in transforms:
            self._add_node(LineageNode(
                id=t_id, name=name, type=NodeType.TRANSFORMATION, properties=props
            ))

        # Datasets intermédiaires
        datasets = [
            ("DS-CUSTOMER-STG", "Customer Staging", {"layer": "staging"}),
            ("DS-POLICY-STG", "Policy Staging", {"layer": "staging"}),
            ("DS-CLAIMS-STG", "Claims Staging", {"layer": "staging"}),
            ("DS-CUSTOMER-CLEAN", "Customer Cleaned", {"layer": "curated"}),
            ("DS-POLICY-CLEAN", "Policy Cleaned", {"layer": "curated"})
        ]

        for d_id, name, props in datasets:
            self._add_node(LineageNode(
                id=d_id, name=name, type=NodeType.DATASET, properties=props
            ))

        # Destinations
        destinations = [
            ("DEST-DWH", "Data Warehouse", {"type": "dwh", "database": "Snowflake"}),
            ("DEST-DATAMART", "Claims Datamart", {"type": "datamart"}),
            ("DEST-REPORTING", "BI Reporting", {"type": "reporting", "tool": "PowerBI"})
        ]

        for d_id, name, props in destinations:
            self._add_node(LineageNode(
                id=d_id, name=name, type=NodeType.DESTINATION, properties=props
            ))

        # Liens du graphe
        edges = [
            # Sources -> Transformations
            ("SRC-CRM", "ETL-CUSTOMER", EdgeType.DATA_FLOW),
            ("SRC-PAS", "ETL-POLICY", EdgeType.DATA_FLOW),
            ("SRC-PAS", "CDC-POLICY", EdgeType.DATA_FLOW),
            ("SRC-CLAIMS", "ETL-CLAIMS", EdgeType.DATA_FLOW),

            # Transformations -> Staging
            ("ETL-CUSTOMER", "DS-CUSTOMER-STG", EdgeType.TRANSFORMS),
            ("ETL-POLICY", "DS-POLICY-STG", EdgeType.TRANSFORMS),
            ("CDC-POLICY", "DS-POLICY-STG", EdgeType.TRANSFORMS),
            ("ETL-CLAIMS", "DS-CLAIMS-STG", EdgeType.TRANSFORMS),

            # Staging -> Curated
            ("DS-CUSTOMER-STG", "DS-CUSTOMER-CLEAN", EdgeType.DERIVES_FROM),
            ("DS-POLICY-STG", "DS-POLICY-CLEAN", EdgeType.DERIVES_FROM),

            # Curated -> Destinations
            ("DS-CUSTOMER-CLEAN", "DEST-DWH", EdgeType.LOADS_TO),
            ("DS-POLICY-CLEAN", "DEST-DWH", EdgeType.LOADS_TO),
            ("DS-CLAIMS-STG", "DEST-DATAMART", EdgeType.LOADS_TO),

            # DWH -> Reporting
            ("DEST-DWH", "DEST-REPORTING", EdgeType.DATA_FLOW),
            ("DEST-DATAMART", "DEST-REPORTING", EdgeType.DATA_FLOW)
        ]

        for src, tgt, edge_type in edges:
            self._add_edge(LineageEdge(
                id=self._generate_id("E"),
                source_id=src,
                target_id=tgt,
                type=edge_type
            ))

    def _generate_id(self, prefix: str = "LN") -> str:
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

    def _add_node(self, node: LineageNode):
        """Ajoute un nœud au graphe."""
        self._nodes[node.id] = node
        if node.id not in self._adjacency:
            self._adjacency[node.id] = set()
        if node.id not in self._reverse_adjacency:
            self._reverse_adjacency[node.id] = set()
        self._stats["nodes_created"] += 1

    def _add_edge(self, edge: LineageEdge):
        """Ajoute un lien au graphe."""
        self._edges[edge.id] = edge

        # Met à jour les listes d'adjacence
        if edge.source_id not in self._adjacency:
            self._adjacency[edge.source_id] = set()
        self._adjacency[edge.source_id].add(edge.target_id)

        if edge.target_id not in self._reverse_adjacency:
            self._reverse_adjacency[edge.target_id] = set()
        self._reverse_adjacency[edge.target_id].add(edge.source_id)

        self._stats["edges_created"] += 1

    async def add_node(
        self,
        name: str,
        node_type: str,
        properties: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ) -> LineageNode:
        """
        Ajoute un nouveau nœud au graphe de lignage.

        Args:
            name: Nom du nœud
            node_type: Type (source, transformation, destination, dataset)
            properties: Propriétés additionnelles
            metadata: Métadonnées

        Returns:
            Le nœud créé
        """
        await self._simulate_latency()

        node = LineageNode(
            id=self._generate_id("N"),
            name=name,
            type=NodeType(node_type),
            properties=properties or {},
            metadata=metadata or {}
        )

        self._add_node(node)

        await self._notify_event("lineage_node_added", {"node": node.to_dict()})

        return node

    async def add_edge(
        self,
        source_id: str,
        target_id: str,
        edge_type: str = "data_flow",
        metadata: Optional[Dict] = None
    ) -> LineageEdge:
        """
        Ajoute un lien entre deux nœuds.

        Args:
            source_id: ID du nœud source
            target_id: ID du nœud cible
            edge_type: Type de lien
            metadata: Métadonnées

        Returns:
            Le lien créé
        """
        await self._simulate_latency()

        if source_id not in self._nodes:
            raise ValueError(f"Source node not found: {source_id}")
        if target_id not in self._nodes:
            raise ValueError(f"Target node not found: {target_id}")

        edge = LineageEdge(
            id=self._generate_id("E"),
            source_id=source_id,
            target_id=target_id,
            type=EdgeType(edge_type),
            metadata=metadata or {}
        )

        self._add_edge(edge)

        await self._notify_event("lineage_edge_added", {"edge": edge.to_dict()})

        return edge

    async def trace_upstream(self, node_id: str, max_depth: int = 10) -> List[Dict]:
        """
        Trace les nœuds en amont (sources).

        Args:
            node_id: ID du nœud de départ
            max_depth: Profondeur maximale

        Returns:
            Liste des nœuds en amont
        """
        await self._simulate_latency()

        visited = set()
        result = []

        def _traverse(current_id: str, depth: int):
            if depth > max_depth or current_id in visited:
                return
            visited.add(current_id)

            for parent_id in self._reverse_adjacency.get(current_id, set()):
                if parent_id in self._nodes:
                    node = self._nodes[parent_id]
                    result.append({
                        **node.to_dict(),
                        "depth": depth
                    })
                    _traverse(parent_id, depth + 1)

        _traverse(node_id, 1)
        return result

    async def trace_downstream(self, node_id: str, max_depth: int = 10) -> List[Dict]:
        """
        Trace les nœuds en aval (destinations).

        Args:
            node_id: ID du nœud de départ
            max_depth: Profondeur maximale

        Returns:
            Liste des nœuds en aval
        """
        await self._simulate_latency()

        visited = set()
        result = []

        def _traverse(current_id: str, depth: int):
            if depth > max_depth or current_id in visited:
                return
            visited.add(current_id)

            for child_id in self._adjacency.get(current_id, set()):
                if child_id in self._nodes:
                    node = self._nodes[child_id]
                    result.append({
                        **node.to_dict(),
                        "depth": depth
                    })
                    _traverse(child_id, depth + 1)

        _traverse(node_id, 1)
        return result

    async def get_full_lineage(self, node_id: str) -> LineageTrace:
        """
        Récupère le lignage complet d'un nœud.

        Args:
            node_id: ID du nœud

        Returns:
            Trace complète avec amont et aval
        """
        await self._simulate_latency()

        if node_id not in self._nodes:
            raise ValueError(f"Node not found: {node_id}")

        node = self._nodes[node_id]
        upstream = await self.trace_upstream(node_id)
        downstream = await self.trace_downstream(node_id)

        # Construit le chemin complet
        full_path = []

        # Ajoute l'amont (inversé pour avoir les sources d'abord)
        for item in reversed(upstream):
            full_path.append(item)

        # Ajoute le nœud courant
        full_path.append({**node.to_dict(), "depth": 0, "is_current": True})

        # Ajoute l'aval
        full_path.extend(downstream)

        max_depth = max(
            max((item["depth"] for item in upstream), default=0),
            max((item["depth"] for item in downstream), default=0)
        )

        self._stats["traces_computed"] += 1

        return LineageTrace(
            element_id=node_id,
            element_name=node.name,
            upstream=upstream,
            downstream=downstream,
            full_path=full_path,
            depth=max_depth
        )

    async def impact_analysis(self, node_id: str) -> Dict:
        """
        Analyse l'impact d'un changement sur un nœud.

        Args:
            node_id: ID du nœud modifié

        Returns:
            Analyse d'impact avec les éléments affectés
        """
        await self._simulate_latency()

        downstream = await self.trace_downstream(node_id)

        # Groupe par type
        impact_by_type = {}
        for item in downstream:
            node_type = item["type"]
            if node_type not in impact_by_type:
                impact_by_type[node_type] = []
            impact_by_type[node_type].append(item)

        return {
            "source_node": node_id,
            "total_impacted": len(downstream),
            "impact_by_type": impact_by_type,
            "critical_destinations": [
                item for item in downstream
                if item["type"] == "destination"
            ]
        }

    def get_node(self, node_id: str) -> Optional[Dict]:
        """Récupère un nœud par son ID."""
        node = self._nodes.get(node_id)
        return node.to_dict() if node else None

    def get_nodes(self, node_type: Optional[str] = None) -> List[Dict]:
        """Récupère tous les nœuds, optionnellement filtrés par type."""
        nodes = list(self._nodes.values())
        if node_type:
            nodes = [n for n in nodes if n.type.value == node_type]
        return [n.to_dict() for n in nodes]

    def get_edges(self) -> List[Dict]:
        """Récupère tous les liens."""
        return [e.to_dict() for e in self._edges.values()]

    def get_graph(self) -> Dict:
        """Récupère le graphe complet pour visualisation."""
        return {
            "nodes": self.get_nodes(),
            "edges": self.get_edges()
        }

    def get_stats(self) -> Dict:
        """Retourne les statistiques."""
        return {
            **self._stats,
            "total_nodes": len(self._nodes),
            "total_edges": len(self._edges),
            "node_types": list(set(n.type.value for n in self._nodes.values()))
        }

    def reset(self):
        """Réinitialise le système de lignage."""
        self._nodes.clear()
        self._edges.clear()
        self._adjacency.clear()
        self._reverse_adjacency.clear()
        self._stats = {
            "nodes_created": 0,
            "edges_created": 0,
            "traces_computed": 0
        }
        self._init_sample_lineage()


# Instance singleton
_lineage_instance: Optional[DataLineage] = None


def get_data_lineage() -> DataLineage:
    """Retourne l'instance singleton du système de lignage."""
    global _lineage_instance
    if _lineage_instance is None:
        _lineage_instance = DataLineage()
    return _lineage_instance


def reset_data_lineage():
    """Réinitialise l'instance."""
    global _lineage_instance
    if _lineage_instance:
        _lineage_instance.reset()
    _lineage_instance = DataLineage()
