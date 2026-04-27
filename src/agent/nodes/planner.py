from ..state import GraphState, AgentState
from ...llm.ollama import OllamaLLM
from pydantic import BaseModel, ConfigDict
from typing import List
from ollama import ChatResponse
import json
from ...llm.base import BaseLLM
from ..state import AgentState, Questions


async def planner_node(state: GraphState):
    agent_state = AgentState(query=state["query"])

    planner = PlannerAgent(
        llm=OllamaLLM(model="qwen3:0.6b", timeout=120),
        questions=1
    )
    result = await planner.run(state=agent_state)

    return {
        "sub_questions": result.sub_questions,
        "timestamp": result.timestamp,
        "tokens_read": result.tokens_read,
        "token_write": result.tokens_write,
        "total_latency": result.total_latency,
        "status": result.status
    }


class PlannerAgent(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    llm: BaseLLM
    questions: int = 3

    async def run(self, state: AgentState,) -> AgentState:
        prompt = (f"Break down the topic '{state.query}' "
                  f"into {self.questions} sub questions"
                  " to retrieve better answer.")

        message = [{"role": "user", "content": prompt}]

        response, latency = await self.llm.execute_chat(
            message=message, format="json")
        state.total_latency += latency

        if isinstance(response, ChatResponse):
            state.sub_questions = self._extract_sub_question(
                str(response.message.content))
            state.tokens_write += response.eval_count
            state.tokens_read += response.prompt_eval_count
            state.status = "completed"
        else:
            state.status = "error"
        return state

    def _extract_sub_question(
            self, questions: str
                ) -> List[str]:
        results = json.loads(questions)
        all_question = []

        for key, question_list in results.items():
            if "question" in key and isinstance(question_list, list):
                for question in question_list:
                    if isinstance(question, str):
                        all_question.append(
                            Questions(question=question))
                    elif isinstance(question, dict):
                        all_question.extend(
                            [Questions(question=value)
                             for key, value in question.items()
                             if "question" in key])

        return all_question
