#!/bin/bash

# shutdown.sh - Graceful shutdown script for LangChain Weather Agent
# This script safely shuts down the Node.js application and Redis container

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NODE_PROCESS_NAME="node.*src/index.js"
REDIS_CONTAINER_NAME="langchain-redis"
SHUTDOWN_TIMEOUT=10

print_header() {
    echo -e "${BLUE}🛑 LangChain Weather Agent Shutdown${NC}"
    echo "========================================"
}

print_step() {
    echo -e "${YELLOW}⏳ $1...${NC}"
}

print_success() {
    echo -e "${GREEN} $1${NC}"
}

print_warning() {
    echo -e "${YELLOW} $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to gracefully shutdown Node.js processes
shutdown_node_processes() {
    print_step "Shutting down Node.js application"
    
    # Find Node.js processes running our application
    NODE_PIDS=$(pgrep -f "$NODE_PROCESS_NAME" 2>/dev/null || true)
    
    if [ -z "$NODE_PIDS" ]; then
        print_warning "No Node.js processes found running the weather agent"
        return 0
    fi
    
    echo "Found Node.js processes: $NODE_PIDS"
    
    # Send SIGTERM for graceful shutdown
    for PID in $NODE_PIDS; do
        if kill -TERM "$PID" 2>/dev/null; then
            print_step "Sent SIGTERM to process $PID"
        else
            print_warning "Could not send SIGTERM to process $PID"
        fi
    done
    
    # Wait for processes to terminate gracefully
    print_step "Waiting up to ${SHUTDOWN_TIMEOUT}s for graceful shutdown"
    
    for i in $(seq 1 $SHUTDOWN_TIMEOUT); do
        REMAINING_PIDS=$(pgrep -f "$NODE_PROCESS_NAME" 2>/dev/null || true)
        if [ -z "$REMAINING_PIDS" ]; then
            print_success "All Node.js processes shut down gracefully"
            return 0
        fi
        sleep 1
        echo -n "."
    done
    echo ""
    
    # Force kill if still running
    REMAINING_PIDS=$(pgrep -f "$NODE_PROCESS_NAME" 2>/dev/null || true)
    if [ -n "$REMAINING_PIDS" ]; then
        print_warning "Force killing remaining processes: $REMAINING_PIDS"
        for PID in $REMAINING_PIDS; do
            kill -KILL "$PID" 2>/dev/null || true
        done
        print_success "Force killed Node.js processes"
    fi
}

# Function to shutdown Redis container
shutdown_redis_container() {
    print_step "Shutting down Redis container"
    
    # Check if container exists and is running
    if docker ps --format "{{.Names}}" | grep -q "^${REDIS_CONTAINER_NAME}$" 2>/dev/null; then
        print_step "Stopping Redis container: $REDIS_CONTAINER_NAME"
        
        if docker stop "$REDIS_CONTAINER_NAME" >/dev/null 2>&1; then
            print_success "Redis container stopped successfully"
        else
            print_error "Failed to stop Redis container"
            return 1
        fi
    elif docker ps -a --format "{{.Names}}" | grep -q "^${REDIS_CONTAINER_NAME}$" 2>/dev/null; then
        print_warning "Redis container exists but is not running"
    else
        print_warning "Redis container not found"
    fi
}

# Function to check and display final status
check_final_status() {
    print_step "Checking final status"
    
    # Check Node.js processes
    NODE_RUNNING=$(pgrep -f "$NODE_PROCESS_NAME" 2>/dev/null | wc -l)
    if [ "$NODE_RUNNING" -eq 0 ]; then
        print_success "Node.js application: Stopped"
    else
        print_error "Node.js application: Still running ($NODE_RUNNING processes)"
    fi
    
    # Check Redis container
    if docker ps --format "{{.Names}}" | grep -q "^${REDIS_CONTAINER_NAME}$" 2>/dev/null; then
        print_error "Redis container: Still running"
    else
        print_success "Redis container: Stopped"
    fi
    
    # Check port usage
    print_step "Checking port usage"
    PORT_3000=$(netstat -tlnp 2>/dev/null | grep ":3000 " | wc -l)
    PORT_6379=$(netstat -tlnp 2>/dev/null | grep ":6379 " | wc -l)
    
    if [ "$PORT_3000" -eq 0 ]; then
        print_success "Port 3000: Available"
    else
        print_warning "Port 3000: Still in use"
    fi
    
    if [ "$PORT_6379" -eq 0 ]; then
        print_success "Port 6379: Available"
    else
        print_warning "Port 6379: Still in use"
    fi
}

# Function to save Redis data before shutdown (optional)
backup_redis_data() {
    if [ "$1" = "--backup" ]; then
        print_step "Backing up Redis data"
        
        if docker ps --format "{{.Names}}" | grep -q "^${REDIS_CONTAINER_NAME}$" 2>/dev/null; then
            BACKUP_FILE="redis-backup-$(date +%Y%m%d-%H%M%S).rdb"
            if docker exec "$REDIS_CONTAINER_NAME" redis-cli BGSAVE >/dev/null 2>&1; then
                docker cp "$REDIS_CONTAINER_NAME:/data/dump.rdb" "./$BACKUP_FILE" 2>/dev/null || true
                if [ -f "$BACKUP_FILE" ]; then
                    print_success "Redis data backed up to: $BACKUP_FILE"
                else
                    print_warning "Redis backup may have failed"
                fi
            else
                print_warning "Could not create Redis backup"
            fi
        else
            print_warning "Redis container not running, skipping backup"
        fi
    fi
}

# Main shutdown procedure
main() {
    print_header
    echo "Starting graceful shutdown procedure..."
    echo ""
    
    # Parse command line arguments
    BACKUP_DATA=false
    FORCE_CLEANUP=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --backup)
                BACKUP_DATA=true
                shift
                ;;
            --force)
                FORCE_CLEANUP=true
                SHUTDOWN_TIMEOUT=3
                shift
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --backup    Backup Redis data before shutdown"
                echo "  --force     Force quick shutdown (3s timeout)"
                echo "  --help      Show this help message"
                echo ""
                echo "Examples:"
                echo "  $0                # Normal graceful shutdown"
                echo "  $0 --backup      # Shutdown with Redis data backup"
                echo "  $0 --force       # Quick forced shutdown"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Create PID file to track shutdown process
    echo $$ > /tmp/weather-agent-shutdown.pid
    
    # Backup Redis data if requested
    if [ "$BACKUP_DATA" = true ]; then
        backup_redis_data --backup
    fi
    
    # Shutdown sequence
    shutdown_node_processes
    echo ""
    
    shutdown_redis_container
    echo ""
    
    # Wait a moment for everything to settle
    sleep 2
    
    check_final_status
    echo ""
    
    # Final message
    if [ "$NODE_RUNNING" -eq 0 ] && ! docker ps --format "{{.Names}}" | grep -q "^${REDIS_CONTAINER_NAME}$" 2>/dev/null; then
        print_success " LangChain Weather Agent shutdown completed successfully!"
        echo -e "${GREEN}All services stopped, ports are available for restart.${NC}"
    else
        print_warning "⚠️ Some components may still be running. Check the status above."
        echo -e "${YELLOW}You may need to run the cleanup script for a complete reset.${NC}"
    fi
    
    # Remove PID file
    rm -f /tmp/weather-agent-shutdown.pid
}

# Trap signals for cleanup
trap 'print_error "Shutdown interrupted!"; rm -f /tmp/weather-agent-shutdown.pid; exit 1' INT TERM

# Run main function with all arguments
main "$@"
