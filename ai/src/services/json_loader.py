from langchain.document_loaders import JSONLoader
from langchain.schema import Document
from langchain_text_splitters import RecursiveJsonSplitter
from typing import List

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
        max_chunk_size=max_chunk_size,
        chunk_overlap=0,
        keep_separator=True
    )

    chunks = splitter.split_documents(documents)
    print(f"Split {len(documents)} JSON documents into {len(chunks)} chunks.")
    return chunks

