from langchain.agents import create_agent

from app.llm.llm import llm
from app.prompts.prompts import agent_prompt
from app.tools.tools import tools
from app.utils.context import Context


def build_agent(checkpointer=None):
    return create_agent(
        model=llm,
        tools=tools,
        context_schema=Context,
        checkpointer=checkpointer,
        system_prompt=agent_prompt,
    )
