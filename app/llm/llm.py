import json
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from app.tools.tools import tools

load_dotenv()

secret_string = os.getenv("NEBIUS_API_KEY")

if not secret_string:
    raise RuntimeError("NEBIUS_API_KEY is not set")


try:
    parsed = json.loads(secret_string)
    NEBIUS_API_KEY = parsed["NEBIUS_API_KEY"]
except (json.JSONDecodeError, TypeError, KeyError):
    NEBIUS_API_KEY = secret_string

llm = ChatOpenAI(
    model="Qwen/Qwen3-235B-A22B-Instruct-2507",
    base_url="https://api.tokenfactory.us-central1.nebius.com/v1/",
    api_key=NEBIUS_API_KEY,
    stream_usage=True,
    streaming=True,
)

llm_with_tools = llm.bind_tools(tools)
