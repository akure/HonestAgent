from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Mapping

from honest_agent.core.guardrail import HonestGuard
from honest_agent.schemas.models import DecisionStatus, EvaluationRequest, GuardDecision


@dataclass(frozen=True)
class AdapterResult:
    status: str
    executed: bool
    decision: GuardDecision
    result: Any = None
    error: str | None = None


class GuardedFrameworkTool:
    """Framework-neutral pre-execution boundary; framework wrappers must delegate here."""

    def __init__(self, guard: HonestGuard, framework_name: str):
        self.guard = guard
        self.framework_name = framework_name

    async def invoke(
        self,
        request: EvaluationRequest,
        tool: Callable[[Mapping[str, Any]], Any | Awaitable[Any]],
        *,
        evidence: Mapping[str, Any] | None = None,
    ) -> AdapterResult:
        metadata = dict(request.metadata)
        if evidence is not None:
            metadata["evidence"] = dict(evidence)
        guarded_request = request.model_copy(update={"metadata": metadata})
        decision = await self.guard.evaluate(guarded_request)
        if decision.status != DecisionStatus.PROCEED:
            return AdapterResult(status=decision.status.value, executed=False, decision=decision)
        if not decision.handoff_token or not self.guard.validate_handoff(decision.handoff_token, guarded_request, decision.trajectory_id):
            return AdapterResult(status=DecisionStatus.REJECTED.value, executed=False, decision=decision, error="handoff validation failed")
        try:
            result = tool(guarded_request.tool_input)
            if inspect.isawaitable(result):
                result = await result
        except Exception as exc:
            return AdapterResult(status="PROVIDER_FAILURE", executed=False, decision=decision, error=type(exc).__name__)
        return AdapterResult(status=DecisionStatus.PROCEED.value, executed=True, decision=decision, result=result)
