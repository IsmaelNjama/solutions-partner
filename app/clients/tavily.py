import os

from dotenv import load_dotenv
from langchain_tavily import TavilySearch

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


_tavily_client = None


def get_tavily_client() -> TavilySearch:
    """
    Lazily initialize the Tavily client.
    """
    global _tavily_client

    if _tavily_client is None:
        if not TAVILY_API_KEY:
            raise RuntimeError(
                "TAVILY_API_KEY is not set. "
                "Please add it to your environment variables or .env file."
            )

        _tavily_client = TavilySearch(
            max_results=5,
            search_depth="basic",
        )

    return _tavily_client
