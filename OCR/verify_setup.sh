#!/bin/bash
# Test script to verify OCR setup

echo "======================================================"
echo "OCR Setup Verification Script"
echo "======================================================"
echo ""

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✓ Virtual environment is activated: $VIRTUAL_ENV"
else
    echo "✗ Virtual environment is NOT activated"
    echo "  Please run: source .venv/bin/activate"
    exit 1
fi

echo ""
echo "Checking system dependencies..."
echo "------------------------------------------------------"

# Check Tesseract
if command -v tesseract &> /dev/null; then
    VERSION=$(tesseract --version | head -n1)
    echo "✓ Tesseract OCR: $VERSION"
else
    echo "✗ Tesseract OCR not found"
    echo "  Install with: sudo apt install tesseract-ocr"
fi

# Check Poppler
if command -v pdftoppm &> /dev/null; then
    VERSION=$(pdftoppm -v 2>&1 | head -n1)
    echo "✓ Poppler utils: $VERSION"
else
    echo "✗ Poppler utils not found"
    echo "  Install with: sudo apt install poppler-utils"
fi

# Check Ollama
if command -v ollama &> /dev/null; then
    VERSION=$(ollama --version)
    echo "✓ Ollama: $VERSION"
    
    # Check if Ollama server is running
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "  ✓ Ollama server is running"
        
        # Check for vision model
        if ollama list | grep -q "llama3.2-vision"; then
            echo "  ✓ Llama 3.2 Vision model is installed"
        else
            echo "  ✗ Llama 3.2 Vision model not found"
            echo "    Install with: ollama pull llama3.2-vision:11b"
        fi
    else
        echo "  ✗ Ollama server is not running"
        echo "    Start with: ollama serve"
    fi
else
    echo "✗ Ollama not found"
    echo "  Install from: https://ollama.com/download"
fi

echo ""
echo "Checking Python packages..."
echo "------------------------------------------------------"

# Function to check Python package
check_package() {
    if python -c "import $1" &> /dev/null; then
        VERSION=$(python -c "import $1; print($1.__version__)" 2>/dev/null || echo "installed")
        echo "✓ $1: $VERSION"
        return 0
    else
        echo "✗ $1 not found"
        return 1
    fi
}

# Check essential packages
check_package "PIL"
check_package "pytesseract"
check_package "cv2"
check_package "numpy"
check_package "fastapi"
check_package "uvicorn"

echo ""
echo "Checking optional packages..."
echo "------------------------------------------------------"

check_package "easyocr"
check_package "torch"
check_package "transformers"
check_package "fitz"  # PyMuPDF

echo ""
echo "======================================================"
echo "Verification Complete"
echo "======================================================"
echo ""
echo "Next steps:"
echo "  1. If any system dependencies are missing, install them"
echo "  2. If Python packages are missing, install with:"
echo "     pip install -r requirements.txt"
echo "  3. For specific use cases, install from subdirectories:"
echo "     - PDF: pip install -r PDF/requirements.txt"
echo "     - BIM: pip install -r BIM/requirements.txt"
echo "     - LLM: pip install -r LLM/requirements.txt"
echo ""
