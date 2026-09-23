from typing import Annotated

from langchain_core.messages import ToolMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from app.agent.agent import build_agent
from app.router.router import router_chain
from app.schemas.schemas import Route
from app.services.rag_service import retrieve_tech_info
from app.services.search_service import perform_web_search


class State(TypedDict):
    input: str
    messages: Annotated[list, add_messages]
    query_type: str
    output: str


# Router node

def make_router_node(chain):
    """Return a LangGraph node that classifies the user query."""

    def router_node(state: State) -> dict:
        messages = state.get("messages", [])

        user_input = state.get("input") or (
            messages[-1].content if messages else ""
        )

        # History = all messages except the current one
        history = "\n".join(msg.content for msg in messages[:-1])

        result: Route = chain.invoke(
            {
                "input": user_input,
                "history": history,
            }
        )

        print(f"[Router] query_type={result.query_type!r}")

        return {"query_type": result.query_type}

    return router_node


def route_after_router(state: State) -> str:
    """Conditional edge: fan out based on the router's decision."""
    query_type = state.get("query_type", "out_of_scope")
    print(f"[Router edge] routing to → {query_type!r}")

    if query_type == "query_docs":
        return "retrieve"
    if query_type == "web_search":
        return "web_search"
    return "agent"


# Retrieval nodes  (plain async — no ToolNode, no AIMessage dependency)


async def retrieve_node(state: State) -> dict:
    """Query the Milvus knowledge base and add the result to messages."""
    messages = state.get("messages", [])
    user_input = state.get("input") or (
        messages[-1].content if messages else ""
    )

    print(f"[retrieve_node] querying docs for: {user_input!r}")
    result = await retrieve_tech_info(user_input)

    return {
        "messages": [
            ToolMessage(content=result, tool_call_id="retrieve_tech_info")
        ]
    }


async def web_search_node(state: State) -> dict:
    """Run a Tavily web search and add the result to messages."""
    messages = state.get("messages", [])
    user_input = state.get("input") or (
        messages[-1].content if messages else ""
    )

    print(f"[web_search_node] searching web for: {user_input!r}")
    result = await perform_web_search(user_input)

    return {
        "messages": [
            ToolMessage(content=result, tool_call_id="web_search")
        ]
    }


# Build the graph

agent = build_agent(checkpointer=None)

workflow = StateGraph(State)

workflow.add_node("router", make_router_node(router_chain))
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("web_search", web_search_node)
workflow.add_node("agent", agent)

workflow.set_entry_point("router")

workflow.add_conditional_edges(
    "router",
    route_after_router,
    {
        "retrieve": "retrieve",
        "web_search": "web_search",
        "agent": "agent",
    },
)

# Both retrieval paths converge on the agent for final synthesis.
workflow.add_edge("retrieve", "agent")
workflow.add_edge("web_search", "agent")
workflow.add_edge("agent", END)

workflow_app = workflow.compile(checkpointer=InMemorySaver())
