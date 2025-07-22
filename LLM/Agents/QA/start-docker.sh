#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
OLLAMA_CONTAINER_NAME="ollama-server"
OPENWEBUI_CONTAINER_NAME="open-webui"

echo -e "${GREEN}🐳 Starting Docker Services for QA Chat System...${NC}"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Docker is installed
if ! command_exists docker; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# 1. Start Ollama server
echo -e "${YELLOW}🚀 Starting Ollama server...${NC}"

if [ "$(docker ps -q -f name=$OLLAMA_CONTAINER_NAME)" ]; then
    echo -e "${GREEN}✅ Ollama container is already running.${NC}"
else
    if [ "$(docker ps -aq -f status=exited -f name=$OLLAMA_CONTAINER_NAME)" ]; then
        echo -e "${YELLOW}🔄 Starting existing Ollama container...${NC}"
        docker start $OLLAMA_CONTAINER_NAME
    else
        echo -e "${YELLOW}🆕 Creating new Ollama container...${NC}"
        docker run -d \
            --name $OLLAMA_CONTAINER_NAME \
            -p 11434:11434 \
            -v ollama:/root/.ollama \
            --restart unless-stopped \
            ollama/ollama:latest
    fi
fi

# Wait for Ollama to be ready
echo -e "${YELLOW}⏳ Waiting for Ollama server to be ready...${NC}"
sleep 5

# Check if Llama 4 Scout model is available, if not pull it
echo -e "${YELLOW}🔍 Checking for Llama 4 Scout model...${NC}"
if ! docker exec $OLLAMA_CONTAINER_NAME ollama list | grep -q "llama4:scout"; then
    echo -e "${YELLOW}📥 Pulling Llama 4 Scout model (this may take a while)...${NC}"
    docker exec $OLLAMA_CONTAINER_NAME ollama pull llama4:scout
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Llama 4 Scout model downloaded successfully.${NC}"
    else
        echo -e "${RED}❌ Failed to download Llama 4 Scout model. Trying alternative...${NC}"
        echo -e "${YELLOW}📥 Trying to pull llama3.1 as fallback...${NC}"
        docker exec $OLLAMA_CONTAINER_NAME ollama pull llama3.1
    fi
else
    echo -e "${GREEN}✅ Llama 4 Scout model is available.${NC}"
fi

# 2. Start Open WebUI
echo -e "${YELLOW}🌐 Starting Open WebUI...${NC}"

if [ "$(docker ps -q -f name=$OPENWEBUI_CONTAINER_NAME)" ]; then
    echo -e "${GREEN}✅ Open WebUI container is already running.${NC}"
else
    if [ "$(docker ps -aq -f status=exited -f name=$OPENWEBUI_CONTAINER_NAME)" ]; then
        echo -e "${YELLOW}🔄 Starting existing Open WebUI container...${NC}"
        docker start $OPENWEBUI_CONTAINER_NAME
    else
        echo -e "${YELLOW}🆕 Creating new Open WebUI container...${NC}"
        docker run -d \
            --name $OPENWEBUI_CONTAINER_NAME \
            -p 8080:8080 \
            -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
            --add-host=host.docker.internal:host-gateway \
            -v open-webui:/app/backend/data \
            --restart unless-stopped \
            ghcr.io/open-webui/open-webui:main
    fi
fi

# Wait for Open WebUI to be ready
echo -e "${YELLOW}⏳ Waiting for Open WebUI to be ready...${NC}"
sleep 10

# Test services
echo -e "${YELLOW}🧪 Testing services...${NC}"

# Test Ollama
if curl -s http://localhost:11434 > /dev/null; then
    echo -e "${GREEN}✅ Ollama server is responding.${NC}"
else
    echo -e "${RED}❌ Ollama server is not responding.${NC}"
fi

# Test Open WebUI
if curl -s http://localhost:8080 > /dev/null; then
    echo -e "${GREEN}✅ Open WebUI is responding.${NC}"
else
    echo -e "${RED}❌ Open WebUI is not responding.${NC}"
fi

echo -e "${GREEN}🎉 Docker services startup complete!${NC}"
echo -e "${GREEN}📋 Service URLs:${NC}"
echo -e "   🐳 Ollama API: http://localhost:11434"
echo -e "   🌐 Open WebUI: http://localhost:8080"
echo -e ""
echo -e "${YELLOW}💡 Next steps:${NC}"
echo -e "   1. Run ./start-nodejs.sh to start the QA Chat Service"
echo -e "   2. Configure Nginx with ./startup.sh for HTTPS support"
echo -e "   3. Access Open WebUI at http://localhost:8080"
echo -e ""
echo -e "${YELLOW}📝 To stop Docker services, run: ./stop-docker.sh${NC}"
