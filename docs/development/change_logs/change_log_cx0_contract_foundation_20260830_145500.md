# Change Log — CX0 contract and threat-model foundation

| Field | Value |
|---|---|
| Phase | `CX0` |
| Feature | `Complex workflow identity, tool intent, evidence, and control-event contracts` |
| Timestamp UTC | `2026-08-30 14:55:00` |
| Status | `complete` |

## Problem

HonestAgent’s MVP safety decision was primarily single-request oriented. Complex agentic workflows and RAG systems require durable run/step identity, attenuated delegation, deterministic tool-intent identity, attributable evidence, and redacted decision lineage before workflow orchestration is added.

## Change

Added versioned Pydantic contracts for `WorkflowRunContext`, `WorkflowBudgets`, `ToolIntent`, `EvidenceEnvelope`, `DecisionRecord`, and `ControlEvent`. Workflow children can only attenuate tools, budgets, deadlines, and inherited authority. Tool intents use deterministic canonical JSON and SHA-256 identity. Authorization-bearing evidence requires trusted provenance, raw content is excluded by construction, and freshness is explicit. Added CX0 architecture, threat-model, compatibility, and state-transition documentation.

## Verification

| Check | Result |
|---|---|
| Child delegation cannot add tools | `PASS` |
| Child delegation cannot increase budgets | `PASS` |
| Child delegation cannot extend deadline | `PASS` |
| Intent hash stable across key order | `PASS` |
| Intent hash changes on semantic mutation | `PASS` |
| Untrusted evidence cannot bear authorization | `PASS` |
| Raw evidence without redacted reference rejected | `PASS` |
| Stale evidence detected | `PASS` |
| Unknown contract fields rejected | `PASS` |
| Full regression suite | `80 passed` |

## Decision

CX0 is **complete** and ready for CX-1. No framework-specific workflow or RAG authorization path was added, and existing MVP contracts remain compatible.

## Safety invariants

The model remains a proposal source rather than an authority source. Retrieved content remains untrusted unless a trusted producer explicitly attests to it. Consequential actions retain human review and executor handoff requirements. No raw evidence content or credential material is added to audit contracts.
