from __future__ import annotations

from typing import Any, Mapping

from honest_agent.core.guardrail import HonestGuard
from honest_agent.interfaces.upstream import UpstreamClient
from honest_agent.schemas.models import EvaluationRequest


class ExecutionBlocked(RuntimeError):
    """Raised when an executor cannot prove an authorized guard decision."""


class ExecutorGateway:
    """The final deterministic boundary before an external side effect."""

    def __init__(self, guard: HonestGuard, upstream: UpstreamClient):
        self.guard = guard
        self.upstream = upstream

    async def execute(
        self,
        request: EvaluationRequest,
        handoff_token: str | None,
        trajectory_id: str,
        upstream_payload: Mapping[str, Any],
    ) -> dict[str, Any]:
        if not handoff_token or not self.guard.validate_handoff(handoff_token, request, trajectory_id):
            raise ExecutionBlocked("execution requires a valid request-bound handoff")
        if not self.upstream.enabled:
            return {
                "id": trajectory_id,
                "object": "honest_agent.simulated_execution",
                "choices": [],
            }
        return await self.upstream.chat_completions(upstream_payload)
