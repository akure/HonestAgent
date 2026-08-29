# Architecture Overview

Honest Agent is a **pre-execution control plane** for AI agent tool calls. It does not replace an agent framework, model provider, or executor. Its boundary is intentionally narrow: normalize a proposed action, measure context pressure, apply deterministic policy, obtain an independent verification result, and return a decision before the caller performs the side effect.

## Trust boundaries

| Boundary | Responsibility | Trust rule |
|---|---|---|
| Agent or application | Proposes a structured action and grounding context. | Treat proposals as untrusted input. |
| Honest Agent core | Evaluates telemetry, policy, verifier result, and checkpoint state. | Deterministic policy controls consequential actions. |
| Verifier provider | Supplies an independent confidence assessment. | Provider output never directly authorizes irreversible work. |
| Human reviewer | Resolves uncertain or consequential checkpoints. | Approval is explicit, attributable, and persisted. |
| Executor | Performs the real side effect. | Invoked only by the caller after `PROCEED` or approved resumption. |

## Package boundaries

```text
honest_agent/
├── core/
│   ├── evaluator.py    # deterministic context telemetry
│   ├── policy.py       # action classification and risk policy
│   ├── verifier.py     # provider protocol and offline verifier
│   ├── guardrail.py    # decision lifecycle and HITL state
│   └── logger.py       # trajectory persistence
├── schemas/
│   ├── models.py       # Pydantic implementation models
│   ├── config.py       # stable configuration import path
│   └── trajectory.py   # stable audit-contract import path
└── interfaces/
    ├── proxy.py        # FastAPI adapter
    ├── mcp_server.py   # MCP-style stdio adapter
    └── sdk.py          # Python decorator adapter
```

The `core` package must remain independent of FastAPI, MCP transport, and a particular LLM vendor. Interfaces are adapters only. Applications may replace `VerifierProvider`, `ActionPolicy`, `TrajectoryLogger`, and executor behavior without changing the normalized schema.

## Deployment modes

The default development mode runs the deterministic verifier and local JSON trajectory storage. A service mode runs the FastAPI adapter behind an application gateway. A production deployment should add authenticated reviewer identity, durable shared checkpoint storage, append-only audit storage, request authentication, and an explicit application policy registry before allowing real side effects.

## Non-goals

The project is not an observability suite, model router, sandbox runtime, autonomous executor, or multi-tenant SaaS control plane. It is deliberately useful as a composable safety boundary that can sit beside those systems.
