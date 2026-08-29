# M5 PMF Validation and Policy Simulation

## Product hypothesis

Customers will pay for Honest Agent when it reduces the risk and review cost of consequential AI actions without forcing them to replace their existing agent framework or model gateway.

## Dry-run workflow

A customer first exports representative, sanitized tool proposals as `EvaluationRequest` JSON. The policy simulator classifies each action without calling a verifier and without executing a side effect. The customer reviews which actions would proceed, pause, or reject, then tunes explicit policy rules before enabling enforcement in staging.

```bash
python3 scripts/simulate_policy.py fixtures/customer_sanitized_requests.json reports/policy-simulation.json
```

The simulation output is advisory. It is not an approval artifact and cannot be used as an execution handoff.

## PMF event dictionary

| Event | Meaning | Required values |
|---|---|---|
| `workflow_activated` | A customer connects one agent workflow. | customer, workflow |
| `protected_action` | A consequential proposal passes through the guard. | action class, status, policy version |
| `checkpoint_created` | A proposal is paused for review. | trajectory ID, reason |
| `checkpoint_resolved` | A reviewer approves or rejects a checkpoint. | reviewer role, outcome, turnaround |
| `evidence_exported` | A customer generates a control-readiness report. | case count, report version |
| `pilot_completed` | A fixed-scope pilot reaches its recommendation. | baseline, guarded metrics, decision |
| `pilot_converted` | A pilot becomes a paid recurring deployment. | plan, workflow count |

Payloads must exclude prompts, tool arguments, credentials, and customer content unless an explicit retention policy permits a redacted field. Event semantics must stabilize before building a dashboard.

## PMF decision metrics

| Metric | Definition | Early signal |
|---|---|---|
| Time to first protected action | Time from setup to first guarded consequential proposal. | Falling across pilots. |
| Review burden | Percentage of proposals paused and median reviewer turnaround. | Customers can operate the workflow without excessive friction. |
| Safe-action pass rate | Safe proposals that proceed without unnecessary review. | High availability is preserved. |
| Protected actions per workflow | Count of guarded consequential proposals per active workflow. | Product becomes habitual rather than a one-time audit. |
| 30-day workflow retention | Active workflows still sending proposals after 30 days. | Repeated use validates the wedge. |
| Paid pilot conversion | Qualified pilots that become paid deployments. | Willingness to pay is demonstrated. |

## Validation sequence

Run twelve problem interviews before expanding the product surface. Use two design-partner pilots with one workflow each. For each pilot, compare an identical sanitized replay against the pass-through baseline and guarded path. Review the report with the customer, measure review burden, and ask for a paid continuation or procurement path.

Do not interpret synthetic benchmark accuracy as product-market fit. Product-market fit requires repeated customer use, a retained workflow, and a commercial commitment.
