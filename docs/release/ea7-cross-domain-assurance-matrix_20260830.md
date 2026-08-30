# EA-7 Cross-Domain Assurance Matrix

## Evidence boundary

This matrix records **local synthetic and deterministic evidence only**. It is not regulatory certification, production deployment evidence, customer validation, or a claim that every unsafe action is detected. All six packs are DRAFT, opt-in, dry-run configurations.

| Domain | Representative allowed/review path | Explicit hard stop | Tested control evidence |
|---|---|---|---|
| Healthcare | Patient lookup and encounter support | PHI export and clinical-order execution | Tenant scope, evidence, prohibited action, redaction fields |
| Recruiting/HR | Candidate search and reviewed outreach | Autonomous rejection and hiring decision | Consent/source-purpose evidence, review, prohibited action |
| Financial Trading | Synthetic market lookup and bounded order draft | Settlement transfer and unreviewed order submission | Venue allowlist, quantity/notional cap, idempotency, review |
| Forecasting | Versioned series retrieval and bounded forecast | Committed planning action | Lineage, horizon cap, stale/contradictory evidence, review |
| Ecommerce | Product/inventory lookup and reviewed refund request | Payment capture | Ownership evidence, refund cap, idempotency, review |
| Customer Support | Scoped ticket lookup and cited guidance | Secret collection and autonomous account recovery | Ticket scope, queue allowlist, freshness, review |

## Framework assurance

The five framework examples share one adapter contract and were exercised with synthetic local callables. The conformance suite verifies proceed, pause, reject, provider failure, and altered-argument handoff rejection across all five examples. No example contacts a provider or executes a real side effect.

## Reproduction

```bash
pytest -q
for framework in langchain langgraph crewai autogen llamaindex; do
  python "examples/$framework/demo.py"
done
python -m json.tool examples/domain_packs/healthcare_operations_synthetic_v1.json >/dev/null
```

## Known gaps

Production evidence remains required for managed key custody, identity-provider integration, immutable audit sinks, distributed replay/rate state, real evidence provenance and freshness, framework-version compatibility, host/network controls, monitoring, alerting, kill-switch drills, and every customer deployment. Optional examples are disabled unless explicitly invoked by the caller.
