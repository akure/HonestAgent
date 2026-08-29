# Python SDK Integration

Use the decorator when the application already owns the tool function and wants a pre-execution guard without adopting the HTTP proxy.

```python
from honest_agent.interfaces.sdk import GuardrailPaused, guard


@guard(confidence_threshold=0.85, tool_name="write_file", irreversible=True)
def write_file(*, path: str, content: str, context: str, thought: str = ""):
    # The application owns execution. This function is never called while paused.
    return open(path, "w", encoding="utf-8").write(content)
```

When the decorator raises `GuardrailPaused`, the application should display the structured decision to a qualified reviewer and preserve the trajectory ID. The SDK does not silently retry, rewrite arguments, or execute a fallback side effect.

For production use, inject a durable logger and policy registry rather than relying on the development default local JSON store. The caller remains responsible for authenticating reviewers and enforcing its own authorization model.

# IDE skill integration

The root `SKILL.md` is a portable instruction file for IDE agents. Copy it into a project-specific skills directory or adapt it into `.cursorrules`. The essential rule is that an agent must propose a structured tool action, call the guard, and stop when the decision is `PAUSED`.
