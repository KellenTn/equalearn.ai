# Overview

Solvely Lite is a completely offline math problem solver application built with Flask and modern web technologies. The application provides two primary input methods: direct text input and image upload with OCR (Optical Character Recognition) capabilities. It processes mathematical problems using a mandatory local Ollama + Gemma 3n model installation and returns formatted solutions using LaTeX rendering via KaTeX. The system requires a local Ollama instance running with Gemma 3n model and operates entirely without network connectivity. No fallback mechanisms are provided - the system only functions with proper local AI setup.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
The frontend uses a single-page application (SPA) approach with vanilla JavaScript, HTML5, and CSS3. Bootstrap 5 with Replit's dark theme provides the UI framework, while KaTeX handles client-side LaTeX mathematical notation rendering. The application features a responsive design with two main input panels - text input and image upload with OCR.

## Backend Architecture
The backend is built on Flask, a lightweight Python web framework that provides excellent WSGI compatibility with Gunicorn. The application follows a REST API pattern with main endpoints: `/solve_text` for processing text-based math problems, `/solve_image` for OCR processing, and `/test_ollama_connection` for testing local AI integration. The architecture includes template rendering using Jinja2 for serving the main HTML interface and features intelligent API fallbacks.

## Data Processing Pipeline
Mathematical problem solving features dual-mode operation: primary integration with local Ollama + Gemma 3n model for authentic mathematical solutions, with intelligent fallback to simulation when the local AI is unavailable. The system processes text input directly or extracts text from uploaded images using Tesseract OCR. Solutions are formatted as LaTeX expressions and rendered client-side using KaTeX for mathematical notation display. The application provides clear visual indicators of solution source (AI vs simulation).

## File Structure
The application follows a standard web application structure with separate directories for templates, static assets, and the main application logic. Static files include CSS, JavaScript, and potential KaTeX assets, while templates contain the HTML interface. The main application logic resides in the root-level Python files.

## Security and Privacy
The application operates entirely offline with no user authentication, session management, or data persistence. This design ensures complete privacy as no user data is stored or transmitted to external services. All processing occurs locally on the server instance.

# External Dependencies

## Core Framework Dependencies
- **Flask**: Lightweight Python web framework for building web applications with WSGI compatibility
- **Gunicorn**: WSGI HTTP server for running the Flask application in production
- **Jinja2**: Template engine for rendering HTML responses
- **Werkzeug**: WSGI utilities for handling file uploads and form data processing
- **Requests**: HTTP library for communicating with external APIs (Ollama integration)

## Image Processing Dependencies
- **Pytesseract**: Python wrapper for Tesseract OCR engine for text extraction from images
- **Pillow (PIL)**: Python Imaging Library for image processing and manipulation

## Frontend Dependencies
- **Bootstrap 5**: CSS framework with Replit's dark theme integration via CDN
- **KaTeX**: Fast math typesetting library for rendering LaTeX mathematical notation via CDN
- **Feather Icons**: Icon library for UI elements via CDN

## System Dependencies
- **Tesseract OCR**: System-level OCR engine that requires installation on the host system for image text extraction functionality

## Local AI Integration
The application features mandatory integration with local Ollama + Gemma 3n models for authentic mathematical problem solving. The system is hardcoded to use localhost:11434 API endpoint only, ensuring complete offline operation. The system includes connection testing and comprehensive error handling with setup guidance when the local AI is unavailable. No fallback mechanisms are provided - the application requires proper local Ollama installation with Gemma 3n model to function. The modular design allows for easy integration of additional mathematical computation libraries or AI models without significant architectural changes.

## Recent Changes (August 2025)
- Migrated from FastAPI to Flask for better WSGI/Gunicorn compatibility
- Implemented mandatory local-only Ollama + Gemma 3n integration (no network fallbacks)
- Fixed API endpoints to localhost only (http://localhost:11434) for complete offline operation
- Removed all simulation fallback mechanisms to ensure only authentic AI solutions
- Enhanced error handling to guide users for proper local Ollama setup
- Added Chinese language interface elements for local usage
- Updated UI to reflect local-only operation requirements