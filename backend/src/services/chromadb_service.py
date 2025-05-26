from langchain_chroma import Chroma
from src.config.config_manager import ConfigManager
from langchain_openai import OpenAIEmbeddings
import os
import chromadb
from chromadb.config import Settings


class ChromaDBService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChromaDBService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, config_path: str = "src/config/config.yaml"):
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
    
    def add_documents(self, collection_name: str, documents: list[str], metadatas: list[dict] = None, ids: list[str] = None):
        """Add documents to the specified collection."""
        collection = self.get_collection(collection_name)
        return collection.add_texts(documents, metadatas=metadatas, ids=ids)

    def reset_collection(self, name: str):
        """Delete and recreate the collection"""
        self._client.delete_collection(name)
        self._collections.pop(name, None)
        self.get_collection(name)
