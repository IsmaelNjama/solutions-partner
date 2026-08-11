# import time
# from langchain_core.tools import tool

# import os
# from langchain_core.tools import tool
# from langchain_tavily import TavilySearch


# # Initialize the Tavily client
# _tavily = TavilySearch(max_results=5, search_depth="basic")


# @tool
# def web_search(query: str) -> str:
#     """Search the web for real-time information using Tavily. Use this for current events, recent data, or any up-to-date facts."""
#     results = _tavily.invoke({"query": query})
#     # Return a formatted string of results for the LLM
#     output = []
#     for r in results.get("results", []):
#         output.append(f"[{r['title']}]({r['url']})\n{r['content']}")
#     return "\n\n".join(output)


# tools = [web_search]

# app/tools/tools.py

import os

from langchain_core.tools import tool
from langchain_tavily import TavilySearch


_tavily = None


def get_tavily_client():
    """
    Lazily initialize the Tavily client.

    This avoids failing at import time if the environment
    has not been fully loaded yet.
    """
    global _tavily

    if _tavily is None:
        if not os.getenv("TAVILY_API_KEY"):
            raise RuntimeError(
                "TAVILY_API_KEY is not set. "
                "Please add it to your environment variables or .env file."
            )

        _tavily = TavilySearch(
            max_results=5,
            search_depth="basic",
        )

    return _tavily


@tool
def web_search(query: str) -> str:
    """
    Search the web for real-time information using Tavily.

    Use this tool when the user asks for current events, recent data,
    live facts, documentation, news, prices, releases, or anything
    that may require up-to-date external information.
    """
    tavily = get_tavily_client()

    results = tavily.invoke({"query": query})

    output = []

    for result in results.get("results", []):
        title = result.get("title", "Untitled")
        url = result.get("url", "")
        content = result.get("content", "").strip()

        output.append(
            f"[{title}]({url})\n"
            f"{content}"
        )

    if not output:
        return "No search results were found for that query."

    return "\n\n".join(output)


tools = [web_search]
