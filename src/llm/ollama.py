from typing import Dict, List, Tuple
# from pydantic import BaseModel
import asyncio
import time
from ollama import ChatResponse, AsyncClient
from .base import BaseLLM
from .base import ValidMessage, LLMResponse, LLMResponseTools
# from ..tools.search.base import BaseSearchTool
from ..tools.search.web_search import WebSearch
from ..tools.tool_registry import ToolRegistry
from ..core.config import settings


class OllamaLLM(BaseLLM):
    def __init__(self) -> None:
        self.model = settings.MODEL_NAME
        self.bouncer = asyncio.Semaphore(settings.MAX_PARALLEL_REQUESTS)
        self.timeout = settings.LLM_TIMEOUT
        self.client = AsyncClient()

    async def _execute_chat(
            self, message: List[Dict], tools: List[Dict] | None = None
                ) -> Tuple[ChatResponse, float] | Tuple[str, float]:
        async with self.bouncer:
            client = AsyncClient()
            try:
                start = time.perf_counter()
                response: ChatResponse = await asyncio.wait_for(
                    client.chat(
                        model=self.model,
                        messages=message,
                        think="low",
                        tools=tools
                    ),
                    timeout=self.timeout
                )
                end = time.perf_counter()
                latency = round(end - start, 2)
                return response, latency
            except asyncio.TimeoutError:
                return (f'"error": "Request timed out ({self.timeout}s)", '
                        f'"query": {message[0]["content"]}', self.timeout)

    def _get_tokens_per_sec(self, response: ChatResponse) -> float:
        if response.eval_count and response.eval_duration:
            tps = round(response.eval_count / (
                    response.eval_duration / 1e9), 1)
        else:
            tps = 0.0
        return tps

    async def complete(self, message: ValidMessage) -> LLMResponse:
        formatted_msg = [{"role": "user", "content": message}]
        response, latency = await self._execute_chat(formatted_msg)
        if isinstance(response, ChatResponse):
            tps = self._get_tokens_per_sec(response)

            return LLMResponse(
                    msg=message,
                    response_msg=str(response.message.content).strip(),
                    read_token=response.prompt_eval_count,
                    write_token=response.eval_count,
                    latency=latency,
                    tokens_per_sec=tps
                )
        else:
            return LLMResponse(
                msg=message,
                response_msg=response,
                latency=latency,
            )

    async def complete_with_tools(
            self, message: ValidMessage, tools: ToolRegistry
                ) -> LLMResponseTools:
        history = [{"role": "user", "content": message}]

        response, latency = await self._execute_chat(
            message=history, tools=tools.get_all_schemas())

        if isinstance(response, ChatResponse):
            print(response.message.model_dump())
            history.append(response.message.model_dump())
            tps = self._get_tokens_per_sec(response)
            response_msg = str(response.message.content).strip()

            if not response.message.tool_calls:
                return LLMResponseTools(
                    msg=message,
                    response_msg=response_msg,
                    read_token=response.prompt_eval_count,
                    write_token=response.eval_count,
                    latency=latency,
                    tokens_per_sec=tps,
                    tools=response.message.tool_calls
                )

            for call in response.message.tool_calls:
                tool_name = call.function.name
                args = call.function.arguments

                tool_instance = tools.get_tool(tool_name)

                tool_result = await tool_instance.search(**args)

                history.append(
                    {
                        "role": "tool",
                        "content": str(tool_result),
                        "tool_name": call.function.name
                    }
                )
            return LLMResponseTools(
                msg=message,
                response_msg="Error: Unable to receive the answer",
                latency=latency,
            )

        else:
            return LLMResponseTools(
                msg=message,
                response_msg=response,
                latency=latency,
            )


async def test_ollama():
    ollama = OllamaLLM(model='qwen3:4b',time_out=120)

    # coros = [
    #     ollama.complete('How is the weather today in prague?'),
    # ]

    coros = [
        ollama.complete_with_tools(
            message = 'Search for the current weather in Prague. You can use the tools',
            tools = [WebSearch.get_tool_schema(),]),
    ]

    responses = await asyncio.gather(*coros)

    for r in responses:
        print(r.response_msg)
        print(r.latency)
        print(r.tokens_per_sec)
        print(r.tools)
        print("_" * 80)


if __name__ == "__main__":
    asyncio.run(test_ollama())
