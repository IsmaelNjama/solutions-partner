import os

from langchain_tavily import TavilySearch


_tavily_client = None


def get_tavily_client() -> TavilySearch:
    """
    Lazily initialize the Tavily client.
    """
    global _tavily_client

    if _tavily_client is None:
        if not os.getenv("TAVILY_API_KEY"):
            raise RuntimeError(
                "TAVILY_API_KEY is not set. "
                "Please add it to your environment variables or .env file."
            )

        _tavily_client = TavilySearch(
            max_results=5,
            search_depth="basic",
        )

    return _tavily_client
