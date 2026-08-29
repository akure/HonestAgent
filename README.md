# HonestAgent
Honest Agent is a small runtime gateway that pauses an agent’s proposed tool action when context pressure, missing grounding, ambiguity, or irreversible side effects make execution unsafe. It exposes one guardrail core through a FastAPI proxy, MCP-style stdio tools, and a Python decorator. Every evaluation can be logged as a structured trajectory.
