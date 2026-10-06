"""LangSmith-shaped observability boundary for HonestAgent examples.

The local sample intentionally does not import LangSmith or make network calls.
In production, replace ``LocalTraceSink`` with a LangSmith callback/run tree,
while keeping the HonestAgent decision as the only execution authority.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True)
class TraceRecord:
    """Redacted, local trace record; it contains no credentials or raw prompts."""

    framework: str
    tool_name: str
    decision: str
    executed: bool
    trajectory_id: str | None
    error: str | None = None


class LocalTraceSink:
    """Offline sink with the same responsibility as an observability callback."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def record(self, result: Any, *, framework: str, tool_name: str) -> TraceRecord:
        decision = result.decision
        record = TraceRecord(
            framework=framework,
            tool_name=tool_name,
            decision=result.status,
            executed=bool(result.executed),
            trajectory_id=getattr(decision, "trajectory_id", None),
            error=result.error,
        )
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(asdict(record), sort_keys=True) + "\n")
        return record


def langsmith_metadata(record: TraceRecord) -> Mapping[str, Any]:
    """Return safe metadata for a LangSmith run/callback.

    Do not put raw retrieved documents, credentials, or unrestricted model
    messages into tracing metadata. The trace describes the control decision;
    it does not authorize a tool call.
    """

    return {
        "honestagent.framework": record.framework,
        "honestagent.tool": record.tool_name,
        "honestagent.decision": record.decision,
        "honestagent.executed": record.executed,
        "honestagent.trajectory_id": record.trajectory_id,
        "honestagent.error": record.error,
    }
