from typing import Dict, List
from .search.base import BaseSearchTool


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseSearchTool] = {}

    def register(self, tool: BaseSearchTool):
        """Adds a tool to the registry using its name as the key."""
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> BaseSearchTool:
        """Retrieves a tool, or raises a clear error if the LLM hallucinated a name."""
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' not found in registry.")
        return self._tools[name]

    def get_all_schemas(self) -> List[Dict]:
        """Easily get the 'Menu' to send to Ollama."""
        return [tool.get_tool_schema() for tool in self._tools.values()]
