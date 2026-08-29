from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable


SENSITIVE_KEYS = {"api_key", "authorization", "token", "secret", "password", "credential"}


def sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: "[REDACTED]" if key.lower() in SENSITIVE_KEYS else sanitize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    return value


def build_control_readiness_report(results: dict[str, Any], *, customer: str = "synthetic-pilot") -> dict[str, Any]:
    unsafe = int(results.get("unsafe_cases", 0))
    safe = int(results.get("safe_cases", 0))
    return sanitize({
        "report_version": "mvp-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "customer": customer,
        "scope": "pre-execution guardrail evaluation",
        "case_count": int(results.get("cases", unsafe + safe)),
        "metrics": {
            "unsafe_action_catch_rate": results.get("unsafe_catch_rate", results.get("unsafe_action_catch_rate")),
            "safe_action_pass_rate": results.get("safe_pass_rate"),
            "false_negatives": results.get("false_negatives", 0),
            "false_positives": results.get("false_positives", 0),
            "latency_p50_ms": results.get("latency_p50_ms", results.get("mean_guard_latency_ms")),
            "latency_p95_ms": results.get("latency_p95_ms"),
            "unsafe_cases": unsafe,
            "safe_cases": safe,
        },
        "routing": {
            "fast_cases": results.get("fast_cases", 0),
            "escalated_cases": results.get("escalated_cases", 0),
        },
        "limitations": [
            "Synthetic fixtures do not represent customer production traffic.",
            "Provider-backed verification and multi-process storage require separate validation.",
            "A passing benchmark does not authorize real side effects without executor handoff validation.",
        ],
        "recommendation": "Proceed to a controlled staging pilot only after customer policy review and executor integration tests.",
    })
