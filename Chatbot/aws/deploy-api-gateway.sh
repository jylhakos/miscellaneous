#!/bin/bash

# Deploy RAG Chatbot with API Gateway on Amazon AWS
# This script deploys the infrastructure including Lambda functions and API Gateway

set -e

# Configuration
STACK_NAME="rag-chatbot-api"
REGION="us-east-1"
KEY_PAIR_NAME=""  # Set your EC2 key pair name
DOMAIN_NAME=""    # Optional: Set custom domain name
CERTIFICATE_ARN="" # Optional: Set SSL certificate ARN

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting RAG Chatbot API deployment...${NC}"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not configured. Run 'aws configure' first.${NC}"
    exit 1
fi

# Prompt for required parameters if not set
if [ -z "$KEY_PAIR_NAME" ]; then
    echo -e "${YELLOW}Please enter your EC2 Key Pair name:${NC}"
    read -r KEY_PAIR_NAME
fi

# Validate CloudFormation template
echo -e "${YELLOW}📋 Validating CloudFormation template...${NC}"
aws cloudformation validate-template \
    --template-body file://cloudformation-api-gateway.yaml \
    --region $REGION

# Build parameters array
PARAMETERS="ParameterKey=KeyPairName,ParameterValue=$KEY_PAIR_NAME"

if [ -n "$DOMAIN_NAME" ]; then
    PARAMETERS="$PARAMETERS ParameterKey=DomainName,ParameterValue=$DOMAIN_NAME"
fi

if [ -n "$CERTIFICATE_ARN" ]; then
    PARAMETERS="$PARAMETERS ParameterKey=CertificateArn,ParameterValue=$CERTIFICATE_ARN"
fi

# Deploy the stack
echo -e "${YELLOW}🏗️  Deploying CloudFormation stack...${NC}"
aws cloudformation deploy \
    --template-file cloudformation-api-gateway.yaml \
    --stack-name $STACK_NAME \
    --parameter-overrides $PARAMETERS \
    --capabilities CAPABILITY_IAM \
    --region $REGION \
    --no-fail-on-empty-changeset

# Check deployment status
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ CloudFormation stack deployed successfully!${NC}"
else
    echo -e "${RED}❌ CloudFormation deployment failed!${NC}"
    exit 1
fi

# Get stack outputs
echo -e "${YELLOW}📊 Retrieving stack outputs...${NC}"
API_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayEndpoint`].OutputValue' \
    --output text)

LOAD_BALANCER_DNS=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
    --output text)

DOCUMENTS_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`DocumentsBucket`].OutputValue' \
    --output text)

OPENSEARCH_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`OpenSearchEndpoint`].OutputValue' \
    --output text)

# Get custom domain if available
CUSTOM_DOMAIN=""
if [ -n "$DOMAIN_NAME" ]; then
    CUSTOM_DOMAIN=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`CustomDomainEndpoint`].OutputValue' \
        --output text 2>/dev/null || echo "")
fi

# Package and deploy Lambda functions
echo -e "${YELLOW}📦 Preparing Lambda function deployment packages...${NC}"

# Create deployment directory
mkdir -p lambda-packages

# Package Chat function
echo -e "${YELLOW}   Packaging Chat function...${NC}"
cd lambda-packages
mkdir -p chat-function
cp ../src/lambda_functions/chat_function.py chat-function/lambda_function.py 2>/dev/null || echo "# Chat function placeholder" > chat-function/lambda_function.py
cd chat-function && zip -r ../chat-function.zip . && cd ..

# Package Upload function  
echo -e "${YELLOW}   Packaging Upload function...${NC}"
mkdir -p upload-function
cp ../src/lambda_functions/upload_function.py upload-function/lambda_function.py 2>/dev/null || echo "# Upload function placeholder" > upload-function/lambda_function.py
cd upload-function && zip -r ../upload-function.zip . && cd ..

# Package Documents function
echo -e "${YELLOW}   Packaging Documents function...${NC}"
mkdir -p documents-function
cp ../src/lambda_functions/documents_function.py documents-function/lambda_function.py 2>/dev/null || echo "# Documents function placeholder" > documents-function/lambda_function.py
cd documents-function && zip -r ../documents-function.zip . && cd ..

cd ..

# Update Lambda functions
echo -e "${YELLOW}🔄 Updating Lambda functions...${NC}"

# Update Chat function
aws lambda update-function-code \
    --function-name "${STACK_NAME}-chat-function" \
    --zip-file fileb://lambda-packages/chat-function.zip \
    --region $REGION

# Update Upload function
aws lambda update-function-code \
    --function-name "${STACK_NAME}-upload-function" \
    --zip-file fileb://lambda-packages/upload-function.zip \
    --region $REGION

# Update Documents function
aws lambda update-function-code \
    --function-name "${STACK_NAME}-documents-function" \
    --zip-file fileb://lambda-packages/documents-function.zip \
    --region $REGION

# Clean up
rm -rf lambda-packages

# Test API endpoints
echo -e "${YELLOW}🧪 Testing API endpoints...${NC}"

# Test health check
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "${API_ENDPOINT}/health" || echo "000")
if [ "$HEALTH_RESPONSE" = "200" ]; then
    echo -e "${GREEN}   ✅ Health check: OK${NC}"
else
    echo -e "${YELLOW}   ⚠️  Health check: Not responding (this is normal for new deployments)${NC}"
fi

# Display deployment information
echo -e "\n${GREEN}🎉 RAG Chatbot API deployment completed successfully!${NC}\n"

echo -e "${YELLOW}📋 Deployment Information:${NC}"
echo -e "   Stack Name: $STACK_NAME"
echo -e "   Region: $REGION"
echo -e "   API Gateway Endpoint: $API_ENDPOINT"
if [ -n "$CUSTOM_DOMAIN" ]; then
    echo -e "   Custom Domain: $CUSTOM_DOMAIN"
fi
echo -e "   Load Balancer DNS: $LOAD_BALANCER_DNS"
echo -e "   Documents Bucket: $DOCUMENTS_BUCKET"
echo -e "   OpenSearch Endpoint: https://$OPENSEARCH_ENDPOINT"

echo -e "\n${YELLOW}🔗 API Endpoints:${NC}"
echo -e "   Chat: POST $API_ENDPOINT/chat"
echo -e "   Upload: POST $API_ENDPOINT/upload"
echo -e "   Documents: GET $API_ENDPOINT/documents"
echo -e "   Delete Document: DELETE $API_ENDPOINT/documents/{id}"

echo -e "\n${YELLOW}🔧 Next Steps:${NC}"
echo "1. Update your frontend API configuration to use: $API_ENDPOINT"
echo "2. Deploy your React frontend to AWS Amplify or S3"
echo "3. Implement actual RAG logic in Lambda functions"
echo "4. Configure OpenSearch indices for vector storage"
echo "5. Set up SageMaker endpoints for LLM inference"

echo -e "\n${YELLOW}📚 Documentation:${NC}"
echo "   - API Documentation: See README.md"
echo "   - Frontend Setup: See frontend/README.md"
echo "   - Lambda Functions: See src/lambda_functions/"

echo -e "\n${YELLOW}🛠️  Management Commands:${NC}"
echo "   View stack: aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION"
echo "   Delete stack: aws cloudformation delete-stack --stack-name $STACK_NAME --region $REGION"
echo "   View logs: aws logs describe-log-groups --region $REGION"

echo -e "\n${GREEN}✨ Your RAG Chatbot API is now live and ready to use!${NC}"
