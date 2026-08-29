---
name: hackathon-baseline-and-eval
description: Use to design and run the baseline comparison and the evaluation for the micro1 hackathon — building the simple baseline before/alongside the agent solution, and scoring both on identical cases. Load before running any evaluation, and again before writing the metrics table into the README. Covers the Measured Improvement rubric criterion (15/100).
---

# Baseline & Evaluation (Gate 3 build, Gate 5 measure — 15/100 points for Measured Improvement)

The baseline and the eval must be designed together, before either the solution or the numbers exist, or the comparison won't be fair — and judges explicitly check for a *fair* baseline.

## Choose ONE baseline type (pick the strongest honest comparison for this problem)

- One direct prompt, basic instructions, no tools.
- One general-purpose agent with basic tools (no memory/verification/skills/orchestration).
- A simple script or template — no LLM at all, if that's genuinely how the task is done today.
- The actual manual process a human currently uses — best baseline when reproducible, since it's what the "improvement" claim is really against.

Fairness rule: **give the baseline and the final solution the exact same task and the exact same evaluation cases.** If the solution gets extra resources (more tool calls, more tokens, more time), state that difference explicitly rather than let the comparison imply a like-for-like win.

## Design the evaluation before running it

1. Pick **one primary metric** that reflects what success means to *this* user (tests passing for a developer; time/cost saved for ops; calibration for forecasting — pull this from `problem-framing`'s bottleneck description, don't invent a generic one).
2. Add at most two secondary metrics: human time per task, cost per task.
3. Define what a "good" final result looks like for the intended user *before* running anything — write this down first, don't back-fit it after seeing results.
4. Build ≥10 cases where the task allows it. Include at least one deliberately hard/edge case and write down what it revealed, even if the result was a failure — failures are evidence, not something to hide.
5. Run baseline and solution on the identical case set. Report every result, not a cherry-picked subset.

## Metrics table (use this shape in the README)

```
| Metric              | Simple baseline | Agent solution | Change |
|---------------------|-----------------|-----------------|--------|
| [Primary outcome]   | [value]         | [value]         | [Δ]    |
| Human time per task  | [value]         | [value]         | [Δ]    |
| Cost per task        | [value]         | [value]         | [Δ]    |
```

If this shape doesn't fit the task, design an explicit scoring rubric instead and state it plainly — judges will use whatever rubric you propose, but only if it's clear and you ran it yourself.

## Non-negotiables

- Every number in the table must come from a run you actually executed — never estimate a result and present it as measured (see orchestrator rule).
- The baseline and eval cases feed directly into `improvement-changelog` — each changelog entry cites the same evaluation method so results are comparable across iterations.
