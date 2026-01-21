"""
Tests unitaires pour l'Event Store.

Couvre:
- Ajout d'événements (append)
- Lecture d'événements par aggregate
- Reconstruction d'état (rebuild_state)
- Snapshots
- Concurrence optimiste
- Projections
"""
import pytest
import asyncio
from app.integration.events.event_store import (
    EventStore, Event, ConcurrencyError,
    policy_reducer, get_event_store, reset_event_store
)


@pytest.fixture
def event_store():
    """Crée une nouvelle instance d'Event Store pour chaque test."""
    return EventStore()


@pytest.fixture(autouse=True)
def reset_singleton():
    """Réinitialise le singleton avant chaque test."""
    reset_event_store()
    yield
    reset_event_store()


# ========== TESTS APPEND ==========

class TestEventAppend:
    """Tests de l'ajout d'événements."""

    @pytest.mark.asyncio
    async def test_append_creates_event(self, event_store):
        """Vérifie que append crée un événement."""
        event = await event_store.append(
            aggregate_id="POL-001",
            event_data={"type": "PolicyCreated", "data": {"premium": 500}}
        )

        assert event is not None
        assert event.id.startswith("EVT-")
        assert event.aggregate_id == "POL-001"
        assert event.type == "PolicyCreated"
        assert event.version == 1

    @pytest.mark.asyncio
    async def test_append_increments_version(self, event_store):
        """Vérifie l'incrémentation de version."""
        event1 = await event_store.append("AGG-001", {"type": "Event1"})
        event2 = await event_store.append("AGG-001", {"type": "Event2"})
        event3 = await event_store.append("AGG-001", {"type": "Event3"})

        assert event1.version == 1
        assert event2.version == 2
        assert event3.version == 3

    @pytest.mark.asyncio
    async def test_append_with_expected_version_success(self, event_store):
        """Vérifie le succès avec expected_version correct."""
        await event_store.append("AGG-001", {"type": "Event1"})

        # Version attendue = 1 (version actuelle après premier append)
        event2 = await event_store.append(
            "AGG-001",
            {"type": "Event2"},
            expected_version=1
        )

        assert event2.version == 2

    @pytest.mark.asyncio
    async def test_append_with_wrong_expected_version_raises(self, event_store):
        """Vérifie l'erreur avec expected_version incorrect."""
        await event_store.append("AGG-001", {"type": "Event1"})

        with pytest.raises(ConcurrencyError) as exc_info:
            await event_store.append(
                "AGG-001",
                {"type": "Event2"},
                expected_version=5  # Version incorrecte
            )

        assert "Expected version 5" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_append_adds_to_global_stream(self, event_store):
        """Vérifie l'ajout au stream global."""
        await event_store.append("AGG-001", {"type": "Event1"})
        await event_store.append("AGG-002", {"type": "Event2"})

        global_stream = event_store.get_global_stream()

        assert len(global_stream) == 2

    @pytest.mark.asyncio
    async def test_append_with_metadata(self, event_store):
        """Vérifie l'ajout de métadonnées."""
        event = await event_store.append(
            "AGG-001",
            {
                "type": "TestEvent",
                "data": {"value": 42},
                "metadata": {"user_id": "USER-123", "source": "api"}
            }
        )

        assert event.metadata == {"user_id": "USER-123", "source": "api"}


# ========== TESTS GET EVENTS ==========

class TestGetEvents:
    """Tests de la récupération d'événements."""

    @pytest.mark.asyncio
    async def test_get_events_for_aggregate(self, event_store):
        """Vérifie la récupération des événements d'un aggregate."""
        await event_store.append("AGG-001", {"type": "Event1"})
        await event_store.append("AGG-001", {"type": "Event2"})
        await event_store.append("AGG-002", {"type": "Event3"})  # Autre aggregate

        events = await event_store.get_events("AGG-001")

        assert len(events) == 2
        assert events[0].type == "Event1"
        assert events[1].type == "Event2"

    @pytest.mark.asyncio
    async def test_get_events_from_version(self, event_store):
        """Vérifie le filtrage par version de départ."""
        await event_store.append("AGG-001", {"type": "Event1"})
        await event_store.append("AGG-001", {"type": "Event2"})
        await event_store.append("AGG-001", {"type": "Event3"})

        events = await event_store.get_events("AGG-001", from_version=2)

        assert len(events) == 2
        assert events[0].version == 2
        assert events[1].version == 3

    @pytest.mark.asyncio
    async def test_get_events_to_version(self, event_store):
        """Vérifie le filtrage par version de fin."""
        await event_store.append("AGG-001", {"type": "Event1"})
        await event_store.append("AGG-001", {"type": "Event2"})
        await event_store.append("AGG-001", {"type": "Event3"})

        events = await event_store.get_events("AGG-001", to_version=2)

        assert len(events) == 2
        assert events[-1].version == 2

    @pytest.mark.asyncio
    async def test_get_events_nonexistent_aggregate(self, event_store):
        """Vérifie le retour vide pour aggregate inexistant."""
        events = await event_store.get_events("NONEXISTENT")
        assert events == []

    @pytest.mark.asyncio
    async def test_get_current_version(self, event_store):
        """Vérifie get_current_version."""
        assert event_store.get_current_version("AGG-001") == 0

        await event_store.append("AGG-001", {"type": "Event1"})
        await event_store.append("AGG-001", {"type": "Event2"})

        assert event_store.get_current_version("AGG-001") == 2


# ========== TESTS REBUILD STATE ==========

class TestRebuildState:
    """Tests de la reconstruction d'état."""

    @pytest.mark.asyncio
    async def test_rebuild_state_with_default_reducer(self, event_store):
        """Vérifie la reconstruction avec le reducer par défaut."""
        await event_store.append("AGG-001", {"type": "Created", "data": {"name": "Test"}})
        await event_store.append("AGG-001", {"type": "Updated", "data": {"status": "active"}})

        state = await event_store.rebuild_state("AGG-001")

        assert state["name"] == "Test"
        assert state["status"] == "active"
        assert state["_version"] == 2

    @pytest.mark.asyncio
    async def test_rebuild_state_with_custom_reducer(self, event_store):
        """Vérifie la reconstruction avec un reducer custom."""
        await event_store.append("AGG-001", {"type": "Increment", "data": {"value": 5}})
        await event_store.append("AGG-001", {"type": "Increment", "data": {"value": 3}})

        def sum_reducer(state, event):
            current = state.get("total", 0)
            return {"total": current + event.data.get("value", 0)}

        state = await event_store.rebuild_state("AGG-001", reducer=sum_reducer)

        assert state["total"] == 8

    @pytest.mark.asyncio
    async def test_rebuild_state_to_specific_version(self, event_store):
        """Vérifie la reconstruction jusqu'à une version spécifique."""
        await event_store.append("AGG-001", {"type": "Event", "data": {"v": 1}})
        await event_store.append("AGG-001", {"type": "Event", "data": {"v": 2}})
        await event_store.append("AGG-001", {"type": "Event", "data": {"v": 3}})

        state = await event_store.rebuild_state("AGG-001", to_version=2)

        assert state["v"] == 2
        assert state["_version"] == 2


# ========== TESTS POLICY REDUCER ==========

class TestPolicyReducer:
    """Tests du reducer spécifique aux polices."""

    @pytest.mark.asyncio
    async def test_policy_created(self, event_store):
        """Vérifie PolicyCreated."""
        await event_store.append("POL-001", {
            "type": "PolicyCreated",
            "data": {
                "policy_number": "POL-001",
                "customer_id": "CUST-001",
                "product": "AUTO",
                "premium": 500.0
            }
        })

        state = await event_store.rebuild_state("POL-001", reducer=policy_reducer)

        assert state["policy_number"] == "POL-001"
        assert state["customer_id"] == "CUST-001"
        assert state["status"] == "DRAFT"
        assert state["premium"] == 500.0

    @pytest.mark.asyncio
    async def test_policy_activated(self, event_store):
        """Vérifie PolicyActivated."""
        await event_store.append("POL-001", {
            "type": "PolicyCreated",
            "data": {"policy_number": "POL-001", "product": "AUTO", "premium": 500}
        })
        await event_store.append("POL-001", {
            "type": "PolicyActivated",
            "data": {"start_date": "2024-01-01", "end_date": "2025-01-01"}
        })

        state = await event_store.rebuild_state("POL-001", reducer=policy_reducer)

        assert state["status"] == "ACTIVE"
        assert state["start_date"] == "2024-01-01"
        assert state["end_date"] == "2025-01-01"

    @pytest.mark.asyncio
    async def test_policy_cancelled(self, event_store):
        """Vérifie PolicyCancelled."""
        await event_store.append("POL-001", {
            "type": "PolicyCreated",
            "data": {"policy_number": "POL-001"}
        })
        await event_store.append("POL-001", {
            "type": "PolicyCancelled",
            "data": {"reason": "Non-payment"}
        })

        state = await event_store.rebuild_state("POL-001", reducer=policy_reducer)

        assert state["status"] == "CANCELLED"
        assert state["cancellation_reason"] == "Non-payment"

    @pytest.mark.asyncio
    async def test_policy_history_tracking(self, event_store):
        """Vérifie le suivi de l'historique."""
        await event_store.append("POL-001", {"type": "PolicyCreated", "data": {}})
        await event_store.append("POL-001", {"type": "PolicyActivated", "data": {}})
        await event_store.append("POL-001", {"type": "PolicyModified", "data": {}})

        state = await event_store.rebuild_state("POL-001", reducer=policy_reducer)

        assert len(state["history"]) == 3
        assert state["history"][0]["event"] == "PolicyCreated"
        assert state["history"][1]["event"] == "PolicyActivated"
        assert state["history"][2]["event"] == "PolicyModified"


# ========== TESTS SNAPSHOTS ==========

class TestSnapshots:
    """Tests des snapshots."""

    @pytest.mark.asyncio
    async def test_create_and_get_snapshot(self, event_store):
        """Vérifie la création et récupération de snapshot."""
        state = {"name": "Test", "value": 42}

        await event_store.create_snapshot("AGG-001", state)
        snapshot = await event_store.get_snapshot("AGG-001")

        assert snapshot is not None
        assert snapshot["name"] == "Test"
        assert snapshot["value"] == 42
        assert "_snapshot_at" in snapshot

    @pytest.mark.asyncio
    async def test_snapshot_includes_version(self, event_store):
        """Vérifie que le snapshot inclut la version."""
        await event_store.append("AGG-001", {"type": "Event1"})
        await event_store.append("AGG-001", {"type": "Event2"})

        state = {"computed": "state"}
        await event_store.create_snapshot("AGG-001", state)

        snapshot = await event_store.get_snapshot("AGG-001")

        assert snapshot["_snapshot_version"] == 2

    @pytest.mark.asyncio
    async def test_get_nonexistent_snapshot(self, event_store):
        """Vérifie le retour None pour snapshot inexistant."""
        snapshot = await event_store.get_snapshot("NONEXISTENT")
        assert snapshot is None


# ========== TESTS PROJECTIONS ==========

class TestProjections:
    """Tests des projections."""

    @pytest.mark.asyncio
    async def test_projection_handler_called(self, event_store):
        """Vérifie que les handlers de projection sont appelés."""
        events_received = []

        def projection_handler(event):
            events_received.append(event)

        event_store.register_projection(projection_handler)
        await event_store.append("AGG-001", {"type": "TestEvent"})

        assert len(events_received) == 1
        assert events_received[0].type == "TestEvent"

    @pytest.mark.asyncio
    async def test_async_projection_handler(self, event_store):
        """Vérifie le support des handlers asynchrones."""
        events_received = []

        async def async_projection(event):
            events_received.append(event)

        event_store.register_projection(async_projection)
        await event_store.append("AGG-001", {"type": "TestEvent"})

        assert len(events_received) == 1

    @pytest.mark.asyncio
    async def test_multiple_projections(self, event_store):
        """Vérifie plusieurs projections simultanées."""
        projection_1_calls = []
        projection_2_calls = []

        def handler_1(event):
            projection_1_calls.append(event)

        def handler_2(event):
            projection_2_calls.append(event)

        event_store.register_projection(handler_1)
        event_store.register_projection(handler_2)

        await event_store.append("AGG-001", {"type": "Event"})

        assert len(projection_1_calls) == 1
        assert len(projection_2_calls) == 1


# ========== TESTS GLOBAL STREAM ==========

class TestGlobalStream:
    """Tests du stream global."""

    @pytest.mark.asyncio
    async def test_get_global_stream(self, event_store):
        """Vérifie la récupération du stream global."""
        await event_store.append("AGG-001", {"type": "Event1"})
        await event_store.append("AGG-002", {"type": "Event2"})
        await event_store.append("AGG-001", {"type": "Event3"})

        stream = event_store.get_global_stream()

        assert len(stream) == 3

    @pytest.mark.asyncio
    async def test_get_global_stream_with_limit(self, event_store):
        """Vérifie la limite du stream global."""
        for i in range(10):
            await event_store.append(f"AGG-{i}", {"type": f"Event{i}"})

        stream = event_store.get_global_stream(limit=5)

        assert len(stream) == 5

    @pytest.mark.asyncio
    async def test_get_events_by_type(self, event_store):
        """Vérifie le filtrage par type d'événement."""
        await event_store.append("AGG-001", {"type": "TypeA"})
        await event_store.append("AGG-002", {"type": "TypeB"})
        await event_store.append("AGG-003", {"type": "TypeA"})

        events = event_store.get_events_by_type("TypeA")

        assert len(events) == 2
        assert all(e["type"] == "TypeA" for e in events)


# ========== TESTS STATISTIQUES ==========

class TestStatistics:
    """Tests des statistiques."""

    @pytest.mark.asyncio
    async def test_get_stats(self, event_store):
        """Vérifie les statistiques de l'Event Store."""
        await event_store.append("AGG-001", {"type": "TypeA"})
        await event_store.append("AGG-001", {"type": "TypeB"})
        await event_store.append("AGG-002", {"type": "TypeA"})

        stats = event_store.get_stats()

        assert stats["total_events"] == 3
        assert stats["aggregates_count"] == 2
        assert "TypeA" in stats["event_types"]
        assert "TypeB" in stats["event_types"]

    @pytest.mark.asyncio
    async def test_reset(self, event_store):
        """Vérifie la réinitialisation."""
        await event_store.append("AGG-001", {"type": "Event"})
        await event_store.create_snapshot("AGG-001", {"state": "value"})

        event_store.reset()

        assert event_store.get_stats()["total_events"] == 0
        assert event_store.get_stats()["aggregates_count"] == 0
        assert event_store.get_stats()["snapshots_count"] == 0


# ========== TESTS EVENT MODEL ==========

class TestEventModel:
    """Tests du modèle Event."""

    def test_event_to_dict(self):
        """Vérifie la sérialisation d'un événement."""
        event = Event(
            id="EVT-TEST123",
            aggregate_id="AGG-001",
            type="TestEvent",
            data={"key": "value"},
            version=5,
            metadata={"user": "test"}
        )

        data = event.to_dict()

        assert data["id"] == "EVT-TEST123"
        assert data["aggregate_id"] == "AGG-001"
        assert data["type"] == "TestEvent"
        assert data["data"] == {"key": "value"}
        assert data["version"] == 5
        assert data["metadata"] == {"user": "test"}

    def test_event_default_values(self):
        """Vérifie les valeurs par défaut d'un événement."""
        event = Event(
            id="EVT-TEST",
            aggregate_id="AGG-001",
            type="Test",
            data={}
        )

        assert event.version == 0
        assert event.metadata == {}


# ========== TESTS SINGLETON ==========

class TestSingleton:
    """Tests du singleton de l'Event Store."""

    def test_get_event_store_returns_same_instance(self):
        """Vérifie que get_event_store retourne la même instance."""
        store1 = get_event_store()
        store2 = get_event_store()

        assert store1 is store2

    @pytest.mark.asyncio
    async def test_reset_event_store_clears_data(self):
        """Vérifie que reset_event_store efface les données."""
        store = get_event_store()
        await store.append("AGG-001", {"type": "Event"})

        reset_event_store()

        new_store = get_event_store()
        assert new_store.get_stats()["total_events"] == 0
