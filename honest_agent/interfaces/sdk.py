from __future__ import annotations

import asyncio
import inspect
from functools import wraps
from typing import Any, Callable, ParamSpec, TypeVar

from honest_agent.core.guardrail import HonestGuard
from honest_agent.schemas.models import Config, EvaluationRequest, DecisionStatus

P = ParamSpec("P")
R = TypeVar("R")


class GuardrailPaused(RuntimeError):
    def __init__(self, decision):
        super().__init__(f"Action paused: {decision.trajectory_id}")
        self.decision = decision


def guard(confidence_threshold: float = 0.85, tool_name: str | None = None, irreversible: bool = False):
    runtime_guard = HonestGuard(Config(confidence_threshold=confidence_threshold))

    def decorator(fn: Callable[P, R]) -> Callable[P, R]:
        if inspect.iscoroutinefunction(fn):
            @wraps(fn)
            async def async_wrapper(*args: P.args, **kwargs: P.kwargs):
                request = EvaluationRequest(tool_name=tool_name or fn.__name__, tool_input={"args": list(args), "kwargs": kwargs}, context=str(kwargs.get("context", "")), thought=str(kwargs.get("thought", "")), irreversible=irreversible)
                decision = await runtime_guard.evaluate(request)
                if decision.status != DecisionStatus.PROCEED:
                    raise GuardrailPaused(decision)
                return await fn(*args, **kwargs)
            return async_wrapper  # type: ignore[return-value]

        @wraps(fn)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs):
            request = EvaluationRequest(tool_name=tool_name or fn.__name__, tool_input={"args": list(args), "kwargs": kwargs}, context=str(kwargs.get("context", "")), thought=str(kwargs.get("thought", "")), irreversible=irreversible)
            decision = asyncio.run(runtime_guard.evaluate(request))
            if decision.status != DecisionStatus.PROCEED:
                raise GuardrailPaused(decision)
            return fn(*args, **kwargs)
        return sync_wrapper  # type: ignore[return-value]

    return decorator
