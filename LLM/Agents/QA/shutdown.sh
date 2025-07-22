#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
OLLAMA_CONTAINER_NAME="ollama-server"
OPENWEBUI_CONTAINER_NAME="open-webui"

echo -e "${YELLOW}🛑 Shutting down QA Chat System...${NC}"

# 1. Stop Node.js QA service
echo -e "${YELLOW}🛑 Stopping QA Chat Service...${NC}"
if [ -f "qa-service.pid" ]; then
    QA_PID=$(cat qa-service.pid)
    if ps -p $QA_PID > /dev/null; then
        kill $QA_PID
        echo -e "${GREEN}✅ QA Chat Service stopped.${NC}"
    else
        echo -e "${YELLOW}⚠️ QA Chat Service was not running.${NC}"
    fi
    rm -f qa-service.pid
else
    # Try to find and kill node processes running index.js
    pkill -f "node.*index.js" && echo -e "${GREEN}✅ QA Chat Service stopped.${NC}" || echo -e "${YELLOW}⚠️ No QA Chat Service found.${NC}"
fi

# 2. Stop Docker containers
echo -e "${YELLOW}🐳 Stopping Docker containers...${NC}"

# Stop Open WebUI
if [ "$(docker ps -q -f name=$OPENWEBUI_CONTAINER_NAME)" ]; then
    docker stop $OPENWEBUI_CONTAINER_NAME
    echo -e "${GREEN}✅ Open WebUI container stopped.${NC}"
else
    echo -e "${YELLOW}⚠️ Open WebUI container was not running.${NC}"
fi

# Stop Ollama
if [ "$(docker ps -q -f name=$OLLAMA_CONTAINER_NAME)" ]; then
    docker stop $OLLAMA_CONTAINER_NAME
    echo -e "${GREEN}✅ Ollama container stopped.${NC}"
else
    echo -e "${YELLOW}⚠️ Ollama container was not running.${NC}"
fi

# 3. Optional: Remove containers (uncomment if you want to remove them completely)
# echo -e "${YELLOW}🗑️ Removing Docker containers...${NC}"
# docker rm $OPENWEBUI_CONTAINER_NAME $OLLAMA_CONTAINER_NAME 2>/dev/null || true

# 4. Restore default Nginx configuration (optional)
echo -e "${YELLOW}🌐 Nginx configuration...${NC}"
if [ -f "/etc/nginx/sites-enabled/qa-chat" ]; then
    echo -e "${YELLOW}💡 Nginx configuration for QA Chat is still active.${NC}"
    echo -e "${YELLOW}💡 To remove it: sudo rm /etc/nginx/sites-enabled/qa-chat && sudo systemctl reload nginx${NC}"
else
    echo -e "${GREEN}✅ No custom Nginx configuration found.${NC}"
fi

echo -e "${GREEN}🎉 QA Chat System shutdown complete!${NC}"
echo -e "${YELLOW}📝 Note: Docker containers are stopped but not removed.${NC}"
echo -e "${YELLOW}📝 Note: Nginx configuration is preserved.${NC}"
echo -e "${YELLOW}📝 To start again, run: ./startup.sh${NC}"
