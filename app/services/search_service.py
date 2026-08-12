from app.clients.tavily import get_tavily_client


def search_web(query: str) -> dict:
    """
    Call Tavily search and return raw results.
    """
    client = get_tavily_client()

    return client.invoke({"query": query})


def format_search_results(results: dict) -> str:
    """
    Format Tavily results into a string the LLM can read.
    """
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


def perform_web_search(query: str) -> str:
    """
    Search the web and return formatted results.
    """
    raw_results = search_web(query)

    return format_search_results(raw_results)
