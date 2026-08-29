from __future__ import annotations

from fastapi import APIRouter, HTTPException

from honest_agent.core.guardrail import HonestGuard
from honest_agent.schemas.models import ApprovalRequest


def build_router(guard: HonestGuard) -> APIRouter:
    router = APIRouter()

    @router.post("/approve/{trajectory_id}")
    async def approve(trajectory_id: str, request: ApprovalRequest):
        try:
            decision = await guard.approve(trajectory_id, request.reviewer)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="unknown trajectory") from exc
        return {"decision": decision.model_dump()}

    @router.post("/reject/{trajectory_id}")
    async def reject(trajectory_id: str, request: ApprovalRequest):
        try:
            decision = await guard.reject(trajectory_id, request.reviewer)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="unknown trajectory") from exc
        return {"decision": decision.model_dump()}

    return router
