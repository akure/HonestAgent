from __future__ import annotations

import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from honest_agent.core.guardrail import HonestGuard
from honest_agent.core.checkpoints import FileCheckpointStore
from honest_agent.core.logger import TrajectoryLogger
from honest_agent.interfaces.proxy import app
from honest_agent.schemas.models import Config, DecisionStatus, EvaluationRequest


def test_pending_checkpoint_survives_guard_restart(tmp_path: Path):
    async def run():
        checkpoint_path = tmp_path / "checkpoints.json"
        trajectory_dir = tmp_path / "trajectories"
        config = Config(checkpoint_path=str(checkpoint_path), trajectory_dir=str(trajectory_dir))
        request = EvaluationRequest(context="migration approved by policy", tool_name="db_migrate", tool_input={"version": 2}, irreversible=True)

        first = HonestGuard(config=config)
        pending = await first.evaluate(request)
        assert pending.status == DecisionStatus.PAUSED

        second = HonestGuard(config=config)
        approved = await second.approve(pending.trajectory_id, "reviewer@example.com")
        assert approved.status == DecisionStatus.PROCEED
        assert approved.human_checkpoint.reviewer == "reviewer@example.com"

        persisted = json.loads(Path(approved.trajectory_path).read_text(encoding="utf-8"))
        assert persisted["trajectory"][0]["human_checkpoint"]["status"] == "APPROVED"
        stored = FileCheckpointStore(str(checkpoint_path)).get_resolved(pending.trajectory_id)
        assert stored is not None
        assert stored.status == DecisionStatus.PROCEED

    asyncio.run(run())


def test_webhook_routes_are_registered_separately():
    paths = {route.path for route in app.routes}
    assert "/approve/{trajectory_id}" in paths
    assert "/reject/{trajectory_id}" in paths
