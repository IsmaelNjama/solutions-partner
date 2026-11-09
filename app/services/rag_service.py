import os
from functools import lru_cache

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_milvus import Milvus
from langchain_nebius import NebiusEmbeddings

load_dotenv()

EMBEDDING_MODEL = "Qwen/Qwen3-Embedding-8B"
COLLECTION_NAME = "rag_search"


@lru_cache(maxsize=1)
def get_retriever() -> BaseRetriever:
    """Create the Milvus retriever once per process."""
    embeddings = NebiusEmbeddings(
        model=EMBEDDING_MODEL,
        base_url="https://api.tokenfactory.nebius.com/v1/",
        api_key=os.environ.get("NEBIUS_API_KEY"),
    )

    vector_store = Milvus(
        embedding_function=embeddings,
        connection_args={
            "uri": os.environ.get("SERVING_CLUSTER_ENDPOINT"),
            "token": os.environ.get("TOKEN"),
        },
        collection_name=COLLECTION_NAME,
    )

    return vector_store.as_retriever(search_kwargs={"k": 3})


def _format_documents(documents: list[Document]) -> str:
    if not documents:
        return "No relevant technical information was found."

    return "\n\n".join(document.page_content for document in documents)


async def retrieve_tech_info(query: str) -> str:
    """Retrieve relevant Risco panel information from the document store."""
    documents = await get_retriever().ainvoke(query)
    return _format_documents(documents)
