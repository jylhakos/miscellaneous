#!/bin/bash

# Quick Start Script for Time-Series Forecasting Microservices
# This script helps you quickly set up and run the system

set -e  # Exit on error

echo "=================================================="
echo "Time-Series Forecasting Microservices Quick Start"
echo "=================================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required commands exist
check_dependencies() {
    print_info "Checking dependencies..."
    
    local missing_deps=()
    
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi
    
    if ! command -v node &> /dev/null; then
        missing_deps+=("node")
    fi
    
    if ! command -v psql &> /dev/null; then
        print_warning "PostgreSQL client (psql) not found. Database setup may fail."
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing required dependencies: ${missing_deps[*]}"
        print_info "Please install missing dependencies and try again."
        exit 1
    fi
    
    print_info "All required dependencies found!"
}

# Create environment file
setup_environment() {
    print_info "Setting up environment configuration..."
    
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            cp .env.example .env
            print_info "Created .env file from template"
            print_warning "Please edit .env file with your configuration"
        else
            print_warning ".env.example not found, skipping environment setup"
        fi
    else
        print_info ".env file already exists"
    fi
}

# Install Python dependencies
install_python_deps() {
    print_info "Installing Python dependencies..."
    
    if [ -f requirements.txt ]; then
        pip3 install -r requirements.txt
        print_info "Python dependencies installed successfully"
    else
        print_error "requirements.txt not found!"
        exit 1
    fi
}

# Install Node.js dependencies
install_node_deps() {
    print_info "Installing Node.js dependencies..."
    
    cd scripts/
    
    if [ -f package.json ]; then
        npm install
        print_info "Node.js dependencies installed successfully"
    else
        print_error "package.json not found!"
        exit 1
    fi
    
    cd ..
}

# Create necessary directories
create_directories() {
    print_info "Creating necessary directories..."
    
    mkdir -p MODEL
    mkdir -p logs
    
    print_info "Directories created"
}

# Initialize database
init_database() {
    print_info "Initializing database..."
    
    if [ -f init-db.sql ]; then
        print_warning "Please ensure PostgreSQL is running and accessible"
        read -p "Database host (default: localhost): " db_host
        db_host=${db_host:-localhost}
        
        read -p "Database name (default: demo): " db_name
        db_name=${db_name:-demo}
        
        read -p "Database user (default: demo): " db_user
        db_user=${db_user:-demo}
        
        print_info "Running database initialization..."
        PGPASSWORD=${DB_PASSWORD:-demo} psql -h "$db_host" -U "$db_user" -d "$db_name" -f init-db.sql
        
        if [ $? -eq 0 ]; then
            print_info "Database initialized successfully"
        else
            print_warning "Database initialization failed. You may need to run it manually."
        fi
    else
        print_warning "init-db.sql not found, skipping database initialization"
    fi
}

# Display startup commands
show_startup_commands() {
    echo ""
    echo "=================================================="
    print_info "Setup completed successfully!"
    echo "=================================================="
    echo ""
    echo "To start the services, run the following commands in separate terminals:"
    echo ""
    echo "Terminal 1 - Data Collector:"
    echo "  cd scripts/"
    echo "  python3 water_data_collector.py"
    echo ""
    echo "Terminal 2 - LSTM Service (Improved):"
    echo "  cd scripts/"
    echo "  python3 water_lstm_service_improved.py 0"
    echo ""
    echo "Terminal 3 - Output Service:"
    echo "  cd scripts/"
    echo "  python3 water_output_service_0.py"
    echo ""
    echo "Terminal 4 - Web Application:"
    echo "  cd scripts/"
    echo "  node water_app.js"
    echo ""
    echo "Then open your browser to: http://localhost:3001/predict"
    echo ""
    echo "=================================================="
    echo "For Docker deployment, run:"
    echo "  docker-compose up -d"
    echo "=================================================="
    echo ""
}

# Start services (optional)
start_services() {
    read -p "Do you want to start services now in background? (y/N): " start_now
    
    if [[ $start_now =~ ^[Yy]$ ]]; then
        print_info "Starting services in background..."
        
        cd scripts/
        
        # Start data collector
        nohup python3 water_data_collector.py > ../logs/data_collector.log 2>&1 &
        echo $! > ../logs/data_collector.pid
        print_info "Data collector started (PID: $(cat ../logs/data_collector.pid))"
        
        # Start LSTM service
        nohup python3 water_lstm_service_improved.py 0 > ../logs/lstm_gpu0.log 2>&1 &
        echo $! > ../logs/lstm_gpu0.pid
        print_info "LSTM service started (PID: $(cat ../logs/lstm_gpu0.pid))"
        
        # Start output service
        nohup python3 water_output_service_0.py > ../logs/output_service0.log 2>&1 &
        echo $! > ../logs/output_service0.pid
        print_info "Output service started (PID: $(cat ../logs/output_service0.pid))"
        
        # Start web app
        nohup node water_app.js > ../logs/webapp.log 2>&1 &
        echo $! > ../logs/webapp.pid
        print_info "Web application started (PID: $(cat ../logs/webapp.pid))"
        
        cd ..
        
        echo ""
        print_info "All services started! Check logs in logs/ directory"
        print_info "Web dashboard: http://localhost:3001/predict"
        echo ""
        echo "To stop services, run: ./scripts/stop_services.sh"
    fi
}

# Main execution
main() {
    check_dependencies
    setup_environment
    
    read -p "Install dependencies? (Y/n): " install_deps
    install_deps=${install_deps:-Y}
    
    if [[ $install_deps =~ ^[Yy]$ ]]; then
        install_python_deps
        install_node_deps
    fi
    
    create_directories
    
    read -p "Initialize database? (y/N): " init_db
    if [[ $init_db =~ ^[Yy]$ ]]; then
        init_database
    fi
    
    show_startup_commands
    start_services
}

# Run main function
main
