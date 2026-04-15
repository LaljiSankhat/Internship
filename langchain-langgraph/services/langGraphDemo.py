from typing import TypedDict
from langgraph.graph import StateGraph, END

class State(TypedDict):
    message: str


def hello_node(state: State) -> dict:
    print("Node received state:", state)
    return {"message": state["message"] + " → Hello from LangGraph"}

def hello_node_second(state: State) -> dict:
    print("Node received state:", state)
    return {"message": state["message"] + " → Hello from LangGraph node second"}


# Create graph
graph = StateGraph(State)

# Add node
graph.add_node("hello", hello_node)

graph.add_node("hello_2", hello_node_second)

# Define entry point
graph.set_entry_point("hello")

# Define end
graph.add_edge("hello", "hello_2")

graph.add_edge("hello_2", END)

# Compile graph
app = graph.compile()


result = app.invoke({"message": "Start"})
print("Final state:", result)