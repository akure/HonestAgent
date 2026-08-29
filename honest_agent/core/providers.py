from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass, field
from typing import Any, Protocol

import httpx

from honest_agent.core.evaluator import ContextTelemetry
from honest_agent.schemas.models import EvaluationRequest, RecommendedAction, RiskLevel, VerifierResult, VerifierTier


class ProviderError(RuntimeError):
    pass


class ProviderTimeout(ProviderError):
    pass


class ProviderUnavailable(ProviderError):
    pass


class ProviderContractError(ProviderError):
    pass


class ProviderDisagreement(ProviderError):
    pass


class VerifierProvider(Protocol):
    async def verify(self, request: EvaluationRequest, telemetry: ContextTelemetry, tier: VerifierTier) -> VerifierResult:
        ...


class OpenAICompatibleVerifierProvider:
    """Live verifier adapter with explicit transport and contract failures."""

    def __init__(self, endpoint: str, api_key: str, model: str, client: httpx.AsyncClient | None = None):
        self.endpoint = endpoint
        self.api_key = api_key
        self.model = model
        self.client = client or httpx.AsyncClient(timeout=5.0)

    async def verify(self, request: EvaluationRequest, telemetry: ContextTelemetry, tier: VerifierTier) -> VerifierResult:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "Return JSON only with confidence_score, has_sufficient_context, hallucination_risk, reasoning, recommended_action."},
                {"role": "user", "content": json.dumps({"context": request.context, "thought": request.thought, "tool_name": request.tool_name, "tool_input": request.tool_input, "context_ratio": telemetry.ratio})},
            ],
            "temperature": 0,
            "response_format": {"type": "json_object"},
        }
        try:
            response = await self.client.post(self.endpoint, headers={"Authorization": f"Bearer {self.api_key}"}, json=payload)
            response.raise_for_status()
            body = response.json()
        except httpx.TimeoutException as exc:
            raise ProviderTimeout("provider request timed out") from exc
        except httpx.HTTPError as exc:
            raise ProviderUnavailable("provider request failed") from exc
        except ValueError as exc:
            raise ProviderContractError("provider returned invalid JSON") from exc
        try:
            content: Any = body["choices"][0]["message"]["content"]
            parsed = json.loads(content) if isinstance(content, str) else content
            return VerifierResult(**parsed, verifier_tier=tier)
        except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise ProviderContractError("provider returned an invalid verifier response") from exc


@dataclass
class ProviderMetrics:
    attempts: int = 0
    successes: int = 0
    failures: int = 0
    latencies_ms: list[float] = field(default_factory=list)

    def snapshot(self) -> dict[str, Any]:
        ordered = sorted(self.latencies_ms)
        p95_index = max(0, min(len(ordered) - 1, int(len(ordered) * 0.95) - 1)) if ordered else 0
        return {
            "attempts": self.attempts,
            "successes": self.successes,
            "failures": self.failures,
            "latency_ms": {"count": len(ordered), "p50": ordered[len(ordered) // 2] if ordered else None, "p95": ordered[p95_index] if ordered else None},
        }


class ObservedVerifierProvider:
    """Measures provider attempts without logging payloads or secret material."""

    def __init__(self, provider: VerifierProvider, metrics: ProviderMetrics | None = None):
        self.provider = provider
        self.metrics = metrics or ProviderMetrics()

    async def verify(self, request: EvaluationRequest, telemetry: ContextTelemetry, tier: VerifierTier) -> VerifierResult:
        started = time.perf_counter()
        self.metrics.attempts += 1
        try:
            result = await self.provider.verify(request, telemetry, tier)
            self.metrics.successes += 1
            return result
        except BaseException:
            self.metrics.failures += 1
            raise
        finally:
            self.metrics.latencies_ms.append((time.perf_counter() - started) * 1000)


class ResilientVerifierProvider:
    """Bounded retry and optional independent comparison for live providers."""

    def __init__(self, primary: VerifierProvider, secondary: VerifierProvider | None = None, max_retries: int = 1, retry_delay_seconds: float = 0.0):
        self.primary = primary
        self.secondary = secondary
        self.max_retries = max(0, max_retries)
        self.retry_delay_seconds = max(0.0, retry_delay_seconds)

    async def _call_with_retry(self, provider: VerifierProvider, request: EvaluationRequest, telemetry: ContextTelemetry, tier: VerifierTier) -> VerifierResult:
        attempts = 0
        while True:
            try:
                return await provider.verify(request, telemetry, tier)
            except (ProviderTimeout, ProviderUnavailable):
                if attempts >= self.max_retries:
                    raise
                attempts += 1
                if self.retry_delay_seconds:
                    await asyncio.sleep(self.retry_delay_seconds)
            except asyncio.CancelledError:
                raise

    async def verify(self, request: EvaluationRequest, telemetry: ContextTelemetry, tier: VerifierTier) -> VerifierResult:
        primary = await self._call_with_retry(self.primary, request, telemetry, tier)
        if self.secondary is None:
            return primary
        secondary = await self._call_with_retry(self.secondary, request, telemetry, tier)
        if primary.recommended_action != secondary.recommended_action or primary.hallucination_risk != secondary.hallucination_risk or abs(primary.confidence_score - secondary.confidence_score) > 0.10:
            raise ProviderDisagreement("verifier providers disagreed; failing closed")
        return primary
