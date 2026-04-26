from pydantic import BaseModel, ConfigDict
from ollama import ChatResponse
from typing import Dict
from ..llm.base import BaseLLM
from ..tools.tool_registry import ToolRegistry
from .state import ResearchState
from ..core.config import settings


class ResearcherAgent(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    llm: BaseLLM
    tools: ToolRegistry

    async def run(self, query: str) -> ResearchState:
        state = ResearchState(query=query)
        prompt = f"{state.query}"
        state.history.append({"role": "user", "content": prompt})

        for _ in range(settings.MAX_RECURSION_LIMIT):
            response, latency = await self.llm.execute_chat(
                message=state.history, tools=self.tools.get_all_schemas())
            state.total_latency += latency
            state.iteration_count += 1

            # print(f"{state.iteration_count}: {state.history}")
            # print("-" * 100)

            if isinstance(response, ChatResponse):
                # print(response.message.model_dump())
                state.history.append(response.message.model_dump())
                # tps = self._get_tokens_per_sec(response)

                if not response.message.tool_calls:
                    state.final_answer = str(response.message.content).strip()
                    state.tokens_write += response.eval_count
                    state.tokens_read += response.prompt_eval_count
                    state.status = "completed"

                    return state
                
                await self._handle_tool_calls(
                    state=state, tool_calls=response.message.tool_calls)

            else:
                state.history.append(
                    {
                        "role": "timeout",
                        "contents": response,
                    }
                )

        state.history.append(
                {
                    "role": "error",
                    "content": "Error: Unable to retrieved the answer",
                }
            )
        state.status = "max_iterations_reached"
        return state
    
    async def _handle_tool_calls(
            self, state: ResearchState, tool_calls: Dict
                ) -> None:
        for call in tool_calls:
            tool = self.tools.get_tool(call.function.name)
            result = await tool.search(**call.function.arguments)
            
            state.history.append({
                "role": "tool",
                "content": str(result),
                "tool_name": call.function.name,
            })
            state.tool_used.append(call.function.name)
