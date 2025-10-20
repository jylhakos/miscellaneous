# Vector database setup

## Infrastructure

The RAG Chatbot has vector database support with automated setup scripts for both local and AWS environments.

### What are options for Vector Databases?

#### 1. **Databases**
- **ChromaDB**: Default embedded database for local development
- **FAISS**: High-performance CPU-based vector search
- **Pinecone**: Cloud-hosted vector database service
- **AWS OpenSearch**: Production-ready AWS-managed vector search

#### 2. **Automated setup scripts**

**Local Setup** (`scripts/setup_vector_db.sh`):
```bash
# Setup ChromaDB (default)
./scripts/setup_vector_db.sh setup --type chroma

# Setup FAISS
./scripts/setup_vector_db.sh setup --type faiss

# Setup Pinecone
export PINECONE_API_KEY="your-key"
./scripts/setup_vector_db.sh setup --type pinecone

# Test all connections
./scripts/setup_vector_db.sh test

# Check status
./scripts/setup_vector_db.sh status
```

**Amazon AWS Setup** (`scripts/setup_aws_vector_db.sh`):
```bash
# Deploy OpenSearch domain
./scripts/setup_aws_vector_db.sh deploy

# Create vector index
./scripts/setup_aws_vector_db.sh index

# Test connection
./scripts/setup_aws_vector_db.sh test

# Configure Python client
./scripts/setup_aws_vector_db.sh configure
```

#### 3. **Vector Database abstraction** (`src/vector_database.py`)
- Unified interface across all database types
- Automatic configuration based on environment variables
- Optimized for RAG use cases with document chunking and similarity search

#### 4. **LLM integration**
- **Ollama**: Local Llama 3.x models (3.0, 3.1, 3.2)
- **AWS SageMaker**: Cloud-hosted meta-textgeneration-llama-3-8b-instruct
- **Hugging Face**: Direct integration with Transformers library
- **Prompt Templates**: Optimized for RAG context injection

### 🔧 Configurations

#### Environment Variables
```bash
# Vector Database Configuration
export VECTOR_DB_TYPE=chromadb          # chromadb, faiss, pinecone, opensearch
export CHROMADB_PATH=./data/chromadb    # ChromaDB persistence directory
export FAISS_INDEX_PATH=./data/faiss    # FAISS index file path
export PINECONE_API_KEY=your-key        # Pinecone authentication
export AWS_REGION=us-east-1             # AWS OpenSearch region

# LLM Configuration
export LLM_TYPE=ollama                   # ollama, sagemaker, huggingface
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_MODEL=llama3.2:latest
```

#### Database selection matrix
| Database | Use Case | Setup Command | Dependencies |
|----------|----------|---------------|--------------|
| **ChromaDB** | Local development, prototyping | `setup --type chroma` | `pip install chromadb` |
| **FAISS** | High-performance CPU search | `setup --type faiss` | `pip install faiss-cpu` |
| **Pinecone** | Cloud production, managed | `setup --type pinecone` | `pip install pinecone-client` |
| **OpenSearch** | AWS production | `setup_aws_vector_db.sh deploy` | AWS CLI configured |

### Performance characteristics

#### ChromaDB
- **Pros**: Easy setup, persistent, built-in embeddings
- **Cons**: Single-node only, not for high-scale production
- **Best For**: Development, prototyping, small-scale deployments

#### FAISS
- **Pros**: Extremely fast CPU search, no external dependencies
- **Cons**: No built-in persistence, requires manual index management
- **Best For**: High-performance local search, research environments

#### Pinecone
- **Pros**: Fully managed, scalable, real-time updates
- **Cons**: Requires API key, usage-based pricing
- **Best For**: Production applications, real-time search

#### AWS OpenSearch
- **Pros**: AWS-integrated, secure, scalable, enterprise-ready
- **Cons**: More complex setup, AWS-specific
- **Best For**: Enterprise production, AWS-native applications

### Workflows

#### For local development
```bash
# 1. Clone and setup
cd /path/to/chatbot
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup vector database
./scripts/setup_vector_db.sh setup --type chroma

# 4. Test connection
./scripts/setup_vector_db.sh test

# 5. Start application
export VECTOR_DB_TYPE=chromadb
python src/main.py
```

#### For Amazon AWS production
```bash
# 1. Configure AWS
aws configure

# 2. Deploy OpenSearch
./scripts/setup_aws_vector_db.sh deploy

# 3. Create vector index
./scripts/setup_aws_vector_db.sh index

# 4. Deploy application infrastructure
aws cloudformation deploy \
    --template-file infrastructure/aws-infrastructure.yaml \
    --stack-name rag-chatbot \
    --capabilities CAPABILITY_IAM

# 5. Configure environment
export VECTOR_DB_TYPE=opensearch
export AWS_REGION=us-east-1
```

### Troubleshooting

#### Issues

1. **ChromaDB "database is locked"**
   ```bash
   pkill -f chromadb
   ./scripts/setup_vector_db.sh cleanup
   ./scripts/setup_vector_db.sh setup --type chroma
   ```

2. **FAISS import errors**
   ```bash
   pip uninstall faiss-cpu faiss-gpu
   pip install faiss-cpu  # or faiss-gpu for GPU support
   ```

3. **Pinecone connection timeout**
   ```bash
   echo $PINECONE_API_KEY
   ./scripts/setup_vector_db.sh test --type pinecone
   ```

4. **AWS OpenSearch access denied**
   ```bash
   aws sts get-caller-identity
   aws opensearch describe-domain --domain-name rag-chatbot-search
   ```

### Documents

- **Main Setup**: `scripts/README.md` - Comprehensive setup guide
- **Ollama Integration**: `OLLAMA.md` - LLM model configuration
- **AWS Infrastructure**: `infrastructure/README.md` - Cloud deployment
- **API Documentation**: `docs/api.md` - REST API endpoints
- **Configuration**: `config/config.yaml` - Application settings

---

