"""
Ollama Integration Module for Local LLM Inference
Supports Llama 3.x models and other open-source LLMs
"""
import logging
import json
import requests
from typing import List, Dict, Any, Optional
from langchain.schema import Document

from .config import settings

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with Ollama inference server"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model_name: str = "llama3"):
        self.base_url = base_url.rstrip('/')
        self.model_name = model_name
        self.session = requests.Session()
        self.session.timeout = 300  # 5 minutes timeout for generation
        
    def _check_server_health(self) -> bool:
        """Check if Ollama server is running"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List available models in Ollama"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                return response.json().get('models', [])
            return []
        except requests.RequestException as e:
            logger.error(f"Failed to list models: {e}")
            return []
    
    def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama registry"""
        try:
            logger.info(f"Pulling model: {model_name}")
            payload = {"name": model_name}
            
            response = self.session.post(
                f"{self.base_url}/api/pull",
                json=payload,
                stream=True
            )
            
            if response.status_code == 200:
                # Stream the download progress
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line.decode('utf-8'))
                            if 'status' in data:
                                logger.info(f"Pull status: {data['status']}")
                        except json.JSONDecodeError:
                            continue
                logger.info(f"Model {model_name} pulled successfully")
                return True
            else:
                logger.error(f"Failed to pull model: {response.text}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"Error pulling model {model_name}: {e}")
            return False
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using Ollama"""
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get('temperature', 0.7),
                    "num_predict": kwargs.get('max_tokens', 2048),
                    "top_p": kwargs.get('top_p', 0.9),
                    "top_k": kwargs.get('top_k', 40),
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '')
            else:
                logger.error(f"Generation failed: {response.text}")
                return "I apologize, but I encountered an error while generating a response."
                
        except requests.RequestException as e:
            logger.error(f"Error generating with Ollama: {e}")
            return "I apologize, but I couldn't connect to the inference server."
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat with Ollama using conversation format"""
        try:
            payload = {
                "model": self.model_name,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": kwargs.get('temperature', 0.7),
                    "num_predict": kwargs.get('max_tokens', 2048),
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/chat",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('message', {}).get('content', '')
            else:
                logger.error(f"Chat failed: {response.text}")
                return "I apologize, but I encountered an error while generating a response."
                
        except requests.RequestException as e:
            logger.error(f"Error in chat with Ollama: {e}")
            return "I apologize, but I couldn't connect to the inference server."


class OllamaLLM:
    """Enhanced Local LLM implementation using Ollama"""
    
    def __init__(self, model_name: Optional[str] = None, base_url: Optional[str] = None):
        self.model_name = model_name or settings.ollama_model_name
        self.base_url = base_url or settings.ollama_base_url
        self.client = OllamaClient(self.base_url, self.model_name)
        
        # Check server health and model availability
        self._initialize()
    
    def _initialize(self):
        """Initialize Ollama client and ensure model is available"""
        if not self.client._check_server_health():
            logger.warning(f"Ollama server not reachable at {self.base_url}")
            logger.warning("Please ensure Ollama is running: 'ollama serve'")
            return
        
        # Check if model is available
        available_models = self.client.list_models()
        model_names = [model['name'] for model in available_models]
        
        if self.model_name not in model_names:
            logger.info(f"Model {self.model_name} not found. Attempting to pull...")
            if not self.client.pull_model(self.model_name):
                logger.error(f"Failed to pull model {self.model_name}")
        else:
            logger.info(f"Model {self.model_name} is available")
    
    def _format_prompt_with_context(self, query: str, context_docs: List[Document]) -> str:
        """Format prompt for RAG with context documents"""
        context_text = "\n\n".join([
            f"Document {i+1}:\n{doc.page_content}" 
            for i, doc in enumerate(context_docs[:5])  # Limit to top 5 docs
        ])
        
        prompt = f"""You are a helpful AI assistant. Use the following context documents to answer the user's question. If the answer cannot be found in the provided context, say "I don't have enough information in the provided documents to answer that question."

Context Documents:
{context_text}

Question: {query}

Please provide a comprehensive answer based on the context above:"""
        
        return prompt
    
    def _format_chat_messages(self, query: str, context_docs: List[Document]) -> List[Dict[str, str]]:
        """Format messages for chat API with context"""
        context_text = "\n\n".join([
            f"Document {i+1}: {doc.page_content}" 
            for i, doc in enumerate(context_docs[:5])
        ])
        
        system_message = {
            "role": "system",
            "content": """You are a helpful AI assistant that answers questions based on provided context documents. 
            Always cite the document number when referencing information. 
            If the answer cannot be found in the context, clearly state that."""
        }
        
        user_message = {
            "role": "user", 
            "content": f"""Context Documents:
{context_text}

Question: {query}

Please answer based on the provided context:"""
        }
        
        return [system_message, user_message]
    
    def generate_response(self, query: str, context: List[Document]) -> str:
        """Generate response using Ollama with RAG context"""
        try:
            if not self.client._check_server_health():
                return "The inference server is not available. Please ensure Ollama is running."
            
            # Use chat API for better conversation handling
            messages = self._format_chat_messages(query, context)
            
            response = self.client.chat(
                messages=messages,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response with Ollama: {e}")
            return "I apologize, but I encountered an error while generating a response."
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        models = self.client.list_models()
        for model in models:
            if model['name'] == self.model_name:
                return {
                    "name": model['name'],
                    "size": model.get('size', 'Unknown'),
                    "modified": model.get('modified_at', 'Unknown'),
                    "family": model.get('details', {}).get('family', 'Unknown'),
                    "parameter_size": model.get('details', {}).get('parameter_size', 'Unknown')
                }
        return {"name": self.model_name, "status": "Not found"}


# Supported Llama 3.x models for Ollama
SUPPORTED_LLAMA3_MODELS = {
    "llama3:8b": "Meta Llama 3 8B",
    "llama3:8b-instruct": "Meta Llama 3 8B Instruct",
    "llama3:70b": "Meta Llama 3 70B", 
    "llama3:70b-instruct": "Meta Llama 3 70B Instruct",
    "llama3.1:8b": "Meta Llama 3.1 8B",
    "llama3.1:8b-instruct": "Meta Llama 3.1 8B Instruct", 
    "llama3.1:70b": "Meta Llama 3.1 70B",
    "llama3.1:70b-instruct": "Meta Llama 3.1 70B Instruct",
    "llama3.2:1b": "Meta Llama 3.2 1B",
    "llama3.2:3b": "Meta Llama 3.2 3B",
    "llama3.2:11b": "Meta Llama 3.2 11B Vision",
    "llama3.2:90b": "Meta Llama 3.2 90B Vision"
}


def get_recommended_model(use_case: str = "general") -> str:
    """Get recommended Llama 3.x model based on use case"""
    recommendations = {
        "general": "llama3.1:8b-instruct",
        "chat": "llama3.1:8b-instruct", 
        "reasoning": "llama3.1:70b-instruct",
        "vision": "llama3.2:11b",
        "lightweight": "llama3.2:3b",
        "performance": "llama3.1:70b-instruct"
    }
    
    return recommendations.get(use_case, "llama3.1:8b-instruct")


# Example usage and testing
if __name__ == "__main__":
    # Test Ollama connection
    client = OllamaClient()
    
    if client._check_server_health():
        print("✅ Ollama server is running")
        
        models = client.list_models()
        print(f"📋 Available models: {[m['name'] for m in models]}")
        
        # Test generation
        llm = OllamaLLM("llama3.1:8b-instruct")
        
        # Mock context for testing
        from langchain.schema import Document
        test_docs = [
            Document(page_content="The capital of France is Paris."),
            Document(page_content="Paris is known for the Eiffel Tower.")
        ]
        
        response = llm.generate_response("What is the capital of France?", test_docs)
        print(f"🤖 Response: {response}")
        
    else:
        print("❌ Ollama server not reachable")
        print("💡 Start Ollama: 'ollama serve'")
