from langchain_chroma import Chroma
from config.config_manager import ConfigManager
from langchain_openai import OpenAIEmbeddings
import os
import chromadb
from chromadb.config import Settings
from langchain.schema import Document

class ChromaDBService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChromaDBService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config_path: str = os.path.join(os.path.dirname(__file__), "../../config/config.yaml")):
        if getattr(self, "_initialized", False):
            return
        config_manager = ConfigManager(config_path)
        chroma_host = config_manager.get_value("chroma.host", "data")
        chroma_port = config_manager.get_value("chroma.port", 8000)

        # Use chromadb HttpClient for REST API
        self._client = chromadb.HttpClient(
            host=chroma_host,
            port=chroma_port,
            settings=Settings(allow_reset=True, anonymized_telemetry=False)
        )
        self._collections = {}

        # Get OpenAI API key from environment variable
        _openai_api_key = os.environ.get("OPENAI_API_KEY")
        if not _openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")

        # Get embedding model from config, default to 'text-embedding-3-small'
        _embedding_model = config_manager.get_value("chroma.embedding_model", "text-embedding-3-small")

        # Use OpenAI embeddings with the specified model
        self._embedding_function = OpenAIEmbeddings(
            openai_api_key=_openai_api_key,
            model=_embedding_model
        )

        self._initialized = True
        print(f"Connected to Chroma DB at: {chroma_host}:{chroma_port} using model: {_embedding_model}")

    def get_collection(self, collection_name: str) -> Chroma:
        """Get or create a Chroma collection by name."""
        if collection_name not in self._collections:
            self._collections[collection_name] = Chroma(
                collection_name=collection_name,
                embedding_function=self._embedding_function,
                client=self._client,
                create_collection_if_not_exists=True
            )
        return self._collections[collection_name]

    def add_documents(
        self,
        collection_name: str,
        chunks: list[Document],
        metadatas: list[dict] = None,
        ids: list[str] = None,
        batch_size: int = 100
    ):
        """Add documents to the specified collection in batches."""
        collection = self.get_collection(collection_name)

        for i in range(0, len(chunks), batch_size):
            batch_docs = chunks[i:i + batch_size]
            batch_ids = ids[i:i + batch_size] if ids else None
            batch_metadatas = metadatas[i:i + batch_size] if metadatas else None

            collection.add_documents(
                documents=batch_docs,
                ids=batch_ids
            )
            print(f"Uploading batch {i // batch_size + 1}")
            
    def reset_collection(self, name: str):
        """Delete and recreate the collection"""
        self._client.delete_collection(name)
        self._collections.pop(name, None)
        self.get_collection(name)

