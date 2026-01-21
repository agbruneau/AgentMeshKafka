"""
Tests unitaires pour le Saga Orchestrator.

Couvre:
- Exécution séquentielle des étapes
- Compensation automatique en cas d'échec
- Retry avec backoff
- Suivi de l'état d'exécution
- SubscriptionSaga spécifique
"""
import pytest
import asyncio
from app.integration.events.saga import (
    SagaOrchestrator, SagaStep, SagaExecution, SagaStatus,
    SubscriptionSaga
)


@pytest.fixture
def saga():
    """Crée un nouvel orchestrateur pour chaque test."""
    return SagaOrchestrator()


# ========== TESTS AJOUT D'ÉTAPES ==========

class TestAddStep:
    """Tests de l'ajout d'étapes."""

    def test_add_step_with_function(self, saga):
        """Vérifie l'ajout d'une étape avec fonction."""
        async def action(ctx):
            return {"result": "done"}

        saga.add_step(action=action, name="step1")

        assert len(saga.steps) == 1
        assert saga.steps[0].name == "step1"

    def test_add_step_with_string(self, saga):
        """Vérifie l'ajout d'une étape avec nom string."""
        saga.add_step(action="validate_data")

        assert len(saga.steps) == 1
        assert saga.steps[0].name == "validate_data"

    def test_add_step_with_compensate(self, saga):
        """Vérifie l'ajout d'une étape avec compensation."""
        async def action(ctx):
            return {"result": "done"}

        async def compensate(ctx):
            return {"compensated": True}

        saga.add_step(action=action, compensate=compensate, name="step_with_comp")

        assert saga.steps[0].compensate is not None

    def test_add_step_with_config(self, saga):
        """Vérifie la configuration timeout/retries."""
        async def action(ctx):
            return {}

        saga.add_step(action=action, name="configured", timeout=60.0, retries=5)

        assert saga.steps[0].timeout == 60.0
        assert saga.steps[0].retries == 5


# ========== TESTS EXÉCUTION ==========

class TestExecution:
    """Tests de l'exécution de saga."""

    @pytest.mark.asyncio
    async def test_execute_all_steps_success(self, saga):
        """Vérifie l'exécution réussie de toutes les étapes."""
        results = []

        async def step1(ctx):
            results.append("step1")
            return {"step1": "done"}

        async def step2(ctx):
            results.append("step2")
            return {"step2": "done"}

        saga.add_step(action=step1, name="step1")
        saga.add_step(action=step2, name="step2")

        result = await saga.execute()

        assert result["status"] == "COMPLETED"
        assert results == ["step1", "step2"]

    @pytest.mark.asyncio
    async def test_execute_with_context(self, saga):
        """Vérifie le passage du contexte entre étapes."""
        async def step1(ctx):
            ctx["value"] = 10
            return {"added": True}

        async def step2(ctx):
            ctx["value"] = ctx["value"] * 2
            return {"multiplied": True}

        saga.add_step(action=step1, name="step1")
        saga.add_step(action=step2, name="step2")

        result = await saga.execute({"initial": True})

        assert result["context"]["value"] == 20
        assert result["context"]["initial"] is True

    @pytest.mark.asyncio
    async def test_execute_returns_saga_id(self, saga):
        """Vérifie que l'exécution retourne un saga_id."""
        async def step(ctx):
            return {}

        saga.add_step(action=step, name="step")

        result = await saga.execute()

        assert "saga_id" in result
        assert result["saga_id"].startswith("SAGA-")

    @pytest.mark.asyncio
    async def test_execute_updates_execution_record(self, saga):
        """Vérifie la mise à jour de l'enregistrement d'exécution."""
        async def step(ctx):
            return {}

        saga.add_step(action=step, name="test_step")

        result = await saga.execute()
        saga_id = result["saga_id"]

        execution = saga.get_execution(saga_id)

        assert execution is not None
        assert execution.status == SagaStatus.COMPLETED
        assert "test_step" in execution.steps_completed


# ========== TESTS ÉCHEC ET COMPENSATION ==========

class TestFailureAndCompensation:
    """Tests de l'échec et de la compensation."""

    @pytest.mark.asyncio
    async def test_failure_triggers_compensation(self, saga):
        """Vérifie que l'échec déclenche la compensation."""
        compensated = []

        async def step1(ctx):
            return {"step1": "done"}

        async def compensate1(ctx):
            compensated.append("step1")

        async def step2(ctx):
            raise ValueError("Step 2 failed")

        saga.add_step(action=step1, compensate=compensate1, name="step1")
        saga.add_step(action=step2, name="step2")

        result = await saga.execute()

        assert result["status"] == "COMPENSATED"
        assert "step1" in compensated

    @pytest.mark.asyncio
    async def test_compensation_order_is_reversed(self, saga):
        """Vérifie que la compensation est en ordre inverse."""
        compensated = []

        async def step1(ctx):
            return {}

        async def compensate1(ctx):
            compensated.append("step1")

        async def step2(ctx):
            return {}

        async def compensate2(ctx):
            compensated.append("step2")

        async def step3(ctx):
            raise ValueError("Fail")

        saga.add_step(action=step1, compensate=compensate1, name="step1")
        saga.add_step(action=step2, compensate=compensate2, name="step2")
        saga.add_step(action=step3, name="step3")

        result = await saga.execute()

        # Compensation en ordre inverse: step2 puis step1
        assert compensated == ["step2", "step1"]

    @pytest.mark.asyncio
    async def test_failed_step_recorded(self, saga):
        """Vérifie que l'étape échouée est enregistrée."""
        async def step1(ctx):
            return {}

        async def step2(ctx):
            raise ValueError("Specific error")

        saga.add_step(action=step1, name="step1")
        saga.add_step(action=step2, name="failing_step")

        result = await saga.execute()

        assert result["failed_step"] == "failing_step"
        assert "Specific error" in result["error"]

    @pytest.mark.asyncio
    async def test_steps_without_compensate_are_skipped(self, saga):
        """Vérifie que les étapes sans compensation sont ignorées."""
        compensated = []

        async def step1(ctx):
            return {}

        async def compensate1(ctx):
            compensated.append("step1")

        async def step2_no_comp(ctx):
            return {}

        async def step3(ctx):
            raise ValueError("Fail")

        saga.add_step(action=step1, compensate=compensate1, name="step1")
        saga.add_step(action=step2_no_comp, name="step2")  # Pas de compensation
        saga.add_step(action=step3, name="step3")

        result = await saga.execute()

        assert compensated == ["step1"]  # Seul step1 a une compensation


# ========== TESTS RETRY ==========

class TestRetry:
    """Tests du retry d'étapes."""

    @pytest.mark.asyncio
    async def test_retry_on_failure(self, saga):
        """Vérifie le retry sur échec."""
        call_count = 0

        async def flaky_step(ctx):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return {"success": True}

        saga.add_step(action=flaky_step, name="flaky", retries=5)

        result = await saga.execute()

        assert result["status"] == "COMPLETED"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_exhausted_retries_triggers_compensation(self, saga):
        """Vérifie la compensation après épuisement des retries."""
        async def always_fail(ctx):
            raise ValueError("Always fails")

        saga.add_step(action=always_fail, name="failing", retries=2)

        result = await saga.execute()

        assert result["status"] in ["COMPENSATED", "COMPENSATION_FAILED"]


# ========== TESTS TIMEOUT ==========

class TestStepTimeout:
    """Tests du timeout d'étapes."""

    @pytest.mark.asyncio
    async def test_step_timeout(self, saga):
        """Vérifie le timeout d'une étape."""
        async def slow_step(ctx):
            await asyncio.sleep(5.0)
            return {}

        saga.add_step(action=slow_step, name="slow", timeout=0.1, retries=1)

        result = await saga.execute()

        assert result["status"] in ["COMPENSATED", "COMPENSATION_FAILED"]


# ========== TESTS EVENT HANDLERS ==========

class TestEventHandlers:
    """Tests des handlers d'événements."""

    @pytest.mark.asyncio
    async def test_on_event_handler_called(self, saga):
        """Vérifie que les handlers d'événements sont appelés."""
        events = []

        def handler(event):
            events.append(event)

        saga.on_event(handler)

        async def step(ctx):
            return {}

        saga.add_step(action=step, name="step")
        await saga.execute()

        assert len(events) > 0
        assert any(e["type"] == "saga_started" for e in events)
        assert any(e["type"] == "saga_completed" for e in events)

    @pytest.mark.asyncio
    async def test_async_event_handler(self, saga):
        """Vérifie le support des handlers asynchrones."""
        events = []

        async def async_handler(event):
            events.append(event)

        saga.on_event(async_handler)

        async def step(ctx):
            return {}

        saga.add_step(action=step, name="step")
        await saga.execute()

        assert len(events) > 0


# ========== TESTS GET EXECUTION ==========

class TestGetExecution:
    """Tests de récupération d'exécution."""

    @pytest.mark.asyncio
    async def test_get_execution(self, saga):
        """Vérifie la récupération d'une exécution."""
        async def step(ctx):
            return {}

        saga.add_step(action=step, name="step")
        result = await saga.execute()

        execution = saga.get_execution(result["saga_id"])

        assert execution is not None
        assert execution.saga_id == result["saga_id"]

    @pytest.mark.asyncio
    async def test_get_nonexistent_execution(self, saga):
        """Vérifie le retour None pour exécution inexistante."""
        execution = saga.get_execution("SAGA-NONEXISTENT")
        assert execution is None

    @pytest.mark.asyncio
    async def test_get_all_executions(self, saga):
        """Vérifie la récupération de toutes les exécutions."""
        async def step(ctx):
            return {}

        saga.add_step(action=step, name="step")

        await saga.execute()
        await saga.execute()
        await saga.execute()

        executions = saga.get_all_executions()

        assert len(executions) == 3


# ========== TESTS SAGA EXECUTION MODEL ==========

class TestSagaExecutionModel:
    """Tests du modèle SagaExecution."""

    def test_to_dict(self):
        """Vérifie la sérialisation de SagaExecution."""
        execution = SagaExecution(
            saga_id="SAGA-TEST123",
            status=SagaStatus.COMPLETED,
            steps_completed=["step1", "step2"],
            context={"key": "value"}
        )

        data = execution.to_dict()

        assert data["saga_id"] == "SAGA-TEST123"
        assert data["status"] == "completed"
        assert data["steps_completed"] == ["step1", "step2"]
        assert data["context"] == {"key": "value"}


# ========== TESTS SUBSCRIPTION SAGA ==========

class TestSubscriptionSaga:
    """Tests de la saga de souscription d'assurance."""

    @pytest.mark.asyncio
    async def test_subscription_saga_success(self):
        """Vérifie l'exécution réussie de la saga de souscription."""
        saga = SubscriptionSaga()

        result = await saga.execute({"quote_id": "QUO-001"})

        assert result["status"] == "COMPLETED"
        assert "policy_id" in result["context"]
        assert "invoice_id" in result["context"]
        assert "document_ids" in result["context"]

    @pytest.mark.asyncio
    async def test_subscription_saga_all_steps_completed(self):
        """Vérifie que toutes les étapes sont complétées."""
        saga = SubscriptionSaga()

        result = await saga.execute({"quote_id": "QUO-001"})
        execution = saga.get_execution(result["saga_id"])

        expected_steps = [
            "validate_quote",
            "create_policy",
            "create_invoice",
            "generate_documents",
            "send_notifications"
        ]

        for step in expected_steps:
            assert step in execution.steps_completed

    @pytest.mark.asyncio
    async def test_subscription_saga_generates_ids(self):
        """Vérifie la génération d'IDs dans la saga."""
        saga = SubscriptionSaga()

        result = await saga.execute({"quote_id": "QUO-001"})
        ctx = result["context"]

        assert ctx["policy_id"].startswith("POL-")
        assert ctx["invoice_id"].startswith("INV-")
        assert len(ctx["document_ids"]) == 3


# ========== TESTS SYNC VS ASYNC ACTIONS ==========

class TestSyncAsyncActions:
    """Tests des actions synchrones vs asynchrones."""

    @pytest.mark.asyncio
    async def test_sync_action_execution(self, saga):
        """Vérifie l'exécution d'une action synchrone."""
        def sync_step(ctx):
            return {"sync": True}

        saga.add_step(action=sync_step, name="sync_step")

        result = await saga.execute()

        assert result["status"] == "COMPLETED"
        assert result["context"]["sync"] is True

    @pytest.mark.asyncio
    async def test_mixed_sync_async_actions(self, saga):
        """Vérifie le mélange d'actions sync et async."""
        def sync_step(ctx):
            return {"sync": True}

        async def async_step(ctx):
            return {"async": True}

        saga.add_step(action=sync_step, name="sync")
        saga.add_step(action=async_step, name="async")

        result = await saga.execute()

        assert result["status"] == "COMPLETED"
        assert result["context"]["sync"] is True
        assert result["context"]["async"] is True


# ========== TESTS COMPENSATION FAILURE ==========

class TestCompensationFailure:
    """Tests de l'échec de compensation."""

    @pytest.mark.asyncio
    async def test_compensation_failure_recorded(self, saga):
        """Vérifie que l'échec de compensation est enregistré."""
        async def step1(ctx):
            return {}

        async def failing_compensate(ctx):
            raise ValueError("Compensation failed")

        async def step2(ctx):
            raise ValueError("Step 2 failed")

        saga.add_step(action=step1, compensate=failing_compensate, name="step1")
        saga.add_step(action=step2, name="step2")

        result = await saga.execute()

        assert result["status"] == "COMPENSATION_FAILED"


# ========== TESTS SAGA STATUS ENUM ==========

class TestSagaStatusEnum:
    """Tests de l'enum SagaStatus."""

    def test_saga_status_values(self):
        """Vérifie les valeurs de SagaStatus."""
        assert SagaStatus.PENDING.value == "pending"
        assert SagaStatus.RUNNING.value == "running"
        assert SagaStatus.COMPLETED.value == "completed"
        assert SagaStatus.FAILED.value == "failed"
        assert SagaStatus.COMPENSATING.value == "compensating"
        assert SagaStatus.COMPENSATED.value == "compensated"
