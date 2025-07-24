#!/bin/bash

# RAG Chat Application Installation Script
# This script installs Node.js, Docker, Docker Compose, and sets up the RAG application

set -e

echo "🚀 RAG Chat Application Installation Script"
echo "==========================================="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ This script should not be run as root. Please run as a regular user with sudo privileges."
   exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install Node.js
install_nodejs() {
    echo "📦 Installing Node.js..."
    
    if command_exists node; then
        echo "✅ Node.js is already installed ($(node --version))"
        return 0
    fi

    # Install Node.js via NodeSource repository
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
    
    echo "✅ Node.js installed successfully ($(node --version))"
}

# Function to install Docker
install_docker() {
    echo "🐳 Installing Docker..."
    
    if command_exists docker; then
        echo "✅ Docker is already installed ($(docker --version))"
        return 0
    fi

    # Install Docker
    sudo apt-get update
    sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
    
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io
    
    # Add current user to docker group
    sudo usermod -aG docker $USER
    
    echo "✅ Docker installed successfully"
    echo "⚠️  Please log out and log back in for Docker group membership to take effect"
}

# Function to install Docker Compose
install_docker_compose() {
    echo "🔧 Installing Docker Compose..."
    
    if command_exists docker-compose; then
        echo "✅ Docker Compose is already installed ($(docker-compose --version))"
        return 0
    fi

    # Install Docker Compose
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    echo "✅ Docker Compose installed successfully"
}

# Function to install application dependencies
install_app_dependencies() {
    echo "📚 Installing application dependencies..."
    
    if [ ! -f "package.json" ]; then
        echo "❌ package.json not found. Make sure you're in the correct directory."
        exit 1
    fi
    
    npm install
    echo "✅ Application dependencies installed"
}

# Function to setup environment
setup_environment() {
    echo "⚙️  Setting up environment..."
    
    if [ ! -f ".env" ]; then
        cp .env.example .env
        echo "📝 Created .env file from .env.example"
        echo "⚠️  Please review and update the .env file with your specific configuration"
    else
        echo "✅ .env file already exists"
    fi
    
    # Create necessary directories
    mkdir -p uploads logs nginx/ssl
    echo "✅ Created necessary directories"
}

# Function to download Ollama models
download_ollama_models() {
    echo "🤖 Setting up Ollama models..."
    
    echo "This will download the required models. This may take a while depending on your internet connection."
    read -p "Do you want to download Ollama models now? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Starting Docker Compose to download models..."
        docker-compose up -d ollama
        
        # Wait for Ollama to be ready
        echo "Waiting for Ollama to be ready..."
        sleep 10
        
        # Download models
        echo "Downloading Llama 3.1 8B model..."
        docker-compose exec ollama ollama pull llama3.1:8b
        
        echo "Downloading embedding model..."
        docker-compose exec ollama ollama pull nomic-embed-text
        
        echo "✅ Models downloaded successfully"
        
        # Ask about Meta Llama 4 Scout (when available)
        read -p "Do you want to download Meta Llama 4 Scout models? (y/N): " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "Attempting to download Meta Llama 4 Scout models..."
            docker-compose exec ollama ollama pull llama4-scout:4b || echo "⚠️  llama4-scout:4b not available yet"
            docker-compose exec ollama ollama pull llama4-scout:8b || echo "⚠️  llama4-scout:8b not available yet"
        fi
    else
        echo "⏭️  Skipping model download. You can download them later using:"
        echo "   docker-compose exec ollama ollama pull llama3.1:8b"
        echo "   docker-compose exec ollama ollama pull nomic-embed-text"
    fi
}

# Main installation process
main() {
    echo "Starting installation process..."
    
    # Update package list
    sudo apt-get update
    
    # Install basic dependencies
    sudo apt-get install -y curl wget git
    
    # Install components
    install_nodejs
    install_docker
    install_docker_compose
    install_app_dependencies
    setup_environment
    
    echo ""
    echo "🎉 Installation completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Review and update the .env file"
    echo "2. If Docker was just installed, log out and log back in"
    echo "3. Run 'docker-compose up -d' to start all services"
    echo "4. Run './scripts/setup-models.sh' to download AI models"
    echo "5. Visit http://localhost:3000 to access the application"
    echo ""
    echo "For more information, see the README.md file"
}

# Run main function
main "$@"
