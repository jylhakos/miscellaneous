#!/usr/bin/env python3
"""
Model Management Utility for Arcee Agent

This script provides utilities for downloading, managing, and deploying
Arcee Agent models in various formats.

Usage:
    python model_manager.py download --type quantized
    python model_manager.py serve --type ollama
    python model_manager.py info --model_path ./models/arcee-agent-q4_k_m.gguf
"""

import argparse
import os
import sys
import subprocess
import json
import time
from pathlib import Path
import requests

def check_ollama_installed():
    """Check if Ollama is installed."""
    try:
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def check_gpu():
    """Check GPU availability."""
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            return True, gpu_name, gpu_memory
        else:
            return False, None, None
    except ImportError:
        return False, None, None

def download_quantized_model(model_dir="./models"):
    """Download quantized GGUF model."""
    print("📦 Downloading quantized Arcee Agent model...")
    
    try:
        from huggingface_hub import hf_hub_download
        
        os.makedirs(model_dir, exist_ok=True)
        
        model_path = hf_hub_download(
            repo_id="crusoeai/Arcee-Agent-GGUF",
            filename="arcee-agent-q4_k_m.gguf",
            local_dir=model_dir,
            local_dir_use_symlinks=False
        )
        
        print(f"✅ Model downloaded to: {model_path}")
        
        # Get file size
        file_size = os.path.getsize(model_path) / 1024**3
        print(f"📊 File size: {file_size:.2f} GB")
        
        return model_path
        
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return None

def download_original_model(model_dir="./models"):
    """Download original model from HuggingFace."""
    print("📦 Downloading original Arcee Agent model...")
    
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        model_name = "arcee-ai/Arcee-Agent"
        local_path = os.path.join(model_dir, "arcee-agent-original")
        
        print("Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        tokenizer.save_pretrained(local_path)
        
        print("Downloading model...")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype="auto",
            trust_remote_code=True
        )
        model.save_pretrained(local_path)
        
        print(f"✅ Model downloaded to: {local_path}")
        return local_path
        
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return None

def setup_ollama():
    """Set up Ollama with Arcee Agent."""
    print("🔧 Setting up Ollama with Arcee Agent...")
    
    if not check_ollama_installed():
        print("❌ Ollama not found. Please install from https://ollama.ai/")
        return False
    
    try:
        # Pull the model
        print("Pulling arcee-ai/arcee-agent...")
        result = subprocess.run(
            ['ollama', 'pull', 'arcee-ai/arcee-agent'],
            capture_output=True, text=True, timeout=600
        )
        
        if result.returncode == 0:
            print("✅ Ollama model pulled successfully")
            return True
        else:
            print(f"❌ Failed to pull model: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout while pulling model")
        return False
    except Exception as e:
        print(f"❌ Error setting up Ollama: {e}")
        return False

def start_ollama_server():
    """Start Ollama server."""
    print("🚀 Starting Ollama server...")
    
    try:
        # Check if already running
        response = requests.get("http://127.0.0.1:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama server is already running")
            return True
    except:
        pass
    
    try:
        # Start server
        subprocess.Popen(
            ['ollama', 'serve'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Wait for server to start
        for i in range(30):
            try:
                time.sleep(1)
                response = requests.get("http://127.0.0.1:11434/api/tags", timeout=2)
                if response.status_code == 200:
                    print("✅ Ollama server started successfully")
                    return True
            except:
                continue
        
        print("❌ Failed to start Ollama server")
        return False
        
    except Exception as e:
        print(f"❌ Error starting Ollama server: {e}")
        return False

def start_vllm_server(model_path=None, port=8000):
    """Start VLLM server."""
    print("🚀 Starting VLLM server...")
    
    try:
        import vllm
    except ImportError:
        print("❌ VLLM not installed. Install with: pip install vllm")
        return False
    
    model_name = model_path or "arcee-ai/Arcee-Agent"
    
    cmd = [
        'vllm', 'serve', model_name,
        '--port', str(port),
        '--trust-remote-code'
    ]
    
    try:
        print(f"Starting VLLM server on port {port}...")
        print(f"Model: {model_name}")
        print("This will run in the foreground. Press Ctrl+C to stop.")
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\\n🛑 VLLM server stopped")
    except Exception as e:
        print(f"❌ Error starting VLLM server: {e}")
        return False

def get_model_info(model_path):
    """Get information about a model file."""
    print(f"📊 Model Information: {model_path}")
    print("=" * 50)
    
    if not os.path.exists(model_path):
        print("❌ Model file not found")
        return
    
    # File size
    file_size = os.path.getsize(model_path) / 1024**3
    print(f"File size: {file_size:.2f} GB")
    
    # File type
    if model_path.endswith('.gguf'):
        print("Format: GGUF (Quantized)")
        print("Compatible with: llama.cpp, Ollama, text-generation-webui")
    elif 'safetensors' in model_path or os.path.isdir(model_path):
        print("Format: HuggingFace Transformers")
        print("Compatible with: transformers, VLLM, text-generation-webui")
    else:
        print("Format: Unknown")
    
    # Try to get more info for GGUF files
    if model_path.endswith('.gguf'):
        try:
            # This would require llama-cpp-python for detailed GGUF info
            print("\\nFor detailed GGUF metadata, install llama-cpp-python")
        except:
            pass

def list_available_models():
    """List available models in the models directory."""
    models_dir = "./models"
    
    print("📋 Available Models")
    print("=" * 50)
    
    if not os.path.exists(models_dir):
        print("No models directory found")
        return
    
    models = []
    for root, dirs, files in os.walk(models_dir):
        for file in files:
            if file.endswith(('.gguf', '.bin', '.safetensors')) or 'pytorch_model' in file:
                full_path = os.path.join(root, file)
                size = os.path.getsize(full_path) / 1024**3
                models.append((full_path, size))
    
    if not models:
        print("No models found in ./models/")
        print("\\nTo download models:")
        print("  python model_manager.py download --type quantized")
        print("  python model_manager.py download --type original")
    else:
        for model_path, size in models:
            rel_path = os.path.relpath(model_path)
            print(f"  {rel_path} ({size:.2f} GB)")

def system_info():
    """Display system information."""
    print("💻 System Information")
    print("=" * 50)
    
    # GPU info
    has_gpu, gpu_name, gpu_memory = check_gpu()
    if has_gpu:
        print(f"GPU: {gpu_name}")
        print(f"GPU Memory: {gpu_memory:.1f} GB")
        print("GPU Status: ✅ CUDA Available")
    else:
        print("GPU Status: ❌ No CUDA GPU detected")
    
    # Memory info
    try:
        import psutil
        memory = psutil.virtual_memory()
        print(f"System RAM: {memory.total / 1024**3:.1f} GB")
        print(f"Available RAM: {memory.available / 1024**3:.1f} GB")
    except ImportError:
        print("RAM: Install psutil for memory info")
    
    # Ollama status
    if check_ollama_installed():
        print("Ollama: ✅ Installed")
        
        try:
            response = requests.get("http://127.0.0.1:11434/api/tags", timeout=2)
            if response.status_code == 200:
                print("Ollama Server: ✅ Running")
                data = response.json()
                models = data.get('models', [])
                print(f"Ollama Models: {len(models)} available")
                for model in models:
                    print(f"  - {model['name']}")
            else:
                print("Ollama Server: ❌ Not running")
        except:
            print("Ollama Server: ❌ Not running")
    else:
        print("Ollama: ❌ Not installed")
    
    # Python packages
    packages = ['torch', 'transformers', 'vllm', 'datasets', 'openai']
    print("\\nPython Packages:")
    for package in packages:
        try:
            __import__(package)
            print(f"  {package}: ✅")
        except ImportError:
            print(f"  {package}: ❌")

def main():
    parser = argparse.ArgumentParser(description="Arcee Agent Model Manager")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Download command
    download_parser = subparsers.add_parser('download', help='Download models')
    download_parser.add_argument('--type', choices=['quantized', 'original'], 
                               required=True, help='Model type to download')
    download_parser.add_argument('--output_dir', default='./models', 
                               help='Output directory')
    
    # Serve command
    serve_parser = subparsers.add_parser('serve', help='Start model server')
    serve_parser.add_argument('--type', choices=['ollama', 'vllm'], 
                            required=True, help='Server type')
    serve_parser.add_argument('--model_path', help='Path to model (for VLLM)')
    serve_parser.add_argument('--port', type=int, default=8000, 
                            help='Port for VLLM server')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show model information')
    info_parser.add_argument('--model_path', help='Path to model file')
    
    # List command
    subparsers.add_parser('list', help='List available models')
    
    # System command
    subparsers.add_parser('system', help='Show system information')
    
    # Setup command
    subparsers.add_parser('setup', help='Setup Ollama with Arcee Agent')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'download':
        if args.type == 'quantized':
            download_quantized_model(args.output_dir)
        elif args.type == 'original':
            download_original_model(args.output_dir)
    
    elif args.command == 'serve':
        if args.type == 'ollama':
            if setup_ollama():
                start_ollama_server()
        elif args.type == 'vllm':
            start_vllm_server(args.model_path, args.port)
    
    elif args.command == 'info':
        if args.model_path:
            get_model_info(args.model_path)
        else:
            print("Please specify --model_path")
    
    elif args.command == 'list':
        list_available_models()
    
    elif args.command == 'system':
        system_info()
    
    elif args.command == 'setup':
        setup_ollama()

if __name__ == "__main__":
    main()
