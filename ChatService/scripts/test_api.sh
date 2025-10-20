#!/bin/bash

# Chat Service API Test Scripts
# Base URL for the API
BASE_URL="http://localhost:8080/v1"

echo "===== Chat Service API Tests ====="
echo

# Test 1: Health Check
echo "1. Testing Health Check..."
curl -s -X GET http://localhost:8080/health | jq .
echo -e "\n"

# Test 2: Create a new message
echo "2. Creating a new message..."
MESSAGE_RESPONSE=$(curl -s -X POST "$BASE_URL/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Hello from API test!",
    "sender_id": "test_user_001",
    "message_type": "text",
    "priority": "normal",
    "tags": ["api-test", "curl"]
  }')

echo $MESSAGE_RESPONSE | jq .
MESSAGE_ID=$(echo $MESSAGE_RESPONSE | jq -r '.id')
echo "Created message ID: $MESSAGE_ID"
echo -e "\n"

# Test 3: Get the created message
echo "3. Retrieving the created message..."
curl -s -X GET "$BASE_URL/messages/$MESSAGE_ID" | jq .
echo -e "\n"

# Test 4: List all messages
echo "4. Listing all messages (first page)..."
curl -s -X GET "$BASE_URL/messages?page=1&limit=5" | jq .
echo -e "\n"

# Test 5: Check anomaly score
echo "5. Checking anomaly score for the message..."
curl -s -X GET "$BASE_URL/messages/$MESSAGE_ID/anomaly-check" | jq .
echo -e "\n"

# Test 6: Create a suspicious message (should have high anomaly score)
echo "6. Creating a suspicious message..."
SPAM_RESPONSE=$(curl -s -X POST "$BASE_URL/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "FREE MONEY!!! CLICK HERE NOW!!! URGENT!!!",
    "sender_id": "suspicious_user",
    "message_type": "text",
    "priority": "high"
  }')

echo $SPAM_RESPONSE | jq .
SPAM_MESSAGE_ID=$(echo $SPAM_RESPONSE | jq -r '.id')
echo -e "\n"

# Test 7: Check anomaly score for suspicious message
echo "7. Checking anomaly score for suspicious message..."
curl -s -X GET "$BASE_URL/messages/$SPAM_MESSAGE_ID/anomaly-check" | jq .
echo -e "\n"

# Test 8: Delete a message
echo "8. Deleting the suspicious message..."
curl -s -X DELETE "$BASE_URL/messages/$SPAM_MESSAGE_ID" -w "HTTP Status: %{http_code}\n"
echo -e "\n"

# Test 9: Try to retrieve deleted message (should return 404)
echo "9. Trying to retrieve deleted message (should return 404)..."
curl -s -X GET "$BASE_URL/messages/$SPAM_MESSAGE_ID" -w "HTTP Status: %{http_code}\n" | jq .
echo -e "\n"

# Test 10: Test invalid requests
echo "10. Testing invalid requests..."

echo "10a. Creating message with invalid data..."
curl -s -X POST "$BASE_URL/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "",
    "sender_id": "",
    "message_type": "invalid_type"
  }' | jq .
echo -e "\n"

echo "10b. Getting message with invalid ID..."
curl -s -X GET "$BASE_URL/messages/invalid_id" -w "HTTP Status: %{http_code}\n" | jq .
echo -e "\n"

echo "===== API Tests Completed ====="