from __future__ import annotations

import asyncio
import sqlite3
import time
import uuid
from collections.abc import Awaitable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Awaitable, Callable, Mapping


class ExecutionSemantics(str, Enum):
    AT_MOST_ONCE = "AT_MOST_ONCE"
    IDEMPOTENT_AT_LEAST_ONCE = "IDEMPOTENT_AT_LEAST_ONCE"


class IntentState(str, Enum):
    ACCEPTED = "ACCEPTED"
    EXECUTING = "EXECUTING"
    RETRYABLE_FAILURE = "RETRYABLE_FAILURE"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    UNKNOWN_AFTER_CRASH = "UNKNOWN_AFTER_CRASH"


class ExecutionError(RuntimeError):
    pass


@dataclass(frozen=True)
class ExecutionIntent:
    intent_id: str
    tenant_id: str
    workflow_id: str
    tool_name: str
    payload: Mapping[str, Any]
    idempotency_key: str
    semantics: ExecutionSemantics
    max_attempts: int
    timeout_seconds: float
    state: IntentState
    attempts: int
    last_error: str | None = None
    result: Any = None


class IntentStore:
    """SQLite transactional inbox/outbox with durable kill switches and quotas."""

    def __init__(self, path: str = "trajectories/execution.sqlite3"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS execution_intents (
                    intent_id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, workflow_id TEXT NOT NULL,
                    tool_name TEXT NOT NULL, payload_json TEXT NOT NULL, idempotency_key TEXT NOT NULL,
                    semantics TEXT NOT NULL, max_attempts INTEGER NOT NULL, timeout_seconds REAL NOT NULL,
                    state TEXT NOT NULL, attempts INTEGER NOT NULL, last_error TEXT, result_json TEXT,
                    updated_at REAL NOT NULL, UNIQUE (tenant_id, tool_name, idempotency_key)
                );
                CREATE TABLE IF NOT EXISTS execution_controls (scope TEXT PRIMARY KEY, enabled INTEGER NOT NULL DEFAULT 1, quota INTEGER);
            """)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        connection.row_factory = sqlite3.Row
        return connection

    @staticmethod
    def _decode(row: sqlite3.Row) -> ExecutionIntent:
        import json
        return ExecutionIntent(row["intent_id"], row["tenant_id"], row["workflow_id"], row["tool_name"], json.loads(row["payload_json"]), row["idempotency_key"], ExecutionSemantics(row["semantics"]), row["max_attempts"], row["timeout_seconds"], IntentState(row["state"]), row["attempts"], row["last_error"], json.loads(row["result_json"]) if row["result_json"] is not None else None)

    def submit(self, tenant_id: str, workflow_id: str, tool_name: str, payload: Mapping[str, Any], *, idempotency_key: str, semantics: ExecutionSemantics, max_attempts: int = 1, timeout_seconds: float = 30.0) -> ExecutionIntent:
        import json
        if not all(isinstance(value, str) and value.strip() for value in (tenant_id, workflow_id, tool_name, idempotency_key)) or not isinstance(payload, Mapping) or max_attempts < 1 or timeout_seconds <= 0:
            raise ValueError("invalid execution intent")
        if semantics == ExecutionSemantics.AT_MOST_ONCE:
            max_attempts = 1
        intent_id = uuid.uuid4().hex
        with self._connect() as connection:
            try:
                connection.execute("INSERT INTO execution_intents VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (intent_id, tenant_id, workflow_id, tool_name, json.dumps(dict(payload), sort_keys=True), idempotency_key, semantics.value, max_attempts, timeout_seconds, IntentState.ACCEPTED.value, 0, None, None, time.time(),))
            except sqlite3.IntegrityError:
                row = connection.execute("SELECT * FROM execution_intents WHERE tenant_id = ? AND tool_name = ? AND idempotency_key = ?", (tenant_id, tool_name, idempotency_key)).fetchone()
                if row is None:
                    raise ExecutionError("intent could not be recorded")
                return self._decode(row)
        return self.get(intent_id)

    def get(self, intent_id: str) -> ExecutionIntent:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM execution_intents WHERE intent_id = ?", (intent_id,)).fetchone()
        if row is None:
            raise KeyError(intent_id)
        return self._decode(row)

    def claim(self, intent_id: str, *, allow_retry: bool = False) -> ExecutionIntent:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute("SELECT * FROM execution_intents WHERE intent_id = ?", (intent_id,)).fetchone()
            if row is None:
                connection.rollback()
                raise KeyError(intent_id)
            state = IntentState(row["state"])
            allowed = {IntentState.ACCEPTED} | ({IntentState.RETRYABLE_FAILURE} if allow_retry else set())
            if state not in allowed:
                connection.rollback()
                raise ExecutionError(f"intent cannot be claimed from {state.value}")
            blocked = self._blocked(connection, row)
            if blocked:
                connection.rollback()
                raise ExecutionError(f"execution blocked: {blocked}")
            if row["attempts"] >= row["max_attempts"]:
                connection.rollback()
                raise ExecutionError("execution attempt cap exceeded")
            connection.execute("UPDATE execution_intents SET state = ?, attempts = attempts + 1, updated_at = ? WHERE intent_id = ? AND state = ?", (IntentState.EXECUTING.value, time.time(), intent_id, state.value))
            connection.commit()
        return self.get(intent_id)

    @staticmethod
    def _blocked(connection: sqlite3.Connection, row: sqlite3.Row) -> str | None:
        scopes = (f"tenant:{row['tenant_id']}", f"workflow:{row['workflow_id']}", f"tool:{row['tool_name']}", "global")
        for scope in scopes:
            control = connection.execute("SELECT enabled, quota FROM execution_controls WHERE scope = ?", (scope,)).fetchone()
            if control is not None and not control["enabled"]:
                return scope
            kind, _, value = scope.partition(":")
            if kind == "tenant":
                attempts = connection.execute("SELECT COALESCE(SUM(attempts), 0) FROM execution_intents WHERE tenant_id = ?", (value,)).fetchone()[0]
            elif kind == "workflow":
                attempts = connection.execute("SELECT COALESCE(SUM(attempts), 0) FROM execution_intents WHERE workflow_id = ?", (value,)).fetchone()[0]
            elif kind == "tool":
                attempts = connection.execute("SELECT COALESCE(SUM(attempts), 0) FROM execution_intents WHERE tool_name = ?", (value,)).fetchone()[0]
            else:
                attempts = connection.execute("SELECT COALESCE(SUM(attempts), 0) FROM execution_intents").fetchone()[0]
            if control is not None and control["quota"] is not None and attempts >= control["quota"]:
                return f"quota:{scope}"
        return None

    def finish(self, intent_id: str, *, result: Any = None) -> ExecutionIntent:
        import json
        with self._connect() as connection:
            changed = connection.execute("UPDATE execution_intents SET state = ?, result_json = ?, updated_at = ? WHERE intent_id = ? AND state = ?", (IntentState.SUCCEEDED.value, json.dumps(result, sort_keys=True), time.time(), intent_id, IntentState.EXECUTING.value)).rowcount
            if changed != 1:
                raise ExecutionError("intent is not executing")
        return self.get(intent_id)

    def fail(self, intent_id: str, error: str, *, retryable: bool) -> ExecutionIntent:
        state = IntentState.RETRYABLE_FAILURE if retryable else IntentState.FAILED
        with self._connect() as connection:
            changed = connection.execute("UPDATE execution_intents SET state = ?, last_error = ?, updated_at = ? WHERE intent_id = ? AND state = ?", (state.value, error[:500], time.time(), intent_id, IntentState.EXECUTING.value)).rowcount
            if changed != 1:
                raise ExecutionError("intent is not executing")
        return self.get(intent_id)

    def cancel(self, intent_id: str) -> ExecutionIntent:
        with self._connect() as connection:
            changed = connection.execute("UPDATE execution_intents SET state = ?, updated_at = ? WHERE intent_id = ? AND state IN (?, ?)", (IntentState.CANCELLED.value, time.time(), intent_id, IntentState.ACCEPTED.value, IntentState.RETRYABLE_FAILURE.value)).rowcount
            if changed != 1:
                raise ExecutionError("only unclaimed intents can be cancelled")
        return self.get(intent_id)

    def recover(self, intent_id: str) -> ExecutionIntent:
        """Mark an interrupted claim unknown; never silently replay an at-most-once mutation."""
        with self._connect() as connection:
            changed = connection.execute("UPDATE execution_intents SET state = ?, updated_at = ? WHERE intent_id = ? AND state = ?", (IntentState.UNKNOWN_AFTER_CRASH.value, time.time(), intent_id, IntentState.EXECUTING.value)).rowcount
            if changed != 1:
                raise ExecutionError("only executing intents can be recovered")
        return self.get(intent_id)

    def set_quota(self, scope: str, quota: int | None) -> None:
        if quota is not None and quota < 1:
            raise ValueError("quota must be positive or None")
        if not scope.strip():
            raise ValueError("quota scope is required")
        with self._connect() as connection:
            connection.execute("INSERT INTO execution_controls(scope, enabled, quota) VALUES (?, 1, ?) ON CONFLICT(scope) DO UPDATE SET quota = excluded.quota", (scope, quota))

    def set_kill_switch(self, scope: str, enabled: bool = False) -> None:
        if not scope.strip():
            raise ValueError("kill-switch scope is required")
        with self._connect() as connection:
            connection.execute("INSERT INTO execution_controls(scope, enabled) VALUES (?, ?) ON CONFLICT(scope) DO UPDATE SET enabled = excluded.enabled", (scope, int(enabled)))


class ReliableExecutor:
    """Execute a claimed intent without false success; retries require idempotency."""

    def __init__(self, store: IntentStore):
        self.store = store

    async def run_once(self, intent_id: str, tool: Callable[[Mapping[str, Any]], Any | Awaitable[Any]], *, retry: bool = False) -> ExecutionIntent:
        intent = self.store.claim(intent_id, allow_retry=retry)
        try:
            output = await asyncio.wait_for(self._call(tool, intent.payload), timeout=intent.timeout_seconds)
        except asyncio.TimeoutError:
            return self.store.fail(intent_id, "timeout", retryable=intent.semantics == ExecutionSemantics.IDEMPOTENT_AT_LEAST_ONCE and intent.attempts < intent.max_attempts)
        except asyncio.CancelledError:
            return self.store.fail(intent_id, "cancelled", retryable=False)
        except Exception as exc:
            return self.store.fail(intent_id, type(exc).__name__, retryable=intent.semantics == ExecutionSemantics.IDEMPOTENT_AT_LEAST_ONCE and intent.attempts < intent.max_attempts)
        return self.store.finish(intent_id, result=output)

    @staticmethod
    async def _call(tool: Callable[[Mapping[str, Any]], Any | Awaitable[Any]], payload: Mapping[str, Any]) -> Any:
        result = tool(payload)
        return await result if isinstance(result, Awaitable) else result


__all__ = ["ExecutionError", "ExecutionIntent", "ExecutionSemantics", "IntentState", "IntentStore", "ReliableExecutor"]
