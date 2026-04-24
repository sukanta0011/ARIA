import pytest
import asyncio
from src.llm.ollama import OllamaLLM
from src.llm.base import LLMResponse

@pytest.fixture
def llm():
    return OllamaLLM(model="qwen3:0.6b", time_out=20)


@pytest.mark.asyncio
async def test_single_prompt(llm):
    response = await llm.complete("Hello")
    assert response.response_msg is not None


@pytest.mark.asyncio
async def test_ollama_concurrency(llm):
    coros = [
        llm.complete('Why is the sky blue?'),
        llm.complete('Why is the sea blue?'),
        llm.complete('Why is TCP/IP?'),
        llm.complete('Why is UDP?'),
    ]

    responses = await asyncio.gather(*coros)

    assert len(responses) == 4
    for resp in responses:
        assert isinstance(resp, LLMResponse)
        assert resp.response_msg is not None
        assert len(resp.response_msg) > 0
        print(resp.response_msg)
        assert resp.latency > 0
        print(resp.latency)
        print("-" * 100)
