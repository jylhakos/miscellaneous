"""
RAG Chatbot Package
A complete Retrieval-Augmented Generation chatbot implementation
"""

__version__ = "1.0.0"
__author__ = "RAG Chatbot Team"

from .config import settings
from .document_processor import DocumentProcessor
from .embeddings import EmbeddingGenerator
from .vector_database import VectorDatabase
from .llm_integration import RAGPipeline, SageMakerLLM, LocalLLM

__all__ = [
    "settings",
    "DocumentProcessor",
    "EmbeddingGenerator", 
    "VectorDatabase",
    "RAGPipeline",
    "SageMakerLLM",
    "LocalLLM"
]
