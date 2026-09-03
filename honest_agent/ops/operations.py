from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True)
class AlertRule:
    name: str
    state: str
    threshold: int


@dataclass(frozen=True)
class OperationalAlert:
    name: str
    severity: str
    observed: int
    threshold: int
    state: str
    message: str


def evaluate_alerts(snapshot: Mapping[str, Any], rules: tuple[AlertRule, ...] = ()) -> list[OperationalAlert]:
    states = snapshot.get("intents", {}).get("by_state", {})
    if not isinstance(states, Mapping):
        raise ValueError("snapshot intent state counts are malformed")
    alerts: list[OperationalAlert] = []
    for rule in rules:
        if not rule.name.strip() or not rule.state.strip() or rule.threshold < 1:
            raise ValueError("alert rules require a name, state, and positive threshold")
        observed = states.get(rule.state, 0)
        if not isinstance(observed, int) or observed < 0:
            raise ValueError("snapshot intent state counts must be non-negative integers")
        if observed >= rule.threshold:
            severity = "critical" if rule.state in {"UNKNOWN_AFTER_CRASH", "FAILED"} else "warning"
            alerts.append(OperationalAlert(rule.name, severity, observed, rule.threshold, rule.state, f"{rule.state} count reached {observed} (threshold {rule.threshold})"))
    return alerts


def build_operational_dashboard(snapshot: Mapping[str, Any], alerts: list[OperationalAlert] | None = None) -> dict[str, Any]:
    intents = snapshot.get("intents", {})
    controls = snapshot.get("controls", [])
    if not isinstance(intents, Mapping) or not isinstance(controls, list):
        raise ValueError("operational snapshot is malformed")
    return {
        "dashboard_version": "std10d-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "intents": {"total": intents.get("total", 0), "by_state": dict(intents.get("by_state", {}))},
        "controls": [
            {"scope": item.get("scope"), "enabled": bool(item.get("enabled")), "quota": item.get("quota")}
            for item in controls
            if isinstance(item, Mapping)
        ],
        "alerts": [alert.__dict__ for alert in (alerts or [])],
        "limitations": [
            "This dashboard is a read-only local operational snapshot.",
            "Alert evaluation does not page an external incident system.",
            "Kill-switch activation still requires an explicitly authorized control path.",
        ],
    }


__all__ = ["AlertRule", "OperationalAlert", "evaluate_alerts", "build_operational_dashboard"]
