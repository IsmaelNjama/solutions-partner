from langchain.agents import create_agent

from app.tools.tools import tools
from app.utils.context import Context
from app.llm.llm import llm


def build_agent(checkpointer=None):
    return create_agent(
        model=llm,
        tools=tools,
        context_schema=Context,
        checkpointer=checkpointer,
    )
