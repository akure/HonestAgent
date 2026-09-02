import asyncio

import pytest

from honest_agent.adapters import PINNED_SUPPORT, UnsupportedFrameworkVersion, VersionPinnedFrameworkAdapter
from honest_agent.core.guardrail import HonestGuard
from honest_agent.schemas.models import Config, DecisionStatus, EvaluationRequest


def adapter(tmp_path):
    guard = HonestGuard(Config(trajectory_dir=str(tmp_path / "traces"), checkpoint_path=str(tmp_path / "checkpoints.json")))
    return VersionPinnedFrameworkAdapter(guard, PINNED_SUPPORT["langgraph"])


def test_pinned_graph_support_and_unsupported_version_fail_closed(tmp_path):
    pinned = adapter(tmp_path)
    assert pinned.support.version == "0.2.53"
    with pytest.raises(UnsupportedFrameworkVersion):
        VersionPinnedFrameworkAdapter(pinned.guard, type(pinned.support)("langgraph", "0.0.0", "graph", ()))


def test_framework_native_pause_resume_and_handoff_boundary(tmp_path):
    integration = adapter(tmp_path)
    calls = []
    request = EvaluationRequest(tool_name="send_email", irreversible=True, context="synthetic approved context", tool_input={"to": "synthetic@example.invalid"})
    paused = asyncio.run(integration.invoke_versioned(request, lambda payload: calls.append(payload)))
    assert paused.status == DecisionStatus.PAUSED.value
    resumed = asyncio.run(integration.resume(paused.decision.trajectory_id, "synthetic-reviewer", request, lambda payload: calls.append(payload) or {"sent": False}))
    assert resumed.status == DecisionStatus.PROCEED.value
    assert resumed.executed is True
    assert calls == [{"to": "synthetic@example.invalid"}]


def test_cancelled_framework_state_cannot_reach_tool(tmp_path):
    integration = adapter(tmp_path)
    calls = []
    request = EvaluationRequest(tool_name="lookup_customer", context="synthetic customer exists", tool_input={"id": "synthetic"}, metadata={"trajectory_id": "framework-run-1"})
    integration.cancel("framework-run-1")
    result = asyncio.run(integration.invoke_versioned(request, lambda payload: calls.append(payload)))
    assert result.status == DecisionStatus.REJECTED.value
    assert result.executed is False
    assert calls == []
