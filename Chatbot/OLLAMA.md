# Ollama Inference Server Setup Guide

This guide covers setting up Ollama for local LLM inference with Llama 3.x models.

## Overview

The RAG Chatbot supports **Llama 3.x models** from Meta AI through multiple deployment options:

1. **AWS SageMaker** - Cloud-hosted inference with `meta-textgeneration-llama-3-8b-instruct`
2. **Ollama** - Local inference server for development and privacy-focused deployments
3. **Hugging Face Integration** - Direct model loading from Hugging Face Hub

## Ollama Local Inference Server

### What is Ollama?

Ollama is a local inference server that runs Large Language Models on your machine. It provides:
- **Easy model management** - Download and run models with simple commands
- **REST API** - Standard HTTP endpoints for integration
- **Optimized performance** - Efficient CPU and GPU utilization
- **Privacy** - All inference happens locally

### Installation

#### Option 1: Direct Installation (Recommended)

**Linux/macOS:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download the installer from [ollama.ai](https://ollama.ai/download)

#### Option 2: Docker Installation

```bash
# Pull Ollama Docker image
docker pull ollama/ollama

# Run Ollama container
docker run -d \
  --name ollama \
  -p 11434:11434 \
  -v ollama:/root/.ollama \
  ollama/ollama

# Start the server
docker exec -it ollama ollama serve
```

### Starting Ollama Server

```bash
# Start Ollama server
ollama serve

# Server will be available at http://localhost:11434
# You should see: "Ollama is running"
```

### Downloading Llama 3.x Models

The chatbot supports multiple Llama 3.x variants:

#### Llama 3.1 Models (Recommended)

```bash
# Llama 3.1 8B Instruct (Recommended for most use cases)
ollama pull llama3.1:8b-instruct

# Llama 3.1 70B Instruct (Better quality, requires more resources)
ollama pull llama3.1:70b-instruct

# Llama 3.1 8B Base (For fine-tuning)
ollama pull llama3.1:8b
```

#### Llama 3.2 Models (Latest)

```bash
# Llama 3.2 3B (Lightweight, fast inference)
ollama pull llama3.2:3b

# Llama 3.2 11B Vision (Multimodal capabilities)
ollama pull llama3.2:11b

# Llama 3.2 90B Vision (Best quality, requires substantial resources)
ollama pull llama3.2:90b
```

#### Llama 3.0 Models (Original)

```bash
# Llama 3 8B Instruct
ollama pull llama3:8b-instruct

# Llama 3 70B Instruct
ollama pull llama3:70b-instruct
```

### Model Selection Guide

| Model | Size | RAM Requirement | Use Case |
|-------|------|----------------|----------|
| `llama3.2:3b` | 3B | 4GB | Lightweight, fast responses |
| `llama3.1:8b-instruct` | 8B | 8GB | **Recommended** - Good balance |
| `llama3.2:11b` | 11B | 12GB | Vision capabilities |
| `llama3.1:70b-instruct` | 70B | 40GB+ | Best quality, slow |
| `llama3.2:90b` | 90B | 60GB+ | Highest quality, vision |

### Configuration

#### Environment Variables

Update your `.env` file:

```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL_NAME=llama3.1:8b-instruct
OLLAMA_TIMEOUT=300

# Use Ollama for local inference
LLM_TYPE=ollama  # Set to 'sagemaker' for AWS deployment
```

#### Programmatic Configuration

```python
from src.ollama_integration import OllamaLLM
from src.vector_database import VectorDatabase

# Initialize with specific Llama model
llm = OllamaLLM(model_name="llama3.1:8b-instruct")

# Check model info
model_info = llm.get_model_info()
print(f"Model: {model_info['name']}")
print(f"Size: {model_info['size']}")
```

### Testing Ollama Integration

#### 1. Test Server Connection

```bash
# Check if server is running
curl http://localhost:11434/api/tags

# Should return JSON with available models
```

#### 2. Test Model Generation

```bash
# Test model directly
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.1:8b-instruct",
  "prompt": "Why is the sky blue?"
}'
```

#### 3. Test RAG Integration

```python
# Run the test script
python -c "
from src.ollama_integration import OllamaLLM
from langchain.schema import Document

# Create test documents
docs = [Document(page_content='The sky appears blue due to Rayleigh scattering.')]

# Test RAG response
llm = OllamaLLM('llama3.1:8b-instruct')
response = llm.generate_response('Why is the sky blue?', docs)
print(response)
"
```

### Prompt Templates and RAG Integration

#### System Prompt Template

The chatbot uses specialized prompts optimized for Llama 3.x models:

```python
SYSTEM_PROMPT = """You are a helpful AI assistant that answers questions based on provided context documents. 
Always cite the document number when referencing information. 
If the answer cannot be found in the context, clearly state that."""

USER_PROMPT = """Context Documents:
{context}

Question: {query}

Please answer based on the provided context:"""
```

#### RAG Pipeline with Ollama

```python
from src.ollama_integration import OllamaLLM
from src.vector_database import VectorDatabase
from src.llm_integration import RAGPipeline

# Initialize components
vector_db = VectorDatabase("chroma")
llm = OllamaLLM("llama3.1:8b-instruct")

# Create RAG pipeline
rag = RAGPipeline(vector_db, llm)

# Query with context retrieval
response = rag.query("What is machine learning?")
print(f"Answer: {response['answer']}")
print(f"Sources: {len(response['sources'])}")
```

### Performance Optimization

#### GPU Acceleration

For NVIDIA GPUs:

```bash
# Install CUDA support for Ollama
# Ollama automatically detects CUDA if available

# Verify GPU usage
nvidia-smi  # Check GPU utilization during inference
```

#### Memory Management

```bash
# Monitor Ollama memory usage
docker stats ollama  # If using Docker

# For direct installation
htop  # Check system memory usage
```

#### Model Optimization

```bash
# Use quantized models for better performance
ollama pull llama3.1:8b-instruct-q4_0  # 4-bit quantization
ollama pull llama3.1:8b-instruct-q8_0  # 8-bit quantization
```

### Troubleshooting

#### Common Issues

1. **Server not starting:**
   ```bash
   # Check if port 11434 is available
   lsof -i :11434
   
   # Kill existing processes if needed
   pkill -f ollama
   ```

2. **Model download fails:**
   ```bash
   # Check internet connection and disk space
   df -h
   
   # Retry download
   ollama pull llama3.1:8b-instruct
   ```

3. **Out of memory errors:**
   ```bash
   # Use smaller model
   ollama pull llama3.2:3b
   
   # Or configure swap space
   sudo swapon --show
   ```

4. **Slow inference:**
   ```bash
   # Check GPU availability
   nvidia-smi
   
   # Use quantized models
   ollama pull llama3.1:8b-instruct-q4_0
   ```

#### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Test with debug output
from src.ollama_integration import OllamaLLM
llm = OllamaLLM("llama3.1:8b-instruct")
```

### Production Deployment

#### Docker Compose Setup

```yaml
version: '3.8'
services:
  ollama:
    image: ollama/ollama
    container_name: ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_models:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0
      - OLLAMA_PORT=11434
    restart: unless-stopped
    
  rag-chatbot:
    build: .
    container_name: rag-chatbot
    ports:
      - "8000:8000"
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - OLLAMA_MODEL_NAME=llama3.1:8b-instruct
    depends_on:
      - ollama
    restart: unless-stopped

volumes:
  ollama_models:
```

#### Model Preloading

```bash
# Create model initialization script
cat > init-models.sh << 'EOF'
#!/bin/bash
ollama serve &
sleep 10
ollama pull llama3.1:8b-instruct
wait
EOF

chmod +x init-models.sh
./init-models.sh
```

### API Reference

#### Ollama REST API Endpoints

- `GET /api/tags` - List available models
- `POST /api/pull` - Download a model
- `POST /api/generate` - Generate text
- `POST /api/chat` - Chat conversation
- `DELETE /api/delete` - Remove a model

#### Python Integration

```python
from src.ollama_integration import OllamaClient, OllamaLLM, SUPPORTED_LLAMA3_MODELS

# Direct client usage
client = OllamaClient()
models = client.list_models()

# RAG integration
llm = OllamaLLM("llama3.1:8b-instruct")
response = llm.generate_response(query, context_docs)

# Get model recommendations
recommended = get_recommended_model("chat")  # Returns "llama3.1:8b-instruct"
```

This setup provides a complete local inference solution using Llama 3.x models with optimized prompts and templates for RAG applications.
