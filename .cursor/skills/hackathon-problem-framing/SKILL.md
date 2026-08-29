---
name: hackathon-problem-framing
description: Use at the start of a micro1 Agentic Workflows Hackathon project, before any design or code, to pin down who has the problem, why it's worth solving, and whether it's reproducible. Also use to sanity-check a problem idea the user already has in mind, or to critique a draft README's opening section.
---

# Problem Framing (Gate 1)

The hackathon is scored 15/100 on "Problem & User Value" and the judges' first check is: *who experiences the bottleneck and why does solving it matter?* A vague or generic problem statement caps every other score, because a strong agent solving a fake problem still reads as a demo, not a product.

## The four questions — answer all four, in writing, before touching code

1. **Who has this problem?** Name a specific role or person, not "users" or "people." ("A recruiter screening 40 candidates a week for a mid-size startup" — not "hiring teams.")
2. **What bottleneck makes it worth solving?** Describe the *current* manual process and where it breaks — where errors creep in, what gets missed, what takes too long. Be concrete about the failure mode, not just "it's slow."
3. **Does the agent solve it well?** Not "can an LLM touch this" — can an *agent*, with the right context/tools/memory/verification, plausibly beat the current process on the metric that matters to that user?
4. **Can another person reproduce the result?** If the answer depends on private data, a manual judgment call, or infrastructure only you have, redesign the problem now — this is far cheaper to fix at Gate 1 than at Gate 8.

## Red flags to reject at this stage

- The "user" is an abstraction ("developers", "teams") with no specific bottleneck named.
- The problem is solvable by a single prompt with no real context/tool/memory need — there's no agentic story, just an LLM call.
- The evidence for the bottleneck is assumed, not described — you should be able to write 2–3 sentences on *why* the current approach fails, not just that it's tedious.
- The eventual evaluation would require private, sensitive, or unlicensed data (see `ground-rules-compliance` — rule 07/08 already fails here).

## Output format

Write this as the opening section of the eventual README, so it's reused, not redone:

```
## Who has this problem
[specific role/person]

## The bottleneck
[current manual process, where it breaks, why it's costly]

## Why an agent
[what agent capability — context, tools, memory, verification, skills,
orchestration — plausibly beats the manual process, and on what metric]
```

Reference the three worked examples (repo quality assessment, candidate evaluation, podcast translation consistency) as calibration for specificity — not as templates to copy. A strong problem statement is as concrete as those, about a different problem.

Do not proceed to `agent-engineering` until the user has confirmed this section.
