#!/usr/bin/env python3
"""
Ollama integration example for RAG Chatbot
Demonstrates local LLM inference with Llama 3.x models
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from ollama_integration import OllamaLLM, OllamaClient, SUPPORTED_LLAMA3_MODELS, get_recommended_model
from vector_database import VectorDatabase
from llm_integration import RAGPipeline
from document_processor import DocumentProcessor
from langchain.schema import Document


def check_ollama_setup():
    """Check if Ollama is properly set up"""
    print("🔍 Checking Ollama setup...")
    
    client = OllamaClient()
    
    # Check server health
    if not client._check_server_health():
        print("❌ Ollama server not reachable at http://localhost:11434")
        print("💡 Please start Ollama:")
        print("   1. Install: curl -fsSL https://ollama.ai/install.sh | sh")
        print("   2. Start server: ollama serve")
        return False
    
    print("✅ Ollama server is running")
    
    # List available models
    models = client.list_models()
    model_names = [model['name'] for model in models]
    
    print(f"📋 Available models: {model_names}")
    
    # Check for recommended model
    recommended = get_recommended_model("chat")
    if recommended not in model_names:
        print(f"📥 Recommended model '{recommended}' not found")
        print(f"💡 Download with: ollama pull {recommended}")
        return False
    
    print(f"✅ Recommended model '{recommended}' is available")
    return True


def demonstrate_basic_generation():
    """Demonstrate basic text generation with Ollama"""
    print("\nTesting basic generation...")
    
    try:
        # Initialize LLM
        llm = OllamaLLM("llama3.1:8b-instruct")
        
        # Test simple generation without context
        test_docs = [Document(page_content="This is a test document for demonstration.")]
        
        response = llm.generate_response(
            "What is the purpose of this test?",
            test_docs
        )
        
        print(f"✅ Response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        return False


def demonstrate_rag_pipeline():
    """Demonstrate full RAG pipeline with Ollama"""
    print("\nTesting RAG pipeline...")
    
    try:
        # Initialize components
        vector_db = VectorDatabase("chroma")  # Use ChromaDB for local testing
        llm = OllamaLLM("llama3.1:8b-instruct")
        
        # Create test documents
        test_documents = [
            "Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed.",
            "Deep learning uses neural networks with multiple layers to model and understand complex patterns in data.",
            "Natural language processing (NLP) is a branch of AI that helps computers understand, interpret, and manipulate human language.",
            "The transformer architecture revolutionized NLP by introducing the attention mechanism for better context understanding."
        ]
        
        # Add documents to vector database
        print("Adding test documents to vector database...")
        for i, content in enumerate(test_documents):
            doc = Document(
                page_content=content,
                metadata={"source": f"test_doc_{i}", "type": "educational"}
            )
            vector_db.add_documents([doc])
        
        # Create RAG pipeline
        rag = RAGPipeline(vector_db, llm)
        
        # Test queries
        test_queries = [
            "What is machine learning?",
            "How does deep learning work?",
            "What is the transformer architecture?",
            "Explain natural language processing"
        ]
        
        for query in test_queries:
            print(f"\n❓ Query: {query}")
            
            response = rag.query(query, num_docs=3)
            
            print(f"🤖 Answer: {response['answer']}")
            print(f"Confidence: {response['confidence']:.2f}")
            print(f"📚 Sources used: {response['num_sources']}")
            
            # Show source information
            for i, source in enumerate(response['sources'][:2]):  # Show top 2 sources
                print(f"   📄 Source {i+1}: {source['content'][:100]}...")
        
        print("\n✅ RAG pipeline test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ RAG pipeline test failed: {e}")
        return False


def demonstrate_model_management():
    """Demonstrate model management features"""
    print("\n🔧 Testing model management...")
    
    try:
        client = OllamaClient()
        
        # List all supported Llama 3.x models
        print("🦙 Supported Llama 3.x models:")
        for model_id, description in SUPPORTED_LLAMA3_MODELS.items():
            print(f"   {model_id}: {description}")
        
        # Get model recommendations
        use_cases = ["general", "chat", "reasoning", "lightweight"]
        print("\n💡 Model recommendations:")
        for use_case in use_cases:
            recommended = get_recommended_model(use_case)
            print(f"   {use_case}: {recommended}")
        
        # Show current model info
        llm = OllamaLLM("llama3.1:8b-instruct")
        model_info = llm.get_model_info()
        print(f"\n📋 Current model info:")
        for key, value in model_info.items():
            print(f"   {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Model management test failed: {e}")
        return False


def main():
    """Main example function"""
    print("Ollama Integration Example for RAG Chatbot")
    print("=" * 50)
    
    # Check prerequisites
    if not check_ollama_setup():
        print("\nSetup instructions:")
        print("1. Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh")
        print("2. Start server: ollama serve")
        print("3. Download model: ollama pull llama3.1:8b-instruct")
        return
    
    # Run demonstrations
    tests = [
        ("Basic Generation", demonstrate_basic_generation),
        ("RAG Pipeline", demonstrate_rag_pipeline),
        ("Model Management", demonstrate_model_management),
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        results[test_name] = test_func()
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 Test Results Summary:")
    for test_name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   {test_name}: {status}")
    
    all_passed = all(results.values())
    if all_passed:
        print("\nAll tests passed! Ollama integration is working correctly.")
        print("💡 You can now use the RAG chatbot with local Llama 3.x inference!")
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.")


if __name__ == "__main__":
    main()
