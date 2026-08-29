# Honest Agent — Client One-Pager

## The problem

Your agent can be excellent at reasoning and still be unsafe at the moment it calls a tool. As context fills, arguments become less grounded, and a write, send, migration, or external API call can execute before anyone checks whether the action is justified.

## The solution

Honest Agent is a runtime safety boundary that evaluates the proposed action before execution. It measures context pressure, applies deterministic action policy, routes higher-risk cases to a stronger verifier, pauses uncertainty for a human reviewer, and records the decision.

> **The agent can propose. Honest Agent decides whether the proposal is safe to execute. A human remains the final checkpoint for consequential work.**

## Why customers buy

| Customer outcome | How we create it |
|---|---|
| Fewer unsafe side effects | Block or pause unsupported, ambiguous, and irreversible actions before execution. |
| Faster security review | Produce structured evidence of policy, confidence, reviewer, and final decision. |
| Less integration work | Adopt through an OpenAI-compatible proxy, MCP, Python SDK, or IDE skill. |
| Lower operating cost | Keep fast verification on low-risk actions and escalate only where consequence justifies it. |

## Pilot offer

In two weeks, we instrument one workflow, define the action policy, run a baseline-versus-guard benchmark, configure reviewer checkpoints, and deliver a control-readiness report. The pilot is fixed-scope and does not require replacing the customer’s agent framework or model provider.

## Discovery questions

What actions can your agent perform today? Which ones are irreversible or externally visible? Where does human approval happen? What evidence would your security or compliance reviewer need before approving production use? How many bespoke guards are your platform engineers maintaining today?

## Close

Start with one consequential workflow. Keep your existing models and framework. Add a narrow, measurable pre-execution control boundary.
