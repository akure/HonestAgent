from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from honest_agent.schemas.workflow import WorkflowRunContext


class BudgetExceeded(RuntimeError):
    def __init__(self, dimension: str, limit: float, current: float, requested: float):
        self.dimension = dimension
        self.limit = limit
        self.current = current
        self.requested = requested
        super().__init__(f"CAP_EXCEEDED:{dimension}")


class WorkflowCancelled(RuntimeError):
    pass


@dataclass(frozen=True)
class BudgetReservation:
    run_id: str
    step_id: str
    usage: dict[str, float]


class DurableWorkflowStore:
    """SQLite-backed workflow context and atomic budget accounting."""

    DIMENSIONS = ("verifier_calls", "tool_calls", "retries", "tokens", "fan_out", "concurrency", "cumulative_amount")

    def __init__(self, path: str = "trajectories/workflows.sqlite3"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS workflow_contexts (
                    context_key TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    step_id TEXT NOT NULL,
                    context_json TEXT NOT NULL,
                    usage_json TEXT NOT NULL,
                    cancelled INTEGER NOT NULL DEFAULT 0,
                    updated_at REAL NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_workflow_run ON workflow_contexts(run_id);
            """)

    @staticmethod
    def _key(context: WorkflowRunContext) -> str:
        return f"{context.run_id}:{context.step_id}"

    def create(self, context: WorkflowRunContext) -> None:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute("INSERT OR IGNORE INTO workflow_contexts VALUES (?, ?, ?, ?, ?, 0, ?)", (self._key(context), context.run_id, context.step_id, context.model_dump_json(), json.dumps({dimension: 0.0 for dimension in self.DIMENSIONS}), time.time()))
            connection.commit()

    def get(self, run_id: str, step_id: str) -> tuple[WorkflowRunContext, dict[str, float], bool] | None:
        with self._connect() as connection:
            row = connection.execute("SELECT context_json, usage_json, cancelled FROM workflow_contexts WHERE context_key = ?", (f"{run_id}:{step_id}",)).fetchone()
            if row is None:
                return None
            return WorkflowRunContext.model_validate_json(row["context_json"]), json.loads(row["usage_json"]), bool(row["cancelled"])

    def cancel(self, run_id: str, step_id: str) -> None:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            changed = connection.execute("UPDATE workflow_contexts SET cancelled = 1, updated_at = ? WHERE context_key = ?", (time.time(), f"{run_id}:{step_id}")).rowcount
            connection.commit()
            if changed == 0:
                raise KeyError(f"{run_id}:{step_id}")

    def reserve(self, run_id: str, step_id: str, **increments: float) -> BudgetReservation:
        unknown = set(increments) - set(self.DIMENSIONS)
        if unknown or any(value < 0 for value in increments.values()):
            raise ValueError("unknown or negative budget increment")
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute("SELECT context_json, usage_json, cancelled FROM workflow_contexts WHERE context_key = ?", (f"{run_id}:{step_id}",)).fetchone()
            if row is None:
                connection.rollback()
                raise KeyError(f"{run_id}:{step_id}")
            context = WorkflowRunContext.model_validate_json(row["context_json"])
            if row["cancelled"]:
                connection.rollback()
                raise WorkflowCancelled(f"workflow step cancelled: {step_id}")
            if time.time() > context.deadline:
                connection.rollback()
                raise BudgetExceeded("deadline", context.deadline, time.time(), 0)
            usage: dict[str, float] = json.loads(row["usage_json"])
            limits = context.budgets.model_dump()
            for dimension, requested in increments.items():
                current = usage.get(dimension, 0.0)
                limit = limits[dimension]
                if current + requested > limit:
                    connection.rollback()
                    raise BudgetExceeded(dimension, limit, current, requested)
            for dimension, requested in increments.items():
                usage[dimension] = usage.get(dimension, 0.0) + requested
            connection.execute("UPDATE workflow_contexts SET usage_json = ?, updated_at = ? WHERE context_key = ?", (json.dumps(usage, sort_keys=True), time.time(), f"{run_id}:{step_id}"))
            connection.commit()
            return BudgetReservation(run_id, step_id, usage)

    def release_concurrency(self, run_id: str, step_id: str) -> None:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute("SELECT usage_json FROM workflow_contexts WHERE context_key = ?", (f"{run_id}:{step_id}",)).fetchone()
            if row is None:
                connection.rollback()
                raise KeyError(f"{run_id}:{step_id}")
            usage = json.loads(row["usage_json"])
            usage["concurrency"] = max(0.0, usage.get("concurrency", 0.0) - 1.0)
            connection.execute("UPDATE workflow_contexts SET usage_json = ?, updated_at = ? WHERE context_key = ?", (json.dumps(usage, sort_keys=True), time.time(), f"{run_id}:{step_id}"))
            connection.commit()
