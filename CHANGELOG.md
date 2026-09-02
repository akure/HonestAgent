# Changelog

All notable changes to HonestAgent are documented in this file. Entries summarize repository changes and link to the corresponding evidence where available. Results are reported with their measurement boundary; local tests, synthetic fixtures, and rehearsals are not presented as production evidence.

## Unreleased

The current repository state is a proprietary, source-available development release and remains **NO-GO for unrestricted production**. The Sustainable Use License is a draft for legal review and is not the active license.

### Added

- Reusable `honest-agent-enterprise-sprint-delivery` skill covering one-sprint scope control, fail-closed implementation, adversarial validation, evidence discipline, and two-stage Git publication. Evidence: `skills/honest-agent-enterprise-sprint-delivery/SKILL.md`.
- STD-6 reliable execution semantics and operational controls: durable intent inbox/outbox, explicit at-most-once/idempotent retry modes, timeout, cancellation, crash recovery, kill switches, quotas, and duplicate-side-effect tests. Evidence: `docs/development/sprint_traces/sprint_std6_reliable_execution_20260902.md`.
- STD-7 version-pinned framework integration boundary: explicit LangGraph/RAG support metadata, unsupported-version rejection, native pause/resume/cancellation, and request-bound handoff tests. Actual package compatibility remains explicitly unmeasured. Evidence: `docs/development/sprint_traces/sprint_std7_framework_integrations_20260902.md`.
- STD-8 independent reproduction and benchmark evidence: fixed identical baseline/control vector, false-pause and false-proceed metrics, machine-readable result schema, clean-checkout runner, and reviewer reproduction protocol. Results are local synthetic evidence only. Evidence: `docs/development/sprint_traces/sprint_std8_independent_reproduction_20260902.md`.
- STD-9 ecosystem and protocol adoption: dependency-free TypeScript/HTTP client, non-Python conformance runner, adapter template, compatibility/deprecation policy, and measured 8/8 canonical fixture result. Third-party reproduction and de facto standard status remain unclaimed. Evidence: `docs/development/sprint_traces/sprint_std9_ecosystem_adoption_20260902.md`.
- STD-10A enterprise policy registry: tenant-bound HMAC signatures, importer/approver/activation separation of duties, simulation gating, rollback-preserving activation, and persisted lifecycle evidence events. Deployment, hosted-service, and production IAM evidence remain out of scope. Evidence: `docs/development/sprint_traces/sprint_std10a_policy_registry_20260902.md`.
- STD-10B enterprise identity and reviewer governance: optional tenant-bound reviewer claims, strict expiry, subject/token/roster revocation, tenant-aware webhook authentication, body-spoof resistance, and authenticated role/tenant audit attribution. Production IdP, MFA, HSM, and distributed-revocation evidence remain out of scope. Evidence: `docs/development/sprint_traces/sprint_std10b_identity_governance_20260902.md`.
- STD-5 policy composition and delegation attenuation: monotonic layered resolution, deterministic policy snapshots, conflict explanations, capability intersection, and effective budget enforcement. Evidence: `docs/development/sprint_traces/sprint_std5_policy_composition_20260901.md`.
- STD-4 durable workflow state and human oversight: SQLite lifecycle state machine, exact approval scope, expiry/cancellation, restart persistence, and duplicate-execution rejection. Evidence: `docs/development/sprint_traces/sprint_std4_durable_workflow_state_20260901.md`.
- STD-3 RAG safety reference workflow: offline retrieve/cite/guard/approve/resume/execute composition, tenant and injection isolation tests, and synthetic support example. Evidence: `docs/development/sprint_traces/sprint_std3_rag_safety_reference_20260901.md`.
- STD-2 Python developer experience and CLI: stable `HonestAgent` facade, guarded-tool decorator, typed blocking errors, non-destructive initializer, credential-free offline demo, and migration guide. Evidence: `docs/development/sprint_traces/sprint_std2_developer_experience_20260901.md`.
- STD-1 golden fixtures and conformance kit: versioned `honestagent.control.v1` core-profile manifest, deterministic runner, machine-readable results, independent-implementation guide, and fail-closed mismatch tests. Evidence: `docs/development/sprint_traces/sprint_std1_conformance_20260901.md`.
- STD-0 protocol governance and public contract boundary: `honestagent.control.v1` normative semantics, fail-closed version negotiation, namespaced extension rules, trust-boundary threat model, architecture decision record, and public protocol helpers. Evidence: `docs/development/sprint_traces/sprint_std0_protocol_governance_20260901.md`.
- De facto standardization sprint plan covering protocol governance, conformance fixtures, developer experience, RAG reference workflow, durable workflow state, delegation, reliable execution, pinned integrations, independent reproduction, ecosystem adoption, and enterprise packaging. Evidence: `docs/development/de-facto-standardization-sprint-plan_20260901.md`.
- EA-5–EA-7 framework and assurance tranche: five credential-free adapters, shared conformance tests, compatibility/security documentation, cross-domain assurance matrix, and threat-model update. Evidence: `docs/development/framework-adapter-compatibility-ea6_20260830.md`, `docs/release/ea7-cross-domain-assurance-matrix_20260830.md`, and `docs/security/enterprise-adaptability-threat-model-ea7_20260830.md`.
- Mature Git workflow and initial implementation release record covering focused branches, review gates, immutable annotated tags, hotfixes, rollback, and conservative release posture. Evidence: `docs/development/git-workflow.md` and `docs/release/v0.1.0-initial-implementation.md`.
- EA-4 synthetic Ecommerce and Customer Support policy packs with ownership, refund, account-change, identity, escalation, knowledge-freshness, and sensitive-data boundaries. Evidence: `docs/development/sprint_traces/sprint_ea4_ecommerce_support_policy_packs_20260830.md`.
- EA-3 synthetic Trading and Forecasting policy packs with pre-trade caps, venue/account scope, idempotency, forecast lineage, freshness, contradiction handling, review boundaries, and no-live-execution hard stops. Evidence: `docs/development/sprint_traces/sprint_ea3_trading_forecasting_policy_packs_20260830.md`.
- EA-2 synthetic Healthcare and Recruiting/HR policy packs with dry-run rollout, evidence requirements, idempotency controls, human-review boundaries, and hard stops for clinical and autonomous employment decisions. Evidence: `docs/development/sprint_traces/sprint_ea2_healthcare_hr_policy_packs_20260830.md`.
- EA-0/EA-1 domain policy-pack foundation: tenant-scoped Pydantic contract, bounded deterministic evaluator, HMAC-SHA256 signed lifecycle registry, and optional fail-closed `HonestGuard` gate. Evidence: `docs/development/sprint_traces/sprint_ea1_domain_policy_pack_foundation_20260830.md` and `docs/development/change_logs/change_log_sprint_ea1_domain_policy_pack_foundation_20260830_135600.md`.

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
- Hardened PMF event persistence so recognized sensitive fields are recursively redacted before JSONL serialization. Evidence: `change_log_ops_audit_redaction_20260829_100800.md`.
- Hardened trajectory persistence so free-text system instructions and thoughts are omitted while structured tool inputs remain recursively redacted. Evidence: `change_log_core_trajectory_privacy_20260829_104500.md`.
- Hardened the report and policy-simulation CLIs to create output directories and added the sanitized fixture referenced by the documented simulation workflow. Evidence: `change_log_scripts_reproducibility_20260829_105000.md`.

### Verified evidence

- Full regression suite: **83 passed**.
- EA-1 regression suite: **92 passed** in the post-integration full run, including signature tamper, tenant isolation, malformed evidence, prohibited action, and guard-gate tests.
- EA-2 artifact and full regression suite: **94 passed**, including synthetic Healthcare/HR pack validation and hard-stop assertions.
- EA-3 artifact and full regression suite: **99 passed**, including synthetic Trading/Forecasting caps, stale/contradictory evidence, lineage, replay, and hard-stop assertions.
- EA-4 artifact and full regression suite: **103 passed**, including synthetic Ecommerce/Support ownership, refund, identity, freshness, replay, and hard-stop assertions.
- EA-5–EA-7 framework and assurance suite: **120 passed**, including five-adapter proceed/pause/reject/provider-failure/altered-handoff cases, six-domain hard-stop coverage, JSON validation, and five offline demos.
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

### Development change-log index

The following index reconciles every file currently present in `docs/development/change_logs/` with the milestone or evidence activity it records. Historical test counts in these dated records are intentionally preserved; they describe the run at that time and are not substitutes for the latest metrics above.

| Change log | Scope | Recorded outcome |
|---|---|---|
| `change_log_policy_contract_m0_20260829_054852.md` | M0 policy contract | Structured action/policy contract and fail-closed unknown-action behavior established. |
| `change_log_durable_checkpoint_audit_m1_20260829_060033.md` | M1 checkpoint and audit | Durable checkpoint/audit foundation and restart-safe resolution established. |
| `change_log_signed_executor_handoff_m2_20260829_060434.md` | M2 handoff | Payload- and trajectory-bound signed handoff established. |
| `change_log_upstream_passthrough_provider_m3_20260829_060706.md` | M3 provider boundary | Optional OpenAI-compatible provider and guarded upstream path added; local simulation remains the default. |
| `change_log_control_readiness_reporting_m4_20260829_060915.md` | M4 reporting | Structured control-readiness reporting added. |
| `change_log_pmf_simulation_instrumentation_m5_20260829_061112.md` | M5 pilot instrumentation | Policy simulation and sanitized pilot event vocabulary added. |
| `change_log_launch_readiness_program_20260829_062926.md` | LR program | Ordered launch-readiness gates and acceptance evidence defined. |
| `change_log_reviewer_auth_20260829_063624.md` | LR-1 identity | Reviewer authentication, roles, expiry, revocation, and attribution controls added. |
| `change_log_checkpoint_storage_20260829_064548.md` | LR-2 storage | SQLite/file-backed durability, locking, retention, backup, and restore controls exercised. |
| `change_log_executor_enforcement_20260829_065316.md` | LR-3 executor | Invalid, stale, replayed, or mismatched handoffs blocked before callable invocation. |
| `change_log_managed_secrets_20260829_065609.md` | LR-4 secrets | Managed startup, rotation overlap, validation, and redaction controls added. |
| `change_log_provider_testing_20260829_065833.md` | LR-5 providers | Timeout, malformed output, disagreement, retry, cancellation, and latency tests added. |
| `change_log_customer_policy_20260829_070256.md` | LR-6 policy | Policy import, simulation, approval, activation, signing, and rollback controls added. |
| `change_log_security_hardening_20260829_070602.md` | LR-7 security | SSRF, redaction, payload-limit, private-network, and security-boundary controls added. |
| `change_log_final_launch_readiness_20260829_071047.md` | Final LR review | Conservative NO-GO decision recorded for unrestricted production. |
| `change_log_blocker_closure_program_20260829_071500.md` | B-1–B-7 program | Ordered target-environment evidence closure program defined. |
| `change_log_blocker_b1_provider_evidence_20260829_071700.md` | B-1 provider | Local fault harness passed; live-provider evidence remained not measured. |
| `change_log_blocker_b2_transactional_storage_20260829_072115.md` | B-2 storage | Transactional storage controls passed locally; deployment failover evidence remained incomplete. |
| `change_log_blocker_b3_executor_coverage_20260829_072253.md` | B-3 executor | Supported adapter blocked invalid handoffs with zero callable side effects. |
| `change_log_blocker_b4_platform_security_20260829_074000.md` | B-4 platform security | DNS-rebinding and TLS application controls added; target-platform evidence remained not measured. |
| No standalone `change_log_blocker_b5_*.md` file | B-5 identity operations | B-5 implementation is recorded in `change_log_reviewer_auth_20260829_063624.md`, the CP-5 sprint trace/change log, and the B-5 implementation commit history. |
| `change_log_blocker_b6_enterprise_policy_governance_20260829_075000.md` | B-6 governance | Signed records, quorum, simulation gating, activation, and tamper detection added. |
| `change_log_blocker_b7_final_release_decision_20260829_080000.md` | B-7 release gate | Deterministic fail-closed release decision gate added. |
| `change_log_sprint_cp1_immutable_build_supply_chain_20260829_084500.md` | CP-1 supply chain | Isolated build, provenance, SBOM, dependency, and secret-scan evidence recorded. |
| `change_log_sprint_cp2_provider_reliability_20260829_090000.md` | CP-2 provider | Local evidence runner executed; approved live-provider result remained `NOT MEASURED`. |
| `change_log_sprint_cp3_storage_recovery_20260829_091500.md` | CP-3 recovery | Restart, concurrency, backup/restore, and retention controls passed locally; production topology remained partial. |
| `change_log_sprint_cp4_executor_side_effect_safety_20260829_094500.md` | CP-4 executor safety | Twelve targeted side-effect and handoff tests passed; real adapter coverage remained partial. |
| `change_log_sprint_cp5_identity_audit_operations_20260829_101500.md` | CP-5 identity/audit | Eleven identity and audit tests passed; production IdP and immutable sink remained not measured. |
| `change_log_sprint_cp6_policy_governance_20260829_103000.md` | CP-6 governance | Six policy lifecycle tests passed; enterprise custody and authority remained not measured. |
| `change_log_sprint_cp7_platform_security_operations_20260829_110000.md` | CP-7 operations | Eighteen tests, compilation, dependency scan, and secret scan passed locally; host/platform drills remained partial. |
| `change_log_sprint_ea1_domain_policy_pack_foundation_20260830_135600.md` | EA-0/EA-1 domain policy foundation | Tenant-scoped signed packs, deterministic evaluation, lifecycle controls, and additive guard integration passed local regression tests. |
| `change_log_sprint_ea2_healthcare_hr_policy_packs_20260830_140300.md` | EA-2 Healthcare and HR packs | Synthetic dry-run packs and hard-stop regression tests passed; no production or regulatory claim. |
| `change_log_sprint_ea3_trading_forecasting_policy_packs_20260830_140700.md` | EA-3 Trading and Forecasting packs | Synthetic pre-trade and forecast-planning controls passed local tests; no live execution or commitment claim. |
| `change_log_sprint_ea4_ecommerce_support_policy_packs_20260830_141000.md` | EA-4 Ecommerce and Support packs | Synthetic refund, account, identity, escalation, and freshness controls passed local tests; no live remediation claim. |
| `change_log_sprint_ea5_ea7_framework_assurance_20260830_141500.md` | EA-5–EA-7 framework and assurance tranche | Five offline adapters, conformance suite, compatibility review, cross-domain matrix, and threat-model update passed local validation. |
| `change_log_launch_readiness_audit_20260829_083000.md` | Final audit | Found and fixed missing guard-endpoint payload-size enforcement; historical 81-test verification passed. |
| `change_log_github_history_reconciliation_20260829_100500.md` | Git history | One-to-one chronological ledger covering all 64 commits reachable on `main` at reconciliation time. |
| `change_log_ops_audit_redaction_20260829_100800.md` | Ops privacy fix | Found and fixed unsanitized PMF event values; added nested redaction regression coverage. |
| `change_log_core_trajectory_privacy_20260829_104500.md` | Core privacy fix | Found and fixed persisted free-text instructions and thoughts; added regression coverage. |
| `change_log_scripts_reproducibility_20260829_105000.md` | Scripts reproducibility | Fixed missing output-directory creation and added the documented sanitized policy fixture. |

## Baseline and evidence policy

The benchmark baseline is a transparent pass-through executor with no independent guard checks. Baseline and solution runs use the same labeled synthetic cases. The primary metric is unsafe-action interception **before execution**; safe pass-through and latency are reported separately. Any future metric change must preserve the case set or explain the difference explicitly.

## Versioning and release status

The repository currently uses the package version `0.1.0`. Until a tagged release process and production evidence are approved, commit SHAs and dated evidence artifacts are the authoritative references for implementation and evaluation state.

## License

The active repository terms are in [`LICENSE`](LICENSE). The repository is proprietary and not open source. The Sustainable Use License draft is available at [`LICENSE-SUSTAINABLE-USE-DRAFT.md`](LICENSE-SUSTAINABLE-USE-DRAFT.md) for legal review only.
