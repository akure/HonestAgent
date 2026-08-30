import asyncio

import pytest

from honest_agent.core.guardrail import HonestGuard
from honest_agent.schemas.models import Config, DecisionStatus, EvaluationRequest
from examples.autogen.adapter import AutoGenFunctionTool
from examples.crewai.adapter import CrewAIToolBoundary
from examples.langchain.adapter import LangChainToolWrapper
from examples.langgraph.adapter import LangGraphGuardNode
from examples.llamaindex.adapter import LlamaIndexWorkflowGuard

ADAPTERS = [
    AutoGenFunctionTool,
    CrewAIToolBoundary,
    LangChainToolWrapper,
    LangGraphGuardNode,
    LlamaIndexWorkflowGuard,
]


def make_guard(tmp_path):
    return HonestGuard(Config(trajectory_dir=str(tmp_path / "traces"), checkpoint_path=str(tmp_path / "checkpoints.json")))


@pytest.mark.parametrize("adapter_class", ADAPTERS)
def test_each_adapter_executes_only_after_valid_handoff(adapter_class, tmp_path):
    calls = []
    adapter = adapter_class(make_guard(tmp_path))
    request = EvaluationRequest(tool_name="lookup_customer", context="customer record exists", tool_input={"id": "synthetic"})
    result = asyncio.run(adapter.call(request, lambda payload: calls.append(payload) or {"ok": True}))
    assert result.status == DecisionStatus.PROCEED.value
    assert result.executed is True
    assert result.result == {"ok": True}
    assert len(calls) == 1


@pytest.mark.parametrize("adapter_class", ADAPTERS)
def test_each_adapter_blocks_pause_reject_and_provider_failure(adapter_class, tmp_path):
    calls = []
    adapter = adapter_class(make_guard(tmp_path))
    paused = EvaluationRequest(tool_name="send_email", irreversible=True, context="approved context", tool_input={"to": "synthetic"})
    paused_result = asyncio.run(adapter.call(paused, lambda payload: calls.append(payload)))
    assert paused_result.status == DecisionStatus.PAUSED.value
    assert paused_result.executed is False
    rejected = EvaluationRequest(tool_name="", context="approved context")
    rejected_result = asyncio.run(adapter.call(rejected, lambda payload: calls.append(payload)))
    assert rejected_result.status == DecisionStatus.REJECTED.value
    assert rejected_result.executed is False

    def failing_tool(_payload):
        raise TimeoutError("synthetic provider timeout")

    failed = asyncio.run(adapter.call(EvaluationRequest(tool_name="lookup_customer", context="customer record exists"), failing_tool))
    assert failed.status == "PROVIDER_FAILURE"
    assert failed.executed is False
    assert failed.error == "TimeoutError"
    assert calls == []


@pytest.mark.parametrize("adapter_class", ADAPTERS)
def test_altered_arguments_cannot_reuse_handoff(adapter_class, tmp_path):
    guard = make_guard(tmp_path)
    adapter = adapter_class(guard)
    request = EvaluationRequest(tool_name="lookup_customer", context="customer record exists", tool_input={"id": "one"})
    decision = asyncio.run(guard.evaluate(request))
    altered = request.model_copy(update={"tool_input": {"id": "two"}})
    assert decision.handoff_token
    assert guard.validate_handoff(decision.handoff_token, altered, decision.trajectory_id) is False
