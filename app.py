import os
import io
import logging
import requests
import json
import base64
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import pytesseract
from PIL import Image
import cv2
import numpy as np
import tempfile
import wave
import audioop
from pydub import AudioSegment
import speech_recognition as sr
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'mp4', 'avi', 'mov', 'wmv', 'webm', 'wav', 'mp3', 'm4a', 'ogg'}
MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Create PDF output directory
PDF_OUTPUT_FOLDER = 'pdf_output'
os.makedirs(PDF_OUTPUT_FOLDER, exist_ok=True)

# Ollama API configuration - Only local instance supported
OLLAMA_API_URL = 'http://localhost:11434'  # Fixed to localhost only
OLLAMA_MODEL = 'gemma3:4b'  # Fixed to Gemma 3 4B model

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def parse_practice_problems_and_solutions(ai_response):
    """Parse AI response to extract practice problems and solutions"""
    try:
        calculation = []
        answers = []
        
        # Split the response into sections
        sections = ai_response.split('**')
        
        current_section = ""
        
        for section in sections:
            section = section.strip()
            if "Calculation Problems" in section:
                current_section = "calculation"
            elif "Answers:" in section:
                current_section = "answers"
            elif current_section and section:
                # Parse problems based on current section
                lines = section.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and line[0].isdigit():
                        # Extract problem number and content
                        parts = line.split('.', 1)
                        if len(parts) > 1:
                            problem_num = int(parts[0])
                            problem_content = parts[1].strip()
                            
                            if current_section == "calculation" and 1 <= problem_num <= 10:
                                calculation.append(problem_content)
                            elif current_section == "answers" and 1 <= problem_num <= 10:
                                answers.append(problem_content)
        
        # Ensure we have the right number of problems
        if len(calculation) < 10:
            calculation.extend([f"Calculation problem {i+1}" for i in range(len(calculation), 10)])
        if len(answers) < 10:
            answers.extend([f"Solution for problem {i+1}" for i in range(len(answers), 10)])
        
        return calculation[:10], answers[:10]
        
    except Exception as e:
        logger.error(f"Error parsing practice problems: {e}")
        # Return fallback problems and solutions
        calculation = [f"Calculation problem {i+1}" for i in range(10)]
        answers = [f"Solution for problem {i+1}" for i in range(10)]
        return calculation, answers

def generate_practice_pdf(original_problem, calculation, answers):
    """Generate a PDF worksheet with practice problems and solutions"""
    try:
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"practice_worksheet_{timestamp}.pdf"
        filepath = os.path.join(PDF_OUTPUT_FOLDER, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Create custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        problem_style = ParagraphStyle(
            'ProblemStyle',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=20,
            spaceBefore=10,
            leftIndent=20
        )
        
        answer_space_style = ParagraphStyle(
            'AnswerSpace',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=30,
            spaceBefore=10,
            leftIndent=40
        )
        
        solution_style = ParagraphStyle(
            'SolutionStyle',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=15,
            spaceBefore=10,
            leftIndent=20,
            textColor=colors.darkgreen
        )
        
        # Build PDF content
        story = []
        
        # Title
        story.append(Paragraph("Mathematics Practice Worksheet", title_style))
        story.append(Spacer(1, 20))
        
        # Original problem reference
        story.append(Paragraph(f"<b>Based on:</b> {original_problem}", problem_style))
        story.append(Spacer(1, 20))
        
        # Instructions
        story.append(Paragraph("<b>Instructions:</b> Answer all 10 calculation problems. Show your work and provide step-by-step solutions.", problem_style))
        story.append(Spacer(1, 30))
        
        # Calculation Problems
        story.append(Paragraph("<b>Calculation Problems (10 points each):</b>", problem_style))
        story.append(Spacer(1, 15))
        
        for i, problem in enumerate(calculation, 1):
            # Problem number and content - convert basic LaTeX to readable format
            problem_text = problem.replace('$', '').replace('\\frac{', '').replace('}', '').replace('\\sqrt{', '√').replace('\\int', '∫')
            story.append(Paragraph(f"<b>{i}.</b> {problem_text}", problem_style))
            
            # Answer space - just blank lines
            story.append(Paragraph("_________________________________", answer_space_style))
            story.append(Paragraph("_________________________________", answer_space_style))
            story.append(Paragraph("_________________________________", answer_space_style))
            story.append(Paragraph("_________________________________", answer_space_style))
            
            story.append(Spacer(1, 15))
        
        # Page break before answers
        story.append(PageBreak())
        
        # Answers section
        story.append(Paragraph("Answers", title_style))
        story.append(Spacer(1, 20))
        
        # Calculation answers
        story.append(Paragraph("<b>Problem Solutions:</b>", solution_style))
        for i in range(10):
            if i < len(answers):
                # Convert basic LaTeX to readable format for answers
                answer_text = answers[i].replace('$', '').replace('\\frac{', '').replace('}', '').replace('\\sqrt{', '√').replace('\\int', '∫')
                story.append(Paragraph(f"<b>{i+1}.</b> {answer_text}", solution_style))
                story.append(Spacer(1, 10))
        
        # Build PDF
        doc.build(story)
        
        return filename
        
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        return None

def extract_text_from_video(video_path):
    """Extract text from video frames using OCR"""
    try:
        # Check if tesseract is available
        try:
            import subprocess
            subprocess.run(['tesseract', '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "ERROR: Tesseract OCR is not installed. Please install tesseract to enable video text extraction."
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return "ERROR: Could not open video file."
        
        extracted_texts = []
        
        # Extract frames at regular intervals
        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            # Process every 30th frame (assuming 30fps, so every second)
            if frame_count % 30 == 0:
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(rgb_frame)
                
                # Extract text from frame
                try:
                    text = pytesseract.image_to_string(pil_image, lang='eng')
                    if text.strip():
                        extracted_texts.append(text.strip())
                except Exception as e:
                    logger.warning(f"OCR failed on frame {frame_count}: {e}")
            
            frame_count += 1
            
            # Limit to first 10 seconds to avoid long processing
            if frame_count > 300:  # 10 seconds at 30fps
                break
        
        cap.release()
        
        # Combine all extracted text
        combined_text = ' '.join(extracted_texts)
        if not combined_text.strip():
            return "No text found in video frames. Please ensure the video contains clear, readable text."
        return combined_text.strip()
        
    except Exception as e:
        logger.error(f"Error extracting text from video: {e}")
        return f"ERROR: Failed to process video: {str(e)}"

def process_audio_file(audio_file):
    """Convert audio file to text using speech recognition"""
    try:
        # Check if ffmpeg is available for audio conversion
        try:
            import subprocess
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "ERROR: FFmpeg is not installed. Please install ffmpeg to enable audio processing."
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            audio_file.save(temp_file.name)
            temp_path = temp_file.name
        
        try:
            # Convert to WAV if needed
            audio = AudioSegment.from_file(temp_path)
            wav_path = temp_path.replace('.wav', '_converted.wav')
            audio.export(wav_path, format='wav')
            
            # Use speech recognition
            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_path) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data, language='en-US')  # English only
                if not text.strip():
                    return "No speech detected in audio file. Please ensure the audio contains clear speech."
                return text
                
        finally:
            # Clean up temporary files
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            if os.path.exists(wav_path):
                os.unlink(wav_path)
                
    except sr.UnknownValueError:
        return "ERROR: Could not understand audio. Please ensure the audio contains clear speech."
    except sr.RequestError as e:
        return f"ERROR: Speech recognition service error: {str(e)}"
    except Exception as e:
        logger.error(f"Error processing audio: {e}")
        return f"ERROR: Failed to process audio: {str(e)}"

def call_ollama_api(text, mode="solve"):
    """
    Call the local Ollama API with different modes:
    - solve: Solve the math problem
    - practice: Generate practice problems
    """
    try:
        if mode == "solve":
            # Enhanced prompt for detailed step-by-step solutions
            enhanced_prompt = f"""You are a professional mathematics teacher. Please solve this math problem step by step with the following requirements:

1. Use LaTeX format for all mathematical formulas
2. Provide detailed step-by-step explanations with clear reasoning
3. Use \\begin{{align}} and \\end{{align}} to wrap multi-line mathematical expressions
4. Add clear explanations for each key step
5. Provide a clear final answer

Math Problem: {text}

Please begin solving:"""
        else:  # practice mode
            enhanced_prompt = f"""Based on this math problem, generate a comprehensive practice worksheet with the following requirements:

1. Generate exactly 10 calculation/solution problems (short answer questions)
2. Each problem should be clearly stated and solvable
3. Use simple LaTeX format for mathematical expressions
4. Diversify problem types and difficulty levels
5. All problems should require step-by-step solutions
6. Format the response as follows:

**Calculation Problems (10):**
1. [Question 1 with simple math expressions]
2. [Question 2 with simple math expressions]
3. [Question 3 with simple math expressions]
4. [Question 4 with simple math expressions]
5. [Question 5 with simple math expressions]
6. [Question 6 with simple math expressions]
7. [Question 7 with simple math expressions]
8. [Question 8 with simple math expressions]
9. [Question 9 with simple math expressions]
10. [Question 10 with simple math expressions]

**Answers:**
1. [Detailed step-by-step solution for Problem 1]
2. [Detailed step-by-step solution for Problem 2]
3. [Detailed step-by-step solution for Problem 3]
4. [Detailed step-by-step solution for Problem 4]
5. [Detailed step-by-step solution for Problem 5]
6. [Detailed step-by-step solution for Problem 6]
7. [Detailed step-by-step solution for Problem 7]
8. [Detailed step-by-step solution for Problem 8]
9. [Detailed step-by-step solution for Problem 9]
10. [Detailed step-by-step solution for Problem 10]

IMPORTANT: Use simple LaTeX format for mathematical expressions. For example:
- Use x^2 for x squared
- Use a/b for fractions
- Use sqrt(x) for square roots
- Use int f(x) dx for integrals
- Use d/dx for derivatives

Original Problem: {text}

Please generate 10 calculation problems with detailed solutions:"""
        
        response = requests.post(
            f"{OLLAMA_API_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": enhanced_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1 if mode == "solve" else 0.3,
                    "top_p": 0.9,
                    "num_predict": 2048
                }
            },
            timeout=300  # Increased timeout for complex problems
        )
        
        if response.status_code == 200:
            result = response.json()
            latex_response = result.get("response", "").strip()
            
            if latex_response:
                return {
                    "success": True,
                    "latex": latex_response,
                    "source": "ollama"
                }
            else:
                return {"success": False, "error": "Ollama returned empty response"}
        else:
            logger.error(f"Ollama API error: {response.status_code}")
            return {"success": False, "error": f"Ollama API error: {response.status_code}"}
            
    except requests.exceptions.Timeout:
        logger.error("Ollama API timeout")
        return {"success": False, "error": "Local Ollama response timeout. Please check system performance."}
    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to Ollama API")
        return {"success": False, "error": "Cannot connect to local Ollama. Please ensure Ollama is running with Gemma 3n model loaded."}
    except Exception as e:
        logger.error(f"Ollama API error: {str(e)}")
        return {"success": False, "error": f"Ollama error: {str(e)}"}

@app.route('/')
def home():
    """Serve the main application page"""
    return render_template('index.html')

@app.route('/debug')
def debug():
    """Serve the debug page"""
    return send_from_directory('.', 'debug.html')

@app.route('/test_frontend')
def test_frontend():
    """Serve the frontend test page"""
    return send_from_directory('.', 'test_frontend.html')

@app.route('/test_solution_format')
def test_solution_format():
    """Serve the solution format test page"""
    return send_from_directory('.', 'test_solution_format.html')

@app.route('/demo_steps')
def demo_steps():
    """Serve the steps format demo page"""
    return send_from_directory('.', 'demo_steps.html')

@app.route('/pdf_demo')
def pdf_demo():
    """Serve the PDF demo page"""
    return send_from_directory('.', 'pdf_demo.html')

@app.route('/solve_text', methods=['POST'])
def solve_text():
    """
    Process text input for math problem solving
    """
    try:
        text = request.form.get('text', '').strip()
        
        if not text:
            return jsonify({
                "success": False,
                "error": "Please provide a math problem to solve"
            }), 400
        
        logger.info(f"Processing text problem: {text[:100]}...")
        
        # Call local Ollama API with Gemma 3n model
        ollama_result = call_ollama_api(text, mode="solve")
        
        if ollama_result["success"]:
            logger.info("Successfully solved using local Ollama + Gemma 3n")
            return jsonify({
                "success": True,
                "latex": ollama_result["latex"],
                "original_text": text,
                "source": "ollama",
                "message": "Solution generated by local Ollama + Gemma 3n model"
            })
        else:
            logger.error(f"Ollama failed: {ollama_result.get('error')}")
            return jsonify({
                "success": False,
                "error": ollama_result.get('error', 'Local Ollama not available'),
                "troubleshooting": "Please ensure: 1) Ollama is installed and running 2) Gemma 3n model is downloaded 3) Run command: ollama pull gemma:3n"
            }), 500
        
    except Exception as e:
        logger.error(f"Error processing text: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Error processing math problem: {str(e)}"
        }), 500

@app.route('/generate_practice', methods=['POST'])
def generate_practice():
    """
    Generate practice problems based on the original problem
    """
    try:
        text = request.form.get('text', '').strip()
        
        if not text:
            return jsonify({
                "success": False,
                "error": "Please provide a math problem to generate practice questions"
            }), 400
        
        logger.info(f"Generating practice problems for: {text[:100]}...")
        
        # Call local Ollama API for practice problems
        ollama_result = call_ollama_api(text, mode="practice")
        
        if ollama_result["success"]:
            logger.info("Successfully generated practice problems using local Ollama + Gemma 3n")
            
            # Parse the AI response to extract problems and solutions
            calculation, answers = parse_practice_problems_and_solutions(ollama_result["latex"])
            
            # Generate PDF
            pdf_filename = generate_practice_pdf(text, calculation, answers)
            
            if pdf_filename:
                return jsonify({
                    "success": True,
                    "pdf_filename": pdf_filename,
                    "original_text": text,
                    "source": "ollama",
                    "message": "Practice worksheet PDF generated successfully",
                    "calculation": calculation,
                    "answers": answers
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Failed to generate PDF"
                }), 500
        else:
            logger.error(f"Ollama failed: {ollama_result.get('error')}")
            return jsonify({
                "success": False,
                "error": ollama_result.get('error', 'Local Ollama not available')
            }), 500
        
    except Exception as e:
        logger.error(f"Error generating practice problems: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Error generating practice problems: {str(e)}"
        }), 500

@app.route('/solve_image', methods=['POST'])
def solve_image():
    """
    Process uploaded image/video/audio using OCR or speech recognition
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "error": "No file provided"
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                "success": False,
                "error": "No file selected"
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                "success": False,
                "error": "Please upload a valid file (PNG, JPG, JPEG, GIF, BMP, MP4, MOV, AVI, WAV, MP3, M4A, OGG)"
            }), 400
        
        logger.info(f"Processing file: {file.filename}")
        
        # Read file data
        file_data = file.read()
        if len(file_data) == 0:
            return jsonify({
                "success": False,
                "error": "Empty file"
            }), 400
        
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        extracted_text = ""
        
        # Process based on file type
        if file_extension in ['wav', 'mp3', 'm4a', 'ogg']:
            # Audio file - speech recognition
            file.seek(0)  # Reset file pointer
            extracted_text = process_audio_file(file)
            
        elif file_extension in ['mp4', 'avi', 'mov', 'wmv', 'webm']:
            # Video file - extract frames and OCR
            with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as temp_file:
                temp_file.write(file_data)
                temp_path = temp_file.name
            
            try:
                extracted_text = extract_text_from_video(temp_path)
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        else:
            # Image file - OCR
            try:
                # Check if tesseract is available
                import subprocess
                try:
                    subprocess.run(['tesseract', '--version'], capture_output=True, check=True)
                except (subprocess.CalledProcessError, FileNotFoundError):
                    return jsonify({
                        "success": False,
                        "error": "Tesseract OCR is not installed. Please install it to enable image text extraction, or use text input instead."
                    }), 400
                
                image = Image.open(io.BytesIO(file_data))
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                extracted_text = pytesseract.image_to_string(image, lang='eng')
                extracted_text = extracted_text.strip()
                
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": "Invalid image format or OCR processing failed"
                }), 400
        
        # Check if extracted_text contains error messages
        if extracted_text.startswith("ERROR:"):
            return jsonify({
                "success": False,
                "error": extracted_text
            }), 400
        
        if not extracted_text:
            file_type = "image" if file_extension in ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'] else \
                       "video" if file_extension in ['mp4', 'avi', 'mov', 'wmv', 'webm'] else "audio"
            
            return jsonify({
                "success": True,
                "extracted_text": "",
                "message": f"No text could be extracted from the {file_type}. Please ensure the {file_type} contains clear, readable text or speech."
            })
        
        logger.info(f"Extracted text: {extracted_text[:100]}...")
        
        return jsonify({
            "success": True,
            "extracted_text": extracted_text,
            "message": "Text successfully extracted from file"
        })
        
    except Exception as e:
        logger.error(f"Unexpected error processing file: {str(e)}")
        return jsonify({
            "success": False,
            "error": "An unexpected error occurred while processing the file"
        }), 500

@app.route('/test_ollama_connection', methods=['POST'])
def test_ollama_connection():
    """Test connection to local Ollama instance"""
    try:
        # Only test localhost connection
        response = requests.get(f"{OLLAMA_API_URL}/api/tags", timeout=10)
        
        if response.status_code == 200:
            models_data = response.json()
            models = [model.get('name', 'unknown') for model in models_data.get('models', [])]
            
            if 'gemma3:4b' in models:
                return jsonify({
                    "success": True,
                    "message": "Local Ollama connected successfully, Gemma 3 4B model available",
                    "models": models
                })
            else:
                return jsonify({
                    "success": False,
                    "error": f"Local Ollama connected but Gemma 3 4B model not found. Please run: ollama pull gemma3:4b\nAvailable models: {', '.join(models) if models else 'None'}"
                })
        else:
            return jsonify({
                "success": False,
                "error": f"Local Ollama API returned status code {response.status_code}"
            })
            
    except requests.exceptions.Timeout:
        return jsonify({
            "success": False,
            "error": "Connection timeout - Please check if local Ollama is running"
        })
    except requests.exceptions.ConnectionError:
        return jsonify({
            "success": False,
            "error": "Cannot connect to local Ollama - Please ensure Ollama service is installed and started"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Connection error: {str(e)}"
        })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "equalearn.ai."})

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

@app.route('/download_pdf/<filename>')
def download_pdf(filename):
    """Download generated PDF file"""
    try:
        return send_from_directory(PDF_OUTPUT_FOLDER, filename, as_attachment=True)
    except Exception as e:
        logger.error(f"Error downloading PDF {filename}: {e}")
        return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)