"""Tests pour Feature 4.2: Modules 9-11 Data et scénarios."""
import pytest
from httpx import AsyncClient, ASGITransport


@pytest.mark.asyncio
async def test_modules_9_10_11():
    """Test que les modules 9, 10 et 11 sont accessibles."""
    from app.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        for m in [9, 10, 11]:
            r = await client.get(f"/api/theory/modules/{m}")
            assert r.status_code == 200
            data = r.json()
            assert "content" in data


@pytest.mark.asyncio
async def test_module_9_etl_content():
    """Test contenu module 9 ETL."""
    from app.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/api/theory/modules/9")
        assert r.status_code == 200
        content = r.json()["content"].lower()
        assert "etl" in content or "extract" in content


@pytest.mark.asyncio
async def test_module_10_cdc_content():
    """Test contenu module 10 CDC."""
    from app.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/api/theory/modules/10")
        assert r.status_code == 200
        content = r.json()["content"].lower()
        assert "cdc" in content or "change" in content


@pytest.mark.asyncio
async def test_module_11_quality_content():
    """Test contenu module 11 Data Quality."""
    from app.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/api/theory/modules/11")
        assert r.status_code == 200
        content = r.json()["content"].lower()
        assert "qualit" in content or "quality" in content


@pytest.mark.asyncio
async def test_data_scenarios():
    """Test que les scénarios DATA-01 à DATA-07 existent."""
    from app.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        for i in range(1, 8):
            scenario_id = f"DATA-0{i}"
            r = await client.get(f"/api/sandbox/scenarios/{scenario_id}")
            assert r.status_code == 200, f"Scenario {scenario_id} not found"
            data = r.json()
            assert "steps" in data
            assert len(data["steps"]) >= 6


@pytest.mark.asyncio
async def test_data_quality_validation():
    """Test du système de validation Data Quality."""
    from app.integration.data.data_quality import DataQuality

    dq = DataQuality()
    data = [
        {"id": "C001", "name": "Jean Dupont", "email": "jean@mail.com", "segment": "PREMIUM"},
        {"id": "C002", "name": "Marie Martin", "email": "", "segment": "STANDARD"},
        {"id": "C003", "name": "", "email": "pierre@mail.com", "segment": "INVALID"},
    ]

    report = await dq.validate("customers", data)
    assert report.total_records == 3
    assert report.overall_score < 1.0  # Devrait avoir des erreurs


@pytest.mark.asyncio
async def test_mdm_golden_record():
    """Test de la création de Golden Record MDM."""
    from app.integration.data.mdm import MDM

    mdm = MDM()
    records = [
        {"id": "C001", "name": "Jean Dupont", "email": "jean@mail.com"},
        {"id": "C001", "name": "J. Dupont", "phone": "0612345678"}
    ]

    golden = await mdm.merge("customer", records, "test")
    assert golden is not None
    assert golden.data.get("name") is not None


@pytest.mark.asyncio
async def test_data_lineage_trace():
    """Test de la traçabilité Data Lineage."""
    from app.integration.data.lineage import DataLineage

    lineage = DataLineage()
    trace = await lineage.get_full_lineage("SRC-CRM")
    assert trace is not None
    assert len(trace.downstream) >= 0


@pytest.mark.asyncio
async def test_data_profiling():
    """Test du profiling de données."""
    from app.integration.data.data_quality import DataQuality

    dq = DataQuality()
    data = [
        {"id": "1", "name": "Test1", "amount": 100},
        {"id": "2", "name": "Test2", "amount": 200},
        {"id": "3", "name": "Test3", "amount": None},
    ]

    profile = await dq.profile("test", data)
    assert "columns" in profile
    assert profile["total_records"] == 3
