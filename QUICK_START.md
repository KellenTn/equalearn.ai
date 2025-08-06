# 🚀 Solvely Lite Quick Start Guide

## 5-Minute Quick Start

### 1. Install Ollama

```bash
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# Download and install: https://ollama.ai/download/windows
```

### 2. Download Model

```bash
ollama pull gemma3:4b
```

### 3. Start Ollama

```bash
ollama serve
```

### 4. Run Application

#### Method 1: Using Startup Script (Recommended)

```bash
# macOS/Linux
./start.sh

# Windows
start.bat
```

#### Method 2: Manual Startup

```bash
# Install dependencies
pip install -r requirements.txt

# Start application
python app.py
```

### 5. Access Application

Open your browser and visit: http://localhost:8080

## Feature Demo

### 📝 Text Input

1. Enter in text box: `Solve the equation 2x + 3 = 7`
2. Click "Solve Problem"
3. View detailed solution steps

### 🎤 Voice Input

1. Click the microphone button
2. Speak the math problem
3. Voice automatically converts to text

### 📷 Image Upload

1. Drag math problem image to upload area
2. System automatically performs OCR recognition
3. Click "Solve This Problem"

### 📚 Generate Practice Problems

1. Enter a math problem
2. Click "Generate Practice"
3. Get 3 related practice problems

## Common Questions

### Q: "Ollama connection failed" error

A: Ensure Ollama service is running: `ollama serve`

### Q: "Gemma 3 4B model not found" error

A: Download the model: `ollama pull gemma3:4b`

### Q: Voice input not working

A: Ensure browser supports speech recognition and allow microphone permissions

### Q: Image OCR recognition failed

A: Ensure image is clear with readable text

## System Requirements

- **Memory**: 8GB+ RAM
- **Storage**: 10GB+ available space
- **Network**: Only needed for initial model download

## Supported Formats

- **Images**: PNG, JPG, JPEG, GIF, BMP, WebP
- **Videos**: MP4, AVI, MOV, WMV, WebM
- **Audio**: WAV, MP3, M4A, OGG

## Language Support

- **Interface**: English
- **Voice**: English
- **OCR**: English

---

🎉 **Start using your local AI math tutor now!**
