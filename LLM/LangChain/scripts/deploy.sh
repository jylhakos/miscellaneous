#!/bin/bash
# scripts/deploy.sh
# Deployment script for LangChain serverless application

set -e

echo "🚀 Deploying LangChain Serverless Application to AWS"

# Check if we're in the right directory
if [ ! -f "serverless.yml" ]; then
    echo "❌ serverless.yml not found. Please run this script from the project root."
    exit 1
fi

# Get deployment stage (default: dev)
STAGE=${1:-dev}
REGION=${2:-us-east-1}

echo "📋 Deployment Configuration:"
echo "  Stage: $STAGE"
echo "  Region: $REGION"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Run tests before deployment
echo "🧪 Running tests..."
npm test

# Deploy to AWS
echo "☁️ Deploying to AWS Lambda..."
serverless deploy --stage $STAGE --region $REGION --verbose

# Get the API endpoint
echo "🔍 Getting API endpoint..."
ENDPOINT=$(serverless info --stage $STAGE --region $REGION | grep "ServiceEndpoint" | awk '{print $2}')

if [ -n "$ENDPOINT" ]; then
    echo "✅ Deployment successful!"
    echo "📍 API Endpoint: $ENDPOINT"
    echo ""
    echo "🔗 Available endpoints:"
    echo "  POST $ENDPOINT/transform - Transform text to uppercase"
    echo "  GET  $ENDPOINT/health - Health check"
    echo ""
    echo "📝 Example usage:"
    echo "  curl -X POST $ENDPOINT/transform \\"
    echo "    -H 'Content-Type: application/json' \\"
    echo "    -d '{\"text\": \"hello langchain\"}'"
    echo ""
    echo "🏥 Health check:"
    echo "  curl $ENDPOINT/health"
else
    echo "❌ Could not retrieve API endpoint. Check the deployment logs."
fi

echo ""
echo "🎉 Deployment completed!"
