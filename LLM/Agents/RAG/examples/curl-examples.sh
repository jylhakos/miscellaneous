#!/bin/bash

# Example cURL commands for RAG Chat Application
# This script demonstrates how to interact with the API

BASE_URL="http://localhost:3000"
SESSION_ID="example_session_$(date +%s)"

echo "🧪 RAG Chat Application - cURL Examples"
echo "======================================="
echo "Base URL: $BASE_URL"
echo "Session ID: $SESSION_ID"
echo ""

# Function to pretty print JSON
print_json() {
    echo "$1" | jq . 2>/dev/null || echo "$1"
}

echo "1. 🏥 Health Check"
echo "=================="
echo "Command: curl $BASE_URL/api/health"
response=$(curl -s "$BASE_URL/api/health")
print_json "$response"
echo ""

echo "2. 💬 Basic Chat"
echo "================"
chat_command="curl -X POST $BASE_URL/api/chat \\
  -H \"Content-Type: application/json\" \\
  -d '{
    \"message\": \"Hello! What can you help me with?\",
    \"sessionId\": \"$SESSION_ID\"
  }'"
echo "Command: $chat_command"

response=$(curl -s -X POST "$BASE_URL/api/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"Hello! What can you help me with?\",
    \"sessionId\": \"$SESSION_ID\"
  }")
print_json "$response"
echo ""

echo "3. 📚 Meta Llama 4 Scout Prompt Example"
echo "======================================="
meta_command="curl -X POST $BASE_URL/api/chat \\
  -H \"Content-Type: application/json\" \\
  -d '{
    \"message\": \"Using your knowledge base, explain how RAG systems work and their benefits in AI applications.\",
    \"sessionId\": \"$SESSION_ID\"
  }'"
echo "Command: $meta_command"

response=$(curl -s -X POST "$BASE_URL/api/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"Using your knowledge base, explain how RAG systems work and their benefits in AI applications.\",
    \"sessionId\": \"$SESSION_ID\"
  }")
print_json "$response"
echo ""

echo "4. 📄 Document Upload Example"
echo "============================="

# Create a sample document
cat > sample_document.txt << 'EOF'
# RAG Systems Documentation

## What is RAG?

Retrieval-Augmented Generation (RAG) is a powerful AI technique that combines:
- Document retrieval from a knowledge base
- Text generation using large language models

## How RAG Works

1. **Document Ingestion**: Documents are split into chunks and embedded
2. **Vector Storage**: Embeddings are stored in a vector database
3. **Query Processing**: User queries are embedded and similar documents retrieved
4. **Context Assembly**: Retrieved documents provide context for the LLM
5. **Response Generation**: LLM generates responses based on context

## Benefits of RAG

- **Domain-specific knowledge**: Access to custom knowledge bases
- **Up-to-date information**: Can be updated with new documents
- **Reduced hallucination**: Responses grounded in actual documents
- **Transparency**: Sources can be cited and verified

## Meta Llama 4 Scout Integration

Meta Llama 4 Scout models work excellently with RAG systems:
- Advanced reasoning capabilities
- Better context understanding
- Improved instruction following
- Efficient quantized versions available
EOF

upload_command="curl -X POST $BASE_URL/api/documents/upload \\
  -F \"document=@sample_document.txt\""
echo "Command: $upload_command"

response=$(curl -s -X POST "$BASE_URL/api/documents/upload" \
  -F "document=@sample_document.txt")
print_json "$response"
echo ""

# Wait a moment for document processing
echo "⏳ Waiting for document to be processed..."
sleep 3

echo "5. 🔍 RAG Query with Uploaded Document"
echo "======================================"
rag_command="curl -X POST $BASE_URL/api/chat \\
  -H \"Content-Type: application/json\" \\
  -d '{
    \"message\": \"Based on the uploaded documentation, explain the benefits of RAG systems.\",
    \"sessionId\": \"$SESSION_ID\"
  }'"
echo "Command: $rag_command"

response=$(curl -s -X POST "$BASE_URL/api/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"Based on the uploaded documentation, explain the benefits of RAG systems.\",
    \"sessionId\": \"$SESSION_ID\"
  }")
print_json "$response"
echo ""

echo "6. 🧠 Conversation Memory Test"
echo "=============================="
memory_command1="curl -X POST $BASE_URL/api/chat \\
  -H \"Content-Type: application/json\" \\
  -d '{
    \"message\": \"My name is Alex and I work as a data scientist.\",
    \"sessionId\": \"$SESSION_ID\"
  }'"
echo "Command 1: $memory_command1"

response=$(curl -s -X POST "$BASE_URL/api/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"My name is Alex and I work as a data scientist.\",
    \"sessionId\": \"$SESSION_ID\"
  }")
print_json "$response"
echo ""

memory_command2="curl -X POST $BASE_URL/api/chat \\
  -H \"Content-Type: application/json\" \\
  -d '{
    \"message\": \"What is my name and profession?\",
    \"sessionId\": \"$SESSION_ID\"
  }'"
echo "Command 2: $memory_command2"

response=$(curl -s -X POST "$BASE_URL/api/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"What is my name and profession?\",
    \"sessionId\": \"$SESSION_ID\"
  }")
print_json "$response"
echo ""

echo "7. 📋 List Documents"
echo "==================="
list_command="curl $BASE_URL/api/documents"
echo "Command: $list_command"

response=$(curl -s "$BASE_URL/api/documents")
print_json "$response"
echo ""

# Clean up
rm -f sample_document.txt

echo "✅ All examples completed!"
echo ""
echo "📝 Additional cURL Examples:"
echo ""
echo "# Error handling test (empty message)"
echo "curl -X POST $BASE_URL/api/chat \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"message\": \"\", \"sessionId\": \"test\"}'"
echo ""
echo "# Upload different file types"
echo "curl -X POST $BASE_URL/api/documents/upload \\"
echo "  -F \"document=@your_document.pdf\""
echo ""
echo "# Check specific session conversation"
echo "curl -X POST $BASE_URL/api/chat \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"message\": \"What did we discuss earlier?\", \"sessionId\": \"specific_session_id\"}'"
echo ""
echo "🔗 For more information, see the README.md file"
