# HonestAgent Control Protocol v1 Conformance Fixtures

This directory contains the first language-neutral golden fixture manifest for `honestagent.control.v1`. The cases intentionally contain only synthetic identifiers and deterministic values. They do not contain credentials, raw prompts, protected retrieval content, or live side effects.

## Run the reference implementation

From the repository root:

```bash
PYTHONPATH=. python -m honest_agent.conformance.runner \
  fixtures/conformance/v1/manifest.json \
  --output /tmp/honestagent-control-v1-result.json
```

Exit code `0` means every case matched its expected result. The output is a JSON result object containing the suite, profile, pass/fail counts, per-case actual and expected values, and an overall `conformant` boolean.

## Fixture operations

The initial core profile covers compatible minor-version negotiation, unsupported major versions, malformed versions, namespaced extension classification, malformed extensions, deterministic `ToolIntent` hashing, and hash mutation detection.

An independent implementation may consume the manifest as data and implement equivalent operations. A conformance report must state the implementation version, protocol/profile version, fixture-suite version and commit, environment, date, and unsupported features. Passing the reference runner is local evidence; it is not independent certification.

## Safety rule

A fixture mismatch is a conformance failure. It must not be “corrected” by treating an error, altered hash, unsupported version, or unclassified extension as a successful authorization.
