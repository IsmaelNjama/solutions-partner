# app/tools/tools.py

from langchain_core.tools import tool

from app.services.search_service import perform_web_search


@tool
async def web_search(query: str) -> str:
    """
    Search the web for real-time information using Tavily.

    Use this tool when the user asks for current events, recent data,
    live facts, documentation, news, prices, releases, or anything
    that may require up-to-date external information.
    """
    return await perform_web_search(query)


tools = [web_search]
