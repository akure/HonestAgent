#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from honest_agent.std8_benchmark import run_benchmark


parser = argparse.ArgumentParser(description="Run the credential-free STD-8 reproducible benchmark")
parser.add_argument("--output", default="test_reports/std8_benchmark.json")
args = parser.parse_args()
result = run_benchmark(args.output)
print(json.dumps(result, indent=2, sort_keys=True))
