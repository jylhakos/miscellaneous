#!/bin/bash

# RAG Application Start Script
# This script starts all Docker services for the RAG application

set -e  # Exit on any error

echo "🚀 Starting RAG Chat Application"
echo "================================"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check Docker Compose availability
DOCKER_COMPOSE_CMD=""
if command_exists docker-compose; then
    DOCKER_COMPOSE_CMD="docker-compose"
elif docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="docker compose"
else
    echo "❌ Docker Compose is not available. Please install it first."
    echo "Run: sudo apt install docker-compose"
    exit 1
fi

echo "✅ Using Docker Compose command: $DOCKER_COMPOSE_CMD"

# Navigate to project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

# Start services
echo ""
echo "🐳 Starting Docker containers..."
echo "This may take a few minutes on first run to download images..."

# Start all services in the background
$DOCKER_COMPOSE_CMD up -d

# Wait a moment for services to initialize
echo ""
echo "⏳ Waiting for services to initialize..."
sleep 10

# Check service status
echo ""
echo "📊 Service Status:"
$DOCKER_COMPOSE_CMD ps

# Check which services are healthy
echo ""
echo "🔍 Checking service health..."

# Function to check if a service is running
check_service() {
    local service_name=$1
    local port=$2
    local url=$3
    
    if $DOCKER_COMPOSE_CMD ps | grep -q "$service_name.*Up"; then
        echo "✅ $service_name: Running"
        if [ -n "$port" ]; then
            echo "   📍 Available at: http://localhost:$port$url"
        fi
    else
        echo "❌ $service_name: Not running"
        return 1
    fi
}

# Check individual services
check_service "ollama" "11434" ""
check_service "chromadb" "8000" ""
check_service "rag-chat-app" "3000" "/api/health"
check_service "nginx" "80" ""
check_service "open-webui" "3001" ""

echo ""
echo "🎉 RAG Application Started Successfully!"
echo ""
echo "📌 Quick Access URLs:"
echo "   🌐 Main Application: http://localhost"
echo "   🔧 RAG API: http://localhost:3000"
echo "   🤖 Open WebUI: http://localhost:3001"
echo "   📊 Health Check: http://localhost:3000/api/health"
echo ""
echo "📋 Useful Commands:"
echo "   📝 View logs: $DOCKER_COMPOSE_CMD logs -f [service-name]"
echo "   🔄 Restart service: $DOCKER_COMPOSE_CMD restart [service-name]"
echo "   ⏹️  Stop all: ./scripts/stop.sh"
echo ""
echo "💡 To download AI models, run: ./scripts/setup-models.sh"
