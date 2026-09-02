from __future__ import annotations

import fcntl
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Callable

from honest_agent.core.security import redact


class AuditIntegrityError(ValueError):
    pass


class AppendOnlyAuditSink:
    """Durable local append-only audit sink with tamper-evident hash chaining.

    Production deployments should place the file and lock on an access-controlled,
    append-only volume or forward the same records to an immutable sink. This
    reference sink never deletes records; retention filters retrieval instead.
    """

    def __init__(self, path: str = "audit/events.jsonl", *, retention_seconds: int | None = None, clock: Callable[[], float] = time.time):
        if retention_seconds is not None and retention_seconds < 1:
            raise ValueError("retention_seconds must be positive")
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock_path = self.path.with_suffix(self.path.suffix + ".lock")
        self.retention_seconds = retention_seconds
        self.clock = clock

    def _lock(self):
        self.lock_path.touch(exist_ok=True)
        return self.lock_path.open("r+")

    def _last_hash(self) -> str:
        if not self.path.exists():
            return ""
        lines = self.path.read_text(encoding="utf-8").splitlines()
        if not lines:
            return ""
        try:
            record = json.loads(lines[-1])
            return record["hash"]
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            raise AuditIntegrityError("audit sink has an invalid final record") from exc

    def append(
        self,
        event: str,
        *,
        subject: str,
        trajectory_id: str,
        policy_version: str,
        details: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not event.strip() or not subject.strip() or not trajectory_id.strip() or not policy_version.strip():
            raise ValueError("audit event, subject, trajectory_id, and policy_version are required")
        with self._lock() as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            previous_hash = self._last_hash()
            timestamp = self.clock()
            record = {
                "event": event,
                "subject": subject,
                "trajectory_id": trajectory_id,
                "policy_version": policy_version,
                "timestamp": timestamp,
                "details": redact(details or {}),
                "previous_hash": previous_hash,
            }
            if self.retention_seconds is not None:
                record["retention_until"] = timestamp + self.retention_seconds
            encoded = json.dumps(record, sort_keys=True, separators=(",", ":"))
            record["hash"] = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, sort_keys=True) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
            return record

    @staticmethod
    def _verify_records(lines: list[str]) -> list[dict[str, Any]]:
        previous_hash = ""
        records: list[dict[str, Any]] = []
        for line in lines:
            try:
                parsed = json.loads(line)
                if not isinstance(parsed, dict) or not isinstance(parsed.get("hash"), str):
                    raise ValueError
                observed = parsed["hash"]
                record = dict(parsed)
                del record["hash"]
                if record.get("previous_hash") != previous_hash:
                    raise AuditIntegrityError("audit chain is broken")
                encoded = json.dumps(record, sort_keys=True, separators=(",", ":"))
                if hashlib.sha256(encoded.encode("utf-8")).hexdigest() != observed:
                    raise AuditIntegrityError("audit record was modified")
                record["hash"] = observed
                records.append(record)
                previous_hash = observed
            except AuditIntegrityError:
                raise
            except (json.JSONDecodeError, TypeError, ValueError, KeyError) as exc:
                raise AuditIntegrityError("audit record is malformed") from exc
        return records

    def verify(self) -> bool:
        self._verify_records(self.path.read_text(encoding="utf-8").splitlines() if self.path.exists() else [])
        return True

    def retrieve(
        self,
        *,
        subject: str | None = None,
        trajectory_id: str | None = None,
        since: float | None = None,
        until: float | None = None,
        limit: int = 1000,
    ) -> list[dict[str, Any]]:
        if limit < 1:
            raise ValueError("limit must be positive")
        if since is not None and until is not None and since > until:
            raise ValueError("since must not be later than until")
        records = self._verify_records(self.path.read_text(encoding="utf-8").splitlines() if self.path.exists() else [])
        effective_since = since
        if effective_since is None and self.retention_seconds is not None:
            effective_since = self.clock() - self.retention_seconds
        selected = [
            record
            for record in records
            if (subject is None or record.get("subject") == subject)
            and (trajectory_id is None or record.get("trajectory_id") == trajectory_id)
            and (effective_since is None or record.get("timestamp", 0) >= effective_since)
            and (until is None or record.get("timestamp", 0) <= until)
        ]
        return selected[-limit:]


__all__ = ["AppendOnlyAuditSink", "AuditIntegrityError"]
