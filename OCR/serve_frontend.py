"""
Frontend Server - Serve the React-like frontend for OCR Vision
This script serves static HTML/CSS/JS files for the OCR frontend interface.
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

# Configuration
PORT = 3000
FRONTEND_DIR = Path(__file__).parent / "frontend"

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP request handler with CORS support."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)
    
    def end_headers(self):
        """Add CORS headers to allow requests from the frontend."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight."""
        self.send_response(200)
        self.end_headers()
    
    def log_message(self, format, *args):
        """Custom log message format."""
        sys.stdout.write("%s - [%s] %s\n" %
                         (self.address_string(),
                          self.log_date_time_string(),
                          format % args))


def main():
    """Start the frontend server."""
    
    # Check if frontend directory exists
    if not FRONTEND_DIR.exists():
        print(f"Error: Frontend directory not found: {FRONTEND_DIR}")
        print("Please ensure the 'frontend' folder exists in the project root.")
        sys.exit(1)
    
    # Check if index.html exists
    index_file = FRONTEND_DIR / "index.html"
    if not index_file.exists():
        print(f"Error: index.html not found in {FRONTEND_DIR}")
        sys.exit(1)
    
    print("=" * 60)
    print("OCR Vision - Frontend Server")
    print("=" * 60)
    print(f"\nFrontend directory: {FRONTEND_DIR}")
    print(f"Server port: {PORT}")
    print("\nStarting server...")
    
    try:
        with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
            print(f"\n✓ Server started successfully!")
            print("\n" + "=" * 60)
            print("ACCESS THE APPLICATION")
            print("=" * 60)
            print(f"\nFrontend URL: http://localhost:{PORT}")
            print(f"Alternative:  http://127.0.0.1:{PORT}")
            print("\n" + "=" * 60)
            print("PREREQUISITES")
            print("=" * 60)
            print("\n1. FastAPI backend must be running:")
            print("   python fastapi_ocr_service.py")
            print("   (Should be running on http://localhost:8000)")
            print("\n2. Ollama server must be running:")
            print("   ollama serve")
            print("   (Should be running on http://localhost:11434)")
            print("\n3. Llama 3.2 Vision model must be installed:")
            print("   ollama pull llama3.2-vision:11b")
            print("\n" + "=" * 60)
            print("USAGE")
            print("=" * 60)
            print("\n1. Open http://localhost:3000 in your web browser")
            print("2. Upload an image file (JPG, PNG, etc.)")
            print("3. Optionally customize the prompt")
            print("4. Click 'Analyze Image with AI'")
            print("5. Wait for the LLM to process (10-30 seconds)")
            print("6. View the AI-generated description")
            print("\n" + "=" * 60)
            print("\nPress Ctrl+C to stop the server")
            print("=" * 60)
            print()
            
            httpd.serve_forever()
            
    except OSError as e:
        if e.errno == 98 or e.errno == 48:  # Address already in use
            print(f"\n✗ Error: Port {PORT} is already in use")
            print("\nOptions:")
            print("1. Stop the process using port 3000:")
            print(f"   lsof -ti:{PORT} | xargs kill -9")
            print("2. Or change the PORT variable in this script")
            sys.exit(1)
        else:
            raise
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("Server stopped by user")
        print("=" * 60)
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
