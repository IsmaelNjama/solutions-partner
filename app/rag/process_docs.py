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
# if we already have a collection, clear it first
# if client.has_collection(collection_name=COLLECTION_NAME):
#     stats = client.get_collection_stats(collection_name=COLLECTION_NAME)
#     row_count = stats.get('row_count', 0)

#     print(
#         f'⚠️  Collection "{COLLECTION_NAME}" exists with {row_count} entities')
#     confirm = input('Drop and lose all data? (y/n): ').lower()

#     if confirm == 'yes':
#         client.drop_collection(collection_name=COLLECTION_NAME)
#         print('✅ Cleared collection')
#     elif confirm == "no":
#         print('❌ Keeping existing collection')

# Create with auto-generated schema
client.create_collection(
    collection_name=COLLECTION_NAME,
    dimension=4096,
    metric_type="COSINE",
    auto_id=True
)
print('✅ Created collection :', COLLECTION_NAME)

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
    consistency_level="Eventually",
    # drop_old=True,  # ⚠️ This will drop the existing collection!
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
