from typing import Optional

from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    query: str = Field(..., description="The user's question or prompt")
    user_id: str = Field(default="anonymous")
    thread_id: Optional[str] = Field(
        default=None,
        description="Optional conversation/thread id. If omitted, a new thread is created.",
    )


class AgentResponse(BaseModel):
    thread_id: str
    response: str
