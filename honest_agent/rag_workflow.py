from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Mapping

from honest_agent.core.rag import RAGEvidenceBoundary, RetrievalChunk, RetrievalDecision
from honest_agent.sdk import HonestAgent
from honest_agent.schemas.models import DecisionStatus, EvaluationRequest, GuardDecision


@dataclass(frozen=True)
class RAGWorkflowResult:
    retrieval: RetrievalDecision
    decision: GuardDecision | None
    outcome: str
    executed: bool
    result: Any = None
    error: str | None = None


class RAGSafetyWorkflow:
    """Reference offline RAG flow; retrieval content never authorizes execution."""

    def __init__(self, agent: HonestAgent, boundary: RAGEvidenceBoundary):
        self.agent = agent
        self.boundary = boundary

    async def run(
        self,
        chunks: list[RetrievalChunk],
        request: EvaluationRequest,
        tool: Callable[[Mapping[str, Any]], Any | Awaitable[Any]],
        *,
        cited_evidence_ids: list[str] | tuple[str, ...] = (),
        high_impact: bool = False,
    ) -> RAGWorkflowResult:
        retrieval = self.boundary.inspect(chunks, high_impact=high_impact)
        if retrieval.outcome != "ALLOW":
            return RAGWorkflowResult(retrieval, None, "RETRIEVAL_PAUSED", False, error=";".join(retrieval.reasons))
        try:
            self.boundary.require_citation_coverage(retrieval.accepted_evidence_ids, cited_evidence_ids, high_impact=high_impact)
        except ValueError as exc:
            return RAGWorkflowResult(retrieval, None, "CITATION_BLOCKED", False, error=str(exc))
        evidence = {"evidence_ids": list(retrieval.accepted_evidence_ids), "cited_evidence_ids": list(cited_evidence_ids), "retrieval_outcome": retrieval.outcome}
        guarded_request = request.model_copy(update={"metadata": {**request.metadata, "evidence": evidence}})
        decision = await self.agent.check(guarded_request)
        if decision.status == DecisionStatus.PROCEED:
            return await self._execute(guarded_request, decision, tool, retrieval)
        return RAGWorkflowResult(retrieval, decision, decision.status.value, False)

    async def resume_after_approval(
        self,
        trajectory_id: str,
        tool: Callable[[Mapping[str, Any]], Any | Awaitable[Any]],
        retrieval: RetrievalDecision,
        *,
        reviewer: str,
    ) -> RAGWorkflowResult:
        request = self.agent.guard.pending_requests.get(trajectory_id)
        decision = await self.agent.guard.approve(trajectory_id, reviewer)
        if request is None:
            return RAGWorkflowResult(retrieval, decision, "APPROVAL_NOT_RESUMABLE", False, error="request is not available for resume")
        return await self._execute(request, decision, tool, retrieval)

    async def _execute(self, request: EvaluationRequest, decision: GuardDecision, tool: Callable[[Mapping[str, Any]], Any | Awaitable[Any]], retrieval: RetrievalDecision) -> RAGWorkflowResult:
        if decision.status != DecisionStatus.PROCEED or not decision.handoff_token or not self.agent.guard.validate_handoff(decision.handoff_token, request, decision.trajectory_id):
            return RAGWorkflowResult(retrieval, decision, "HANDOFF_BLOCKED", False, error="current handoff validation failed")
        try:
            result = tool(request.tool_input)
            if inspect.isawaitable(result):
                result = await result
        except Exception as exc:
            return RAGWorkflowResult(retrieval, decision, "PROVIDER_FAILURE", False, error=type(exc).__name__)
        return RAGWorkflowResult(retrieval, decision, DecisionStatus.PROCEED.value, True, result=result)


__all__ = ["RAGSafetyWorkflow", "RAGWorkflowResult"]
