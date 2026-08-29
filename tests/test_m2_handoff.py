from __future__ import annotations

import asyncio
from pathlib import Path

from honest_agent.core.guardrail import HonestGuard
from honest_agent.schemas.models import Config, DecisionStatus, EvaluationRequest


def test_handoff_is_bound_to_payload_and_trajectory(tmp_path: Path):
    async def run():
        config = Config(trajectory_dir=str(tmp_path / "trajectories"), checkpoint_path=str(tmp_path / "checkpoints.json"))
        guard = HonestGuard(config=config)
        request = EvaluationRequest(context="known data", tool_name="lookup_record", tool_input={"id": 42})
        decision = await guard.evaluate(request)
        assert decision.status == DecisionStatus.PROCEED
        assert decision.handoff_token
        assert guard.validate_handoff(decision.handoff_token, request, decision.trajectory_id)

        changed = request.model_copy(update={"tool_input": {"id": 43}})
        assert not guard.validate_handoff(decision.handoff_token, changed, decision.trajectory_id)
        assert not guard.validate_handoff(decision.handoff_token, request, "different-trajectory")

    asyncio.run(run())


def test_paused_action_cannot_issue_handoff(tmp_path: Path):
    async def run():
        config = Config(trajectory_dir=str(tmp_path / "trajectories"), checkpoint_path=str(tmp_path / "checkpoints.json"))
        guard = HonestGuard(config=config)
        request = EvaluationRequest(context="unknown dependency", tool_name="db_migrate", tool_input={"version": 1}, irreversible=True)
        decision = await guard.evaluate(request)
        assert decision.status == DecisionStatus.PAUSED
        assert decision.handoff_token is None

    asyncio.run(run())
