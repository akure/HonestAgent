---
name: hackathon-final-deliverables
description: Use last, to assemble the four required micro1 hackathon submission deliverables — solution code + changelog, reproduction guide, solution video script/outline, and agent trajectories. Load after judging-rubric and ground-rules-compliance both pass. Also use when the user asks what's missing before they submit.
---

# Final Deliverables (Gate 8 — packaging)

Four items, all required. Missing or thin ones on Reproducibility (15 pts) and End to End Quality (20 pts) are the most common avoidable point losses.

## 1. Solution code + Improvement Changelog

- Full project, including every agent instruction/prompt, not just the orchestration code.
- README doc-first order: **who the intended user is and their bottleneck → why an agent → engineering guide (design choices and why) → architecture → code.** (Pull the opening directly from `problem-framing`'s output — don't rewrite it.)
- Improvement Changelog section, in the table format from `improvement-changelog`, every iteration included.
- Close with: the main failure mode observed, and the hot take (from `judging-rubric`'s Hot Take check).

## 2. Reproduction guide

Written for a stranger on a clean environment. Must include:
- Setup steps and exact commands for: the baseline, the solution, and the evaluation — three separate runnable paths, not just "run main.py."
- Required data (and where to get the public/synthetic/approved version — see `ground-rules-compliance` rule 07).
- Expected output, so the reader can confirm they reproduced the right thing, not just *a* thing.
- Versions of key dependencies/models, plus approximate runtime and cost.
- **Actually test this yourself (or have someone else test it) from a clean checkout before submitting** — this is the single highest-leverage check in the whole package.

## 3. Solution video (≤5 minutes)

Script/outline structure:
1. Problem + simple baseline (short — this is context, not the payoff).
2. One realistic execution, start to finish, of the actual solution.
3. Final baseline-vs-solution comparison, shown not just claimed.
4. Brief changelog walkthrough: the change that contributed most, and one experiment you removed.

Keep the baseline section brief — judges already have it in the README; the video's value is *watching the real thing work end to end*.

## 4. Agent trajectories

For every agent used, include a representative trajectory showing:
- The instructions/prompt given to that agent.
- What it did and how each tool responded.
- The feedback that shaped its next step.
- Any retries or human-approval checkpoints (these matter especially for any consequential-action agent flagged in `agent-engineering`).

Trajectories should be easy to follow end-to-end by someone who wasn't in the room — annotate rather than paste raw logs if the raw logs are noisy.

## Pre-submit pass

Run through `judging-rubric` and `ground-rules-compliance` one more time against the assembled package, not against your memory of the project — packaging often reintroduces gaps (a credential left in a config, a claim without a matching artifact).
