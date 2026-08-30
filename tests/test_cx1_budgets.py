import asyncio
import multiprocessing
import time

import pytest

from honest_agent.core.budgets import BudgetExceeded, DurableWorkflowStore, WorkflowCancelled
from honest_agent.schemas.workflow import WorkflowBudgets, WorkflowRunContext


def _context(deadline=None, tool_calls=2):
    return WorkflowRunContext(run_id="run-cx1", tenant_id="tenant-a", root_agent_id="agent", step_id="step-1", workflow_version="wf-v1", deadline=deadline or time.time() + 60, policy_snapshot_id="policy-v1", budgets=WorkflowBudgets(tool_calls=tool_calls, verifier_calls=2, retries=1, tokens=1000, fan_out=2, concurrency=1, cumulative_amount=10))


def _reserve(path, queue):
    store = DurableWorkflowStore(path)
    try:
        store.reserve("run-cx1", "step-1", tool_calls=1)
        queue.put("PASS")
    except BudgetExceeded as exc:
        queue.put(exc.dimension)


def test_counters_survive_store_restart(tmp_path):
    path = str(tmp_path / "workflow.sqlite3")
    store = DurableWorkflowStore(path)
    store.create(_context(tool_calls=3))
    store.reserve("run-cx1", "step-1", tool_calls=1, tokens=20)
    restarted = DurableWorkflowStore(path)
    context, usage, cancelled = restarted.get("run-cx1", "step-1")
    assert context.run_id == "run-cx1"
    assert usage["tool_calls"] == 1
    assert usage["tokens"] == 20
    assert cancelled is False


def test_concurrent_reservations_cannot_exceed_cap(tmp_path):
    path = str(tmp_path / "workflow.sqlite3")
    DurableWorkflowStore(path).create(_context(tool_calls=1))
    context = multiprocessing.get_context("fork")
    queue = context.Queue()
    workers = [context.Process(target=_reserve, args=(path, queue)) for _ in range(2)]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join(timeout=10)
        assert worker.exitcode == 0
    results = [queue.get(timeout=2), queue.get(timeout=2)]
    assert sorted(results) == ["PASS", "tool_calls"]


def test_cancelled_step_and_expired_deadline_fail_closed(tmp_path):
    cancelled_path = str(tmp_path / "cancelled.sqlite3")
    cancelled_store = DurableWorkflowStore(cancelled_path)
    cancelled_store.create(_context())
    cancelled_store.cancel("run-cx1", "step-1")
    with pytest.raises(WorkflowCancelled):
        cancelled_store.reserve("run-cx1", "step-1", tool_calls=1)
    expired_path = str(tmp_path / "expired.sqlite3")
    expired_store = DurableWorkflowStore(expired_path)
    expired_store.create(_context(deadline=time.time() - 1))
    with pytest.raises(BudgetExceeded) as error:
        expired_store.reserve("run-cx1", "step-1", tool_calls=1)
    assert error.value.dimension == "deadline"


def test_budget_limit_is_typed_and_does_not_mutate_on_failure(tmp_path):
    path = str(tmp_path / "workflow.sqlite3")
    store = DurableWorkflowStore(path)
    store.create(_context(tool_calls=1))
    with pytest.raises(BudgetExceeded) as error:
        store.reserve("run-cx1", "step-1", tool_calls=2)
    assert error.value.dimension == "tool_calls"
    assert store.get("run-cx1", "step-1")[1]["tool_calls"] == 0
