from __future__ import annotations

import json
import os
import time
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from honest_agent.core.executor import ExecutionBlocked, ExecutorGateway
from honest_agent.core.guardrail import HonestGuard
from honest_agent.core.logger import TrajectoryLogger
from honest_agent.core.secrets import load_secret_config
from honest_agent.core.security import SSRFBlocked, validate_deployment_security
from honest_agent.interfaces.upstream import UpstreamClient, UpstreamError
from honest_agent.interfaces.webhooks import build_router
from honest_agent.schemas.models import Config, EvaluationRequest


app = FastAPI(title="Honest Agent Runtime Gateway", version="0.1.0")


@app.middleware("http")
async def enforce_request_size(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            if int(content_length) > _runtime_config.max_payload_bytes:
                return JSONResponse(status_code=413, content={"detail": "request payload exceeds configured limit"})
        except ValueError:
            return JSONResponse(status_code=400, content={"detail": "invalid content-length header"})
    return await call_next(request)
_secret_config = load_secret_config()
_runtime_config = Config(
    environment=_secret_config.environment,
    allow_private_upstream=os.getenv("HONEST_AGENT_ALLOW_PRIVATE_UPSTREAM", "false").lower() == "true",
    max_payload_bytes=int(os.getenv("HONEST_AGENT_MAX_PAYLOAD_BYTES", "1000000")),
    handoff_secret=_secret_config.handoff_secret,
    handoff_previous_secrets=list(_secret_config.handoff_previous_secrets),
    reviewer_auth_secret=_secret_config.reviewer_auth_secret,
    reviewer_previous_secrets=list(_secret_config.reviewer_previous_secrets),
    require_reviewer_auth=_secret_config.managed,
)
validate_deployment_security(_runtime_config.environment, _runtime_config.allow_private_upstream, _runtime_config.max_payload_bytes)
guard = HonestGuard(config=_runtime_config)
logger = TrajectoryLogger(guard.config.trajectory_dir)
upstream = UpstreamClient(os.getenv("HONEST_AGENT_UPSTREAM_URL"), allow_private_network=_runtime_config.allow_private_upstream)
app.include_router(build_router(guard))


def _request_from_chat(payload: Dict[str, Any]) -> EvaluationRequest:
    messages = payload.get("messages", [])
    context = "\n".join(str(message.get("content", "")) for message in messages)
    metadata = payload.get("honest_agent", {}) or {}
    tool = metadata.get("tool_name", "chat_completion")
    tool_input = metadata.get("tool_input", {"model": payload.get("model", "unknown")})
    return EvaluationRequest(
        agent_id=metadata.get("agent_id", "openai-client"),
        system_instruction=next((m.get("content", "") for m in messages if m.get("role") == "system"), ""),
        thought=metadata.get("thought", ""),
        context=context,
        max_context_tokens=int(metadata.get("max_context_tokens", 128000)),
        tool_name=tool,
        tool_input=tool_input,
        irreversible=bool(metadata.get("irreversible", False)),
        metadata=metadata,
    )


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/guard")
async def evaluate(request: EvaluationRequest):
    started = time.perf_counter()
    decision = await guard.evaluate(request)
    path = logger.write(request, decision, latency_ms=(time.perf_counter() - started) * 1000)
    return {"decision": decision.model_dump(), "trajectory_path": str(path)}


@app.post("/v1/execute")
async def execute(payload: Dict[str, Any]):
    """Execute only when a previously issued handoff validates at this boundary."""
    if len(json.dumps(payload, separators=(",", ":"))) > guard.config.max_payload_bytes:
        raise HTTPException(status_code=413, detail="request payload exceeds configured limit")
    try:
        request = EvaluationRequest.model_validate(payload.get("request", {}))
        trajectory_id = str(payload["trajectory_id"])
        handoff_token = payload.get("handoff_token")
        upstream_payload = payload.get("upstream_payload", {})
        result = await ExecutorGateway(guard, upstream).execute(request, handoff_token, trajectory_id, upstream_payload)
    except (KeyError, ValueError, ExecutionBlocked) as exc:
        raise HTTPException(status_code=403, detail="execution blocked: invalid or missing handoff") from exc
    except UpstreamError as exc:
        raise HTTPException(status_code=502, detail="upstream execution failed") from exc
    return {"result": result, "trajectory_id": trajectory_id}


@app.post("/v1/chat/completions")
async def chat_completions(payload: Dict[str, Any]):
    if len(json.dumps(payload, separators=(",", ":"))) > guard.config.max_payload_bytes:
        raise HTTPException(status_code=413, detail="request payload exceeds configured limit")
    request = _request_from_chat(payload)
    started = time.perf_counter()
    decision = await guard.evaluate(request)
    path = logger.write(request, decision, latency_ms=(time.perf_counter() - started) * 1000)
    if decision.status.value != "PROCEED":
        return {
            "id": decision.trajectory_id,
            "object": "honest_agent.guardrail_decision",
            "choices": [],
            "honest_agent": {"status": decision.status.value, "decision": decision.model_dump(), "trajectory_path": str(path)},
        }
    metadata = payload.get("honest_agent", {}) or {}
    handoff_token = metadata.get("handoff_token")
    trajectory_id = metadata.get("trajectory_id", decision.trajectory_id)
    forwarded = dict(payload)
    forwarded.pop("honest_agent", None)
    try:
        response = await ExecutorGateway(guard, upstream).execute(request, handoff_token, trajectory_id, forwarded)
    except ExecutionBlocked:
        return {
            "id": decision.trajectory_id,
            "object": "honest_agent.execution_blocked",
            "choices": [],
            "honest_agent": {"status": "EXECUTION_BLOCKED", "decision": decision.model_dump(), "trajectory_path": str(path)},
        }
    except UpstreamError as exc:
        return {"id": decision.trajectory_id, "object": "honest_agent.upstream_error", "choices": [], "error": str(exc), "honest_agent": {"status": "UPSTREAM_ERROR", "decision": decision.model_dump(), "trajectory_path": str(path)}}
    response["honest_agent"] = {"status": decision.status.value, "decision": decision.model_dump(), "trajectory_path": str(path)}
    return response
