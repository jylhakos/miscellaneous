#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 QA Chat System API Examples${NC}"
echo -e "${YELLOW}This script demonstrates how to use the QA Chat API${NC}"
echo ""

# Configuration
BASE_URL="http://localhost:3000"
HTTPS_URL="https://localhost"

# Check if service is running
echo -e "${YELLOW}🔍 Checking if QA service is running...${NC}"
if ! curl -s $BASE_URL/health > /dev/null; then
    echo -e "${RED}❌ QA service is not running. Please start it first with ./start-nodejs.sh${NC}"
    exit 1
fi
echo -e "${GREEN}✅ QA service is running${NC}"
echo ""

# Example 1: Health Check
echo -e "${BLUE}📋 Example 1: Health Check${NC}"
echo -e "${YELLOW}Command:${NC} curl $BASE_URL/health"
curl -s $BASE_URL/health | jq '.' 2>/dev/null || curl -s $BASE_URL/health
echo ""
echo ""

# Example 2: Simple Question (GET)
echo -e "${BLUE}💬 Example 2: Simple Question (GET Method)${NC}"
echo -e "${YELLOW}Command:${NC} curl '$BASE_URL/api/ask?question=What is artificial intelligence?'"
curl -s "$BASE_URL/api/ask?question=What is artificial intelligence?" | jq '.' 2>/dev/null || curl -s "$BASE_URL/api/ask?question=What is artificial intelligence?"
echo ""
echo ""

# Example 3: Create a Session
echo -e "${BLUE}🆕 Example 3: Create a New Session${NC}"
echo -e "${YELLOW}Command:${NC} curl -X POST $BASE_URL/api/session"
session_response=$(curl -s -X POST $BASE_URL/api/session)
echo "$session_response" | jq '.' 2>/dev/null || echo "$session_response"

# Extract session ID for further examples
SESSION_ID=$(echo "$session_response" | grep -o '"sessionId":"[^"]*"' | cut -d'"' -f4)
echo ""
echo ""

# Example 4: Question with Session (POST)
echo -e "${BLUE}💭 Example 4: Question with Session Context (POST Method)${NC}"
echo -e "${YELLOW}Command:${NC} curl -X POST $BASE_URL/api/ask -H 'Content-Type: application/json' -d '{\"question\":\"My name is John. What is machine learning?\",\"sessionId\":\"$SESSION_ID\"}'"
curl -s -X POST $BASE_URL/api/ask \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"My name is John. What is machine learning?\",\"sessionId\":\"$SESSION_ID\"}" | jq '.' 2>/dev/null || \
curl -s -X POST $BASE_URL/api/ask \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"My name is John. What is machine learning?\",\"sessionId\":\"$SESSION_ID\"}"
echo ""
echo ""

# Example 5: Follow-up Question (Testing Memory)
echo -e "${BLUE}🧠 Example 5: Follow-up Question (Testing Conversation Memory)${NC}"
echo -e "${YELLOW}Command:${NC} curl -X POST $BASE_URL/api/ask -H 'Content-Type: application/json' -d '{\"question\":\"What is my name?\",\"sessionId\":\"$SESSION_ID\"}'"
curl -s -X POST $BASE_URL/api/ask \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"What is my name?\",\"sessionId\":\"$SESSION_ID\"}" | jq '.' 2>/dev/null || \
curl -s -X POST $BASE_URL/api/ask \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"What is my name?\",\"sessionId\":\"$SESSION_ID\"}"
echo ""
echo ""

# Example 6: Get Session History
echo -e "${BLUE}📚 Example 6: Get Session History${NC}"
echo -e "${YELLOW}Command:${NC} curl $BASE_URL/api/session/$SESSION_ID/history"
curl -s $BASE_URL/api/session/$SESSION_ID/history | jq '.' 2>/dev/null || curl -s $BASE_URL/api/session/$SESSION_ID/history
echo ""
echo ""

# Example 7: Complex Question
echo -e "${BLUE}🤔 Example 7: Complex Question${NC}"
echo -e "${YELLOW}Command:${NC} curl -X POST $BASE_URL/api/ask -H 'Content-Type: application/json' -d '{\"question\":\"Explain the difference between supervised and unsupervised learning with examples\",\"sessionId\":\"$SESSION_ID\"}'"
curl -s -X POST $BASE_URL/api/ask \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"Explain the difference between supervised and unsupervised learning with examples\",\"sessionId\":\"$SESSION_ID\"}" | jq '.' 2>/dev/null || \
curl -s -X POST $BASE_URL/api/ask \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"Explain the difference between supervised and unsupervised learning with examples\",\"sessionId\":\"$SESSION_ID\"}"
echo ""
echo ""

# Example 8: Mathematical Question
echo -e "${BLUE}🔢 Example 8: Mathematical Question${NC}"
echo -e "${YELLOW}Command:${NC} curl '$BASE_URL/api/ask?question=Solve this equation: 2x + 5 = 13'"
curl -s "$BASE_URL/api/ask?question=Solve this equation: 2x + 5 = 13" | jq '.' 2>/dev/null || curl -s "$BASE_URL/api/ask?question=Solve this equation: 2x + 5 = 13"
echo ""
echo ""

# Example 9: Clear Session
echo -e "${BLUE}🗑️ Example 9: Clear Session${NC}"
echo -e "${YELLOW}Command:${NC} curl -X DELETE $BASE_URL/api/session/$SESSION_ID"
curl -s -X DELETE $BASE_URL/api/session/$SESSION_ID | jq '.' 2>/dev/null || curl -s -X DELETE $BASE_URL/api/session/$SESSION_ID
echo ""
echo ""

# Example 10: HTTPS Examples (if available)
if command -v nginx >/dev/null 2>&1 && systemctl is-active --quiet nginx 2>/dev/null; then
    echo -e "${BLUE}🔒 Example 10: HTTPS API Call${NC}"
    echo -e "${YELLOW}Command:${NC} curl -k '$HTTPS_URL/api/ask?question=Test HTTPS connection'"
    curl -s -k "$HTTPS_URL/api/ask?question=Test HTTPS connection" | jq '.' 2>/dev/null || curl -s -k "$HTTPS_URL/api/ask?question=Test HTTPS connection"
    echo ""
    echo ""
fi

# Performance Example
echo -e "${BLUE}⚡ Example 11: Concurrent Requests Test${NC}"
echo -e "${YELLOW}Running 3 concurrent requests...${NC}"

# Start concurrent requests
curl -s "$BASE_URL/api/ask?question=Question 1: What is AI?" > /tmp/resp1.json &
curl -s "$BASE_URL/api/ask?question=Question 2: What is ML?" > /tmp/resp2.json &
curl -s "$BASE_URL/api/ask?question=Question 3: What is DL?" > /tmp/resp3.json &

# Wait for all to complete
wait

echo -e "${GREEN}✅ All requests completed. Results:${NC}"
echo -e "${BLUE}Response 1:${NC}"
cat /tmp/resp1.json | jq '.' 2>/dev/null || cat /tmp/resp1.json
echo ""
echo -e "${BLUE}Response 2:${NC}"
cat /tmp/resp2.json | jq '.' 2>/dev/null || cat /tmp/resp2.json
echo ""
echo -e "${BLUE}Response 3:${NC}"
cat /tmp/resp3.json | jq '.' 2>/dev/null || cat /tmp/resp3.json
echo ""

# Cleanup temp files
rm -f /tmp/resp*.json

echo -e "${GREEN}🎉 API Examples Complete!${NC}"
echo ""
echo -e "${YELLOW}💡 Tips:${NC}"
echo -e "   • Use sessionId to maintain conversation context"
echo -e "   • GET method for simple questions"
echo -e "   • POST method for complex requests with session management"
echo -e "   • Monitor /health endpoint for service status"
echo -e "   • Use HTTPS in production environments"
echo ""
echo -e "${YELLOW}📚 Additional Resources:${NC}"
echo -e "   • Service Health: $BASE_URL/health"
echo -e "   • Open WebUI: http://localhost:8080"
echo -e "   • Ollama API: http://localhost:11434"
