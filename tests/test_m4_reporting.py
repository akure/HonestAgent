from __future__ import annotations

from honest_agent.ops.control_report import build_control_readiness_report


def test_control_report_preserves_metrics_and_redacts_sensitive_values():
    report = build_control_readiness_report(
        {
            "cases": 40,
            "unsafe_cases": 20,
            "safe_cases": 20,
            "unsafe_catch_rate": 1.0,
            "safe_pass_rate": 1.0,
            "false_negatives": 0,
            "false_positives": 0,
            "latency_p50_ms": 0.18,
            "latency_p95_ms": 0.24,
            "fast_cases": 22,
            "escalated_cases": 18,
            "api_key": "do-not-export",
        },
        customer="pilot-01",
    )
    assert report["customer"] == "pilot-01"
    assert report["metrics"]["unsafe_action_catch_rate"] == 1.0
    assert report["metrics"]["latency_p95_ms"] == 0.24
    assert "api_key" not in report
    assert report["limitations"]
