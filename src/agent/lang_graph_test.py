from typing import TypedDict
from langgraph.graph import StateGraph, END


class GreetState(TypedDict):
    name: str
    message: str


def check_identity(state: GreetState):
    # Node 1: Only decides the message
    if state["name"].lower() == "admin":
        return {"message": "Access Granted"}
    return {"message": f"Hello {state['name']}"}


def logger(state: GreetState):
    # Node 2: Just prints
    print(f"LOG: Greeting sent - {state['message']}")
    return {}



# 1. Initialize the "Factory Floor"
workflow = StateGraph(GreetState)

# 2. Place the Workstations
workflow.add_node("ident_check", check_identity)
workflow.add_node("log_step", logger)

# 3. Connect the Belts
workflow.set_entry_point("ident_check") # Where it starts
workflow.add_edge("ident_check", "log_step") # Next step
workflow.add_edge("log_step", END) # Where it finishes

# 4. Compile the Factory
app = workflow.compile()


import asyncio

async def run_example():
    # Provide the initial state
    inputs = {"name": "Gemini"} 
    
    # Run the graph
    # .ainvoke is the async version of .invoke
    final_state = await app.ainvoke(inputs)
    
    print("--- Final State Result ---")
    print(final_state)


async def stream_example():
    inputs = {"name": "User"}
    
    print("--- Starting Stream ---")
    async for output in app.astream(inputs):
        # 'output' is a dictionary where keys are node names 
        # and values are the updates they made
        for node_name, state_update in output.items():
            print(f"Node '{node_name}' finished. Update: {state_update}")
    print("--- Stream Finished ---")


if __name__ == "__main__":
    asyncio.run(run_example())