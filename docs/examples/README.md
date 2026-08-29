# HonestAgent Examples and Commercial Usage

These examples show how a licensed customer can integrate HonestAgent and how a provider can package paid work. They use synthetic values only. They are not a license, a production approval, legal advice, or a promise of support. The repository is proprietary; client use requires a separate written commercial license or services agreement under [`LICENSE`](../../LICENSE).

## 1. Credential-free Python evaluation

Use the deterministic core to evaluate a proposed action before the application-owned executor runs it:

```python
import asyncio
from honest_agent.core.guardrail import HonestGuard
from honest_agent.schemas.models import EvaluationRequest

async def main():
    guard = HonestGuard()
    request = EvaluationRequest(
        agent_id="demo-agent",
        context="Invoice 123 is approved for reconciliation.",
        tool_name="lookup_invoice",
        tool_input={"invoice_id": 123},
        irreversible=False,
    )
    decision = await guard.evaluate(request)
    print(decision.status.value, decision.trajectory_id)
    if decision.status.value == "PROCEED":
        # The integrating application owns and invokes the real tool.
        result = lookup_invoice(**request.tool_input)
        return result
    # For PAUSED or REJECTED, do not execute; route the trajectory to a reviewer.
    return {"status": decision.status.value, "trajectory": decision.trajectory_path}

# asyncio.run(main())
```

The default local path is intended for evaluation with synthetic data. Do not put provider keys, customer data, or production credentials in examples or source control.

## 2. Python SDK guard around an application-owned tool

Use the SDK when the client owns the callable and wants the guard immediately before execution:

```python
from honest_agent.interfaces.sdk import GuardrailPaused, guard

@guard(confidence_threshold=0.85, tool_name="send_invoice", irreversible=True)
def send_invoice(*, invoice_id: int, recipient: str, context: str, thought: str = ""):
    return billing_api.send(invoice_id=invoice_id, recipient=recipient)

try:
    response = send_invoice(
        invoice_id=123,
        recipient="approved@example.test",
        context="Invoice 123 is approved and recipient is verified.",
    )
except GuardrailPaused as paused:
    # Persist the trajectory and obtain an authorized human decision.
    print(paused.decision.trajectory_id)
```

The client remains responsible for authentication, authorization, idempotency, transaction boundaries, and the actual side effect. A paused action must not be retried with altered arguments.

## 3. HTTP proxy integration

Start the gateway locally:

```bash
uvicorn honest_agent.interfaces.proxy:app --host 127.0.0.1 --port 8000
```

Evaluate a normalized action:

```bash
curl -s http://127.0.0.1:8000/v1/guard \
  -H 'content-type: application/json' \
  -d '{
    "agent_id": "billing-agent",
    "context": "Invoice 123 is approved for reconciliation.",
    "tool_name": "lookup_invoice",
    "tool_input": {"invoice_id": 123},
    "irreversible": false
  }'
```

A `PROCEED` response means the guard evaluated the request; it does not mean HonestAgent executed the tool. The client must execute only through its own authenticated executor boundary. A `PAUSED` response requires preserving the trajectory and waiting for an authorized reviewer.

## 4. Safe reviewer checkpoint pattern

A client application should treat a checkpoint as a state transition, not as a retry prompt:

```python
async def handle_decision(request, decision, executor, reviewer_queue):
    if decision.status.value == "PROCEED":
        return await executor(request, decision.handoff_token)
    if decision.status.value == "PAUSED":
        await reviewer_queue.publish({
            "trajectory_id": decision.trajectory_id,
            "tool_name": request.tool_name,
            "tool_input": request.tool_input,
            "reason": decision.reasoning,
        })
        return {"status": "WAITING_FOR_REVIEW", "trajectory_id": decision.trajectory_id}
    return {"status": decision.status.value, "trajectory_id": decision.trajectory_id}
```

In a licensed deployment, configure durable checkpoint storage, reviewer authentication, append-only audit storage, retention, and an emergency disable procedure before enabling real side effects.

## 5. Suggested paid client engagement

The recommended commercial motion is a fixed-scope, two-week control-readiness pilot for one named customer and one workflow. The provider should define the action taxonomy, instrument the workflow, run a baseline-versus-guard benchmark, configure reviewer checkpoints, and deliver a written evidence report. Side effects should remain simulated or explicitly allowlisted until the client accepts the pilot evidence and signs the applicable agreement.

### Illustrative price card

| Offer | Example price | Scope |
|---|---:|---|
| Evaluation | Free or time-limited | Internal, credential-free evaluation only; no client delivery or production use |
| Control-readiness pilot | $15,000 fixed | One workflow, two weeks, policy mapping, integration, benchmark, reviewer procedure, final report |
| Team subscription | $1,500/month | One team, supported self-hosting or hosted endpoint, policy/review operations, monthly reliability review |
| Business subscription | $5,000–$10,000/month | Multiple teams, SSO/RBAC, durable audit, environment separation, SLA and quarterly control review |
| Enterprise | Custom annual agreement | Private deployment, data residency, custom integration, security-review support, response commitments |
| Implementation services | $15,000–$40,000 fixed | Threat model, action taxonomy, integration, benchmark, runbook, and handoff documentation |

These figures are commercial hypotheses for discovery, adapted from the product business model; they are not binding list prices.

## 6. Example quote and invoice structure

A written quote should identify the customer, scope, term, environment, deliverables, price, payment schedule, support boundaries, data handling, acceptance criteria, and license rights. For example:

```text
Quote: HonestAgent Control-Readiness Pilot
Customer: Example Co.
Workflow: Invoice reconciliation (one staging workflow)
Term: 14 calendar days from kickoff
Deliverables: policy map; integration; baseline-versus-guard benchmark;
              reviewer procedure; evidence report; closeout meeting
Side effects: simulated only
Fee: USD 15,000 fixed
Payment: 50% at signature; 50% on delivery of the evidence report
License: limited, non-transferable pilot license for the named customer,
         named environment, and stated term; no redistribution or resale
Acceptance: report delivered and reviewed in a closeout meeting
Exclusions: unrestricted production use, managed service rights, source
            redistribution, custom features, and third-party provider fees
```

For a subscription, invoice the recurring fee in advance and separately itemize implementation, usage above an agreed allowance, travel, and third-party costs. Do not describe payment as granting source-code ownership or broad redistribution rights unless the signed agreement expressly says so.

## 7. Commercial safeguards

Before accepting money or granting access, obtain a signed agreement reviewed by qualified counsel. Ensure the agreement is consistent with the proprietary license, names the permitted deployment, limits client and affiliate use, defines confidentiality and data processing, states support and service levels, addresses subprocessors and provider costs, and explains termination and deletion. Keep license keys, credentials, customer data, and invoices outside this public repository.

## 8. Concrete use-case matrix

The following scenarios show where a customer can place the boundary. The decision labels are **control objectives**, not guaranteed outcomes: the customer must map the tool names and action classes to its approved policy and run its own fixtures.

| Client workflow | Read-only action that may proceed | Consequential action that should pause or require approval | Evidence to retain |
|---|---|---|---|
| Finance: accounts payable | `lookup_invoice` or `get_vendor_status` | `approve_invoice`, `release_payment`, or `change_bank_details` | Invoice ID, amount, payee, policy version, reviewer, trajectory ID |
| Customer support: refunds | `get_order` or `check_refund_eligibility` | `issue_refund` or `change_customer_credit` | Order ID, refund amount, customer authorization, reviewer decision |
| Developer operations: production deploy | `read_deploy_status` or `preview_plan` | `deploy_production`, `rollback_release`, or `change_feature_flag` | Commit SHA, environment, diff/plan, approval, deployment result |
| Data platform: schema change | `describe_table` or `validate_migration` | `db_migrate`, `drop_table`, or `backfill_production` | Migration hash, affected tables, backup reference, approval |
| Healthcare administration | `check_coverage` or `read_claim_status` | `submit_claim`, `change_patient_contact`, or `release_record` | Minimum necessary fields, purpose, reviewer, audit chain |
| HR operations | `read_leave_balance` or `preview_payroll_change` | `approve_payroll`, `terminate_employee`, or `change_bank_account` | Employee reference, change summary, authorization, reviewer |
| Legal operations | `search_contract` or `compare_clause` | `send_notice`, `accept_terms`, or `publish_filing` | Document hash, recipients, final text hash, legal approval |
| Procurement | `search_catalog` or `compare_quotes` | `create_purchase_order`, `accept_supplier`, or `commit_spend` | Supplier, amount, budget, segregation-of-duties approval |

For every consequential action, the application must preserve the exact tool name and payload that were evaluated. It must not call the real executor after `PAUSED` or `REJECTED`, and it must not modify arguments to obtain a more favorable decision.

## 9. Finance example: invoice payment release

**Scenario:** An accounts-payable agent reads approved invoices and prepares payment batches. Reading invoice data is low consequence; releasing funds is consequential.

```python
request = EvaluationRequest(
    agent_id="ap-agent",
    context="Invoice INV-1042 is approved by the budget owner; payee matches the vendor master.",
    tool_name="release_payment",
    tool_input={"invoice_id": "INV-1042", "amount_minor": 125000, "currency": "USD"},
    irreversible=True,
)
decision = await guard.evaluate(request)

if decision.status.value == "PAUSED":
    await review_queue.publish({
        "trajectory_id": decision.trajectory_id,
        "summary": "Release USD 1,250.00 for INV-1042",
        "payload": request.tool_input,
    })
    # Do not call payments_api.release until an authorized reviewer approves.
elif decision.status.value == "PROCEED":
    # Only use this branch if policy explicitly permits the action class.
    await payments_api.release(**request.tool_input)
```

**Pilot acceptance test:** run a synthetic approved invoice, an amount mismatch, a changed payee, a duplicate request, and an expired reviewer token. Confirm the payment adapter records zero calls for every blocked case and that the approved case has a reviewer-attributed trajectory.

**Commercial package:** a two-week AP control-readiness pilot can include one staging payment simulator, an action taxonomy, reviewer matrix, benchmark, and evidence report. Charge implementation separately from the recurring policy and audit subscription.

## 10. Developer operations example: production deployment

**Scenario:** A release agent can inspect CI and propose a deployment, but production rollout requires an approval checkpoint.

```python
request = EvaluationRequest(
    agent_id="release-agent",
    context="Release 2026.08.29 passed the staging test suite; rollback image is available.",
    tool_name="deploy_production",
    tool_input={"service": "billing-api", "commit": "<approved-commit-sha>", "environment": "prod"},
    irreversible=True,
)
decision = await guard.evaluate(request)
if decision.status.value != "PROCEED":
    record_for_release_manager(decision.trajectory_id, request.tool_input, decision.reasoning)
else:
    await deployment_executor.run(request.tool_input, decision.handoff_token)
```

**Pilot acceptance test:** validate that an altered commit, wrong environment, replayed handoff, and missing rollback reference cannot reach the deployment executor. Capture the deployment plan and the final approval as separate records.

**Commercial package:** price the initial engagement as a fixed implementation plus a Team or Business subscription when the customer requires environment separation, shared review queues, retention, and recurring control reviews.

## 11. Data-platform example: migration and rollback

**Scenario:** A data agent may inspect schemas and generate a migration plan, but it must not alter production state without simulation, backup confirmation, and human approval.

```json
{
  "agent_id": "data-platform-agent",
  "context": "Migration M-77 adds a nullable index; simulation completed against a production-like clone.",
  "tool_name": "db_migrate",
  "tool_input": {
    "migration_id": "M-77",
    "schema": "billing",
    "backup_ref": "backup://staging/2026-08-29/M-77",
    "rollback_id": "RB-M-77"
  },
  "irreversible": true
}
```

**Pilot acceptance test:** reject unsigned policy, missing simulation evidence, missing backup reference, changed migration payload, and a second approval from the same reviewer when the policy requires two distinct reviewers. Retain migration hash, policy version, quorum approvals, activation record, and rollback result.

**Commercial package:** sell this as a control-readiness engagement for one schema and one staging topology, with a separate fee for production-like recovery design and ongoing audit retention.

## 12. Customer-support example: refund approval

**Scenario:** A support agent can read an order and calculate a refund, but payment reversal requires an authorized reviewer above a threshold.

```bash
curl -s http://127.0.0.1:8000/v1/guard \
  -H 'content-type: application/json' \
  -d '{
    "agent_id": "support-agent",
    "context": "Order O-88 arrived damaged; customer identity is verified.",
    "tool_name": "issue_refund",
    "tool_input": {"order_id": "O-88", "amount_minor": 7500, "reason": "damaged"},
    "irreversible": true
  }'
```

If the configured policy returns `PAUSED`, place the trajectory in the support review queue. The reviewer should see the order reference, amount, reason, and decision explanation, but not unnecessary payment credentials. After approval, the executor must use the same evaluated payload and request-bound handoff.

## 13. How to turn a use case into a paid proposal

For each prospective client, write the proposal around one workflow rather than generic AI access:

1. Define the agent, tools, data boundary, irreversible actions, reviewer roles, and success metric.
2. Instrument a staging or sanitized workflow and establish a baseline without the guard.
3. Add the guard, run safe/unsafe, duplicate, timeout, replay, and reviewer drills, and retain redacted trajectories.
4. Deliver a decision report containing the action taxonomy, benchmark, latency, review rate, blocked-side-effect results, limitations, and next-step recommendation.
5. Convert the pilot to a subscription only when the customer wants retained policy lifecycle, shared review operations, support, private deployment, or formal audit evidence.

A concrete proposal should state the exact workflow, number of environments, number of reviewers, retention period, included support hours, allowed side effects, deployment responsibility, third-party provider costs, acceptance test, fee, payment schedule, and license scope. It should explicitly exclude unrestricted production, redistribution, source ownership, resale, and use by affiliates unless those rights are separately priced and granted in writing.
