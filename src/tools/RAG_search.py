from typing import Dict
from pydantic import BaseModel, Field
from .base import BaseTool


class RAGSearchArgs(BaseModel):
    query: str = Field(
        description="Look for the local shared document through RAG")
    max_results: int = Field(
        default = 1,
        description="Number of resources to extract")


class RAGSearch(BaseTool):
    name = "RAG_search"
    description = "Search for the locally stored info using lexical and semantic search"
    args_schema = RAGSearchArgs


    async def search(self, **kwargs) -> Dict:
        return {"contents": "The info not available",}


if __name__ == "__main__":
    print(RAGSearch.get_tool_schema())
