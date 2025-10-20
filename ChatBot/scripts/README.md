# RAG Chatbot setup scripts

This directory contains automated setup scripts for deploying the RAG chatbot infrastructure across different environments (local and cloud).

## Overview

The RAG chatbot supports multiple deployment scenarios:
- **Local development**: Using ChromaDB embedded or Docker
- **Cloud production**: Using AWS OpenSearch Service
- **Hybrid**: Local LLM (Ollama) with cloud vector database

## Scripts

### 1. Local Vector Database Setup (`setup_vector_db.sh`)

**Purpose**: Sets up vector databases for local development and testing.

**Supported databases**:
- ChromaDB (embedded and server modes)
- FAISS (CPU-optimized)
- Pinecone (cloud service)

**Usage**:
```bash
# Setup ChromaDB (default)
./scripts/setup_vector_db.sh setup chromadb

# Setup FAISS
./scripts/setup_vector_db.sh setup faiss

# Setup Pinecone (requires API key)
export PINECONE_API_KEY="your-api-key"
./scripts/setup_vector_db.sh setup pinecone

# Test all databases
./scripts/setup_vector_db.sh test

# Clean up
./scripts/setup_vector_db.sh cleanup
```

**Features**:
- Automatic dependency installation
- Docker integration for ChromaDB server
- Comprehensive testing and validation
- Environment configuration
- Cleanup utilities

### 2. AWS Vector Database Setup (`setup_aws_vector_db.sh`)

**Purpose**: Deploys AWS OpenSearch Service for production vector search.

**Prerequisites**:
- AWS CLI configured (`aws configure`)
- Appropriate AWS permissions for OpenSearch, CloudFormation, IAM

**Usage**:
```bash
# Deploy OpenSearch domain
./scripts/setup_aws_vector_db.sh deploy

# Create vector index
./scripts/setup_aws_vector_db.sh index

# Test connection
./scripts/setup_aws_vector_db.sh test

# Configure Python client
./scripts/setup_aws_vector_db.sh configure

# Check status
./scripts/setup_aws_vector_db.sh status

# Cleanup (delete domain)
./scripts/setup_aws_vector_db.sh cleanup
```

**Options**:
```bash
# Custom domain and instance type
./scripts/setup_aws_vector_db.sh deploy \
    --domain my-search \
    --instance t3.medium.search \
    --region us-west-2

# Set region via environment
export AWS_REGION=eu-west-1
./scripts/setup_aws_vector_db.sh deploy
```

**Features**:
- CloudFormation-based deployment
- Security best practices (encryption, HTTPS)
- Automatic AWS authentication
- Python client configuration
- Cost-optimized for development

## Quick Start

### For local development

1. **Start with ChromaDB** (simplest option):
   ```bash
   cd /path/to/chatbot
   ./scripts/setup_vector_db.sh setup chromadb
   ./scripts/setup_vector_db.sh test
   ```

2. **Set environment variables**:
   ```bash
   export VECTOR_DB_TYPE=chromadb
   export CHROMADB_PATH=./data/chromadb
   ```

3. **Start the application**:
   ```bash
   python src/main.py
   ```

### For AWS production

1. **Configure AWS CLI**:
   ```bash
   aws configure
   ```

2. **Deploy OpenSearch**:
   ```bash
   ./scripts/setup_aws_vector_db.sh deploy
   ./scripts/setup_aws_vector_db.sh index
   ./scripts/setup_aws_vector_db.sh configure
   ```

3. **Update configuration**:
   ```bash
   export VECTOR_DB_TYPE=opensearch
   export AWS_REGION=us-east-1
   ```

4. **Deploy the application** (using existing CloudFormation):
   ```bash
   aws cloudformation deploy --template-file infrastructure/aws-infrastructure.yaml --stack-name rag-chatbot
   ```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `VECTOR_DB_TYPE` | Database type (chromadb/faiss/pinecone/opensearch) | chromadb | Yes |
| `CHROMADB_PATH` | Path for ChromaDB persistence | ./data/chromadb | No |
| `CHROMADB_SERVER_URL` | ChromaDB server URL | http://localhost:8000 | No |
| `FAISS_INDEX_PATH` | Path for FAISS index | ./data/faiss_index | No |
| `PINECONE_API_KEY` | Pinecone API key | - | For Pinecone |
| `PINECONE_ENVIRONMENT` | Pinecone environment | us-east1-gcp | No |
| `AWS_REGION` | AWS region for OpenSearch | us-east-1 | For AWS |

### Database comparison

| Database | Use Case | Pros | Cons |
|----------|----------|------|------|
| **ChromaDB** | Local development, prototyping | Easy setup, persistent, built-in embeddings | Single-node only |
| **FAISS** | High-performance local search | Fast CPU search, no dependencies | No persistence layer |
| **Pinecone** | Cloud production | Managed service, scalable | Requires API key, costs |
| **OpenSearch** | AWS production | Integrated with AWS, secure | Complex setup, AWS-specific |

## Troubleshooting

### Issues

1. **ChromaDB "database is locked"**:
   ```bash
   # Stop any running ChromaDB processes
   pkill -f chromadb
   ./scripts/setup_vector_db.sh cleanup chromadb
   ./scripts/setup_vector_db.sh setup chromadb
   ```

2. **AWS OpenSearch access denied**:
   ```bash
   # Check AWS credentials
   aws sts get-caller-identity
   
   # Verify region
   aws opensearch describe-domain --domain-name rag-chatbot-search
   ```

3. **Pinecone connection issues**:
   ```bash
   # Verify API key
   echo $PINECONE_API_KEY
   
   # Test connection
   ./scripts/setup_vector_db.sh test pinecone
   ```

4. **Python dependencies missing**:
   ```bash
   # Install all dependencies
   pip install -r requirements.txt
   
   # Or install specific database packages
   pip install chromadb faiss-cpu pinecone-client opensearch-py
   ```

### Performance tuning

1. **ChromaDB optimization**:
   - Use SSD for persistence path
   - Increase batch size for bulk operations
   - Consider ChromaDB server mode for multiple clients

2. **FAISS optimization**:
   - Choose appropriate index type (IndexFlatIP, IndexIVFFlat)
   - Tune nprobe parameter for search speed vs accuracy
   - Use GPU if available (faiss-gpu package)

3. **OpenSearch optimization**:
   - Scale instance type based on data size
   - Adjust shard count and replica settings
   - Monitor CloudWatch metrics

## Integration with main application

The setup scripts automatically configure the vector database, but you need to update your main application configuration:

1. **Update `config/config.yaml`**:
   ```yaml
   vector_database:
     type: ${VECTOR_DB_TYPE}
     chromadb:
       persist_directory: ${CHROMADB_PATH}
     opensearch:
       region: ${AWS_REGION}
       domain: rag-chatbot-search
   ```

2. **Use in Python code**:
   ```python
   from src.vector_database import VectorStore
   
   # Database is automatically configured based on environment
   vector_store = VectorStore.create()
   ```

## Security

### Local Development
- ChromaDB: No authentication by default (suitable for development)
- FAISS: File system permissions only
- Pinecone: API key security (use environment variables)

### Production (AWS)
- OpenSearch: IAM-based authentication
- Encryption at rest and in transit
- VPC integration available
- CloudTrail logging enabled

## Cost

### AWS OpenSearch
- Start with `t3.small.search` for development
- Use single-node configuration
- Enable deletion protection for production
- Monitor usage with CloudWatch

### Pinecone
- Free tier: 1M vectors, 1 index
- Pay-per-use for additional capacity
- Consider index size and query volume

For additional support, refer to the main `README.md`, check the troubleshooting section in `OLLAMA.md` for LLM-related issues, or see `VECTOR_DATABASE.md` for comprehensive vector database configuration.

## Monitoring


### Local monitoring
```bash
# Check ChromaDB status
./scripts/setup_vector_db.sh status chromadb

# Check disk usage
du -sh ./data/chromadb ./data/faiss_index
```

### AWS monitoring
```bash
# Check OpenSearch domain status
./scripts/setup_aws_vector_db.sh status

# Monitor via CloudWatch
aws logs describe-log-groups --log-group-name-prefix /aws/opensearch
```
