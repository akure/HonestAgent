from __future__ import annotations

from dataclasses import dataclass
import inspect
from typing import Any, Awaitable, Callable, Mapping

from honest_agent.adapters.contract import AdapterResult, GuardedFrameworkTool
from honest_agent.schemas.models import DecisionStatus, EvaluationRequest


class UnsupportedFrameworkVersion(ValueError):
    pass


@dataclass(frozen=True)
class FrameworkSupport:
    framework: str
    version: str
    integration_kind: str
    supported_operations: tuple[str, ...]


PINNED_SUPPORT = {
    "langgraph": FrameworkSupport("langgraph", "0.2.53", "graph", ("proceed", "pause", "reject", "failure", "cancel", "resume", "state")),
    "rag-reference": FrameworkSupport("rag-reference", "std3", "rag", ("proceed", "pause", "reject", "failure", "stale", "injection", "cancel", "handoff")),
}


class VersionPinnedFrameworkAdapter(GuardedFrameworkTool):
    """Framework-neutral lifecycle adapter with an explicit support/version boundary."""

    def __init__(self, guard, support: FrameworkSupport):
        if support.framework not in PINNED_SUPPORT or PINNED_SUPPORT[support.framework] != support:
            raise UnsupportedFrameworkVersion(f"unsupported framework/version: {support.framework}@{support.version}")
        super().__init__(guard, support.framework)
        self.support = support
        self._cancelled: set[str] = set()

    async def invoke_versioned(self, request: EvaluationRequest, tool: Callable[[Mapping[str, Any]], Any | Awaitable[Any]], *, evidence: Mapping[str, Any] | None = None) -> AdapterResult:
        trajectory_id = str(request.metadata.get("trajectory_id", ""))
        if trajectory_id in self._cancelled:
            decision = await self.guard.evaluate(request)
            return AdapterResult(DecisionStatus.REJECTED.value, False, decision, error="framework action was cancelled")
        return await self.invoke(request, tool, evidence=evidence)

    def cancel(self, trajectory_id: str) -> None:
        if not trajectory_id.strip():
            raise ValueError("trajectory id is required")
        self._cancelled.add(trajectory_id)

    async def resume(self, trajectory_id: str, reviewer: str, request: EvaluationRequest, tool: Callable[[Mapping[str, Any]], Any | Awaitable[Any]], *, evidence: Mapping[str, Any] | None = None) -> AdapterResult:
        if trajectory_id in self._cancelled:
            return await self.invoke_versioned(request, tool, evidence=evidence)
        decision = await self.guard.approve(trajectory_id, reviewer)
        if decision.status != DecisionStatus.PROCEED:
            return AdapterResult(decision.status.value, False, decision)
        metadata = dict(request.metadata)
        if evidence is not None:
            metadata["evidence"] = dict(evidence)
        guarded_request = request.model_copy(update={"metadata": metadata})
        if not decision.handoff_token or not self.guard.validate_handoff(decision.handoff_token, guarded_request, trajectory_id):
            return AdapterResult(DecisionStatus.REJECTED.value, False, decision, error="handoff validation failed")
        try:
            result = tool(guarded_request.tool_input)
            if inspect.isawaitable(result):
                result = await result
        except Exception as exc:
            return AdapterResult("PROVIDER_FAILURE", False, decision, error=type(exc).__name__)
        return AdapterResult(DecisionStatus.PROCEED.value, True, decision, result=result)


__all__ = ["FrameworkSupport", "PINNED_SUPPORT", "UnsupportedFrameworkVersion", "VersionPinnedFrameworkAdapter"]
