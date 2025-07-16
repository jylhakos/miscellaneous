#!/bin/bash

# Enhanced Setup script for Arcee Agent Function Calling Project

echo "🚀 Setting up Arcee Agent Function Calling environment..."
echo "================================================================"

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry not found. Please install poetry first:"
    echo "curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

echo "✅ Poetry found"

# Install core dependencies
echo "📦 Installing core dependencies with poetry..."
poetry install --no-dev

# Install additional packages for the project
echo "📦 Installing additional Python packages..."
poetry add openai datasets huggingface_hub transformers torch tqdm

# Install optional packages for advanced features
read -p "Install advanced packages for fine-tuning and serving? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📦 Installing advanced packages..."
    poetry add peft bitsandbytes accelerate
    
    # Try to install VLLM (might fail on some systems)
    echo "📦 Attempting to install VLLM..."
    poetry add vllm || echo "⚠️  VLLM installation failed. Install manually if needed: pip install vllm"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p models
mkdir -p logs
mkdir -p fine_tuned_models

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x main.py
chmod +x test_arcee_agent.py
chmod +x test_api.py
chmod +x fine_tune_arcee.py
chmod +x model_manager.py
chmod +x demo_ollama.py

# Check system capabilities
echo "💻 Checking system capabilities..."
python3 -c "
import torch
print(f'PyTorch version: {torch.__version__}')
if torch.cuda.is_available():
    print(f'✅ CUDA available: {torch.cuda.get_device_name(0)}')
    print(f'   GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')
else:
    print('❌ CUDA not available')
"

# Check if Ollama is installed
if command -v ollama &> /dev/null; then
    echo "✅ Ollama found"
    
    read -p "Setup Ollama with Arcee Agent model? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔧 Setting up Ollama..."
        python model_manager.py setup
    fi
else
    echo "❌ Ollama not found"
    echo "💡 Install Ollama from https://ollama.ai/ for easy local deployment"
fi

# Download the quantized Arcee Agent model (optional)
read -p "Download the quantized Arcee Agent model (~4.3GB)? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📥 Downloading quantized Arcee Agent model..."
    python model_manager.py download --type quantized
fi

# Run tests
echo "🧪 Running test suite..."
python test_arcee_agent.py

echo ""
echo "🎉 Setup complete!"
echo "================================================================"
echo ""
echo "📋 Quick Start Guide:"
echo ""
echo "1. Test everything is working:"
echo "   python test_arcee_agent.py"
echo ""
echo "2. Check system status:"
echo "   python model_manager.py system"
echo ""
echo "3. List available models:"
echo "   python model_manager.py list"
echo ""
echo "4. Start with Ollama (easiest):"
echo "   python demo_ollama.py"
echo ""
echo "5. Or use the main script:"
echo "   python main.py --model arcee-ai/arcee-agent --base_url http://127.0.0.1:11434/v1 --max_samples 5"
echo ""
echo "6. For VLLM server (production):"
echo "   python model_manager.py serve --type vllm"
echo "   # Then in another terminal:"
echo "   python main.py --model arcee-ai/Arcee-Agent --base_url http://127.0.0.1:8000/v1 --max_samples 5"
echo ""
echo "7. Fine-tune on your dataset:"
echo "   python fine_tune_arcee.py --dataset_path ./dataset --num_epochs 3"
echo ""
echo "📖 Full documentation: README.md"
echo "🔧 Advanced features: IMPLEMENTATION_COMPLETE.md"
