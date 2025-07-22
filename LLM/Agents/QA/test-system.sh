#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Testing QA Chat System...${NC}"

# Configuration
BASE_URL="http://localhost:3000"
HTTPS_URL="https://localhost"

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run a test
run_test() {
    local test_name="$1"
    local command="$2"
    local expected_status="$3"
    
    echo -e "${YELLOW}Testing: $test_name${NC}"
    
    response=$(eval "$command" 2>/dev/null)
    status=$?
    
    if [ $status -eq $expected_status ]; then
        echo -e "${GREEN}✅ PASS: $test_name${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        if [ ! -z "$response" ]; then
            echo -e "${BLUE}Response: ${response:0:100}...${NC}"
        fi
    else
        echo -e "${RED}❌ FAIL: $test_name${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        if [ ! -z "$response" ]; then
            echo -e "${RED}Error: $response${NC}"
        fi
    fi
    echo ""
}

# Test 1: Health check
run_test "Health Check" \
    "curl -s -o /dev/null -w '%{http_code}' $BASE_URL/health" \
    0

# Test 2: Ollama connection
run_test "Ollama Server Connection" \
    "curl -s -o /dev/null -w '%{http_code}' http://localhost:11434" \
    0

# Test 3: Create session
echo -e "${YELLOW}Testing: Create Session${NC}"
session_response=$(curl -s -X POST $BASE_URL/api/session 2>/dev/null)
if echo "$session_response" | grep -q "sessionId"; then
    SESSION_ID=$(echo "$session_response" | grep -o '"sessionId":"[^"]*"' | cut -d'"' -f4)
    echo -e "${GREEN}✅ PASS: Create Session (ID: $SESSION_ID)${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}❌ FAIL: Create Session${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    SESSION_ID="test-session"
fi
echo ""

# Test 4: Ask question via GET
run_test "Ask Question (GET)" \
    "curl -s '$BASE_URL/api/ask?question=What is 2+2?' | grep -q 'answer'" \
    0

# Test 5: Ask question via POST
run_test "Ask Question (POST)" \
    "curl -s -X POST $BASE_URL/api/ask -H 'Content-Type: application/json' -d '{\"question\":\"Hello\",\"sessionId\":\"$SESSION_ID\"}' | grep -q 'answer'" \
    0

# Test 6: Get session history
run_test "Get Session History" \
    "curl -s $BASE_URL/api/session/$SESSION_ID/history | grep -q 'history'" \
    0

# Test 7: Test with complex question
run_test "Complex Question" \
    "curl -s '$BASE_URL/api/ask?question=Explain artificial intelligence in one sentence' | grep -q 'answer'" \
    0

# Test 8: Clear session
run_test "Clear Session" \
    "curl -s -X DELETE $BASE_URL/api/session/$SESSION_ID | grep -q 'cleared'" \
    0

# Test 9: Test HTTPS (if nginx is configured)
if command -v nginx >/dev/null 2>&1 && systemctl is-active --quiet nginx; then
    run_test "HTTPS Health Check" \
        "curl -s -k -o /dev/null -w '%{http_code}' $HTTPS_URL/health" \
        0
    
    run_test "HTTPS API Call" \
        "curl -s -k '$HTTPS_URL/api/ask?question=Test HTTPS' | grep -q 'answer'" \
        0
fi

# Test 10: Performance test (multiple requests)
echo -e "${YELLOW}Testing: Performance (5 concurrent requests)${NC}"
for i in {1..5}; do
    curl -s "$BASE_URL/api/ask?question=Test question $i" > /dev/null &
done
wait

# Wait a moment and check if server is still responsive
sleep 2
performance_test=$(curl -s -o /dev/null -w '%{http_code}' $BASE_URL/health)
if [ "$performance_test" = "200" ]; then
    echo -e "${GREEN}✅ PASS: Performance Test${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}❌ FAIL: Performance Test${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
echo ""

# Test Summary
echo -e "${BLUE}📊 Test Summary:${NC}"
echo -e "${GREEN}✅ Tests Passed: $TESTS_PASSED${NC}"
echo -e "${RED}❌ Tests Failed: $TESTS_FAILED${NC}"
echo -e "${BLUE}📈 Success Rate: $(( TESTS_PASSED * 100 / (TESTS_PASSED + TESTS_FAILED) ))%${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed! Your QA Chat System is working correctly.${NC}"
    exit 0
else
    echo -e "${RED}⚠️ Some tests failed. Please check the system configuration.${NC}"
    exit 1
fi
