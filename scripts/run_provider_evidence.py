from __future__ import annotations

import argparse
import asyncio
import json
import os
import time
from pathlib import Path

from honest_agent.core.evaluator import ContextEvaluator
from honest_agent.core.providers import ObservedVerifierProvider, OpenAICompatibleVerifierProvider, ResilientVerifierProvider
from honest_agent.schemas.models import EvaluationRequest, VerifierTier


async def run(endpoint: str, api_key: str, model: str, iterations: int) -> dict:
    request = EvaluationRequest(context="approved provider evidence request", tool_name="lookup", tool_input={"id": "synthetic-1"})
    telemetry = ContextEvaluator().evaluate(request.context, request.max_context_tokens, 0.8)
    observed = ObservedVerifierProvider(OpenAICompatibleVerifierProvider(endpoint, api_key, model))
    resilient = ResilientVerifierProvider(observed, max_retries=1)
    outcomes = []
    for _ in range(iterations):
        started = time.perf_counter()
        try:
            result = await resilient.verify(request, telemetry, VerifierTier.FAST)
            outcomes.append({"status": "PASS", "recommended_action": result.recommended_action.value, "latency_ms": (time.perf_counter() - started) * 1000})
        except asyncio.CancelledError:
            outcomes.append({"status": "CANCELLED"})
            raise
        except Exception as exc:
            outcomes.append({"status": "FAIL", "error_type": type(exc).__name__, "latency_ms": (time.perf_counter() - started) * 1000})
    metrics = observed.metrics.snapshot()
    await observed.provider.client.aclose()
    return {"status": "MEASURED", "iterations": iterations, "metrics": metrics, "outcomes": outcomes}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run approved live-provider evidence without printing secrets or payloads")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=5)
    args = parser.parse_args()
    endpoint = os.getenv("HONEST_AGENT_PROVIDER_ENDPOINT", "")
    api_key = os.getenv("HONEST_AGENT_PROVIDER_API_KEY", "")
    model = os.getenv("HONEST_AGENT_PROVIDER_MODEL", "")
    if not endpoint or not api_key or not model:
        report = {"status": "NOT_MEASURED", "reason": "HONEST_AGENT_PROVIDER_ENDPOINT, HONEST_AGENT_PROVIDER_API_KEY, and HONEST_AGENT_PROVIDER_MODEL are required", "secret_logged": False}
    else:
        report = asyncio.run(run(endpoint, api_key, model, max(1, args.iterations)))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.output} status={report['status']}")


if __name__ == "__main__":
    main()
