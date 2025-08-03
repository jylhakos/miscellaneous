"""
Example script demonstrating RAG Chatbot usage
This script shows how to use the chatbot components programmatically
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.document_processor import DocumentProcessor
from src.vector_database import VectorDatabase
from src.llm_integration import RAGPipeline, SageMakerLLM, LocalLLM

def example_document_processing():
    """Example: Process documents and create embeddings"""
    print("=== Document Processing Example ===")
    
    # Initialize document processor
    processor = DocumentProcessor()
    
    # Example documents (create some sample files first)
    sample_documents = [
        "./examples/sample_ml.txt",
        "./examples/sample_ai.txt"
    ]
    
    # Create sample documents if they don't exist
    create_sample_documents()
    
    # Process documents
    try:
        documents = processor.process_documents(sample_documents)
        print(f"Processed {len(documents)} document chunks")
        
        # Print sample chunks
        for i, doc in enumerate(documents[:3]):
            print(f"\nChunk {i+1}:")
            print(f"Content: {doc.page_content[:200]}...")
            print(f"Metadata: {doc.metadata}")
            
    except Exception as e:
        print(f"Error processing documents: {e}")

def example_vector_database():
    """Example: Create and use vector database"""
    print("\n=== Vector Database Example ===")
    
    try:
        # Initialize components
        processor = DocumentProcessor()
        vector_db = VectorDatabase("chroma")  # Use ChromaDB
        
        # Create sample documents
        create_sample_documents()
        
        # Process and add documents
        documents = processor.process_documents([
            "./examples/sample_ml.txt",
            "./examples/sample_ai.txt"
        ])
        
        # Add to vector database
        vector_db.add_documents(documents)
        print(f"Added {len(documents)} documents to vector database")
        
        # Search for relevant documents
        query = "What is machine learning?"
        results = vector_db.search(query, k=3)
        
        print(f"\nSearch results for: '{query}'")
        for i, (doc, score) in enumerate(results):
            print(f"\nResult {i+1} (Score: {score:.3f}):")
            print(f"Content: {doc.page_content[:150]}...")
            print(f"Source: {doc.metadata.get('source', 'Unknown')}")
        
        # Save vector store
        vector_db.save("./examples/vector_store")
        print("\nVector store saved")
        
    except Exception as e:
        print(f"Error with vector database: {e}")

def example_rag_pipeline():
    """Example: Complete RAG pipeline"""
    print("\n=== RAG Pipeline Example ===")
    
    try:
        # Initialize components
        processor = DocumentProcessor()
        vector_db = VectorDatabase("chroma")
        
        # Use Local LLM for this example (SageMaker requires deployment)
        llm = LocalLLM()
        
        # Create RAG pipeline
        rag = RAGPipeline(vector_db, llm)
        
        # Create and process sample documents
        create_sample_documents()
        documents = processor.process_documents([
            "./examples/sample_ml.txt",
            "./examples/sample_ai.txt"
        ])
        
        # Add documents to vector database
        vector_db.add_documents(documents)
        
        # Query the RAG system
        questions = [
            "What is machine learning?",
            "How does artificial intelligence work?",
            "What are the benefits of AI?"
        ]
        
        for question in questions:
            print(f"\nQuestion: {question}")
            response = rag.query(question)
            
            print(f"Answer: {response['answer']}")
            print(f"Confidence: {response['confidence']:.2f}")
            print(f"Sources: {response['num_sources']}")
            
            # Show source snippets
            if response['sources']:
                print("Source snippets:")
                for i, source in enumerate(response['sources'][:2], 1):
                    print(f"  {i}. {source['content'][:100]}...")
            
    except Exception as e:
        print(f"Error with RAG pipeline: {e}")

def create_sample_documents():
    """Create sample documents for testing"""
    
    # Create examples directory if it doesn't exist
    os.makedirs("./examples", exist_ok=True)
    
    # Sample ML document
    ml_content = """
    Machine Learning (ML) is a subset of artificial intelligence that enables computers to learn and make decisions without being explicitly programmed. ML algorithms analyze data, identify patterns, and make predictions or decisions based on the patterns they discover.

    Types of Machine Learning:
    1. Supervised Learning: Uses labeled data to train models
    2. Unsupervised Learning: Finds patterns in unlabeled data
    3. Reinforcement Learning: Learns through interaction with environment

    Common ML algorithms include:
    - Linear Regression
    - Decision Trees
    - Random Forest
    - Neural Networks
    - Support Vector Machines

    Machine learning is used in various applications such as:
    - Image recognition
    - Natural language processing
    - Recommendation systems
    - Fraud detection
    - Predictive analytics
    """
    
    # Sample AI document
    ai_content = """
    Artificial Intelligence (AI) is the simulation of human intelligence in machines that are programmed to think and learn like humans. AI systems can perform tasks that typically require human intelligence, such as visual perception, speech recognition, decision-making, and language translation.

    Key Components of AI:
    1. Machine Learning: Algorithms that improve through experience
    2. Natural Language Processing: Understanding and generating human language
    3. Computer Vision: Interpreting and analyzing visual information
    4. Robotics: Physical embodiment of AI systems

    Benefits of AI:
    - Automation of repetitive tasks
    - Enhanced decision-making
    - Improved efficiency and productivity
    - 24/7 availability
    - Handling large amounts of data

    AI Applications:
    - Virtual assistants (Siri, Alexa)
    - Autonomous vehicles
    - Medical diagnosis
    - Financial trading
    - Content recommendation
    - Customer service chatbots
    """
    
    # Write sample documents
    with open("./examples/sample_ml.txt", "w") as f:
        f.write(ml_content)
    
    with open("./examples/sample_ai.txt", "w") as f:
        f.write(ai_content)
    
    print("Sample documents created")

def main():
    """Run all examples"""
    print("RAG Chatbot examples")
    print("=" * 50)
    
    # Run examples
    example_document_processing()
    example_vector_database()
    example_rag_pipeline()
    
    print("\n" + "=" * 50)
    print("Examples completed")
    print("Next steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Configure .env file with your settings")
    print("3. Deploy to AWS using: ./aws/deploy.sh deploy")
    print("4. Start web interface: python -m src.main web")

if __name__ == "__main__":
    main()
