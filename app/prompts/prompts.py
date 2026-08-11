# app/prompts/prompts.py

system_prompt = (
    "You are a helpful research assistant with access to a web_search tool. "
    "Use the web_search tool whenever the user asks about current events, "
    "recent information, news, documentation, prices, releases, or facts "
    "that may not be part of your internal knowledge. "
    "Search using concise, targeted queries. "
    "If the first search does not produce enough information, refine the query and search again. "
    "Base your answer on the retrieved search results. "
    "Include source URLs when useful. "
    "If you cannot find reliable information, say so clearly."
)


def build_research_prompt(user_query: str) -> str:
    """
    Build a prompt that tells the agent to research the user's query
    using the web_search tool.
    """
    return (
        "Use the web_search tool to research the following request.\n\n"
        f"User request:\n{user_query}\n\n"
        "Instructions:\n"
        "1. Call web_search with a focused search query.\n"
        "2. If the results are incomplete or unclear, refine the query and search again.\n"
        "3. Answer using only the relevant information from the search results.\n"
        "4. Include source URLs when helpful.\n"
        "5. If no useful results are found, say so clearly.\n"
    )


agent_prompt = system_prompt
