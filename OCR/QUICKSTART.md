# Quick Start Guide

This guide will help you get started with the OCR project in minutes.

## Prerequisites

Make sure you have completed the [DevOps Setup](README.md#devops-setup) section in the README.

## Quick Installation

```bash
# 1. Navigate to project directory
cd /home/laptop/EXERCISES/MISCELLANEOUS/miscellaneous/OCR

# 2. Activate virtual environment
source .venv/bin/activate

# 3. Verify setup
./verify_setup.sh

# 4. Install base dependencies (if not already installed)
pip install -r requirements.txt
```

## Quick Tests

### Test 1: Simple Image OCR with Tesseract

Create a test image with text:

```bash
# Create a simple test image with text
convert -size 800x200 xc:white -pointsize 40 -fill black \
  -annotate +50+100 "Hello World! This is OCR test." \
  test_image.png

# Run OCR (make sure virtual environment is activated)
python PDF/pdf_ocr_tesseract.py test_image.png output.txt

# View result
cat output.txt
```

### Test 2: FastAPI Service

```bash
# Terminal 1: Start the API server
source .venv/bin/activate
python fastapi_ocr_service.py

# Terminal 2: Test the API
source .venv/bin/activate
python test_api_client.py

# Or use curl
curl http://localhost:8000/health
```

### Test 3: Test with Sample File

If you have a PDF or image file:

```bash
# Activate virtual environment
source .venv/bin/activate

# Test with PDF
python PDF/pdf_ocr_tesseract.py your_file.pdf output.txt

# Test with image
python PDF/pdf_ocr_tesseract.py your_image.jpg output.txt
```

## Install Additional Components

### For PDF Processing with EasyOCR

```bash
source .venv/bin/activate
pip install -r PDF/requirements.txt
```

### For BIM Processing

```bash
source .venv/bin/activate
pip install -r BIM/requirements.txt
```

### For LLM OCR

```bash
# Install Ollama first (if not installed)
curl -fsSL https://ollama.com/install.sh | sh

# Pull vision model
ollama pull llama3.2-vision:11b

# Start Ollama server (in a separate terminal)
ollama serve

# Install Python dependencies
source .venv/bin/activate
pip install -r LLM/requirements.txt
```

## Common Commands

```bash
# Activate virtual environment (always run this first)
source .venv/bin/activate

# Deactivate virtual environment
deactivate

# Update pip packages
pip install --upgrade pip

# List installed packages
pip list

# Verify setup
./verify_setup.sh

# Start FastAPI service
python fastapi_ocr_service.py

# Run tests
python test_api_client.py
```

## File Examples

### Python Script Example

```python
# example_ocr.py
from PDF.pdf_ocr_tesseract import PDFOCRProcessor

# Initialize processor
processor = PDFOCRProcessor(dpi=600)

# Extract text
text = processor.extract_text_from_image("sample.jpg", "output.txt")
print(text)
```

Run it:
```bash
source .venv/bin/activate
python example_ocr.py
```

### API Usage Example

```python
# example_api.py
import requests

# Test image OCR
with open('test_image.png', 'rb') as f:
    files = {'file': f}
    data = {'method': 'tesseract'}
    response = requests.post(
        'http://localhost:8000/api/ocr/image',
        files=files,
        data=data
    )
    print(response.json()['text'])
```

## Troubleshooting Quick Fixes

### Issue: Command not found

```bash
# Make sure virtual environment is activated
source .venv/bin/activate
```

### Issue: Module not found

```bash
# Install missing dependencies
source .venv/bin/activate
pip install -r requirements.txt
```

### Issue: Tesseract not found

```bash
# Install Tesseract
sudo apt install tesseract-ocr

# Verify installation
tesseract --version
```

### Issue: API won't start

```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill process if needed
kill -9 <PID>

# Or use a different port
uvicorn fastapi_ocr_service:app --port 8001
```

## Next Steps

1. ✅ Read the full [README.md](README.md)
2. ✅ Explore the [Use Cases](README.md#use-cases)
3. ✅ Try the [FastAPI Service](README.md#fastapi-service)
4. ✅ Check the API documentation at http://localhost:8000/docs

## Getting Help

- Check error messages carefully
- Verify virtual environment is activated
- Ensure all prerequisites are installed
- Review the main README.md for detailed documentation

---

Happy OCR! 🎉
