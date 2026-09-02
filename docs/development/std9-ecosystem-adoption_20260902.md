# STD-9 Ecosystem and Protocol Adoption

## TypeScript/HTTP reference client

The dependency-free TypeScript client lives under `clients/typescript/`. It uses standard `fetch` and exposes `guard()` and `execute()` methods for the HTTP gateway. It does not implement policy locally: the server remains the enforcement authority, and HTTP errors are surfaced without invoking a tool.

```bash
cd clients/typescript
npm run conformance
```

The conformance command uses Node's built-in runtime and does not require npm dependencies. The TypeScript source can be compiled by an adopter's pinned TypeScript toolchain; the repository deliberately avoids claiming a compiler or framework version that was not measured here.

## Independent conformance result

The non-Python `conformance.mjs` implementation passed all **8/8** canonical `honestagent.control.v1` core-profile fixture cases, including highest-compatible-minor negotiation, major-version rejection, malformed-version rejection, namespaced extension validation, and canonical intent hashing. This is a local independent implementation run, not an independent third-party reproduction.

## Adapter template

`examples/adapter-template/README.md` defines the required adapter boundary: convert framework proposals to protocol requests, delegate to HonestAgent, preserve pause/reject/failure/cancellation outcomes, and invoke only after request-bound handoff validation. Adapter-local approval flags and framework state cannot authorize execution.

## Version and deprecation policy

Protocol versions use `major.minor`. Minor versions may add backward-compatible fields or extensions. Major versions are never silently downgraded. Unknown extensions fail closed unless explicitly namespaced and classified. A deprecation notice must identify the replacement, effective date, and removal version; removal requires a major version or an explicitly approved compatibility transition. Implementations must report the exact protocol suite/profile and tested version in conformance output.

## Conformance badge rules

A project may say **“HonestAgent control protocol conformant”** only when it passes the published fixture suite for a named suite version and profile, with the result artifact and implementation version available. “Compatible,” “adapter,” or “protocol-shaped” must be used for partial or unmeasured integrations. No badge implies production safety, regulatory certification, customer validation, or support for untested framework versions.

## Adoption boundary

STD-9 establishes reusable adoption artifacts and one measured independent non-Python implementation. It does not claim that HonestAgent is already a de facto standard. Ecosystem adoption, third-party reproduction, actual TypeScript compilation, and live HTTP interoperability remain follow-on evidence work.
