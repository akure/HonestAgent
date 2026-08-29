---
name: hackathon-ground-rules-compliance
description: Use before finalizing any micro1 hackathon submission, and any time the solution touches real data, external actions, or third-party tools/services, to check compliance with the 10 baseline ground rules (sandboxing, human review, licensing, data ethics, credential handling). Treat a failed rule as blocking, not a note for later.
---

# Ground Rules Compliance (baseline requirements — not scored separately, but disqualifying if missed)

These are pass/fail, not a rubric category — a violation undermines the whole submission regardless of how good the engineering is. Check every rule explicitly; do not assume compliance.

| # | Rule | Check |
|---|---|---|
| 01 | Free to build with known tools/components | No action needed, just don't hide it — see rule 02 |
| 02 | Clearly mark what pre-existed vs. what you built | README distinguishes prior art/libraries from original work |
| 03 | Respect every tool/service license and terms | Check license of every non-stdlib dependency and any API/service terms before using it |
| 04 | Consequential actions stay sandboxed/simulated with human approval | Any external side effect (send, write, spend, publish) is gated — see `agent-engineering`'s deterministic-action pattern |
| 05 | Qualified human reviewer in any solution that could significantly affect someone | Explicit human-in-the-loop step exists wherever the output could materially affect a real person (hiring, credit, medical, safety) |
| 06 | Legal, ethical use case; responsible treatment of people and data | No PII beyond what's needed; no use case that could harm or unfairly disadvantage someone |
| 07 | Only data you're allowed to share — public, synthetic, or approved-anonymous | Every dataset used in the demo/eval is public, synthetic, or explicitly approved |
| 08 | No credentials or private information in the submission | Grep the repo for API keys, tokens, `.env` files, personal data before packaging |
| 09 | Every claim about results is connected to submitted evidence | Every number in the README/changelog has a corresponding artifact (eval output, trajectory, log) in the submission |
| 10 | Judges can access and reproduce the main result | Reproduction guide tested end-to-end; access (data, credentials-free demo mode) confirmed |

## How to run this check

1. Walk the table top to bottom against the actual repo/submission, not against intent.
2. Any "no" is blocking — fix it before packaging, don't note it as a known gap.
3. Rules 07/08/09 are the ones most often silently violated by convenience (using a real dataset because it was handy, leaving a test API key in a config file, an unverified metric in the README) — check these last, right before submission, since they're easiest to reintroduce during final edits.
