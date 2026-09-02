# Change Log — STD-9 Ecosystem and Protocol Adoption

| Field | Value |
|---|---|
| Sprint | STD-9 |
| Change type | ecosystem / protocol / TypeScript / conformance / governance |
| Date | 2026-09-02 |
| Related commit | `e3929a7` |
| Evidence class | Local independent implementation and deterministic fixture evidence |

## Change

Added a dependency-free TypeScript/HTTP client, Node conformance runner, adapter template, compatibility/deprecation policy, and conformance badge rules. The TypeScript runner independently implements the canonical protocol operations and executes the shared `honestagent.control.v1` fixture manifest.

## Validation

| Check | Result |
|---|---|
| Non-Python conformance runner | PASS — 8/8 fixtures |
| Intent-hash parity | PASS |
| Version negotiation | PASS |
| Extension validation | PASS |
| Node syntax | PASS |
| Full Python regression suite | PASS — 150 tests |
| Python compilation | PASS |
| `git diff --check` | PASS |

## Evidence boundary

This is local independent implementation evidence, not independent third-party reproduction. The TypeScript source was not compiled in this environment, and live HTTP interoperability, external framework adoption, and production support remain unmeasured. The project does not claim de facto standard status.

## Security invariants

Unknown or malformed protocol inputs fail closed. The client delegates authorization to the server. Adapter guidance preserves pause, reject, failure, cancellation, and altered-handoff outcomes and disallows local approval bypasses.

## Rollback

Revert the TypeScript client and runner, adapter template, governance guide, and STD-9 evidence artifacts. Existing Python protocol tooling remains available.

## Next action

Implement STD-10 enterprise control plane and commercial packaging.
