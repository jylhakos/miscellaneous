"""
Embedding Module for RAG Chatbot
Handles text embedding generation using Hugging Face Sentence Transformers
"""
import logging
from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from langchain.schema import Document

from .config import settings

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generate embeddings for text chunks using Sentence Transformers"""
    
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.embedding_model
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the sentence transformer model"""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def encode_texts(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts"""
        try:
            if not self.model:
                raise ValueError("Model not loaded")
            
            logger.info(f"Generating embeddings for {len(texts)} texts")
            embeddings = self.model.encode(
                texts,
                convert_to_numpy=True,
                show_progress_bar=True
            )
            
            logger.info(f"Generated embeddings with shape: {embeddings.shape}")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    def encode_documents(self, documents: List[Document]) -> np.ndarray:
        """Generate embeddings for LangChain documents"""
        texts = [doc.page_content for doc in documents]
        return self.encode_texts(texts)
    
    def encode_query(self, query: str) -> np.ndarray:
        """Generate embedding for a single query"""
        return self.encode_texts([query])[0]
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embedding vectors"""
        if not self.model:
            raise ValueError("Model not loaded")
        return self.model.get_sentence_embedding_dimension()


# Example usage
if __name__ == "__main__":
    # Initialize embedding generator
    embedder = EmbeddingGenerator()
    
    # Example texts
    texts = [
        "This is a sample document about machine learning.",
        "RAG combines retrieval and generation for better AI responses.",
        "AWS provides cloud services for deploying AI applications."
    ]
    
    # Generate embeddings
    embeddings = embedder.encode_texts(texts)
    print(f"Generated embeddings shape: {embeddings.shape}")
    print(f"Embedding dimension: {embedder.get_embedding_dimension()}")
    
    # Generate query embedding
    query = "What is machine learning?"
    query_embedding = embedder.encode_query(query)
    print(f"Query embedding shape: {query_embedding.shape}")
