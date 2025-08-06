#!/bin/bash

echo "🚀 equalearn.ai. - Local AI Math Tutor Startup Script"
echo "===================================================="

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
if [[ $(echo "$python_version >= 3.11" | bc -l) -eq 1 ]]; then
    echo "✅ Python version: $python_version (meets requirements)"
else
    echo "❌ Python version too low, requires 3.11 or higher"
    exit 1
fi

# Check Ollama
echo "📋 Checking Ollama..."
if command -v ollama &> /dev/null; then
    echo "✅ Ollama installed"
    
    # Check Ollama service status
    if curl -s http://localhost:11434/api/tags > /dev/null; then
        echo "✅ Ollama service running"
        
        # Check Gemma 3 4B model
        if ollama list | grep -q "gemma3:4b"; then
            echo "✅ Gemma 3 4B model installed"
        else
            echo "⚠️  Gemma 3 4B model not installed, downloading..."
            ollama pull gemma3:4b
        fi
    else
        echo "⚠️  Ollama service not running, starting..."
        ollama serve &
        sleep 5
    fi
else
    echo "❌ Ollama not installed, please install Ollama first:"
    echo "   curl -fsSL https://ollama.ai/install.sh | sh"
    exit 1
fi

# Check Tesseract
echo "📋 Checking Tesseract OCR..."
if command -v tesseract &> /dev/null; then
    echo "✅ Tesseract installed"
else
    echo "⚠️  Tesseract not installed, please install Tesseract OCR"
    echo "   macOS: brew install tesseract tesseract-lang"
    echo "   Ubuntu: sudo apt install tesseract-ocr tesseract-ocr-eng"
fi

# Check FFmpeg
echo "📋 Checking FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    echo "✅ FFmpeg installed"
else
    echo "⚠️  FFmpeg not installed, audio processing may not work"
    echo "   macOS: brew install ffmpeg"
    echo "   Ubuntu: sudo apt install ffmpeg"
fi

# Install Python dependencies
echo "📋 Installing Python dependencies..."
if command -v uv &> /dev/null; then
    echo "Using uv to install dependencies..."
    uv sync
else
    echo "Using pip to install dependencies..."
    pip install -r requirements.txt
fi

# Create upload directory
mkdir -p uploads

# Start application
echo "🚀 Starting equalearn.ai. application..."
echo "📱 Access URL: http://localhost:8080"
echo "🛑 Press Ctrl+C to stop application"
echo ""

python3 app.py 