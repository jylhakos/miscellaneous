#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 QA Chat System Setup Verification${NC}"
echo ""

# Check dependencies
echo -e "${YELLOW}📋 Checking Dependencies...${NC}"

dependencies=(
    "docker:Docker"
    "node:Node.js"
    "npm:npm"
    "nginx:Nginx"
    "curl:cURL"
    "openssl:OpenSSL"
)

all_deps_ok=true
for dep in "${dependencies[@]}"; do
    cmd=${dep%%:*}
    name=${dep##*:}
    
    if command -v $cmd >/dev/null 2>&1; then
        version=$(
            case $cmd in
                docker) docker --version | cut -d' ' -f3 | tr -d ',' ;;
                node) node --version ;;
                npm) npm --version ;;
                nginx) nginx -v 2>&1 | cut -d'/' -f2 ;;
                curl) curl --version | head -1 | cut -d' ' -f2 ;;
                openssl) openssl version | cut -d' ' -f2 ;;
            esac
        )
        echo -e "  ${GREEN}✅ $name: $version${NC}"
    else
        echo -e "  ${RED}❌ $name: Not installed${NC}"
        all_deps_ok=false
    fi
done

if [ "$all_deps_ok" = false ]; then
    echo -e "${RED}❌ Some dependencies are missing. Please install them before proceeding.${NC}"
    exit 1
fi

echo ""

# Check project files
echo -e "${YELLOW}📁 Checking Project Files...${NC}"

required_files=(
    "package.json:Package configuration"
    "src/index.js:Express server"
    "src/qa.js:QA logic"
    ".env:Environment configuration"
    "nginx.conf:Nginx configuration"
    "startup.sh:Startup script"
    "shutdown.sh:Shutdown script"
    "docker-compose.yml:Docker Compose"
)

all_files_ok=true
for file_desc in "${required_files[@]}"; do
    file=${file_desc%%:*}
    desc=${file_desc##*:}
    
    if [ -f "$file" ]; then
        echo -e "  ${GREEN}✅ $desc: $file${NC}"
    else
        echo -e "  ${RED}❌ $desc: $file (missing)${NC}"
        all_files_ok=false
    fi
done

if [ "$all_files_ok" = false ]; then
    echo -e "${RED}❌ Some required files are missing. Please ensure all files are present.${NC}"
    exit 1
fi

echo ""

# Check Node.js dependencies
echo -e "${YELLOW}📦 Checking Node.js Dependencies...${NC}"

if [ -d "node_modules" ]; then
    echo -e "  ${GREEN}✅ Node modules installed${NC}"
    
    # Check key packages
    key_packages=(
        "@langchain/ollama"
        "@langchain/core"
        "express"
        "cors"
        "dotenv"
        "uuid"
        "langchain"
    )
    
    for package in "${key_packages[@]}"; do
        if [ -d "node_modules/$package" ]; then
            echo -e "    ${GREEN}✅ $package${NC}"
        else
            echo -e "    ${RED}❌ $package (not installed)${NC}"
        fi
    done
else
    echo -e "  ${YELLOW}⚠️ Node modules not installed. Run 'npm install' to install dependencies.${NC}"
fi

echo ""

# Check environment configuration
echo -e "${YELLOW}⚙️ Checking Environment Configuration...${NC}"

if [ -f ".env" ]; then
    echo -e "  ${GREEN}✅ .env file exists${NC}"
    
    # Check key environment variables
    env_vars=(
        "OLLAMA_BASE_URL"
        "OLLAMA_MODEL"
        "PORT"
        "NODE_ENV"
    )
    
    for var in "${env_vars[@]}"; do
        if grep -q "^$var=" .env; then
            value=$(grep "^$var=" .env | cut -d'=' -f2)
            echo -e "    ${GREEN}✅ $var=$value${NC}"
        else
            echo -e "    ${YELLOW}⚠️ $var (not set)${NC}"
        fi
    done
else
    echo -e "  ${RED}❌ .env file missing. Copy from .env.example and configure.${NC}"
fi

echo ""

# Check ports availability
echo -e "${YELLOW}🔌 Checking Port Availability...${NC}"

ports=(
    "3000:Node.js QA Service"
    "8080:Open WebUI"
    "11434:Ollama Server"
    "80:HTTP (Nginx)"
    "443:HTTPS (Nginx)"
)

for port_desc in "${ports[@]}"; do
    port=${port_desc%%:*}
    desc=${port_desc##*:}
    
    if netstat -tlnp 2>/dev/null | grep ":$port " >/dev/null; then
        process=$(netstat -tlnp 2>/dev/null | grep ":$port " | awk '{print $7}' | head -1)
        echo -e "  ${YELLOW}⚠️ Port $port ($desc): In use by $process${NC}"
    else
        echo -e "  ${GREEN}✅ Port $port ($desc): Available${NC}"
    fi
done

echo ""

# Check Docker
echo -e "${YELLOW}🐳 Checking Docker...${NC}"

if systemctl is-active --quiet docker 2>/dev/null || service docker status >/dev/null 2>&1; then
    echo -e "  ${GREEN}✅ Docker service is running${NC}"
    
    # Check for existing containers
    if docker ps -a --format "table {{.Names}}\t{{.Status}}" | grep -E "(ollama-server|open-webui)" >/dev/null; then
        echo -e "  ${GREEN}ℹ️ Existing containers found:${NC}"
        docker ps -a --format "table {{.Names}}\t{{.Status}}" | grep -E "(ollama-server|open-webui)" | while read line; do
            echo -e "    $line"
        done
    else
        echo -e "  ${YELLOW}ℹ️ No QA-related containers found${NC}"
    fi
else
    echo -e "  ${RED}❌ Docker service is not running${NC}"
fi

echo ""

# Summary
echo -e "${BLUE}📊 Setup Verification Summary${NC}"

if [ "$all_deps_ok" = true ] && [ "$all_files_ok" = true ]; then
    echo -e "${GREEN}🎉 Your QA Chat System is ready to run!${NC}"
    echo ""
    echo -e "${YELLOW}🚀 Quick Start Commands:${NC}"
    echo -e "  ${BLUE}Full System:${NC} ./startup.sh"
    echo -e "  ${BLUE}Docker Only:${NC} ./start-docker.sh"
    echo -e "  ${BLUE}Node.js Only:${NC} ./start-nodejs.sh"
    echo -e "  ${BLUE}Test System:${NC} ./test-system.sh"
    echo -e "  ${BLUE}See Examples:${NC} ./examples.sh"
    echo ""
    echo -e "${YELLOW}📚 Documentation: See README.md for detailed setup instructions${NC}"
else
    echo -e "${RED}❌ Setup verification failed. Please resolve the issues above.${NC}"
    exit 1
fi
