# Honest Agent

**A pre-execution safety boundary for AI agent tool calls.**

Honest Agent helps teams prevent unsupported, ambiguous, or consequential agent actions from executing without an explicit control decision. It measures context pressure, applies deterministic action policy, routes higher-risk cases to verification, pauses uncertainty for human review, and records the decision as a structured trajectory.

> **Agents propose actions. Honest Agent evaluates whether they are safe to execute. Human reviewers remain the final checkpoint for consequential work.**

## Why it exists

AI infrastructure teams are increasingly responsible for agents that can read and change files, databases, production records, and external systems. Framework checkpoints and post-hoc logs are useful, but they do not by themselves provide an independent pre-execution decision or a durable explanation of why an action was allowed.

Honest Agent is designed for platform engineers operating agents in regulated or high-consequence workflows. It is framework-neutral and can be adopted through an OpenAI-compatible HTTP proxy, MCP, a Python decorator, or an IDE skill file.

## Who has this problem

The primary user is an AI platform engineer responsible for an agent that can write to a system of record, send an external message, deploy software, or spend money. The bottleneck is the last step before execution: ordinary agent frameworks can produce a plausible tool call, but the application still needs a deterministic, reviewable answer to whether the proposed action is grounded, authorized, and safe to execute.

## Why an agentic safety boundary

The agent remains responsible for proposing structured actions and gathering context. HonestAgent adds the verification capability that a prompt or post-hoc log cannot provide: deterministic policy classification, bounded verification, a human checkpoint for consequential actions, request-bound executor handoff, and an attributable trajectory. The primary success metric is interception **before execution** on an identical synthetic case set, with safe-action pass-through and latency reported separately.

## Original work and third-party components

The repository’s original work is the HonestAgent guardrail contract, policy and checkpoint flow, executor handoff validation, audit trajectory handling, integration adapters, evidence runners, tests, and release documentation. FastAPI, Pydantic, Uvicorn, HTTPX, pytest, optional provider SDKs, and other dependencies remain third-party components under their respective licenses. Their use does not imply endorsement, and their licenses must be preserved when applicable.

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

> **Permission notice:** This repository is not open source. The source is visible for evaluation, but copying, modifying, redistributing, hosting, embedding in a client deliverable, operating in production, or using HonestAgent commercially requires prior written permission under [`LICENSE`](LICENSE). See the [usage examples](docs/examples/README.md) for evaluation and licensed client-integration patterns.

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

## Usage examples

The repository includes practical, non-secret examples for the Python SDK, HTTP proxy, reviewer checkpoint flow, MCP integration, and a commercial pilot. Start with [`docs/examples/README.md`](docs/examples/README.md). Examples are illustrative: they do not grant a license, authorize production use, or replace a signed customer agreement.

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

The internal deterministic evaluation currently covers 40 synthetic cases: 20 labeled unsafe and 20 labeled safe. The latest run achieved 20/20 unsafe actions intercepted before execution, 20/20 safe actions allowed, zero false negatives, zero false positives, and p50/p95 guard latency of approximately 41.5/46.7 ms on the audit machine. The repository regression suite contains 83 passing tests. These results describe the included fixtures and offline verifier only; they are not a production guarantee or a measurement of live provider latency. Machine-readable requirement evidence and limitations are recorded in [`requirements_eval_results.json`](requirements_eval_results.json).

Run the reproducible evaluation with:

```bash
PYTHONPATH=. python3 tests/deep_eval.py
PYTHONPATH=. python3 tests/benchmark.py
```

## Project status

This is an early proprietary foundation with policy lifecycle, provider fault handling, durable checkpoint storage, reviewer authentication, executor handoff validation, platform-security boundaries, and release-gate controls implemented. The current release remains `NO-GO` for unrestricted production; see [`docs/release/conditional-pilot-evidence-sprint-plan_20260829_082500.md`](docs/release/conditional-pilot-evidence-sprint-plan_20260829_082500.md) and [`docs/operations/production-readiness.md`](docs/operations/production-readiness.md) before deploying beyond a controlled pilot.

## License and commercial permission

HonestAgent is proprietary software under the [HonestAgent Proprietary License](LICENSE). No default right is granted to copy, fork, modify, redistribute, host, resell, or use the Materials for client or revenue-generating work. A signed commercial license or services agreement is required for paid pilots, production deployment, managed service, consulting deliverables, and any other commercial use. The proposed source-available alternative is documented in the [HonestAgent Sustainable Use License draft](LICENSE-SUSTAINABLE-USE-DRAFT.md), which is for legal review and is not currently the governing license. See the [commercial licensing and enforcement model](docs/product/commercial-license-and-enforcement.md) and [`docs/product/business-model.md`](docs/product/business-model.md) for packaging hypotheses; neither is a license grant or binding offer.
