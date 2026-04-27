import asyncio
from .llm.ollama import OllamaLLM
from .tools.tool_registry import tools
from .agent.state import AgentState
from .agent.nodes.researcher import ResearcherAgent
from .agent.nodes.planner import PlannerAgent


async def main():
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
            tools=tools).run(query=q)
            for q in state.sub_questions]

    state.research_states = await asyncio.gather(*jobs)

    for state in state.research_states:
        print(state.query)
        print(state.final_answer)
        print(state.total_latency)


if __name__ == "__main__":
    asyncio.run(main())
