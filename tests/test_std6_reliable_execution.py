import asyncio

import pytest

from honest_agent import ExecutionError, ExecutionSemantics, IntentState, IntentStore, ReliableExecutor


def submit(store, *, semantics=ExecutionSemantics.AT_MOST_ONCE, max_attempts=2, key="k-1"):
    return store.submit("tenant-a", "workflow-a", "charge", {"amount": 10}, idempotency_key=key, semantics=semantics, max_attempts=max_attempts, timeout_seconds=0.02)


def test_idempotent_submit_is_deduplicated_and_at_most_once_is_capped(tmp_path):
    store = IntentStore(str(tmp_path / "execution.sqlite3"))
    first = submit(store)
    duplicate = submit(store)
    assert duplicate.intent_id == first.intent_id
    assert first.max_attempts == 1
    store.claim(first.intent_id)
    with pytest.raises(ExecutionError):
        store.claim(first.intent_id, allow_retry=True)


def test_provider_failure_can_retry_only_for_idempotent_intent(tmp_path):
    store = IntentStore(str(tmp_path / "execution.sqlite3"))
    intent = submit(store, semantics=ExecutionSemantics.IDEMPOTENT_AT_LEAST_ONCE, max_attempts=2)
    executor = ReliableExecutor(store)
    failed = asyncio.run(executor.run_once(intent.intent_id, lambda _: (_ for _ in ()).throw(RuntimeError("provider down"))))
    assert failed.state is IntentState.RETRYABLE_FAILURE
    retried = asyncio.run(executor.run_once(intent.intent_id, lambda _: {"ok": True}, retry=True))
    assert retried.state is IntentState.SUCCEEDED
    assert retried.result == {"ok": True}


def test_timeout_does_not_claim_success_and_at_most_once_recovery_is_unknown(tmp_path):
    store = IntentStore(str(tmp_path / "execution.sqlite3"))
    intent = submit(store)
    executor = ReliableExecutor(store)
    result = asyncio.run(executor.run_once(intent.intent_id, async_sleep))
    assert result.state is IntentState.FAILED
    assert result.result is None
    second = submit(store, key="k-2")
    store.claim(second.intent_id)
    assert store.recover(second.intent_id).state is IntentState.UNKNOWN_AFTER_CRASH
    with pytest.raises(ExecutionError):
        store.claim(second.intent_id, allow_retry=True)


async def async_sleep(_):
    await asyncio.sleep(0.05)


def test_cancel_and_kill_switch_block_before_tool_call(tmp_path):
    store = IntentStore(str(tmp_path / "execution.sqlite3"))
    cancelled = submit(store, key="cancel")
    assert store.cancel(cancelled.intent_id).state is IntentState.CANCELLED
    with pytest.raises(ExecutionError):
        store.claim(cancelled.intent_id)
    blocked = submit(store, key="blocked")
    store.set_kill_switch("tool:charge", enabled=False)
    with pytest.raises(ExecutionError, match="execution blocked"):
        store.claim(blocked.intent_id)
    quota_seed = submit(store, key="quota-seed")
    store.set_kill_switch("tool:charge", enabled=True)
    store.claim(quota_seed.intent_id)
    quota = submit(store, key="quota")
    store.set_quota("tenant:tenant-a", 1)
    with pytest.raises(ExecutionError, match="quota"):
        store.claim(quota.intent_id)
