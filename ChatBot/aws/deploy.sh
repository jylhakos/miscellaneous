#!/bin/bash

# Amazon AWS deployment script for RAG Chatbot
# This script automates the deployment of the RAG Chatbot to Amazon AWS

set -e

# Configuration
STACK_NAME="rag-chatbot-stack"
REGION="us-east-1"
ECR_REPOSITORY="rag-chatbot"
IMAGE_TAG="latest"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if AWS CLI is installed and configured
check_aws_cli() {
    print_status "Checking AWS CLI configuration..."
    
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI not found. Please install AWS CLI and configure it."
        exit 1
    fi
    
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS CLI not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    print_status "AWS CLI is configured."
}

# Function to get AWS account ID
get_account_id() {
    aws sts get-caller-identity --query Account --output text
}

# Function to create ECR repository
create_ecr_repository() {
    print_status "Creating ECR repository..."
    
    aws ecr describe-repositories --repository-names ${ECR_REPOSITORY} --region ${REGION} &> /dev/null || \
    aws ecr create-repository \
        --repository-name ${ECR_REPOSITORY} \
        --region ${REGION} \
        --image-scanning-configuration scanOnPush=true
    
    print_status "ECR repository ready."
}

# Function to build and push Docker image
build_and_push_image() {
    local account_id=$(get_account_id)
    local ecr_uri="${account_id}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPOSITORY}:${IMAGE_TAG}"
    
    print_status "Building Docker image..."
    docker build -t ${ECR_REPOSITORY}:${IMAGE_TAG} .
    
    print_status "Tagging image for ECR..."
    docker tag ${ECR_REPOSITORY}:${IMAGE_TAG} ${ecr_uri}
    
    print_status "Logging in to ECR..."
    aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${account_id}.dkr.ecr.${REGION}.amazonaws.com
    
    print_status "Pushing image to ECR..."
    docker push ${ecr_uri}
    
    echo ${ecr_uri}
}

# Function to deploy CloudFormation stack
deploy_cloudformation() {
    print_status "Deploying CloudFormation stack..."
    
    aws cloudformation deploy \
        --template-file aws/cloudformation-template.yaml \
        --stack-name ${STACK_NAME} \
        --region ${REGION} \
        --capabilities CAPABILITY_NAMED_IAM \
        --parameter-overrides \
            EnvironmentName=rag-chatbot \
        --tags \
            Project=RAGChatbot \
            Environment=production
    
    print_status "CloudFormation stack deployed successfully."
}

# Function to deploy SageMaker model
deploy_sagemaker_model() {
    print_status "Deploying SageMaker model..."
    
    cd aws
    python sagemaker_deploy.py deploy
    cd ..
    
    print_status "SageMaker model deployed successfully."
}

# Function to get stack outputs
get_stack_outputs() {
    print_status "Getting stack outputs..."
    
    local load_balancer_dns=$(aws cloudformation describe-stacks \
        --stack-name ${STACK_NAME} \
        --region ${REGION} \
        --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
        --output text)
    
    local documents_bucket=$(aws cloudformation describe-stacks \
        --stack-name ${STACK_NAME} \
        --region ${REGION} \
        --query 'Stacks[0].Outputs[?OutputKey==`DocumentsBucket`].OutputValue' \
        --output text)
    
    echo ""
    print_status "Deployment completed successfully!"
    echo ""
    echo "Application URL: http://${load_balancer_dns}"
    echo "Documents Bucket: ${documents_bucket}"
    echo ""
    echo "You can now:"
    echo "1. Access the chatbot at the Application URL"
    echo "2. Upload documents via the web interface"
    echo "3. Start chatting with your RAG-enabled AI assistant"
}

# Function to cleanup resources
cleanup() {
    print_warning "Cleaning up AWS resources..."
    
    # Delete SageMaker endpoint
    cd aws
    python sagemaker_deploy.py cleanup
    cd ..
    
    # Delete CloudFormation stack
    aws cloudformation delete-stack \
        --stack-name ${STACK_NAME} \
        --region ${REGION}
    
    print_status "Cleanup initiated. Resources will be deleted shortly."
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [deploy|cleanup|build-only]"
    echo ""
    echo "Commands:"
    echo "  deploy      - Full deployment (infrastructure + application)"
    echo "  cleanup     - Remove all AWS resources"
    echo "  build-only  - Only build and push Docker image"
    echo ""
    echo "Example:"
    echo "  $0 deploy"
}

# Main execution
main() {
    case "${1:-deploy}" in
        deploy)
            print_status "Starting full deployment..."
            check_aws_cli
            create_ecr_repository
            image_uri=$(build_and_push_image)
            deploy_cloudformation
            deploy_sagemaker_model
            get_stack_outputs
            ;;
        cleanup)
            print_status "Starting cleanup..."
            check_aws_cli
            cleanup
            ;;
        build-only)
            print_status "Building and pushing image only..."
            check_aws_cli
            create_ecr_repository
            build_and_push_image
            ;;
        help|-h|--help)
            show_usage
            ;;
        *)
            print_error "Unknown command: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
