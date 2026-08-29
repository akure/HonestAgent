from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Any

from honest_agent.schemas.models import ActionClass, DecisionStatus, EvaluationRequest, ExecutionHandoff, GuardDecision


class HandoffError(ValueError):
    pass


def payload_hash(request: EvaluationRequest) -> str:
    body = json.dumps(
        {"tool_name": request.tool_name, "tool_input": request.tool_input},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


class HandoffSigner:
    def __init__(self, secret: str = "honest-agent-development-secret", ttl_seconds: int = 300, previous_secrets: list[str] | tuple[str, ...] = ()):
        if not secret:
            raise ValueError("handoff secret must not be empty")
        self.secret = secret.encode("utf-8")
        self.validation_secrets = (self.secret, *(item.encode("utf-8") for item in previous_secrets if item))
        self.ttl_seconds = ttl_seconds

    def issue(self, request: EvaluationRequest, decision: GuardDecision) -> ExecutionHandoff:
        if decision.status != DecisionStatus.PROCEED:
            raise HandoffError("only PROCEED decisions can issue an execution handoff")
        expires_at = int(time.time()) + self.ttl_seconds
        claims: dict[str, Any] = {
            "trajectory_id": decision.trajectory_id,
            "tool_name": request.tool_name,
            "payload_hash": payload_hash(request),
            "policy_version": decision.policy_version,
            "action_class": decision.action_class.value,
            "expires_at": expires_at,
        }
        encoded = base64.urlsafe_b64encode(json.dumps(claims, sort_keys=True, separators=(",", ":")).encode()).decode().rstrip("=")
        signature = hmac.new(self.secret, encoded.encode(), hashlib.sha256).hexdigest()
        token = f"{encoded}.{signature}"
        return ExecutionHandoff(**claims, token=token)

    def validate(self, token: str, request: EvaluationRequest, decision: GuardDecision) -> ExecutionHandoff:
        try:
            encoded, signature = token.split(".", 1)
            if not any(hmac.compare_digest(signature, hmac.new(key, encoded.encode(), hashlib.sha256).hexdigest()) for key in self.validation_secrets):
                raise HandoffError("invalid handoff signature")
            claims = json.loads(base64.urlsafe_b64decode(encoded + "===").decode("utf-8"))
            handoff = ExecutionHandoff(**claims, token=token)
        except (ValueError, json.JSONDecodeError, UnicodeDecodeError, KeyError) as exc:
            raise HandoffError("malformed handoff token") from exc
        if handoff.expires_at < int(time.time()):
            raise HandoffError("handoff expired")
        if decision.status != DecisionStatus.PROCEED:
            raise HandoffError("decision is not executable")
        if handoff.trajectory_id != decision.trajectory_id or handoff.tool_name != request.tool_name:
            raise HandoffError("handoff does not match decision")
        if handoff.payload_hash != payload_hash(request):
            raise HandoffError("handoff does not match tool payload")
        return handoff
