from ..state import GraphState
from ...llm.ollama import OllamaLLM


async def synthesizer_node(state: GraphState):

    results = []

    for res in state["research_states"]:
        results.append({
            "question": res.question.question,
            "answer": res.final_answer
        })

    prompt = (f"{results}\n Original question: {state['query']}\n"
              "Provide a summarized answer. Answer>>")

    llm = OllamaLLM(model="qwen3:0.6b", timeout=200)
    response, latency = await llm.execute_chat(
        message=[{"role": "user", "content": prompt}])

    return {
        "final_report": response.message.content,
        "tokens_read": response.eval_count,
        "token_write": response.prompt_eval_count,
        "total_latency": latency,
    }
