from __future__ import annotations

import time
from typing import Any, Dict

from fastapi import FastAPI

from honest_agent.core.guardrail import HonestGuard
from honest_agent.core.logger import TrajectoryLogger
from honest_agent.interfaces.webhooks import build_router
from honest_agent.schemas.models import Config, EvaluationRequest


app = FastAPI(title="Honest Agent Runtime Gateway", version="0.1.0")
guard = HonestGuard()
logger = TrajectoryLogger(guard.config.trajectory_dir)
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


@app.post("/v1/chat/completions")
async def chat_completions(payload: Dict[str, Any]):
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
    return {
        "id": decision.trajectory_id,
        "object": "chat.completion",
        "choices": [{"index": 0, "message": {"role": "assistant", "content": "Guard approved simulated passthrough."}, "finish_reason": "stop"}],
        "honest_agent": {"status": decision.status.value, "decision": decision.model_dump(), "trajectory_path": str(path)},
    }

