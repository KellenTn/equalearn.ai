# Contributing to equalearn.ai.

Thank you for your interest in contributing to equalearn.ai.! This document provides guidelines for contributing to the project.

## Mission

equalearn.ai. is dedicated to eliminating educational inequality and achieving equal educational resources through AI technology.

## How to Contribute

### 1. Fork the Repository

1. Go to the [equalearn.ai. repository](https://github.com/yourusername/equalearn.ai.)
2. Click the "Fork" button in the top right corner
3. Clone your forked repository to your local machine

### 2. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 3. Make Your Changes

- Follow the existing code style and conventions
- Add comments to explain complex logic
- Update documentation if needed
- Test your changes thoroughly

### 4. Commit Your Changes

```bash
git add .
git commit -m "feat: add your feature description"
```

### 5. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 6. Create a Pull Request

1. Go to your forked repository on GitHub
2. Click "New Pull Request"
3. Select your feature branch
4. Fill out the pull request template
5. Submit the pull request

## Development Setup

### Prerequisites

- Python 3.11+
- Ollama
- Tesseract OCR (for image processing)
- FFmpeg (for audio/video processing)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/equalearn.ai..git
cd equalearn.ai.
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install system dependencies:
```bash
# macOS
brew install tesseract ffmpeg

# Ubuntu/Debian
sudo apt install tesseract-ocr ffmpeg

# Windows
# Download from official websites
```

4. Install Ollama and download the model:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull gemma3:4b
```

5. Start the application:
```bash
python3 app.py
```

## Code Style

- Use meaningful variable and function names
- Add docstrings to functions and classes
- Follow PEP 8 style guidelines
- Keep functions small and focused
- Write clear commit messages

## Testing

Before submitting a pull request, please ensure:

1. All existing tests pass
2. New tests are added for new features
3. The application runs without errors
4. All features work as expected

## Reporting Issues

When reporting issues, please include:

1. Operating system and version
2. Python version
3. Steps to reproduce the issue
4. Expected vs actual behavior
5. Error messages (if any)

## Feature Requests

When requesting features, please:

1. Explain the problem you're trying to solve
2. Describe your proposed solution
3. Consider the impact on educational equality
4. Provide examples if possible

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please be respectful and considerate in all interactions.

## License

By contributing to equalearn.ai., you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to educational equality! 🌟 