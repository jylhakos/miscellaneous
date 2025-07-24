#!/bin/bash

# Setup Ollama Models Script
# Downloads and configures AI models for the RAG application

set -e

echo "🤖 Ollama Models Setup Script"
echo "============================="

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install it first."
    exit 1
fi

# Check if Ollama container is running
if ! docker-compose ps ollama | grep -q "Up"; then
    echo "🐳 Starting Ollama container..."
    docker-compose up -d ollama
    
    echo "⏳ Waiting for Ollama to be ready..."
    sleep 15
fi

# Function to check if model exists
model_exists() {
    docker-compose exec -T ollama ollama list | grep -q "$1" || return 1
}

# Function to download model with progress
download_model() {
    local model_name="$1"
    local description="$2"
    
    echo "📥 Downloading $description..."
    echo "   Model: $model_name"
    
    if model_exists "$model_name"; then
        echo "✅ $model_name is already downloaded"
        return 0
    fi
    
    echo "⬇️  This may take several minutes depending on your internet connection..."
    docker-compose exec -T ollama ollama pull "$model_name"
    
    if model_exists "$model_name"; then
        echo "✅ Successfully downloaded $model_name"
    else
        echo "❌ Failed to download $model_name"
        return 1
    fi
}

# Main models for the application
echo "📦 Downloading essential models for RAG application..."

download_model "llama3.1:8b" "Llama 3.1 8B (Main Chat Model)"
download_model "nomic-embed-text" "Nomic Embedding Model (for vector search)"

# Optional: Download smaller Llama model for faster responses
read -p "Do you want to download Llama 3.1 7B for faster responses? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    download_model "llama3.1:7b" "Llama 3.1 7B (Faster Alternative)"
fi

# Meta Llama 4 Scout models (when available)
echo ""
echo "🔬 Meta Llama 4 Scout Models"
echo "Note: These models may not be available yet. Check https://ollama.com/library for availability."

read -p "Do you want to try downloading Meta Llama 4 Scout models? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Try downloading Meta Llama 4 Scout models
    download_model "llama4-scout:4b" "Meta Llama 4 Scout 4B (Quantized)" || echo "⚠️  llama4-scout:4b not available yet"
    download_model "llama4-scout:8b" "Meta Llama 4 Scout 8B (Quantized)" || echo "⚠️  llama4-scout:8b not available yet"
fi

# Alternative quantized models
echo ""
read -p "Do you want to download alternative quantized models for lower memory usage? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    download_model "llama3.1:8b-instruct-q4_0" "Llama 3.1 8B Quantized (4-bit)" || echo "⚠️  Quantized version not available"
    download_model "phi3:3.8b" "Phi-3 3.8B (Lightweight Alternative)"
fi

# Show available models
echo ""
echo "📋 Available models in Ollama:"
docker-compose exec -T ollama ollama list

echo ""
echo "✅ Model setup completed!"
echo ""
echo "To use a specific model, update the OLLAMA_MODEL variable in your .env file:"
echo "   OLLAMA_MODEL=llama3.1:8b          # Default"
echo "   OLLAMA_MODEL=llama3.1:7b          # Faster"
echo "   OLLAMA_MODEL=llama4-scout:8b      # Meta Llama 4 Scout (when available)"
echo "   OLLAMA_MODEL=phi3:3.8b            # Lightweight"
echo ""
echo "For Meta Llama 4 Scout specific prompting, see:"
echo "   https://www.llama.com/docs/model-cards-and-prompt-formats/llama4/"
