# Contributing to Honest Agent

Thank you for helping improve a safety-oriented project. Contributions should make the pre-execution boundary more reliable, more explainable, or easier to integrate without weakening deterministic controls around consequential actions.

The complete branch, commit, review, release, tagging, hotfix, and rollback process is documented in [`docs/development/git-workflow.md`](docs/development/git-workflow.md).

## Development workflow

Create a focused branch, add or update a deterministic fixture for the behavior you are changing, run the full test suite, and explain the trade-off in the pull request. Changes that affect policy, approval, audit records, or provider failure behavior require a regression test and a short design note.

```bash
pip install -e '.[dev]'
PYTHONPATH=. pytest -q
PYTHONPATH=. python3 tests/deep_eval.py
```

## Pull request expectations

A pull request should state the failure mode it addresses, identify whether it changes the public schema or integration contracts, include evidence from the same evaluation method, and document any known false positives or false negatives. Do not include credentials, private customer data, or unlicensed fixtures.

## Design principles

Keep interfaces thin and the core framework-neutral. Treat model output as advisory evidence, never as authorization for irreversible work. Prefer explicit policy and human checkpoints over hidden heuristics. Preserve auditability when changing state transitions. Avoid adding dependencies unless they are necessary for a user-facing capability.
