#!/bin/bash

# RAG Application Status Script
# This script shows the current status of all Docker services

set -e  # Exit on any error

echo "📊 RAG Chat Application Status"
echo "============================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Docker Compose availability
DOCKER_COMPOSE_CMD=""
if command_exists docker-compose; then
    DOCKER_COMPOSE_CMD="docker-compose"
elif docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="docker compose"
else
    echo "❌ Docker Compose is not available."
    exit 1
fi

# Navigate to project directory  
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

# Show service status
echo ""
echo "🐳 Docker Container Status:"
$DOCKER_COMPOSE_CMD ps

# Show resource usage
echo ""
echo "💾 Resource Usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" $(docker ps --format "{{.Names}}" | grep rag- | head -5) 2>/dev/null || echo "No running containers found"

# Check individual service health
echo ""
echo "🔍 Service Health Checks:"

# Function to check if a port is open
check_port() {
    local port=$1
    local service=$2
    if nc -z localhost $port 2>/dev/null; then
        echo "✅ $service (port $port): Available"
    else
        echo "❌ $service (port $port): Not accessible"
    fi
}

check_port 11434 "Ollama LLM Server"
check_port 8000 "ChromaDB Vector Store"
check_port 3000 "RAG Application"
check_port 80 "Nginx Reverse Proxy"
check_port 3001 "Open WebUI"

# Test API endpoints
echo ""
echo "🌐 API Endpoint Tests:"

# Test health endpoint
if curl -s -f "http://localhost:3000/api/health" > /dev/null 2>&1; then
    echo "✅ RAG API Health: OK"
else
    echo "❌ RAG API Health: Failed"
fi

# Test Ollama
if curl -s -f "http://localhost:11434/api/tags" > /dev/null 2>&1; then
    echo "✅ Ollama API: OK"
else
    echo "❌ Ollama API: Failed"
fi

# Show disk usage
echo ""
echo "💿 Docker Volume Usage:"
docker system df --format "table {{.Type}}\t{{.TotalCount}}\t{{.Size}}\t{{.Reclaimable}}"

# Show logs summary
echo ""
echo "📝 Recent Log Summary:"
echo "   View full logs with: $DOCKER_COMPOSE_CMD logs -f [service-name]"
echo "   Services: ollama, chromadb, rag-app, nginx, open-webui"

echo ""
echo "🎯 Quick Actions:"
echo "   🚀 Start services: ./scripts/start.sh"
echo "   ⏹️  Stop services: ./scripts/stop.sh"
echo "   🔄 Restart all: $DOCKER_COMPOSE_CMD restart"
echo "   📊 View logs: $DOCKER_COMPOSE_CMD logs -f"
