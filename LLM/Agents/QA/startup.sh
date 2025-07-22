#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
OLLAMA_CONTAINER_NAME="ollama-server"
OPENWEBUI_CONTAINER_NAME="open-webui"
QA_SERVICE_NAME="qa-chat-service"
NGINX_SERVICE_NAME="nginx"

echo -e "${GREEN}🚀 Starting QA Chat System...${NC}"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    netstat -tlnp 2>/dev/null | grep ":$1 " >/dev/null
}

# Check dependencies
echo -e "${YELLOW}📋 Checking dependencies...${NC}"

if ! command_exists docker; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

if ! command_exists node; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js first.${NC}"
    exit 1
fi

if ! command_exists nginx; then
    echo -e "${RED}❌ Nginx is not installed. Please install Nginx first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All dependencies are available.${NC}"

# Check if required ports are available
echo -e "${YELLOW}🔍 Checking port availability...${NC}"

REQUIRED_PORTS=(3000 8080 11434 80 443)
for port in "${REQUIRED_PORTS[@]}"; do
    if port_in_use $port && [ $port != 80 ] && [ $port != 443 ]; then
        echo -e "${YELLOW}⚠️ Port $port is in use. This might cause conflicts.${NC}"
    fi
done

# 1. Start Ollama server in Docker
echo -e "${YELLOW}🐳 Starting Ollama server...${NC}"

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

# Check if Llama 4 Scout model is available
echo -e "${YELLOW}🔍 Checking for Llama 4 Scout model...${NC}"
if ! docker exec $OLLAMA_CONTAINER_NAME ollama list | grep -q "llama4:scout"; then
    echo -e "${YELLOW}📥 Pulling Llama 4 Scout model (this may take a while)...${NC}"
    docker exec $OLLAMA_CONTAINER_NAME ollama pull llama4:scout
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
            -e OLLAMA_BASE_URL=http://localhost:11434 \
            --add-host=host.docker.internal:host-gateway \
            -v open-webui:/app/backend/data \
            --restart unless-stopped \
            ghcr.io/open-webui/open-webui:main
    fi
fi

# 3. Install Node.js dependencies
echo -e "${YELLOW}📦 Installing Node.js dependencies...${NC}"
if [ ! -d "node_modules" ]; then
    npm install
else
    echo -e "${GREEN}✅ Node.js dependencies already installed.${NC}"
fi

# 4. Configure iptables (if running with sudo)
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}🔒 Configuring iptables...${NC}"
    
    # Allow HTTP and HTTPS
    iptables -A INPUT -p tcp --dport 80 -j ACCEPT
    iptables -A INPUT -p tcp --dport 443 -j ACCEPT
    
    # Allow Node.js service
    iptables -A INPUT -p tcp --dport 3000 -j ACCEPT
    
    # Allow Ollama
    iptables -A INPUT -p tcp --dport 11434 -j ACCEPT
    
    # Allow Open WebUI
    iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
    
    # Save iptables rules
    iptables-save > /etc/iptables/rules.v4 2>/dev/null || true
    
    echo -e "${GREEN}✅ iptables configured.${NC}"
else
    echo -e "${YELLOW}⚠️ Not running as root. Skipping iptables configuration.${NC}"
    echo -e "${YELLOW}💡 Run with sudo to configure iptables automatically.${NC}"
fi

# 5. Generate SSL certificates if they don't exist
echo -e "${YELLOW}🔐 Checking SSL certificates...${NC}"
SSL_DIR="/etc/nginx/ssl"
if [ ! -f "$SSL_DIR/cert.pem" ] || [ ! -f "$SSL_DIR/key.pem" ]; then
    echo -e "${YELLOW}🆕 Generating self-signed SSL certificates...${NC}"
    sudo mkdir -p $SSL_DIR
    sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout $SSL_DIR/key.pem \
        -out $SSL_DIR/cert.pem \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
    echo -e "${GREEN}✅ SSL certificates generated.${NC}"
fi

# 6. Configure and start Nginx
echo -e "${YELLOW}🌐 Configuring Nginx...${NC}"
if [ -f "nginx.conf" ]; then
    sudo cp nginx.conf /etc/nginx/sites-available/qa-chat
    sudo ln -sf /etc/nginx/sites-available/qa-chat /etc/nginx/sites-enabled/
    sudo nginx -t && sudo systemctl restart nginx || sudo service nginx restart
    echo -e "${GREEN}✅ Nginx configured and restarted.${NC}"
else
    echo -e "${RED}❌ nginx.conf not found in current directory.${NC}"
fi

# 7. Start Node.js QA service
echo -e "${YELLOW}🚀 Starting QA Chat Service...${NC}"
npm start &
QA_PID=$!
echo $QA_PID > qa-service.pid

# Wait a moment for the service to start
sleep 3

# Test the service
echo -e "${YELLOW}🧪 Testing QA Chat Service...${NC}"
if curl -s http://localhost:3000/health > /dev/null; then
    echo -e "${GREEN}✅ QA Chat Service is running successfully!${NC}"
else
    echo -e "${RED}❌ QA Chat Service failed to start.${NC}"
fi

echo -e "${GREEN}🎉 QA Chat System startup complete!${NC}"
echo -e "${GREEN}📋 Service Status:${NC}"
echo -e "   🐳 Ollama Server: http://localhost:11434"
echo -e "   🌐 Open WebUI: http://localhost:8080"
echo -e "   💬 QA Chat API: http://localhost:3000"
echo -e "   🔒 Nginx HTTPS: https://localhost"
echo -e ""
echo -e "${YELLOW}💡 Usage Examples:${NC}"
echo -e "   cURL: curl -X GET 'https://localhost/api/ask?question=Hello'"
echo -e "   Open WebUI: Navigate to http://localhost:8080"
echo -e "   Health Check: curl https://localhost/health"
echo -e ""
echo -e "${YELLOW}📝 To stop all services, run: ./shutdown.sh${NC}"
