#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Node.js QA Chat Service...${NC}"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️ .env file not found. Copying from .env.example...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✅ .env file created. Please review and update the configuration.${NC}"
    else
        echo -e "${RED}❌ .env.example file not found. Please create a .env file with the required configuration.${NC}"
        exit 1
    fi
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Installing Node.js dependencies...${NC}"
    npm install
fi

# Check if Ollama is running
echo -e "${YELLOW}🔍 Checking Ollama connection...${NC}"
OLLAMA_URL="http://localhost:11434"
if curl -s "$OLLAMA_URL" > /dev/null; then
    echo -e "${GREEN}✅ Ollama server is running.${NC}"
else
    echo -e "${RED}❌ Ollama server is not running. Please start Ollama first.${NC}"
    echo -e "${YELLOW}💡 You can start Ollama with: docker run -d --name ollama-server -p 11434:11434 -v ollama:/root/.ollama ollama/ollama:latest${NC}"
    exit 1
fi

# Start the Node.js service
echo -e "${YELLOW}🚀 Starting QA Chat Service on port 3000...${NC}"

# Run in development mode if NODE_ENV is development
if [ "$NODE_ENV" = "development" ]; then
    echo -e "${YELLOW}🔧 Running in development mode with nodemon...${NC}"
    npx nodemon src/index.js
else
    echo -e "${GREEN}🚀 Running in production mode...${NC}"
    node src/index.js
fi
