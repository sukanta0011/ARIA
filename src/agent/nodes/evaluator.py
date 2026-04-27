from ollama import ChatResponse
from ..state import GraphState
from ...llm.ollama import OllamaLLM


async def evaluator_node(state: GraphState):

    for res in state["research_states"]:
        if res.status != "completed":
            pass
        else:
            prompt = (
                f"question: {res.query}\n answer: {res.final_answer}\n. "
                "Evaluate the answer based on the question and give "
                "it a score between 1 to 10.")
            message = [{"role": "user", "content": prompt}]

            llm = OllamaLLM(model="qwen3:0.6b", timeout=200)
            response, _ = await llm.execute_chat(message=message)

            print(response.message.content)
