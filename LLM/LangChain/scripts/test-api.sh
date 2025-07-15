#!/bin/bash
# scripts/test-api.sh
# Script to test the deployed API endpoints

set -e

# Get the API endpoint URL
ENDPOINT=${1:-""}

if [ -z "$ENDPOINT" ]; then
    echo "Usage: $0 <API_ENDPOINT_URL>"
    echo "Example: $0 https://abc123.execute-api.us-east-1.amazonaws.com/dev"
    exit 1
fi

echo "🧪 Testing LangChain API at: $ENDPOINT"
echo ""

# Test health check
echo "🏥 Testing health check endpoint..."
curl -s -w "\nHTTP Status: %{http_code}\n" \
    -H "Content-Type: application/json" \
    "$ENDPOINT/health" | jq .

echo ""
echo "---"
echo ""

# Test text transformation
echo "📝 Testing text transformation endpoint..."
curl -s -w "\nHTTP Status: %{http_code}\n" \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"text": "hello langchain serverless!"}' \
    "$ENDPOINT/transform" | jq .

echo ""
echo "---"
echo ""

# Test error handling - missing text
echo "❌ Testing error handling (missing text)..."
curl -s -w "\nHTTP Status: %{http_code}\n" \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{}' \
    "$ENDPOINT/transform" | jq .

echo ""
echo "---"
echo ""

# Test error handling - invalid JSON
echo "❌ Testing error handling (invalid JSON)..."
curl -s -w "\nHTTP Status: %{http_code}\n" \
    -X POST \
    -H "Content-Type: application/json" \
    -d 'invalid json' \
    "$ENDPOINT/transform" | jq .

echo ""
echo "---"
echo ""

# Test error handling - wrong method
echo "❌ Testing error handling (wrong method)..."
curl -s -w "\nHTTP Status: %{http_code}\n" \
    -X GET \
    "$ENDPOINT/transform" | jq .

echo ""
echo "✅ API testing completed!"
