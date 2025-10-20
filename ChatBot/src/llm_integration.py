"""
LLM Integration Module for RAG Chatbot
Supports both AWS SageMaker and local LLM deployments
"""
import logging
from typing import List, Optional, Dict, Any
import json
import boto3
from langchain.schema import Document

from .config import settings

logger = logging.getLogger(__name__)


class LLMInterface:
    """Base interface for LLM interactions"""
    
    def generate_response(self, prompt: str, context: List[Document]) -> str:
        """Generate response from LLM given prompt and context"""
        raise NotImplementedError


class SageMakerLLM(LLMInterface):
    """AWS SageMaker LLM implementation"""
    
    def __init__(self, endpoint_name: Optional[str] = None):
        self.endpoint_name = endpoint_name or settings.sagemaker_endpoint_name
        self.sagemaker_runtime = boto3.client(
            'sagemaker-runtime',
            region_name=settings.aws_region
        )
    
    def _format_prompt(self, query: str, context_docs: List[Document]) -> str:
        """Format the prompt with context and query"""
        context_text = "\n\n".join([doc.page_content for doc in context_docs])
        
        prompt = f"""You are a helpful AI assistant. Use the following context to answer the user's question. If the answer cannot be found in the context, say "I don't have enough information to answer that question."

Context:
{context_text}

Question: {query}

Answer:"""
        
        return prompt
    
    def generate_response(self, query: str, context: List[Document]) -> str:
        """Generate response using SageMaker endpoint"""
        try:
            # Format prompt
            prompt = self._format_prompt(query, context)
            
            # Prepare payload
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": settings.max_tokens,
                    "temperature": settings.temperature,
                    "do_sample": True,
                    "top_p": 0.9
                }
            }
            
            # Call SageMaker endpoint
            response = self.sagemaker_runtime.invoke_endpoint(
                EndpointName=self.endpoint_name,
                ContentType='application/json',
                Body=json.dumps(payload)
            )
            
            # Parse response
            response_body = json.loads(response['Body'].read().decode())
            
            # Extract generated text
            if isinstance(response_body, list) and len(response_body) > 0:
                generated_text = response_body[0].get('generated_text', '')
            else:
                generated_text = response_body.get('generated_text', '')
            
            # Clean up the response (remove the original prompt)
            if prompt in generated_text:
                generated_text = generated_text.replace(prompt, '').strip()
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Error generating response with SageMaker: {e}")
            return "I apologize, but I encountered an error while generating a response."


class LocalLLM(LLMInterface):
    """Local LLM implementation using Ollama"""
    
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.ollama_model_name
        
        # Import Ollama integration
        try:
            from .ollama_integration import OllamaLLM
            self.ollama_llm = OllamaLLM(self.model_name)
            self.is_available = True
        except ImportError:
            logger.warning("Ollama integration not available. Install with: pip install ollama")
            self.ollama_llm = None
            self.is_available = False
    
    def generate_response(self, query: str, context: List[Document]) -> str:
        """Generate response using local LLM via Ollama"""
        if not self.is_available or not self.ollama_llm:
            return "Local LLM not available. Please ensure Ollama is installed and running."
        
        return self.ollama_llm.generate_response(query, context)


class RAGPipeline:
    """Complete RAG pipeline combining retrieval and generation"""
    
    def __init__(self, vector_db, llm: LLMInterface):
        self.vector_db = vector_db
        self.llm = llm
    
    def query(self, question: str, num_docs: int = 5) -> Dict[str, Any]:
        """Process a query through the complete RAG pipeline"""
        try:
            logger.info(f"Processing query: {question}")
            
            # Step 1: Retrieve relevant documents
            relevant_docs = self.vector_db.search(question, k=num_docs)
            
            if not relevant_docs:
                return {
                    "answer": "I couldn't find any relevant information to answer your question.",
                    "sources": [],
                    "confidence": 0.0
                }
            
            # Extract documents and scores
            docs = [doc for doc, score in relevant_docs]
            scores = [score for doc, score in relevant_docs]
            
            # Step 2: Generate response using LLM
            answer = self.llm.generate_response(question, docs)
            
            # Step 3: Prepare response with sources
            sources = []
            for doc, score in relevant_docs:
                source_info = {
                    "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": score
                }
                sources.append(source_info)
            
            response = {
                "answer": answer,
                "sources": sources,
                "confidence": max(scores) if scores else 0.0,
                "num_sources": len(relevant_docs)
            }
            
            logger.info(f"Generated response with {len(sources)} sources")
            return response
            
        except Exception as e:
            logger.error(f"Error in RAG pipeline: {e}")
            return {
                "answer": "I apologize, but I encountered an error while processing your question.",
                "sources": [],
                "confidence": 0.0
            }


# Example usage
if __name__ == "__main__":
    from .vector_database import VectorDatabase
    
    # Initialize components
    vector_db = VectorDatabase("chroma")
    
    # Choose LLM implementation
    llm = SageMakerLLM()  # or LocalLLM()
    
    # Create RAG pipeline
    rag = RAGPipeline(vector_db, llm)
    
    # Example query
    # response = rag.query("What is machine learning?")
    # print(f"Answer: {response['answer']}")
    # print(f"Confidence: {response['confidence']}")
    # print(f"Sources: {len(response['sources'])}")
