import pytest
import asyncio
from ollama import ChatResponse
from src.llm.ollama import OllamaLLM
from src.llm.base import LLMResponse
from src.tools.web_search import WebSearch
from src.tools.RAG_search import RAGSearch
from src.tools.tool_registry import ToolRegistry
from src.tools.base import BaseTool
from src.agent.state import AgentState
from src.agent.researcher import ResearcherAgent
from src.agent.planner import PlannerAgent


@pytest.fixture
def llm():
    return OllamaLLM()


@pytest.fixture
def tools() -> ToolRegistry:
    tools = ToolRegistry()
    tools.register(WebSearch())
    tools.register(RAGSearch())
    return tools


@pytest.mark.asyncio
async def test_single_prompt(llm):
    msg = [{"role": "user", "content": "Hello"}]
    response, _ = await llm.execute_chat(msg)
    assert response.message.content is not None
    print(response.message.content)


@pytest.mark.parametrize("iteration", range(5))
@pytest.mark.asyncio
async def test_ollama_web_search(llm, tools, iteration):
    from src.agent.researcher import ResearcherAgent

    research_agent = ResearcherAgent(
        llm = llm, tools = tools)
    
    state: ResearcherAgent = await research_agent.run(
        query="What is the weather in prague?")

    # print(state)
    assert len(state.tool_used) > 0
    assert "web_search" in state.tool_used
    assert len(state.final_answer) > 0
    print(f"Run {iteration} latency: {state.total_latency}")
    assert state.status == "completed"


@pytest.mark.asyncio
async def test_planner_agent(llm):
    state = AgentState(
        query="Search for the current weather in Prague.")

    planner = PlannerAgent(
        llm=llm, questions=3
        )
    await planner.run(state=state)

    # assert len(state.sub_questions) == 3
    print(state.sub_questions)
