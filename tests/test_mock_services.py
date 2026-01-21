"""
Tests unitaires pour les Mock Services.

Couvre:
- MockService base class
- Latence configurable
- Injection de pannes
- Statistiques
- Registry des services
"""
import pytest
import asyncio
from app.mocks.base import (
    MockService, MockServiceRegistry, MockServiceError,
    ServiceStatus, ServiceConfig
)


@pytest.fixture
def service():
    """Crée un nouveau service mock pour chaque test."""
    return MockService(
        name="test_service",
        default_latency=10,
        failure_rate=0.0
    )


@pytest.fixture
def registry():
    """Crée un nouveau registry pour chaque test."""
    return MockServiceRegistry()


# ========== TESTS MOCK SERVICE BASE ==========

class TestMockServiceBase:
    """Tests de la classe de base MockService."""

    def test_service_creation(self, service):
        """Vérifie la création d'un service."""
        assert service.name == "test_service"
        assert service.latency == 10
        assert service.failure_rate == 0.0
        assert service.status == ServiceStatus.RUNNING

    def test_initial_stats(self, service):
        """Vérifie les stats initiales."""
        assert service.stats["requests"] == 0
        assert service.stats["successes"] == 0
        assert service.stats["failures"] == 0

    def test_generate_id(self, service):
        """Vérifie la génération d'ID."""
        id1 = service._generate_id("TST-")
        id2 = service._generate_id("TST-")

        assert id1.startswith("TST-")
        assert id1 != id2  # IDs uniques


# ========== TESTS EXECUTE ==========

class TestExecute:
    """Tests de l'exécution d'opérations."""

    @pytest.mark.asyncio
    async def test_execute_success(self, service):
        """Vérifie l'exécution réussie."""
        async def handler():
            return {"result": "success"}

        result = await service.execute("test_op", handler)

        assert result == {"result": "success"}
        assert service.stats["requests"] == 1
        assert service.stats["successes"] == 1

    @pytest.mark.asyncio
    async def test_execute_sync_handler(self, service):
        """Vérifie l'exécution d'un handler synchrone."""
        def sync_handler():
            return {"sync": True}

        result = await service.execute("sync_op", sync_handler)

        assert result == {"sync": True}

    @pytest.mark.asyncio
    async def test_execute_with_args(self, service):
        """Vérifie l'exécution avec arguments."""
        async def handler(a, b, c=None):
            return {"a": a, "b": b, "c": c}

        result = await service.execute("args_op", handler, 1, 2, c=3)

        assert result == {"a": 1, "b": 2, "c": 3}

    @pytest.mark.asyncio
    async def test_execute_failure_from_handler(self, service):
        """Vérifie l'échec provenant du handler."""
        async def failing_handler():
            raise ValueError("Handler error")

        with pytest.raises(MockServiceError) as exc_info:
            await service.execute("fail_op", failing_handler)

        assert "Handler error" in str(exc_info.value)
        assert service.stats["failures"] == 1


# ========== TESTS LATENCE ==========

class TestLatency:
    """Tests de la latence simulée."""

    @pytest.mark.asyncio
    async def test_latency_is_applied(self):
        """Vérifie que la latence est appliquée."""
        service = MockService(name="latent", default_latency=100)

        import time
        start = time.time()

        async def handler():
            return {}

        await service.execute("op", handler)

        elapsed = (time.time() - start) * 1000

        # La latence devrait être d'environ 100ms (±20%)
        assert elapsed >= 80  # Au moins 80ms

    @pytest.mark.asyncio
    async def test_zero_latency(self):
        """Vérifie qu'une latence de 0 n'ajoute pas de délai."""
        service = MockService(name="fast", default_latency=0)

        import time
        start = time.time()

        async def handler():
            return {}

        await service.execute("op", handler)

        elapsed = (time.time() - start) * 1000

        assert elapsed < 50  # Devrait être rapide


# ========== TESTS INJECTION DE PANNES ==========

class TestFailureInjection:
    """Tests de l'injection de pannes."""

    @pytest.mark.asyncio
    async def test_failure_rate_100_percent(self):
        """Vérifie le taux d'échec de 100%."""
        service = MockService(name="failing", default_latency=0, failure_rate=1.0)

        async def handler():
            return {"result": "should not reach"}

        with pytest.raises(MockServiceError):
            await service.execute("op", handler)

    @pytest.mark.asyncio
    async def test_stopped_service_fails(self, service):
        """Vérifie qu'un service arrêté échoue."""
        service.stop()

        async def handler():
            return {}

        with pytest.raises(MockServiceError) as exc_info:
            await service.execute("op", handler)

        assert "unavailable" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_error_status_fails(self, service):
        """Vérifie qu'un service en erreur échoue."""
        service.set_status(ServiceStatus.ERROR)

        async def handler():
            return {}

        with pytest.raises(MockServiceError):
            await service.execute("op", handler)

    @pytest.mark.asyncio
    async def test_inject_failure_changes_status(self, service):
        """Vérifie que inject_failure change le status."""
        service.inject_failure(0.5)
        assert service.status == ServiceStatus.DEGRADED

        service.inject_failure(1.0)
        assert service.status == ServiceStatus.ERROR


# ========== TESTS CONFIGURATION ==========

class TestConfiguration:
    """Tests de la configuration du service."""

    def test_configure_latency(self, service):
        """Vérifie la configuration de latence."""
        service.configure(latency=200)
        assert service.latency == 200

    def test_configure_failure_rate(self, service):
        """Vérifie la configuration du taux d'échec."""
        service.configure(failure_rate=0.5)
        assert service.failure_rate == 0.5

    def test_configure_clamps_values(self, service):
        """Vérifie le clamping des valeurs."""
        service.configure(latency=-100)
        assert service.latency == 0

        service.configure(failure_rate=2.0)
        assert service.failure_rate == 1.0

        service.configure(failure_rate=-0.5)
        assert service.failure_rate == 0.0


# ========== TESTS START/STOP ==========

class TestStartStop:
    """Tests de start/stop du service."""

    def test_stop_changes_status(self, service):
        """Vérifie que stop change le status."""
        service.stop()
        assert service.status == ServiceStatus.STOPPED

    def test_start_changes_status(self, service):
        """Vérifie que start change le status."""
        service.stop()
        service.start()
        assert service.status == ServiceStatus.RUNNING


# ========== TESTS RESET ==========

class TestReset:
    """Tests de la réinitialisation."""

    @pytest.mark.asyncio
    async def test_reset_clears_stats(self, service):
        """Vérifie que reset efface les stats."""
        async def handler():
            return {}

        await service.execute("op", handler)
        assert service.stats["requests"] > 0

        service.reset()

        assert service.stats["requests"] == 0
        assert service.stats["successes"] == 0

    def test_reset_restores_defaults(self, service):
        """Vérifie que reset restaure les défauts."""
        service.inject_failure(1.0)
        service.stop()

        service.reset()

        assert service.status == ServiceStatus.RUNNING
        assert service.failure_rate == 0.0


# ========== TESTS STATISTIQUES ==========

class TestStatistics:
    """Tests des statistiques."""

    @pytest.mark.asyncio
    async def test_get_stats(self, service):
        """Vérifie get_stats."""
        async def handler():
            return {}

        await service.execute("op", handler)

        stats = service.get_stats()

        assert stats["name"] == "test_service"
        assert stats["status"] == "running"
        assert stats["requests"] == 1
        assert stats["successes"] == 1

    @pytest.mark.asyncio
    async def test_avg_latency_calculated(self, service):
        """Vérifie le calcul de latence moyenne."""
        async def handler():
            return {}

        await service.execute("op1", handler)
        await service.execute("op2", handler)

        stats = service.get_stats()

        assert stats["avg_latency_ms"] > 0


# ========== TESTS LOGS ==========

class TestLogs:
    """Tests des logs."""

    @pytest.mark.asyncio
    async def test_logs_recorded(self, service):
        """Vérifie l'enregistrement des logs."""
        async def handler():
            return {}

        await service.execute("test_op", handler)

        logs = service.get_logs()

        assert len(logs) > 0
        assert logs[0]["service"] == "test_service"
        assert logs[0]["operation"] == "test_op"
        assert logs[0]["success"] is True

    @pytest.mark.asyncio
    async def test_logs_limit(self, service):
        """Vérifie la limite des logs."""
        async def handler():
            return {}

        for _ in range(150):
            await service.execute("op", handler)

        # Les logs sont limités à 100
        assert len(service.logs) == 100

    @pytest.mark.asyncio
    async def test_get_logs_with_limit(self, service):
        """Vérifie get_logs avec limite."""
        async def handler():
            return {}

        for _ in range(20):
            await service.execute("op", handler)

        logs = service.get_logs(limit=5)

        assert len(logs) == 5


# ========== TESTS EVENT HANDLERS ==========

class TestEventHandlers:
    """Tests des handlers d'événements."""

    @pytest.mark.asyncio
    async def test_on_event_called(self, service):
        """Vérifie que on_event est appelé."""
        events = []

        def handler(event):
            events.append(event)

        service.on_event(handler)

        async def op():
            return {}

        await service.execute("test", op)

        assert len(events) > 0
        assert events[0]["operation"] == "test"


# ========== TESTS SERVICE STATUS ENUM ==========

class TestServiceStatusEnum:
    """Tests de l'enum ServiceStatus."""

    def test_status_values(self):
        """Vérifie les valeurs de status."""
        assert ServiceStatus.RUNNING.value == "running"
        assert ServiceStatus.DEGRADED.value == "degraded"
        assert ServiceStatus.ERROR.value == "error"
        assert ServiceStatus.STOPPED.value == "stopped"


# ========== TESTS MOCK SERVICE ERROR ==========

class TestMockServiceError:
    """Tests de MockServiceError."""

    def test_error_with_message(self):
        """Vérifie la création d'erreur avec message."""
        error = MockServiceError("Test error", 500)

        assert error.message == "Test error"
        assert error.status_code == 500
        assert str(error) == "Test error"

    def test_error_default_status_code(self):
        """Vérifie le status code par défaut."""
        error = MockServiceError("Error")

        assert error.status_code == 500


# ========== TESTS MOCK SERVICE REGISTRY ==========

class TestMockServiceRegistry:
    """Tests du registry des services."""

    def test_register_and_get(self, registry, service):
        """Vérifie register et get."""
        registry.register("svc1", service)

        retrieved = registry.get("svc1")

        assert retrieved is service

    def test_get_nonexistent(self, registry):
        """Vérifie le retour None pour service inexistant."""
        result = registry.get("nonexistent")
        assert result is None

    def test_get_all(self, registry):
        """Vérifie get_all."""
        svc1 = MockService(name="svc1")
        svc2 = MockService(name="svc2")

        registry.register("svc1", svc1)
        registry.register("svc2", svc2)

        all_services = registry.get_all()

        assert len(all_services) == 2
        assert "svc1" in all_services
        assert "svc2" in all_services

    @pytest.mark.asyncio
    async def test_get_all_stats(self, registry):
        """Vérifie get_all_stats."""
        svc1 = MockService(name="svc1", default_latency=0)
        svc2 = MockService(name="svc2", default_latency=0)

        registry.register("svc1", svc1)
        registry.register("svc2", svc2)

        async def handler():
            return {}

        await svc1.execute("op", handler)

        stats = registry.get_all_stats()

        assert len(stats) == 2
        svc1_stats = next(s for s in stats if s["name"] == "svc1")
        assert svc1_stats["requests"] == 1

    def test_reset_all(self, registry):
        """Vérifie reset_all."""
        svc1 = MockService(name="svc1")
        svc2 = MockService(name="svc2")

        registry.register("svc1", svc1)
        registry.register("svc2", svc2)

        svc1.inject_failure(1.0)
        svc2.stop()

        registry.reset_all()

        assert svc1.status == ServiceStatus.RUNNING
        assert svc2.status == ServiceStatus.RUNNING
        assert svc1.failure_rate == 0.0

    def test_stop_all(self, registry):
        """Vérifie stop_all."""
        svc1 = MockService(name="svc1")
        svc2 = MockService(name="svc2")

        registry.register("svc1", svc1)
        registry.register("svc2", svc2)

        registry.stop_all()

        assert svc1.status == ServiceStatus.STOPPED
        assert svc2.status == ServiceStatus.STOPPED

    def test_start_all(self, registry):
        """Vérifie start_all."""
        svc1 = MockService(name="svc1")
        svc2 = MockService(name="svc2")

        registry.register("svc1", svc1)
        registry.register("svc2", svc2)

        svc1.stop()
        svc2.stop()

        registry.start_all()

        assert svc1.status == ServiceStatus.RUNNING
        assert svc2.status == ServiceStatus.RUNNING


# ========== TESTS SERVICE CONFIG ==========

class TestServiceConfig:
    """Tests de ServiceConfig."""

    def test_default_config(self):
        """Vérifie la config par défaut."""
        config = ServiceConfig()

        assert config.latency_ms == 50
        assert config.failure_rate == 0.0
        assert config.status == ServiceStatus.RUNNING

    def test_custom_config(self):
        """Vérifie une config personnalisée."""
        config = ServiceConfig(
            latency_ms=200,
            failure_rate=0.5,
            status=ServiceStatus.DEGRADED
        )

        assert config.latency_ms == 200
        assert config.failure_rate == 0.5
        assert config.status == ServiceStatus.DEGRADED
