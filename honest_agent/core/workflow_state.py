from __future__ import annotations

import sqlite3
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class WorkflowState(str, Enum):
    PROPOSED = "PROPOSED"
    EVALUATING = "EVALUATING"
    PAUSED = "PAUSED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"
    HANDOFF_ISSUED = "HANDOFF_ISSUED"
    EXECUTION_STARTED = "EXECUTION_STARTED"
    COMPLETED = "COMPLETED"
    COMPENSATED = "COMPENSATED"


class WorkflowStateError(RuntimeError):
    pass


@dataclass(frozen=True)
class WorkflowStateRecord:
    run_id: str
    step_id: str
    attempt: int
    intent_hash: str
    evidence_snapshot_id: str
    policy_snapshot_id: str
    state: WorkflowState
    reviewer: str | None
    expires_at: float
    updated_at: float


class DurableWorkflowStateStore:
    """SQLite state machine with approval and resume scope enforced atomically."""

    _TRANSITIONS = {
        WorkflowState.PROPOSED: {WorkflowState.EVALUATING, WorkflowState.CANCELLED, WorkflowState.EXPIRED},
        WorkflowState.EVALUATING: {WorkflowState.PAUSED, WorkflowState.REJECTED, WorkflowState.EXPIRED, WorkflowState.CANCELLED},
        WorkflowState.PAUSED: {WorkflowState.APPROVED, WorkflowState.REJECTED, WorkflowState.EXPIRED, WorkflowState.CANCELLED},
        WorkflowState.APPROVED: {WorkflowState.HANDOFF_ISSUED, WorkflowState.EXPIRED, WorkflowState.CANCELLED},
        WorkflowState.HANDOFF_ISSUED: {WorkflowState.EXECUTION_STARTED, WorkflowState.EXPIRED, WorkflowState.CANCELLED},
        WorkflowState.EXECUTION_STARTED: {WorkflowState.COMPLETED, WorkflowState.COMPENSATED, WorkflowState.CANCELLED},
    }

    def __init__(self, path: str = "trajectories/workflow_state.sqlite3"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute("CREATE TABLE IF NOT EXISTS workflow_states (run_id TEXT NOT NULL, step_id TEXT NOT NULL, attempt INTEGER NOT NULL, intent_hash TEXT NOT NULL, evidence_snapshot_id TEXT NOT NULL, policy_snapshot_id TEXT NOT NULL, state TEXT NOT NULL, reviewer TEXT, expires_at REAL NOT NULL, updated_at REAL NOT NULL, PRIMARY KEY (run_id, step_id, attempt))")

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        connection.row_factory = sqlite3.Row
        return connection

    @staticmethod
    def _record(row: sqlite3.Row) -> WorkflowStateRecord:
        return WorkflowStateRecord(row["run_id"], row["step_id"], row["attempt"], row["intent_hash"], row["evidence_snapshot_id"], row["policy_snapshot_id"], WorkflowState(row["state"]), row["reviewer"], row["expires_at"], row["updated_at"])

    def create(self, run_id: str, step_id: str, attempt: int, intent_hash: str, evidence_snapshot_id: str, policy_snapshot_id: str, *, expires_at: float) -> WorkflowStateRecord:
        if not all(isinstance(value, str) and value for value in (run_id, step_id, intent_hash, evidence_snapshot_id, policy_snapshot_id)) or attempt < 1 or expires_at <= time.time():
            raise ValueError("invalid workflow state identity or expiry")
        now = time.time()
        with self._connect() as connection:
            try:
                connection.execute("INSERT INTO workflow_states VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (run_id, step_id, attempt, intent_hash, evidence_snapshot_id, policy_snapshot_id, WorkflowState.PROPOSED.value, None, expires_at, now))
            except sqlite3.IntegrityError as exc:
                raise WorkflowStateError("workflow attempt already exists") from exc
        return self.get(run_id, step_id, attempt)

    def get(self, run_id: str, step_id: str, attempt: int) -> WorkflowStateRecord:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM workflow_states WHERE run_id = ? AND step_id = ? AND attempt = ?", (run_id, step_id, attempt)).fetchone()
        if row is None:
            raise KeyError((run_id, step_id, attempt))
        return self._record(row)

    def transition(self, run_id: str, step_id: str, attempt: int, target: WorkflowState) -> WorkflowStateRecord:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute("SELECT * FROM workflow_states WHERE run_id = ? AND step_id = ? AND attempt = ?", (run_id, step_id, attempt)).fetchone()
            if row is None:
                connection.rollback()
                raise KeyError((run_id, step_id, attempt))
            current = WorkflowState(row["state"])
            if time.time() >= row["expires_at"] and current not in {WorkflowState.EXPIRED, WorkflowState.COMPLETED, WorkflowState.COMPENSATED, WorkflowState.CANCELLED, WorkflowState.REJECTED}:
                target = WorkflowState.EXPIRED
            if target not in self._TRANSITIONS.get(current, set()):
                connection.rollback()
                raise WorkflowStateError(f"invalid transition {current.value}->{target.value}")
            connection.execute("UPDATE workflow_states SET state = ?, updated_at = ? WHERE run_id = ? AND step_id = ? AND attempt = ?", (target.value, time.time(), run_id, step_id, attempt))
            connection.commit()
        return self.get(run_id, step_id, attempt)

    def approve(self, run_id: str, step_id: str, attempt: int, *, reviewer: str, intent_hash: str, evidence_snapshot_id: str, policy_snapshot_id: str) -> WorkflowStateRecord:
        if not reviewer.strip():
            raise WorkflowStateError("reviewer is required")
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute("SELECT * FROM workflow_states WHERE run_id = ? AND step_id = ? AND attempt = ?", (run_id, step_id, attempt)).fetchone()
            if row is None:
                connection.rollback()
                raise KeyError((run_id, step_id, attempt))
            if time.time() >= row["expires_at"]:
                connection.rollback()
                raise WorkflowStateError("checkpoint expired")
            if row["state"] != WorkflowState.PAUSED.value:
                connection.rollback()
                raise WorkflowStateError("checkpoint is not pending approval")
            if (row["intent_hash"], row["evidence_snapshot_id"], row["policy_snapshot_id"]) != (intent_hash, evidence_snapshot_id, policy_snapshot_id):
                connection.rollback()
                raise WorkflowStateError("approval scope does not match current state")
            connection.execute("UPDATE workflow_states SET state = ?, reviewer = ?, updated_at = ? WHERE run_id = ? AND step_id = ? AND attempt = ? AND state = ?", (WorkflowState.APPROVED.value, reviewer, time.time(), run_id, step_id, attempt, WorkflowState.PAUSED.value))
            connection.commit()
        return self.get(run_id, step_id, attempt)

    def cancel(self, run_id: str, step_id: str, attempt: int) -> WorkflowStateRecord:
        return self.transition(run_id, step_id, attempt, WorkflowState.CANCELLED)

    def consume_for_execution(self, run_id: str, step_id: str, attempt: int, *, intent_hash: str, evidence_snapshot_id: str, policy_snapshot_id: str) -> WorkflowStateRecord:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute("SELECT * FROM workflow_states WHERE run_id = ? AND step_id = ? AND attempt = ?", (run_id, step_id, attempt)).fetchone()
            if row is None:
                connection.rollback()
                raise KeyError((run_id, step_id, attempt))
            if time.time() >= row["expires_at"]:
                connection.rollback()
                raise WorkflowStateError("execution authorization expired")
            if row["state"] not in {WorkflowState.APPROVED.value, WorkflowState.HANDOFF_ISSUED.value}:
                connection.rollback()
                raise WorkflowStateError("workflow is not ready for execution")
            if (row["intent_hash"], row["evidence_snapshot_id"], row["policy_snapshot_id"]) != (intent_hash, evidence_snapshot_id, policy_snapshot_id):
                connection.rollback()
                raise WorkflowStateError("execution scope does not match approval")
            connection.execute("UPDATE workflow_states SET state = ?, updated_at = ? WHERE run_id = ? AND step_id = ? AND attempt = ? AND state IN (?, ?)", (WorkflowState.EXECUTION_STARTED.value, time.time(), run_id, step_id, attempt, WorkflowState.APPROVED.value, WorkflowState.HANDOFF_ISSUED.value))
            connection.commit()
        return self.get(run_id, step_id, attempt)


__all__ = ["DurableWorkflowStateStore", "WorkflowState", "WorkflowStateError", "WorkflowStateRecord"]
