import os
from langchain_openai import ChatOpenAI
# from tools.tools import tools
from app.tools.tools import tools

from dotenv import load_dotenv

load_dotenv()

tools = tools
llm = ChatOpenAI(
    model="Qwen/Qwen3-235B-A22B-Instruct-2507",
    base_url="https://api.tokenfactory.us-central1.nebius.com/v1/",
    api_key=os.environ.get("NEBIUS_API_KEY"),
    stream_usage=True,
    streaming=True,  # Explicitly enforce streaming behavior
)

llm_with_tools = llm.bind_tools(tools)
