# Optical Character Recognition (OCR)

An OCR system leveraging Machine Learning, Deep Learning, and Large Language Models for text extraction from PDF files, BIM images, and general documents.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [How LLM Models Work for OCR](#how-llm-models-work-for-ocr)
- [Prerequisites](#prerequisites)
- [DevOps Setup](#devops-setup)
- [Use Cases](#use-cases)
  - [PDF OCR](#1-pdf-ocr)
  - [BIM OCR](#2-bim-ocr)
  - [LLM OCR](#3-llm-ocr)
- [FastAPI Service](#fastapi-service)
- [Web Frontend UI](#web-frontend-ui)
- [Datasets](#datasets)
- [References](#references)

## Documentation

This README contains the complete project documentation.

- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes with installation and basic usage
- **[API.md](API.md)** - Detailed REST API reference with examples
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture and request flow diagrams

## Overview

**Optical Character Recognition (OCR)** is a technology that converts different types of documents (scanned paper documents, PDF files, or images) into editable and searchable data. This project implements OCR using multiple approaches:

1. **Traditional OCR** - Using Tesseract and EasyOCR
2. **Deep Learning OCR** - Using CNNs and transformers
3. **LLM-based OCR** - Using vision-enabled language models

### How OCR Works

The OCR process involves several stages:

1. **Image Acquisition**: Capture or load the document image
2. **Preprocessing**: Enhance image quality (de-skewing, noise reduction, binarization)
3. **Text Detection**: Identify regions containing text
4. **Character Recognition**: Convert detected patterns into characters
5. **Post-processing**: Apply spell-checking and grammar rules
6. **Output**: Generate machine-readable text

### Machine Learning in OCR

Modern OCR systems use machine learning (ML) to:

- **Pattern Recognition**: Train models on vast datasets to recognize character patterns
- **Context Understanding**: Use language models to improve accuracy
- **Layout Analysis**: Understand document structure and formatting
- **Multi-language Support**: Recognize text in multiple languages

### Deep Learning OCR

Deep learning (DL) enhances OCR through:

- **CNNs (Convolutional Neural Networks)**: Extract visual features from images
- **RNNs (Recurrent Neural Networks)**: Understand sequential text patterns
- **Transformers**: Provide context-aware text understanding
- **Vision Models**: Combine visual and textual information

## Features

- **Multiple OCR Engines**: Tesseract, EasyOCR, LLM-based
- **PDF Processing**: Extract text from both scanned and native PDFs
- **BIM Support**: Extract structured data from blueprints and floor plans
- **LLM Integration**: Advanced text extraction with Ollama
- **REST API**: FastAPI service with OpenAI-compatible endpoints
- **Multi-format Support**: PDF, JPG, PNG, BMP, TIFF
- **Batch Processing**: Process multiple documents
- **Structured Output**: JSON, TXT, with metadata

## Project Structure

```
OCR/
├── README.md                      # Complete project documentation
├── QUICKSTART.md                  # Quick start guide
├── PROJECT_SUMMARY.md             # Project summary and status
├── .gitignore                     # Git ignore configuration
├── requirements.txt               # Main dependencies (FastAPI service)
├── demo.py                        # Interactive demonstration
├── verify_setup.sh                # Setup verification script
├── test_api_client.py            # API client examples
├── fastapi_ocr_service.py        # REST API service
├── serve_frontend.py             # Frontend server script
├── .venv/                         # Python virtual environment (excluded from git)
│
├── frontend/                      # Web Frontend UI
│   ├── index.html                 # Single-page web application
│   └── requirements.txt           # Frontend dependencies (none needed)
│
├── PDF/                           # PDF OCR implementations
│   ├── requirements.txt           # PDF-specific dependencies
│   ├── pdf_ocr_tesseract.py      # Tesseract + pdf2image approach
│   └── pdf_ocr_easyocr.py        # PyMuPDF + EasyOCR approach
│
├── BIM/                           # BIM (Building Information Modeling) OCR
│   ├── requirements.txt           # BIM-specific dependencies
│   └── bim_ocr_processor.py      # Blueprint/floor plan processor
│
└── LLM/                           # Large Language Model OCR
    ├── requirements.txt           # LLM-specific dependencies
    ├── llm_ocr_ollama.py         # Ollama + Llama 3.2 Vision
    └── llm_ocr_transformers.py   # ViT + BERT multimodal approach
```

### File Descriptions

**Root Directory:**
- `README.md` - Documentation (this file)
- `QUICKSTART.md` - Quick installation and testing guide
- `PROJECT_SUMMARY.md` - Complete project summary and checklist
- `demo.py` - Demonstrates all OCR approaches with examples
- `verify_setup.sh` - Bash script to verify installation
- `test_api_client.py` - Python client for testing API
- `fastapi_ocr_service.py` - Production-ready REST API server
- `requirements.txt` - Base dependencies for FastAPI service

**PDF Folder:**
- `pdf_ocr_tesseract.py` - Fast OCR using Tesseract (good for standard documents)
- `pdf_ocr_easyocr.py` - Deep learning OCR using EasyOCR (multi-language support)
- `requirements.txt` - Dependencies: pdf2image, pytesseract, PyMuPDF, etc.

**BIM Folder:**
- `bim_ocr_processor.py` - Extracts dimensions, room names, and structured data
- `requirements.txt` - Dependencies: easyocr, opencv-python, PyMuPDF

**LLM Folder:**
- `llm_ocr_ollama.py` - Uses Llama 3.2 Vision for context-aware OCR
- `llm_ocr_transformers.py` - Research-grade multimodal processing with ViT and BERT
- `requirements.txt` - Dependencies: transformers, torch, ollama, langchain

## How LLM Models Work for OCR

### Overview of Vision-Enabled LLMs

Large Language Models (LLMs) with vision capabilities represent an advancement in OCR technology. Unlike traditional OCR that simply extracts text character-by-character, vision-enabled LLMs understand the context, layout, and meaning of documents.

### Architecture of Vision LLMs

Vision LLMs combine three key components:

1. **Vision Encoder** - Processes and understands images
2. **Language Model** - Understands and generates text
3. **Cross-Modal Fusion** - Connects visual and textual understanding

### How Vision LLMs Process Images

#### Step 1: Image Encoding
```
Image → Vision Encoder → Visual Embeddings
```
The vision encoder (like CLIP or ViT) converts the image into a series of numerical representations (embeddings) that capture visual features such as:
- Text regions and characters
- Layout and structure
- Tables, forms, and diagrams
- Spatial relationships

#### Step 2: Visual-Language Alignment
```
Visual Embeddings + Text Prompt → Unified Representation
```
The model aligns visual information with language understanding, allowing it to:
- Interpret what text means in context
- Understand document structure
- Recognize relationships between visual elements

#### Step 3: Text Generation
```
Unified Representation → Language Model → OCR Output
```
The language model generates text output that includes:
- Extracted text content
- Document structure information
- Contextual understanding
- Answers to specific queries

### Recommended LLM Models for OCR

#### 1. Llama 3.2 Vision (Recommended for this Project)

**Model Variants:**
- `llama3.2-vision:11b` - 11 billion parameters (Recommended)
  - Size: ~7GB download
  - RAM Required: 8GB minimum
  - Best balance of quality and performance
  
- `llama3.2-vision:90b` - 90 billion parameters
  - Size: ~50GB download
  - RAM Required: 64GB minimum
  - Highest quality, requires powerful hardware

**Why Llama 3.2 Vision:**
- Open-source and runs locally (privacy)
- Excellent multimodal understanding
- Context length: 128K tokens
- Supports both text and image inputs
- Optimized for on-device use cases
- Strong OCR and document understanding capabilities

**Use Cases:**
- Document OCR with context understanding
- Invoice and form processing
- Technical document analysis
- Multi-language text extraction

**Installation:**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull the model
ollama pull llama3.2-vision:11b

# Run the model
ollama run llama3.2-vision:11b
```

#### 2. GPT-4 Vision (OpenAI)

**Specifications:**
- Proprietary cloud-based model
- Excellent accuracy and understanding
- Requires API key and internet connection
- Pay-per-use pricing

**Pros:**
- State-of-the-art accuracy
- No local hardware requirements
- Regular updates and improvements

**Cons:**
- Requires API subscription
- Data sent to cloud (privacy concerns)
- Ongoing costs
- Internet dependency

#### 3. LLaVA (Large Language and Vision Assistant)

**Specifications:**
- Open-source vision-language model
- Based on Vicuna/Llama
- Can be fine-tuned for specific tasks

**Pros:**
- Open-source and customizable
- Good performance on visual tasks
- Active research community

**Cons:**
- Requires more technical setup
- Larger model sizes
- May need fine-tuning for best results

#### 4. Claude 3 Vision (Anthropic)

**Specifications:**
- Proprietary cloud model
- Strong document understanding
- API-based access

**Pros:**
- Excellent at structured data extraction
- Long context windows
- High accuracy

**Cons:**
- Cloud-only (no local deployment)
- Subscription required
- Data privacy considerations

### How This Project Uses LLM Models

#### Implementation 1: Ollama + Llama 3.2 Vision

**File:** `LLM/llm_ocr_ollama.py`

**How it works:**
1. **Image Encoding**: Converts image to base64
2. **API Request**: Sends image and prompt to local Ollama server
3. **Processing**: Llama 3.2 Vision analyzes the image
4. **Response**: Returns extracted text with context

**Advantages:**
- Runs completely offline
- No data leaves your machine
- No API costs
- Context-aware extraction

**Example:**
```python
from llm_ocr_ollama import LLMOCRProcessor

processor = LLMOCRProcessor(model_name='llama3.2-vision:11b')
text = processor.extract_text_from_image("document.jpg")
print(text)
```

#### Implementation 2: Transformers + ViT + BERT

**File:** `LLM/llm_ocr_transformers.py`

**How it works:**
1. **Visual Feature Extraction**: Vision Transformer (ViT) processes image
2. **Text Extraction**: Tesseract OCR extracts text
3. **Text Understanding**: BERT creates contextual embeddings
4. **Feature Fusion**: Combines visual and textual features
5. **Analysis**: Provides multimodal understanding

**Architecture:**
```
Image → ViT → Visual Features (768-dim vector)
      ↓
Image → Tesseract → Text → BERT → Text Features (768-dim vector)
      ↓
Visual + Text Features → Combined (1536-dim vector) → Analysis
```

**Advantages:**
- Full control over the pipeline
- Research-grade analysis
- Feature vectors for downstream tasks
- No API dependencies

**Example:**
```python
from llm_ocr_transformers import CNNBERTOCRProcessor

processor = CNNBERTOCRProcessor(use_gpu=False)
results = processor.process_image_multimodal("document.jpg", "output.json")

print(f"Visual features: {results['visual_feature_dim']}")
print(f"Text features: {results['text_feature_dim']}")
print(f"Extracted text: {results['extracted_text']}")
```

### Comparison: LLM OCR vs Traditional OCR

| Feature | Traditional OCR | LLM-based OCR |
|---------|----------------|---------------|
| **Text Extraction** | Character-by-character | Context-aware |
| **Understanding** | None | Semantic understanding |
| **Layout Analysis** | Limited | Advanced |
| **Complex Documents** | Poor | Excellent |
| **Handwriting** | Poor | Good |
| **Tables/Forms** | Difficult | Easy |
| **Speed** | Very Fast | Moderate |
| **Accuracy** | 85-95% | 95-99% |
| **Cost** | Free (local) | Free (local) or API cost |
| **Privacy** | Complete | Depends on deployment |

### When to Use LLM OCR

**Best Use Cases:**
- Complex document layouts (invoices, forms, receipts)
- Documents requiring context understanding
- Multi-column documents
- Documents with tables and nested structures
- Handwritten text with printed text
- Documents requiring data extraction (not just text)
- Technical documents requiring domain understanding

**When Traditional OCR is Sufficient:**
- Simple, clean documents
- Standard fonts and layouts
- High-volume batch processing (speed critical)
- Resource-constrained environments
- Privacy-critical applications with limited processing power

### Technical Deep Dive: Vision Transformers

Vision Transformers (ViT) are the backbone of modern vision LLMs:

**How ViT Works:**
1. **Patch Embedding**: Divide image into fixed-size patches (e.g., 16x16 pixels)
2. **Linear Projection**: Flatten and project patches to embedding dimension
3. **Position Encoding**: Add positional information to each patch
4. **Transformer Encoder**: Apply multi-head self-attention
5. **Classification Head**: Generate output representations

**Why ViT is Effective for OCR:**
- Captures long-range dependencies in images
- Understands spatial relationships between text regions
- Learns hierarchical features automatically
- Scales well with data and model size

### Memory and Performance Considerations

**Llama 3.2 Vision Models:**

| Model | Size | RAM Required | VRAM (GPU) | Speed | Accuracy |
|-------|------|--------------|------------|-------|----------|
| 11B | 7GB | 8GB | 8GB (opt) | Fast | Excellent |
| 90B | 50GB | 64GB | 48GB (opt) | Slow | Best |

**Recommendations:**
- **For Development/Testing**: Use 11B model
- **For Production**: Use 11B model with GPU
- **For Research**: Use 90B model if hardware permits
- **For API**: Use OpenAI GPT-4 Vision or Claude 3

## Prerequisites

### System Requirements

- **OS**: Linux (Ubuntu 20.04+ recommended)
- **Python**: 3.8 or higher
- **RAM**: Minimum 4GB (8GB+ recommended for LLM models)
- **GPU**: Optional (for faster processing with deep learning models)

### System Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and build tools
sudo apt install -y python3 python3-venv python3-pip

# Install Tesseract OCR
sudo apt install -y tesseract-ocr tesseract-ocr-eng

# Install Poppler (for PDF processing)
sudo apt install -y poppler-utils

# Install system libraries for image processing
sudo apt install -y libsm6 libxext6 libxrender-dev libgomp1
```

## 🚀 DevOps Setup

### 1. Clone or Navigate to Project Directory

```bash
cd /path/to/OCR
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Verify activation (you should see (.venv) in your prompt)
which python
```

### 3. Install Dependencies

#### Option A: Install all dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Option B: Install by use case

**For PDF OCR:**
```bash
cd PDF
pip install -r requirements.txt
cd ..
```

**For BIM OCR:**
```bash
cd BIM
pip install -r requirements.txt
cd ..
```

**For LLM OCR:**
```bash
cd LLM
pip install -r requirements.txt
cd ..
```

### 4. Setup Ollama (for LLM OCR)

Ollama is required for LLM-based OCR with vision models.

#### Install Ollama

```bash
# Download and install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
ollama --version
```

#### Pull Vision Model

```bash
# Pull Llama 3.2 Vision model (11B - requires ~8GB VRAM/RAM)
ollama pull llama3.2-vision:11b

# Alternative: Smaller model (1B - requires ~2GB RAM)
# ollama pull llama3.2-vision:1b

# Verify model is installed
ollama list
```

#### Run Ollama Server

```bash
# Start Ollama server (run in a separate terminal)
ollama serve

# Or run in background
nohup ollama serve > ollama.log 2>&1 &
```

#### Test Ollama

```bash
# Test the model
ollama run llama3.2-vision:11b
```

### 5. Verify Installation

```bash
# Check Python packages
pip list

# Check Tesseract
tesseract --version

# Check Poppler
pdftoppm -v

# Test Python imports
python -c "import pytesseract, easyocr, PIL; print('✓ All imports successful')"
```

### 6. Deactivate Virtual Environment

When done working:
```bash
deactivate
```

### 7. Reactivate Virtual Environment

To resume work:
```bash
cd /path/to/OCR
source .venv/bin/activate
```

## Use Cases

### 1. PDF OCR

Extract text from PDF documents using different approaches.

#### Approach 1: pdf2image + Tesseract

Best for: Fast processing, well-formatted documents

```bash
# Activate virtual environment
source .venv/bin/activate

# Process a PDF file
python PDF/pdf_ocr_tesseract.py sample.pdf output.txt

# Process an image
python PDF/pdf_ocr_tesseract.py document.jpg output.txt
```

**Features:**
- High-speed processing
- Good for English text
- Lightweight
- Requires Tesseract and Poppler

**Code Example:**
```python
from pdf_ocr_tesseract import PDFOCRProcessor

processor = PDFOCRProcessor(dpi=600)
text = processor.extract_text_from_pdf("scanned.pdf", "output.txt")
print(text)
```

#### Approach 2: PyMuPDF + EasyOCR

Best for: Multi-language documents, higher accuracy

```bash
# Activate virtual environment
source .venv/bin/activate

# Process a PDF file
python PDF/pdf_ocr_easyocr.py sample.pdf output.txt

# Use GPU acceleration (if available)
python PDF/pdf_ocr_easyocr.py sample.pdf output.txt --gpu

# Keep temporary images
python PDF/pdf_ocr_easyocr.py sample.pdf output.txt --keep-images
```

**Features:**
- Supports 80+ languages
- Deep learning-based
- Higher accuracy
- GPU acceleration support

**Code Example:**
```python
from pdf_ocr_easyocr import PDFOCREasyProcessor

processor = PDFOCREasyProcessor(languages=['en'], gpu=False)
text = processor.extract_text_from_pdf("scanned.pdf", "output.txt")
print(text)
```

### 2. BIM OCR

Extract structured data from Building Information Modeling images, blueprints, and floor plans.

```bash
# Activate virtual environment
source .venv/bin/activate

# Process BIM image
python BIM/bim_ocr_processor.py blueprint.jpg bim_data.json

# With visualization
python BIM/bim_ocr_processor.py floorplan.png output.json --visualize

# Use GPU acceleration
python BIM/bim_ocr_processor.py drawing.jpg output.json --gpu --visualize
```

**Features:**
- Text detection with bounding boxes
- Dimension extraction (measurements)
- Room name identification
- Structured JSON output
- Visualization support

**Code Example:**
```python
from bim_ocr_processor import BIMOCRProcessor

processor = BIMOCRProcessor(languages=['en'], gpu=False)
results = processor.process_bim_image("blueprint.jpg", "output.json")

print(f"Found {len(results['dimensions'])} dimensions")
print(f"Found {len(results['rooms'])} rooms")
```

**Output Structure:**
```json
{
  "image_path": "blueprint.jpg",
  "total_text_elements": 45,
  "dimensions": [
    {"value": "10.5m", "confidence": 0.92}
  ],
  "rooms": [
    {"name": "LIVING ROOM", "type": "living", "confidence": 0.95}
  ],
  "text_data": [...]
}
```

### 3. LLM OCR

Advanced OCR using Large Language Models with vision capabilities.

#### Approach 1: Ollama with Llama 3.2 Vision

Best for: Context-aware text extraction, document understanding

```bash
# Make sure Ollama server is running
ollama serve

# In another terminal, activate virtual environment
source .venv/bin/activate

# Process an image
python LLM/llm_ocr_ollama.py document.jpg output.txt

# Extract structured data
python LLM/llm_ocr_ollama.py invoice.png output.json --structured

# Stream response
python LLM/llm_ocr_ollama.py image.jpg output.txt --stream

# Custom prompt
python LLM/llm_ocr_ollama.py form.jpg output.txt --prompt "Extract all form fields and values"

# Use different model
python LLM/llm_ocr_ollama.py doc.png out.txt --model llama3.2-vision:1b
```

**Features:**
- Context-aware text extraction
- Document type identification
- Table and structure understanding
- Natural language querying
- Multiple language support

**Code Example:**
```python
from llm_ocr_ollama import LLMOCRProcessor

processor = LLMOCRProcessor(model_name='llama3.2-vision:11b')
text = processor.extract_text_from_image("document.jpg")

# Or extract structured data
data = processor.extract_structured_data("invoice.png")
print(data)
```

#### Approach 2: Transformers + BERT + Vision Transformer

Best for: Research, custom training, offline processing

```bash
# Activate virtual environment
source .venv/bin/activate

# Process an image
python LLM/llm_ocr_transformers.py document.jpg analysis.json

# Use GPU acceleration
python LLM/llm_ocr_transformers.py image.jpg output.json --gpu
```

**Features:**
- Vision Transformer for visual features
- BERT for text understanding
- Multimodal feature fusion
- Detailed text analysis
- Feature vector extraction

**Code Example:**
```python
from llm_ocr_transformers import CNNBERTOCRProcessor

processor = CNNBERTOCRProcessor(use_gpu=False)
results = processor.process_image_multimodal("document.jpg", "output.json")

print(f"Visual features: {results['visual_feature_dim']}")
print(f"Text features: {results['text_feature_dim']}")
print(f"Extracted text: {results['extracted_text']}")
```

## FastAPI Service

A production-ready REST API service that provides all OCR capabilities through HTTP endpoints.

### Start the Service

```bash
# Activate virtual environment
source .venv/bin/activate

# Start the FastAPI server
python fastapi_ocr_service.py

# The service will start at http://localhost:8000
```

### Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### API Endpoints

#### 1. PDF OCR

```bash
# Using Tesseract
curl -X POST "http://localhost:8000/api/ocr/pdf" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample.pdf" \
  -F "method=tesseract" \
  -F "dpi=600"

# Using EasyOCR
curl -X POST "http://localhost:8000/api/ocr/pdf" \
  -F "file=@sample.pdf" \
  -F "method=easyocr"
```

#### 2. Image OCR

```bash
# Using Tesseract
curl -X POST "http://localhost:8000/api/ocr/image" \
  -F "file=@document.jpg" \
  -F "method=tesseract"

# Using EasyOCR
curl -X POST "http://localhost:8000/api/ocr/image" \
  -F "file=@document.jpg" \
  -F "method=easyocr"
```

#### 3. BIM OCR

```bash
curl -X POST "http://localhost:8000/api/ocr/bim" \
  -F "file=@blueprint.jpg"
```

#### 4. LLM OCR

```bash
curl -X POST "http://localhost:8000/api/ocr/llm" \
  -F "file=@document.jpg" \
  -F "prompt=Extract all text and describe the document" \
  -F "model=llama3.2-vision:11b"
```

#### 5. OpenAI-Compatible Chat Completions

```bash
curl -X POST "http://localhost:8000/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2-vision:11b",
    "messages": [
      {
        "role": "user",
        "content": [
          {"type": "text", "text": "Extract text from this image"},
          {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
        ]
      }
    ]
  }'
```

### REST API Reference

#### Architecture Overview

```
Frontend (Port 3000)          Backend (Port 8000)           LLM Service (Port 11434)
┌─────────────────┐           ┌──────────────────┐           ┌─────────────────┐
│                 │           │                  │           │                 │
│  Static Files   │           │   FastAPI        │           │   Ollama        │
│  (HTML/CSS/JS)  │  HTTP     │   REST API       │  HTTP     │   LLM Server    │
│                 │──────────>│                  │──────────>│                 │
│  serve_frontend │           │  fastapi_ocr_    │           │  llama3.2-      │
│  .py            │           │  service.py      │           │  vision         │
│                 │           │                  │           │                 │
└─────────────────┘           └──────────────────┘           └─────────────────┘
     localhost:3000               localhost:8000               localhost:11434

User Browser ──> Frontend Server ──> FastAPI Backend ──> Ollama ──> LLM Model
```

**Key Points:**
- **Frontend Server** (`serve_frontend.py`): Serves static HTML/CSS/JS files, does NOT process images
- **FastAPI Backend** (`fastapi_ocr_service.py`): Handles OCR requests, calls Ollama for LLM-based recognition
- **Ollama**: Local LLM inference server that runs the Llama 3.2 Vision model
- **Communication**: Frontend → FastAPI (REST API) → Ollama (REST API) → LLM Response

#### API Endpoints Overview

| Endpoint | Method | Purpose | Uses Ollama |
|----------|--------|---------|-------------|
| `/api/ocr/pdf` | POST | Extract text from PDF | No (Tesseract/EasyOCR) |
| `/api/ocr/image` | POST | Extract text from image | No (Tesseract/EasyOCR) |
| `/api/ocr/bim` | POST | Extract BIM data from blueprints | No (EasyOCR) |
| `/api/ocr/llm` | POST | AI-powered image analysis | **Yes (Ollama + LLM)** |
| `/v1/chat/completions` | POST | OpenAI-compatible chat | **Yes (Ollama + LLM)** |
| `/docs` | GET | Swagger UI documentation | N/A |
| `/redoc` | GET | ReDoc documentation | N/A |

#### Endpoint 1: PDF OCR

**Path:** `POST /api/ocr/pdf`

**Description:** Extract text from PDF files using traditional OCR methods.

**Request:**
- **Content-Type:** `multipart/form-data`
- **Parameters:**
  - `file` (required): PDF file to process
  - `method` (optional): OCR method - `tesseract` or `easyocr` (default: `tesseract`)
  - `dpi` (optional): DPI for image conversion (default: `300`)

**Response:**
```json
{
  "text": "Extracted text content...",
  "method": "tesseract",
  "pages": 5
}
```

**Example (curl):**
```bash
curl -X POST "http://localhost:8000/api/ocr/pdf" \
  -F "file=@invoice.pdf" \
  -F "method=easyocr" \
  -F "dpi=600"
```

**Example (Python):**
```python
import requests

files = {'file': open('invoice.pdf', 'rb')}
data = {'method': 'easyocr', 'dpi': 600}
response = requests.post('http://localhost:8000/api/ocr/pdf', files=files, data=data)
print(response.json()['text'])
```

**Example (JavaScript/Frontend):**
```javascript
const formData = new FormData();
formData.append('file', pdfFile);
formData.append('method', 'easyocr');
formData.append('dpi', '600');

const response = await fetch('http://localhost:8000/api/ocr/pdf', {
    method: 'POST',
    body: formData
});
const result = await response.json();
console.log(result.text);
```

#### Endpoint 2: Image OCR

**Path:** `POST /api/ocr/image`

**Description:** Extract text from images using traditional OCR methods.

**Request:**
- **Content-Type:** `multipart/form-data`
- **Parameters:**
  - `file` (required): Image file (JPG, PNG, BMP, etc.)
  - `method` (optional): OCR method - `tesseract` or `easyocr` (default: `tesseract`)

**Response:**
```json
{
  "text": "Extracted text content...",
  "method": "tesseract",
  "confidence": 87.5
}
```

**Example (curl):**
```bash
curl -X POST "http://localhost:8000/api/ocr/image" \
  -F "file=@document.jpg" \
  -F "method=easyocr"
```

**Example (Python):**
```python
import requests

files = {'file': open('document.jpg', 'rb')}
data = {'method': 'easyocr'}
response = requests.post('http://localhost:8000/api/ocr/image', files=files, data=data)
print(response.json()['text'])
```

**Example (JavaScript/Frontend):**
```javascript
const formData = new FormData();
formData.append('file', imageFile);
formData.append('method', 'easyocr');

const response = await fetch('http://localhost:8000/api/ocr/image', {
    method: 'POST',
    body: formData
});
const result = await response.json();
console.log(result.text);
```

#### Endpoint 3: BIM OCR

**Path:** `POST /api/ocr/bim`

**Description:** Extract structured data from Building Information Modeling images, blueprints, and floor plans.

**Request:**
- **Content-Type:** `multipart/form-data`
- **Parameters:**
  - `file` (required): Blueprint/floor plan image

**Response:**
```json
{
  "text": "All extracted text...",
  "detections": [
    {
      "text": "LIVING ROOM",
      "bbox": [120, 450, 280, 490],
      "confidence": 0.95
    },
    {
      "text": "12' x 15'",
      "bbox": [130, 500, 210, 520],
      "confidence": 0.92
    }
  ],
  "dimensions": ["12' x 15'", "8' x 10'"],
  "room_names": ["LIVING ROOM", "BEDROOM"]
}
```

**Example (curl):**
```bash
curl -X POST "http://localhost:8000/api/ocr/bim" \
  -F "file=@floorplan.jpg"
```

**Example (Python):**
```python
import requests

files = {'file': open('floorplan.jpg', 'rb')}
response = requests.post('http://localhost:8000/api/ocr/bim', files=files)
result = response.json()

print(f"Rooms: {result['room_names']}")
print(f"Dimensions: {result['dimensions']}")
```

**Example (JavaScript/Frontend):**
```javascript
const formData = new FormData();
formData.append('file', blueprintFile);

const response = await fetch('http://localhost:8000/api/ocr/bim', {
    method: 'POST',
    body: formData
});
const result = await response.json();
console.log('Rooms:', result.room_names);
console.log('Dimensions:', result.dimensions);
```

#### Endpoint 4: LLM OCR (AI-Powered Analysis)

**Path:** `POST /api/ocr/llm`

**Description:** Use Large Language Models (Llama 3.2 Vision) via Ollama for intelligent image analysis and text extraction. This endpoint provides context-aware understanding of images.

**How It Works:**
1. Frontend sends image + prompt to FastAPI
2. FastAPI forwards request to Ollama (localhost:11434)
3. Ollama loads Llama 3.2 Vision model
4. LLM analyzes image based on prompt
5. Response flows back: LLM → Ollama → FastAPI → Frontend

**Request:**
- **Content-Type:** `multipart/form-data`
- **Parameters:**
  - `file` (required): Image file to analyze
  - `prompt` (required): Natural language instruction for the LLM
  - `model` (optional): LLM model - `llama3.2-vision:11b` or `llama3.2-vision:90b` (default: `11b`)

**Response:**
```json
{
  "text": "AI-generated analysis based on prompt...",
  "model": "llama3.2-vision:11b"
}
```

**Example (curl):**
```bash
curl -X POST "http://localhost:8000/api/ocr/llm" \
  -F "file=@invoice.jpg" \
  -F "prompt=Extract invoice number, date, total amount, and all line items" \
  -F "model=llama3.2-vision:11b"
```

**Example (Python):**
```python
import requests

files = {'file': open('receipt.jpg', 'rb')}
data = {
    'prompt': 'Extract all text and identify the vendor name, date, and total amount',
    'model': 'llama3.2-vision:11b'
}
response = requests.post('http://localhost:8000/api/ocr/llm', files=files, data=data)
print(response.json()['text'])
```

**Example (JavaScript/Frontend - Used by index.html):**
```javascript
const formData = new FormData();
formData.append('file', imageFile);
formData.append('prompt', 'Analyze this image and describe what you see in detail.');
formData.append('model', 'llama3.2-vision:11b');

const response = await fetch('http://localhost:8000/api/ocr/llm', {
    method: 'POST',
    body: formData
});
const result = await response.json();
console.log(result.text);  // AI-generated description
```

**Prompt Examples:**

*General Description:*
```
"Describe this image in detail, including all visible text, objects, and scene elements."
```

*Invoice Processing:*
```
"Extract from this invoice: invoice number, date, vendor name, all line items with quantities and prices, subtotal, tax, and total amount."
```

*Medical Document:*
```
"Extract patient information, test results, and doctor's notes from this medical report."
```

*Blueprint Analysis:*
```
"Describe the floor plan layout, identify all rooms with their dimensions, and locate doors and windows."
```

*Photo Analysis:*
```
"Identify the main subject, describe the setting, list any visible text or signs, and explain the overall context."
```

#### Endpoint 5: OpenAI-Compatible Chat Completions

**Path:** `POST /v1/chat/completions`

**Description:** OpenAI-compatible endpoint for LLM-based vision analysis. Useful for integration with existing OpenAI client libraries.

**Request:**
- **Content-Type:** `application/json`
- **Body:**
```json
{
  "model": "llama3.2-vision:11b",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "What's in this image?"
        },
        {
          "type": "image_url",
          "image_url": {
            "url": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
          }
        }
      ]
    }
  ]
}
```

**Response:**
```json
{
  "model": "llama3.2-vision:11b",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "AI-generated description..."
      }
    }
  ]
}
```

**Example (curl):**
```bash
curl -X POST "http://localhost:8000/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2-vision:11b",
    "messages": [
      {
        "role": "user",
        "content": [
          {"type": "text", "text": "Extract all text from this image"},
          {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
        ]
      }
    ]
  }'
```

**Example (Python with OpenAI library):**
```python
from openai import OpenAI
import base64

# Point to local FastAPI server
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-needed"
)

# Encode image
with open("document.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode('utf-8')

response = client.chat.completions.create(
    model="llama3.2-vision:11b",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Extract all visible text"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_data}"
                    }
                }
            ]
        }
    ]
)

print(response.choices[0].message.content)
```

#### Error Responses

All endpoints return error responses in the following format:

**400 Bad Request:**
```json
{
  "detail": "No file provided"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "OCR processing failed: [error details]"
}
```

**503 Service Unavailable:**
```json
{
  "detail": "Ollama service not available. Please ensure Ollama is running on port 11434"
}
```

#### CORS Configuration

FastAPI is configured to allow cross-origin requests from the frontend:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

This enables the frontend (localhost:3000) to make API calls to the backend (localhost:8000).

### Python Client Example

```python
import requests

# PDF OCR
files = {'file': open('sample.pdf', 'rb')}
data = {'method': 'tesseract', 'dpi': 600}
response = requests.post('http://localhost:8000/api/ocr/pdf', files=files, data=data)
print(response.json()['text'])

# Image OCR
files = {'file': open('document.jpg', 'rb')}
data = {'method': 'easyocr'}
response = requests.post('http://localhost:8000/api/ocr/image', files=files, data=data)
print(response.json()['text'])

# LLM OCR
files = {'file': open('invoice.png', 'rb')}
data = {'prompt': 'Extract invoice details', 'model': 'llama3.2-vision:11b'}
response = requests.post('http://localhost:8000/api/ocr/llm', files=files, data=data)
print(response.json()['text'])
```

## Web Frontend UI

A modern, user-friendly web interface for uploading images and receiving AI-powered descriptions using the LLM OCR capabilities.

### Overview

The frontend provides an interactive single-page application where users can:
- Upload images via drag-and-drop or file selection
- Preview uploaded images before analysis
- Customize prompts to ask specific questions about the image
- Select different LLM models (Llama 3.2 Vision 11B or 90B)
- View AI-generated descriptions and analysis
- Configure API settings

### Architecture

```
Browser (localhost:3000) → FastAPI (localhost:8000) → Ollama (localhost:11434) → LLM → Response
     ↑                           ↓                           ↓                    ↓
     └───────────────────────────┴───────────────────────────┴────────────────────┘
                           Image + Prompt + Model Selection
```

**Request Flow:**
1. User uploads image and enters prompt in web UI
2. Frontend sends POST request to FastAPI endpoint `/api/ocr/llm`
3. FastAPI forwards request to Ollama server with model specification
4. Ollama runs the selected Llama 3.2 Vision model
5. LLM analyzes the image based on the prompt
6. Response flows back through FastAPI to the browser
7. Result displayed in the web interface

### Prerequisites

Before using the frontend, ensure these services are running:

#### 1. Ollama Server

```bash
# Start Ollama server
ollama serve

# In another terminal, verify it's running
curl http://localhost:11434/api/tags
```

#### 2. Llama 3.2 Vision Model

```bash
# Pull the 11B model (recommended, ~7.9 GB)
ollama pull llama3.2-vision:11b

# Or pull the 90B model (higher accuracy, ~55 GB)
ollama pull llama3.2-vision:90b

# Verify model is available
ollama list
```

#### 3. FastAPI Service

```bash
# Activate virtual environment
source .venv/bin/activate

# Start the FastAPI server
python fastapi_ocr_service.py

# The service will start at http://localhost:8000
# Verify it's running: http://localhost:8000/docs
```

### Starting the Frontend

The frontend is served using Python's built-in HTTP server with CORS support:

```bash
# Make sure you're in the project root directory
cd /home/laptop/EXERCISES/MISCELLANEOUS/miscellaneous/OCR

# Start the frontend server (serves on port 3000)
python serve_frontend.py
```

You should see:
```
Starting frontend server on port 3000...
Server started successfully!

Frontend URL: http://localhost:3000
API URL: http://localhost:8000

Prerequisites:
1. FastAPI service should be running on port 8000
   Start with: python fastapi_ocr_service.py

2. Ollama server should be running on port 11434
   Start with: ollama serve

3. Llama 3.2 Vision model should be installed
   Install with: ollama pull llama3.2-vision:11b

Press Ctrl+C to stop the server.
```

### Using the Web Interface

#### 1. Access the Interface

Open your web browser and navigate to:
```
http://localhost:3000
```

#### 2. Upload an Image

**Method A: Drag and Drop**
- Drag an image file from your file explorer
- Drop it onto the upload area with the dotted border
- The image will be previewed immediately

**Method B: File Selection**
- Click the "Choose File" button or anywhere in the upload area
- Select an image file (JPG, PNG, GIF, BMP, WebP)
- The image will be previewed immediately

#### 3. Customize the Prompt

The default prompt is:
```
Analyze this image and describe what you see in detail.
```

You can customize it for specific use cases:

**For Document Analysis:**
```
Extract all text from this document and organize it in a structured format.
```

**For Invoice Processing:**
```
Extract the following information from this invoice:
- Invoice number
- Date
- Total amount
- Line items with prices
- Vendor name
```

**For Blueprint Analysis:**
```
Describe the layout of this floor plan, including:
- Room names and dimensions
- Door and window locations
- Overall structure
```

**For Photo Description:**
```
Describe the scene in this photo, including:
- Main subjects
- Setting and environment
- Colors and lighting
- Any text or signs visible
```

**For Technical Diagrams:**
```
Explain this technical diagram, identifying:
- Components and their labels
- Connections and relationships
- Any measurements or specifications
```

#### 4. Select LLM Model

Choose the appropriate model for your needs:

- **llama3.2-vision:11b** (Default, Recommended)
  - Faster response time (~5-10 seconds)
  - Lower memory usage (~8 GB RAM)
  - Good accuracy for most tasks
  - Suitable for general image analysis

- **llama3.2-vision:90b** (Advanced)
  - Higher accuracy and detail
  - Better for complex images
  - Slower response time (~30-60 seconds)
  - Requires more memory (~64 GB RAM)
  - Best for professional/critical tasks

#### 5. Configure API URL (Optional)

If your FastAPI service is running on a different port or server:
- Modify the API URL field (default: `http://localhost:8000`)
- Example for remote server: `http://192.168.1.100:8000`

#### 6. Analyze Image

Click the "Analyze Image" button:
- A loading spinner will appear
- The request is sent to FastAPI with your image, prompt, and model selection
- Processing time depends on:
  - Image size
  - Model selected (11B vs 90B)
  - System resources
  - Prompt complexity

#### 7. View Results

The AI analysis will be displayed in the results section:
- Detailed description based on your prompt
- Extracted text (if applicable)
- Structured information (if requested)
- Any additional insights from the LLM

### How It Works: Prompt + FastAPI + Ollama + LLM

#### Static File Serving

The `serve_frontend.py` script uses Python's built-in HTTP server:

```python
import http.server
import socketserver

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers for cross-origin requests
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def __init__(self, *args, **kwargs):
        # Serve files from frontend/ directory
        super().__init__(*args, directory='frontend', **kwargs)

# Start server on port 3000
with socketserver.TCPServer(("", 3000), CustomHTTPRequestHandler) as httpd:
    httpd.serve_forever()
```

**Why CORS?** Cross-Origin Resource Sharing headers allow the frontend (localhost:3000) to make API requests to the backend (localhost:8000) without security restrictions.

#### Frontend Request Flow

When you click "Analyze Image", the following happens:

**1. JavaScript Prepares Request**
```javascript
const formData = new FormData();
formData.append('file', imageFile);          // The uploaded image
formData.append('prompt', promptText);        // Your custom prompt
formData.append('model', selectedModel);      // llama3.2-vision:11b or 90b
```

**2. Send to FastAPI**
```javascript
const response = await fetch(`${apiUrl}/api/ocr/llm`, {
    method: 'POST',
    body: formData
});
```

**3. FastAPI Processes Request** (`fastapi_ocr_service.py`)
```python
@app.post("/api/ocr/llm")
async def ocr_llm(
    file: UploadFile = File(...),
    prompt: str = Form(...),
    model: str = Form(default="llama3.2-vision:11b")
):
    # Save uploaded file temporarily
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        buffer.write(await file.read())
    
    # Initialize LLM processor
    processor = LLMOCRProcessor(model=model)
    
    # Process image with prompt
    result = processor.process_image(temp_path, prompt)
    
    # Clean up and return
    os.remove(temp_path)
    return {"text": result, "model": model}
```

**4. FastAPI → Ollama** (`LLM/llm_ocr_ollama.py`)
```python
import base64
import requests

class LLMOCRProcessor:
    def process_image(self, image_path: str, prompt: str):
        # Encode image as base64
        with open(image_path, 'rb') as img_file:
            image_data = base64.b64encode(img_file.read()).decode('utf-8')
        
        # Send to Ollama API
        response = requests.post('http://localhost:11434/api/generate', json={
            'model': self.model,           # llama3.2-vision:11b
            'prompt': prompt,              # Your custom prompt
            'images': [image_data],        # Base64-encoded image
            'stream': False
        })
        
        return response.json()['response']
```

**5. Ollama → LLM Model**
- Ollama receives the base64 image and prompt
- Loads Llama 3.2 Vision model into memory
- Model processes:
  - **Vision Component**: Analyzes the image pixels
  - **Language Component**: Understands the prompt
  - **Fusion**: Combines visual and textual understanding
  - **Generation**: Creates a detailed response

**6. Response Flow**
```
LLM → Ollama → FastAPI → Frontend → User
```

The generated text flows back through the same chain, finally displayed in your browser.

### Prompt Engineering Tips

The quality of results depends heavily on your prompt. Here are best practices:

#### Be Specific
```
Bad:  "What is this?"
Good: "Describe the architectural elements in this building facade."
```

#### Request Structure
```
Bad:  "Tell me about this receipt."
Good: "Extract from this receipt: date, vendor, items with prices, and total amount."
```

#### Provide Context
```
Bad:  "Describe this."
Good: "This is a medical diagram. Identify and label all anatomical structures visible."
```

#### Use Formatting Hints
```
"List the following in bullet points:
- Main subject
- Background elements
- Any text visible
- Overall mood or theme"
```

#### Chain Multiple Questions
```
"First, identify what type of document this is. Then, extract all relevant information 
based on the document type. Finally, highlight any anomalies or important details."
```

### Troubleshooting

#### Issue: "Failed to analyze image"

**Check 1: FastAPI Service**
```bash
# Verify FastAPI is running
curl http://localhost:8000/docs
```

**Check 2: Ollama Service**
```bash
# Verify Ollama is running
curl http://localhost:11434/api/tags
```

**Check 3: Model Installation**
```bash
# List installed models
ollama list

# Should show llama3.2-vision:11b or llama3.2-vision:90b
```

#### Issue: "CORS Error" or "Network Error"

**Solution 1: Verify Frontend Server**
```bash
# Make sure using serve_frontend.py, not just opening index.html
python serve_frontend.py
```

**Solution 2: Check API URL**
- In the web interface, verify API URL is correct
- Should be `http://localhost:8000` by default
- If FastAPI is on different port, update accordingly

#### Issue: "Slow Response Time"

**Solution 1: Use Smaller Model**
- Switch from `llama3.2-vision:90b` to `llama3.2-vision:11b`
- 11B model is 5-6x faster

**Solution 2: Reduce Image Size**
- Resize large images before uploading
- Target resolution: 1024x1024 or smaller

**Solution 3: Optimize Prompt**
- Shorter, more focused prompts = faster processing
- Avoid asking for excessive detail

#### Issue: "Port Already in Use"

**For Frontend (Port 3000):**
```bash
# Find process using port 3000
lsof -i :3000

# Kill the process
kill -9 <PID>

# Or use a different port (edit serve_frontend.py)
```

**For FastAPI (Port 8000):**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

#### Issue: "Out of Memory"

**Solution:** Switch to smaller model
```bash
# The 90B model requires ~64 GB RAM
# Use 11B model instead (requires ~8 GB RAM)
ollama pull llama3.2-vision:11b
```

### File Structure

The frontend consists of minimal files:

```
frontend/
├── index.html              # Complete single-page application
│   ├── HTML structure
│   ├── Inline CSS (styling)
│   └── Inline JavaScript (functionality)
└── requirements.txt        # No additional packages needed
```

**No Build Step Required:** Pure HTML/CSS/JavaScript means:
- No npm/yarn installation
- No webpack/vite compilation
- No node_modules folder
- Instant startup with Python's HTTP server

### Advanced Usage

#### Multiple Images

To process multiple images in sequence:
1. Upload first image and analyze
2. View results
3. Upload next image (previous preview will be replaced)
4. Repeat as needed

Each analysis is independent and doesn't maintain conversation history.

#### Custom API Integration

To integrate with your own backend:
1. Change API URL in the web interface
2. Ensure your backend:
   - Accepts POST requests to `/api/ocr/llm`
   - Expects multipart/form-data with `file`, `prompt`, `model` fields
   - Returns JSON with `text` field: `{"text": "analysis result"}`

#### Programmatic Access

For automation, use the Python client instead of the web UI:

```python
import requests

# Prepare request
files = {'file': open('image.jpg', 'rb')}
data = {
    'prompt': 'Extract all visible text',
    'model': 'llama3.2-vision:11b'
}

# Send to FastAPI
response = requests.post(
    'http://localhost:8000/api/ocr/llm',
    files=files,
    data=data
)

# Get result
result = response.json()
print(result['text'])
```

See `test_api_client.py` for more programmatic examples.

## Datasets

For testing and training OCR models, use these datasets:

### 1. MNIST Dataset (Recommended for Testing)

Small, fast to download, perfect for initial testing.

```bash
# Download automatically with code
python -c "
from torchvision import datasets
datasets.MNIST('./data', download=True)
print('MNIST downloaded to ./data')
"
```

**Details:**
- Size: ~11 MB
- Images: 70,000 handwritten digits (28x28 pixels)
- Use case: Test basic OCR functionality
- Download: http://yann.lecun.com/exdb/mnist/

### 2. IAM Handwriting Database

For handwriting recognition testing.

**Details:**
- Handwritten English text
- Forms and sentences
- Download: https://fki.tic.heia-fr.ch/databases/iam-handwriting-database

### 3. Sample Documents

Create your own test files:

```bash
# Create sample PDF (requires LibreOffice)
echo "This is a test document for OCR." > test.txt
libreoffice --headless --convert-to pdf test.txt

# Or use online sample PDFs
wget https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf
```

### 4. BIM Sample Images

For BIM testing, use:
- Sample floor plans from architecture websites
- Blueprint images from engineering resources
- CAD drawing exports

## References

### Documentation

- **Tesseract OCR**: https://github.com/tesseract-ocr/tessdoc
- **EasyOCR**: https://github.com/JaidedAI/EasyOCR
- **OCRmyPDF**: https://github.com/ocrmypdf/OCRmyPDF
- **Ollama**: https://ollama.com/
- **FastAPI**: https://fastapi.tiangolo.com/

### Research Papers & Articles

- **Vision Transformer (ViT)**: https://huggingface.co/docs/transformers/en/model_doc/vit
- **LLaVA**: https://github.com/haotian-liu/LLaVA
- **Llama 3.2**: https://ai.meta.com/blog/llama-3-2-connect-2024-vision-edge-mobile-devices/
- **MLflow OCR**: https://mlflow.org/blog/mlflow-prompt-evaluate

### Datasets

- **MNIST**: http://yann.lecun.com/exdb/mnist/
- **IAM Handwriting**: https://fki.tic.heia-fr.ch/databases/iam-handwriting-database

## Troubleshooting

### Common Issues

#### 1. Tesseract not found
```bash
sudo apt install tesseract-ocr
tesseract --version
```

#### 2. Poppler not found (PDF conversion fails)
```bash
sudo apt install poppler-utils
pdftoppm -v
```

#### 3. Ollama connection error
```bash
# Start Ollama server
ollama serve

# Check if running
curl http://localhost:11434/api/tags
```

#### 4. GPU not detected
```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# Use CPU mode if GPU unavailable (add --gpu flag when supported)
```

#### 5. Virtual environment issues
```bash
# Recreate virtual environment
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---
