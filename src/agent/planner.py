from pydantic import BaseModel, ConfigDict
from typing import List, Dict
from ollama import ChatResponse
import ast
from ..llm.base import BaseLLM
from .state import AgentState


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
        results = ast.literal_eval(questions)
        all_question = []

        for key, question_list in results.items():
            if "question" in key and isinstance(question_list, list):
                for question in question_list:
                    if isinstance(question, str):
                        all_question.append(question)
                    elif isinstance(question, dict):
                        all_question.extend(
                            [value for key, value in question.items() if "question" in key])
                
        return all_question