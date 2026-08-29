# CP-4 Executor Inventory

| Surface | Executor boundary | Handoff enforcement | Evidence |
|---|---|---|---|
| HTTP `/v1/execute` | `ExecutorGateway` → configured upstream | Required request-bound signed handoff | `tests/test_lr3_executor.py` |
| HTTP `/v1/chat/completions` | `ExecutorGateway` → upstream or simulated response | Required request-bound signed handoff | `honest_agent/interfaces/proxy.py` |
| Python SDK | `CallableExecutor` → caller callable | Required request-bound signed handoff | `honest_agent/core/executor.py` |
| MCP stdio | Guard approval/rejection operation; no direct tool callable | Approval operation only; external executor remains caller-owned | `honest_agent/interfaces/mcp_server.py` |

Invalid, missing, malformed, replayed, altered-payload, wrong-trajectory, and paused-decision handoffs are covered by the targeted suite. The tests assert zero upstream calls on blocked paths.
