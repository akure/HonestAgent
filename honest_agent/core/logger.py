from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from honest_agent.schemas.models import EvaluationRequest, GuardDecision, Trajectory, TrajectoryMetrics, TrajectoryStep


class TrajectoryLogger:
    def __init__(self, directory: str = "trajectories"):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def write(self, request: EvaluationRequest, decision: GuardDecision, step: int = 1, latency_ms: float = 0.0) -> Path:
        trajectory = Trajectory(
            agent_id=request.agent_id,
            system_instruction=request.system_instruction,
            trajectory=[TrajectoryStep(
                step=step,
                thought=request.thought,
                context_token_ratio=decision.context_token_ratio,
                confidence_score=decision.confidence_score,
                verifier_tier=decision.verifier_tier,
                tool_call={"tool_name": request.tool_name, "input": request.tool_input},
                human_checkpoint=decision.human_checkpoint,
                action_taken=decision.action_taken,
            )],
            metrics=TrajectoryMetrics(total_tokens=decision.context_token_count, latency_ms=latency_ms),
        )
        path = self.directory / f"{decision.trajectory_id}.json"
        path.write_text(trajectory.model_dump_json(indent=2), encoding="utf-8")
        return path
