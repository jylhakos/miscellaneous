# REST API Documentation Summary

## Architecture Overview

### Three-Tier System

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND LAYER                          │
│                   (localhost:3000)                          │
│                                                             │
│  • serve_frontend.py - Python HTTP Server                  │
│  • Serves static files (HTML/CSS/JavaScript)               │
│  • Does NOT process images or OCR                          │
│  • Pure presentation and user interface                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                          ↓ HTTP POST
                    (multipart/form-data)
┌─────────────────────────────────────────────────────────────┐
│                     BACKEND LAYER                           │
│                   (localhost:8000)                          │
│                                                             │
│  • fastapi_ocr_service.py - REST API Service               │
│  • Processes OCR requests                                  │
│  • Routes:                                                 │
│    - Traditional OCR: Tesseract/EasyOCR                   │
│    - LLM OCR: Forwards to Ollama                          │
│  • Returns JSON responses                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                          ↓ HTTP POST
                      (JSON with base64 image)
┌─────────────────────────────────────────────────────────────┐
│                      LLM SERVICE                            │
│                   (localhost:11434)                         │
│                                                             │
│  • Ollama - LLM Inference Server                           │
│  • Runs Llama 3.2 Vision Model                             │
│  • Analyzes images with AI                                 │
│  • Returns natural language descriptions                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Does FastAPI Serve the Frontend?

**NO!** This is a common misconception.

- **Frontend Server**: `serve_frontend.py` (port 3000) - Serves HTML/CSS/JS files
- **Backend API**: `fastapi_ocr_service.py` (port 8000) - Processes OCR requests
- **They are separate servers!**

## Does FastAPI Use Ollama?

**YES!** But only for LLM-based endpoints:

### Endpoints That Use Ollama:
✅ `POST /api/ocr/llm` - AI-powered image analysis  
✅ `POST /v1/chat/completions` - OpenAI-compatible endpoint

### Endpoints That Don't Use Ollama:
❌ `POST /api/ocr/pdf` - Uses Tesseract or EasyOCR  
❌ `POST /api/ocr/image` - Uses Tesseract or EasyOCR  
❌ `POST /api/ocr/bim` - Uses EasyOCR

## Complete Request Flow for LLM OCR

```
1. User Action
   └── User uploads image.jpg in web browser

2. Frontend (localhost:3000)
   └── JavaScript creates FormData with:
       • file: image.jpg
       • prompt: "Extract text from this document"
       • model: "llama3.2-vision:11b"
   
3. HTTP POST Request
   └── fetch('http://localhost:8000/api/ocr/llm', {
         method: 'POST',
         body: formData
       })

4. FastAPI Backend (localhost:8000)
   └── Receives multipart/form-data
   └── Saves temporary file
   └── Calls LLMOCRProcessor.process_image()
   
5. LLM Processor
   └── Encodes image as base64
   └── Sends to Ollama API
   
6. HTTP POST to Ollama
   └── POST http://localhost:11434/api/generate
       {
         "model": "llama3.2-vision:11b",
         "prompt": "Extract text from this document",
         "images": ["base64_encoded_image"],
         "stream": false
       }

7. Ollama Processing
   └── Loads Llama 3.2 Vision model into memory
   └── Vision Transformer processes image
   └── Language model generates response
   └── Returns JSON with analysis

8. Response Flow
   └── Ollama → FastAPI → Frontend → User
   
9. Display Result
   └── Browser shows AI-generated text in results section
```

## API Endpoints Quick Reference

### Traditional OCR Endpoints

| Endpoint | Method | Input | Output | Uses Ollama |
|----------|--------|-------|--------|-------------|
| `/api/ocr/pdf` | POST | PDF file + method + dpi | Extracted text | ❌ No |
| `/api/ocr/image` | POST | Image file + method | Extracted text | ❌ No |
| `/api/ocr/bim` | POST | Blueprint image | Structured data | ❌ No |

### LLM OCR Endpoints

| Endpoint | Method | Input | Output | Uses Ollama |
|----------|--------|-------|--------|-------------|
| `/api/ocr/llm` | POST | Image + prompt + model | AI analysis | ✅ Yes |
| `/v1/chat/completions` | POST | Messages with image | AI response | ✅ Yes |

## Example: Frontend to Backend Communication

### Frontend Code (index.html)
```javascript
async function analyzeImage() {
    const formData = new FormData();
    formData.append('file', imageFile);
    formData.append('prompt', 'Describe this image in detail');
    formData.append('model', 'llama3.2-vision:11b');
    
    const response = await fetch('http://localhost:8000/api/ocr/llm', {
        method: 'POST',
        body: formData
    });
    
    const result = await response.json();
    displayResult(result.text);
}
```

### Backend Code (fastapi_ocr_service.py)
```python
@app.post("/api/ocr/llm")
async def ocr_llm(
    file: UploadFile = File(...),
    prompt: str = Form(...),
    model: str = Form(default="llama3.2-vision:11b")
):
    # Save uploaded file
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        buffer.write(await file.read())
    
    # Process with Ollama
    processor = LLMOCRProcessor(model=model)
    result = processor.process_image(temp_path, prompt)
    
    # Clean up and return
    os.remove(temp_path)
    return {"text": result, "model": model}
```

### LLM Processor Code (LLM/llm_ocr_ollama.py)
```python
class LLMOCRProcessor:
    def process_image(self, image_path: str, prompt: str):
        # Encode image
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Send to Ollama
        response = requests.post('http://localhost:11434/api/generate', json={
            'model': self.model,
            'prompt': prompt,
            'images': [image_data],
            'stream': False
        })
        
        return response.json()['response']
```

## Port Assignments

| Service | Port | Purpose | URL |
|---------|------|---------|-----|
| Frontend Server | 3000 | Static file serving | http://localhost:3000 |
| FastAPI Backend | 8000 | REST API | http://localhost:8000 |
| Ollama LLM | 11434 | LLM inference | http://localhost:11434 |

## Starting All Services

```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start FastAPI Backend
source .venv/bin/activate
python fastapi_ocr_service.py

# Terminal 3: Start Frontend Server
python serve_frontend.py

# Now open browser: http://localhost:3000
```

## Common Questions

### Q: Why are there two Python servers?
**A:** Separation of concerns:
- `serve_frontend.py` (port 3000): Delivers static files to browser
- `fastapi_ocr_service.py` (port 8000): Processes OCR/LLM requests

### Q: Can I use just one server?
**A:** Yes, but not recommended. FastAPI could serve static files with `app.mount()`, but keeping them separate is cleaner for development and deployment.

### Q: Does the frontend talk directly to Ollama?
**A:** No! Frontend → FastAPI → Ollama. FastAPI acts as a proxy/middleware.

### Q: Why not call Ollama directly from JavaScript?
**A:** 
1. CORS restrictions
2. Security (don't expose Ollama to internet)
3. Business logic (preprocessing, error handling)
4. Flexibility (can switch LLM providers)

### Q: What happens if Ollama is not running?
**A:** FastAPI returns HTTP 503 error: "Ollama service not available"

### Q: Can I use a different LLM?
**A:** Yes! Modify `LLMOCRProcessor` in `LLM/llm_ocr_ollama.py` to call:
- OpenAI API (GPT-4 Vision)
- Anthropic API (Claude 3)
- Hugging Face models
- Any other vision-language model

## Testing the API

### Test Traditional OCR
```bash
curl -X POST "http://localhost:8000/api/ocr/image" \
  -F "file=@test.jpg" \
  -F "method=tesseract"
```

### Test LLM OCR
```bash
curl -X POST "http://localhost:8000/api/ocr/llm" \
  -F "file=@test.jpg" \
  -F "prompt=Describe this image" \
  -F "model=llama3.2-vision:11b"
```

### Test from Python
```python
import requests

files = {'file': open('test.jpg', 'rb')}
data = {'prompt': 'Extract all text', 'model': 'llama3.2-vision:11b'}
response = requests.post('http://localhost:8000/api/ocr/llm', files=files, data=data)
print(response.json())
```

## API Documentation Access

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **This Document**: See README.md "REST API Reference" section
