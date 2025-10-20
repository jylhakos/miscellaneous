# Chatbot (AI)

**What is a Chatbot?**

A chatbot is an artificial intelligence (AI) program designed to simulate human conversation through text or voice interactions. Chatbots can provide dynamic responses to customers instead of scripted replies by utilizing natural language processing (NLP) to understand user intent and generate appropriate responses.

For example, chatbots can identify phrases that invoke intent, such as questions like "Can I make a reservation?" If your chatbot needs more data input, you can define prompts the bot should ask to collect information, for example, "What show time would you like to reserve?"

## Retrieval Augmented Generation (RAG)

![alt text](https://github.com/jylhakos/miscellaneous/blob/main/Chatbot/retrieval_augmented_generation.jpg?raw=true)

*Figure: How does retrieval augmented generation work?*

Retrieval augmented generation (RAG) is the technique to upgrade the LLM.

## How to make a Chatbot?

![alt text](https://github.com/jylhakos/miscellaneous/blob/main/Chatbot/how_to_make_a_chatbot.png?raw=true)

*Figure: The chatbot lets users to upload files, ask questions and receive answers based on the file content.*

## Question Answering with Retrieval Augmented Generation

### Steps to create a Chatbot with RAG

#### 1. RAG Workflow

Retrieval-Augmented Generation (RAG) is a technique that enlarge Large Language Models (LLMs) by combining them with an information retrieval component. The RAG workflow consists of the following steps:

1. **Data Ingestion**: Load and parse your external knowledge base (documents, articles, etc.)
2. **Embedding**: Split the ingested data into smaller chunks and generate embeddings for each chunk using an embedding model
3. **Vector Storage**: Store the embeddings in a vector database
4. **Query Processing**: When a user asks a question, embed the query using the same embedding model
5. **Retrieval**: Use the query embedding to perform a similarity search in the vector database and retrieve the most relevant chunks of information
6. **Augmentation**: Combine the retrieved information with the user's original query to create an augmented prompt
7. **Generation**: Pass the augmented prompt to the chosen LLM model to generate a comprehensive answer

#### 2. Chat application requirements

The chat application has the following core requirements:

**Retrieval:**
- When a user asks a question, embed the query using the same embedding model used for the documents
- Perform a similarity search in the local vector database to retrieve the most relevant text chunks based on the query's embedding

**Augmentation:**
- Pass the retrieved relevant chunks along with the user's original query to a local LLM (e.g., using Ollama or other local LLM frameworks)

**Generation:**
- The LLM generates a coherent and informed response based on the provided context and the user's query

#### 3. Creating RAG Chat on Amazon AWS

Creating a chat application with RAG on Amazon AWS using open-source LLM models and Hugging Face Sentence Transformers involves several key steps:

**Data Preparation and Embedding Generation:**
- **Data Collection**: Gather documents or text data that will serve as your knowledge base for RAG
- **Text Chunking**: Split documents into smaller, semantically relevant chunks to optimize retrieval and context provision for the LLM
- **Embedding Generation**: Utilize Hugging Face Sentence Transformers to generate dense vector embeddings for each text chunk. Run this process on AWS EC2 or SageMaker Notebook Instance

**Vector Database setup:**
- **Choose a Vector Database**: Select an appropriate vector database on AWS (Amazon OpenSearch Service with vector search capabilities, or external databases like Pinecone or FAISS hosted on EC2)
- **Ingest Embeddings**: Load the generated embeddings and their corresponding text chunks into the chosen vector database

#### 3.1. Amazon SageMaker Vector Database Architecture

Amazon SageMaker provides a cloud-native approach to document vectorization that differs significantly from local solutions like ChromaDB. Here's how SageMaker integrates with AWS vector databases:

**Amazon SageMaker Embedding Pipeline:**

1. **Document Processing on Amazon SageMaker**:
   ```python
   # SageMaker Processing Job for document chunking
   from sagemaker.processing import ProcessingInput, ProcessingOutput
   from sagemaker.sklearn.processing import SKLearnProcessor
   
   processor = SKLearnProcessor(
       framework_version='1.0-1',
       role=sagemaker_role,
       instance_type='ml.m5.xlarge',
       instance_count=1
   )
   
   processor.run(
       code='document_processing.py',
       inputs=[ProcessingInput(source='s3://your-bucket/documents/', 
                              destination='/opt/ml/processing/input')],
       outputs=[ProcessingOutput(source='/opt/ml/processing/output',
                                destination='s3://your-bucket/chunks/')]
   )
   ```

2. **Embedding Generation with Amazon SageMaker Endpoints**:
   ```python
   # Deploy Sentence Transformers model on SageMaker
   from sagemaker.huggingface import HuggingFaceModel
   
   # Create embedding model endpoint
   embedding_model = HuggingFaceModel(
       model_data='s3://huggingface-models/sentence-transformers/',
       role=sagemaker_role,
       transformers_version='4.21',
       pytorch_version='1.12',
       py_version='py39'
   )
   
   embedding_predictor = embedding_model.deploy(
       initial_instance_count=1,
       instance_type='ml.m5.large',
       endpoint_name='embedding-endpoint'
   )
   ```

3. **Amazon OpenSearch Service Integration**:
   ```python
   import boto3
   from opensearchpy import OpenSearch, RequestsHttpConnection
   from requests_aws4auth import AWS4Auth
   
   # AWS authentication for OpenSearch
   credentials = boto3.Session().get_credentials()
   awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, 
                      'us-east-1', 'es', session_token=credentials.token)
   
   # OpenSearch client with vector search capabilities
   opensearch_client = OpenSearch(
       hosts=[{'host': 'your-domain.us-east-1.es.amazonaws.com', 'port': 443}],
       http_auth=awsauth,
       use_ssl=True,
       verify_certs=True,
       connection_class=RequestsHttpConnection
   )
   
   # Create vector index with k-NN mapping
   index_body = {
       "settings": {
           "index.knn": True,
           "number_of_shards": 1,
           "number_of_replicas": 0
       },
       "mappings": {
           "properties": {
               "text": {"type": "text"},
               "vector": {
                   "type": "knn_vector",
                   "dimension": 384,  # Sentence transformer dimension
                   "method": {
                       "name": "hnsw",
                       "space_type": "cosinesimil",
                       "engine": "nmslib"
                   }
               }
           }
       }
   }
   ```

**Amazon AWS Vector Database options:**

| Service | Use Case | Advantages | Limitations |
|---------|----------|------------|-------------|
| **Amazon OpenSearch** | Production RAG applications | Managed service, k-NN search, AWS integrated | Complex setup, higher cost |
| **Amazon RDS PostgreSQL (pgvector)** | Relational data with vectors | SQL familiarity, ACID compliance | Limited to PostgreSQL |
| **Amazon MemoryDB for Redis** | Real-time applications | In-memory performance, Redis compatibility | Memory constraints, cost |
| **Pinecone on Amazon AWS** | Specialized vector workloads | Purpose-built for vectors, easy scaling | Third-party service, API limits |

**SageMaker Batch Transform for Large-Scale Vectorization:**

```python
# Batch processing for large document collections
from sagemaker.transformer import Transformer

transformer = Transformer(
    model_name='embedding-model',
    instance_count=2,
    instance_type='ml.m5.large',
    output_path='s3://your-bucket/embeddings/',
    accept='application/json',
    content_type='application/json'
)

# Process thousands of documents in parallel
transformer.transform(
    data='s3://your-bucket/chunked-documents/',
    split_type='Line',
    join_source='Input'
)
```

**Cost optimization:**

```python
# Use Spot instances for batch processing
from sagemaker.processing import ProcessingInput, ProcessingOutput

processor = SKLearnProcessor(
    framework_version='1.0-1',
    role=sagemaker_role,
    instance_type='ml.m5.large',
    instance_count=3,
    use_spot_instances=True,
    max_wait=3600,  # 1 hour max wait
    max_run=1800    # 30 minutes max run
)
```

**Real-time vs Batch processing:**

| Approach | Best For | Cost | Latency | Scalability |
|----------|----------|------|---------|-------------|
| **Real-time Endpoints** | Interactive queries | High | Low (ms) | Auto-scaling |
| **Batch Transform** | Bulk processing | Low | High (minutes) | Parallel processing |
| **Processing Jobs** | ETL pipelines | Medium | Medium | Configurable |

**Amazon AWS specific advantages over local ChromaDB:**

1. **Scalability**: Process millions of documents using distributed computing
2. **Managed Infrastructure**: No need to manage servers or databases
3. **Integration**: Native integration with S3, Lambda, API Gateway
4. **Security**: IAM roles, VPC isolation, encryption at rest/transit
5. **Monitoring**: CloudWatch metrics and logs
6. **Cost Optimization**: Spot instances, auto-scaling, pay-per-use

**Serverless Vector Processing Pipeline:**

```python
# Lambda function for real-time document processing
import json
import boto3
from opensearchpy import OpenSearch

def lambda_handler(event, context):
    # Parse S3 event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    # Download and process document
    s3 = boto3.client('s3')
    document = s3.get_object(Bucket=bucket, Key=key)
    
    # Invoke SageMaker endpoint for embedding
    runtime = boto3.client('sagemaker-runtime')
    response = runtime.invoke_endpoint(
        EndpointName='embedding-endpoint',
        ContentType='application/json',
        Body=json.dumps({'text': document_text})
    )
    
    # Store in OpenSearch
    opensearch_client.index(
        index='documents',
        body={
            'text': document_text,
            'vector': embedding,
            'metadata': {'bucket': bucket, 'key': key}
        }
    )
    
    return {'statusCode': 200}
```

This AWS-native approach provides enterprise-grade scalability and reliability compared to local vector databases, making it ideal for production RAG applications.

**Open-Source LLM deployment:**
- **Select an Open-Source LLM**: Choose a suitable model from Hugging Face (e.g., Llama models or instruction-tuned models)
- **Deploy on Amazon SageMaker**: Use SageMaker JumpStart for pre-trained models or deploy custom models with your own container

**RAG pipeline orchestration:**
Build the RAG logic using frameworks like LangChain or LlamaIndex:
- **Query Embedding**: Generate embeddings for user queries using the same Hugging Face Sentence Transformer model
- **Vector Search**: Query the vector database to retrieve relevant text chunks based on similarity
- **Context Augmentation**: Combine retrieved chunks with the user's query to form a comprehensive prompt
- **LLM Inference**: Send the augmented prompt to the deployed LLM on SageMaker to generate responses

**Chat Interface development:**
- **Build User Interface**: Create a chat interface using frameworks like Gradio, Streamlit, or custom frontend applications deployed on AWS Amplify or EC2
- **Integrate with RAG pipeline**: Connect the interface to enable query submission and response generation
- **API Gateway integration**: Use Amazon API Gateway to expose backend services as RESTful APIs for frontend consumption
- **Frontend Frameworks**: Support for React, Vue.js, Angular, or vanilla JavaScript implementations

**Deployment and scalability:**
- Deploy components on appropriate AWS services (Lambda, ECS, or EC2) considering scalability and cost-efficiency

#### 4. Frontend development and API Gateway

**Frontend options:**

1. **React/Vue.js SPA (Single Page Application)**
   - Modern JavaScript framework with real-time chat interface
   - WebSocket support for real-time messaging
   - Document upload with drag-and-drop functionality
   - Responsive design for mobile and desktop

2. **Serverless Frontend with AWS Amplify**
   - Static site hosting with CDN distribution
   - Built-in authentication and authorization
   - Real-time data synchronization
   - CI/CD pipeline integration

3. **Progressive Web App (PWA)**
   - Offline capabilities for chat history
   - Push notifications for responses
   - Mobile-first responsive design
   - Service worker for background processing

**API Gateway integration:**

1. **RESTful API Endpoints**
   - `/api/v1/upload` - Document upload endpoint
   - `/api/v1/chat` - Chat message processing
   - `/api/v1/history` - Chat history retrieval
   - `/api/v1/health` - Health check endpoint

2. **WebSocket API for Real-time Chat**
   - Bidirectional communication for instant responses
   - Connection management for multiple users
   - Message broadcasting and user presence
   - Auto-reconnection on network issues

3. **Authentication and authorization**
   - AWS Cognito integration for user management
   - JWT token-based authentication
   - Role-based access control (RBAC)
   - API key management for external access

#### 4. How Amazon AWS helps with building Chatbots?

Amazon Web Services (AWS) offers comprehensive options for building chatbots:

- **Amazon Aurora PostgreSQL with pgvector**: Create RAG chatbots using the pgvector open-source extension for efficient vector search with HNSW indexing algorithm
- **Amazon AWS AI Services**: Leverage managed AI services for natural language processing and understanding
- **Amazon SageMaker JumpStart**: Quick deployment of pre-trained models including Llama3 models
- **Scalable infrastructure**: Use EC2, Lambda, and other AWS services for scalable deployment

The AWS approach allows users to upload PDF files, ask questions in natural language, and receive answers based on file content using advanced retrieval and generation techniques.

#### 5. Local development setup

The RAG Chatbot supports multiple LLM deployment options:

1. **Amazon SageMaker** - Cloud deployment with Llama 3.x models
2. **Ollama Local Inference** - Privacy-focused local deployment
3. **Hugging Face Integration** - Direct model loading

**Choose Your LLM Backend:**

For **local development with Ollama** (recommended):
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama server
ollama serve

# Download Llama 3.1 8B Instruct model
ollama pull llama3.1:8b-instruct
```

For **Amazon SageMaker deployment**:
```bash
# Configure AWS credentials
aws configure

# Deploy Llama3 to SageMaker
python aws/sagemaker_deploy.py deploy
```

**Install Python Virtual Environment:**

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install required packages
pip install -r requirements.txt

# Deactivate when done
deactivate
```

**Create .gitignore file:**
```
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis
.DS_Store
```

**Create .dockerignore file:**
```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis
.DS_Store
Dockerfile
.dockerignore
```

#### 6. Resources

**Core Documentation:**
- **Building RAG from scratch**: [LlamaIndex Documentation](https://docs.llamaindex.ai/en/v0.10.33/examples/low_level/oss_ingestion_retrieval/)
- **RAG with Llama3 on SageMaker**: [Meta-Llama-on-AWS Repository](https://github.com/aws-samples/Meta-Llama-on-AWS/blob/main/RAG-recipes/llama3-rag-langchain-smjs.ipynb)
- **High-Speed RAG Chatbots**: [AWS Solutions Guidance](https://aws.amazon.com/solutions/guidance/high-speed-rag-chatbots-on-aws/)
- **Sample Implementation**: [AWS Solutions Library](https://github.com/aws-solutions-library-samples/guidance-for-high-speed-rag-chatbots-on-aws)
- **LangChain RAG Tutorial**: [Python LangChain Documentation](https://python.langchain.com/docs/tutorials/rag/)

**Inference Server Setup:**
- **Ollama Local Setup**: [OLLAMA.md](OLLAMA.md) - Complete guide for local Llama 3.x deployment
- **AWS SageMaker Deployment**: [DEPLOYMENT.md](DEPLOYMENT.md) - Cloud deployment instructions
- **Vector Database Setup**: [VECTOR_DATABASE.md](VECTOR_DATABASE.md) - Comprehensive vector database configuration
- **Supported Models**: Llama 3.0, 3.1, 3.2 (8B, 70B variants) from Meta AI via Hugging Face Hub

## Python implementation

This repository contains a complete Python implementation of a RAG chatbot that can be deployed on Amazon AWS.

### Project

```
Chatbot/
├── src/                          # Core application code
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # Main application entry point
│   ├── config.py                # Configuration management
│   ├── document_processor.py    # Document loading and chunking
│   ├── embeddings.py           # Text embedding generation
│   ├── vector_database.py      # Vector storage and retrieval
│   ├── llm_integration.py      # LLM interface and RAG pipeline
│   └── web_interface.py        # FastAPI web interface
├── aws/                         # AWS deployment files
│   ├── deploy.sh               # Automated deployment script
│   ├── sagemaker_deploy.py     # SageMaker model deployment
│   └── cloudformation-template.yaml # Infrastructure as code
├── examples/                    # Example usage scripts
│   └── example_usage.py        # Demonstration scripts
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container configuration
├── docker-compose.yml         # Local development setup
├── .env.example               # Environment configuration template
├── .gitignore                 # Git ignore rules
├── .dockerignore             # Docker ignore rules
├── OLLAMA.md                 # Ollama local inference setup guide
├── DEPLOYMENT.md             # Detailed deployment guide
└── VECTOR_DATABASE.md        # Vector database setup and configuration
```

### Features

1. **Multi-format Document Processing**: Supports PDF, DOCX, TXT, and HTML files
2. **Flexible Vector Storage**:
   - **Local development**: ChromaDB, FAISS for rapid prototyping
   - **Amazon AWS production**: OpenSearch Service with k-NN search, RDS PostgreSQL with pgvector
   - **Hybrid Cloud**: Pinecone integration on AWS infrastructure
3. **LLM integration**: Multiple options for inference
   - **Amazon SageMaker**: Cloud-hosted Llama 3.x models (`meta-textgeneration-llama-3-8b-instruct`)
   - **Ollama**: Local inference with Llama 3.0/3.1/3.2 models
   - **Hugging Face**: Direct integration with `meta-llama/Llama-3-8b-chat-hf`
4. **AWS native vector pipeline**:
   - SageMaker Processing Jobs for large-scale document chunking
   - SageMaker Endpoints for embedding generation at scale
   - OpenSearch Service for production vector search with HNSW indexing
   - S3-triggered Lambda functions for real-time document processing
5. **Prompt Templates**: Optimized prompts for RAG with context injection
6. **Web Interface**: FastAPI-based REST API and interactive web UI
7. **Amazon AWS deployment**: Complete infrastructure automation with CloudFormation
8. **Scalable architecture**: Auto-scaling, batch processing, and serverless options

### Step-by-step

#### 1. Local development

```bash
# Clone and setup
git clone <your-repository>
cd Chatbot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run example
python examples/example_usage.py

# Start web interface
python -m src.main web
```

#### 2. Amazon AWS deployment

```bash
# Configure AWS CLI
aws configure

# Deploy to AWS (automated)
./aws/deploy.sh deploy

# Access your chatbot at the provided URL
```

### Usage

#### Amazon AWS vector pipeline usage

```python
import boto3
from src.aws_vector_pipeline import SageMakerVectorPipeline

# Initialize AWS vector pipeline
pipeline = SageMakerVectorPipeline(
    embedding_endpoint='sentence-transformers-endpoint',
    opensearch_domain='rag-chatbot-search',
    region='us-east-1'
)

# Process documents from S3
pipeline.process_s3_documents(
    bucket='your-document-bucket',
    prefix='documents/',
    batch_size=100
)

# Real-time document processing
pipeline.process_document(
    document_path='s3://bucket/new-document.pdf',
    metadata={'source': 'user-upload', 'timestamp': '2025-08-03'}
)

# Query the vector database
results = pipeline.similarity_search(
    query="What is machine learning?",
    k=5,
    filter={'source': 'user-upload'}
)
```

#### Documents

```python
from src.document_processor import DocumentProcessor
from src.vector_database import VectorDatabase

# Initialize components
processor = DocumentProcessor()
vector_db = VectorDatabase("chroma")

# Process documents
documents = processor.process_documents(["document.pdf"])
vector_db.add_documents(documents)
```

#### Query the Chatbot

```python
from src.llm_integration import RAGPipeline, SageMakerLLM

# Initialize RAG pipeline
llm = SageMakerLLM()  # or LocalLLM()
rag = RAGPipeline(vector_db, llm)

# Ask questions
response = rag.query("What is machine learning?")
print(response['answer'])
```

#### Web API Usage

```bash
# Upload documents
curl -X POST "http://localhost:8000/upload" \
     -F "files=@document.pdf"

# Query chatbot
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"question": "What is AI?", "num_docs": 5}'
```

### Architecture

```
                           Amazon SageMaker Vector Pipeline
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Documents     │    │   SageMaker     │    │   OpenSearch    │
│   (S3 Bucket)   │───▶│   Processing    │───▶│   Service       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Auto Chunking  │    │  Embedding      │    │  Vector Index   │
│  (Lambda/Batch) │    │  Endpoint       │    │  (k-NN Search)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                    ┌─────────────────┐
                    │   RAG Pipeline  │
                    │  (SageMaker)    │
                    └─────────────────┘
                                 │
                                 ▼
                    ┌─────────────────┐
                    │   API Gateway   │
                    │   + Lambda      │
                    └─────────────────┘

         Local Development Alternative
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Documents     │    │   ChromaDB      │    │   Ollama        │
│   (Local Files) │───▶│   (Embedded)    │───▶│   (Local LLM)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Amazon AWS Infrastructure and IAM setup

#### Deployment tools

The project uses **Amazon CloudFormation** as the primary Infrastructure as Code (IaC) tool for setting up AWS resources:

1. **CloudFormation Template**: `aws/cloudformation-template.yaml`
   - Complete infrastructure definition
   - VPC, subnets, security groups
   - EC2 instances with Auto Scaling Groups
   - Application Load Balancer
   - SageMaker execution roles
   - S3 buckets and OpenSearch domain

2. **Automated Deployment Script**: `aws/deploy.sh`
   - Bash script for one-click deployment
   - ECR repository creation
   - Docker image building and pushing
   - CloudFormation stack deployment
   - SageMaker model deployment

3. **SageMaker Deployment**: `aws/sagemaker_deploy.py`
   - Python script for LLM model deployment
   - Llama3 model from SageMaker JumpStart
   - Endpoint configuration and testing

#### Required IAM Roles and Policies

The CloudFormation template automatically creates the following IAM roles:

**1. EC2 Instance Role (`rag-chatbot-EC2-Role`)**
```json
{
  "AssumeRolePolicyDocument": {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": { "Service": "ec2.amazonaws.com" },
        "Action": "sts:AssumeRole"
      }
    ]
  },
  "ManagedPolicyArns": [
    "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess",
    "arn:aws:iam::aws:policy/AmazonS3FullAccess",
    "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
  ]
}
```

**2. SageMaker Execution Role (`rag-chatbot-SageMaker-Role`)**
```json
{
  "AssumeRolePolicyDocument": {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": { "Service": "sagemaker.amazonaws.com" },
        "Action": "sts:AssumeRole"
      }
    ]
  },
  "ManagedPolicyArns": [
    "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess",
    "arn:aws:iam::aws:policy/AmazonS3FullAccess"
  ]
}
```

**3. Additional Policies for Vector Database Access**
```json
{
  "PolicyName": "OpenSearchAccess",
  "PolicyDocument": {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "es:ESHttpGet",
          "es:ESHttpPost", 
          "es:ESHttpPut",
          "es:ESHttpDelete"
        ],
        "Resource": "arn:aws:es:*:*:domain/*"
      }
    ]
  }
}
```

#### Manual IAM setup (Optional)

If you need to create IAM roles manually or customize permissions:

```bash
# Create SageMaker execution role
aws iam create-role \
    --role-name SageMakerRAGChatbotRole \
    --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "sagemaker.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }
        ]
    }'

# Attach required policies
aws iam attach-role-policy \
    --role-name SageMakerRAGChatbotRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess

aws iam attach-role-policy \
    --role-name SageMakerRAGChatbotRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
```

#### Infrastructure components

The CloudFormation template creates:

1. **Networking**:
   - VPC with public/private subnets
   - Internet Gateway and Route Tables
   - Security Groups with appropriate rules

2. **Compute**:
   - EC2 Launch Template with user data script
   - Auto Scaling Group (1-3 instances)
   - Application Load Balancer with health checks

3. **Storage and data**:
   - S3 bucket for document storage
   - OpenSearch domain for vector search with k-NN indexing
   - EBS volumes for application data
   - Document processing pipeline with Lambda triggers

4. **AI/ML services**:
   - SageMaker endpoint for LLM inference (Llama 3.x models)
   - SageMaker endpoint for embedding generation (Sentence Transformers)
   - SageMaker Processing Jobs for batch document vectorization
   - IAM roles for service access

#### Deployment commands

**Automated deployment (Recommended)**:
```bash
# Full deployment
./aws/deploy.sh deploy

# Cleanup resources
./aws/deploy.sh cleanup

# Build and push image only
./aws/deploy.sh build-only
```

**Manual CloudFormation deployment**:
```bash
# Deploy infrastructure
aws cloudformation deploy \
    --template-file aws/cloudformation-template.yaml \
    --stack-name rag-chatbot-stack \
    --region us-east-1 \
    --capabilities CAPABILITY_NAMED_IAM \
    --parameter-overrides EnvironmentName=rag-chatbot

# Deploy SageMaker model
python aws/sagemaker_deploy.py deploy

# Check stack status
aws cloudformation describe-stacks \
    --stack-name rag-chatbot-stack \
    --query 'Stacks[0].StackStatus'
```

#### Required AWS permissions

Your AWS user/role needs the following permissions for deployment:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudformation:*",
        "ec2:*",
        "iam:*",
        "s3:*",
        "sagemaker:*",
        "elasticloadbalancing:*",
        "autoscaling:*",
        "es:*",
        "ecr:*",
        "logs:*"
      ],
      "Resource": "*"
    }
  ]
}
```

#### Cost

- **SageMaker Endpoint**: ~$50-200/month (depending on instance type)
- **EC2 Instances**: ~$25-100/month (t3.medium instances)
- **Load Balancer**: ~$18/month
- **Storage**: ~$5-20/month (S3 + EBS)
- **Total Estimated Cost**: ~$100-350/month

### Deployment options

1. **Local Development**: Run with Docker Compose
2. **AWS EC2**: Deploy with CloudFormation and Auto Scaling
3. **AWS ECS/Fargate**: Container-based deployment
4. **AWS Lambda**: Serverless deployment (with modifications)

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

### References

[Chatbot Tutorial](https://docs.pytorch.org/tutorials/beginner/chatbot_tutorial.html)

[What is a chatbot?](https://aws.amazon.com/what-is/chatbot/)

[Amazon Nova Understanding Models](https://aws.amazon.com/ai/generative-ai/nova/understanding/)
