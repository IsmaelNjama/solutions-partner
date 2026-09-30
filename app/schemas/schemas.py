from typing import Literal

from pydantic import BaseModel


class Route(BaseModel):
    query_type: Literal["web_search", "query_docs", "out_of_scope"]
