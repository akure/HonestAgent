"""AutoGen/AG2 example: function-tool decision boundary; no framework dependency is required for the local demo."""

from honest_agent.adapters import GuardedFrameworkTool


class AutoGenFunctionTool(GuardedFrameworkTool):
    def __init__(self, guard):
        super().__init__(guard, "autogen")

    async def call(self, request, tool, *, evidence=None):
        return await self.invoke(request, tool, evidence=evidence)
