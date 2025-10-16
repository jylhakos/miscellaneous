"""
Complete OCR Demo - Demonstrates all three OCR approaches
This script shows how to use PDF, BIM, and LLM OCR methods.
"""

import os
import sys
from pathlib import Path


def demo_pdf_ocr():
    """Demonstrate PDF OCR with Tesseract."""
    print("\n" + "=" * 60)
    print("1. PDF OCR DEMO - Tesseract")
    print("=" * 60)
    
    print("""
This approach uses pdf2image to convert PDF pages to images,
then uses Tesseract OCR to extract text.

Best for: Fast processing, standard documents

Example usage:
    from PDF.pdf_ocr_tesseract import PDFOCRProcessor
    
    processor = PDFOCRProcessor(dpi=600)
    
    # Extract from PDF
    text = processor.extract_text_from_pdf("sample.pdf", "output.txt")
    
    # Extract from image
    text = processor.extract_text_from_image("document.jpg", "output.txt")

Command line:
    python PDF/pdf_ocr_tesseract.py sample.pdf output.txt
    """)


def demo_bim_ocr():
    """Demonstrate BIM OCR."""
    print("\n" + "=" * 60)
    print("2. BIM OCR DEMO - EasyOCR")
    print("=" * 60)
    
    print("""
This approach uses EasyOCR to extract structured data from
BIM images like blueprints and floor plans.

Best for: Technical drawings, blueprints, architectural plans

Features:
    - Text detection with bounding boxes
    - Dimension extraction
    - Room identification
    - Structured JSON output

Example usage:
    from BIM.bim_ocr_processor import BIMOCRProcessor
    
    processor = BIMOCRProcessor(languages=['en'], gpu=False)
    results = processor.process_bim_image("blueprint.jpg", "output.json")
    
    print(f"Dimensions found: {len(results['dimensions'])}")
    print(f"Rooms found: {len(results['rooms'])}")

Command line:
    python BIM/bim_ocr_processor.py blueprint.jpg output.json --visualize
    """)


def demo_llm_ocr():
    """Demonstrate LLM OCR."""
    print("\n" + "=" * 60)
    print("3. LLM OCR DEMO - Ollama + Vision Models")
    print("=" * 60)
    
    print("""
This approach uses Large Language Models with vision capabilities
for advanced text extraction and document understanding.

Best for: Complex documents, context-aware extraction, document understanding

Features:
    - Context-aware text extraction
    - Document type identification
    - Table and structure understanding
    - Natural language queries
    - Multi-language support

Example usage:
    from LLM.llm_ocr_ollama import LLMOCRProcessor
    
    processor = LLMOCRProcessor(model_name='llama3.2-vision:11b')
    
    # Basic OCR
    text = processor.extract_text_from_image("document.jpg")
    
    # Structured extraction
    data = processor.extract_structured_data("invoice.png")

Command line:
    python LLM/llm_ocr_ollama.py document.jpg output.txt
    python LLM/llm_ocr_ollama.py invoice.png data.json --structured
    
Prerequisites:
    1. Install Ollama: curl -fsSL https://ollama.com/install.sh | sh
    2. Start server: ollama serve
    3. Pull model: ollama pull llama3.2-vision:11b
    """)


def demo_advanced_llm():
    """Demonstrate advanced LLM OCR with transformers."""
    print("\n" + "=" * 60)
    print("4. ADVANCED LLM OCR - Transformers + BERT + ViT")
    print("=" * 60)
    
    print("""
This approach combines Vision Transformer (ViT) for visual features,
Tesseract for OCR, and BERT for contextual text understanding.

Best for: Research, custom training, multimodal analysis

Features:
    - Vision Transformer for image features
    - BERT for text embeddings
    - Multimodal feature fusion
    - Detailed analysis
    - Feature vector extraction

Example usage:
    from LLM.llm_ocr_transformers import CNNBERTOCRProcessor
    
    processor = CNNBERTOCRProcessor(use_gpu=False)
    results = processor.process_image_multimodal("doc.jpg", "output.json")
    
    print(f"Visual features: {results['visual_feature_dim']}")
    print(f"Text features: {results['text_feature_dim']}")

Command line:
    python LLM/llm_ocr_transformers.py document.jpg analysis.json
    python LLM/llm_ocr_transformers.py image.jpg output.json --gpu
    """)


def demo_fastapi():
    """Demonstrate FastAPI service."""
    print("\n" + "=" * 60)
    print("5. FASTAPI SERVICE - REST API for OCR")
    print("=" * 60)
    
    print("""
A production-ready REST API that provides all OCR capabilities
through HTTP endpoints.

Features:
    - PDF OCR endpoint
    - Image OCR endpoint
    - BIM OCR endpoint
    - LLM OCR endpoint
    - OpenAI-compatible chat completions
    - Swagger UI documentation

Start the service:
    python fastapi_ocr_service.py

API Documentation:
    - Swagger UI: http://localhost:8000/docs
    - ReDoc: http://localhost:8000/redoc

Example API calls:

1. Image OCR:
    curl -X POST "http://localhost:8000/api/ocr/image" \\
      -F "file=@document.jpg" \\
      -F "method=tesseract"

2. PDF OCR:
    curl -X POST "http://localhost:8000/api/ocr/pdf" \\
      -F "file=@sample.pdf" \\
      -F "method=tesseract"

3. BIM OCR:
    curl -X POST "http://localhost:8000/api/ocr/bim" \\
      -F "file=@blueprint.jpg"

4. LLM OCR:
    curl -X POST "http://localhost:8000/api/ocr/llm" \\
      -F "file=@document.jpg" \\
      -F "prompt=Extract all text"

Python client:
    from test_api_client import OCRClient
    
    client = OCRClient()
    result = client.image_ocr("document.jpg", method="tesseract")
    print(result['text'])
    """)


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("OCR PROJECT - COMPLETE DEMO")
    print("=" * 60)
    print("""
This project provides three different approaches for OCR:

1. PDF OCR    - Traditional OCR with Tesseract/EasyOCR
2. BIM OCR    - Structured data extraction from technical drawings
3. LLM OCR    - Advanced OCR with vision-enabled language models
4. Advanced   - Research-grade multimodal processing
5. FastAPI    - REST API service for all methods

Each approach has its strengths and use cases.
    """)
    
    # Show all demos
    demo_pdf_ocr()
    demo_bim_ocr()
    demo_llm_ocr()
    demo_advanced_llm()
    demo_fastapi()
    
    # Summary
    print("\n" + "=" * 60)
    print("COMPARISON & RECOMMENDATIONS")
    print("=" * 60)
    print("""
Choose the right approach for your needs:

┌─────────────────┬──────────────┬────────────┬─────────────┐
│ Method          │ Speed        │ Accuracy   │ Best For    │
├─────────────────┼──────────────┼────────────┼─────────────┤
│ PDF OCR         │ ⚡⚡⚡        │ ⭐⭐⭐     │ Standard    │
│ (Tesseract)     │ Very Fast    │ Good       │ documents   │
├─────────────────┼──────────────┼────────────┼─────────────┤
│ BIM OCR         │ ⚡⚡          │ ⭐⭐⭐⭐   │ Technical   │
│ (EasyOCR)       │ Fast         │ Very Good  │ drawings    │
├─────────────────┼──────────────┼────────────┼─────────────┤
│ LLM OCR         │ ⚡            │ ⭐⭐⭐⭐⭐ │ Complex     │
│ (Ollama)        │ Moderate     │ Excellent  │ documents   │
├─────────────────┼──────────────┼────────────┼─────────────┤
│ Advanced        │ ⚡            │ ⭐⭐⭐⭐⭐ │ Research    │
│ (Transformers)  │ Slow         │ Excellent  │ & analysis  │
└─────────────────┴──────────────┴────────────┴─────────────┘

Installation Requirements:

1. PDF OCR:    pip install -r PDF/requirements.txt
2. BIM OCR:    pip install -r BIM/requirements.txt
3. LLM OCR:    pip install -r LLM/requirements.txt
4. FastAPI:    pip install -r requirements.txt
    """)
    
    print("\n" + "=" * 60)
    print("GETTING STARTED")
    print("=" * 60)
    print("""
Quick start:

1. Activate virtual environment:
   source .venv/bin/activate

2. Install dependencies for your use case:
   pip install -r PDF/requirements.txt    # For PDF OCR
   pip install -r BIM/requirements.txt    # For BIM OCR
   pip install -r LLM/requirements.txt    # For LLM OCR

3. Try a simple example:
   python PDF/pdf_ocr_tesseract.py sample.jpg output.txt

4. Start the API service:
   python fastapi_ocr_service.py

5. Read the documentation:
   - README.md for detailed information
   - QUICKSTART.md for quick setup guide
   - http://localhost:8000/docs for API documentation

For more information, see README.md
    """)
    
    print("=" * 60)


if __name__ == "__main__":
    main()
