#!/bin/bash

# Setup script for Deep Learning ETL Pipeline
# This script sets up the virtual environment and installs dependencies

set -e  # Exit on error

echo "========================================="
echo "Deep Learning ETL Pipeline Setup"
echo "========================================="

# Check Python version
PYTHON_CMD="python3"
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Detected Python version: $PYTHON_VERSION"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Skipping creation."
else
    $PYTHON_CMD -m venv venv
    echo "Virtual environment created successfully."
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Create necessary directories
echo ""
echo "Creating project directories..."
mkdir -p src/etl_service
mkdir -p src/inference_service
mkdir -p src/models
mkdir -p src/utils
mkdir -p models
mkdir -p data
mkdir -p tests
mkdir -p notebooks
mkdir -p scripts
mkdir -p docker
mkdir -p kubernetes

# Copy .env.example to .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo ".env file created. Please update with your configuration."
fi

# Display success message
echo ""
echo "========================================="
echo "Setup completed successfully!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Update .env file with your configuration"
echo "3. Start Kafka and Redis: docker-compose -f docker/docker-compose.yml up -d kafka redis"
echo "4. Train the LSTM model: python src/models/train_model.py"
echo "5. Start microservices: docker-compose -f docker/docker-compose.yml up -d"
echo ""
echo "For more information, see README.md"
