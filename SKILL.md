# Honest Agent Runtime Guardrail

Before executing any tool action, provide a structured tool name and input, state the grounding context, and identify whether the action is irreversible or externally consequential.

If context is near the model’s capacity, if required variables are missing, or if the action is ambiguous, pause and request review rather than guessing. Never send, publish, delete, migrate, transfer, charge, or execute an external side effect without an explicit human approval checkpoint.

When integrated with Honest Agent, call `POST /v1/guard` or the MCP tool `verify_context_health` first. If the response is `PAUSED`, do not retry with altered arguments; preserve the trajectory ID and wait for the reviewer decision. Record the final action and the reviewer outcome in the trajectory log.
