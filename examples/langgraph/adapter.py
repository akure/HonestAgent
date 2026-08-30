"""LangGraph example: state-machine guard node; no framework dependency is required for the local demo."""

from honest_agent.adapters import GuardedFrameworkTool


class LangGraphGuardNode(GuardedFrameworkTool):
    def __init__(self, guard):
        super().__init__(guard, "langgraph")

    async def call(self, request, tool, *, evidence=None):
        return await self.invoke(request, tool, evidence=evidence)
