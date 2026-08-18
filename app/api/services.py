# app/api/services.py

import json
from collections.abc import AsyncGenerator
from uuid import uuid4

from langchain_core.messages import HumanMessage

from app.api.schemas import AgentRequest, AgentResponse
from app.graph.workflow import workflow_app
from app.utils.context import Context


def _prepare_agent_inputs(request: AgentRequest):
    thread_id = request.thread_id or str(uuid4())

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    context = Context(
        user_id=request.user_id,
    )

    inputs = {"messages": [HumanMessage(content=request.query)]}

    return thread_id, config, context, inputs


def _content_to_text(content) -> str:
    """
    LangChain message content can sometimes be a string,
    sometimes a list of content blocks depending on provider/model.
    """
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []

        for part in content:
            if isinstance(part, str):
                parts.append(part)

            elif isinstance(part, dict):
                parts.append(part.get("text", ""))

        return "".join(parts)

    return str(content)


async def run_agent_once(request: AgentRequest) -> AgentResponse:
    """
    Non-streaming endpoint.
    Returns the full final answer.
    """
    thread_id, config, context, inputs = _prepare_agent_inputs(request)

    result = await workflow_app.ainvoke(
        inputs,
        config=config,
        context=context,
    )

    final_message = result["messages"][-1]

    return AgentResponse(
        thread_id=thread_id,
        response=_content_to_text(final_message.content),
    )


async def stream_agent_tokens(request: AgentRequest) -> AsyncGenerator[str]:
    """
    Streaming endpoint.
    Streams tokens back as newline-delimited JSON.
    """
    thread_id, config, context, inputs = _prepare_agent_inputs(request)

    async for event in workflow_app.astream_events(
        inputs,
        config=config,
        context=context,
        version="v2",
    ):
        kind = event["event"]

        if kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content

            if content:
                payload = {
                    "type": "token",
                    "content": _content_to_text(content),
                }

                yield json.dumps(payload) + "\n"

    done_payload = {
        "type": "done",
        "thread_id": thread_id,
    }

    yield json.dumps(done_payload) + "\n"
