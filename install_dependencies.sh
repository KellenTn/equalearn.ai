#!/bin/bash

echo "🔧 Installing dependencies for Solvely Lite..."
echo "=============================================="

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew is not installed."
    echo "📦 Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add Homebrew to PATH
    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
    source ~/.zshrc
else
    echo "✅ Homebrew is already installed"
fi

# Install Tesseract OCR
echo "📸 Installing Tesseract OCR..."
if ! command -v tesseract &> /dev/null; then
    brew install tesseract
    echo "✅ Tesseract installed successfully"
else
    echo "✅ Tesseract is already installed"
fi

# Install FFmpeg
echo "🎬 Installing FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    brew install ffmpeg
    echo "✅ FFmpeg installed successfully"
else
    echo "✅ FFmpeg is already installed"
fi

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip3 install -r requirements.txt

echo ""
echo "🎉 Installation complete!"
echo "=============================================="
echo "✅ Tesseract OCR - for image and video text extraction"
echo "✅ FFmpeg - for audio and video processing"
echo "✅ Python packages - for the application"
echo ""
echo "🚀 You can now start the application with:"
echo "   python3 app.py"
echo ""
echo "📝 Note: If you encounter any issues, please restart your terminal"
echo "   to ensure the new PATH settings are loaded." 