from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any

from honest_agent.core.security import redact


class AuditIntegrityError(ValueError):
    pass


class AppendOnlyAuditSink:
    """Local append-only audit sink with tamper-evident hash chaining.

    Production deployments should place the file on an access-controlled,
    append-only volume or forward the same records to an immutable sink.
    """

    def __init__(self, path: str = "audit/events.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: str, *, subject: str, trajectory_id: str, policy_version: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
        previous_hash = ""
        if self.path.exists():
            last = next(reversed(self.path.read_text(encoding="utf-8").splitlines()), "")
            if last:
                previous_hash = json.loads(last)["hash"]
        record = {
            "event": event,
            "subject": subject,
            "trajectory_id": trajectory_id,
            "policy_version": policy_version,
            "timestamp": time.time(),
            "details": redact(details or {}),
            "previous_hash": previous_hash,
        }
        encoded = json.dumps(record, sort_keys=True, separators=(",", ":"))
        record["hash"] = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
        return record

    def verify(self) -> bool:
        previous_hash = ""
        for line in self.path.read_text(encoding="utf-8").splitlines() if self.path.exists() else []:
            record = json.loads(line)
            observed = record.pop("hash")
            if record["previous_hash"] != previous_hash:
                raise AuditIntegrityError("audit chain is broken")
            encoded = json.dumps(record, sort_keys=True, separators=(",", ":"))
            if hashlib.sha256(encoded.encode("utf-8")).hexdigest() != observed:
                raise AuditIntegrityError("audit record was modified")
            previous_hash = observed
        return True


__all__ = ["AppendOnlyAuditSink", "AuditIntegrityError"]
