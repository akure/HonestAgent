from __future__ import annotations

import asyncio
import json
import sys
from typing import Any, Dict

from honest_agent.core.guardrail import HonestGuard
from honest_agent.schemas.models import EvaluationRequest


guard = HonestGuard()


async def verify_context_health(arguments: Dict[str, Any]) -> Dict[str, Any]:
    request = EvaluationRequest(**arguments)
    return (await guard.evaluate(request)).model_dump()


async def trigger_human_checkpoint(arguments: Dict[str, Any]) -> Dict[str, Any]:
    trajectory_id = arguments["trajectory_id"]
    reviewer = arguments["reviewer"]
    decision = await guard.approve(trajectory_id, reviewer) if arguments.get("decision", "APPROVED") == "APPROVED" else await guard.reject(trajectory_id, reviewer)
    return decision.model_dump()


async def serve_stdio() -> None:
    for line in sys.stdin:
        if not line.strip():
            continue
        message = json.loads(line)
        method = message.get("method")
        arguments = message.get("arguments", {})
        if method == "verify_context_health":
            result = await verify_context_health(arguments)
        elif method == "trigger_human_checkpoint":
            result = await trigger_human_checkpoint(arguments)
        else:
            result = {"error": f"unknown method: {method}"}
        sys.stdout.write(json.dumps(result) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    asyncio.run(serve_stdio())
