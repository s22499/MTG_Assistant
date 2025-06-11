import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from services.article_loader import load_documents as load_md, split_text as split_md
from services.json_loader import load_json_documents, split_json_documents
from services.chromadb_service import ChromaDBService

ARTICLE_COLLECTION = "Articles"
JSON_COLLECTION = "Cards"
ARTICLE_PATH = "data/Articles"
JSON_PATH = "data/Cards/oracle-cards-slim2.json"


def initialize_collections():
    # === Initialize Chroma DB service (via HttpClient) ===
    chroma = ChromaDBService()
    
    # === Process Markdown documents ===
    print("Loading and splitting Markdown documents...")
    md_docs = load_md(ARTICLE_PATH)
    md_chunks = split_md(md_docs)
    print(f"Inserting {len(md_chunks)} Markdown chunks into '{ARTICLE_COLLECTION}' collection...")
    chroma.add_documents(collection_name=ARTICLE_COLLECTION, chunks=md_chunks)
    print("Articles succesfuly added to collection")
    
    # === Process JSON document ===
    print("Loading and splitting JSON documents...")
    json_docs = load_json_documents(JSON_PATH)
    json_chunks = split_json_documents(json_docs)
    print(f"Inserting {len(json_chunks)} JSON chunks into '{JSON_COLLECTION}' collection...")
    chroma.add_documents(collection_name=JSON_COLLECTION, chunks=json_chunks)
    print("JSON documents added to collection successfully")
    
    print("Collections initialized successfully.")


if __name__ == "__main__":
    initialize_collections()
