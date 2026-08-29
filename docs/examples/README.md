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
