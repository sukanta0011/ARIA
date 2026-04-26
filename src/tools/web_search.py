from typing import Dict
from pydantic import BaseModel, Field
from datetime import datetime
from .base import BaseTool


class WebSearchArgs(BaseModel):
    query: str = Field(description="Question to be searched in web")
    max_results: int = Field(
        default = 1,
        description="Number of resources to extract")


class WebSearch(BaseTool):
    name = "web_search"
    description = "Search the internet for real-time news."
    args_schema = WebSearchArgs


    async def search(self, **kwargs) -> Dict:
        return {
            "date": datetime.now(),
            "temperature": "20 degree C",
            "humidity": "55%",
            "wind": "2km/h"}


if __name__ == "__main__":
    print(WebSearch.get_tool_schema())
