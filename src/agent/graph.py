from langgraph.graph import StateGraph, END
import asyncio
from .state import GraphState
from .nodes.planner import planner_node
from .nodes.evaluator import evaluator_node
from .nodes.researcher import route_to_research_node, research_node
from .nodes.synthesizer import synthesizer_node
from .nodes.critic import critic_node


workflow = StateGraph(GraphState)

workflow.add_node("planner", planner_node)
workflow.add_node("researcher", research_node)
workflow.add_node("evaluator", evaluator_node)
workflow.add_node("synthesizer", synthesizer_node)
workflow.add_node("critic", critic_node)

workflow.set_entry_point("planner")

workflow.add_conditional_edges(
    "planner", route_to_research_node, ["researcher"]
)
workflow.add_edge(
    "researcher", "evaluator")
workflow.add_conditional_edges(
    "evaluator",
    lambda x: x["next_step"],
    {
        "synthesize": "synthesizer",
        "refine": "planner"
    }
)
workflow.add_edge("synthesizer", "critic")
workflow.add_edge("critic", END)

app = workflow.compile()


async def test_graph():
    # Initial input
    # inputs = {"query": "What is the current weather Prague?"}
    inputs = {"query": "What is the current weather in czech republic?"}

    print("--- 🚀 Starting ARIA Graph Test ---")

    # We use .astream to see the parallel nodes finishing in real-time
    async for output in app.astream(inputs):
        for node_name, state_update in output.items():
            print(f"\n[Node: {node_name}] finished.")
            # If it's a researcher, show which sub-question it finished
            if node_name == "researcher":
                # Remember: research_states is a list
                last_res = state_update["research_states"][-1]
                print(f"   -> Worker ID: '{last_res.worker_id}'")
                print(f"   -> Finished Research for: '{last_res.query}'")
                print(f"   -> Result: {last_res.final_answer}...")
                print(f"   -> Latency: {(last_res.total_latency):.2f}s")
            if node_name == "synthesizer":
                print(f"   -> Final answer: {state_update['final_report']}")
                print(f"   -> Latency: {state_update['total_latency']}")
            if node_name == "critic":
                print(f"   -> Final answer: {state_update['status']}")
                print(f"   -> Latency: {state_update['total_latency']}")


    # # Final Summary
    # final_state = await app.ainvoke(inputs)
    # print("\n--- ✅ Final Graph State Summary ---")
    # print(f"Total Sub-Questions: {len(final_state['sub_questions'])}")
    # print(f"Total Researchers Finished: {len(final_state['research_states'])}")
    # print(f"Total Latency: {final_state['total_latency']:.2f}s")


if __name__ == "__main__":
    asyncio.run(test_graph())
