import asyncio
from .llm.ollama import OllamaLLM
from .tools.search.web_search import WebSearch
from .tools.tool_registry import ToolRegistry


async def main():
    tools = ToolRegistry()
    tools.register(WebSearch())

    ollama = OllamaLLM()

    # coros = [
    #     ollama.complete('How is the weather today in prague?'),
    # ]

    coros = [
        ollama.complete_with_tools(
            message = 'Search for the current weather in Prague. You can use the tools',
            tools = tools,),
    ]

    responses = await asyncio.gather(*coros)

    for r in responses:
        print(r.response_msg)
        print(r.latency)
        print(r.tokens_per_sec)
        print(r.tools)
        print("_" * 80)



if __name__ == "__main__":
    asyncio.run(main())
