---
name: hackathon-agent-engineering
description: Use when designing or building the agent solution itself for the micro1 hackathon — choosing which agent capabilities to use (context, tools, memory, verification, skills, orchestration), and when adding any action that could affect a real person or system. This is the highest-weighted rubric category (30/100), so load this before writing agent code and re-load whenever adding a new capability.
---

# Agent Solution & Engineering (Gate 2/4 — 30/100 points)

Judges score design choices by whether each one **improves the solution and helps the agent reach the goal reliably** — not by how many components you bolted on. "Purposeful choices matter more than the number of components" is explicit in the brief. Every capability you add must trace back to a specific failure mode from `problem-framing`.

## Capability menu — pick only what the problem needs

| Capability | Use when | Skip when |
|---|---|---|
| **Better context** | The agent's errors trace to missing/wrong info at inference time | Context is already sufficient; adding more just adds noise |
| **Better tools** | The agent needs to *do* something (query, compute, act) it can't do via text alone | A single well-scoped prompt already gets it right |
| **Memory** | Important information must carry across turns/episodes (e.g. prior translation choices, prior candidate notes) | The task is single-shot with no state to carry |
| **Verification** | Errors are costly and detectable before reaching the user | Verification cost exceeds the value of catching rare errors |
| **Skills** | The task needs deep, narrow expertise reused across runs | The task is broad/one-off; a skill would be dead weight |
| **Orchestration (multi-agent)** | Sub-tasks are genuinely independent or benefit from separation of concerns/roles | A single agent with good tools already handles it — orchestration for its own sake dilutes reliability |

For each capability you add, write one sentence: *"Added X because [specific failure mode observed], evidence: [what you saw]."* This sentence becomes the changelog entry — don't discard it.

## Deterministic vs. model judgment (Ground Rule 04/05 — do not skip)

Any of the following must be deterministic code, not LLM judgment, with a human-approval checkpoint before the action executes:
- Consequential or irreversible actions (sending something externally, writing to a system of record, spending money).
- Anything that could significantly affect a real person's outcome (a hire/no-hire signal, a credit or valuation number, a medical or safety-adjacent decision).

Pattern: agent reasons → agent proposes an action as structured data → deterministic validator checks it against explicit rules → human approval gate → deterministic executor performs the action. The LLM never directly triggers the consequential step. Sandbox or simulate the action during development and demo; do not depend on live external side effects for judging.

## Working notes as you build

- Keep a running list of what you tried and reverted — this is required later for the changelog's "removed experiments" entries and the Hot Take criterion (5 pts: turn one observed failure mode into a lesson).
- Prefer the smallest capability set that produces the improvement; over-orchestration reads as unreliable, not impressive, to judges who are explicitly told to weight purposefulness over component count.
- Every design choice should be traceable to a sentence in `problem-framing`'s bottleneck description — if you can't trace it, question whether it belongs.
