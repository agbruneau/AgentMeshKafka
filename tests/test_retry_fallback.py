"""
Tests unitaires pour les patterns de résilience: Retry, Fallback, Timeout.

Couvre:
- RetryPolicy avec différentes stratégies de backoff
- Fallback avec valeur et fonction
- Timeout
- ResilientCall (combinaison des patterns)
"""
import pytest
import asyncio
import time
from app.integration.cross_cutting.retry import (
    RetryPolicy, BackoffStrategy, Fallback, FallbackError,
    Timeout, TimeoutError, ResilientCall,
    retry_with_backoff, with_fallback, with_timeout
)


# ========== TESTS RETRY POLICY ==========

class TestRetryPolicy:
    """Tests de la politique de retry."""

    @pytest.mark.asyncio
    async def test_execute_success_no_retry(self):
        """Vérifie qu'une fonction réussie n'est pas retentée."""
        policy = RetryPolicy(max_retries=3)
        call_count = 0

        async def success_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = await policy.execute(success_func)

        assert result == "success"
        assert call_count == 1
        assert policy.stats.successful_attempts == 1
        assert policy.stats.total_retries == 0

    @pytest.mark.asyncio
    async def test_execute_with_retry_then_success(self):
        """Vérifie le retry puis succès."""
        policy = RetryPolicy(max_retries=3, initial_delay=0.01)
        call_count = 0

        async def fail_then_succeed():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "success"

        result = await policy.execute(fail_then_succeed)

        assert result == "success"
        assert call_count == 3
        assert policy.stats.total_retries == 2

    @pytest.mark.asyncio
    async def test_execute_exhausts_retries(self):
        """Vérifie l'échec après tous les retries."""
        policy = RetryPolicy(max_retries=2, initial_delay=0.01)

        async def always_fail():
            raise ValueError("Always fails")

        with pytest.raises(ValueError) as exc_info:
            await policy.execute(always_fail)

        assert "Always fails" in str(exc_info.value)
        assert policy.stats.failed_attempts == 1
        assert policy.stats.total_retries == 2

    @pytest.mark.asyncio
    async def test_sync_function_execution(self):
        """Vérifie l'exécution de fonctions synchrones."""
        policy = RetryPolicy(max_retries=1)

        def sync_func():
            return "sync result"

        result = await policy.execute(sync_func)

        assert result == "sync result"


# ========== TESTS BACKOFF STRATEGIES ==========

class TestBackoffStrategies:
    """Tests des stratégies de backoff."""

    def test_fixed_backoff(self):
        """Vérifie le backoff fixe."""
        policy = RetryPolicy(
            initial_delay=1.0,
            backoff_strategy=BackoffStrategy.FIXED
        )

        delay_0 = policy._calculate_delay(0)
        delay_1 = policy._calculate_delay(1)
        delay_5 = policy._calculate_delay(5)

        assert delay_0 == 1.0
        assert delay_1 == 1.0
        assert delay_5 == 1.0

    def test_linear_backoff(self):
        """Vérifie le backoff linéaire."""
        policy = RetryPolicy(
            initial_delay=1.0,
            backoff_strategy=BackoffStrategy.LINEAR
        )

        delay_0 = policy._calculate_delay(0)
        delay_1 = policy._calculate_delay(1)
        delay_2 = policy._calculate_delay(2)

        assert delay_0 == 1.0
        assert delay_1 == 2.0
        assert delay_2 == 3.0

    def test_exponential_backoff(self):
        """Vérifie le backoff exponentiel."""
        policy = RetryPolicy(
            initial_delay=1.0,
            backoff_strategy=BackoffStrategy.EXPONENTIAL
        )

        delay_0 = policy._calculate_delay(0)
        delay_1 = policy._calculate_delay(1)
        delay_2 = policy._calculate_delay(2)

        assert delay_0 == 1.0
        assert delay_1 == 2.0
        assert delay_2 == 4.0

    def test_max_delay_respected(self):
        """Vérifie que max_delay est respecté."""
        policy = RetryPolicy(
            initial_delay=1.0,
            max_delay=5.0,
            backoff_strategy=BackoffStrategy.EXPONENTIAL
        )

        delay_10 = policy._calculate_delay(10)  # Serait 1024 sans limite

        assert delay_10 == 5.0

    def test_jitter_adds_variation(self):
        """Vérifie que jitter ajoute de la variation."""
        policy = RetryPolicy(
            initial_delay=1.0,
            backoff_strategy=BackoffStrategy.JITTER,
            jitter_factor=0.5
        )

        delays = [policy._calculate_delay(1) for _ in range(10)]

        # Avec jitter, les délais devraient varier
        assert len(set(delays)) > 1


# ========== TESTS RETRY_ON FILTERING ==========

class TestRetryFiltering:
    """Tests du filtrage des exceptions à retry."""

    @pytest.mark.asyncio
    async def test_retry_on_specific_exception(self):
        """Vérifie le retry sur exception spécifique."""
        policy = RetryPolicy(
            max_retries=3,
            initial_delay=0.01,
            retry_on=(ValueError,)
        )
        call_count = 0

        async def fail_with_value_error():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Retryable")
            return "success"

        result = await policy.execute(fail_with_value_error)

        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_no_retry_on_excluded_exception(self):
        """Vérifie l'absence de retry sur exception exclue."""
        policy = RetryPolicy(
            max_retries=3,
            initial_delay=0.01,
            dont_retry_on=(RuntimeError,)
        )
        call_count = 0

        async def fail_with_runtime_error():
            nonlocal call_count
            call_count += 1
            raise RuntimeError("Not retryable")

        with pytest.raises(RuntimeError):
            await policy.execute(fail_with_runtime_error)

        assert call_count == 1  # Pas de retry


# ========== TESTS RETRY DECORATOR ==========

class TestRetryDecorator:
    """Tests du décorateur retry."""

    @pytest.mark.asyncio
    async def test_retry_decorator_async(self):
        """Vérifie le décorateur sur fonction async."""
        policy = RetryPolicy(max_retries=2, initial_delay=0.01)
        call_count = 0

        @policy.retry
        async def decorated_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Fail")
            return "decorated success"

        result = await decorated_func()

        assert result == "decorated success"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_retry_with_backoff_decorator(self):
        """Vérifie le décorateur retry_with_backoff."""
        call_count = 0

        @retry_with_backoff(max_retries=2, initial_delay=0.01)
        async def decorated():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Fail")
            return "success"

        result = await decorated()

        assert result == "success"


# ========== TESTS ON_RETRY CALLBACK ==========

class TestOnRetryCallback:
    """Tests du callback on_retry."""

    @pytest.mark.asyncio
    async def test_on_retry_called(self):
        """Vérifie que on_retry est appelé."""
        retry_calls = []

        def on_retry(attempt, error, delay):
            retry_calls.append((attempt, str(error), delay))

        policy = RetryPolicy(
            max_retries=2,
            initial_delay=0.01,
            on_retry=on_retry
        )
        call_count = 0

        async def fail_once():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Temporary")
            return "success"

        await policy.execute(fail_once)

        assert len(retry_calls) == 1
        assert retry_calls[0][0] == 1
        assert "Temporary" in retry_calls[0][1]


# ========== TESTS FALLBACK ==========

class TestFallback:
    """Tests du pattern Fallback."""

    @pytest.mark.asyncio
    async def test_fallback_value_on_failure(self):
        """Vérifie le fallback avec valeur."""
        fallback = Fallback(fallback_value={"default": True})

        async def failing_func():
            raise ValueError("Primary failed")

        result = await fallback.execute(failing_func)

        assert result == {"default": True}
        assert fallback.stats["fallback_calls"] == 1

    @pytest.mark.asyncio
    async def test_fallback_function_on_failure(self):
        """Vérifie le fallback avec fonction."""
        async def fallback_func():
            return "fallback result"

        fallback = Fallback(fallback_function=fallback_func)

        async def failing_func():
            raise ValueError("Primary failed")

        result = await fallback.execute(failing_func)

        assert result == "fallback result"

    @pytest.mark.asyncio
    async def test_primary_success_no_fallback(self):
        """Vérifie que le fallback n'est pas utilisé sur succès."""
        fallback = Fallback(fallback_value="default")

        async def success_func():
            return "primary"

        result = await fallback.execute(success_func)

        assert result == "primary"
        assert fallback.stats["fallback_calls"] == 0

    @pytest.mark.asyncio
    async def test_no_fallback_raises_error(self):
        """Vérifie l'erreur sans fallback disponible."""
        fallback = Fallback()

        async def failing_func():
            raise ValueError("Fail")

        with pytest.raises(FallbackError):
            await fallback.execute(failing_func)

    @pytest.mark.asyncio
    async def test_fallback_cache(self):
        """Vérifie le cache du fallback."""
        fallback = Fallback(fallback_value="default")
        fallback.set_cache("cached_value", duration=300)

        async def failing_func():
            raise ValueError("Fail")

        result = await fallback.execute(failing_func)

        assert result == "cached_value"
        assert fallback.stats["cache_hits"] == 1


# ========== TESTS FALLBACK DECORATOR ==========

class TestFallbackDecorator:
    """Tests du décorateur with_fallback."""

    @pytest.mark.asyncio
    async def test_with_fallback_decorator(self):
        """Vérifie le décorateur with_fallback."""
        @with_fallback(fallback_value="fallback")
        async def decorated():
            raise ValueError("Fail")

        result = await decorated()

        assert result == "fallback"


# ========== TESTS ON_FALLBACK CALLBACK ==========

class TestOnFallbackCallback:
    """Tests du callback on_fallback."""

    @pytest.mark.asyncio
    async def test_on_fallback_called(self):
        """Vérifie que on_fallback est appelé."""
        errors = []

        def on_fallback(error):
            errors.append(str(error))

        fallback = Fallback(
            fallback_value="default",
            on_fallback=on_fallback
        )

        async def failing_func():
            raise ValueError("Primary error")

        await fallback.execute(failing_func)

        assert len(errors) == 1
        assert "Primary error" in errors[0]


# ========== TESTS TIMEOUT ==========

class TestTimeout:
    """Tests du pattern Timeout."""

    @pytest.mark.asyncio
    async def test_timeout_success(self):
        """Vérifie le succès dans le délai."""
        timeout = Timeout(seconds=1.0)

        async def fast_func():
            await asyncio.sleep(0.01)
            return "fast"

        result = await timeout.execute(fast_func)

        assert result == "fast"
        assert timeout.stats["completed_calls"] == 1

    @pytest.mark.asyncio
    async def test_timeout_exceeded(self):
        """Vérifie le timeout dépassé."""
        timeout = Timeout(seconds=0.05)

        async def slow_func():
            await asyncio.sleep(1.0)
            return "slow"

        with pytest.raises(TimeoutError) as exc_info:
            await timeout.execute(slow_func)

        assert "timed out" in str(exc_info.value)
        assert timeout.stats["timeout_calls"] == 1

    @pytest.mark.asyncio
    async def test_timeout_requires_async(self):
        """Vérifie que Timeout requiert une fonction async."""
        timeout = Timeout(seconds=1.0)

        def sync_func():
            return "sync"

        with pytest.raises(ValueError) as exc_info:
            await timeout.execute(sync_func)

        assert "async function" in str(exc_info.value)


# ========== TESTS TIMEOUT DECORATOR ==========

class TestTimeoutDecorator:
    """Tests du décorateur with_timeout."""

    @pytest.mark.asyncio
    async def test_with_timeout_decorator(self):
        """Vérifie le décorateur with_timeout."""
        @with_timeout(seconds=1.0)
        async def decorated():
            return "quick"

        result = await decorated()

        assert result == "quick"

    @pytest.mark.asyncio
    async def test_with_timeout_decorator_timeout(self):
        """Vérifie le timeout du décorateur."""
        @with_timeout(seconds=0.05)
        async def slow_decorated():
            await asyncio.sleep(1.0)
            return "slow"

        with pytest.raises(TimeoutError):
            await slow_decorated()


# ========== TESTS ON_TIMEOUT CALLBACK ==========

class TestOnTimeoutCallback:
    """Tests du callback on_timeout."""

    @pytest.mark.asyncio
    async def test_on_timeout_called(self):
        """Vérifie que on_timeout est appelé."""
        timeouts = []

        def on_timeout(duration):
            timeouts.append(duration)

        timeout = Timeout(seconds=0.05, on_timeout=on_timeout)

        async def slow_func():
            await asyncio.sleep(1.0)

        with pytest.raises(TimeoutError):
            await timeout.execute(slow_func)

        assert len(timeouts) == 1
        assert timeouts[0] == 0.05


# ========== TESTS RESILIENT CALL ==========

class TestResilientCall:
    """Tests de ResilientCall (combinaison des patterns)."""

    @pytest.mark.asyncio
    async def test_resilient_call_success(self):
        """Vérifie le succès avec ResilientCall."""
        resilient = ResilientCall(
            timeout=1.0,
            max_retries=3,
            fallback_value="fallback"
        )

        async def success_func():
            return "success"

        result = await resilient.execute(success_func)

        assert result == "success"

    @pytest.mark.asyncio
    async def test_resilient_call_retry_then_success(self):
        """Vérifie retry puis succès avec ResilientCall."""
        resilient = ResilientCall(
            timeout=1.0,
            max_retries=3,
            initial_delay=0.01,
            fallback_value="fallback"
        )
        call_count = 0

        async def fail_then_succeed():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Temporary")
            return "success"

        result = await resilient.execute(fail_then_succeed)

        assert result == "success"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_resilient_call_fallback(self):
        """Vérifie le fallback avec ResilientCall."""
        resilient = ResilientCall(
            timeout=1.0,
            max_retries=1,
            initial_delay=0.01,
            fallback_value={"fallback": True}
        )

        async def always_fail():
            raise ValueError("Always fails")

        result = await resilient.execute(always_fail)

        assert result == {"fallback": True}

    @pytest.mark.asyncio
    async def test_resilient_call_timeout_triggers_retry(self):
        """Vérifie que timeout déclenche retry."""
        resilient = ResilientCall(
            timeout=0.05,
            max_retries=2,
            initial_delay=0.01,
            fallback_value="fallback"
        )
        call_count = 0

        async def slow_then_fast():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                await asyncio.sleep(1.0)
            return "fast"

        result = await resilient.execute(slow_then_fast)

        # Devrait avoir retry après timeout
        assert call_count >= 2


# ========== TESTS RESILIENT CALL DECORATOR ==========

class TestResilientCallDecorator:
    """Tests du décorateur wrap de ResilientCall."""

    @pytest.mark.asyncio
    async def test_wrap_decorator(self):
        """Vérifie le décorateur wrap."""
        resilient = ResilientCall(
            timeout=1.0,
            max_retries=1,
            fallback_value="fallback"
        )

        @resilient.wrap
        async def decorated():
            return "wrapped"

        result = await decorated()

        assert result == "wrapped"


# ========== TESTS GET_STATS ==========

class TestGetStats:
    """Tests de récupération des statistiques."""

    @pytest.mark.asyncio
    async def test_retry_policy_get_stats(self):
        """Vérifie les stats de RetryPolicy."""
        policy = RetryPolicy(max_retries=2, initial_delay=0.01)

        async def success():
            return "ok"

        await policy.execute(success)

        stats = policy.get_stats()

        assert stats["total_attempts"] == 1
        assert stats["successful_attempts"] == 1
        assert stats["config"]["max_retries"] == 2

    @pytest.mark.asyncio
    async def test_resilient_call_get_stats(self):
        """Vérifie les stats combinées de ResilientCall."""
        resilient = ResilientCall(
            timeout=1.0,
            max_retries=1,
            fallback_value="default"
        )

        async def success():
            return "ok"

        await resilient.execute(success)

        stats = resilient.get_stats()

        assert "timeout" in stats
        assert "retry" in stats
        assert "fallback" in stats


# ========== TESTS RESET STATS ==========

class TestResetStats:
    """Tests de réinitialisation des statistiques."""

    @pytest.mark.asyncio
    async def test_retry_policy_reset_stats(self):
        """Vérifie reset_stats de RetryPolicy."""
        policy = RetryPolicy()

        async def success():
            return "ok"

        await policy.execute(success)
        assert policy.stats.total_attempts > 0

        policy.reset_stats()

        assert policy.stats.total_attempts == 0
        assert policy.stats.successful_attempts == 0
