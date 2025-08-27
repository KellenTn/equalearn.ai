# equalearn.ai. - Local AI Tutor Aiming to remove the learning inequality for the whole human society 

An AI tutor dedicated to eliminating inequality and achieving equal educational resources, using local Ollama + Gemma 3n model.

## Features

### 🎯 Core Features

- **Completely Offline** - No internet connection required, privacy protected
- **Multiple Input Methods** - Support for text, image, video, and voice input
- **Detailed Step-by-Step Solutions** - AI generates detailed mathematical solution steps
- **Practice Problem Generation** - Generate related practice problems based on original questions
- **LaTeX Rendering** - Beautiful mathematical notation display

### 📱 Input Methods

1. **Text Input** - Directly input math problems
2. **Voice Input** - Speech-to-text conversion (English)
3. **Image Upload** - OCR recognition of math problems in images
4. **Video Upload** - Extract text from video frames
5. **Audio Upload** - Convert audio files to text

### 🤖 AI Features

- **Solution Steps** - Detailed step-by-step explanations
- **Practice Problem Generation** - Generate 3 practice problems with increasing difficulty
- **English Support** - Full English interface and solutions
- **LaTeX Format** - Professional mathematical formula typesetting

## System Requirements

### Hardware Requirements

- **Memory**: At least 8GB RAM (16GB+ recommended)
- **Storage**: At least 10GB available space
- **CPU**: Support for AVX2 instruction set (most modern CPUs)

### Software Requirements

- **Operating System**: macOS, Linux, Windows
- **Python**: 3.11+
- **Ollama**: Latest version

## Installation Steps

### 1. Install Ollama

#### macOS

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### Linux

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### Windows

Download and install [Ollama for Windows](https://ollama.ai/download/windows)

### 2. Download Gemma 3 4B Model

```bash
ollama pull gemma3:4b
```

### 3. Start Ollama Service

```bash
ollama serve
```

### 4. Install Python Dependencies

#### Using uv (Recommended)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

#### Using pip

```bash
pip install -r requirements.txt
```

### 5. Install System Dependencies

#### macOS

```bash
# Install Tesseract OCR
brew install tesseract tesseract-lang

# Install FFmpeg (for audio processing)
brew install ffmpeg
```

#### Ubuntu/Debian

```bash
# Install Tesseract OCR
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-eng

# Install FFmpeg
sudo apt install ffmpeg

# Install OpenCV dependencies
sudo apt install libgl1-mesa-glx libglib2.0-0
```

#### Windows

- Download and install [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)
- Download and install [FFmpeg](https://ffmpeg.org/download.html)

## Usage

### 1. Start the Application

```bash
python app.py
```

### 2. Access the Application

Open your browser and visit: http://localhost:8080

### 3. Using Features

#### Text Input

1. Enter a math problem in the text box
2. Click "Solve Problem" button
3. View detailed solution steps

#### Voice Input

1. Click the microphone button
2. Speak the math problem
3. Voice automatically converts to text

#### Image/Video/Audio Upload

1. Drag and drop files to the upload area or click to select files
2. Files are automatically processed and text is extracted
3. Click "Solve This Problem" button

#### Generate Practice Problems

1. Enter a math problem
2. Click "Generate Practice" button
3. View 3 generated practice problems

## Configuration

### Model Configuration

- **Model**: Gemma 3 4B (default)
- **API Address**: http://localhost:11434
- **Timeout**: 120 seconds

### File Upload Limits

- **Maximum File Size**: 32MB
- **Supported Formats**:
  - Images: PNG, JPG, JPEG, GIF, BMP, WebP
  - Videos: MP4, AVI, MOV, WMV, WebM
  - Audio: WAV, MP3, M4A, OGG

### Language Support

- **Interface Language**: English
- **Voice Recognition**: English
- **OCR Recognition**: English

## Troubleshooting

### Ollama Connection Issues

```bash
# Check Ollama service status
ollama list

# Restart Ollama service
ollama serve

# Check if model is downloaded
ollama pull gemma:3n
```

### OCR Recognition Issues

```bash
# Check Tesseract installation
tesseract --version

# Check language packs
tesseract --list-langs
```

### Audio Processing Issues

```bash
# Check FFmpeg installation
ffmpeg -version
```

### Common Errors

1. **"Cannot connect to local Ollama"**

   - Ensure Ollama service is running
   - Check if port 11434 is occupied

2. **"Gemma 3 4B model not found"**

   - Run `ollama pull gemma3:4b`
   - Wait for download to complete

3. **"OCR failed"**

   - Ensure Tesseract is properly installed
   - Check image clarity

4. **"Speech recognition error"**

   - Ensure browser supports speech recognition
   - Check microphone permissions

## Development

### Project Structure

```
1-2/
├── app.py              # Main application file
├── templates/          # HTML templates
│   └── index.html
├── static/            # Static files
│   ├── app.js
│   └── style.css
├── uploads/           # Upload directory
├── pyproject.toml     # Project configuration
└── README.md          # Documentation
```

### API Endpoints

- `GET /` - Main page
- `POST /solve_text` - Text problem solving
- `POST /generate_practice` - Generate practice problems
- `POST /solve_image` - File processing
- `POST /test_ollama_connection` - Test connection
- `GET /health` - Health check

### Custom Configuration

You can modify the following configurations in `app.py`:

- `OLLAMA_MODEL` - Model to use
- `MAX_CONTENT_LENGTH` - File size limit
- `ALLOWED_EXTENSIONS` - Supported file formats

## License

MIT License

## Contributing

Welcome to submit Issues and Pull Requests!

## Changelog

### v1.0.0

- Initial version release
- Support for text, image, video, and voice input
- Integration with Ollama + Gemma 3 4B model
- Practice problem generation support
- English interface support
