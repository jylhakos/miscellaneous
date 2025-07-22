#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
OLLAMA_CONTAINER_NAME="ollama-server"
OPENWEBUI_CONTAINER_NAME="open-webui"

echo -e "${YELLOW}🛑 Stopping Docker Services for QA Chat System...${NC}"

# Stop Open WebUI
echo -e "${YELLOW}🛑 Stopping Open WebUI container...${NC}"
if [ "$(docker ps -q -f name=$OPENWEBUI_CONTAINER_NAME)" ]; then
    docker stop $OPENWEBUI_CONTAINER_NAME
    echo -e "${GREEN}✅ Open WebUI container stopped.${NC}"
else
    echo -e "${YELLOW}⚠️ Open WebUI container was not running.${NC}"
fi

# Stop Ollama
echo -e "${YELLOW}🛑 Stopping Ollama container...${NC}"
if [ "$(docker ps -q -f name=$OLLAMA_CONTAINER_NAME)" ]; then
    docker stop $OLLAMA_CONTAINER_NAME
    echo -e "${GREEN}✅ Ollama container stopped.${NC}"
else
    echo -e "${YELLOW}⚠️ Ollama container was not running.${NC}"
fi

# Optional: Remove containers completely (uncomment if needed)
echo -e "${YELLOW}❓ Do you want to remove the containers completely? (y/N): ${NC}"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo -e "${YELLOW}🗑️ Removing Docker containers...${NC}"
    docker rm $OPENWEBUI_CONTAINER_NAME $OLLAMA_CONTAINER_NAME 2>/dev/null || true
    echo -e "${GREEN}✅ Containers removed.${NC}"
else
    echo -e "${YELLOW}📝 Containers stopped but not removed. They can be restarted with ./start-docker.sh${NC}"
fi

echo -e "${GREEN}🎉 Docker services shutdown complete!${NC}"
