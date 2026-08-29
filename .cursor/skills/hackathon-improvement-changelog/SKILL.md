---
name: hackathon-improvement-changelog
description: Use continuously during Gate 4 (build + iterate) of the micro1 hackathon to log every meaningful experiment as it happens — additions, changes, and removals — with evidence from the same evaluation method each time. Also use when assembling the final README's changelog section. Do not write this retroactively from memory at the end; append entries live.
---

# Improvement Changelog (feeds Measured Improvement, 15/100, and Hot Take, 5/100)

The changelog is what lets judges connect *which* changes actually helped to the evidence — a baseline-vs-final comparison alone doesn't tell that story. Log entries live, in the same turn you make the change, not reconstructed afterward from memory (memory of "why we did X" degrades fast and reads as vaguer in the final writeup).

## Entry rule — one row per meaningful experiment, including removed ones

Every entry needs, before you move to the next change:
1. **What you tried and why** — tie it to a specific observed failure, not a generic "improve quality."
2. **Evidence** — the result, using the *same evaluation method* as every other entry (see `baseline-and-eval`). If you haven't run the eval yet for this entry, don't fill in a guessed number — leave it open and come back.
3. **Decision** — kept, revised, or removed, and what it taught you if removed. Removed experiments are explicitly valuable to the brief — don't quietly delete them from the log, that erases evidence judges want to see.

## Table shape

```
| Stage       | What you tried and why              | Evidence      | Decision / Learning        |
|-------------|--------------------------------------|---------------|-----------------------------|
| Baseline    | Started with [basic approach]        | [baseline result] | Established starting point |
| Iteration 1 | Added [capability] to address [issue]| [new result]  | [kept/revised/removed + why]|
| Iteration 2 | ...                                   | ...           | ...                          |
| Final       | Combined the changes that worked     | [final result]| Identified main contribution|
```

## Discipline

- Append the row **before** starting the next iteration, not after the whole project is "done" — this is the single biggest cause of a thin, hand-wavy changelog at submission time.
- If an iteration didn't move the metric, log it anyway with "no change / removed" — a flat result on a plausible-sounding idea is exactly the kind of evidence that supports the Hot Take criterion later.
- At the end, review the full log and pull out: (a) the single change that contributed most, (b) the failure mode worth turning into the Hot Take. Both go into `final-deliverables`.
