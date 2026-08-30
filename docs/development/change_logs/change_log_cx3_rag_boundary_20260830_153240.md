# Change Log — CX-3 first-class RAG evidence boundary

| Field | Value |
|---|---|
| Phase | `CX3` |
| Feature | `Retrieval and evidence boundary` |
| Timestamp UTC | `2026-08-30 15:32:40` |
| Status | `complete` |

## Problem

RAG content was not yet represented as a first-class control boundary. Retrieved text could be confused with authorization metadata, and tenant scope, source allowlists, egress class, freshness, citation coverage, and prompt-injection signals were not composed into one deterministic decision.

## Change

Added `RAGEvidenceBoundary` and `RetrievalChunk`. The boundary checks tenant scope, optional source allowlists, egress class, evidence freshness, and trusted-producer requirements for high-impact actions. It returns redacted evidence IDs and typed reasons rather than raw content. A deterministic prompt-injection detector produces a pause signal; it is not treated as an authorization mechanism. High-impact workflows can require citation coverage, and authorization-bearing evidence is permitted only for trusted envelopes with a redacted reference.

## Verification

| Check | Result |
|---|---|
| Fresh scoped evidence accepted | `PASS` |
| Cross-tenant chunk paused/rejected | `PASS` |
| Stale evidence paused/rejected | `PASS` |
| Disallowed egress class paused/rejected | `PASS` |
| Prompt-injection signal detected | `PASS` |
| High-impact untrusted evidence blocked | `PASS` |
| Incomplete citation coverage blocked | `PASS` |
| Retrieved content cannot bear authority by default | `PASS` |
| Full regression suite | `93 passed` |
| Formatting check | `PASS` |

## Live experiment log

| Stage | What was tried and why | Evidence | Decision |
|---|---|---|---|
| Baseline | Treat retrieved text as ordinary context | Existing context checks did not express tenant/source/freshness or citation controls | Replaced with explicit boundary |
| Iteration 1 | Reject cross-tenant, stale, and disallowed-egress chunks | Adversarial tests produced `PAUSE` with redacted evidence IDs | Kept |
| Iteration 2 | Detect common instruction-injection patterns | Injection fixture produced a deterministic signal and pause | Kept as signal, not sole authorization |
| Iteration 3 | Require trusted evidence and citation coverage for high-impact actions | Untrusted/missing-citation cases blocked | Kept |

## Decision

CX-3 is **complete** for the in-memory retrieval/evidence boundary contract. CX-4 can add workflow state transitions and scoped checkpoints around this boundary.

## Known limitations

No external vector database, document connector, DNS/egress deployment, or live customer corpus was accessed. Prompt-injection detection is a signal and must be combined with policy, provenance, and human review. Raw chunk content remains available only to the application caller and is not persisted by this boundary.
