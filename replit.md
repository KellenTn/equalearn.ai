# Overview

Solvely Lite is an offline math problem solver application built with FastAPI and modern web technologies. The application provides two primary input methods: direct text input and image upload with OCR (Optical Character Recognition) capabilities. It processes mathematical problems and returns formatted solutions using LaTeX rendering via KaTeX. The system is designed to run completely offline without requiring external API calls or user authentication.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
The frontend uses a single-page application (SPA) approach with vanilla JavaScript, HTML5, and CSS3. Bootstrap 5 with Replit's dark theme provides the UI framework, while KaTeX handles client-side LaTeX mathematical notation rendering. The application features a responsive design with two main input panels - text input and image upload with OCR.

## Backend Architecture
The backend is built on FastAPI, a modern Python web framework that provides automatic API documentation and high performance. The application follows a simple request-response pattern with two main endpoints: `/solve_text` for processing text-based math problems and image upload handling for OCR processing. The architecture includes template rendering using Jinja2 for serving the main HTML interface.

## Data Processing Pipeline
Mathematical problem solving currently uses a simulation layer that will be replaced with local LLM inference in production. The system processes text input directly or extracts text from uploaded images using Tesseract OCR. Solutions are formatted as LaTeX expressions and rendered client-side using KaTeX for mathematical notation display.

## File Structure
The application follows a standard web application structure with separate directories for templates, static assets, and the main application logic. Static files include CSS, JavaScript, and potential KaTeX assets, while templates contain the HTML interface. The main application logic resides in the root-level Python files.

## Security and Privacy
The application operates entirely offline with no user authentication, session management, or data persistence. This design ensures complete privacy as no user data is stored or transmitted to external services. All processing occurs locally on the server instance.

# External Dependencies

## Core Framework Dependencies
- **FastAPI**: Modern Python web framework for building APIs with automatic documentation
- **Uvicorn**: ASGI server for running the FastAPI application
- **Jinja2Templates**: Template engine for rendering HTML responses
- **Python-multipart**: Handles file uploads and form data processing

## Image Processing Dependencies
- **Pytesseract**: Python wrapper for Tesseract OCR engine for text extraction from images
- **Pillow (PIL)**: Python Imaging Library for image processing and manipulation

## Frontend Dependencies
- **Bootstrap 5**: CSS framework with Replit's dark theme integration via CDN
- **KaTeX**: Fast math typesetting library for rendering LaTeX mathematical notation via CDN
- **Feather Icons**: Icon library for UI elements via CDN

## System Dependencies
- **Tesseract OCR**: System-level OCR engine that requires installation on the host system for image text extraction functionality

## Future Integration Points
The architecture is designed to accommodate local LLM integration (such as Ollama with Gemma models) for actual mathematical problem solving, replacing the current simulation layer. The modular design allows for easy integration of additional mathematical computation libraries or AI models without significant architectural changes.