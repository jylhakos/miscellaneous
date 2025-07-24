#!/bin/bash

# Test Script for RAG Chat Application
# Tests all API endpoints with cURL commands

set -e

BASE_URL="http://localhost:3000"
SESSION_ID="test_session_$(date +%s)"

echo "🧪 RAG Chat Application Test Suite"
echo "=================================="
echo "Base URL: $BASE_URL"
echo "Session ID: $SESSION_ID"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print test results
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC}: $2"
    else
        echo -e "${RED}❌ FAIL${NC}: $2"
    fi
}

# Function to test endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local description=$3
    local data=$4
    local expected_status=$5

    echo -e "${YELLOW}Testing:${NC} $description"
    echo "Endpoint: $method $endpoint"
    
    if [ -n "$data" ]; then
        response=$(curl -s -w "HTTPSTATUS:%{http_code}" -X $method \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$BASE_URL$endpoint")
    else
        response=$(curl -s -w "HTTPSTATUS:%{http_code}" -X $method "$BASE_URL$endpoint")
    fi
    
    # Extract status code
    status_code=$(echo $response | sed -n 's/.*HTTPSTATUS:\([0-9]*\)$/\1/p')
    body=$(echo $response | sed 's/HTTPSTATUS:[0-9]*$//')
    
    echo "Status: $status_code"
    echo "Response: $body" | jq . 2>/dev/null || echo "Response: $body"
    
    if [ "$status_code" -eq "$expected_status" ]; then
        print_result 0 "$description"
    else
        print_result 1 "$description (Expected: $expected_status, Got: $status_code)"
    fi
    echo ""
}

echo "🏥 1. Health Check"
echo "=================="
test_endpoint "GET" "/api/health" "Health check endpoint" "" 200

echo "💬 2. Chat Endpoints"
echo "==================="

# Test basic chat
chat_data='{
    "message": "Hello, what can you help me with?",
    "sessionId": "'$SESSION_ID'"
}'
test_endpoint "POST" "/api/chat" "Basic chat message" "$chat_data" 200

# Test empty message
empty_chat_data='{
    "message": "",
    "sessionId": "'$SESSION_ID'"
}'
test_endpoint "POST" "/api/chat" "Empty chat message (should fail)" "$empty_chat_data" 400

# Test Meta Llama 4 Scout specific prompting
llama4_data='{
    "message": "Using the system prompt format for Meta Llama 4 Scout, explain quantum computing in simple terms.",
    "sessionId": "'$SESSION_ID'"
}'
test_endpoint "POST" "/api/chat" "Meta Llama 4 Scout style prompt" "$llama4_data" 200

echo "📄 3. Document Upload Test"
echo "========================="

# Create a test document
test_doc_content="# Test Document for RAG

This is a test document for the RAG (Retrieval-Augmented Generation) system.

## Key Information

- This document contains information about machine learning
- RAG systems combine retrieval and generation
- Vector databases store document embeddings
- Meta Llama 4 Scout is an advanced language model

## Technical Details

The RAG system works by:
1. Splitting documents into chunks
2. Creating embeddings for each chunk
3. Storing embeddings in a vector database
4. Retrieving relevant chunks for user queries
5. Using an LLM to generate responses based on retrieved context

This test document should be successfully processed and made available for queries."

echo "$test_doc_content" > test_document.txt

echo "📄 Created test document: test_document.txt"

# Test document upload
echo "Testing document upload..."
upload_response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
    -X POST \
    -F "document=@test_document.txt" \
    "$BASE_URL/api/documents/upload")

upload_status=$(echo $upload_response | sed -n 's/.*HTTPSTATUS:\([0-9]*\)$/\1/p')
upload_body=$(echo $upload_response | sed 's/HTTPSTATUS:[0-9]*$//')

echo "Upload Status: $upload_status"
echo "Upload Response: $upload_body" | jq . 2>/dev/null || echo "Upload Response: $upload_body"

if [ "$upload_status" -eq 200 ]; then
    print_result 0 "Document upload"
    
    # Wait a moment for processing
    echo "⏳ Waiting for document to be processed..."
    sleep 3
    
    # Test RAG with uploaded document
    rag_data='{
        "message": "What information do you have about RAG systems from the uploaded document?",
        "sessionId": "'$SESSION_ID'"
    }'
    test_endpoint "POST" "/api/chat" "RAG query with uploaded document" "$rag_data" 200
    
    # Test specific query about Meta Llama 4 Scout
    meta_query='{
        "message": "Tell me about Meta Llama 4 Scout based on the information you have.",
        "sessionId": "'$SESSION_ID'"
    }'
    test_endpoint "POST" "/api/chat" "Query about Meta Llama 4 Scout" "$meta_query" 200
else
    print_result 1 "Document upload (Status: $upload_status)"
fi

# Clean up test file
rm -f test_document.txt

echo "📊 4. Document Management"
echo "========================"
test_endpoint "GET" "/api/documents" "List documents" "" 200

echo "🔄 5. Session Persistence Test"
echo "=============================="

# Test conversation memory
memory_data1='{
    "message": "My name is Alice and I work as a data scientist.",
    "sessionId": "'$SESSION_ID'"
}'
test_endpoint "POST" "/api/chat" "Set context in conversation" "$memory_data1" 200

memory_data2='{
    "message": "What is my name and profession?",
    "sessionId": "'$SESSION_ID'"
}'
test_endpoint "POST" "/api/chat" "Test conversation memory" "$memory_data2" 200

echo "🚀 6. Advanced RAG Features"
echo "=========================="

# Test complex query
complex_query='{
    "message": "Explain how vector databases work in the context of RAG systems, and provide examples of how they might be used with Meta Llama 4 Scout models.",
    "sessionId": "'$SESSION_ID'"
}'
test_endpoint "POST" "/api/chat" "Complex RAG query" "$complex_query" 200

echo ""
echo "🎯 Test Summary"
echo "==============="
echo "All tests completed. Check the results above."
echo ""
echo "💡 Additional Manual Tests:"
echo "1. Visit http://localhost:3000 for the web interface"
echo "2. Test file upload through the web interface"
echo "3. Test conversation persistence through multiple browser tabs"
echo "4. Check logs at: docker-compose logs rag-app"
echo ""
echo "📚 For Meta Llama 4 Scout specific testing:"
echo "- Update OLLAMA_MODEL in .env to use llama4-scout models when available"
echo "- Use the prompt format from: https://www.llama.com/docs/model-cards-and-prompt-formats/llama4/"
