"""
FastAPI OCR Service
A REST API service that provides OCR capabilities for PDF, BIM images, and LLM-based processing.
This service is compatible with OpenAI-like API structure and uses Ollama for LLM processing.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import base64
import os
import tempfile
import shutil
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

# Import OCR processors
import pytesseract
from pdf2image import convert_from_path
import fitz  # PyMuPDF
from PIL import Image
import easyocr
import requests
import json

# Initialize FastAPI app
app = FastAPI(
    title="OCR Service API",
    description="RESTful API for OCR processing of PDF files, BIM images, and LLM-based OCR",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize EasyOCR reader (lazy loading)
ocr_reader = None

def get_ocr_reader():
    """Lazy load EasyOCR reader."""
    global ocr_reader
    if ocr_reader is None:
        print("Initializing EasyOCR reader...")
        ocr_reader = easyocr.Reader(['en'], gpu=False)
    return ocr_reader


# Pydantic models
class OCRResponse(BaseModel):
    """Response model for OCR operations."""
    success: bool
    text: str
    method: str
    metadata: Optional[dict] = None


class LLMRequest(BaseModel):
    """Request model for LLM OCR (OpenAI-like format)."""
    model: str = "llama3.2-vision:11b"
    messages: List[dict]
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7


class LLMResponse(BaseModel):
    """Response model for LLM OCR (OpenAI-like format)."""
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[dict]
    usage: Optional[dict] = None


# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "service": "OCR API",
        "version": "1.0.0",
        "endpoints": {
            "pdf_ocr": "/api/ocr/pdf",
            "image_ocr": "/api/ocr/image",
            "bim_ocr": "/api/ocr/bim",
            "llm_ocr": "/api/ocr/llm",
            "chat_completions": "/v1/chat/completions"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ocr-api"}


# PDF OCR endpoint
@app.post("/api/ocr/pdf", response_model=OCRResponse)
async def pdf_ocr(
    file: UploadFile = File(...),
    method: str = Form("tesseract"),
    dpi: int = Form(600)
):
    """
    Extract text from PDF file.
    
    - **file**: PDF file to process
    - **method**: OCR method ('tesseract' or 'easyocr')
    - **dpi**: Resolution for PDF to image conversion
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        shutil.copyfileobj(file.file, tmp_file)
        tmp_path = tmp_file.name
    
    try:
        # Convert PDF to images
        print(f"Converting PDF to images at {dpi} DPI...")
        pages = convert_from_path(tmp_path, dpi)
        
        text_data = ""
        
        if method == "tesseract":
            # Use Tesseract OCR
            for i, page in enumerate(pages, 1):
                text = pytesseract.image_to_string(page)
                text_data += f"\n--- Page {i} ---\n{text}\n"
        
        elif method == "easyocr":
            # Use EasyOCR
            reader = get_ocr_reader()
            for i, page in enumerate(pages, 1):
                # Save page as temporary image
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as img_tmp:
                    page.save(img_tmp.name)
                    result = reader.readtext(img_tmp.name, detail=0)
                    text = '\n'.join(result)
                    text_data += f"\n--- Page {i} ---\n{text}\n"
                    os.unlink(img_tmp.name)
        else:
            raise HTTPException(status_code=400, detail="Invalid method. Use 'tesseract' or 'easyocr'")
        
        return OCRResponse(
            success=True,
            text=text_data,
            method=method,
            metadata={
                "pages": len(pages),
                "dpi": dpi,
                "filename": file.filename
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Clean up
        os.unlink(tmp_path)


# Image OCR endpoint
@app.post("/api/ocr/image", response_model=OCRResponse)
async def image_ocr(
    file: UploadFile = File(...),
    method: str = Form("tesseract")
):
    """
    Extract text from image file.
    
    - **file**: Image file to process (jpg, png, bmp, tiff)
    - **method**: OCR method ('tesseract' or 'easyocr')
    """
    # Save uploaded file temporarily
    suffix = Path(file.filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        shutil.copyfileobj(file.file, tmp_file)
        tmp_path = tmp_file.name
    
    try:
        if method == "tesseract":
            # Use Tesseract OCR
            image = Image.open(tmp_path)
            text = pytesseract.image_to_string(image)
        
        elif method == "easyocr":
            # Use EasyOCR
            reader = get_ocr_reader()
            result = reader.readtext(tmp_path, detail=0)
            text = '\n'.join(result)
        
        else:
            raise HTTPException(status_code=400, detail="Invalid method. Use 'tesseract' or 'easyocr'")
        
        return OCRResponse(
            success=True,
            text=text,
            method=method,
            metadata={"filename": file.filename}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Clean up
        os.unlink(tmp_path)


# BIM OCR endpoint
@app.post("/api/ocr/bim")
async def bim_ocr(file: UploadFile = File(...)):
    """
    Extract structured data from BIM images (blueprints, floor plans).
    
    - **file**: BIM image file to process
    """
    # Save uploaded file temporarily
    suffix = Path(file.filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        shutil.copyfileobj(file.file, tmp_file)
        tmp_path = tmp_file.name
    
    try:
        reader = get_ocr_reader()
        
        # Extract text with positions
        result = reader.readtext(tmp_path)
        
        extracted_data = []
        dimensions = []
        rooms = []
        
        import re
        
        room_keywords = [
            'room', 'bedroom', 'bathroom', 'kitchen', 'living', 'dining',
            'office', 'hall', 'corridor', 'lobby', 'entrance', 'garage',
            'balcony', 'terrace', 'storage'
        ]
        
        for detection in result:
            bbox, text, confidence = detection
            
            item = {
                'text': text,
                'confidence': float(confidence),
                'bbox': bbox
            }
            extracted_data.append(item)
            
            # Extract dimensions
            dim_pattern = r'(\d+\.?\d*)\s*(?:m|mm|cm|ft|in|\'|")'
            if re.search(dim_pattern, text, re.IGNORECASE):
                dimensions.append(item)
            
            # Extract room names
            text_lower = text.lower()
            for keyword in room_keywords:
                if keyword in text_lower:
                    rooms.append({**item, 'type': keyword})
                    break
        
        return {
            "success": True,
            "filename": file.filename,
            "total_elements": len(extracted_data),
            "dimensions_found": len(dimensions),
            "rooms_found": len(rooms),
            "text_data": extracted_data,
            "dimensions": dimensions,
            "rooms": rooms
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Clean up
        os.unlink(tmp_path)


# LLM OCR endpoint
@app.post("/api/ocr/llm")
async def llm_ocr(
    file: UploadFile = File(...),
    prompt: str = Form("Describe this image and transcribe any text in it."),
    model: str = Form("llama3.2-vision:11b"),
    ollama_url: str = Form("http://localhost:11434")
):
    """
    Extract text from image using LLM vision model (Ollama).
    
    - **file**: Image file to process
    - **prompt**: Custom prompt for the LLM
    - **model**: Ollama model name
    - **ollama_url**: Ollama server URL
    """
    # Save uploaded file temporarily
    suffix = Path(file.filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        shutil.copyfileobj(file.file, tmp_file)
        tmp_path = tmp_file.name
    
    try:
        # Encode image to base64
        with open(tmp_path, "rb") as img_file:
            image_base64 = base64.b64encode(img_file.read()).decode('utf-8')
        
        # Prepare request to Ollama
        payload = {
            "model": model,
            "prompt": prompt,
            "images": [image_base64],
            "stream": False
        }
        
        # Send request to Ollama
        response = requests.post(
            f"{ollama_url}/api/generate",
            json=payload,
            timeout=300
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "text": result.get('response', ''),
                "model": model,
                "filename": file.filename,
                "metadata": {
                    "prompt": prompt,
                    "model": model
                }
            }
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Ollama API error: {response.text}"
            )
    
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Could not connect to Ollama server: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Clean up
        os.unlink(tmp_path)


# OpenAI-compatible chat completions endpoint
@app.post("/v1/chat/completions")
async def chat_completions(request: LLMRequest):
    """
    OpenAI-compatible chat completions endpoint for vision tasks.
    
    This endpoint mimics OpenAI's API structure but uses Ollama backend.
    """
    try:
        # Extract image from messages
        image_base64 = None
        prompt_text = ""
        
        for message in request.messages:
            if isinstance(message.get('content'), list):
                for content_item in message['content']:
                    if content_item.get('type') == 'image_url':
                        # Extract base64 from data URL
                        image_url = content_item['image_url']['url']
                        if image_url.startswith('data:image'):
                            image_base64 = image_url.split(',')[1]
                        else:
                            raise HTTPException(
                                status_code=400,
                                detail="Only base64 encoded images are supported"
                            )
                    elif content_item.get('type') == 'text':
                        prompt_text += content_item['text'] + " "
            elif isinstance(message.get('content'), str):
                prompt_text += message['content'] + " "
        
        if not image_base64:
            raise HTTPException(
                status_code=400,
                detail="No image found in request"
            )
        
        # Send request to Ollama
        payload = {
            "model": request.model,
            "prompt": prompt_text.strip(),
            "images": [image_base64],
            "stream": False
        }
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=300
        )
        
        if response.status_code == 200:
            result = response.json()
            
            import time
            
            # Format response in OpenAI style
            return {
                "id": f"chatcmpl-{int(time.time())}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": request.model,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": result.get('response', '')
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
            }
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Ollama API error: {response.text}"
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 50)
    print("Starting OCR FastAPI Service")
    print("=" * 50)
    print("\nAvailable endpoints:")
    print("  - PDF OCR:    POST /api/ocr/pdf")
    print("  - Image OCR:  POST /api/ocr/image")
    print("  - BIM OCR:    POST /api/ocr/bim")
    print("  - LLM OCR:    POST /api/ocr/llm")
    print("  - Chat API:   POST /v1/chat/completions")
    print("\nAPI Documentation:")
    print("  - Swagger UI: http://localhost:8000/docs")
    print("  - ReDoc:      http://localhost:8000/redoc")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
