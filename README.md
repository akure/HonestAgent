# Honest Agent

**A pre-execution safety boundary for AI agent tool calls.**

Honest Agent helps teams prevent unsupported, ambiguous, or consequential agent actions from executing without an explicit control decision. It measures context pressure, applies deterministic action policy, routes higher-risk cases to verification, pauses uncertainty for human review, and records the decision as a structured trajectory.

> **Agents propose actions. Honest Agent evaluates whether they are safe to execute. Human reviewers remain the final checkpoint for consequential work.**

## Why it exists

AI infrastructure teams are increasingly responsible for agents that can read and change files, databases, production records, and external systems. Framework checkpoints and post-hoc logs are useful, but they do not by themselves provide an independent pre-execution decision or a durable explanation of why an action was allowed.

Honest Agent is designed for platform engineers operating agents in regulated or high-consequence workflows. It is framework-neutral and can be adopted through an OpenAI-compatible HTTP proxy, MCP, a Python decorator, or an IDE skill file.

## Core capabilities

| Capability | What it does |
|---|---|
| Context telemetry | Counts context tokens with a deterministic local evaluator and computes capacity ratio. |
| Deterministic policy | Classifies explicit and tool-name-based irreversible actions without delegating authorization to an LLM. |
| Risk-based verification | Keeps low-risk actions on a fast tier and escalates high-context or consequential actions. |
| Human checkpoint | Returns `PAUSED` for uncertain or consequential actions and supports attributable approval or rejection. |
| Audit trajectory | Persists confidence, verifier tier, context ratio, policy outcome, reviewer, and action status. |
| Multiple adapters | Exposes the same core contract through HTTP, MCP-style stdio, and Python SDK surfaces. |

## Quick start

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
PYTHONPATH=. pytest -q
PYTHONPATH=. python3 tests/deep_eval.py
```

The default path is deterministic and credential-free. It uses synthetic fixtures and does not execute real external side effects.

## Minimal usage

```python
from honest_agent.core.guardrail import HonestGuard
from honest_agent.schemas.trajectory import EvaluationRequest

request = EvaluationRequest(
    agent_id="example-agent",
    context="Invoice 123 is approved for reconciliation.",
    tool_name="lookup_invoice",
    tool_input={"invoice_id": 123},
)

decision = await HonestGuard().evaluate(request)
if decision.status.value == "PROCEED":
    execute_your_tool(request.tool_name, request.tool_input)
else:
    show_to_reviewer(decision.trajectory_path)
```

The guard evaluates and records; it does not own the customer’s executor.

## Integration paths

| Path | Best for | Documentation |
|---|---|---|
| HTTP proxy | Existing OpenAI-compatible clients and service boundaries | [`docs/integrations/proxy.md`](docs/integrations/proxy.md) |
| MCP | Claude Desktop, Cursor, and other MCP-capable clients | [`docs/integrations/mcp.md`](docs/integrations/mcp.md) |
| Python SDK | Applications that own their tool functions | [`docs/integrations/python-sdk.md`](docs/integrations/python-sdk.md) |
| IDE skill | Agent instructions and project-level guardrail conventions | [`SKILL.md`](SKILL.md) |

## Documentation

The documentation is organized by audience:

| Area | Contents |
|---|---|
| Architecture | Trust boundaries, package responsibilities, and deployment modes in [`docs/architecture/overview.md`](docs/architecture/overview.md). |
| Operations | Production controls and release gates in [`docs/operations/production-readiness.md`](docs/operations/production-readiness.md). |
| Product | Client one-pager and proposed commercial model in [`docs/product/client-one-pager.md`](docs/product/client-one-pager.md) and [`docs/product/business-model.md`](docs/product/business-model.md). |
| Development | Contribution and testing guidance in `docs/development/`. |

## Scope and safety

Honest Agent is not a general observability platform, model router, sandbox runtime, multi-tenant SaaS product, or autonomous executor. Version 0.1 is intended for local development and controlled pilots. Before allowing real side effects, deploy authentication, durable shared checkpoint storage, append-only audit storage, explicit application policy, reviewer authorization, data retention controls, and provider-failure tests.

The model verifier never directly authorizes an irreversible action. Deterministic policy and an explicit human checkpoint control that boundary.

## Evaluation status

The internal deterministic evaluation currently covers 40 synthetic cases: 20 labeled unsafe and 20 labeled safe. The latest verified run achieved 20/20 unsafe actions intercepted before execution, 20/20 safe actions allowed, zero false negatives, zero false positives, and p50/p95 guard latency of approximately 16.4/29.6 ms on the audit machine. The repository regression suite contains 80 passing tests. These results describe the included fixtures and offline verifier only; they are not a production guarantee or a measurement of live provider latency.

Run the reproducible evaluation with:

```bash
PYTHONPATH=. python3 tests/deep_eval.py
PYTHONPATH=. python3 tests/benchmark.py
```

## Project status

This is an early open-source foundation with policy lifecycle, provider fault handling, durable checkpoint storage, reviewer authentication, executor handoff validation, platform-security boundaries, and release-gate controls implemented. The current release remains `NO-GO` for unrestricted production; see [`docs/release/conditional-pilot-evidence-sprint-plan_20260829_082500.md`](docs/release/conditional-pilot-evidence-sprint-plan_20260829_082500.md) and [`docs/operations/production-readiness.md`](docs/operations/production-readiness.md) before deploying beyond a controlled pilot.

## License

Honest Agent is released under the Apache License 2.0. See [`LICENSE`](LICENSE).
