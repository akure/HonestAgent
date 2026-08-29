from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from uuid import uuid4

from pydantic import BaseModel, Field

from honest_agent.core.policy import ActionPolicy
from honest_agent.ops.control_report import sanitize
from honest_agent.schemas.models import ActionClass, DecisionStatus, EvaluationRequest


class PolicySimulationRow(BaseModel):
    request_id: str
    tool_name: str
    action_class: ActionClass
    policy_version: str
    would_status: DecisionStatus
    would_execute: bool
    reason: str


class PolicySimulation(BaseModel):
    simulation_id: str = Field(default_factory=lambda: str(uuid4()))
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    rows: list[PolicySimulationRow] = Field(default_factory=list)


def simulate_policy(requests: Iterable[EvaluationRequest], policy: ActionPolicy | None = None) -> PolicySimulation:
    policy = policy or ActionPolicy()
    rows: list[PolicySimulationRow] = []
    for request in requests:
        decision = policy.classify(request.tool_name, request.irreversible)
        if not request.tool_name.strip():
            status = DecisionStatus.REJECTED
            would_execute = False
            reason = "tool name is missing"
        elif decision.requires_escalation:
            status = DecisionStatus.PAUSED
            would_execute = False
            reason = decision.reason
        else:
            status = DecisionStatus.PROCEED
            would_execute = True
            reason = decision.reason
        rows.append(PolicySimulationRow(
            request_id=str(request.metadata.get("request_id", uuid4())),
            tool_name=request.tool_name,
            action_class=decision.action_class,
            policy_version=decision.policy_version,
            would_status=status,
            would_execute=would_execute,
            reason=reason,
        ))
    return PolicySimulation(rows=rows)


class PMFEvent(BaseModel):
    event_name: str
    customer_id: str
    workflow_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    value: dict[str, Any] = Field(default_factory=dict)


class PMFEventLog:
    def __init__(self, path: str = "test_reports/pmf_events.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: PMFEvent) -> None:
        safe_event = event.model_copy(update={"value": sanitize(event.value)})
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(safe_event.model_dump_json() + "\n")

    def read(self) -> list[PMFEvent]:
        if not self.path.exists():
            return []
        return [PMFEvent.model_validate_json(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]
