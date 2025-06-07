from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter, SentenceTransformersTokenTextSplitter, MarkdownHeaderTextSplitter
from langchain.schema import Document

def load_documents(DATA_PATH):
    loader = DirectoryLoader(
        DATA_PATH,
        glob="**/*.md",       
        recursive=True       
    )
    documents =  loader.load()
    return documents

def split_text(documents: list[Document]) -> list[Document]:
    splitter = SentenceTransformersTokenTextSplitter(
        chunk_overlap=20,
        tokens_per_chunk=256,
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    chunks = []
    for doc in documents:
        split = splitter.split_documents([doc])
        for chunk in split:
            chunk.metadata = doc.metadata
        chunks.extend(split)

    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")
    return chunks

