# RAG Chatbot deployment

This document provides step-by-step instructions for deploying the RAG Chatbot application to Amazon AWS.

## Prerequisites

### Local development environment

1. **Python 3.11+**
2. **Docker and Docker Compose**
3. **AWS CLI v2**
4. **Git**

### AWS account setup

1. **AWS Account** with appropriate permissions
2. **AWS CLI configured** with access keys
3. **Docker installed** for container builds

#### IAM permissions setup

Before deployment, ensure you have the necessary IAM permissions:

**Option 1: Automated IAM Setup (Recommended)**
```bash
# Create IAM user with deployment permissions
./aws/setup-iam.sh setup-user

# Create CloudFormation service role
./aws/setup-iam.sh setup-role

# Validate permissions
./aws/setup-iam.sh validate
```

**Option 2: Manual IAM setup**
```bash
# Create IAM policy for deployment
aws iam create-policy \
    --policy-name RAGChatbotDeploymentPolicy \
    --policy-document file://aws/iam-deployment-policy.json

# Attach policy to your user/role
aws iam attach-user-policy \
    --user-name your-username \
    --policy-arn arn:aws:iam::ACCOUNT-ID:policy/RAGChatbotDeploymentPolicy
```

The deployment requires permissions for:
- CloudFormation (stack creation/management)
- EC2 (instances, VPC, security groups)
- IAM (role creation and management)
- S3 (bucket creation and access)
- SageMaker (model deployment)
- ECR (container registry)
- Application Load Balancer
- Auto Scaling Groups
- OpenSearch (optional)

## Start

### 1. Local development setup

```bash
# Clone the repository (or use existing code)
cd /path/to/your/chatbot/project

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env

# Edit .env file with your configuration
nano .env
```

### 2. Local testing

```bash
# Test document processing
python -m src.main process --files ./documents/sample.pdf

# Start interactive chat (after processing documents)
python -m src.main chat

# Start web interface
python -m src.main web
```

### 3. Docker testing

```bash
# Build Docker image
docker build -t rag-chatbot .

# Run with Docker Compose
docker-compose up -d

# Access application at http://localhost:8000
```

## Amazon AWS deployment

### Option 1: Automated deployment (Recommended)

```bash
# Make deployment script executable
chmod +x aws/deploy.sh

# Deploy everything to AWS
./aws/deploy.sh deploy
```

This will:
- Create ECR repository
- Build and push Docker image
- Deploy CloudFormation infrastructure
- Deploy SageMaker LLM endpoint
- Provide access URLs

### Option 2: Manual deployment

#### Step 1: Configure Amazon AWS credentials

```bash
# Configure AWS CLI
aws configure

# Verify configuration
aws sts get-caller-identity
```

#### Step 2: Create Infrastructure

```bash
# Deploy CloudFormation stack
aws cloudformation deploy \
    --template-file aws/cloudformation-template.yaml \
    --stack-name rag-chatbot-stack \
    --region us-east-1 \
    --capabilities CAPABILITY_NAMED_IAM \
    --parameter-overrides EnvironmentName=rag-chatbot
```

#### Step 3: Deploy SageMaker model

```bash
# Deploy Llama3 model to SageMaker
cd aws
python sagemaker_deploy.py deploy
cd ..
```

#### Step 4: Build and deploy application

```bash
# Create ECR repository
aws ecr create-repository --repository-name rag-chatbot --region us-east-1

# Get ECR login
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and tag image
docker build -t rag-chatbot .
docker tag rag-chatbot:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/rag-chatbot:latest

# Push to ECR
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/rag-chatbot:latest
```

## Configuration

### Environment Variables

Update `.env` file with your AWS settings:

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# SageMaker Configuration
SAGEMAKER_ENDPOINT_NAME=llama3-rag-endpoint
SAGEMAKER_ROLE_ARN=arn:aws:iam::account:role/SageMakerRAGRole

# Vector Database (choose one)
VECTOR_DB_TYPE=chroma  # or faiss, pinecone
PINECONE_API_KEY=your_pinecone_key  # if using Pinecone

# Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHUNK_SIZE=512
CHUNK_OVERLAP=50

# LLM Configuration
LLM_MODEL_NAME=meta-llama/Llama-3-8b-chat-hf
MAX_TOKENS=2048
TEMPERATURE=0.7
```

## Usage

### 1. Access the web interface

After deployment, access your chatbot at:
```
http://<load-balancer-dns>
```

### 2. Upload documents

- Use the web interface to upload PDF, DOCX, TXT, or HTML files
- Documents are automatically processed and indexed
- You can upload multiple files at once

### 3. Chat with the bot

- Ask questions about your uploaded documents
- The bot uses RAG to provide accurate, context-aware responses
- View source documents and confidence scores

### 4. API usage

The application also provides REST API endpoints:

```bash
# Upload documents
curl -X POST "http://<endpoint>/upload" \
     -F "files=@document1.pdf" \
     -F "files=@document2.pdf"

# Query the chatbot
curl -X POST "http://<endpoint>/query" \
     -H "Content-Type: application/json" \
     -d '{"question": "What is machine learning?", "num_docs": 5}'

# Health check
curl "http://<endpoint>/health"
```

## Monitoring and troubleshooting

### CloudWatch logs

Monitor application logs in CloudWatch:
```bash
# View application logs
aws logs describe-log-groups --region us-east-1

# Stream logs
aws logs tail rag-chatbot-logs --follow --region us-east-1
```

### SageMaker monitoring

```bash
# Check endpoint status
aws sagemaker describe-endpoint --endpoint-name llama3-rag-endpoint

# View endpoint metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/SageMaker \
    --metric-name InvocationsPerInstance \
    --dimensions Name=EndpointName,Value=llama3-rag-endpoint \
    --start-time 2024-01-01T00:00:00Z \
    --end-time 2024-01-02T00:00:00Z \
    --period 3600 \
    --statistics Sum
```

### Issues

1. **SageMaker Endpoint timeout**
   - Check endpoint status in AWS Console
   - Verify IAM roles and permissions
   - Check CloudWatch logs for errors

2. **Vector Database issues**
   - Ensure documents are properly processed
   - Check embedding model compatibility
   - Verify vector store persistence

3. **Memory issues**
   - Increase EC2 instance size
   - Optimize chunk size and overlap
   - Use smaller embedding models

## Scaling and optimization

### Auto scaling

The CloudFormation template includes:
- Application Load Balancer
- Auto Scaling Group (1-3 instances)
- Health checks and automatic recovery

### Cost

1. **SageMaker Endpoints**
   - Use smaller instance types for development
   - Enable auto-scaling for production
   - Consider Serverless Inference for variable workloads

2. **Vector Databases**
   - Use local storage (ChromaDB/FAISS) for smaller datasets
   - Consider managed services (OpenSearch/Pinecone) for large-scale

3. **EC2 Instances**
   - Use Spot Instances for development
   - Right-size instances based on usage
   - Enable detailed monitoring

## Cleanup

To avoid ongoing charges, clean up AWS resources:

```bash
# Automated cleanup
./aws/deploy.sh cleanup

# Manual cleanup
python aws/sagemaker_deploy.py cleanup
aws cloudformation delete-stack --stack-name rag-chatbot-stack --region us-east-1
```

## Security

1. **IAM roles**: Use least-privilege IAM roles
2. **VPC security**: Deploy in private subnets when possible
3. **Encryption**: Enable encryption for S3, EBS, and data in transit
4. **API security**: Implement authentication for production use
5. **Network security**: Use security groups and NACLs appropriately

## Additional Resources

- [Vector Database Setup Guide](VECTOR_DATABASE.md) - Complete configuration for all supported databases
- [AWS SageMaker Documentation](https://docs.aws.amazon.com/sagemaker/)
- [LangChain Documentation](https://python.langchain.com/)
- [Sentence Transformers Documentation](https://www.sbert.net/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
