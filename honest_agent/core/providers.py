from __future__ import annotations

import json
from typing import Any

import httpx

from honest_agent.core.evaluator import ContextTelemetry
from honest_agent.schemas.models import EvaluationRequest, RecommendedAction, RiskLevel, VerifierResult, VerifierTier


class ProviderContractError(RuntimeError):
    pass


class OpenAICompatibleVerifierProvider:
    """Optional live verifier adapter; tests inject httpx.MockTransport."""

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
        response = await self.client.post(self.endpoint, headers={"Authorization": f"Bearer {self.api_key}"}, json=payload)
        response.raise_for_status()
        body = response.json()
        try:
            content: Any = body["choices"][0]["message"]["content"]
            parsed = json.loads(content) if isinstance(content, str) else content
            return VerifierResult(**parsed, verifier_tier=tier)
        except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise ProviderContractError("provider returned an invalid verifier response") from exc
