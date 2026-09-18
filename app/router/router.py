from langchain_core.prompts import ChatPromptTemplate

from app.llm.router_llm import router_llm
from app.prompts.prompts import router_prompt
from app.schemas.schemas import Route

# Build the router chain once at import time.
# router_llm.with_structured_output(Route) forces the model to return a
# valid Route object (query_docs | web_search | out_of_scope) every time.
_prompt = ChatPromptTemplate.from_messages(
    [("human", router_prompt)]
)

router_chain = _prompt | router_llm.with_structured_output(Route)
