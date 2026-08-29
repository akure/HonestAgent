# M0 Safety Invariants and Threat Model

## Safety invariants

| ID | Invariant | Enforcement |
|---|---|---|
| SI-01 | The core never executes a customer side effect. | `HonestGuard` returns a decision; execution remains with the caller. |
| SI-02 | Verifier failure cannot produce `PROCEED`. | Provider exceptions are converted to fail-closed rejection. |
| SI-03 | Unknown or unclassified consequential actions require review. | `ActionPolicy` defaults unknown tools to `requires_review=True`. |
| SI-04 | Approval is bound to the original trajectory and request. | Pending state is keyed by trajectory ID; future handoff work will add payload binding. |
| SI-05 | Approval and rejection are idempotent. | Resolved decisions are returned without replaying the transition. |
| SI-06 | Final human state is reflected in persisted audit evidence. | Resolution rewrites the trajectory with the final checkpoint. |
| SI-07 | Policy classification is deterministic and independent of free-form tool arguments. | `ActionPolicy` uses explicit rules and tool-name tokens only. |
| SI-08 | Evaluation claims identify the fixture set and measurement boundary. | Benchmark and deep-evaluation reports preserve case counts and confusion metrics. |

## Threats in scope

The M0 threat model covers accidental execution after context degradation, unsupported tool identifiers, ambiguous arguments, provider timeout or malformed output, approval replay, concurrent approval, stale audit state, and unsafe default policy behavior.

## Deferred threats

Payload-bound execution handoff tokens, authenticated reviewer identity, durable multi-process storage, prompt-injection-specific classifiers, secret redaction, upstream provider compromise, and tenant isolation are deferred to later milestones. Deferral is explicit; these controls are launch blockers for real customer side effects.
