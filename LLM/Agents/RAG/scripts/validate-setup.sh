#!/bin/bash

# RAG Chat Application Setup Validation
# This script validates that all components are properly configured

set -e

echo "🔍 RAG Chat Application - Setup Validation"
echo "==========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    case $status in
        "PASS")
            echo -e "${GREEN}✅ PASS${NC}: $message"
            ;;
        "FAIL")
            echo -e "${RED}❌ FAIL${NC}: $message"
            ;;
        "WARN")
            echo -e "${YELLOW}⚠️  WARN${NC}: $message"
            ;;
        "INFO")
            echo -e "${BLUE}ℹ️  INFO${NC}: $message"
            ;;
    esac
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is open
port_open() {
    nc -z localhost $1 2>/dev/null
}

# Function to check HTTP endpoint
check_http() {
    local url=$1
    local expected_status=${2:-200}
    local response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$url" 2>/dev/null || echo "HTTPSTATUS:000")
    local status=$(echo $response | sed -n 's/.*HTTPSTATUS:\([0-9]*\)$/\1/p')
    
    if [ "$status" = "$expected_status" ]; then
        return 0
    else
        return 1
    fi
}

echo ""
echo "📋 Checking Prerequisites..."
echo "=========================="

# Check Node.js
if command_exists node; then
    NODE_VERSION=$(node --version)
    print_status "PASS" "Node.js is installed ($NODE_VERSION)"
else
    print_status "FAIL" "Node.js is not installed"
fi

# Check npm
if command_exists npm; then
    NPM_VERSION=$(npm --version)
    print_status "PASS" "npm is installed ($NPM_VERSION)"
else
    print_status "FAIL" "npm is not installed"
fi

# Check Docker
if command_exists docker; then
    DOCKER_VERSION=$(docker --version)
    print_status "PASS" "Docker is installed ($DOCKER_VERSION)"
else
    print_status "FAIL" "Docker is not installed"
fi

# Check Docker Compose
if command_exists docker-compose; then
    COMPOSE_VERSION=$(docker-compose --version)
    print_status "PASS" "Docker Compose is installed ($COMPOSE_VERSION)"
else
    print_status "FAIL" "Docker Compose is not installed"
fi

echo ""
echo "📁 Checking Project Files..."
echo "=========================="

# Check package.json
if [ -f "package.json" ]; then
    print_status "PASS" "package.json exists"
else
    print_status "FAIL" "package.json not found"
fi

# Check .env file
if [ -f ".env" ]; then
    print_status "PASS" ".env file exists"
else
    if [ -f ".env.example" ]; then
        print_status "WARN" ".env file missing (but .env.example exists)"
    else
        print_status "FAIL" ".env and .env.example files missing"
    fi
fi

# Check Docker Compose file
if [ -f "docker-compose.yml" ]; then
    print_status "PASS" "docker-compose.yml exists"
else
    print_status "FAIL" "docker-compose.yml not found"
fi

# Check source files
if [ -d "src" ]; then
    print_status "PASS" "src directory exists"
    
    if [ -f "src/server.js" ]; then
        print_status "PASS" "src/server.js exists"
    else
        print_status "FAIL" "src/server.js not found"
    fi
    
    if [ -f "src/rag.js" ]; then
        print_status "PASS" "src/rag.js exists"
    else
        print_status "FAIL" "src/rag.js not found"
    fi
else
    print_status "FAIL" "src directory not found"
fi

echo ""
echo "🐳 Checking Docker Services..."
echo "============================="

# Check if Docker is running
if docker info >/dev/null 2>&1; then
    print_status "PASS" "Docker daemon is running"
else
    print_status "FAIL" "Docker daemon is not running"
    exit 1
fi

# Check Docker Compose services
if [ -f "docker-compose.yml" ]; then
    # Check if services are defined
    if docker-compose config >/dev/null 2>&1; then
        print_status "PASS" "Docker Compose configuration is valid"
        
        # Check individual services
        if docker-compose ps >/dev/null 2>&1; then
            print_status "INFO" "Docker Compose services status:"
            docker-compose ps --format "table {{.Name}}\t{{.State}}\t{{.Ports}}"
        fi
    else
        print_status "FAIL" "Docker Compose configuration is invalid"
    fi
fi

echo ""
echo "🌐 Checking Network Connectivity..."
echo "================================="

# Check if services are reachable
declare -A SERVICES=(
    ["Ollama"]="11434"
    ["ChromaDB"]="8000"
    ["RAG App"]="3000"
    ["Open WebUI"]="3001"
)

for service in "${!SERVICES[@]}"; do
    port=${SERVICES[$service]}
    if port_open $port; then
        print_status "PASS" "$service is reachable on port $port"
    else
        print_status "WARN" "$service is not reachable on port $port"
    fi
done

echo ""
echo "🔗 Checking API Endpoints..."
echo "==========================="

# Check health endpoint
if check_http "http://localhost:3000/api/health"; then
    print_status "PASS" "Health endpoint is responding"
    
    # Get health details
    HEALTH_RESPONSE=$(curl -s "http://localhost:3000/api/health" 2>/dev/null || echo '{}')
    echo "$HEALTH_RESPONSE" | jq . 2>/dev/null || echo "Health response: $HEALTH_RESPONSE"
else
    print_status "FAIL" "Health endpoint is not responding"
fi

# Check Ollama API
if check_http "http://localhost:11434/api/tags"; then
    print_status "PASS" "Ollama API is responding"
    
    # List available models
    MODELS=$(curl -s "http://localhost:11434/api/tags" 2>/dev/null | jq -r '.models[]?.name' 2>/dev/null || echo "Unable to list models")
    if [ "$MODELS" != "Unable to list models" ] && [ ! -z "$MODELS" ]; then
        print_status "INFO" "Available Ollama models:"
        echo "$MODELS"
    else
        print_status "WARN" "No models found or unable to list models"
    fi
else
    print_status "FAIL" "Ollama API is not responding"
fi

# Check ChromaDB API
if check_http "http://localhost:8000/api/v1/heartbeat"; then
    print_status "PASS" "ChromaDB API is responding"
else
    print_status "FAIL" "ChromaDB API is not responding"
fi

echo ""
echo "📊 System Summary..."
echo "==================="

# Count services
TOTAL_CHECKS=0
PASSED_CHECKS=0

# This is a simplified summary - in a real implementation, 
# you'd track the actual pass/fail counts from above

if command_exists node && command_exists docker && [ -f "package.json" ] && [ -f "docker-compose.yml" ]; then
    print_status "PASS" "Core requirements are met"
else
    print_status "FAIL" "Some core requirements are missing"
fi

echo ""
echo "💡 Next Steps:"
echo "============="

if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    echo "1. Copy .env.example to .env and configure your settings"
fi

if ! docker-compose ps | grep -q "Up"; then
    echo "2. Start the services: docker-compose up -d"
fi

if ! check_http "http://localhost:11434/api/tags"; then
    echo "3. Download AI models: ./scripts/setup-models.sh"
fi

if ! check_http "http://localhost:3000/api/health"; then
    echo "4. Check application logs: docker-compose logs rag-app"
fi

echo "5. Test the application: ./scripts/test.sh"
echo "6. Try the web interface: http://localhost:3000"
echo "7. Use cURL examples: ./examples/curl-examples.sh"

echo ""
echo "📚 For detailed setup instructions, see README.md"
echo "🐛 For troubleshooting, check the logs and health endpoint"
