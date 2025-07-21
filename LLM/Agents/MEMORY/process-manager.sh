#!/bin/bash

# process-manager.sh - Complete process management for LangChain Weather Agent
# Usage: ./process-manager.sh [start|stop|restart|status|monitor]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="LangChain Weather Agent"
NODE_SCRIPT="src/index.js"
PID_FILE="/tmp/weather-agent.pid"
LOG_FILE="weather-agent.log"
REDIS_CONTAINER="langchain-redis"

print_header() {
    echo -e "${BLUE} $APP_NAME Process Manager${NC}"
    echo "========================================"
}

print_success() {
    echo -e "${GREEN} $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_info() {
    echo -e "${CYAN} $1${NC}"
}

# Function to start the entire system
start_system() {
    print_header
    echo " Starting $APP_NAME..."
    echo ""
    
    # Check if already running
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        print_warning "Application is already running (PID: $(cat $PID_FILE))"
        return 1
    fi
    
    # Start Redis if not running
    echo "1. Starting Redis..."
    if ! docker ps --format "{{.Names}}" | grep -q "^${REDIS_CONTAINER}$"; then
        ./redis-manager.sh start
    else
        print_success "Redis is already running"
    fi
    
    echo ""
    echo "2. Starting Node.js application..."
    
    # Start Node.js application in background
    nohup node "$NODE_SCRIPT" > "$LOG_FILE" 2>&1 &
    APP_PID=$!
    
    # Save PID
    echo "$APP_PID" > "$PID_FILE"
    
    # Wait and verify startup
    sleep 3
    
    if kill -0 "$APP_PID" 2>/dev/null; then
        print_success "Application started successfully (PID: $APP_PID)"
        print_info "Logs: tail -f $LOG_FILE"
        print_info "API: http://localhost:3000"
        
        # Test API endpoint
        if curl -s http://localhost:3000/health > /dev/null 2>&1; then
            print_success "API is responding"
        else
            print_warning "API may still be starting up"
        fi
    else
        print_error "Failed to start application"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Function to stop the entire system
stop_system() {
    print_header
    echo "🛑 Stopping $APP_NAME..."
    echo ""
    
    # Stop Node.js application
    if [ -f "$PID_FILE" ]; then
        APP_PID=$(cat "$PID_FILE")
        if kill -0 "$APP_PID" 2>/dev/null; then
            echo "Stopping Node.js application (PID: $APP_PID)..."
            
            # Graceful shutdown
            kill -TERM "$APP_PID" 2>/dev/null || true
            
            # Wait for graceful shutdown
            for i in {1..10}; do
                if ! kill -0 "$APP_PID" 2>/dev/null; then
                    break
                fi
                sleep 1
            done
            
            # Force kill if still running
            if kill -0 "$APP_PID" 2>/dev/null; then
                print_warning "Forcing application shutdown..."
                kill -KILL "$APP_PID" 2>/dev/null || true
            fi
            
            rm -f "$PID_FILE"
            print_success "Node.js application stopped"
        else
            print_warning "Application was not running"
            rm -f "$PID_FILE"
        fi
    else
        print_warning "No PID file found"
    fi
    
    # Optionally stop Redis
    echo ""
    read -p "Stop Redis container as well? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ./redis-manager.sh stop
    else
        print_info "Redis container left running"
    fi
}

# Function to restart the system
restart_system() {
    print_header
    echo " Restarting $APP_NAME..."
    echo ""
    
    stop_system
    sleep 2
    start_system
}

# Function to show system status
show_status() {
    print_header
    echo " System Status"
    echo ""
    
    # Node.js application status
    echo "Node.js Application:"
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        APP_PID=$(cat "$PID_FILE")
        print_success "Running (PID: $APP_PID)"
        
        # Show memory and CPU usage
        if command -v ps >/dev/null 2>&1; then
            MEM_CPU=$(ps -p "$APP_PID" -o pid,pcpu,pmem,etime --no-headers 2>/dev/null || echo "N/A")
            echo "  Process info: $MEM_CPU"
        fi
        
        # Test API
        if curl -s http://localhost:3000/health > /dev/null 2>&1; then
            print_success "API responding on port 3000"
        else
            print_warning "API not responding"
        fi
    else
        print_error "Not running"
        if [ -f "$PID_FILE" ]; then
            rm -f "$PID_FILE"
        fi
    fi
    
    echo ""
    echo "Redis Container:"
    if docker ps --format "{{.Names}}\t{{.Status}}" | grep -q "^${REDIS_CONTAINER}"; then
        STATUS=$(docker ps --format "{{.Names}}\t{{.Status}}" | grep "^${REDIS_CONTAINER}" | cut -f2)
        print_success "Running - $STATUS"
        
        # Test Redis connection
        if docker exec "$REDIS_CONTAINER" redis-cli ping 2>/dev/null | grep -q "PONG"; then
            print_success "Redis responding on port 6379"
        else
            print_warning "Redis not responding to ping"
        fi
    else
        print_error "Not running"
    fi
    
    echo ""
    echo "System Resources:"
    echo "  Memory usage: $(free -h | awk '/^Mem:/ {print $3 "/" $2}')"
    echo "  Disk usage: $(df -h . | tail -1 | awk '{print $5 " used"}')"
    
    # Show port usage
    echo ""
    echo "Port Usage:"
    PORT_3000=$(netstat -tlnp 2>/dev/null | grep ":3000 " | awk '{print $7}' | head -1)
    PORT_6379=$(netstat -tlnp 2>/dev/null | grep ":6379 " | awk '{print $7}' | head -1)
    
    if [ -n "$PORT_3000" ]; then
        echo "  Port 3000: $PORT_3000"
    else
        echo "  Port 3000: Available"
    fi
    
    if [ -n "$PORT_6379" ]; then
        echo "  Port 6379: $PORT_6379"
    else
        echo "  Port 6379: Available"
    fi
}

# Function to monitor the system
monitor_system() {
    print_header
    echo " Monitoring $APP_NAME (Press Ctrl+C to exit)"
    echo ""
    
    # Initial status
    show_status
    
    echo ""
    echo "Live monitoring..."
    echo "=================="
    
    while true; do
        sleep 5
        
        # Clear screen
        clear
        echo -e "${BLUE} Live Monitor - $APP_NAME${NC}"
        echo "Time: $(date)"
        echo "========================================"
        
        # Quick status check
        if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
            APP_PID=$(cat "$PID_FILE")
            echo -e "${GREEN} Node.js: Running (PID: $APP_PID)${NC}"
            
            # Show resource usage
            if command -v ps >/dev/null 2>&1; then
                CPU_MEM=$(ps -p "$APP_PID" -o pcpu,pmem --no-headers 2>/dev/null || echo "N/A N/A")
                echo "   CPU: $(echo $CPU_MEM | cut -d' ' -f1)% | Memory: $(echo $CPU_MEM | cut -d' ' -f2)%"
            fi
        else
            echo -e "${RED}❌ Node.js: Not running${NC}"
        fi
        
        if docker ps --format "{{.Names}}" | grep -q "^${REDIS_CONTAINER}$"; then
            echo -e "${GREEN} Redis: Running${NC}"
        else
            echo -e "${RED}❌ Redis: Not running${NC}"
        fi
        
        # API test
        if curl -s http://localhost:3000/health > /dev/null 2>&1; then
            echo -e "${GREEN} API: Responding${NC}"
        else
            echo -e "${RED}❌ API: Not responding${NC}"
        fi
        
        # Show recent log entries
        if [ -f "$LOG_FILE" ]; then
            echo ""
            echo "Recent logs (last 5 lines):"
            tail -5 "$LOG_FILE" | sed 's/^/  /'
        fi
        
        echo ""
        echo "Press Ctrl+C to exit monitoring..."
    done
}

# Function to show logs
show_logs() {
    print_header
    echo " Application Logs"
    echo ""
    
    if [ -f "$LOG_FILE" ]; then
        echo "Following $LOG_FILE (Press Ctrl+C to exit):"
        echo "============================================="
        tail -f "$LOG_FILE"
    else
        print_warning "No log file found: $LOG_FILE"
        echo "Start the application first with: $0 start"
    fi
}

# Help function
show_help() {
    print_header
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  start     Start the complete system (Redis + Node.js)"
    echo "  stop      Stop the complete system"
    echo "  restart   Restart the complete system"
    echo "  status    Show system status"
    echo "  monitor   Live monitoring (refreshes every 5s)"
    echo "  logs      Show and follow application logs"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start                # Start everything"
    echo "  $0 status               # Check if running"
    echo "  $0 monitor              # Live monitoring"
    echo "  $0 restart              # Restart all services"
    echo ""
    echo "Files:"
    echo "  PID file: $PID_FILE"
    echo "  Log file: $LOG_FILE"
    echo ""
}

# Main function
main() {
    case "${1:-help}" in
        start)
            start_system
            ;;
        stop)
            stop_system
            ;;
        restart)
            restart_system
            ;;
        status)
            show_status
            ;;
        monitor)
            monitor_system
            ;;
        logs)
            show_logs
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Trap SIGINT for monitor mode
trap 'echo -e "\n${YELLOW}Monitoring stopped${NC}"; exit 0' INT

# Run main function
main "$@"
