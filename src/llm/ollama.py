from typing import Dict, List, Tuple
from pydantic import BaseModel
import asyncio
import time
from ollama import chat, ChatResponse, AsyncClient
from .base import BaseLLM
from .base import ValidMessage, LLMResponse


class OllamaLLM(BaseLLM):
    def __init__(
            self, model: str = "qwen3:0.6b",
            max_parallel: int = 1, time_out: int = 10
            ) -> None:

        self.model = model
        self.bouncer = asyncio.Semaphore(max_parallel)
        self.timeout = time_out
        self.client = AsyncClient()

    async def _execute_chat(
            self, message: List[Dict]
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
                        format="json",
                    ),
                    timeout=self.timeout
                )
                end = time.perf_counter()
                latency = round(end - start, 2)
                return response, latency
            except asyncio.TimeoutError:
                return (f'"error": "Request timed out ({self.timeout}s)", '
                        f'"query": {message[0]["content"]}', self.timeout)

    async def complete(self, message: ValidMessage) -> LLMResponse:
        formatted_msg = [{"role": "user", "content": message}]
        response, latency = await self._execute_chat(formatted_msg)
        if isinstance(response, ChatResponse):
            if response.eval_count and response.eval_duration:
                tps = round(response.eval_count / (
                    response.eval_duration / 1e9), 1)
            else:
                tps = 0.0

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
            self, message: ValidMessage, tools: List[Dict]):
        pass


async def test_ollama():
    ollama = OllamaLLM(time_out=30)

    coros = [
        ollama.complete('Why is the sky blue?'),
        ollama.complete('Why is the sea blue?'),
        ollama.complete('Why is TCP/IP?'),
        ollama.complete('Why is UDP?'),
    ]

    responses = await asyncio.gather(*coros)

    for r in responses:
        print(r.response_msg)
        print(r.latency)
        print(r.tokens_per_sec)
        print("_" * 100)


if __name__ == "__main__":
    asyncio.run(test_ollama())
