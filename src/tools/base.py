from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Dict, Type, Any


class BaseTool(ABC):
    name: str
    description: str
    args_schema: Type[BaseModel]

    @classmethod
    def get_tool_schema(cls) -> Dict[str, Any]:
        return {
            "type": "function",
            "function" : {
                "name": cls.name,
                "description": cls.description,
                "parameters": cls.args_schema.model_json_schema()
            }
        }

    @abstractmethod
    async def search(self, **kwargs) -> Dict: ...
