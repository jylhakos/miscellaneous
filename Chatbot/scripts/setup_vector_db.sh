#!/bin/bash

# Vector Database Setup Script for RAG Chatbot
# Supports ChromaDB, FAISS, and Pinecone configurations
# Works for both local development and AWS deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEFAULT_VECTOR_DB="chroma"
CHROMA_DATA_DIR="./chroma_db"
FAISS_DATA_DIR="./faiss_db"
VECTOR_DB_TYPE=${VECTOR_DB_TYPE:-$DEFAULT_VECTOR_DB}

print_header() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}    RAG Chatbot Vector Database Setup${NC}"
    echo -e "${BLUE}================================================${NC}"
}

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if vector database is available
check_vector_db_availability() {
    print_status "Checking vector database availability..."
    
    case $VECTOR_DB_TYPE in
        "chroma")
            python3 -c "import chromadb; print('ChromaDB is available')" 2>/dev/null || {
                print_error "ChromaDB not installed"
                print_status "Install with: pip install chromadb"
                return 1
            }
            ;;
        "faiss")
            python3 -c "import faiss; print('FAISS is available')" 2>/dev/null || {
                print_error "FAISS not installed"
                print_status "Install with: pip install faiss-cpu"
                return 1
            }
            ;;
        "pinecone")
            python3 -c "import pinecone; print('Pinecone is available')" 2>/dev/null || {
                print_error "Pinecone not installed"
                print_status "Install with: pip install pinecone-client"
                return 1
            }
            if [ -z "$PINECONE_API_KEY" ]; then
                print_error "PINECONE_API_KEY environment variable not set"
                return 1
            fi
            ;;
        *)
            print_error "Unsupported vector database type: $VECTOR_DB_TYPE"
            print_status "Supported types: chroma, faiss, pinecone"
            return 1
            ;;
    esac
    
    print_status "Vector database $VECTOR_DB_TYPE is available"
    return 0
}

# Function to setup ChromaDB
setup_chromadb() {
    print_status "Setting up ChromaDB..."
    
    # Create data directory
    mkdir -p $CHROMA_DATA_DIR
    
    # Initialize ChromaDB with Python script
    python3 << EOF
import chromadb
import os

# Create persistent client
client = chromadb.PersistentClient(path="$CHROMA_DATA_DIR")

# Create or get collection
collection = client.get_or_create_collection(
    name="rag_documents",
    metadata={"hnsw:space": "cosine"}
)

print(f"ChromaDB initialized with collection: {collection.name}")
print(f"Data directory: $CHROMA_DATA_DIR")
print(f"Collection count: {collection.count()}")
EOF
    
    print_status "ChromaDB setup completed"
    print_status "Data will be persisted in: $CHROMA_DATA_DIR"
}

# Function to setup FAISS
setup_faiss() {
    print_status "Setting up FAISS..."
    
    # Create data directory
    mkdir -p $FAISS_DATA_DIR
    
    # Initialize FAISS with Python script
    python3 << EOF
import faiss
import numpy as np
import os

# Create directory if it doesn't exist
os.makedirs("$FAISS_DATA_DIR", exist_ok=True)

# Create a sample index (will be recreated with actual embeddings)
dimension = 384  # Default for sentence-transformers/all-MiniLM-L6-v2
index = faiss.IndexFlatIP(dimension)

# Save the empty index
faiss.write_index(index, "$FAISS_DATA_DIR/index.faiss")

print(f"FAISS index initialized with dimension: {dimension}")
print(f"Data directory: $FAISS_DATA_DIR")
print(f"Index file: $FAISS_DATA_DIR/index.faiss")
EOF
    
    print_status "FAISS setup completed"
    print_status "Index will be saved in: $FAISS_DATA_DIR"
}

# Function to setup Pinecone
setup_pinecone() {
    print_status "Setting up Pinecone..."
    
    if [ -z "$PINECONE_API_KEY" ]; then
        print_error "PINECONE_API_KEY environment variable is required"
        return 1
    fi
    
    # Initialize Pinecone with Python script
    python3 << EOF
import pinecone
import os

# Initialize Pinecone
pinecone.init(
    api_key=os.getenv("PINECONE_API_KEY"),
    environment=os.getenv("PINECONE_ENV", "us-east1-gcp")
)

index_name = os.getenv("PINECONE_INDEX_NAME", "rag-chatbot-index")
dimension = 384  # Default for sentence-transformers/all-MiniLM-L6-v2

# Check if index exists
if index_name not in pinecone.list_indexes():
    print(f"Creating Pinecone index: {index_name}")
    pinecone.create_index(
        name=index_name,
        dimension=dimension,
        metric="cosine"
    )
    print(f"Index {index_name} created successfully")
else:
    print(f"Index {index_name} already exists")

# Get index info
index = pinecone.Index(index_name)
stats = index.describe_index_stats()
print(f"Index statistics: {stats}")
EOF
    
    print_status "Pinecone setup completed"
}

# Function to start vector database services
start_vector_services() {
    print_status "Starting vector database services..."
    
    case $VECTOR_DB_TYPE in
        "chroma")
            print_status "ChromaDB uses embedded mode - no separate service needed"
            ;;
        "faiss")
            print_status "FAISS uses embedded mode - no separate service needed"
            ;;
        "pinecone")
            print_status "Pinecone is a cloud service - no local service needed"
            ;;
    esac
}

# Function to start ChromaDB server (optional)
start_chromadb_server() {
    print_status "Starting ChromaDB server (optional)..."
    
    if command -v docker &> /dev/null; then
        print_status "Starting ChromaDB with Docker..."
        docker run -d \
            --name chromadb \
            -p 8001:8000 \
            -v $(pwd)/chroma_data:/chroma/chroma \
            -e CHROMA_SERVER_AUTHN_PROVIDER=chromadb.auth.basic.BasicAuthenticationServerProvider \
            chromadb/chroma:latest
        
        print_status "ChromaDB server started on http://localhost:8001"
    else
        print_warning "Docker not available. Using embedded ChromaDB mode."
    fi
}

# Function to test vector database connection
test_vector_db() {
    print_status "Testing vector database connection..."
    
    python3 << EOF
import sys
sys.path.append('./src')

try:
    from vector_database import VectorDatabase
    from langchain.schema import Document
    
    # Initialize vector database
    vector_db = VectorDatabase("$VECTOR_DB_TYPE")
    
    # Test with sample documents
    test_docs = [
        Document(page_content="This is a test document for vector database.", metadata={"source": "test1"}),
        Document(page_content="Another test document to verify functionality.", metadata={"source": "test2"})
    ]
    
    # Add documents
    vector_db.add_documents(test_docs)
    print(f"✅ Successfully added {len(test_docs)} test documents")
    
    # Test search
    results = vector_db.search("test document", k=2)
    print(f"✅ Search returned {len(results)} results")
    
    for i, (doc, score) in enumerate(results):
        print(f"   Result {i+1}: Score={score:.3f}, Content='{doc.page_content[:50]}...'")
    
    print("✅ Vector database test completed successfully!")
    
except Exception as e:
    print(f"❌ Vector database test failed: {e}")
    sys.exit(1)
EOF
    
    if [ $? -eq 0 ]; then
        print_status "Vector database test passed!"
    else
        print_error "Vector database test failed!"
        return 1
    fi
}

# Function to show vector database status
show_status() {
    print_status "Vector Database Status:"
    echo "  Type: $VECTOR_DB_TYPE"
    
    case $VECTOR_DB_TYPE in
        "chroma")
            echo "  Mode: Embedded/Persistent"
            echo "  Data Directory: $CHROMA_DATA_DIR"
            if [ -d "$CHROMA_DATA_DIR" ]; then
                echo "  Status: ✅ Data directory exists"
            else
                echo "  Status: ❌ Data directory not found"
            fi
            ;;
        "faiss")
            echo "  Mode: Embedded"
            echo "  Data Directory: $FAISS_DATA_DIR"
            if [ -d "$FAISS_DATA_DIR" ]; then
                echo "  Status: ✅ Data directory exists"
            else
                echo "  Status: ❌ Data directory not found"
            fi
            ;;
        "pinecone")
            echo "  Mode: Cloud Service"
            if [ -n "$PINECONE_API_KEY" ]; then
                echo "  Status: ✅ API key configured"
            else
                echo "  Status: ❌ API key not configured"
            fi
            ;;
    esac
}

# Function to cleanup vector database
cleanup() {
    print_warning "Cleaning up vector database..."
    
    case $VECTOR_DB_TYPE in
        "chroma")
            if [ -d "$CHROMA_DATA_DIR" ]; then
                read -p "Remove ChromaDB data directory? (y/N): " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    rm -rf "$CHROMA_DATA_DIR"
                    print_status "ChromaDB data directory removed"
                fi
            fi
            
            # Stop Docker container if running
            if docker ps | grep -q chromadb; then
                docker stop chromadb && docker rm chromadb
                print_status "ChromaDB Docker container stopped"
            fi
            ;;
        "faiss")
            if [ -d "$FAISS_DATA_DIR" ]; then
                read -p "Remove FAISS data directory? (y/N): " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    rm -rf "$FAISS_DATA_DIR"
                    print_status "FAISS data directory removed"
                fi
            fi
            ;;
        "pinecone")
            print_warning "Pinecone cleanup must be done manually via Pinecone console"
            print_status "Visit: https://app.pinecone.io/"
            ;;
    esac
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  setup     - Setup vector database"
    echo "  start     - Start vector database services"
    echo "  test      - Test vector database connection"
    echo "  status    - Show vector database status"
    echo "  cleanup   - Cleanup vector database data"
    echo "  server    - Start ChromaDB server (Docker)"
    echo ""
    echo "Options:"
    echo "  --type TYPE    Vector database type (chroma, faiss, pinecone)"
    echo "  --help         Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  VECTOR_DB_TYPE       Vector database type (default: chroma)"
    echo "  PINECONE_API_KEY     Pinecone API key (required for Pinecone)"
    echo "  PINECONE_INDEX_NAME  Pinecone index name (default: rag-chatbot-index)"
    echo ""
    echo "Examples:"
    echo "  $0 setup --type chroma"
    echo "  $0 start"
    echo "  VECTOR_DB_TYPE=faiss $0 setup"
    echo "  $0 test"
}

# Main execution
main() {
    print_header
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --type)
                VECTOR_DB_TYPE="$2"
                shift 2
                ;;
            --help)
                show_usage
                exit 0
                ;;
            setup)
                COMMAND="setup"
                shift
                ;;
            start)
                COMMAND="start"
                shift
                ;;
            test)
                COMMAND="test"
                shift
                ;;
            status)
                COMMAND="status"
                shift
                ;;
            cleanup)
                COMMAND="cleanup"
                shift
                ;;
            server)
                COMMAND="server"
                shift
                ;;
            *)
                COMMAND="${1:-setup}"
                shift
                ;;
        esac
    done
    
    # Set default command
    COMMAND="${COMMAND:-setup}"
    
    echo "Vector Database Type: $VECTOR_DB_TYPE"
    echo ""
    
    # Execute command
    case $COMMAND in
        setup)
            check_vector_db_availability || exit 1
            case $VECTOR_DB_TYPE in
                "chroma") setup_chromadb ;;
                "faiss") setup_faiss ;;
                "pinecone") setup_pinecone ;;
            esac
            ;;
        start)
            start_vector_services
            ;;
        server)
            start_chromadb_server
            ;;
        test)
            test_vector_db || exit 1
            ;;
        status)
            show_status
            ;;
        cleanup)
            cleanup
            ;;
        *)
            print_error "Unknown command: $COMMAND"
            show_usage
            exit 1
            ;;
    esac
    
    print_status "Vector database operation completed!"
}

# Run main function with all arguments
main "$@"
