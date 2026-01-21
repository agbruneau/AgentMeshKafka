"""
Tests unitaires pour le Pipeline ETL.

Couvre:
- Phases Extract, Transform, Load
- Filtres et transformations
- Gestion des jobs
- Statistiques et métriques
- Gestion des erreurs
"""
import pytest
import asyncio
from app.integration.data.etl_pipeline import (
    ETLPipeline, ETLJob, ETLStep, ETLStatus,
    get_etl_pipeline, reset_etl_pipeline
)


@pytest.fixture
def pipeline():
    """Crée un nouveau pipeline pour chaque test."""
    return ETLPipeline(latency_ms=10)  # Latence réduite pour les tests


@pytest.fixture(autouse=True)
def reset_singleton():
    """Réinitialise le singleton avant chaque test."""
    reset_etl_pipeline()
    yield
    reset_etl_pipeline()


# ========== TESTS EXÉCUTION DE BASE ==========

class TestBasicExecution:
    """Tests de l'exécution de base du pipeline."""

    @pytest.mark.asyncio
    async def test_run_returns_result(self, pipeline):
        """Vérifie que run retourne un résultat."""
        result = await pipeline.run({
            "source": "claims",
            "destination": "dwh"
        })

        assert result is not None
        assert "status" in result
        assert "job_id" in result

    @pytest.mark.asyncio
    async def test_run_completes_successfully(self, pipeline):
        """Vérifie l'exécution réussie."""
        result = await pipeline.run({
            "source": "claims",
            "destination": "dwh"
        })

        assert result["status"] == "completed"

    @pytest.mark.asyncio
    async def test_run_generates_job_id(self, pipeline):
        """Vérifie la génération d'ID de job."""
        result = await pipeline.run({
            "source": "policies",
            "destination": "datamart"
        })

        assert result["job_id"].startswith("ETL-")

    @pytest.mark.asyncio
    async def test_run_processes_all_records(self, pipeline):
        """Vérifie que tous les enregistrements sont traités."""
        result = await pipeline.run({
            "source": "claims",
            "destination": "dwh"
        })

        # claims a 5 enregistrements dans MOCK_DATA
        assert result["total_records"] == 5
        assert result["processed_records"] == 5


# ========== TESTS EXTRACTION ==========

class TestExtraction:
    """Tests de la phase d'extraction."""

    @pytest.mark.asyncio
    async def test_extract_from_claims(self, pipeline):
        """Vérifie l'extraction depuis claims."""
        result = await pipeline.run({
            "source": "claims",
            "destination": "dwh"
        })

        assert result["source"] == "claims"
        assert result["total_records"] == 5

    @pytest.mark.asyncio
    async def test_extract_from_policies(self, pipeline):
        """Vérifie l'extraction depuis policies."""
        result = await pipeline.run({
            "source": "policies",
            "destination": "dwh"
        })

        assert result["source"] == "policies"
        assert result["total_records"] == 4

    @pytest.mark.asyncio
    async def test_extract_from_customers(self, pipeline):
        """Vérifie l'extraction depuis customers."""
        result = await pipeline.run({
            "source": "customers",
            "destination": "dwh"
        })

        assert result["source"] == "customers"
        assert result["total_records"] == 3

    @pytest.mark.asyncio
    async def test_extract_with_filter(self, pipeline):
        """Vérifie l'extraction avec filtre."""
        result = await pipeline.run({
            "source": "claims",
            "destination": "dwh",
            "filters": {"status": "OPEN"}
        })

        # Seulement les claims OPEN
        assert result["total_records"] == 2

    @pytest.mark.asyncio
    async def test_extract_unknown_source_fails(self, pipeline):
        """Vérifie l'échec sur source inconnue."""
        result = await pipeline.run({
            "source": "unknown_source",
            "destination": "dwh"
        })

        assert result["status"] == "failed"
        assert "unknown" in result["error"].lower()


# ========== TESTS TRANSFORMATION ==========

class TestTransformation:
    """Tests de la phase de transformation."""

    @pytest.mark.asyncio
    async def test_transform_adds_etl_metadata(self, pipeline):
        """Vérifie l'ajout de métadonnées ETL."""
        result = await pipeline.run({
            "source": "customers",
            "destination": "dwh"
        })

        # Vérifier les données chargées
        data = pipeline.get_destination_data("dwh")

        assert len(data) > 0
        assert "_etl_timestamp" in data[0]
        assert "_etl_source" in data[0]

    @pytest.mark.asyncio
    async def test_transform_uppercase_names(self, pipeline):
        """Vérifie la transformation uppercase_names."""
        result = await pipeline.run({
            "source": "customers",
            "destination": "dwh",
            "transforms": ["uppercase_names"]
        })

        data = pipeline.get_destination_data("dwh")

        # Les noms devraient être en majuscules
        assert data[0]["name"] == "JEAN DUPONT"

    @pytest.mark.asyncio
    async def test_transform_calculate_totals(self, pipeline):
        """Vérifie la transformation calculate_totals."""
        result = await pipeline.run({
            "source": "claims",
            "destination": "dwh",
            "transforms": ["calculate_totals"]
        })

        data = pipeline.get_destination_data("dwh")

        # amount_with_tax = amount * 1.2
        assert "amount_with_tax" in data[0]
        assert data[0]["amount_with_tax"] == data[0]["amount"] * 1.2

    @pytest.mark.asyncio
    async def test_transform_normalize_dates(self, pipeline):
        """Vérifie la transformation normalize_dates."""
        result = await pipeline.run({
            "source": "claims",
            "destination": "dwh",
            "transforms": ["normalize_dates"]
        })

        data = pipeline.get_destination_data("dwh")

        assert "date_normalized" in data[0]
        assert data[0]["date_normalized"].endswith("T00:00:00Z")

    @pytest.mark.asyncio
    async def test_transform_enrich_segment(self, pipeline):
        """Vérifie la transformation enrich_segment."""
        result = await pipeline.run({
            "source": "customers",
            "destination": "dwh",
            "transforms": ["enrich_segment"]
        })

        data = pipeline.get_destination_data("dwh")

        # Jean Dupont est PREMIUM = 3
        premium_customer = next(c for c in data if c["segment"] == "PREMIUM")
        assert premium_customer["segment_score"] == 3

    @pytest.mark.asyncio
    async def test_multiple_transforms(self, pipeline):
        """Vérifie l'application de plusieurs transformations."""
        result = await pipeline.run({
            "source": "customers",
            "destination": "dwh",
            "transforms": ["uppercase_names", "enrich_segment"]
        })

        data = pipeline.get_destination_data("dwh")

        assert data[0]["name"].isupper()
        assert "segment_score" in data[0]


# ========== TESTS CHARGEMENT ==========

class TestLoading:
    """Tests de la phase de chargement."""

    @pytest.mark.asyncio
    async def test_load_to_destination(self, pipeline):
        """Vérifie le chargement vers la destination."""
        result = await pipeline.run({
            "source": "claims",
            "destination": "test_dwh"
        })

        data = pipeline.get_destination_data("test_dwh")

        assert len(data) == 5

    @pytest.mark.asyncio
    async def test_load_different_destinations(self, pipeline):
        """Vérifie le chargement vers différentes destinations."""
        await pipeline.run({
            "source": "claims",
            "destination": "dwh"
        })
        await pipeline.run({
            "source": "policies",
            "destination": "datamart"
        })
        await pipeline.run({
            "source": "customers",
            "destination": "datalake"
        })

        assert len(pipeline.get_destination_data("dwh")) == 5
        assert len(pipeline.get_destination_data("datamart")) == 4
        assert len(pipeline.get_destination_data("datalake")) == 3


# ========== TESTS JOB MANAGEMENT ==========

class TestJobManagement:
    """Tests de la gestion des jobs."""

    @pytest.mark.asyncio
    async def test_get_job(self, pipeline):
        """Vérifie la récupération d'un job."""
        result = await pipeline.run({
            "source": "claims",
            "destination": "dwh"
        })

        job = pipeline.get_job(result["job_id"])

        assert job is not None
        assert job["id"] == result["job_id"]
        assert job["source"] == "claims"
        assert job["destination"] == "dwh"

    @pytest.mark.asyncio
    async def test_get_nonexistent_job(self, pipeline):
        """Vérifie le retour None pour job inexistant."""
        job = pipeline.get_job("ETL-NONEXISTENT")
        assert job is None

    @pytest.mark.asyncio
    async def test_get_jobs(self, pipeline):
        """Vérifie la récupération de tous les jobs."""
        await pipeline.run({"source": "claims", "destination": "dwh"})
        await pipeline.run({"source": "policies", "destination": "dwh"})
        await pipeline.run({"source": "customers", "destination": "dwh"})

        jobs = pipeline.get_jobs()

        assert len(jobs) == 3

    @pytest.mark.asyncio
    async def test_get_jobs_with_limit(self, pipeline):
        """Vérifie la limite sur get_jobs."""
        for _ in range(5):
            await pipeline.run({"source": "claims", "destination": "dwh"})

        jobs = pipeline.get_jobs(limit=3)

        assert len(jobs) == 3


# ========== TESTS STEPS ==========

class TestETLSteps:
    """Tests des étapes ETL."""

    @pytest.mark.asyncio
    async def test_job_has_three_steps(self, pipeline):
        """Vérifie que chaque job a 3 étapes."""
        result = await pipeline.run({
            "source": "claims",
            "destination": "dwh"
        })

        job = pipeline.get_job(result["job_id"])

        assert len(job["steps"]) == 3

    @pytest.mark.asyncio
    async def test_steps_have_correct_phases(self, pipeline):
        """Vérifie les phases des étapes."""
        result = await pipeline.run({
            "source": "claims",
            "destination": "dwh"
        })

        job = pipeline.get_job(result["job_id"])
        phases = [s["phase"] for s in job["steps"]]

        assert phases == ["extract", "transform", "load"]

    @pytest.mark.asyncio
    async def test_steps_have_timestamps(self, pipeline):
        """Vérifie les timestamps des étapes."""
        result = await pipeline.run({
            "source": "claims",
            "destination": "dwh"
        })

        job = pipeline.get_job(result["job_id"])

        for step in job["steps"]:
            assert step["started_at"] is not None
            assert step["completed_at"] is not None

    @pytest.mark.asyncio
    async def test_steps_record_processed_count(self, pipeline):
        """Vérifie le comptage des enregistrements par étape."""
        result = await pipeline.run({
            "source": "customers",
            "destination": "dwh"
        })

        job = pipeline.get_job(result["job_id"])

        for step in job["steps"]:
            assert step["records_processed"] == 3


# ========== TESTS STATISTIQUES ==========

class TestStatistics:
    """Tests des statistiques du pipeline."""

    @pytest.mark.asyncio
    async def test_get_stats(self, pipeline):
        """Vérifie les statistiques."""
        await pipeline.run({"source": "claims", "destination": "dwh"})

        stats = pipeline.get_stats()

        assert stats["jobs_total"] == 1
        assert stats["jobs_completed"] == 1
        assert stats["records_extracted"] == 5
        assert stats["records_transformed"] == 5
        assert stats["records_loaded"] == 5

    @pytest.mark.asyncio
    async def test_stats_accumulate(self, pipeline):
        """Vérifie l'accumulation des stats."""
        await pipeline.run({"source": "claims", "destination": "dwh"})  # 5 records
        await pipeline.run({"source": "policies", "destination": "dwh"})  # 4 records

        stats = pipeline.get_stats()

        assert stats["jobs_total"] == 2
        assert stats["records_extracted"] == 9
        assert stats["records_loaded"] == 9

    @pytest.mark.asyncio
    async def test_failed_jobs_counted(self, pipeline):
        """Vérifie le comptage des jobs échoués."""
        await pipeline.run({"source": "invalid", "destination": "dwh"})

        stats = pipeline.get_stats()

        assert stats["jobs_failed"] == 1

    @pytest.mark.asyncio
    async def test_destinations_in_stats(self, pipeline):
        """Vérifie les destinations dans les stats."""
        await pipeline.run({"source": "claims", "destination": "dwh"})
        await pipeline.run({"source": "policies", "destination": "datamart"})

        stats = pipeline.get_stats()

        assert "dwh" in stats["destinations"]
        assert "datamart" in stats["destinations"]


# ========== TESTS RESET ==========

class TestReset:
    """Tests de la réinitialisation."""

    @pytest.mark.asyncio
    async def test_reset_clears_jobs(self, pipeline):
        """Vérifie que reset efface les jobs."""
        await pipeline.run({"source": "claims", "destination": "dwh"})

        pipeline.reset()

        assert len(pipeline.get_jobs()) == 0

    @pytest.mark.asyncio
    async def test_reset_clears_destinations(self, pipeline):
        """Vérifie que reset efface les destinations."""
        await pipeline.run({"source": "claims", "destination": "dwh"})

        pipeline.reset()

        assert len(pipeline.get_destination_data("dwh")) == 0

    @pytest.mark.asyncio
    async def test_reset_clears_stats(self, pipeline):
        """Vérifie que reset efface les stats."""
        await pipeline.run({"source": "claims", "destination": "dwh"})

        pipeline.reset()

        stats = pipeline.get_stats()
        assert stats["jobs_total"] == 0
        assert stats["records_extracted"] == 0


# ========== TESTS EVENT HANDLERS ==========

class TestEventHandlers:
    """Tests des handlers d'événements."""

    @pytest.mark.asyncio
    async def test_on_event_handler_called(self, pipeline):
        """Vérifie que les handlers sont appelés."""
        events = []

        def handler(event):
            events.append(event)

        pipeline.on_event(handler)
        await pipeline.run({"source": "claims", "destination": "dwh"})

        assert len(events) > 0
        event_types = [e["type"] for e in events]
        assert "etl_started" in event_types
        assert "etl_completed" in event_types

    @pytest.mark.asyncio
    async def test_async_event_handler(self, pipeline):
        """Vérifie le support des handlers asynchrones."""
        events = []

        async def async_handler(event):
            events.append(event)

        pipeline.on_event(async_handler)
        await pipeline.run({"source": "claims", "destination": "dwh"})

        assert len(events) > 0


# ========== TESTS ETL STATUS ENUM ==========

class TestETLStatusEnum:
    """Tests de l'enum ETLStatus."""

    def test_status_values(self):
        """Vérifie les valeurs de status."""
        assert ETLStatus.PENDING.value == "pending"
        assert ETLStatus.RUNNING.value == "running"
        assert ETLStatus.EXTRACTING.value == "extracting"
        assert ETLStatus.TRANSFORMING.value == "transforming"
        assert ETLStatus.LOADING.value == "loading"
        assert ETLStatus.COMPLETED.value == "completed"
        assert ETLStatus.FAILED.value == "failed"


# ========== TESTS ETL MODELS ==========

class TestETLModels:
    """Tests des modèles ETL."""

    def test_etl_step_to_dict(self):
        """Vérifie la sérialisation de ETLStep."""
        step = ETLStep(
            id="EXT-001",
            name="Extract",
            phase="extract",
            status=ETLStatus.COMPLETED,
            records_processed=100
        )

        data = step.to_dict()

        assert data["id"] == "EXT-001"
        assert data["name"] == "Extract"
        assert data["phase"] == "extract"
        assert data["status"] == "completed"
        assert data["records_processed"] == 100

    def test_etl_job_to_dict(self):
        """Vérifie la sérialisation de ETLJob."""
        job = ETLJob(
            id="ETL-001",
            name="Test Job",
            source="claims",
            destination="dwh",
            status=ETLStatus.COMPLETED,
            total_records=50,
            processed_records=50
        )

        data = job.to_dict()

        assert data["id"] == "ETL-001"
        assert data["source"] == "claims"
        assert data["destination"] == "dwh"
        assert data["status"] == "completed"


# ========== TESTS SINGLETON ==========

class TestSingleton:
    """Tests du singleton du pipeline."""

    def test_get_etl_pipeline_returns_same_instance(self):
        """Vérifie que get_etl_pipeline retourne la même instance."""
        pipeline1 = get_etl_pipeline()
        pipeline2 = get_etl_pipeline()

        assert pipeline1 is pipeline2

    @pytest.mark.asyncio
    async def test_reset_etl_pipeline_clears_data(self):
        """Vérifie que reset_etl_pipeline efface les données."""
        pipeline = get_etl_pipeline()
        await pipeline.run({"source": "claims", "destination": "dwh"})

        reset_etl_pipeline()

        new_pipeline = get_etl_pipeline()
        assert new_pipeline.get_stats()["jobs_total"] == 0


# ========== TESTS DURATION CALCULATION ==========

class TestDurationCalculation:
    """Tests du calcul de durée."""

    @pytest.mark.asyncio
    async def test_duration_calculated(self, pipeline):
        """Vérifie que la durée est calculée."""
        result = await pipeline.run({
            "source": "claims",
            "destination": "dwh"
        })

        assert "duration_ms" in result
        assert result["duration_ms"] >= 0


# ========== TESTS MOCK DATA ==========

class TestMockData:
    """Tests des données mock."""

    def test_mock_data_has_all_sources(self, pipeline):
        """Vérifie que toutes les sources sont présentes."""
        assert "claims" in pipeline.MOCK_DATA
        assert "policies" in pipeline.MOCK_DATA
        assert "customers" in pipeline.MOCK_DATA
        assert "invoices" in pipeline.MOCK_DATA

    def test_mock_data_has_records(self, pipeline):
        """Vérifie que les sources ont des enregistrements."""
        assert len(pipeline.MOCK_DATA["claims"]) > 0
        assert len(pipeline.MOCK_DATA["policies"]) > 0
        assert len(pipeline.MOCK_DATA["customers"]) > 0
