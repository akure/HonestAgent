# Changelog

All notable changes to HonestAgent are documented in this file. Entries summarize repository changes and link to the corresponding evidence where available. Results are reported with their measurement boundary; local tests, synthetic fixtures, and rehearsals are not presented as production evidence.

## Unreleased

No unreleased code changes. The current repository state is a proprietary, source-available development release and remains **NO-GO for unrestricted production**. The Sustainable Use License is a draft for legal review and is not the active license.

## 0.1.0 — 2026-08-29 — Conditional-pilot evidence release

### Added

- Conditional-pilot evidence sprint artifacts for immutable build and supply chain, provider reliability, storage recovery, executor safety, identity and audit operations, policy governance, and platform security.
- Machine-readable requirement evaluation and structured release evidence under `docs/development/evidence/` and `requirements_eval_results.json`.
- Stakeholder release decision summary, conditional-pilot transition template, evidence sprint plan, production-readiness gap plan, and CP-2 through CP-7 presentation materials.
- Hackathon self-evaluation, final compliance audit, clean-checkout reproduction rehearsal, and consent-safe customer interview evaluation kit.
- Concrete integration and client-use examples for finance, customer support, developer operations, data platforms, healthcare administration, HR operations, legal operations, and procurement.
- Commercial licensing and technical enforcement documentation covering hosted, private-deployment, OEM, managed-service, and source-escrow models.
- Updated root runtime skill with structured proposals, guard-first behavior, fail-closed decisions, prompt-injection resistance, bounded retries, human approval requirements, and no-unverified-success rules.

### Changed

- Replaced the stale README licensing and evaluation language with explicit proprietary-use boundaries, original-work attribution, problem framing, evidence links, and current project status.
- Added an HonestAgent Proprietary License with no default redistribution, hosting, resale, or commercial-use permission.
- Added a separate HonestAgent Sustainable Use License draft for legal review; it does not currently govern the repository.
- Strengthened `SECURITY.md` with reporting, supported-version, deployment-security, evidence, privacy, and dependency guidance.
- Hardened the Docker image to run as non-root UID `10001`, use unbuffered output, disable bytecode generation, and preserve application-file ownership.
- Anchored generated benchmark ignore rules so evidence JSON under documentation directories can be tracked and reviewed.
- Corrected stale evaluation claims, including old test counts, old latency values, old provider/webhook statuses, and runtime trajectory references.
- Updated reproduction instructions with the public repository URL, current test count, and honest latency limitations.
- Added concrete commercial-use examples, pilot scope, pricing hypotheses, proposal structure, invoice structure, and license boundaries.

### Verified evidence

- Full regression suite: **81 passed**.
- Deterministic deep evaluation: **20/20 unsafe actions intercepted** and **20/20 safe actions allowed** on 40 synthetic cases.
- Shared 12-case benchmark: pass-through baseline caught **0/10** unsafe actions; HonestAgent caught **10/10**.
- Latest local deep-evaluation latency: approximately **41.5 ms p50** and **46.7 ms p95**; the historical 25 ms p95 target is not met by that run.
- Dependency audit: **no known vulnerabilities** reported by `pip-audit -r requirements.txt`.
- Secret-pattern scan: no candidate API keys, private keys, or tokens found.
- The clean-checkout reproduction rehearsal passed, but remains **not independent third-party evidence**.
- Customer interview material is a preparation kit plus synthetic rehearsal; no real customer validation is claimed.

### Known limitations

- Production readiness remains NO-GO for unrestricted consequential execution.
- Live provider reliability, latency, malformed-output, disagreement, retry, and cancellation evidence is not measured against an approved production provider.
- The HTTP-compatible prototype and lightweight MCP adapter do not establish complete production protocol fidelity.
- Enterprise identity-provider integration, production audit sink, production-scale storage, container/host/network deployment evidence, monitoring, alerting, and kill-switch drills remain deployment-dependent.
- Local synthetic fixture results do not prove universal unsafe-action detection, compliance, or suitability for a customer’s workflow.
- The active repository license is proprietary and not an OSI-approved open-source license.

## 0.1.0-pre — 2026-08-29 — Launch-readiness hardening and early milestones

This historical sequence records the implementation progression from the initial contract through the launch-readiness gates. Detailed rationale and verification are retained in the linked sprint traces and change logs.

### M0–M5 foundation

- **M0 — Policy contract:** froze the structured evaluation contract, explicit action policy, safety invariants, and fail-closed unknown-action behavior. Evidence: `change_log_policy_contract_m0_20260829_054852.md`.
- **M1 — Durable checkpoint and audit:** added file-backed checkpoint storage, atomic resolution, restart persistence, compare-and-set behavior, retention handling, and separated webhook routing. Evidence: `change_log_durable_checkpoint_audit_m1_20260829_060033.md`.
- **M2 — Signed executor handoff:** added request-bound handoff signing, expiry handling, payload/trajectory binding, and executor-side validation. Evidence: `change_log_signed_executor_handoff_m2_20260829_060434.md`.
- **M3 — Upstream boundary:** added upstream passthrough boundary and provider-facing integration seam. Evidence: `change_log_upstream_passthrough_provider_m3_20260829_060706.md`.
- **M4 — Control-readiness reporting:** added structured launch and control reports. Evidence: `change_log_control_readiness_reporting_m4_20260829_060915.md`.
- **M5 — PMF instrumentation:** added policy simulation and sanitized JSONL event instrumentation for pilot measurement. Evidence: `change_log_pmf_simulation_instrumentation_m5_20260829_061112.md`.

### Launch-readiness gates

- **LR-1 — Reviewer identity:** added authenticated reviewer operations, roles, expiry, revocation, roster controls, and audit attribution. Evidence: `change_log_reviewer_auth_20260829_063624.md`.
- **LR-2 — Storage durability:** added durable checkpoint and SQLite transactional storage with restart, contention, retention, backup, and restore tests. Evidence: `change_log_checkpoint_storage_20260829_064548.md`.
- **LR-3 — Executor enforcement:** required valid request-bound handoffs at the executor boundary and blocked invalid, expired, mismatched, or absent handoffs without side effects. Evidence: `change_log_executor_enforcement_20260829_065316.md`.
- **LR-4 — Managed secrets:** added environment-backed secret loading, rotation overlap, validation, and development-default rejection in managed environments. Evidence: `change_log_managed_secrets_20260829_065609.md`.
- **LR-5 — Provider testing:** added typed provider fault handling, bounded retries, cancellation behavior, disagreement handling, and latency instrumentation. Evidence: `change_log_provider_testing_20260829_065833.md`.
- **LR-6 — Customer policy lifecycle:** added policy import, validation, simulation, approval, activation, signatures, quorum support, and rollback controls. Evidence: `change_log_customer_policy_20260829_070256.md`.
- **LR-7 — Security hardening:** added SSRF and private-target controls, payload redaction, request limits, DNS-rebinding validation, TLS policy, and deployment security checks. Evidence: `change_log_security_hardening_20260829_070602.md`.

### Blocker closure

- Closed B-1 through B-3 application-level provider, storage, and executor coverage with documented limitations.
- Closed B-4 platform-security application controls while retaining deployment-evidence limitations.
- Closed B-5 identity operations with reviewer roster, token revocation, and append-only hash-chained audit controls.
- Closed B-6 enterprise policy governance with signed policy records, approval quorum, simulation gating, activation, and tamper detection.
- Closed B-7 release decision controls with a deterministic fail-closed release gate.
- Evidence: `docs/release/blocker-closure-plan_20260829_071500.md` and the corresponding B-1 through B-7 traces and change logs.

## Baseline and evidence policy

The benchmark baseline is a transparent pass-through executor with no independent guard checks. Baseline and solution runs use the same labeled synthetic cases. The primary metric is unsafe-action interception **before execution**; safe pass-through and latency are reported separately. Any future metric change must preserve the case set or explain the difference explicitly.

## Versioning and release status

The repository currently uses the package version `0.1.0`. Until a tagged release process and production evidence are approved, commit SHAs and dated evidence artifacts are the authoritative references for implementation and evaluation state.

## License

The active repository terms are in [`LICENSE`](LICENSE). The repository is proprietary and not open source. The Sustainable Use License draft is available at [`LICENSE-SUSTAINABLE-USE-DRAFT.md`](LICENSE-SUSTAINABLE-USE-DRAFT.md) for legal review only.
