# Testing and Evaluation

Honest Agent uses layered tests because safety behavior and interface behavior fail differently.

## Test layers

| Layer | Purpose | Command |
|---|---|---|
| Unit and contract tests | Validate schemas, policy, evaluator, HITL, proxy, MCP, SDK, and audit behavior. | `PYTHONPATH=. pytest -q` |
| Adversarial tests | Probe false positives, provider failure, replay, concurrency, and zero-argument tools. | `PYTHONPATH=. pytest -q tests/test_adversarial.py tests/test_interfaces.py` |
| Original benchmark | Compare the pass-through baseline with the guardrail on the original scenario set. | `PYTHONPATH=. python3 tests/benchmark.py` |
| Deep evaluation | Produce a confusion matrix and p50/p95 latency over fixed synthetic cases. | `PYTHONPATH=. python3 tests/deep_eval.py` |

## Evaluation discipline

Never report a safety percentage without naming the fixture set, labeling policy, verifier configuration, and measurement boundary. The primary metric is interception **before execution**. A human-approved action counts as safely intercepted because it was paused before the irreversible boundary. False positives must be reported separately because an over-blocking guard can be operationally unusable.

## Adding a fixture

Each fixture should state the expected safety label, tool name, structured input, context, and whether an explicit irreversible declaration is present. Add at least one safe counterpart when adding a new unsafe pattern. Record the reason for the fixture in the changelog and rerun the same evaluation commands.
