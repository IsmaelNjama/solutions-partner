
from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=9000,
                       description="The user's question or prompt")
    user_id: str = Field(default="anonymous")
    thread_id: str | None = Field(
        default=None,
        description="Optional conversation/thread id. If omitted, a new thread is created.",
    )


class AgentResponse(BaseModel):
    thread_id: str
    response: str
