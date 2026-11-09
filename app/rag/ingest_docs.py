"""
Ingest PDFs into a Milvus collection for RAG.

Usage:
    python ingest_docs.py                       # uses defaults
    python ingest_docs.py --data-dir ./pdfs     # custom folder
    python ingest_docs.py --drop-old            # recreate the collection (destructive!)
    python ingest_docs.py --dry-run             # load + chunk only, no embedding/upload
"""

import argparse
import os
import sys

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_milvus import Milvus
from langchain_nebius import NebiusEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pymilvus import MilvusClient

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA_DIR = os.path.normpath(
    os.path.join(SCRIPT_DIR, "..", "..", "data", "docs")
)

EMBEDDING_MODEL = "Qwen/Qwen3-Embedding-8B"
NEBIUS_BASE_URL = "https://api.tokenfactory.nebius.com/v1/"
DEFAULT_COLLECTION = "rag_search"


def parse_args():
    p = argparse.ArgumentParser(description="Ingest PDFs into Milvus.")
    p.add_argument(
        "--data-dir", default=DEFAULT_DATA_DIR, help="Folder containing PDFs"
    )
    p.add_argument(
        "--collection", default=DEFAULT_COLLECTION, help="Milvus collection name"
    )
    p.add_argument("--chunk-size", type=int, default=512)
    p.add_argument("--chunk-overlap", type=int, default=51)
    p.add_argument(
        "--batch-size", type=int, default=64, help="Chunks embedded/uploaded per batch"
    )
    p.add_argument(
        "--drop-old",
        action="store_true",
        help="Drop the existing collection before ingesting (destructive)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Load and chunk documents only; skip embedding and upload",
    )
    return p.parse_args()


def require_env(*names):
    missing = [n for n in names if not os.environ.get(n)]
    if missing:
        sys.exit(
            f"Missing environment variables: {', '.join(missing)} (check your .env file)"
        )


def load_documents(data_dir):
    if not os.path.isdir(data_dir):
        sys.exit(f"Data directory not found: {data_dir}")
    docs = PyPDFDirectoryLoader(data_dir).load()
    # Drop pages with no extractable text (e.g. scanned images)
    docs = [d for d in docs if d.page_content.strip()]
    print(f"Loaded {len(docs)} non-empty pages from {data_dir}")
    if not docs:
        sys.exit("No text found in PDFs. Scanned files may need OCR first.")
    return docs


def chunk_documents(documents, chunk_size, chunk_overlap):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    chunks = splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks")
    return chunks


def build_embeddings():
    return NebiusEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=NEBIUS_BASE_URL,
        api_key=os.environ["NEBIUS_API_KEY"],
    )


def check_embeddings(embeddings):
    vec = embeddings.embed_query("This is a test sentence.")
    print(f"Embedding model OK (vector length {len(vec)})")


def check_milvus(uri, token):
    client = MilvusClient(uri=uri, token=token)
    print(
        f"Connected to Milvus. Existing collections: {client.list_collections()}")


def ingest(chunks, embeddings, uri, token, collection, batch_size, drop_old):
    store = Milvus(
        embedding_function=embeddings,
        connection_args={"uri": uri, "token": token},
        collection_name=collection,
        consistency_level="Strong",
        drop_old=drop_old,
        auto_id=True,
        index_params={"metric_type": "COSINE",
                      "index_type": "AUTOINDEX", "params": {}},
    )
    total = len(chunks)
    for start in range(0, total, batch_size):
        batch = chunks[start: start + batch_size]
        store.add_documents(batch)
        print(f"  Uploaded {min(start + batch_size, total)}/{total} chunks")
    return store


def main():
    args = parse_args()
    load_dotenv()

    documents = load_documents(args.data_dir)
    chunks = chunk_documents(documents, args.chunk_size, args.chunk_overlap)

    if args.dry_run:
        print("Dry run complete; nothing was embedded or uploaded.")
        return

    require_env("NEBIUS_API_KEY", "SERVING_CLUSTER_ENDPOINT", "TOKEN")
    uri = os.environ["SERVING_CLUSTER_ENDPOINT"]
    token = os.environ["TOKEN"]

    embeddings = build_embeddings()
    check_embeddings(embeddings)
    check_milvus(uri, token)

    if args.drop_old:
        print(f"WARNING: dropping existing collection '{args.collection}'")

    ingest(
        chunks, embeddings, uri, token, args.collection, args.batch_size, args.drop_old
    )
    print(
        f"Done. Collection '{args.collection}' now has content from {len(chunks)} chunks."
    )


if __name__ == "__main__":
    main()
