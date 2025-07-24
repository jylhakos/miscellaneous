#!/bin/bash

# RAG Application Stop Script
# This script stops all Docker services for the RAG application

set -e  # Exit on any error

echo "🛑 Stopping RAG Chat Application"
echo "================================"

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

echo "✅ Using Docker Compose command: $DOCKER_COMPOSE_CMD"

# Navigate to project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

# Check if any services are running
if ! $DOCKER_COMPOSE_CMD ps | grep -q "Up"; then
    echo "ℹ️  No RAG services are currently running."
    exit 0
fi

# Show current status
echo ""
echo "📊 Current Service Status:"
$DOCKER_COMPOSE_CMD ps

# Stop services
echo ""
echo "🔽 Stopping all RAG services..."
$DOCKER_COMPOSE_CMD down

# Wait a moment
sleep 2

# Verify all services are stopped
echo ""
echo "✅ All RAG services have been stopped."

# Option to remove volumes (data)
echo ""
read -p "🗑️  Do you want to remove data volumes as well? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️  Removing data volumes..."
    $DOCKER_COMPOSE_CMD down -v
    echo "✅ Data volumes removed."
    echo "⚠️  Note: All uploaded documents and conversation history have been deleted."
else
    echo "💾 Data volumes preserved."
fi

echo ""
echo "🎉 RAG Application stopped successfully!"
echo ""
echo "📋 Useful Commands:"
echo "   🚀 Start again: ./scripts/start.sh"
echo "   🔍 View remaining containers: docker ps -a"
echo "   🗑️  Clean up everything: docker system prune"
