import json
from ..state import GraphState, Question
from ...llm.ollama import OllamaLLM


async def evaluator_node(state: GraphState):

    unanswered_questions = []
    unanswered_questions_ids = set()
    if state["iteration_count"] > 3:
        print("Maximum Iteration reached, Moving to Synthesizer")
        return {
            "next_step": "synthesize",
        }

    # print("-" * 100)
    for res in state["research_states"]:
        if (res.status != "completed" or len(res.final_answer) <= 0) and\
                res.question.question_id not in state["failed_question_ids"]:
            # print(f"{res.question.question_id}: {res.question.question}")
            unanswered_questions_ids.add(res.question.question_id)
            unanswered_questions.append(
                Question(question=res.question.question))

    # print(state["failed_question_ids"])
    # print("-" * 100)
    if len(unanswered_questions) > 0:
        print(f"{len(unanswered_questions)} remain unanswered, Moving to Planner")
        return {
                "iteration_count": 1,
                "next_step": "refine",
                "question_registry": {
                    q.question_id: q for q in unanswered_questions},
                "failed_question_ids": unanswered_questions_ids
            }
    else:
        return {"next_step": "synthesize"}
