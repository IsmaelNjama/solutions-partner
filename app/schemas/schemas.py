from pydantic import BaseModel, Field

from typing import Literal


class Route(BaseModel):
    query_type: Literal[
        "web_search",
        "query_docs",
        "out_of_scope"
    ]
