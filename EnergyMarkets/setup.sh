#!/bin/bash
# ==============================================================================
# Power Trading Platform Setup Script
# ==============================================================================
# Automated environment setup for Python virtual environment and dependencies
# ==============================================================================

set -e  # Exit on error

echo "======================================================================"
echo "Power Trading Platform - Environment Setup"
echo "======================================================================"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Detected Python version: $PYTHON_VERSION"

# Check if virtual environment already exists
if [ -d "venv" ]; then
    echo "⚠ Virtual environment already exists at ./venv"
    read -p "Do you want to recreate it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing existing virtual environment..."
        rm -rf venv
    else
        echo "Using existing virtual environment"
        source venv/bin/activate
        echo "✓ Virtual environment activated"
        exit 0
    fi
fi

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ Created .env file"
    echo "⚠ IMPORTANT: Edit .env file and add your API keys:"
    echo "   - ENTSOE_API_KEY"
    echo "   - NORDPOOL_API_KEY"
else
    echo "✓ .env file already exists"
fi

# Create necessary directories
mkdir -p data
mkdir -p logs
echo "✓ Created data and logs directories"

echo ""
echo "======================================================================"
echo "✓ Setup completed successfully!"
echo "======================================================================"
echo ""
echo "Next steps:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Edit .env file with your API keys"
echo "  3. Run standalone scripts:"
echo "     python scripts/entsoe_client.py --zone FI --start 2026-01-01 --end 2026-01-31"
echo "     python scripts/nordpool_client.py --areas SE3,FI --date 2026-07-21"
echo "  4. Or start the FastAPI server:"
echo "     python scripts/main.py"
echo "  5. Or use Docker Compose:"
echo "     docker-compose up -d"
echo ""
