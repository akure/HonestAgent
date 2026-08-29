from __future__ import annotations

import argparse
import json
from pathlib import Path

from honest_agent.ops.control_report import build_control_readiness_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a sanitized Honest Agent control-readiness report")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--customer", default="synthetic-pilot")
    args = parser.parse_args()
    report = build_control_readiness_report(json.loads(args.input.read_text(encoding="utf-8")), customer=args.customer)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
