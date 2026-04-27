import json
from ..state import GraphState
from ...llm.ollama import OllamaLLM


async def evaluator_node(state: GraphState):

    unanswered_question = []
    if state["iteration_count"] > 3:
        print("Maximum Iteration reached, Moving to Synthesizer")
        return [{
            "next_step": "synthesize"
        }]

    for res in state["research_states"]:
        if res.status != "completed":
            unanswered_question.append(res.query)
        else:
            prompt = (
                f"question: {res.query}\n answer: {res.final_answer}\n. "
                "Evaluate the answer based on the question and give "
                "it a score between 1 to 10.\nResponse >> Score: ")
            message = [{"role": "user", "content": prompt}]

            llm = OllamaLLM(model="qwen3:0.6b", timeout=200)
            response, _ = await llm.execute_chat(message=message,format="json")

            response_json = json.loads(response.message.content)
            # print(response_json.items())
            score = response_json.get("score")
            if not score or score < 6:
                unanswered_question.append(res.query)
    
    if len(unanswered_question) > 0:
        print(f"{len(unanswered_question)} remain unanswered, Moving to Planner")
        return {
                "iteration_count": 1,
                "next_step": "refine",
                "failed_questions": unanswered_question
            }
    else:
        return {"next_step": "synthesize", "failed_questions": []}

