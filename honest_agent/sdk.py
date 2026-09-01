from __future__ import annotations

import functools
from collections.abc import Awaitable, Callable, Mapping
from typing import Any, ParamSpec, TypeVar

from honest_agent.adapters.contract import AdapterResult, GuardedFrameworkTool
from honest_agent.core.guardrail import HonestGuard
from honest_agent.schemas.models import DecisionStatus, EvaluationRequest, GuardDecision

P = ParamSpec("P")
R = TypeVar("R")


class GuardBlocked(RuntimeError):
    """Raised by the decorator when the guard does not authorize execution."""

    def __init__(self, decision: GuardDecision):
        self.decision = decision
        super().__init__(f"tool call {decision.status.value}: {decision.reasoning}")


def make_request(tool_name: str, tool_input: Mapping[str, Any] | None = None, *, context: str = "", agent_id: str = "sdk-agent", irreversible: bool = False, metadata: Mapping[str, Any] | None = None) -> EvaluationRequest:
    """Build the canonical legacy request consumed by HonestGuard."""
    return EvaluationRequest(
        agent_id=agent_id,
        context=context,
        tool_name=tool_name,
        tool_input=dict(tool_input or {}),
        irreversible=irreversible,
        metadata=dict(metadata or {}),
    )


class HonestAgent:
    """Small adoption facade; all authorization remains in HonestGuard."""

    def __init__(self, guard: HonestGuard | None = None):
        self.guard = guard or HonestGuard()

    async def check(self, request: EvaluationRequest) -> GuardDecision:
        return await self.guard.evaluate(request)

    async def invoke(self, request: EvaluationRequest, tool: Callable[[Mapping[str, Any]], Any | Awaitable[Any]], *, evidence: Mapping[str, Any] | None = None) -> AdapterResult:
        adapter = GuardedFrameworkTool(self.guard, framework_name="python-sdk")
        return await adapter.invoke(request, tool, evidence=evidence)

    def protect(self, tool_name: str, *, context: str = "", agent_id: str = "sdk-agent", irreversible: bool = False, metadata: Mapping[str, Any] | None = None) -> Callable[[Callable[P, R | Awaitable[R]]], Callable[P, Awaitable[R]]]:
        """Decorate an async or sync tool; the returned callable is always async."""
        def decorator(tool: Callable[P, R | Awaitable[R]]) -> Callable[P, Awaitable[R]]:
            @functools.wraps(tool)
            async def guarded(*args: P.args, **kwargs: P.kwargs) -> R:
                request = make_request(tool_name, kwargs, context=context, agent_id=agent_id, irreversible=irreversible, metadata=metadata)
                result = await self.invoke(request, lambda _payload: tool(*args, **kwargs))
                if result.status != DecisionStatus.PROCEED.value or not result.executed:
                    raise GuardBlocked(result.decision)
                return result.result

            return guarded
        return decorator


__all__ = ["GuardBlocked", "HonestAgent", "make_request"]
