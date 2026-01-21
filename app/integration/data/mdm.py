"""
MDM (Master Data Management) - Gestion des données de référence.

Fonctionnalités:
- Golden Record (enregistrement de référence)
- Matching/Deduplication
- Merge de données
- Survivorship rules
- Traçabilité des sources
"""
import asyncio
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field
from difflib import SequenceMatcher


class MatchConfidence(Enum):
    """Niveaux de confiance du matching."""
    EXACT = "exact"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NO_MATCH = "no_match"


class MergeStrategy(Enum):
    """Stratégies de fusion des données."""
    MOST_RECENT = "most_recent"      # Valeur la plus récente
    MOST_COMPLETE = "most_complete"  # Valeur la plus complète
    PRIORITY_SOURCE = "priority"      # Selon priorité de la source
    MANUAL = "manual"                 # Décision manuelle requise


@dataclass
class MatchResult:
    """Résultat d'un matching entre enregistrements."""
    record_a: Dict
    record_b: Dict
    confidence: MatchConfidence
    score: float  # 0-1
    matched_fields: List[str]
    mismatched_fields: List[str]

    def to_dict(self) -> Dict:
        """Convertit le résultat en dictionnaire."""
        return {
            "record_a_id": record_a.get("id") if isinstance(record_a := self.record_a, dict) else None,
            "record_b_id": record_b.get("id") if isinstance(record_b := self.record_b, dict) else None,
            "confidence": self.confidence.value,
            "score": self.score,
            "matched_fields": self.matched_fields,
            "mismatched_fields": self.mismatched_fields
        }


@dataclass
class GoldenRecord:
    """Enregistrement de référence consolidé."""
    id: str
    entity_type: str  # customer, policy, etc.
    data: Dict[str, Any]
    sources: List[Dict]  # Liste des sources avec leurs données
    created_at: str
    updated_at: str
    confidence_score: float
    merge_history: List[Dict] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convertit l'enregistrement en dictionnaire."""
        return {
            "id": self.id,
            "entity_type": self.entity_type,
            "data": self.data,
            "sources": self.sources,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "confidence_score": self.confidence_score,
            "merge_history": self.merge_history,
            "source_count": len(self.sources)
        }


class MDM:
    """
    Système de Master Data Management.

    Gère la création et maintenance des Golden Records
    (enregistrements de référence) à partir de multiples sources.

    Supporte:
    - Matching probabiliste
    - Règles de survivorship
    - Merge automatique ou manuel
    - Traçabilité complète
    """

    # Configuration des règles de matching par type d'entité
    MATCH_RULES = {
        "customer": {
            "exact_match_fields": ["email"],
            "fuzzy_match_fields": ["name"],
            "weight": {
                "email": 0.5,
                "name": 0.3,
                "phone": 0.2
            },
            "threshold": 0.7
        },
        "policy": {
            "exact_match_fields": ["id"],
            "fuzzy_match_fields": [],
            "weight": {
                "id": 1.0
            },
            "threshold": 0.9
        }
    }

    # Priorité des sources (plus haut = plus fiable)
    SOURCE_PRIORITY = {
        "crm": 100,
        "policy_admin": 90,
        "billing": 80,
        "external": 50,
        "manual": 110
    }

    def __init__(self, latency_ms: int = 50):
        """
        Initialise le système MDM.

        Args:
            latency_ms: Latence simulée en millisecondes
        """
        self.latency_ms = latency_ms
        self._golden_records: Dict[str, Dict[str, GoldenRecord]] = {
            "customer": {},
            "policy": {}
        }
        self._event_handlers: List[Callable] = []
        self._stats = {
            "golden_records_created": 0,
            "golden_records_updated": 0,
            "matches_found": 0,
            "merges_performed": 0
        }

        # Initialise quelques données
        self._init_sample_data()

    def _init_sample_data(self):
        """Initialise des données d'exemple."""
        sample_customers = [
            {
                "id": "GR-C001",
                "data": {
                    "id": "C001",
                    "name": "Jean Dupont",
                    "email": "jean.dupont@email.com",
                    "phone": "0612345678",
                    "segment": "PREMIUM"
                },
                "sources": [
                    {"source": "crm", "data": {"name": "Jean Dupont", "email": "jean.dupont@email.com"}, "timestamp": "2024-01-15"},
                    {"source": "billing", "data": {"name": "J. Dupont", "phone": "0612345678"}, "timestamp": "2024-01-10"}
                ]
            },
            {
                "id": "GR-C002",
                "data": {
                    "id": "C002",
                    "name": "Marie Martin",
                    "email": "marie.martin@email.com",
                    "segment": "STANDARD"
                },
                "sources": [
                    {"source": "crm", "data": {"name": "Marie Martin", "email": "marie.martin@email.com"}, "timestamp": "2024-01-20"}
                ]
            }
        ]

        for customer in sample_customers:
            gr = GoldenRecord(
                id=customer["id"],
                entity_type="customer",
                data=customer["data"],
                sources=customer["sources"],
                created_at="2024-01-01T00:00:00",
                updated_at=datetime.now().isoformat(),
                confidence_score=0.95
            )
            self._golden_records["customer"][gr.id] = gr

    def _generate_id(self, prefix: str = "GR") -> str:
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

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calcule la similarité entre deux chaînes."""
        if not str1 or not str2:
            return 0.0
        str1 = str1.lower().strip()
        str2 = str2.lower().strip()
        return SequenceMatcher(None, str1, str2).ratio()

    async def match(
        self,
        entity_type: str,
        record: Dict,
        candidates: Optional[List[Dict]] = None
    ) -> List[MatchResult]:
        """
        Recherche des correspondances pour un enregistrement.

        Args:
            entity_type: Type d'entité (customer, policy)
            record: Enregistrement à matcher
            candidates: Liste optionnelle de candidats (sinon utilise les golden records)

        Returns:
            Liste des correspondances triées par score
        """
        await self._simulate_latency()

        rules = self.MATCH_RULES.get(entity_type, {})
        if not rules:
            return []

        # Utilise les golden records existants si pas de candidats fournis
        if candidates is None:
            candidates = [gr.data for gr in self._golden_records.get(entity_type, {}).values()]

        results = []

        for candidate in candidates:
            if record.get("id") == candidate.get("id"):
                continue  # Ne pas matcher avec soi-même

            score = 0.0
            matched_fields = []
            mismatched_fields = []

            # Matching exact
            for field in rules.get("exact_match_fields", []):
                weight = rules.get("weight", {}).get(field, 0.5)
                val_a = record.get(field)
                val_b = candidate.get(field)

                if val_a and val_b:
                    if str(val_a).lower() == str(val_b).lower():
                        score += weight
                        matched_fields.append(field)
                    else:
                        mismatched_fields.append(field)

            # Matching fuzzy
            for field in rules.get("fuzzy_match_fields", []):
                weight = rules.get("weight", {}).get(field, 0.3)
                val_a = record.get(field)
                val_b = candidate.get(field)

                if val_a and val_b:
                    similarity = self._calculate_similarity(str(val_a), str(val_b))
                    if similarity >= 0.8:
                        score += weight * similarity
                        matched_fields.append(field)
                    elif similarity >= 0.5:
                        score += weight * similarity * 0.5
                    else:
                        mismatched_fields.append(field)

            # Détermine le niveau de confiance
            threshold = rules.get("threshold", 0.7)
            if score >= 0.95:
                confidence = MatchConfidence.EXACT
            elif score >= threshold:
                confidence = MatchConfidence.HIGH
            elif score >= threshold * 0.7:
                confidence = MatchConfidence.MEDIUM
            elif score >= threshold * 0.5:
                confidence = MatchConfidence.LOW
            else:
                confidence = MatchConfidence.NO_MATCH

            if confidence != MatchConfidence.NO_MATCH:
                results.append(MatchResult(
                    record_a=record,
                    record_b=candidate,
                    confidence=confidence,
                    score=score,
                    matched_fields=matched_fields,
                    mismatched_fields=mismatched_fields
                ))
                self._stats["matches_found"] += 1

        # Trie par score décroissant
        results.sort(key=lambda r: r.score, reverse=True)
        return results

    async def merge(
        self,
        entity_type: str,
        records: List[Dict],
        source: str,
        strategy: MergeStrategy = MergeStrategy.MOST_COMPLETE
    ) -> GoldenRecord:
        """
        Fusionne plusieurs enregistrements en un Golden Record.

        Args:
            entity_type: Type d'entité
            records: Enregistrements à fusionner
            source: Source des données
            strategy: Stratégie de fusion

        Returns:
            Le Golden Record résultant
        """
        await self._simulate_latency(len(records))

        if not records:
            raise ValueError("No records to merge")

        # Collecte tous les champs
        all_fields = set()
        for record in records:
            all_fields.update(record.keys())

        # Applique la stratégie de survivorship
        merged_data = {}

        for field in all_fields:
            values = [(r.get(field), i) for i, r in enumerate(records) if r.get(field)]

            if not values:
                continue

            if strategy == MergeStrategy.MOST_COMPLETE:
                # Prend la valeur la plus longue (supposée plus complète)
                best = max(values, key=lambda x: len(str(x[0])) if x[0] else 0)
                merged_data[field] = best[0]

            elif strategy == MergeStrategy.MOST_RECENT:
                # Prend la dernière valeur
                merged_data[field] = values[-1][0]

            elif strategy == MergeStrategy.PRIORITY_SOURCE:
                # Prend la valeur de la source la plus prioritaire
                merged_data[field] = values[0][0]

            else:
                # Par défaut: première valeur non nulle
                merged_data[field] = values[0][0]

        # Crée ou met à jour le Golden Record
        existing_gr = None
        if "id" in merged_data:
            # Cherche un GR existant avec cet ID
            for gr in self._golden_records.get(entity_type, {}).values():
                if gr.data.get("id") == merged_data.get("id"):
                    existing_gr = gr
                    break

        now = datetime.now().isoformat()

        if existing_gr:
            # Met à jour le GR existant
            existing_gr.data.update(merged_data)
            existing_gr.updated_at = now
            existing_gr.sources.append({
                "source": source,
                "data": records[0],
                "timestamp": now
            })
            existing_gr.merge_history.append({
                "action": "update",
                "timestamp": now,
                "records_merged": len(records),
                "strategy": strategy.value
            })
            self._stats["golden_records_updated"] += 1

            await self._notify_event("golden_record_updated", {
                "id": existing_gr.id,
                "entity_type": entity_type
            })

            return existing_gr

        else:
            # Crée un nouveau GR
            gr = GoldenRecord(
                id=self._generate_id(f"GR-{entity_type[0].upper()}"),
                entity_type=entity_type,
                data=merged_data,
                sources=[{
                    "source": source,
                    "data": r,
                    "timestamp": now
                } for r in records],
                created_at=now,
                updated_at=now,
                confidence_score=0.9,
                merge_history=[{
                    "action": "create",
                    "timestamp": now,
                    "records_merged": len(records),
                    "strategy": strategy.value
                }]
            )

            self._golden_records[entity_type][gr.id] = gr
            self._stats["golden_records_created"] += 1
            self._stats["merges_performed"] += 1

            await self._notify_event("golden_record_created", {
                "id": gr.id,
                "entity_type": entity_type
            })

            return gr

    async def get_golden_record(
        self,
        entity_type: str,
        record_id: str
    ) -> Optional[GoldenRecord]:
        """Récupère un Golden Record par son ID."""
        await self._simulate_latency(0.5)
        return self._golden_records.get(entity_type, {}).get(record_id)

    def get_golden_records(
        self,
        entity_type: str,
        limit: int = 100
    ) -> List[Dict]:
        """Récupère tous les Golden Records d'un type."""
        records = list(self._golden_records.get(entity_type, {}).values())
        return [r.to_dict() for r in records[:limit]]

    async def search_golden_records(
        self,
        entity_type: str,
        criteria: Dict
    ) -> List[Dict]:
        """
        Recherche des Golden Records selon des critères.

        Args:
            entity_type: Type d'entité
            criteria: Critères de recherche (ex: {"name": "Dupont"})

        Returns:
            Liste des Golden Records correspondants
        """
        await self._simulate_latency()

        results = []
        for gr in self._golden_records.get(entity_type, {}).values():
            match = True
            for key, value in criteria.items():
                gr_value = gr.data.get(key)
                if gr_value is None:
                    match = False
                    break
                # Recherche partielle insensible à la casse
                if str(value).lower() not in str(gr_value).lower():
                    match = False
                    break

            if match:
                results.append(gr.to_dict())

        return results

    def get_stats(self) -> Dict:
        """Retourne les statistiques."""
        return {
            **self._stats,
            "entity_types": list(self._golden_records.keys()),
            "total_golden_records": sum(
                len(records) for records in self._golden_records.values()
            )
        }

    def reset(self):
        """Réinitialise le système MDM."""
        self._golden_records = {
            "customer": {},
            "policy": {}
        }
        self._stats = {
            "golden_records_created": 0,
            "golden_records_updated": 0,
            "matches_found": 0,
            "merges_performed": 0
        }
        self._init_sample_data()


# Instance singleton
_mdm_instance: Optional[MDM] = None


def get_mdm() -> MDM:
    """Retourne l'instance singleton du MDM."""
    global _mdm_instance
    if _mdm_instance is None:
        _mdm_instance = MDM()
    return _mdm_instance


def reset_mdm():
    """Réinitialise l'instance."""
    global _mdm_instance
    if _mdm_instance:
        _mdm_instance.reset()
    _mdm_instance = MDM()
