"""
LLM OCR Script - Using Ollama with Llama 3.2 Vision for OCR
This script uses Large Language Models with vision capabilities for advanced OCR,
image understanding, and text extraction with context awareness.
"""

import os
import sys
from pathlib import Path
import base64
import requests
import json
from PIL import Image
from io import BytesIO


class LLMOCRProcessor:
    """Process images using LLM with vision capabilities (Ollama)."""
    
    def __init__(self, model_name='llama3.2-vision:11b', api_url='http://localhost:11434'):
        """
        Initialize the LLM OCR processor.
        
        Args:
            model_name (str): Name of the Ollama vision model
            api_url (str): URL of the Ollama API server
        """
        self.model_name = model_name
        self.api_url = api_url
        self.generate_url = f"{api_url}/api/generate"
        
        print(f"Initializing LLM OCR with model: {model_name}")
        self._check_ollama_connection()
    
    def _check_ollama_connection(self):
        """Check if Ollama server is running and model is available."""
        try:
            response = requests.get(f"{self.api_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                
                if self.model_name not in model_names:
                    print(f"Warning: Model '{self.model_name}' not found.")
                    print(f"Available models: {', '.join(model_names)}")
                    print(f"\nTo install the model, run:")
                    print(f"  ollama pull {self.model_name}")
                else:
                    print(f"✓ Model '{self.model_name}' is available")
            else:
                print(f"Warning: Could not verify models (status: {response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"Warning: Could not connect to Ollama server at {self.api_url}")
            print(f"Error: {e}")
            print("\nMake sure Ollama is running:")
            print("  ollama serve")
    
    def encode_image(self, image_path):
        """
        Encode image to base64 string.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            str: Base64 encoded image
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def extract_text_from_image(self, image_path, prompt=None, stream=False):
        """
        Extract text from image using LLM vision model.
        
        Args:
            image_path (str): Path to the image file
            prompt (str, optional): Custom prompt for the model
            stream (bool): Stream the response (default: False)
            
        Returns:
            str: Extracted text and analysis
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        print(f"Processing image: {image_path}")
        
        # Default prompt for OCR
        if prompt is None:
            prompt = """Please analyze this image and:
1. Transcribe all visible text in the image
2. Describe the layout and structure of the content
3. Identify any important elements (tables, lists, headings, etc.)
4. Extract any numbers, dates, or measurements

Provide a clear, structured response."""
        
        # Encode image
        image_base64 = self.encode_image(image_path)
        
        # Prepare request payload
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "images": [image_base64],
            "stream": stream
        }
        
        print("Sending request to Ollama...")
        print(f"Model: {self.model_name}")
        print(f"Prompt: {prompt[:100]}...")
        
        try:
            response = requests.post(
                self.generate_url,
                json=payload,
                timeout=300  # 5 minute timeout for large images
            )
            
            if response.status_code == 200:
                if stream:
                    # Handle streaming response
                    full_response = ""
                    for line in response.iter_lines():
                        if line:
                            json_response = json.loads(line)
                            chunk = json_response.get('response', '')
                            full_response += chunk
                            print(chunk, end='', flush=True)
                    print()  # New line after streaming
                    return full_response
                else:
                    # Handle non-streaming response
                    result = response.json()
                    return result.get('response', '')
            else:
                raise Exception(f"API request failed with status {response.status_code}: {response.text}")
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to connect to Ollama: {e}")
    
    def extract_structured_data(self, image_path):
        """
        Extract structured data from image with specific prompting.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            dict: Structured data extracted from the image
        """
        prompt = """Analyze this image and extract information in the following JSON format:
{
  "text_content": "all visible text",
  "document_type": "type of document (invoice, form, blueprint, etc.)",
  "key_elements": ["list", "of", "important", "elements"],
  "numbers_and_measurements": ["any numbers or measurements found"],
  "tables": "description of any tables or structured data",
  "metadata": "any dates, names, or identifying information"
}

Provide only the JSON response."""
        
        response_text = self.extract_text_from_image(image_path, prompt)
        
        # Try to parse JSON from response
        try:
            # Find JSON in response (it might have extra text)
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end > start:
                json_str = response_text[start:end]
                return json.loads(json_str)
            else:
                return {"raw_response": response_text}
        except json.JSONDecodeError:
            return {"raw_response": response_text}
    
    def compare_images(self, image_path1, image_path2):
        """
        Compare two images and identify differences.
        
        Args:
            image_path1 (str): Path to first image
            image_path2 (str): Path to second image
            
        Returns:
            str: Analysis of differences
        """
        prompt = "Compare these two images and describe any differences you observe."
        
        image1_base64 = self.encode_image(image_path1)
        image2_base64 = self.encode_image(image_path2)
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "images": [image1_base64, image2_base64],
            "stream": False
        }
        
        response = requests.post(self.generate_url, json=payload, timeout=300)
        
        if response.status_code == 200:
            return response.json().get('response', '')
        else:
            raise Exception(f"API request failed: {response.text}")


def main():
    """Main function to demonstrate LLM OCR."""
    
    print("=" * 50)
    print("LLM OCR Processor - Ollama Vision")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else "llm_output.txt"
        
        # Optional custom prompt
        custom_prompt = None
        if '--prompt' in sys.argv:
            prompt_idx = sys.argv.index('--prompt')
            if prompt_idx + 1 < len(sys.argv):
                custom_prompt = sys.argv[prompt_idx + 1]
        
        # Optional model specification
        model_name = 'llama3.2-vision:11b'
        if '--model' in sys.argv:
            model_idx = sys.argv.index('--model')
            if model_idx + 1 < len(sys.argv):
                model_name = sys.argv[model_idx + 1]
        
        structured = '--structured' in sys.argv
        stream = '--stream' in sys.argv
        
        try:
            processor = LLMOCRProcessor(model_name=model_name)
            
            if structured:
                print("\nExtracting structured data...")
                result = processor.extract_structured_data(input_file)
                result_text = json.dumps(result, indent=2, ensure_ascii=False)
            else:
                print("\nExtracting text...")
                result_text = processor.extract_text_from_image(
                    input_file, 
                    prompt=custom_prompt,
                    stream=stream
                )
            
            # Save output
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result_text)
            print(f"\nOutput saved to: {output_file}")
            
            # Print preview
            print("\n" + "=" * 50)
            print("RESULT (Preview - First 500 characters):")
            print("=" * 50)
            print(result_text[:500])
            if len(result_text) > 500:
                print(f"\n... ({len(result_text) - 500} more characters)")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        print("\nUsage:")
        print(f"  python {sys.argv[0]} <input_image> [output_file] [options]")
        print("\nExample:")
        print(f"  python {sys.argv[0]} document.jpg output.txt")
        print(f"  python {sys.argv[0]} invoice.png output.json --structured")
        print(f"  python {sys.argv[0]} image.jpg output.txt --stream")
        print(f"  python {sys.argv[0]} doc.png out.txt --model llama3.2-vision")
        print("\nOptions:")
        print("  --structured           Extract data in structured JSON format")
        print("  --stream               Stream the response in real-time")
        print("  --model <name>         Specify Ollama model (default: llama3.2-vision:11b)")
        print("  --prompt \"<text>\"      Custom prompt for the model")
        print("\nPrerequisites:")
        print("  1. Install Ollama: https://ollama.com/download")
        print("  2. Start Ollama server: ollama serve")
        print("  3. Pull vision model: ollama pull llama3.2-vision:11b")


if __name__ == "__main__":
    main()
