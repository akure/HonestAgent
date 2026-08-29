# FastAPI and OpenAI-Compatible Proxy Integration

The proxy is the lowest-friction integration path. Applications can send a normalized request to `/v1/guard`, or attach `honest_agent` metadata to an OpenAI-shaped request at `/v1/chat/completions`.

## Start the gateway

```bash
uvicorn honest_agent.interfaces.proxy:app --host 127.0.0.1 --port 8000
```

## Normalized guard request

```bash
curl -s http://127.0.0.1:8000/v1/guard \
  -H 'content-type: application/json' \
  -d '{
    "agent_id": "billing-agent",
    "system_instruction": "Reconcile approved invoices",
    "thought": "The invoice ID is present in the context",
    "context": "Invoice 123 is approved for reconciliation.",
    "tool_name": "lookup_invoice",
    "tool_input": {"invoice_id": 123},
    "irreversible": false
  }'
```

A safe read-only action returns `decision.status = PROCEED`. The caller may then invoke its own executor. Honest Agent does not execute the tool.

## Paused action

If the response has `decision.status = PAUSED`, the caller must not retry with altered arguments. Persist `trajectory_id`, show the reviewer the structured action, and wait for an explicit decision.

```bash
curl -s -X POST http://127.0.0.1:8000/approve/$TRAJECTORY_ID \
  -H 'content-type: application/json' \
  -d '{"reviewer":"reviewer@example.com"}'
```

The approval response is idempotent for the same trajectory. The durable JSON trajectory is rewritten with the final checkpoint state.

## OpenAI-shaped requests

The compatibility route extracts message content and optional metadata:

```json
{
  "model": "provider-model",
  "messages": [{"role": "user", "content": "Look up invoice 123"}],
  "honest_agent": {
    "agent_id": "billing-agent",
    "tool_name": "lookup_invoice",
    "tool_input": {"invoice_id": 123},
    "irreversible": false
  }
}
```

The current proprietary prototype returns a simulated completion after approval. Any client production adapter requires a separate written commercial license and must forward only after the guard decision while authenticating both the caller and reviewer endpoints.
