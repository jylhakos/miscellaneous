#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🛑 Stopping Node.js QA Chat Service...${NC}"

# Find and kill the Node.js process
if [ -f "qa-service.pid" ]; then
    QA_PID=$(cat qa-service.pid)
    if ps -p $QA_PID > /dev/null; then
        kill $QA_PID
        echo -e "${GREEN}✅ QA Chat Service (PID: $QA_PID) stopped.${NC}"
    else
        echo -e "${YELLOW}⚠️ Process with PID $QA_PID was not running.${NC}"
    fi
    rm -f qa-service.pid
else
    # Try to find and kill node processes running index.js
    PIDS=$(pgrep -f "node.*index.js")
    if [ ! -z "$PIDS" ]; then
        echo "$PIDS" | xargs kill
        echo -e "${GREEN}✅ Node.js QA Chat Service processes stopped.${NC}"
    else
        echo -e "${YELLOW}⚠️ No Node.js QA Chat Service processes found.${NC}"
    fi
fi

echo -e "${GREEN}🎉 Node.js service shutdown complete!${NC}"
