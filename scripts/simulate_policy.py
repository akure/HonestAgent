from __future__ import annotations

import argparse
import json
from pathlib import Path

from honest_agent.ops.pmf import simulate_policy
from honest_agent.schemas.models import EvaluationRequest


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulate Honest Agent policy without executing tools")
    parser.add_argument("input", type=Path, help="JSON array of EvaluationRequest objects")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    requests = [EvaluationRequest.model_validate(row) for row in json.loads(args.input.read_text(encoding="utf-8"))]
    simulation = simulate_policy(requests)
    args.output.write_text(simulation.model_dump_json(indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
