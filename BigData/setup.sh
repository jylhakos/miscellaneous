#!/bin/bash
# Quick Setup Script for PySpark Gaming ML Pipeline
# This script automates the setup process including data generation

set -e  # Exit on error

echo "=========================================="
echo "PySpark Gaming ML Pipeline - Quick Setup"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source .venv/bin/activate
echo "✓ Virtual environment activated"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q pyspark matplotlib pandas numpy
echo "✓ Dependencies installed"

# Check if data files exist
echo ""
if [ -f "testData.data" ]; then
    echo "✓ testData.data already exists ($(wc -l < testData.data) rows)"
    read -p "Do you want to regenerate it? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Generating new testData.data..."
        python generate_sample_data.py --rows 4000 --output testData.data
    fi
else
    echo "Generating testData.data (4000 rows)..."
    python generate_sample_data.py --rows 4000 --output testData.data
fi

# Verify Java installation
echo ""
echo "Checking Java installation..."
if command -v java &> /dev/null; then
    JAVA_VERSION=$(java -version 2>&1 | head -n 1)
    echo "✓ Java found: $JAVA_VERSION"
    
    # Check for Java 17
    if [ -d "/usr/lib/jvm/java-17-openjdk-amd64" ]; then
        export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
        echo "✓ Using Java 17: $JAVA_HOME"
    fi
else
    echo "⚠ Java not found. Please install Java 17:"
    echo "   sudo apt install openjdk-17-jdk"
fi

# Summary
echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Activate virtual environment:"
echo "     source .venv/bin/activate"
echo ""
echo "  2. Run the pipeline:"
echo "     python machine_learning_pipeline.py"
echo ""
echo "  3. Or start Jupyter Notebook:"
echo "     pip install jupyter"
echo "     jupyter notebook GamingProcessor.ipynb"
echo ""
echo "=========================================="
