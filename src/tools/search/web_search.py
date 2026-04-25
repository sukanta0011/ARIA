from typing import Dict
from pydantic import BaseModel, Field
from .base import BaseSearchTool


class WebSearchArgs(BaseModel):
    query: str = Field(description="Question to be searched in web")
    max_results: int = Field(
        default = 1,
        description="Number of resources to extract")


class WebSearch(BaseSearchTool):
    name = "web_search"
    description = "Search the internet for real-time news."
    args_schema = WebSearchArgs


    async def search(self, **kwargs) -> Dict:
        return {"contents": "Temperature in prague is 20 degree C today",}


if __name__ == "__main__":
    print(WebSearch.get_tool_schema())
