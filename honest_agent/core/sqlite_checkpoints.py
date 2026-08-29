from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path

from honest_agent.schemas.models import EvaluationRequest, GuardDecision
from honest_agent.core.checkpoints import CheckpointStore


class SQLiteCheckpointStore(CheckpointStore):
    """Production-oriented local transactional checkpoint store.

    A deployment may place the SQLite file on a durable volume; the same interface
    can later be backed by a managed relational database without changing guardrail code.
    """

    def __init__(self, path: str = "trajectories/checkpoints.sqlite3", retention_seconds: int | None = None):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.retention_seconds = retention_seconds
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA foreign_keys=ON")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS checkpoints (
                    trajectory_id TEXT PRIMARY KEY,
                    state TEXT NOT NULL CHECK (state IN ('pending', 'resolved')),
                    request_json TEXT NOT NULL,
                    decision_json TEXT NOT NULL,
                    updated_at REAL NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_checkpoints_state_updated
                    ON checkpoints(state, updated_at);
                """
            )

    def _prune(self, connection: sqlite3.Connection) -> None:
        if self.retention_seconds is not None:
            connection.execute("DELETE FROM checkpoints WHERE updated_at < ?", (time.time() - self.retention_seconds,))

    @staticmethod
    def _record(request: EvaluationRequest, decision: GuardDecision) -> tuple:
        return (decision.trajectory_id, request.model_dump_json(), decision.model_dump_json(), time.time())

    def put_pending(self, request: EvaluationRequest, decision: GuardDecision) -> None:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            self._prune(connection)
            connection.execute("INSERT OR REPLACE INTO checkpoints VALUES (?, 'pending', ?, ?, ?)", self._record(request, decision))
            connection.commit()

    def get_pending(self, trajectory_id: str) -> tuple[EvaluationRequest, GuardDecision] | None:
        with self._connect() as connection:
            self._prune(connection)
            row = connection.execute("SELECT request_json, decision_json FROM checkpoints WHERE trajectory_id = ? AND state = 'pending'", (trajectory_id,)).fetchone()
            connection.commit()
            if row is None:
                return None
            return EvaluationRequest.model_validate_json(row["request_json"]), GuardDecision.model_validate_json(row["decision_json"])

    def put_resolved(self, request: EvaluationRequest, decision: GuardDecision) -> None:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            self._prune(connection)
            connection.execute("INSERT OR REPLACE INTO checkpoints VALUES (?, 'resolved', ?, ?, ?)", self._record(request, decision))
            connection.commit()

    def resolve_pending(self, request: EvaluationRequest, decision: GuardDecision) -> GuardDecision:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            self._prune(connection)
            row = connection.execute("SELECT state, decision_json FROM checkpoints WHERE trajectory_id = ?", (decision.trajectory_id,)).fetchone()
            if row is not None and row["state"] == "resolved":
                connection.commit()
                return GuardDecision.model_validate_json(row["decision_json"])
            if row is None:
                connection.rollback()
                raise KeyError(decision.trajectory_id)
            connection.execute("UPDATE checkpoints SET state = 'resolved', request_json = ?, decision_json = ?, updated_at = ? WHERE trajectory_id = ? AND state = 'pending'", (request.model_dump_json(), decision.model_dump_json(), time.time(), decision.trajectory_id))
            connection.commit()
            return decision

    def get_resolved(self, trajectory_id: str) -> GuardDecision | None:
        with self._connect() as connection:
            self._prune(connection)
            row = connection.execute("SELECT decision_json FROM checkpoints WHERE trajectory_id = ? AND state = 'resolved'", (trajectory_id,)).fetchone()
            connection.commit()
            return GuardDecision.model_validate_json(row["decision_json"]) if row else None

    def backup(self, destination: str) -> None:
        destination_path = Path(destination)
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as source, sqlite3.connect(destination_path) as target:
            source.backup(target)

    @classmethod
    def restore(cls, source: str, destination: str, retention_seconds: int | None = None) -> "SQLiteCheckpointStore":
        source_path = Path(source)
        destination_path = Path(destination)
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(source_path) as source_connection, sqlite3.connect(destination_path) as destination_connection:
            source_connection.backup(destination_connection)
        return cls(str(destination_path), retention_seconds)
