# HonestAgent Git Workflow

## Purpose

This workflow is designed for a safety-oriented framework moving from a validated implementation baseline toward a more mature workflow control plane. It keeps changes reviewable, preserves fail-closed behavior, and makes release evidence distinguishable from production claims.

## Branch model

`main` is the protected, releasable branch. All implementation work starts from an up-to-date `main` branch in a focused branch named with one of these prefixes:

| Prefix | Use | Examples |
|---|---|---|
| `feat/` | New capability with tests and documentation | `feat/workflow-context` |
| `fix/` | Correctness or security defect | `fix/handoff-expiry` |
| `sec/` | Security hardening or dependency remediation | `sec/rag-egress-boundary` |
| `docs/` | Documentation-only change | `docs/release-runbook` |
| `test/` | Test/evidence improvement without behavior change | `test/replay-drills` |
| `chore/` | Tooling, packaging, or maintenance | `chore/pin-framework-example` |

Do not develop directly on `main`. Keep a branch focused on one coherent change and rebase or merge `main` before requesting review. Never force-push `main` or rewrite a published release tag.

## Commit rules

Commits should be small, imperative, and explain one logical change. Recommended format is `<type>(<scope>): <summary>`, for example `feat(workflow): add durable run context`. A behavior-changing commit must include its regression tests. A security-sensitive commit must include the threat, root cause, mitigation, and residual risk in the pull request or linked change log.

Do not commit credentials, customer data, raw prompts, provider responses, proprietary client fixtures, generated caches, or unlicensed dependencies. Synthetic fixtures must be clearly labeled. Avoid mixing formatting-only changes with safety behavior changes.

## Required local checks

Before opening a pull request, run the checks relevant to the change and record exact results:

```bash
pip install -e '.[dev]'
PYTHONPATH=. pytest -q
PYTHONPATH=. python3 tests/deep_eval.py
git diff --check
```

For policy, handoff, executor, RAG, workflow-state, or adapter changes, also run the targeted adversarial suite and the relevant offline example commands. For packaging changes, build a wheel and install it into a clean temporary environment. For dependency changes, run the approved vulnerability audit and update the SBOM evidence.

## Pull request gates

Every pull request must state the user problem, affected contracts, threat model, tests, operational assumptions, and rollback path. Reviewers should confirm that the change has one pre-execution enforcement point, cannot authorize itself from model output or retrieved text, does not weaken a stricter policy layer, and fails closed on malformed, unavailable, stale, contradictory, unauthorized, or ambiguous inputs.

Changes affecting public schemas, policy composition, handoffs, checkpoints, execution semantics, identity, secrets, audit events, egress, or licensing require two reviewers: one implementation owner and one security or reliability reviewer. Changes to release posture require the release owner. A review approval is not an authorization to perform live consequential actions.

## Merge strategy

Use a pull request with a green required check suite. Prefer squash merge for small focused changes and preserve the pull request title as the resulting commit subject. Resolve conflicts by bringing the branch up to date and rerunning the full suite. After merge, verify that `main` is clean, the remote points to the expected commit, and the change log or sprint trace references the published commit.

## Release and tagging workflow

A release tag is created only from a clean, tested `main` commit. The release record must identify the exact commit, package version, test count, dependency scan, SBOM status, known limitations, and release decision. Tags are annotated and immutable:

```bash
git checkout main
git pull --ff-only origin main
git status --short
PYTHONPATH=. pytest -q
python -m compileall -q honest_agent
python -m pip wheel . --no-deps -w /tmp/honestagent-wheel
git diff --check
git tag -a vX.Y.Z -m "HonestAgent X.Y.Z"
git push origin vX.Y.Z
```

The initial implementation tag represents a tested source baseline, not unrestricted production approval. A release marked `NO-GO` or `CONDITIONAL PILOT` must say so in its release record and changelog. Never use a tag to imply regulatory certification, customer validation, or safe autonomous execution that has not been evidenced.

## Hotfix and rollback

Security or release-blocking defects branch from the affected release tag into `fix/` or `sec/`. The fix must include a regression test and a new patch tag; do not mutate the old tag. Rollback means reverting the deployment to a previously tested immutable tag or disabling an opt-in policy/example, not deleting audit history or silently changing a policy artifact.

If a change affects handoff validation, policy activation, checkpoint resolution, or executor behavior, pause deployment until replay, altered-argument, duplicate-execution, and recovery tests pass. Preserve the old active policy during failed activation and document the operator decision.

## Maturity roadmap

The repository should move through these gates:

| Gate | Meaning | Minimum evidence |
|---|---|---|
| Source baseline | Versioned implementation checkpoint | Full local tests and known limitations |
| Workflow foundation | Durable run/step/attempt and intent contracts | Replay, concurrency, budget, and handoff tests |
| RAG foundation | First-class evidence and retrieval boundary | Tenant, freshness, provenance, injection, redaction, and egress tests |
| Controlled pilot | Narrow deployment with accountable owner | Deployment checklist, monitoring, identity, storage, recovery, and kill-switch evidence |
| Production consideration | Specific approved deployment only | Live environment evidence and accepted residual risk |

## Emergency controls

The kill switch, policy retirement, credential revocation, and deployment rollback are operator-controlled actions. They must be auditable, tested in the target environment, and scoped to tenant, workflow, tool, or release where possible. Git history is not a substitute for runtime audit history.

## Ownership

The implementation owner is responsible for code and regression evidence. The security/reliability reviewer is responsible for adversarial coverage and residual-risk review. The release owner is responsible for the release decision. Client or production authorization must come from the accountable deployment owner under the applicable commercial and security agreements.
