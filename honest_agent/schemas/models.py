from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class VerifierTier(str, Enum):
    FAST = "fast"
    ESCALATED = "escalated"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RecommendedAction(str, Enum):
    PROCEED = "PROCEED"
    SUMMARIZE_CONTEXT = "SUMMARIZE_CONTEXT"
    REQUIRE_HUMAN_CHECKPOINT = "REQUIRE_HUMAN_CHECKPOINT"


class DecisionStatus(str, Enum):
    PROCEED = "PROCEED"
    PAUSED = "PAUSED"
    REJECTED = "REJECTED"
    CAP_EXCEEDED = "CAP_EXCEEDED"


class CheckpointStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class EvaluationRequest(BaseModel):
    agent_id: str = "demo-agent"
    system_instruction: str = ""
    thought: str = ""
    context: str = ""
    max_context_tokens: int = Field(default=128000, gt=0)
    tool_name: str
    tool_input: Dict[str, Any] = Field(default_factory=dict)
    irreversible: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class VerifierResult(BaseModel):
    confidence_score: float = Field(ge=0.0, le=1.0)
    has_sufficient_context: bool
    hallucination_risk: RiskLevel
    reasoning: str
    recommended_action: RecommendedAction
    verifier_tier: VerifierTier


class HumanCheckpoint(BaseModel):
    status: CheckpointStatus
    reviewer: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class GuardDecision(BaseModel):
    status: DecisionStatus
    confidence_score: float = Field(ge=0.0, le=1.0)
    verifier_tier: VerifierTier
    hallucination_risk: RiskLevel
    reasoning: str
    recommended_action: RecommendedAction
    human_checkpoint: Optional[HumanCheckpoint] = None
    trajectory_id: str = Field(default_factory=lambda: str(uuid4()))
    trajectory_path: Optional[str] = None
    context_token_count: int = 0
    context_token_ratio: float = 0.0
    action_taken: str


class TrajectoryStep(BaseModel):
    step: int
    thought: str = ""
    context_token_ratio: float = Field(ge=0.0, le=1.0)
    confidence_score: float = Field(ge=0.0, le=1.0)
    verifier_tier: VerifierTier
    tool_call: Dict[str, Any]
    human_checkpoint: Optional[HumanCheckpoint] = None
    tool_response: Optional[str] = None
    action_taken: str


class TrajectoryMetrics(BaseModel):
    total_tokens: int = 0
    latency_ms: float = 0.0
    eval_cost_usd: float = 0.0


class Trajectory(BaseModel):
    agent_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    system_instruction: str = ""
    trajectory: List[TrajectoryStep] = Field(default_factory=list)
    metrics: TrajectoryMetrics = Field(default_factory=TrajectoryMetrics)


class ApprovalRequest(BaseModel):
    reviewer: str = Field(min_length=1)


class Config(BaseModel):
    confidence_threshold: float = Field(default=0.85, ge=0.0, le=1.0)
    escalation_ratio: float = Field(default=0.80, ge=0.0, le=1.0)
    max_checks: Optional[int] = Field(default=None, gt=0)
    trajectory_dir: str = "trajectories"
