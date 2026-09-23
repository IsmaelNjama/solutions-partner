from langchain_milvus import Milvus
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pymilvus import MilvusClient
from langchain_nebius import NebiusEmbeddings
import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFDirectoryLoader

load_dotenv()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "..", "data/docs")


# def load_documents():
#     loader = PyPDFDirectoryLoader(DATA_DIR)
#     documents = loader.load()
#     print(f"Loaded {len(documents)} documents")
#     return documents

loader = PyPDFDirectoryLoader(DATA_DIR)
documents = loader.load()
print(f"Loaded {len(documents)} documents")

# Run embedding model
EMBEDDING_MODEL = 'Qwen/Qwen3-Embedding-8B'
embeddings = NebiusEmbeddings(
    model=EMBEDDING_MODEL,
    base_url="https://api.tokenfactory.nebius.com/v1/",
    api_key=os.environ.get("NEBIUS_API_KEY")
)


def test_embedding_model():
    try:
        test_vector = embeddings.embed_query("This is a test sentence.")
        print(f"✅ Embedding model loaded successfully")
        print(f"   Vector length: {len(test_vector)}")
        print(f"   First 5 values: {test_vector[:5]}")
        return True
    except Exception as e:
        print(f"❌ Embedding model failed: {e}")
        return False


# Connect Milvus
COLLECTION_NAME = 'rag_search'

client = MilvusClient(
    uri=os.environ.get("SERVING_CLUSTER_ENDPOINT"),
    token=os.environ.get("TOKEN")
)
print("Connected to Instance:")

print(client.list_collections())


# Chunking
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=512, chunk_overlap=51)
texts = text_splitter.split_documents(documents)

# Vector store
vectorstore = Milvus.from_documents(
    documents=texts,
    embedding=embeddings,
    connection_args={
        "uri": os.environ.get("SERVING_CLUSTER_ENDPOINT"),
        "token": os.environ.get("TOKEN"),
    },
    collection_name="rag_search",
    consistency_level="Strong",
    drop_old=True,  # ⚠️ This will drop the existing collection!
    index_params={
        "metric_type": "COSINE",
        "index_type": "AUTOINDEX",
        "params": {},
    }
)

print(f"Created Milvus collection from {len(texts)} docs")

if __name__ == "__main__":
    test_embedding_model()
    # load_documents()
