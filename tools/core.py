import json
from typing import Any

from pydantic import BaseModel


class BaseTool:
    name: str
    description: str
    args_schema: type[BaseModel]

    async def execute(self, **kwargs: Any) -> Any:
        raise NotImplementedError("Every tool must have an 'execute' method.")

    def get_definition(self) -> dict[str, Any]:
        schema = self.args_schema.model_json_schema()
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": schema,
            },
        }


class ToolRegistry:
    def __init__(self) -> None:
        self.tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        self.tools[tool.name] = tool

    def get_tools_definitions(self) -> list[dict[str, Any]]:
        return [tool.get_definition() for tool in self.tools.values()]

    async def call_tool(self, name: str, arguments: str) -> Any:
        if name not in self.tools:
            return [{"error": f"Unknown tool: {name}"}]

        try:
            args_dict = json.loads(arguments)
            tool = self.tools[name]

            validated_args = tool.args_schema(**args_dict)

            return await tool.execute(**validated_args.model_dump())

        except Exception as e:
            return [{"error": f"Tool execution failed: {str(e)}"}]
