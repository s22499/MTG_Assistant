from langchain_community.document_loaders import JSONLoader
from langchain.schema import Document
from langchain_text_splitters import RecursiveJsonSplitter
from typing import List
import json

def load_json_documents(json_path: str) -> List[Document]:

    loader = JSONLoader(
        file_path=json_path,
        jq_schema=".[]",
        text_content=False,
    )

    documents = loader.load()
    print(f"Loaded {len(documents)} JSON documents from {json_path}")
    return documents


def split_json_documents(documents: List[Document], max_chunk_size: int = 1000) -> List[Document]:

    splitter = RecursiveJsonSplitter(
        max_chunk_size=max_chunk_size
    )

    print(f"Splitting {len(documents)} JSON documents...")


    all_chunks = []
    for i, doc in enumerate(documents):
        try:
            json_obj = json.loads(doc.page_content)
            chunks = splitter.create_documents([json_obj])
            all_chunks.extend(chunks)
        except Exception as e:
            print(f"❌ Error splitting document at index {i}: {e}")
            print(f"Problematic document: {doc}")


    print(f"Split {len(documents)} JSON documents into {len(chunks)} chunks.")
    return all_chunks

