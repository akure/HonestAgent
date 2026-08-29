## Summary

Describe the failure mode or user need this change addresses.

## Safety impact

Explain whether this changes action policy, verifier behavior, approval state, audit records, or an integration contract.

## Validation

- [ ] Added or updated deterministic fixtures.
- [ ] Ran `python -m pytest -q`.
- [ ] Ran `python tests/deep_eval.py` when behavior changed.
- [ ] Confirmed no credentials or private data are included.
- [ ] Documented known false positives, false negatives, or rollout risks.
