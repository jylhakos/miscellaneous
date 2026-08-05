#!/bin/bash

# Stop Services Script
# Stops all background services started by quickstart.sh

set -e

echo "Stopping Time-Series Forecasting Microservices..."

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to stop a service
stop_service() {
    local service_name=$1
    local pid_file="logs/${service_name}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            kill $pid
            print_info "Stopped $service_name (PID: $pid)"
            rm "$pid_file"
        else
            print_warning "$service_name (PID: $pid) not running"
            rm "$pid_file"
        fi
    else
        print_warning "No PID file found for $service_name"
    fi
}

# Stop all services
stop_service "data_collector"
stop_service "lstm_gpu0"
stop_service "output_service0"
stop_service "webapp"

echo ""
print_info "All services stopped"
