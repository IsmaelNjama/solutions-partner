import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from app.tools.tools import tools

load_dotenv()

nebius_api_key = os.environ.get("NEBIUS_API_KEY")


llm = ChatOpenAI(
    model="Qwen/Qwen3-30B-A3B-Instruct-2507",
    base_url="https://api.tokenfactory.nebius.com/v1/",
    api_key=nebius_api_key,
    stream_usage=True,
    streaming=True,  # Explicitly enforce streaming
)

llm_with_tools = llm.bind_tools(tools)
