---
name: micro1-hackathon-orchestrator
description: Load FIRST for any micro1 Agentic Workflows Hackathon task ("hackathon", "micro1", "agentic workflow submission"). Sequences the other hackathon-* skills in the correct order, tracks which gate the project is at, and stops work from skipping ahead (e.g. writing code before the problem is scoped, or writing the changelog before a baseline exists). Re-load whenever unsure what to do next or before final submission packaging.
---

# micro1 Agentic Workflows Hackathon — Orchestrator

You are running an end-to-end hackathon submission, not a single coding task. Work in gates, in order. Do not open a code editor before Gate 1 is written down and confirmed with the user.

## Gate sequence

| Gate | Skill to load | Exit condition |
|---|---|---|
| 1. Frame the problem | `problem-framing` | 4 questions answered in writing, user has confirmed |
| 2. Design the agent | `agent-engineering` | design choices listed with a one-line justification each; safety/consequential-action list drafted |
| 3. Build simple baseline | `baseline-and-eval` (baseline half) | baseline runs end-to-end on real or synthetic cases |
| 4. Build + iterate the solution | `agent-engineering` + `improvement-changelog` | each iteration logged as it happens, not reconstructed later |
| 5. Evaluate | `baseline-and-eval` (eval half) | ≥10 cases, same cases for baseline and solution, 1 hard case included |
| 6. Self-score | `judging-rubric` | every criterion has a one-sentence honest answer, weakest one flagged |
| 7. Compliance check | `ground-rules-compliance` | all 10 rules checked, none silently skipped |
| 8. Package | `final-deliverables` | README, reproduction guide, video script, trajectories all present |

## Operating rules

- **Never fabricate results.** Every number in the changelog or eval table must come from an actual run you executed. If a number can't be produced yet, write "not yet measured" — do not estimate and present it as measured.
- **Log iterations as you go.** The changelog is not a report written at the end; it is a running log. If you make a design change during Gate 4, append the changelog entry in the same turn, before moving to the next change.
- **Deterministic logic for consequential/safety-critical steps.** Anything matching Ground Rule 04/05 (a consequential action, or something that could significantly affect a real person) must be implemented as deterministic code with a human-approval checkpoint — never left to model judgment alone. Flag this explicitly in `agent-engineering`.
- **One primary metric.** Resist the urge to track five metrics loosely — `baseline-and-eval` forces a single primary outcome metric plus at most two secondary ones (time, cost).
- **Reproducibility is a first-class deliverable, not a README afterthought.** Track "could a stranger run this from a clean checkout" from Gate 3 onward, not just at Gate 8.

## When the user gives you a problem idea directly

Skip straight to `problem-framing`, run its 4-question check against what they gave you, surface any gap (usually: no named user, or no bottleneck evidence), then proceed down the gate table.
