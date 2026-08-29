from __future__ import annotations

from pathlib import Path

from honest_agent.ops.pmf import PMFEvent, PMFEventLog, simulate_policy
from honest_agent.schemas.models import ActionClass, DecisionStatus, EvaluationRequest


def test_policy_simulation_never_executes_and_classifies_actions():
    simulation = simulate_policy([
        EvaluationRequest(tool_name="lookup_record", tool_input={"id": 1}, context="known record"),
        EvaluationRequest(tool_name="db_migrate", tool_input={"version": 2}, irreversible=True, context="migration request"),
    ])
    assert simulation.rows[0].action_class == ActionClass.READ_ONLY
    assert simulation.rows[0].would_status == DecisionStatus.PROCEED
    assert simulation.rows[0].would_execute is True
    assert simulation.rows[1].action_class == ActionClass.IRREVERSIBLE
    assert simulation.rows[1].would_status == DecisionStatus.PAUSED
    assert simulation.rows[1].would_execute is False


def test_pmf_event_log_round_trips(tmp_path: Path):
    log = PMFEventLog(str(tmp_path / "events.jsonl"))
    log.append(PMFEvent(event_name="protected_action", customer_id="c1", workflow_id="w1", value={"status": "PAUSED"}))
    events = log.read()
    assert len(events) == 1
    assert events[0].event_name == "protected_action"
    assert events[0].value["status"] == "PAUSED"
