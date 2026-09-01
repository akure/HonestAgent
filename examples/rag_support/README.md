# Synthetic RAG Safety Reference Workflow

This example demonstrates the STD-3 sequence:

```text
retrieve → tenant/source/egress/freshness/trust checks → cite → propose → guard → validate handoff → execute stub
```

Run it from the repository root:

```bash
PYTHONPATH=. python examples/rag_support/demo.py
```

The example uses synthetic support-policy content, a trusted synthetic evidence envelope, local temporary-like paths under `/tmp`, and a stub tool. It requires no credentials, model provider, vector database, network access, or live side effect.

The workflow does not treat retrieved text as authorization. Cross-tenant content, stale chunks, disallowed egress, missing high-impact citations, and deterministic prompt-injection signals pause or block before the tool is reached. The final tool call is allowed only after the existing HonestGuard decision and request-bound handoff validation succeed.
