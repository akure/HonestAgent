# Git Trace and Development Workflow

Every meaningful Honest Agent change must be reviewable from the GitHub repository without relying on chat history. The repository should show what changed, why it changed, how it was tested, and which commit published it.

## Required artifacts

| Artifact | Location | Purpose |
|---|---|---|
| Feature or fix changelog | `docs/development/change_logs/change_log_{feature_or_fix}_{YYYYMMDD_HHMMSS}.md` | Records the problem, change, evidence, risks, and follow-up. |
| Sprint trace | `docs/development/sprint_traces/sprint_{milestone}_{sprint}_{YYYYMMDD_HHMMSS}.md` | Records task sequence, decisions, test runs, and milestone status. |
| Durable roadmap update | `docs/development/` or relevant product/architecture document | Keeps the planned next step aligned with implementation reality. |
| Focused Git commit | Git history | Connects the artifact and implementation to one reviewable change. |
| Validation evidence | `test_reports/` or linked CI output | Preserves the measured result and fixture boundary. |

## Naming convention

Use UTC timestamps in compact 24-hour format:

```text
docs/development/change_logs/change_log_policy_registry_20260829_054852.md
docs/development/sprint_traces/sprint_m0_s1_20260829_054852.md
```

Use lowercase snake case for the feature or fix name. One timestamped changelog should describe one cohesive feature, bug fix, experiment, or security correction. If one sprint contains several independent changes, create one changelog per change and one sprint trace tying them together.

## Commit convention

Commits should be small enough to review and named with a conventional prefix:

| Change type | Prefix | Example |
|---|---|---|
| New product behavior | `feat:` | `feat: add durable checkpoint store` |
| Defect correction | `fix:` | `fix: reject stale approval handoffs` |
| Tests or evaluation | `test:` | `test: add provider failure matrix` |
| Documentation or trace | `docs:` | `docs: record M1 sprint trace` |
| Refactor without behavior change | `refactor:` | `refactor: isolate webhook adapter` |
| Build or CI | `chore:` | `chore: add release workflow` |

Each commit must reference the relevant changelog or sprint trace in its message body or changed files. Do not mix unrelated product changes, generated outputs, credentials, or private customer data into a sprint commit.

## Required changelog sections

A change log must state the change ID, timestamp, milestone, problem statement, implementation summary, files changed, tests run, measured evidence, known limitations, rollback or mitigation plan, and next action. Claims such as catch rate or latency must name the fixture set and measurement boundary.

## Required sprint-trace sections

A sprint trace must state the sprint objective, tasks attempted in order, decisions and trade-offs, failures discovered, fixes applied, commands executed, test results, commit hashes, and whether the milestone is complete. A failed test is evidence and must be recorded before the fix is made.

## Push discipline

At the end of each completed sprint, run the full relevant test suite, commit the sprint artifacts, push to `main`, verify that `origin/main` points to the expected commit, and report the remote hash. Do not begin the next sprint until the current sprint’s trace is published and reviewed.

## Review rule

The next sprint may only start after the previous sprint has a published trace, a passing release gate, and an explicit user decision to continue. This preserves a clear chain from roadmap → builder task → implementation → test evidence → GitHub commit → next decision.
