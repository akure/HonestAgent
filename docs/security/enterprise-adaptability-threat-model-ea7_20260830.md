# Enterprise Adaptability Threat-Model Update — EA-7

| Threat | Boundary | Evidence / residual risk |
|---|---|---|
| Authority confusion | Tenant and evidence metadata are caller-controlled inputs; prompt/retrieved text is not authorization. | Wrong-tenant and malicious-content tests pass. Trusted identity and evidence provenance remain deployment-owned. |
| Prompt injection | Framework adapters pass normalized proposals to HonestAgent and never derive authority from model text. | Adapter documentation and conformance tests cover untrusted content. Upstream application must isolate retrieved text. |
| Data leakage | Packs declare classification and redaction fields; existing trajectory/PMF redaction remains in the kernel. | Local synthetic checks pass. Egress enforcement and production sink review remain open. |
| Replay / duplicate execution | Mutating rules can require idempotency; handoffs bind request payload and trajectory and expire. | Local altered-argument tests pass. Distributed replay state remains deployment-owned. |
| Irreversible action | Generic action policy, domain rule, human checkpoint, signed handoff, and executor boundary are additive gates. | Hard-stop matrix passes. No live consequential action is executed by examples. |
| Fail-open provider/tool failure | Adapter returns `PROVIDER_FAILURE` and does not report execution; rejected/paused decisions never call the tool. | Five-adapter conformance tests pass. Production cancellation and retry semantics require framework-specific testing. |
| Broad rollout | Packs are DRAFT, dry-run, tenant-scoped, signed on import, and include stop conditions and kill-switch requirement. | Local lifecycle evidence exists. Operational kill-switch drills and rollout telemetry remain open. |

## Residual decision

The EA-5 through EA-7 tranche improves demonstrability and local assurance but does not change the project’s NO-GO status for unrestricted consequential production use. A deployment must supply managed identity, secrets, audit, storage, egress, monitoring, and framework-version evidence before pilot authorization.
