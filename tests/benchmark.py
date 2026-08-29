from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path

from honest_agent.core.guardrail import HonestGuard
from honest_agent.schemas.models import Config, DecisionStatus, EvaluationRequest
from tests.fixtures import CASES


def baseline(case):
    return {"executed": True, "unsafe": bool(case["unsafe"]), "status": "PROCEEDED"}


async def run_solution(case, guard):
    request = EvaluationRequest(
        agent_id="benchmark-agent",
        context=case["context"],
        max_context_tokens=case.get("max_context_tokens", 128000),
        tool_name=case["tool_name"],
        tool_input=case["tool_input"],
        irreversible=case["irreversible"],
    )
    initial = await guard.evaluate(request)
    initial_status = initial.status
    if case.get("approved") and initial.status == DecisionStatus.PAUSED:
        final = await guard.approve(initial.trajectory_id, "benchmark-reviewer")
    else:
        final = initial
    return initial_status, final


async def main():
    baseline_results = [baseline(case) for case in CASES]
    guard = HonestGuard(Config(max_checks=11))
    started = time.perf_counter()
    solution_results = [await run_solution(case, guard) for case in CASES]
    elapsed_ms = (time.perf_counter() - started) * 1000
    baseline_caught = sum(1 for result in baseline_results if result["unsafe"] and not result["executed"])
    solution_caught = sum(1 for case, result in zip(CASES, solution_results) if case["unsafe"] and result[0] != DecisionStatus.PROCEED)
    result = {
        "cases": len(CASES),
        "baseline_unsafe_caught": baseline_caught,
        "solution_unsafe_caught": solution_caught,
        "unsafe_cases": sum(1 for case in CASES if case["unsafe"]),
        "unsafe_action_catch_rate": solution_caught / sum(1 for case in CASES if case["unsafe"]),
        "mean_guard_latency_ms": elapsed_ms / len(CASES),
        "results": [{"id": case["id"], "pre_execution_status": initial_status.value, "final_status": decision.status.value, "tier": decision.verifier_tier.value, "confidence": decision.confidence_score} for case, (initial_status, decision) in zip(CASES, solution_results)],
    }
    Path("benchmark_results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
