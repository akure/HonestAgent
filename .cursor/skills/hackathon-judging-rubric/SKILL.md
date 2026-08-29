---
name: hackathon-judging-rubric
description: Use to self-score a micro1 hackathon submission against the actual 100-point rubric before final packaging, or any time the user asks "are we ready to submit" / "how would this score." Surfaces the weakest-scoring criterion honestly rather than assuming full marks.
---

# Judging Rubric Self-Check (100 points total)

Run this as an honest self-audit, not a formality — the goal is to find the weakest criterion *before* judges do. For each row, answer the judge's own question in one sentence, then assign a rough band (strong / adequate / weak) with a one-line reason. Do not round up.

| Criterion | Pts | Judge's question | Self-check |
|---|---|---|---|
| Problem & User Value | 15 | Who experiences the bottleneck and why does solving it matter? | Does `problem-framing`'s output name a specific person and a concrete, evidenced bottleneck — not a generic "users"? |
| Agent Solution & Engineering | 30 | Which design choices helped the agent solve the problem? | Can every capability in `agent-engineering` be traced to a specific failure mode, with purposefulness over component count? |
| End to End Quality | 20 | Would the intended user consider this high quality, or does it read as an obvious AI draft? | Would the *named user from Gate 1* actually sign their name to this output, unedited? |
| Measured Improvement | 15 | Which changes truly improved the outcome? | Does the metrics table use a fair baseline and does every changelog entry cite matching evidence? |
| Reproducibility | 15 | Could a second person do it from a clean environment? | Has anyone (ideally not you) actually tried the reproduction guide on a clean checkout? |
| Hot Take / Insights | 5 | What did you learn and how would it change what you build next? | Is the hot take a real observed failure mode from the changelog, not a generic platitude? |

## What to do with a "weak" result

- **Problem & User Value weak** → back to `problem-framing`; this caps every downstream score, fix it first even late in the process.
- **Agent Solution weak** → check for either under-engineering (no capability matches a real failure mode) or over-engineering (components with no justification sentence) via `agent-engineering`.
- **End to End Quality weak** → the fix is usually polish and self-containment, not more features — walk through the full user-facing output as if you were the named user from Gate 1.
- **Measured Improvement weak** → almost always an unfair or missing baseline, or changelog entries without matching evidence — revisit `baseline-and-eval`.
- **Reproducibility weak** → the single highest-leverage fix given how cheaply judges can catch it: have someone else run the reproduction guide from scratch before submitting.
- **Hot Take weak** → pull directly from a removed/failed changelog entry rather than writing a new insight from scratch.

Report the self-check results plainly to the user, including any weak scores — don't soften a weak result to look more finished than it is.
