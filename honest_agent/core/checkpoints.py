from __future__ import annotations

import fcntl
import json
import os
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from honest_agent.schemas.models import EvaluationRequest, GuardDecision


class CheckpointStore:
    """Persistence interface for checkpoint state."""

    def put_pending(self, request: EvaluationRequest, decision: GuardDecision) -> None:
        raise NotImplementedError

    def get_pending(self, trajectory_id: str) -> tuple[EvaluationRequest, GuardDecision] | None:
        raise NotImplementedError

    def put_resolved(self, request: EvaluationRequest, decision: GuardDecision) -> None:
        raise NotImplementedError

    def resolve_pending(self, request: EvaluationRequest, decision: GuardDecision) -> GuardDecision:
        """Atomically resolve a pending checkpoint; return the winning state."""
        raise NotImplementedError

    def get_resolved(self, trajectory_id: str) -> GuardDecision | None:
        raise NotImplementedError


class FileCheckpointStore(CheckpointStore):
    """Crash-safe JSON checkpoint persistence with cross-process transactions."""

    def __init__(self, path: str = "trajectories/checkpoints.json", retention_seconds: int | None = None):
        self.path = Path(path)
        self.lock_path = self.path.with_suffix(self.path.suffix + ".lock")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self.retention_seconds = retention_seconds
        self._state = self._load_unlocked()

    def _empty(self) -> dict[str, Any]:
        return {"version": 2, "pending": {}, "resolved": {}}

    def _load_unlocked(self) -> dict[str, Any]:
        if not self.path.exists():
            return self._empty()
        try:
            state = json.loads(self.path.read_text(encoding="utf-8"))
            state.setdefault("version", 2)
            state.setdefault("pending", {})
            state.setdefault("resolved", {})
            return state
        except (OSError, json.JSONDecodeError):
            return self._empty()

    @contextmanager
    def _transaction(self, write: bool = False) -> Iterator[dict[str, Any]]:
        with self._lock:
            self.lock_path.touch(exist_ok=True)
            with self.lock_path.open("r+", encoding="utf-8") as lock_file:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX if write else fcntl.LOCK_SH)
                self._state = self._load_unlocked()
                self._prune_unlocked()
                try:
                    yield self._state
                    if write:
                        self._flush_unlocked()
                finally:
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)

    def _flush_unlocked(self) -> None:
        temp = self.path.with_suffix(self.path.suffix + f".{os.getpid()}.tmp")
        temp.write_text(json.dumps(self._state, indent=2, sort_keys=True), encoding="utf-8")
        os.replace(temp, self.path)

    def _record(self, request: EvaluationRequest, decision: GuardDecision) -> dict[str, Any]:
        return {"updated_at": time.time(), "request": request.model_dump(mode="json"), "decision": decision.model_dump(mode="json")}

    def _prune_unlocked(self) -> None:
        if self.retention_seconds is None:
            return
        cutoff = time.time() - self.retention_seconds
        for bucket in ("pending", "resolved"):
            records = self._state.setdefault(bucket, {})
            for trajectory_id, record in list(records.items()):
                if float(record.get("updated_at", time.time())) < cutoff:
                    records.pop(trajectory_id, None)

    def put_pending(self, request: EvaluationRequest, decision: GuardDecision) -> None:
        with self._transaction(write=True) as state:
            state.setdefault("pending", {})[decision.trajectory_id] = self._record(request, decision)

    def get_pending(self, trajectory_id: str) -> tuple[EvaluationRequest, GuardDecision] | None:
        with self._transaction(write=True) as state:
            record = state.get("pending", {}).get(trajectory_id)
            if not record:
                return None
            return EvaluationRequest.model_validate(record["request"]), GuardDecision.model_validate(record["decision"])

    def put_resolved(self, request: EvaluationRequest, decision: GuardDecision) -> None:
        with self._transaction(write=True) as state:
            state.setdefault("resolved", {})[decision.trajectory_id] = self._record(request, decision)
            state.setdefault("pending", {}).pop(decision.trajectory_id, None)

    def resolve_pending(self, request: EvaluationRequest, decision: GuardDecision) -> GuardDecision:
        with self._transaction(write=True) as state:
            trajectory_id = decision.trajectory_id
            existing = state.setdefault("resolved", {}).get(trajectory_id)
            if existing:
                return GuardDecision.model_validate(existing["decision"])
            if trajectory_id not in state.setdefault("pending", {}):
                raise KeyError(trajectory_id)
            state["resolved"][trajectory_id] = self._record(request, decision)
            state["pending"].pop(trajectory_id, None)
            return decision

    def get_resolved(self, trajectory_id: str) -> GuardDecision | None:
        with self._transaction(write=True) as state:
            record = state.get("resolved", {}).get(trajectory_id)
            return GuardDecision.model_validate(record["decision"]) if record else None
