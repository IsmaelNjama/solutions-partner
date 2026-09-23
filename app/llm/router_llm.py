
import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

router_llm = ChatOpenAI(
    model="google/gemma-3-27b-it",
    base_url="https://api.tokenfactory.nebius.com/v1/",
    api_key=os.environ.get("NEBIUS_API_KEY"),
    temperature=0.0,
    max_tokens=20,
)
