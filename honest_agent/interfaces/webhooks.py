from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException

from honest_agent.core.auth import AuthError, ReviewerAuthenticator
from honest_agent.core.guardrail import HonestGuard
from honest_agent.schemas.models import ApprovalRequest


def build_router(guard: HonestGuard, authenticator: ReviewerAuthenticator | None = None) -> APIRouter:
    router = APIRouter()
    auth = authenticator or ReviewerAuthenticator(
        secret=guard.config.reviewer_auth_secret,
        required=guard.config.require_reviewer_auth,
        ttl_seconds=guard.config.reviewer_token_ttl_seconds,
        previous_secrets=guard.config.reviewer_previous_secrets,
    )

    def reviewer_from_header(authorization: str | None) -> str | None:
        try:
            principal = auth.authenticate(authorization)
        except AuthError as exc:
            raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
        return principal.subject if principal else None

    @router.post("/approve/{trajectory_id}")
    async def approve(
        trajectory_id: str,
        request: ApprovalRequest,
        authorization: str | None = Header(default=None),
    ):
        reviewer = reviewer_from_header(authorization) or request.reviewer
        try:
            decision = await guard.approve(trajectory_id, reviewer)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="unknown trajectory") from exc
        return {"decision": decision.model_dump(), "reviewer": reviewer}

    @router.post("/reject/{trajectory_id}")
    async def reject(
        trajectory_id: str,
        request: ApprovalRequest,
        authorization: str | None = Header(default=None),
    ):
        reviewer = reviewer_from_header(authorization) or request.reviewer
        try:
            decision = await guard.reject(trajectory_id, reviewer)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="unknown trajectory") from exc
        return {"decision": decision.model_dump(), "reviewer": reviewer}

    return router
