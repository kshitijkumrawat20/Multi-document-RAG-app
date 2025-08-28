from typing import List 
from app.utils.model_loader import ModelLoader
from app.ingestion.file_loader import fileloader
from app.ingestion.text_splitter import splitting_text
from app.retrieval.retriever import Retriever
from app.embedding.embeder import QueryEmbedding
from app.embedding.vectore_store import VectorStore

class RAGService: 
    def __init__(self):
        self._init_models()
        self.vector_store = None

    def _init_models(self):
        """Initialize LLM and embedding Models"""
        self.model_loader = ModelLoader()
        self.llm = self.model_loader.load_llm("gemini")
        self.embedding_model = self.model_loader.load_embedding_model("huggingface")
        
