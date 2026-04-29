from pydantic import BaseModel
import json
from typing import Literal
from ..state import GraphState
from ...llm.ollama import OllamaLLM


class CriticEvaluation(BaseModel):
    is_approved: bool
    error_type: Literal["research_gap", "synthesis_error", "hallucination", "none"]
    feedback: str


async def critic_node(state: GraphState):

    results = []
    schema = json.dumps(CriticEvaluation.model_json_schema(), indent=2)

    for res in state["research_states"]:
        results.append({
            "question": res.question.question,
            "answer": res.final_answer
        })

    prompt = (f"Research_results: {results}\n"
              f"Question: {state['query']}\n Summery: {state["final_report"]}\n"
              "reviews the answer, identifies the gaps."
              f"Returns in the following format {schema}. Answer >>")

    llm = OllamaLLM(model="qwen3:0.6b", timeout=500)
    response, latency = await llm.execute_chat(
        message=[{"role": "user", "content": prompt}], format="json")

    return {
        "status": response.message.content,
        "tokens_read": response.eval_count,
        "token_write": response.prompt_eval_count,
        "total_latency": latency,
    }
