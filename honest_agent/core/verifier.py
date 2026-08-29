from __future__ import annotations

import re
from typing import Any, Protocol

from honest_agent.core.evaluator import ContextTelemetry
from honest_agent.schemas.models import (
    EvaluationRequest,
    RecommendedAction,
    RiskLevel,
    VerifierResult,
    VerifierTier,
)


class VerifierProvider(Protocol):
    async def verify(self, request: EvaluationRequest, telemetry: ContextTelemetry, tier: VerifierTier) -> VerifierResult:
        ...


IRREVERSIBLE_HINTS = {
    "write", "delete", "drop", "migrate", "send", "publish", "execute", "run", "transfer", "charge"
}
AMBIGUITY_HINTS = {"unknown", "missing", "ambiguous", "guess", "maybe", "unsupported", "contradictory"}


class DeterministicMockVerifier:
    """Offline verifier used for demos and evaluation; providers can replace it in production."""

    async def verify(self, request: EvaluationRequest, telemetry: ContextTelemetry, tier: VerifierTier) -> VerifierResult:
        tool_text = f"{request.tool_name} {request.tool_input}".lower()
        context_text = f"{request.context} {request.thought}".lower()
        tool_tokens = set(re.findall(r"[a-z0-9]+", request.tool_name.lower()))
        reasons: list[str] = []
        score = 0.96

        if not request.tool_name:
            score -= 0.30
            reasons.append("tool name is missing")
        if any(hint in context_text or hint in tool_text for hint in AMBIGUITY_HINTS):
            score -= 0.28
            reasons.append("request contains an ambiguity or unsupported dependency")
        if telemetry.near_capacity:
            score -= 0.16
            reasons.append("context is near capacity")
        if request.irreversible or bool(tool_tokens & IRREVERSIBLE_HINTS):
            score -= 0.12
            reasons.append("action has irreversible or external side effects")
        if not request.context.strip():
            score -= 0.25
            reasons.append("grounding context is empty")

        score = max(0.0, min(1.0, score))
        high_risk = score < 0.65 or request.irreversible
        medium_risk = score < 0.85 or telemetry.near_capacity
        risk = RiskLevel.HIGH if high_risk else RiskLevel.MEDIUM if medium_risk else RiskLevel.LOW
        recommendation = RecommendedAction.PROCEED if score >= 0.85 and not request.irreversible else RecommendedAction.REQUIRE_HUMAN_CHECKPOINT
        if score < 0.65 and not request.irreversible:
            recommendation = RecommendedAction.SUMMARIZE_CONTEXT
        reasoning = "; ".join(reasons) if reasons else "structured action is grounded and low risk"
        return VerifierResult(
            confidence_score=score,
            has_sufficient_context=bool(request.context.strip()) and not telemetry.near_capacity,
            hallucination_risk=risk,
            reasoning=reasoning,
            recommended_action=recommendation,
            verifier_tier=tier,
        )


class VerifierEngine:
    def __init__(self, provider: VerifierProvider | None = None):
        self.provider = provider or DeterministicMockVerifier()

    async def verify(self, request: EvaluationRequest, telemetry: ContextTelemetry, tier: VerifierTier) -> VerifierResult:
        return await self.provider.verify(request, telemetry, tier)
