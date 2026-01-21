"""Tests pour Feature 4.1: ETL & CDC."""
import pytest
from app.integration.data.etl_pipeline import ETLPipeline
from app.integration.data.cdc_simulator import CDCSimulator


@pytest.mark.asyncio
async def test_etl_full():
    """Test d'un pipeline ETL complet."""
    etl = ETLPipeline()
    result = await etl.run({"source": "claims", "destination": "dwh"})
    assert result["status"] == "completed"
    assert result["total_records"] > 0
    assert result["processed_records"] > 0


@pytest.mark.asyncio
async def test_etl_with_transforms():
    """Test ETL avec transformations."""
    etl = ETLPipeline()
    result = await etl.run({
        "source": "policies",
        "destination": "datamart",
        "transforms": ["calculate_totals"]
    })
    assert result["status"] == "completed"


@pytest.mark.asyncio
async def test_etl_with_filters():
    """Test ETL avec filtres."""
    etl = ETLPipeline()
    result = await etl.run({
        "source": "claims",
        "destination": "dwh",
        "filters": {"status": "OPEN"}
    })
    assert result["status"] == "completed"


@pytest.mark.asyncio
async def test_etl_stats():
    """Test des statistiques ETL."""
    etl = ETLPipeline()
    await etl.run({"source": "customers", "destination": "dwh"})
    stats = etl.get_stats()
    assert stats["jobs_total"] >= 1
    assert stats["jobs_completed"] >= 1


@pytest.mark.asyncio
async def test_cdc_capture():
    """Test de la capture CDC."""
    cdc = CDCSimulator()
    await cdc.simulate_change("policies", "UPDATE", {"id": "P1", "status": "ACTIVE"})
    changes = await cdc.capture_since(0)
    assert len(changes) >= 1
    assert changes[-1].operation.value == "UPDATE"


@pytest.mark.asyncio
async def test_cdc_insert():
    """Test capture INSERT."""
    cdc = CDCSimulator()
    initial_seq = cdc.get_current_sequence()
    event = await cdc.simulate_change(
        "policies",
        "INSERT",
        {"id": "POL-NEW", "customer_id": "C001", "premium": 500.0}
    )
    assert event.operation.value == "INSERT"
    assert event.after is not None
    assert event.sequence > initial_seq


@pytest.mark.asyncio
async def test_cdc_delete():
    """Test capture DELETE."""
    cdc = CDCSimulator()
    # D'abord insérer
    await cdc.simulate_change(
        "policies",
        "INSERT",
        {"id": "POL-DEL", "customer_id": "C001"}
    )
    # Puis supprimer
    event = await cdc.simulate_change(
        "policies",
        "DELETE",
        {"id": "POL-DEL"}
    )
    assert event.operation.value == "DELETE"


@pytest.mark.asyncio
async def test_cdc_stats():
    """Test des statistiques CDC."""
    cdc = CDCSimulator()
    await cdc.simulate_change("claims", "INSERT", {"id": "CLM-NEW", "amount": 100})
    stats = cdc.get_stats()
    assert stats["events_captured"] >= 1
    assert stats["inserts"] >= 1


@pytest.mark.asyncio
async def test_cdc_event_handler():
    """Test des handlers d'événements CDC."""
    cdc = CDCSimulator()
    received_events = []

    def handler(event):
        received_events.append(event)

    cdc.on_change(handler)
    await cdc.simulate_change("customers", "UPDATE", {"id": "C001", "name": "Test"})

    assert len(received_events) >= 1
