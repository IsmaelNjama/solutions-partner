import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from app.tools.tools import tools

load_dotenv()

NEBIUS_API_KEY = os.getenv("NEBIUS_API_KEY")


llm = ChatOpenAI(
    model="Qwen/Qwen3-235B-A22B-Instruct-2507",
    base_url="https://api.tokenfactory.us-central1.nebius.com/v1/",
    api_key=NEBIUS_API_KEY,
    stream_usage=True,
    streaming=True,  # Explicitly enforce streaming
)

llm_with_tools = llm.bind_tools(tools)
