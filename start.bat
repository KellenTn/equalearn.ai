@echo off
chcp 65001 >nul
echo 🚀 equalearn.ai. - Local AI Math Tutor Startup Script
echo ====================================================

REM Check Python version
echo 📋 Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not installed or not in PATH
    pause
    exit /b 1
)

REM Check Ollama
echo 📋 Checking Ollama...
ollama --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Ollama not installed, please install Ollama first
    echo    Download: https://ollama.ai/download/windows
    pause
    exit /b 1
)

REM Check Ollama service
echo 📋 Checking Ollama service...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Ollama service not running, please start Ollama first
    echo    Run command: ollama serve
    pause
    exit /b 1
)

REM Check Gemma 3 4B model
echo 📋 Checking Gemma 3 4B model...
ollama list | findstr "gemma3:4b" >nul
if errorlevel 1 (
    echo ⚠️  Gemma 3 4B model not installed, downloading...
    ollama pull gemma3:4b
)

REM Install Python dependencies
echo 📋 Installing Python dependencies...
pip install -r requirements.txt

REM Create upload directory
if not exist uploads mkdir uploads

REM Start application
echo 🚀 Starting equalearn.ai. application...
echo 📱 Access URL: http://localhost:8080
echo 🛑 Press Ctrl+C to stop application
echo.

python app.py
pause 