# System Architecture & API Flow Diagram

## Complete System Overview

```
┌───────────────────────────────────────────────────────────────────────────┐
│                              USER BROWSER                                 │
│                         http://localhost:3000                             │
└───────────────────────────────────────────────────────────────────────────┘
                                    ↓
                            [User uploads image]
                                    ↓
┌───────────────────────────────────────────────────────────────────────────┐
│                         FRONTEND SERVER (Port 3000)                       │
│                           serve_frontend.py                               │
│                                                                           │
│  Purpose: Serve static HTML/CSS/JavaScript files                         │
│  Technology: Python http.server.SimpleHTTPRequestHandler                 │
│  Files Served:                                                            │
│    • frontend/index.html - Web UI                                        │
│    • Inline CSS - Styling                                                │
│    • Inline JavaScript - Functionality                                   │
│                                                                           │
│  ❌ Does NOT process images                                              │
│  ❌ Does NOT perform OCR                                                 │
│  ❌ Does NOT call Ollama                                                 │
│  ✅ Only serves static files to browser                                  │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
                                    ↓
                        [JavaScript makes fetch() call]
                                    ↓
              POST http://localhost:8000/api/ocr/llm
              Content-Type: multipart/form-data
              Body: {file: image.jpg, prompt: "...", model: "..."}
                                    ↓
┌───────────────────────────────────────────────────────────────────────────┐
│                         BACKEND API (Port 8000)                           │
│                        fastapi_ocr_service.py                             │
│                                                                           │
│  Purpose: REST API for OCR processing                                    │
│  Technology: FastAPI + Uvicorn                                           │
│                                                                           │
│  Endpoints:                                                               │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ Traditional OCR (No Ollama)                                     │   │
│  │   POST /api/ocr/pdf      → Tesseract/EasyOCR                   │   │
│  │   POST /api/ocr/image    → Tesseract/EasyOCR                   │   │
│  │   POST /api/ocr/bim      → EasyOCR                             │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ LLM OCR (Uses Ollama) ⭐                                        │   │
│  │   POST /api/ocr/llm              → Ollama + Llama 3.2         │   │
│  │   POST /v1/chat/completions      → Ollama + Llama 3.2         │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ✅ Processes OCR requests                                               │
│  ✅ Forwards LLM requests to Ollama                                      │
│  ✅ Returns JSON responses                                               │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
                                    ↓
                    [For LLM endpoints only]
                                    ↓
              POST http://localhost:11434/api/generate
              Content-Type: application/json
              Body: {model: "...", prompt: "...", images: ["base64..."]}
                                    ↓
┌───────────────────────────────────────────────────────────────────────────┐
│                          LLM SERVICE (Port 11434)                         │
│                              Ollama Server                                │
│                                                                           │
│  Purpose: Local LLM inference                                            │
│  Technology: Ollama                                                      │
│  Model: Llama 3.2 Vision (11B or 90B)                                   │
│                                                                           │
│  Processing Steps:                                                        │
│  1. Receive base64-encoded image + prompt                                │
│  2. Load Llama 3.2 Vision model into memory                             │
│  3. Vision Transformer processes image                                   │
│  4. Language model understands prompt                                    │
│  5. Generate natural language response                                   │
│  6. Return JSON with analysis                                            │
│                                                                           │
│  ✅ Runs AI models locally                                               │
│  ✅ No internet required (after model download)                          │
│  ✅ Privacy-focused (data never leaves your machine)                     │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
                                    ↓
                            [Response flows back]
                                    ↓
              Ollama → FastAPI → Frontend → Browser → User
```

## Request Flow for LLM Image Recognition

```
Step 1: User Interaction
────────────────────────
User opens http://localhost:3000
User drags image.jpg onto upload area
User types prompt: "Extract all text from this document"
User selects model: llama3.2-vision:11b
User clicks "Analyze Image" button

        ↓

Step 2: Frontend JavaScript
────────────────────────────
const formData = new FormData();
formData.append('file', imageFile);
formData.append('prompt', 'Extract all text from this document');
formData.append('model', 'llama3.2-vision:11b');

fetch('http://localhost:8000/api/ocr/llm', {
    method: 'POST',
    body: formData
})

        ↓

Step 3: HTTP Request
────────────────────
POST http://localhost:8000/api/ocr/llm
Content-Type: multipart/form-data

Parts:
  - file: [binary image data]
  - prompt: "Extract all text from this document"
  - model: "llama3.2-vision:11b"

        ↓

Step 4: FastAPI Receives Request
─────────────────────────────────
@app.post("/api/ocr/llm")
async def ocr_llm(file, prompt, model):
    # Save uploaded file
    temp_path = save_temp_file(file)
    
    # Call LLM processor
    processor = LLMOCRProcessor(model=model)
    result = processor.process_image(temp_path, prompt)
    
    # Return result
    return {"text": result, "model": model}

        ↓

Step 5: LLM Processor
─────────────────────
class LLMOCRProcessor:
    def process_image(image_path, prompt):
        # Read and encode image
        image_data = base64.b64encode(open(image_path, 'rb').read())
        
        # Prepare request for Ollama
        payload = {
            'model': 'llama3.2-vision:11b',
            'prompt': prompt,
            'images': [image_data],
            'stream': False
        }
        
        # Send to Ollama
        response = requests.post('http://localhost:11434/api/generate', json=payload)
        return response.json()['response']

        ↓

Step 6: HTTP Request to Ollama
───────────────────────────────
POST http://localhost:11434/api/generate
Content-Type: application/json

{
  "model": "llama3.2-vision:11b",
  "prompt": "Extract all text from this document",
  "images": ["/9j/4AAQSkZJRgABAQEAYABgAAD..."],
  "stream": false
}

        ↓

Step 7: Ollama Processing
──────────────────────────
1. Decode base64 image
2. Load Llama 3.2 Vision model (if not in memory)
3. Vision Transformer extracts visual features
4. Language model processes prompt
5. Generate response based on image + prompt
6. Return JSON with AI-generated text

        ↓

Step 8: Ollama Response
───────────────────────
{
  "model": "llama3.2-vision:11b",
  "response": "This document contains the following text:\n\nInvoice #12345\nDate: 2024-10-16\nTotal: $199.99\n..."
}

        ↓

Step 9: Response Flow
─────────────────────
Ollama → LLMOCRProcessor → FastAPI → Frontend JavaScript

        ↓

Step 10: Display Result
───────────────────────
Browser receives JSON:
{
  "text": "This document contains the following text:\n\nInvoice #12345...",
  "model": "llama3.2-vision:11b"
}

JavaScript updates DOM:
document.getElementById('result').textContent = response.text;

        ↓

User sees AI-generated analysis on screen!
```

## API Endpoint Comparison

### Traditional OCR (No Ollama)

```
Request:
  POST /api/ocr/image
  FormData: {file: image.jpg, method: 'tesseract'}

Processing:
  FastAPI → Tesseract OCR Engine → Text Extraction

Response:
  {"text": "INVOICE\n12345\nTotal: $199.99", "method": "tesseract"}

Speed: ⚡ Very Fast (< 1 second)
Accuracy: 📊 Good (85-95%)
Context: ❌ None
```

### LLM OCR (Uses Ollama)

```
Request:
  POST /api/ocr/llm
  FormData: {file: image.jpg, prompt: 'Extract invoice details', model: 'llama3.2-vision:11b'}

Processing:
  FastAPI → Ollama → Llama 3.2 Vision → AI Analysis

Response:
  {
    "text": "This is an invoice with the following details:\n- Invoice Number: 12345\n- Date: Oct 16, 2024\n- Total Amount: $199.99\n- Vendor: ACME Corp",
    "model": "llama3.2-vision:11b"
  }

Speed: 🐢 Slower (5-10 seconds for 11B, 30-60s for 90B)
Accuracy: 🎯 Excellent (95-99%)
Context: ✅ Advanced understanding
```

## Why Three Separate Servers?

### Frontend Server (Port 3000)
**Purpose:** Deliver static files to browser  
**Why separate?**
- Simple HTTP server, no complex logic
- Can be replaced with nginx/Apache in production
- Easy to serve on CDN
- No Python dependencies in frontend

### Backend API (Port 8000)
**Purpose:** Process OCR requests, business logic  
**Why separate?**
- FastAPI handles complex request processing
- Can scale independently
- Different deployment strategy than static files
- Needs Python environment

### LLM Service (Port 11434)
**Purpose:** Run AI models  
**Why separate?**
- Resource-intensive (needs GPU/RAM)
- Can be on different machine
- Ollama can serve multiple applications
- Isolates ML workload

## Security Note

```
┌─────────────┐
│   Internet  │
└──────┬──────┘
       │
       ↓
┌─────────────────────────────────────────┐
│  Firewall - Only expose what's needed   │
└─────────────────────────────────────────┘
       │
       ↓
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Frontend (3000) │     │  FastAPI (8000)  │     │  Ollama (11434)  │
│  ✅ Public       │────→│  ✅ Public       │────→│  ❌ Private      │
│  Static files    │     │  API Gateway     │     │  Internal only   │
└──────────────────┘     └──────────────────┘     └──────────────────┘

Production Best Practice:
- Frontend: Serve via CDN or nginx
- Backend: Expose via API gateway
- Ollama: Keep private, only accessible by backend
```

## Summary

✅ **Frontend Server** (serve_frontend.py):
   - Serves HTML/CSS/JS files
   - Port 3000
   - No image processing

✅ **Backend API** (fastapi_ocr_service.py):
   - Handles OCR requests
   - Port 8000
   - Routes to Ollama for LLM

✅ **LLM Service** (Ollama):
   - Runs AI models
   - Port 11434
   - Never directly accessed by frontend

✅ **Data Flow**:
   User → Frontend → FastAPI → Ollama → LLM → Response

✅ **Ollama Used By**:
   - /api/ocr/llm ⭐
   - /v1/chat/completions ⭐
   
✅ **Ollama NOT Used By**:
   - /api/ocr/pdf
   - /api/ocr/image
   - /api/ocr/bim
