#!/bin/bash

# cleanup.sh - Complete cleanup script for LangChain Weather Agent
# This script performs a complete cleanup of all resources, containers, and data

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
NODE_PROCESS_NAME="node.*src/index.js"
REDIS_CONTAINER_NAME="langchain-redis"
REDIS_VOLUME_NAME="redis-data"

print_header() {
    echo -e "${BLUE}🧹 LangChain Weather Agent Complete Cleanup${NC}"
    echo "=============================================="
}

print_step() {
    echo -e "${CYAN}🔧 $1...${NC}"
}

print_success() {
    echo -e "${GREEN} $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE} $1${NC}"
}

# Function to kill all Node.js processes
cleanup_node_processes() {
    print_step "Cleaning up Node.js processes"
    
    NODE_PIDS=$(pgrep -f "$NODE_PROCESS_NAME" 2>/dev/null || true)
    
    if [ -z "$NODE_PIDS" ]; then
        print_success "No Node.js processes found"
        return 0
    fi
    
    print_info "Found Node.js processes: $NODE_PIDS"
    
    # Kill all processes
    for PID in $NODE_PIDS; do
        if kill -KILL "$PID" 2>/dev/null; then
            print_success "Killed process $PID"
        else
            print_warning "Could not kill process $PID (may already be dead)"
        fi
    done
    
    # Verify cleanup
    sleep 1
    REMAINING_PIDS=$(pgrep -f "$NODE_PROCESS_NAME" 2>/dev/null || true)
    if [ -z "$REMAINING_PIDS" ]; then
        print_success "All Node.js processes cleaned up"
    else
        print_error "Some Node.js processes still running: $REMAINING_PIDS"
    fi
}

# Function to cleanup Redis container and data
cleanup_redis_container() {
    print_step "Cleaning up Redis container"
    
    # Stop container if running
    if docker ps --format "{{.Names}}" | grep -q "^${REDIS_CONTAINER_NAME}$" 2>/dev/null; then
        print_step "Stopping Redis container"
        docker stop "$REDIS_CONTAINER_NAME" >/dev/null 2>&1 || true
        print_success "Redis container stopped"
    fi
    
    # Remove container if exists
    if docker ps -a --format "{{.Names}}" | grep -q "^${REDIS_CONTAINER_NAME}$" 2>/dev/null; then
        print_step "Removing Redis container"
        docker rm "$REDIS_CONTAINER_NAME" >/dev/null 2>&1 || true
        print_success "Redis container removed"
    else
        print_success "No Redis container found to remove"
    fi
}

# Function to cleanup Redis data volume
cleanup_redis_volume() {
    print_step "Cleaning up Redis data volume"
    
    if docker volume ls --format "{{.Name}}" | grep -q "^${REDIS_VOLUME_NAME}$" 2>/dev/null; then
        print_warning "Redis data volume found: $REDIS_VOLUME_NAME"
        
        if [ "$PRESERVE_DATA" = true ]; then
            print_info "Preserving Redis data volume (--preserve-data flag used)"
        else
            echo -e "${YELLOW}⚠️ This will permanently delete all Redis data!${NC}"
            if [ "$FORCE_CLEANUP" = true ]; then
                docker volume rm "$REDIS_VOLUME_NAME" >/dev/null 2>&1 || true
                print_success "Redis data volume removed"
            else
                read -p "Do you want to delete Redis data? (y/N): " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    docker volume rm "$REDIS_VOLUME_NAME" >/dev/null 2>&1 || true
                    print_success "Redis data volume removed"
                else
                    print_info "Redis data volume preserved"
                fi
            fi
        fi
    else
        print_success "No Redis data volume found to remove"
    fi
}

# Function to cleanup temporary files
cleanup_temp_files() {
    print_step "Cleaning up temporary files"
    
    # Remove PID files
    rm -f /tmp/weather-agent-shutdown.pid
    rm -f /tmp/weather-agent.pid
    
    # Remove log files (if any)
    rm -f weather-agent.log
    rm -f redis.log
    
    # Remove backup files older than 7 days
    find . -name "redis-backup-*.rdb" -mtime +7 -delete 2>/dev/null || true
    
    print_success "Temporary files cleaned up"
}

# Function to cleanup network resources
cleanup_network() {
    print_step "Cleaning up network resources"
    
    # Find and kill processes using our ports
    PIDS_3000=$(lsof -ti:3000 2>/dev/null || true)
    PIDS_6379=$(lsof -ti:6379 2>/dev/null || true)
    
    if [ -n "$PIDS_3000" ]; then
        print_info "Killing processes using port 3000: $PIDS_3000"
        kill -KILL $PIDS_3000 2>/dev/null || true
    fi
    
    if [ -n "$PIDS_6379" ]; then
        print_info "Killing processes using port 6379: $PIDS_6379"
        kill -KILL $PIDS_6379 2>/dev/null || true
    fi
    
    print_success "Network resources cleaned up"
}

# Function to cleanup Docker resources
cleanup_docker_resources() {
    print_step "Cleaning up related Docker resources"
    
    # Remove any orphaned containers related to our project
    ORPHANED=$(docker ps -a -q --filter "name=*redis*" --filter "name=*langchain*" 2>/dev/null | grep -v "$REDIS_CONTAINER_NAME" || true)
    
    if [ -n "$ORPHANED" ]; then
        print_info "Found orphaned containers: $ORPHANED"
        docker rm $ORPHANED >/dev/null 2>&1 || true
        print_success "Orphaned containers removed"
    fi
    
    # Cleanup unused networks (optional)
    if [ "$DEEP_CLEAN" = true ]; then
        print_step "Performing deep Docker cleanup"
        docker network prune -f >/dev/null 2>&1 || true
        docker system prune -f >/dev/null 2>&1 || true
        print_success "Deep Docker cleanup completed"
    fi
    
    print_success "Docker resources cleaned up"
}

# Function to verify complete cleanup
verify_cleanup() {
    print_step "Verifying cleanup completion"
    
    # Check Node.js processes
    NODE_COUNT=$(pgrep -f "$NODE_PROCESS_NAME" 2>/dev/null | wc -l)
    if [ "$NODE_COUNT" -eq 0 ]; then
        print_success "Node.js processes: Clean"
    else
        print_error "Node.js processes: $NODE_COUNT still running"
    fi
    
    # Check Redis container
    if docker ps -a --format "{{.Names}}" | grep -q "^${REDIS_CONTAINER_NAME}$" 2>/dev/null; then
        print_error "Redis container: Still exists"
    else
        print_success "Redis container: Clean"
    fi
    
    # Check ports
    PORT_3000_USAGE=$(netstat -tlnp 2>/dev/null | grep ":3000 " | wc -l)
    PORT_6379_USAGE=$(netstat -tlnp 2>/dev/null | grep ":6379 " | wc -l)
    
    if [ "$PORT_3000_USAGE" -eq 0 ]; then
        print_success "Port 3000: Available"
    else
        print_warning "Port 3000: In use"
    fi
    
    if [ "$PORT_6379_USAGE" -eq 0 ]; then
        print_success "Port 6379: Available"
    else
        print_warning "Port 6379: In use"
    fi
    
    # Check disk space freed
    print_info "System resources after cleanup:"
    df -h . | tail -1 | awk '{print "  Disk space available: " $4 " (" $5 " used)"}'
}

# Function to show cleanup summary
show_cleanup_summary() {
    echo ""
    print_header
    echo -e "${GREEN} Cleanup Summary${NC}"
    echo "=================="
    echo ""
    echo "Cleaned up:"
    echo "  Node.js application processes"
    echo "  Redis Docker container"
    if [ "$PRESERVE_DATA" != true ]; then
        echo "  Redis data volume"
    else
        echo "  Redis data volume (preserved)"
    fi
    echo "  Temporary files and PID files"
    echo "  Network port allocations"
    echo "  Docker resources"
    echo ""
    echo -e "${CYAN}System is now clean and ready for fresh start!${NC}"
    echo ""
    echo "To restart the system:"
    echo "  ./redis-manager.sh start"
    echo "  npm start"
    echo ""
}

# Main cleanup procedure
main() {
    print_header
    echo "Starting complete cleanup procedure..."
    echo ""
    
    # Parse command line arguments
    PRESERVE_DATA=false
    FORCE_CLEANUP=false
    DEEP_CLEAN=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --preserve-data)
                PRESERVE_DATA=true
                shift
                ;;
            --force)
                FORCE_CLEANUP=true
                shift
                ;;
            --deep-clean)
                DEEP_CLEAN=true
                shift
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --preserve-data    Keep Redis data volume"
                echo "  --force           Force cleanup without prompts"
                echo "  --deep-clean      Include Docker system cleanup"
                echo "  --help            Show this help message"
                echo ""
                echo "Examples:"
                echo "  $0                    # Interactive cleanup"
                echo "  $0 --preserve-data    # Cleanup but keep data"
                echo "  $0 --force            # Force cleanup everything"
                echo "  $0 --deep-clean       # Cleanup + Docker system prune"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Warning for destructive operation
    if [ "$FORCE_CLEANUP" != true ] && [ "$PRESERVE_DATA" != true ]; then
        echo -e "${RED}⚠️ WARNING: This will delete ALL data and stop ALL services!${NC}"
        read -p "Are you sure you want to continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Cleanup cancelled by user"
            exit 0
        fi
    fi
    
    # Cleanup sequence
    cleanup_node_processes
    cleanup_redis_container
    cleanup_redis_volume
    cleanup_temp_files
    cleanup_network
    cleanup_docker_resources
    
    echo ""
    verify_cleanup
    
    echo ""
    show_cleanup_summary
}

# Trap signals for cleanup
trap 'print_error "Cleanup interrupted!"; exit 1' INT TERM

# Run main function with all arguments
main "$@"
