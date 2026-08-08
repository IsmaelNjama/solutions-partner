# app/api/routes.py

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.api.schemas import AgentRequest, AgentResponse
from app.api.services import run_agent_once, stream_agent_tokens


router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("", response_model=AgentResponse)
async def agent_endpoint(request: AgentRequest):
    """
    Non-streaming agent endpoint.

    Example request:

    {
        "query": "Write a poem about a fairy tale.",
        "user_id": "user-123"
    }
    """
    return await run_agent_once(request)


@router.post("/stream")
async def agent_stream_endpoint(request: AgentRequest):
    """
    Streaming agent endpoint.

    Streams newline-delimited JSON:

    {"type": "token", "content": "Once"}
    {"type": "token", "content": " upon"}
    {"type": "token", "content": " a"}
    ...
    {"type": "done", "thread_id": "..."}
    """
    return StreamingResponse(
        stream_agent_tokens(request),
        media_type="application/x-ndjson",
    )
