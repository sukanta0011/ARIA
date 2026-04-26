import asyncio
from .llm.ollama import OllamaLLM
from .tools.web_search import WebSearch
from .tools.RAG_search import RAGSearch
from .tools.tool_registry import ToolRegistry
from .agent.state import AgentState
from .agent.researcher import ResearcherAgent
from .agent.planner import PlannerAgent


def create_tool_registry() -> ToolRegistry:
    tools = ToolRegistry()
    tools.register(WebSearch())
    tools.register(RAGSearch())
    return tools


async def main():
    registry = create_tool_registry()
    state = AgentState(query="Search for the current weather in Prague.")

    planner = PlannerAgent(
        llm=OllamaLLM(model="qwen3:0.6b", timeout=120)
    )
    await planner.run(state=state)

    for question in state.sub_questions:
        print(question)
    print(state.total_latency)
    
    jobs = [
        ResearcherAgent(
        llm = OllamaLLM(model="qwen3:0.6b"),
        tools = registry).run(query=q)
        for q in state.sub_questions]
    
    state.research_states = await asyncio.gather(*jobs)

    for state in state.research_states:
        print(state.query)
        print(state.final_answer)
        print(state.total_latency)


if __name__ == "__main__":
    asyncio.run(main())
