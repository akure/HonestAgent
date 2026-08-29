from __future__ import annotations

import asyncio
import time
import re
from pathlib import Path
from typing import Dict, Optional

from honest_agent.core.checkpoints import CheckpointStore, FileCheckpointStore
from honest_agent.core.evaluator import ContextEvaluator
from honest_agent.core.handoff import HandoffError, HandoffSigner
from honest_agent.core.logger import TrajectoryLogger
from honest_agent.core.policy import ActionPolicy
from honest_agent.core.policy_registry import PolicyRegistry
from honest_agent.core.verifier import VerifierEngine
from honest_agent.schemas.models import (
    CheckpointStatus,
    Config,
    DecisionStatus,
    EvaluationRequest,
    GuardDecision,
    HumanCheckpoint,
    RecommendedAction,
    RiskLevel,
    VerifierTier,
)


class HonestGuard:
    def __init__(self, config: Config | None = None, verifier: VerifierEngine | None = None, logger: TrajectoryLogger | None = None, policy: ActionPolicy | None = None, store: CheckpointStore | None = None, policy_registry: PolicyRegistry | None = None):
        self.config = config or Config()
        self.evaluator = ContextEvaluator()
        self.verifier = verifier or VerifierEngine()
        self.logger = logger or TrajectoryLogger(self.config.trajectory_dir)
        self.store = store or FileCheckpointStore(self.config.checkpoint_path, self.config.checkpoint_retention_seconds)
        self.signer = HandoffSigner(self.config.handoff_secret, self.config.handoff_ttl_seconds, self.config.handoff_previous_secrets)
        self.policy_registry = policy_registry
        self.policy = policy or (policy_registry.get_policy() if policy_registry else ActionPolicy())
        self.check_count = 0
        self.pending: Dict[str, GuardDecision] = {}
        self.pending_requests: Dict[str, EvaluationRequest] = {}
        self.resolved: Dict[str, GuardDecision] = {}
        self._lock = asyncio.Lock()

    def activate_policy(self, version: str, actor: str) -> ActionPolicy:
        if self.policy_registry is None:
            raise ValueError("policy registry is not configured")
        self.policy = self.policy_registry.activate(version, actor)
        return self.policy

    def rollback_policy(self, version: str, actor: str) -> ActionPolicy:
        if self.policy_registry is None:
            raise ValueError("policy registry is not configured")
        self.policy = self.policy_registry.rollback(version, actor)
        return self.policy

    def _tier_for(self, request: EvaluationRequest, ratio: float) -> VerifierTier:
        policy = self.policy.classify(request.tool_name, request.irreversible)
        return VerifierTier.ESCALATED if ratio >= self.config.escalation_ratio or policy.requires_escalation else VerifierTier.FAST

    async def evaluate(self, request: EvaluationRequest) -> GuardDecision:
        started = time.perf_counter()
        policy = self.policy.classify(request.tool_name, request.irreversible)
        async with self._lock:
            if self.config.max_checks is not None and self.check_count >= self.config.max_checks:
                return GuardDecision(
                    status=DecisionStatus.CAP_EXCEEDED,
                    confidence_score=0.0,
                    verifier_tier=VerifierTier.FAST,
                    hallucination_risk="HIGH",
                    action_class=policy.action_class,
                    policy_version=policy.policy_version,
                    reasoning="configured check-count cap exceeded",
                    recommended_action=RecommendedAction.REQUIRE_HUMAN_CHECKPOINT,
                    action_taken="REJECTED_BEFORE_EXECUTION",
                )
            self.check_count += 1

        telemetry = self.evaluator.evaluate(request.context, request.max_context_tokens, self.config.escalation_ratio)
        tier = self._tier_for(request, telemetry.ratio)
        try:
            result = await self.verifier.verify(request, telemetry, tier)
        except Exception as exc:
            decision = GuardDecision(
                status=DecisionStatus.REJECTED,
                confidence_score=0.0,
                verifier_tier=tier,
                hallucination_risk=RiskLevel.HIGH,
                action_class=policy.action_class,
                policy_version=policy.policy_version,
                reasoning=f"verification unavailable; failing closed: {type(exc).__name__}",
                recommended_action=RecommendedAction.REQUIRE_HUMAN_CHECKPOINT,
                context_token_count=telemetry.token_count,
                context_token_ratio=telemetry.ratio,
                action_taken="REJECTED_VERIFIER_FAILURE",
            )
            self.resolved[decision.trajectory_id] = decision
            decision.trajectory_path = str(self.logger.write(request, decision))
            self.store.put_resolved(request, decision)
            return decision
        needs_checkpoint = (
            result.confidence_score < self.config.confidence_threshold
            or result.recommended_action == RecommendedAction.REQUIRE_HUMAN_CHECKPOINT
            or policy.requires_escalation
        )
        if not request.tool_name.strip():
            status = DecisionStatus.REJECTED
            action = "REJECTED_INVALID_ACTION"
            checkpoint = None
        elif needs_checkpoint:
            status = DecisionStatus.PAUSED
            action = "PAUSED_FOR_HUMAN_CHECKPOINT"
            checkpoint = HumanCheckpoint(status=CheckpointStatus.PENDING)
        else:
            status = DecisionStatus.PROCEED
            action = "PROCEEDED"
            checkpoint = None
        decision = GuardDecision(
            status=status,
            confidence_score=result.confidence_score,
            verifier_tier=result.verifier_tier,
            hallucination_risk=result.hallucination_risk,
            action_class=policy.action_class,
            policy_version=policy.policy_version,
            reasoning=f"{result.reasoning}; policy={policy.reason}",
            recommended_action=result.recommended_action,
            human_checkpoint=checkpoint,
            context_token_count=telemetry.token_count,
            context_token_ratio=telemetry.ratio,
            action_taken=action,
        )
        if status == DecisionStatus.PAUSED:
            self.pending[decision.trajectory_id] = decision
            self.pending_requests[decision.trajectory_id] = request
            self.store.put_pending(request, decision)
        else:
            if status == DecisionStatus.PROCEED:
                decision.handoff_token = self.signer.issue(request, decision).token
            self.store.put_resolved(request, decision)
        decision.reasoning = f"{decision.reasoning}; latency_ms={(time.perf_counter() - started) * 1000:.3f}"
        decision.trajectory_path = str(self.logger.write(request, decision))
        return decision

    async def approve(self, trajectory_id: str, reviewer: str) -> GuardDecision:
        return await self._resolve(trajectory_id, reviewer, CheckpointStatus.APPROVED, DecisionStatus.PROCEED, "APPROVED_AND_READY_TO_EXECUTE")

    async def reject(self, trajectory_id: str, reviewer: str) -> GuardDecision:
        return await self._resolve(trajectory_id, reviewer, CheckpointStatus.REJECTED, DecisionStatus.REJECTED, "REJECTED_BY_HUMAN")

    async def _resolve(self, trajectory_id: str, reviewer: str, checkpoint_status: CheckpointStatus, status: DecisionStatus, action: str) -> GuardDecision:
        async with self._lock:
            if trajectory_id in self.resolved:
                return self.resolved[trajectory_id]
            stored_resolved = self.store.get_resolved(trajectory_id)
            if stored_resolved is not None:
                self.resolved[trajectory_id] = stored_resolved
                return stored_resolved
            if trajectory_id in self.pending:
                decision = self.pending.pop(trajectory_id)
                request = self.pending_requests.pop(trajectory_id)
            else:
                stored_pending = self.store.get_pending(trajectory_id)
                if stored_pending is None:
                    raise KeyError(trajectory_id)
                request, decision = stored_pending
            decision.status = status
            decision.action_taken = action
            decision.human_checkpoint = HumanCheckpoint(status=checkpoint_status, reviewer=reviewer)
            if status == DecisionStatus.PROCEED:
                decision.handoff_token = self.signer.issue(request, decision).token
            winner = self.store.resolve_pending(request, decision)
            self.resolved[trajectory_id] = winner
            if winner.model_dump() == decision.model_dump():
                decision.trajectory_path = str(self.logger.write(request, decision))
            return winner

    def validate_handoff(self, token: str, request: EvaluationRequest, trajectory_id: str) -> bool:
        decision = self.resolved.get(trajectory_id) or self.store.get_resolved(trajectory_id)
        if decision is None:
            return False
        try:
            self.signer.validate(token, request, decision)
        except HandoffError:
            return False
        return True

