from typing import Annotated

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from app.agent.agent import build_agent


class State(TypedDict):
    messages: Annotated[list, add_messages]


agent = build_agent(checkpointer=None)


workflow = StateGraph(State)

workflow.add_node("agent", agent)
workflow.set_entry_point("agent")
workflow.add_edge("agent", END)


workflow_app = workflow.compile(
    checkpointer=InMemorySaver()
)
