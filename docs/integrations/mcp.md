# MCP Integration

Honest Agent exposes two MCP-style tools through a line-delimited JSON stdio server:

| Tool | Purpose |
|---|---|
| `verify_context_health` | Evaluate a proposed action and return the normalized guard decision. |
| `trigger_human_checkpoint` | Resolve a pending trajectory with an explicit reviewer decision. |

## Run locally

```bash
PYTHONPATH=. python3 -m honest_agent.interfaces.mcp_server
```

The current adapter accepts one JSON object per line on stdin and writes one JSON result per line on stdout. A client can send:

```json
{"method":"verify_context_health","arguments":{"agent_id":"editor-agent","context":"The file is known.","tool_name":"read_file","tool_input":{"path":"README.md"}}}
```

For a paused action, retain the returned `trajectory_id` and send:

```json
{"method":"trigger_human_checkpoint","arguments":{"trajectory_id":"...","decision":"APPROVED","reviewer":"alice"}}
```

## Client configuration

A generic local configuration entry is:

```json
{
  "mcpServers": {
    "honest-agent": {
      "command": "python3",
      "args": ["-m", "honest_agent.interfaces.mcp_server"],
      "cwd": "/absolute/path/to/honest-agent"
    }
  }
}
```

The server should be placed behind the client’s normal process isolation and should not be granted credentials or filesystem access beyond what the calling application requires. The MCP layer only evaluates and records; it is not an executor.
