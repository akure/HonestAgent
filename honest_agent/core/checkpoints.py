from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from typing import Any

from honest_agent.schemas.models import EvaluationRequest, GuardDecision


class CheckpointStore:
    """Small persistence interface for checkpoint state; replaceable in production."""

    def put_pending(self, request: EvaluationRequest, decision: GuardDecision) -> None:
        raise NotImplementedError

    def get_pending(self, trajectory_id: str) -> tuple[EvaluationRequest, GuardDecision] | None:
        raise NotImplementedError

    def put_resolved(self, request: EvaluationRequest, decision: GuardDecision) -> None:
        raise NotImplementedError

    def get_resolved(self, trajectory_id: str) -> GuardDecision | None:
        raise NotImplementedError


class FileCheckpointStore(CheckpointStore):
    """Atomic JSON persistence suitable for local development and single-writer pilots."""

    def __init__(self, path: str = "trajectories/checkpoints.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._state = self._load()

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"pending": {}, "resolved": {}}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {"pending": {}, "resolved": {}}

    def _flush(self) -> None:
        temp = self.path.with_suffix(self.path.suffix + ".tmp")
        temp.write_text(json.dumps(self._state, indent=2), encoding="utf-8")
        os.replace(temp, self.path)

    def put_pending(self, request: EvaluationRequest, decision: GuardDecision) -> None:
        with self._lock:
            self._state.setdefault("pending", {})[decision.trajectory_id] = {
                "request": request.model_dump(mode="json"),
                "decision": decision.model_dump(mode="json"),
            }
            self._flush()

    def get_pending(self, trajectory_id: str) -> tuple[EvaluationRequest, GuardDecision] | None:
        with self._lock:
            record = self._state.get("pending", {}).get(trajectory_id)
            if not record:
                return None
            return EvaluationRequest.model_validate(record["request"]), GuardDecision.model_validate(record["decision"])

    def put_resolved(self, request: EvaluationRequest, decision: GuardDecision) -> None:
        with self._lock:
            self._state.setdefault("resolved", {})[decision.trajectory_id] = {
                "request": request.model_dump(mode="json"),
                "decision": decision.model_dump(mode="json"),
            }
            self._state.setdefault("pending", {}).pop(decision.trajectory_id, None)
            self._flush()

    def get_resolved(self, trajectory_id: str) -> GuardDecision | None:
        with self._lock:
            record = self._state.get("resolved", {}).get(trajectory_id)
            return GuardDecision.model_validate(record["decision"]) if record else None
