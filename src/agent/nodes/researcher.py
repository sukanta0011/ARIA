from typing import Dict
from langgraph.constants import Send
from ..state import GraphState, ResearchState
from ...llm.ollama import OllamaLLM
from ...tools.tool_registry import tools
from pydantic import BaseModel, ConfigDict
from ollama import ChatResponse
from ...llm.base import BaseLLM
from ...tools.tool_registry import ToolRegistry
from ...core.config import settings


async def route_to_research_node(state: GraphState):
    if state.get("failed_questions"):
        target = state["failed_questions"]
    else:
        target = state["sub_questions"]
    
    return [Send("researcher", {"query": q})
            for q in target]


async def research_node(state: Dict):
    # print(f"question: {state["query"]}")
    agent = ResearcherAgent(llm=OllamaLLM(), tools=tools)
    result: ResearchState = await agent.run(query=state["query"])

    return {
        "research_states": [result],
        "tokens_read": result.tokens_read,
        "tokens_write": result.tokens_write,
    }


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

            # print(f"id: {state.worker_id}")
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
