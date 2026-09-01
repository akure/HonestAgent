from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from honest_agent import ExtensionClass, ProtocolError, negotiate_version, parse_version, validate_extension
from honest_agent.schemas.workflow import IntentProvenance, SideEffectMode, ToolIntent


class ConformanceError(ValueError):
    pass


def _run_case(case: dict[str, Any]) -> dict[str, Any]:
    operation = case.get("operation")
    try:
        if operation == "negotiate_version":
            actual = negotiate_version(case["peer_versions"], supported_major=case["supported_major"], supported_minor=case["supported_minor"])
        elif operation == "parse_version":
            parsed = parse_version(case["value"])
            actual = f"{parsed.major}.{parsed.minor}"
        elif operation == "validate_extension":
            actual = validate_extension(case["name"], case["classification"])
        elif operation == "intent_hash":
            data = dict(case["intent"])
            data["expected_side_effect_mode"] = SideEffectMode(data["expected_side_effect_mode"])
            data["provenance"] = IntentProvenance(data["provenance"])
            actual = ToolIntent(**data).canonical_hash()
        else:
            raise ConformanceError(f"unsupported operation: {operation}")
    except (KeyError, TypeError, ValueError, ProtocolError) as exc:
        return {"id": case.get("id", "unknown"), "status": "ERROR", "error": type(exc).__name__}
    return {"id": case.get("id", "unknown"), "status": "PASS", "value": actual}


def run_manifest(path: str | Path) -> dict[str, Any]:
    manifest = json.loads(Path(path).read_text(encoding="utf-8"))
    if manifest.get("suite") != "honestagent.control.v1":
        raise ConformanceError("unsupported conformance suite")
    results = []
    failures = []
    for case in manifest.get("cases", []):
        actual = _run_case(case)
        expected = case.get("expected", {})
        matches = actual.get("status") == expected.get("status") and (
            (expected.get("status") == "ERROR" and actual.get("error") == expected.get("error"))
            or (expected.get("status") == "PASS" and (("value" not in expected) or actual.get("value") == expected.get("value")) and (("not_equal_to" not in expected) or actual.get("value") != expected.get("not_equal_to")))
        )
        result = {**actual, "expected": expected, "conformant": matches}
        results.append(result)
        if not matches:
            failures.append(result)
    return {"suite": manifest["suite"], "suite_version": manifest.get("suite_version"), "profile": manifest.get("profile"), "passed": len(results) - len(failures), "failed": len(failures), "conformant": not failures, "results": results}


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Run HonestAgent control-protocol conformance fixtures")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run_manifest(args.manifest)
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
    return 0 if result["conformant"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
