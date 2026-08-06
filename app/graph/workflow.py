from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from app.llm.llm import llm_with_tools

from langgraph.prebuilt import ToolNode
from app.tools.tools import tools

from langgraph.graph import StateGraph, END

from app.prompts.prompts import agent_prompt
from langchain_core.messages import HumanMessage


class State(TypedDict):
    messages: Annotated[list, add_messages]


async def call_model(state: State):
    messages = state["messages"]
    response = await llm_with_tools.ainvoke(messages)
    return {"messages": [response]}


tool_node = ToolNode(tools)


def should_continue(state: State):
    messages = state["messages"]
    last_message = messages[-1]
    if getattr(last_message, "tool_calls", None):
        return "continue"
    return "end"


workflow = StateGraph(State)
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
    {"continue": "tools", "end": END},
)

workflow.add_edge("tools", "agent")
app = workflow.compile()


async def run_agent():
    prompt = agent_prompt
    inputs = {"messages": [HumanMessage(content=prompt)]}

    print("="*60)
    print("🤖 Agent Streams:")
    print("="*60)

    token_count = 0

    async for event in app.astream_events(inputs, version="v2"):
        kind = event["event"]

        # Stream tokens
        if kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                print(content, end="", flush=True)
                token_count += 1


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_agent())
