"""
Main application entry point for RAG Chatbot
"""
import argparse
import logging
from pathlib import Path

from .config import settings
from .document_processor import DocumentProcessor
from .vector_database import VectorDatabase
from .llm_integration import RAGPipeline, SageMakerLLM, LocalLLM
from .web_interface import main as run_web_interface

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_environment():
    """Set up necessary directories and environment"""
    # Create necessary directories
    Path(settings.upload_dir).mkdir(exist_ok=True)
    Path(settings.processed_dir).mkdir(exist_ok=True)
    Path("./logs").mkdir(exist_ok=True)
    Path("./chroma_db").mkdir(exist_ok=True)
    
    logger.info("Environment setup complete")


def process_documents_cli(file_paths: list):
    """Process documents from command line"""
    try:
        logger.info(f"Processing {len(file_paths)} documents")
        
        # Initialize components
        processor = DocumentProcessor()
        vector_db = VectorDatabase(settings.vector_db_type)
        
        # Process documents
        documents = processor.process_documents(file_paths)
        
        if documents:
            # Add to vector database
            vector_db.add_documents(documents)
            
            # Save vector store
            vector_db.save()
            
            logger.info(f"Successfully processed {len(documents)} document chunks")
        else:
            logger.warning("No documents were processed")
            
    except Exception as e:
        logger.error(f"Error processing documents: {e}")
        raise


def interactive_chat():
    """Run interactive chat session"""
    try:
        logger.info("Starting interactive chat session")
        
        # Initialize components
        vector_db = VectorDatabase(settings.vector_db_type)
        
        # Try to load existing vector store
        try:
            vector_db.load()
            logger.info("Loaded existing vector store")
        except:
            logger.warning("No existing vector store found. Please process documents first.")
            return
        
        # Initialize LLM
        try:
            llm = SageMakerLLM()
            logger.info("Using SageMaker LLM")
        except:
            llm = LocalLLM()
            logger.info("Using Local LLM")
        
        # Initialize RAG pipeline
        rag_pipeline = RAGPipeline(vector_db, llm)
        
        print("\n" + "="*50)
        print("RAG Chatbot Interactive Session")
        print("Type 'quit' or 'exit' to end the session")
        print("="*50 + "\n")
        
        while True:
            try:
                question = input("\nYou: ").strip()
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                if not question:
                    continue
                
                print("Bot: Thinking...")
                response = rag_pipeline.query(question)
                
                print(f"\nBot: {response['answer']}")
                print(f"\nConfidence: {response['confidence']:.2f}")
                print(f"Sources used: {response['num_sources']}")
                
                if response['sources']:
                    print("\nRelevant sources:")
                    for i, source in enumerate(response['sources'][:3], 1):
                        print(f"{i}. {source['content'][:100]}...")
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
                
    except Exception as e:
        logger.error(f"Error in interactive chat: {e}")
        raise


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="RAG Chatbot Application")
    parser.add_argument(
        'command',
        choices=['web', 'chat', 'process'],
        help='Command to run: web (start web interface), chat (interactive chat), process (process documents)'
    )
    parser.add_argument(
        '--files',
        nargs='+',
        help='Files to process (for process command)'
    )
    parser.add_argument(
        '--host',
        default=settings.app_host,
        help='Host for web interface'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=settings.app_port,
        help='Port for web interface'
    )
    
    args = parser.parse_args()
    
    # Setup environment
    setup_environment()
    
    if args.command == 'web':
        logger.info("Starting web interface")
        run_web_interface()
        
    elif args.command == 'chat':
        interactive_chat()
        
    elif args.command == 'process':
        if not args.files:
            print("Error: --files argument required for process command")
            return
        
        # Validate files exist
        valid_files = []
        for file_path in args.files:
            if Path(file_path).exists():
                valid_files.append(file_path)
            else:
                logger.warning(f"File not found: {file_path}")
        
        if valid_files:
            process_documents_cli(valid_files)
        else:
            print("Error: No valid files provided")


if __name__ == "__main__":
    main()
