# from langchain_core.tools import tool

# from app.services.rag_service import retrieve_tech_info as retrieve_tech_info_service
# from app.services.search_service import perform_web_search


# @tool("web_search")
# async def web_search_tool(query: str) -> str:
#     """
#     Search the web for real-time information using Tavily.

#     Use this tool when the user asks for current events, recent data,
#     live facts, documentation, news, prices, releases, or anything
#     that may require up-to-date external information.
#     """
#     return await perform_web_search(query)


# @tool("retrieve_tech_info")
# async def retrieve_tech_info_tool(query: str) -> str:
#     """Search the technical knowledge base for Risco panels information."""
#     return await retrieve_tech_info_service(query)


# # The agent node is a pure synthesis step — it does not call tools.
# # Retrieval and web search are handled exclusively by the workflow router.
# tools = []
