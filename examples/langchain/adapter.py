"""LangChain example: StructuredTool-style wrapper; no framework dependency is required for the local demo."""

from honest_agent.adapters import GuardedFrameworkTool


class LangChainToolWrapper(GuardedFrameworkTool):
    def __init__(self, guard):
        super().__init__(guard, "langchain")

    async def call(self, request, tool, *, evidence=None):
        return await self.invoke(request, tool, evidence=evidence)
