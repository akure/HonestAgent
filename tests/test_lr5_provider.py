import asyncio
import json

import httpx
import pytest

from honest_agent.core.evaluator import ContextEvaluator
from honest_agent.core.providers import (
    OpenAICompatibleVerifierProvider,
    ProviderContractError,
    ProviderDisagreement,
    ProviderTimeout,
    ResilientVerifierProvider,
    ObservedVerifierProvider,
    ProviderMetrics,
)
from honest_agent.schemas.models import EvaluationRequest, RiskLevel, RecommendedAction, VerifierResult, VerifierTier


REQUEST = EvaluationRequest(context="known", tool_name="lookup", tool_input={"id": 1})
TELEMETRY = ContextEvaluator().evaluate(REQUEST.context, REQUEST.max_context_tokens, 0.8)


def _result(score=0.9):
    return VerifierResult(confidence_score=score, has_sufficient_context=True, hallucination_risk=RiskLevel.LOW, reasoning="ok", recommended_action=RecommendedAction.PROCEED, verifier_tier=VerifierTier.FAST)


class FlakyProvider:
    def __init__(self, failures=1):
        self.failures = failures
        self.calls = 0

    async def verify(self, request, telemetry, tier):
        self.calls += 1
        if self.calls <= self.failures:
            raise ProviderTimeout("timeout")
        return _result()


class StaticProvider:
    def __init__(self, result):
        self.result = result

    async def verify(self, request, telemetry, tier):
        return self.result


def test_transient_timeout_is_retried_with_bounded_attempts():
    provider = FlakyProvider(failures=1)
    result = asyncio.run(ResilientVerifierProvider(provider, max_retries=1).verify(REQUEST, TELEMETRY, VerifierTier.FAST))
    assert result.confidence_score == 0.9
    assert provider.calls == 2


def test_repeated_timeout_fails_after_retry_budget():
    provider = FlakyProvider(failures=5)
    with pytest.raises(ProviderTimeout):
        asyncio.run(ResilientVerifierProvider(provider, max_retries=1).verify(REQUEST, TELEMETRY, VerifierTier.FAST))
    assert provider.calls == 2


def test_provider_disagreement_fails_closed():
    primary = StaticProvider(_result(0.95))
    secondary = StaticProvider(_result(0.70))
    with pytest.raises(ProviderDisagreement):
        asyncio.run(ResilientVerifierProvider(primary, secondary).verify(REQUEST, TELEMETRY, VerifierTier.FAST))


def test_cancellation_is_not_retried_or_swallowed():
    class CancelledProvider:
        calls = 0
        async def verify(self, request, telemetry, tier):
            self.calls += 1
            raise asyncio.CancelledError()
    provider = CancelledProvider()
    with pytest.raises(asyncio.CancelledError):
        asyncio.run(ResilientVerifierProvider(provider, max_retries=3).verify(REQUEST, TELEMETRY, VerifierTier.FAST))
    assert provider.calls == 1


def test_observed_provider_records_latency_and_outcomes():
    metrics = ProviderMetrics()
    observed = ObservedVerifierProvider(StaticProvider(_result()), metrics)
    asyncio.run(observed.verify(REQUEST, TELEMETRY, VerifierTier.FAST))
    snapshot = metrics.snapshot()
    assert snapshot["attempts"] == 1
    assert snapshot["successes"] == 1
    assert snapshot["failures"] == 0
    assert snapshot["latency_ms"]["count"] == 1


def test_live_adapter_maps_timeout_and_malformed_contract():
    async def run():
        async def timeout_handler(request):
            raise httpx.ReadTimeout("timeout", request=request)
        timeout_client = httpx.AsyncClient(transport=httpx.MockTransport(timeout_handler))
        with pytest.raises(ProviderTimeout):
            await OpenAICompatibleVerifierProvider("https://provider.test", "key", "model", timeout_client).verify(REQUEST, TELEMETRY, VerifierTier.FAST)
        await timeout_client.aclose()

        async def malformed_handler(request):
            return httpx.Response(200, json={"choices": []})
        malformed_client = httpx.AsyncClient(transport=httpx.MockTransport(malformed_handler))
        with pytest.raises(ProviderContractError):
            await OpenAICompatibleVerifierProvider("https://provider.test", "key", "model", malformed_client).verify(REQUEST, TELEMETRY, VerifierTier.FAST)
        await malformed_client.aclose()
    asyncio.run(run())
