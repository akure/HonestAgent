# Simulated Customer Interview Rehearsal

**Status: SIMULATION ONLY — not customer evidence and not suitable for a score claim.**  
**Purpose:** rehearse the interview protocol, identify likely objections, and prepare a consented interview template before speaking with real target users.

No real people were interviewed. The personas below are synthetic composites and must never be presented as quotes, customers, validation, willingness-to-pay evidence, or product-market-fit evidence.

## Synthetic personas

| ID | Role | Workflow | Simulated bottleneck | Simulated adoption blocker |
|---|---|---|---|---|
| SIM-01 | AI platform engineer | Agent proposes production changes | Approval is scattered across chat, tickets, and deploy tooling; the final executor boundary is hard to prove | Integration effort and latency |
| SIM-02 | Security reviewer | Finance agent releases payments | Logs explain what happened but do not prove why the action was allowed before execution | Need immutable audit and enterprise identity |
| SIM-03 | SRE lead | Release agent deploys services | A stale or replayed approval could authorize the wrong commit or environment | Must integrate with existing deployment controls |
| SIM-04 | Operations manager | Support agent issues refunds | Reviewers lack a consistent threshold and payload summary for high-value refunds | Review queue volume and false positives |
| SIM-05 | Data platform lead | Agent runs schema migrations | Backup, simulation, rollback, and approval evidence are spread across different systems | Recovery objectives and operational ownership |

## Rehearsal synthesis

The synthetic scenarios point to a narrow problem statement: teams need a deterministic, request-bound checkpoint immediately before an agent-controlled consequential action, with attributable approval and durable evidence. The strongest repeated risks are stale approvals, mismatched payloads, replay, scattered reviewer records, and uncertainty about whether a blocked action reached the executor.

The synthetic scenarios also expose adoption questions that must be tested with real people:

- Is the latency overhead acceptable on the actual workflow?
- Which integration surface is easiest to adopt?
- Who owns the reviewer queue and emergency disable process?
- What audit retention and identity guarantees are mandatory?
- Is the main buyer paying for reduced security-review time, reduced incident risk, or operational tooling?

## Interview protocol to use with real participants

Obtain consent before recording notes. Ask about the participant’s current workflow and failure modes before showing HonestAgent. Request no confidential, personal, regulated, customer, credential, or proprietary information. Record only anonymized notes under participant IDs. Publish only an approved synthesis, never raw notes or unapproved quotes.

## Evidence classification

This rehearsal improves interview readiness but earns **zero customer-evidence points** in the hackathon rubric. Real evidence requires interviews with at least three relevant participants, consented anonymized notes, independently described bottlenecks, an adoption blocker, and at least one disconfirming signal.
