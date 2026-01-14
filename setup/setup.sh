#!/bin/bash

# Setup script for Sanskrit RAG System
# Works on macOS and Linux

set -e  # Exit on error

echo "🚀 Setting up Sanskrit RAG System..."
echo ""

# Check Python version
echo "📋 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Found Python $PYTHON_VERSION"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping..."
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet
echo "✅ Pip upgraded"
echo ""

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r code/requirements.txt --quiet
echo "✅ Dependencies installed"
echo ""

# Check for model file
echo "🤖 Checking for model file..."
if [ -f "models/tinyllama.gguf" ]; then
    MODEL_SIZE=$(ls -lh models/tinyllama.gguf | awk '{print $5}')
    echo "✅ Model file found ($MODEL_SIZE)"
else
    echo "⚠️  Model file NOT found!"
    echo ""
    echo "📥 Please download the model file:"
    echo "   1. Visit: https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF"
    echo "   2. Download: tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
    echo "   3. Rename to: tinyllama.gguf"
    echo "   4. Place in: models/tinyllama.gguf"
    echo ""
fi
echo ""

# Run test
echo "🧪 Running system test..."
echo ""
python code/main.py --test

echo ""
echo "✅ Setup complete!"
echo ""
echo "📖 Next steps:"
echo "   • To use CLI: python code/main.py"
echo "   • To use Web UI: streamlit run app.py"
echo "   • For help: see README.md or SETUP.md"
echo ""
