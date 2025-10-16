"""
Sample client script to test the OCR FastAPI service.
Demonstrates how to use all API endpoints.
"""

import requests
import base64
import json
from pathlib import Path


class OCRClient:
    """Client for OCR API service."""
    
    def __init__(self, base_url="http://localhost:8000"):
        """Initialize OCR client."""
        self.base_url = base_url
    
    def health_check(self):
        """Check if the API is running."""
        response = requests.get(f"{self.base_url}/health")
        return response.json()
    
    def pdf_ocr(self, pdf_path, method="tesseract", dpi=600):
        """
        Extract text from PDF.
        
        Args:
            pdf_path: Path to PDF file
            method: 'tesseract' or 'easyocr'
            dpi: Resolution for PDF to image conversion
        """
        with open(pdf_path, 'rb') as f:
            files = {'file': (Path(pdf_path).name, f, 'application/pdf')}
            data = {'method': method, 'dpi': dpi}
            response = requests.post(
                f"{self.base_url}/api/ocr/pdf",
                files=files,
                data=data
            )
        return response.json()
    
    def image_ocr(self, image_path, method="tesseract"):
        """
        Extract text from image.
        
        Args:
            image_path: Path to image file
            method: 'tesseract' or 'easyocr'
        """
        with open(image_path, 'rb') as f:
            files = {'file': (Path(image_path).name, f)}
            data = {'method': method}
            response = requests.post(
                f"{self.base_url}/api/ocr/image",
                files=files,
                data=data
            )
        return response.json()
    
    def bim_ocr(self, image_path):
        """
        Extract structured data from BIM image.
        
        Args:
            image_path: Path to BIM image (blueprint, floor plan)
        """
        with open(image_path, 'rb') as f:
            files = {'file': (Path(image_path).name, f)}
            response = requests.post(
                f"{self.base_url}/api/ocr/bim",
                files=files
            )
        return response.json()
    
    def llm_ocr(self, image_path, prompt=None, model="llama3.2-vision:11b"):
        """
        Extract text using LLM vision model.
        
        Args:
            image_path: Path to image file
            prompt: Custom prompt for the model
            model: Ollama model name
        """
        if prompt is None:
            prompt = "Describe this image and transcribe any text in it."
        
        with open(image_path, 'rb') as f:
            files = {'file': (Path(image_path).name, f)}
            data = {
                'prompt': prompt,
                'model': model,
                'ollama_url': 'http://localhost:11434'
            }
            response = requests.post(
                f"{self.base_url}/api/ocr/llm",
                files=files,
                data=data
            )
        return response.json()
    
    def chat_completion(self, image_path, message, model="llama3.2-vision:11b"):
        """
        OpenAI-compatible chat completion with image.
        
        Args:
            image_path: Path to image file
            message: Text message/prompt
            model: Model name
        """
        # Encode image to base64
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Prepare request in OpenAI format
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": message},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ]
        }
        
        response = requests.post(
            f"{self.base_url}/v1/chat/completions",
            json=payload
        )
        return response.json()


def main():
    """Demonstrate API usage."""
    
    print("=" * 60)
    print("OCR API Client - Example Usage")
    print("=" * 60)
    
    # Initialize client
    client = OCRClient()
    
    # Check if API is running
    print("\n1. Health Check")
    print("-" * 60)
    try:
        health = client.health_check()
        print(f"✓ API Status: {health['status']}")
    except requests.exceptions.ConnectionError:
        print("✗ Error: Could not connect to API")
        print("  Make sure the server is running:")
        print("    python fastapi_ocr_service.py")
        return
    
    # Example usage (requires actual files)
    print("\n2. Example API Calls")
    print("-" * 60)
    
    print("\nPDF OCR Example:")
    print("  result = client.pdf_ocr('sample.pdf', method='tesseract')")
    print("  print(result['text'])")
    
    print("\nImage OCR Example:")
    print("  result = client.image_ocr('document.jpg', method='easyocr')")
    print("  print(result['text'])")
    
    print("\nBIM OCR Example:")
    print("  result = client.bim_ocr('blueprint.jpg')")
    print("  print(f\"Found {result['dimensions_found']} dimensions\")")
    print("  print(f\"Found {result['rooms_found']} rooms\")")
    
    print("\nLLM OCR Example:")
    print("  result = client.llm_ocr('invoice.png',")
    print("      prompt='Extract invoice details')")
    print("  print(result['text'])")
    
    print("\nChat Completion Example:")
    print("  result = client.chat_completion('document.jpg',")
    print("      'What is in this image?')")
    print("  print(result['choices'][0]['message']['content'])")
    
    print("\n" + "=" * 60)
    print("API Documentation:")
    print("  Swagger UI: http://localhost:8000/docs")
    print("  ReDoc:      http://localhost:8000/redoc")
    print("=" * 60)


if __name__ == "__main__":
    main()
