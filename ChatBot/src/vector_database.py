"""
Vector Database Module for RAG Chatbot
Supports multiple vector databases: ChromaDB, FAISS, and Pinecone
"""
import logging
import pickle
from typing import List, Optional, Tuple, Any
from abc import ABC, abstractmethod

import numpy as np
import chromadb
import faiss
from langchain.schema import Document

from .config import settings
from .embeddings import EmbeddingGenerator

logger = logging.getLogger(__name__)


class VectorStore(ABC):
    """Abstract base class for vector stores"""
    
    @abstractmethod
    def add_documents(self, documents: List[Document], embeddings: np.ndarray):
        """Add documents and their embeddings to the store"""
        pass
    
    @abstractmethod
    def similarity_search(self, query_embedding: np.ndarray, k: int = 5) -> List[Tuple[Document, float]]:
        """Search for similar documents"""
        pass
    
    @abstractmethod
    def save(self, path: str):
        """Save the vector store to disk"""
        pass
    
    @abstractmethod
    def load(self, path: str):
        """Load the vector store from disk"""
        pass


class ChromaDBStore(VectorStore):
    """ChromaDB implementation of vector store"""
    
    def __init__(self, collection_name: str = "rag_documents"):
        self.collection_name = collection_name
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        self.documents = []
    
    def add_documents(self, documents: List[Document], embeddings: np.ndarray):
        """Add documents to ChromaDB"""
        try:
            ids = [f"doc_{i}" for i in range(len(documents))]
            texts = [doc.page_content for doc in documents]
            metadatas = [doc.metadata for doc in documents]
            
            self.collection.add(
                ids=ids,
                embeddings=embeddings.tolist(),
                documents=texts,
                metadatas=metadatas
            )
            
            self.documents.extend(documents)
            logger.info(f"Added {len(documents)} documents to ChromaDB")
            
        except Exception as e:
            logger.error(f"Error adding documents to ChromaDB: {e}")
            raise
    
    def similarity_search(self, query_embedding: np.ndarray, k: int = 5) -> List[Tuple[Document, float]]:
        """Search for similar documents in ChromaDB"""
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=k
            )
            
            documents_with_scores = []
            for i, (doc_text, metadata, distance) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )):
                doc = Document(page_content=doc_text, metadata=metadata)
                # Convert distance to similarity score (1 - distance for cosine)
                score = 1 - distance
                documents_with_scores.append((doc, score))
            
            return documents_with_scores
            
        except Exception as e:
            logger.error(f"Error searching ChromaDB: {e}")
            raise
    
    def save(self, path: str):
        """ChromaDB automatically persists data"""
        logger.info("ChromaDB data is automatically persisted")
    
    def load(self, path: str):
        """ChromaDB automatically loads persisted data"""
        logger.info("ChromaDB data is automatically loaded")


class FAISSStore(VectorStore):
    """FAISS implementation of vector store"""
    
    def __init__(self, dimension: int):
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        self.documents = []
    
    def add_documents(self, documents: List[Document], embeddings: np.ndarray):
        """Add documents to FAISS index"""
        try:
            # Normalize embeddings for cosine similarity
            normalized_embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
            self.index.add(normalized_embeddings.astype('float32'))
            self.documents.extend(documents)
            
            logger.info(f"Added {len(documents)} documents to FAISS index")
            
        except Exception as e:
            logger.error(f"Error adding documents to FAISS: {e}")
            raise
    
    def similarity_search(self, query_embedding: np.ndarray, k: int = 5) -> List[Tuple[Document, float]]:
        """Search for similar documents in FAISS"""
        try:
            # Normalize query embedding
            query_embedding = query_embedding / np.linalg.norm(query_embedding)
            query_embedding = query_embedding.reshape(1, -1).astype('float32')
            
            scores, indices = self.index.search(query_embedding, k)
            
            documents_with_scores = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.documents):
                    documents_with_scores.append((self.documents[idx], float(score)))
            
            return documents_with_scores
            
        except Exception as e:
            logger.error(f"Error searching FAISS: {e}")
            raise
    
    def save(self, path: str):
        """Save FAISS index and documents"""
        try:
            faiss.write_index(self.index, f"{path}.index")
            with open(f"{path}.docs", 'wb') as f:
                pickle.dump(self.documents, f)
            logger.info(f"Saved FAISS store to {path}")
        except Exception as e:
            logger.error(f"Error saving FAISS store: {e}")
            raise
    
    def load(self, path: str):
        """Load FAISS index and documents"""
        try:
            self.index = faiss.read_index(f"{path}.index")
            with open(f"{path}.docs", 'rb') as f:
                self.documents = pickle.load(f)
            logger.info(f"Loaded FAISS store from {path}")
        except Exception as e:
            logger.error(f"Error loading FAISS store: {e}")
            raise


class VectorDatabase:
    """Main vector database interface"""
    
    def __init__(self, store_type: str = None):
        self.store_type = store_type or settings.vector_db_type
        self.embedder = EmbeddingGenerator()
        self.store = None
        self._initialize_store()
    
    def _initialize_store(self):
        """Initialize the appropriate vector store"""
        if self.store_type == "chroma":
            self.store = ChromaDBStore()
        elif self.store_type == "faiss":
            dimension = self.embedder.get_embedding_dimension()
            self.store = FAISSStore(dimension)
        elif self.store_type == "pinecone":
            # Note: Pinecone implementation would require pinecone-client
            raise NotImplementedError("Pinecone implementation not included in this example")
        else:
            raise ValueError(f"Unsupported vector store type: {self.store_type}")
        
        logger.info(f"Initialized {self.store_type} vector store")
    
    def add_documents(self, documents: List[Document]):
        """Add documents to the vector database"""
        try:
            # Generate embeddings
            embeddings = self.embedder.encode_documents(documents)
            
            # Add to store
            self.store.add_documents(documents, embeddings)
            
            logger.info(f"Added {len(documents)} documents to vector database")
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def search(self, query: str, k: int = 5) -> List[Tuple[Document, float]]:
        """Search for relevant documents"""
        try:
            # Generate query embedding
            query_embedding = self.embedder.encode_query(query)
            
            # Search in store
            results = self.store.similarity_search(query_embedding, k)
            
            logger.info(f"Found {len(results)} relevant documents for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise
    
    def save(self, path: str = "./vector_store"):
        """Save the vector store"""
        self.store.save(path)
    
    def load(self, path: str = "./vector_store"):
        """Load the vector store"""
        self.store.load(path)


# Example usage
if __name__ == "__main__":
    from .document_processor import DocumentProcessor
    
    # Initialize components
    processor = DocumentProcessor()
    vector_db = VectorDatabase("chroma")
    
    # Example: Process and add documents
    # documents = processor.process_documents(["./documents/sample.pdf"])
    # vector_db.add_documents(documents)
    
    # Example: Search
    # results = vector_db.search("What is machine learning?", k=3)
    # for doc, score in results:
    #     print(f"Score: {score:.3f}")
    #     print(f"Content: {doc.page_content[:200]}...")
    #     print("---")
