#!/bin/bash
# scripts/setup-aws.sh
# Script to set up AWS credentials and IAM roles for serverless deployment

set -e

echo "🚀 Setting up AWS environment for LangChain Serverless deployment"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Installing..."
    
    # Download and install AWS CLI v2
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip awscliv2.zip
    sudo ./aws/install
    rm -rf awscliv2.zip aws/
    
    echo "✅ AWS CLI installed successfully"
fi

# Check AWS CLI version
echo "📋 AWS CLI version:"
aws --version

# Configure AWS credentials (if not already configured)
if [ ! -f ~/.aws/credentials ]; then
    echo "🔐 AWS credentials not found. Please configure them:"
    echo "Run: aws configure"
    echo "You'll need:"
    echo "  - AWS Access Key ID"
    echo "  - AWS Secret Access Key"
    echo "  - Default region (e.g., us-east-1)"
    echo "  - Default output format (json)"
    exit 1
fi

# Set up IAM role and policy for serverless deployment
ROLE_NAME="LangChainServerlessRole"
POLICY_NAME="LangChainServerlessPolicy"
TRUST_POLICY='{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":["lambda.amazonaws.com","apigateway.amazonaws.com"]},"Action":"sts:AssumeRole"}]}'

echo "🔧 Setting up IAM role and policy..."

# Create IAM policy
if ! aws iam get-policy --policy-arn "arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):policy/$POLICY_NAME" &> /dev/null; then
    echo "📝 Creating IAM policy: $POLICY_NAME"
    aws iam create-policy \
        --policy-name "$POLICY_NAME" \
        --policy-document file://aws/iam-policy.json \
        --description "Policy for LangChain serverless deployment"
    echo "✅ IAM policy created"
else
    echo "📋 IAM policy $POLICY_NAME already exists"
fi

# Create IAM role
if ! aws iam get-role --role-name "$ROLE_NAME" &> /dev/null; then
    echo "👤 Creating IAM role: $ROLE_NAME"
    aws iam create-role \
        --role-name "$ROLE_NAME" \
        --assume-role-policy-document "$TRUST_POLICY" \
        --description "Role for LangChain serverless functions"
    echo "✅ IAM role created"
else
    echo "👤 IAM role $ROLE_NAME already exists"
fi

# Attach policy to role
echo "🔗 Attaching policy to role..."
aws iam attach-role-policy \
    --role-name "$ROLE_NAME" \
    --policy-arn "arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):policy/$POLICY_NAME"

# Attach AWS managed policies
aws iam attach-role-policy \
    --role-name "$ROLE_NAME" \
    --policy-arn "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"

aws iam attach-role-policy \
    --role-name "$ROLE_NAME" \
    --policy-arn "arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess"

echo "✅ IAM setup completed"

# Check if Serverless Framework is installed
if ! command -v serverless &> /dev/null; then
    echo "📦 Installing Serverless Framework..."
    npm install -g serverless
    echo "✅ Serverless Framework installed"
fi

echo "🎉 AWS setup completed successfully!"
echo "📋 Next steps:"
echo "  1. Run 'npm install' to install dependencies"
echo "  2. Run 'npm run deploy' to deploy to AWS"
echo "  3. Run 'npm run test:local' to test locally"
