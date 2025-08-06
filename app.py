import os
import io
import logging
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import pytesseract
from PIL import Image

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    """Serve the main application page"""
    return render_template('index.html')

@app.route('/solve_text', methods=['POST'])
def solve_text():
    """
    Process text input for math problem solving
    In a real implementation, this would integrate with a local LLM
    """
    try:
        text = request.form.get('text', '').strip()
        
        if not text:
            return jsonify({
                "success": False,
                "error": "Please provide a math problem to solve"
            }), 400
        
        logger.info(f"Processing text problem: {text[:100]}...")
        
        # Simulate math problem solving with LaTeX output
        if "derivative" in text.lower() or "differentiate" in text.lower():
            latex_answer = r"""\begin{align}
            \text{Solution:} \\
            \frac{d}{dx}[f(x)] &= \lim_{h \to 0} \frac{f(x+h) - f(x)}{h} \\
            \text{Apply the differentiation rules} \\
            \end{align}"""
        elif "integral" in text.lower() or "integrate" in text.lower():
            latex_answer = r"""\begin{align}
            \text{Solution:} \\
            \int f(x) \, dx &= F(x) + C \\
            \text{where } F'(x) &= f(x)
            \end{align}"""
        elif "limit" in text.lower():
            latex_answer = r"""\begin{align}
            \text{Solution:} \\
            \lim_{x \to a} f(x) &= L \\
            \text{Apply limit laws and techniques}
            \end{align}"""
        else:
            # Escape special characters in the input text for LaTeX
            escaped_text = text.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")
            latex_answer = r"""\begin{align}
            \text{Problem Analysis:} \\
            \text{Input: } & \text{""" + escaped_text + r"""} \\
            \text{Solution approach:} & \text{ Identify the mathematical concept} \\
            & \text{ Apply appropriate methods} \\
            & \text{ Verify the result}
            \end{align}"""
        
        return jsonify({
            "success": True,
            "latex": latex_answer,
            "original_text": text
        })
        
    except Exception as e:
        logger.error(f"Error processing text: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Error processing math problem: {str(e)}"
        }), 500

@app.route('/solve_image', methods=['POST'])
def solve_image():
    """
    Process uploaded image using OCR to extract text
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "error": "No image file provided"
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                "success": False,
                "error": "No image file selected"
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                "success": False,
                "error": "Please upload a valid image file (PNG, JPG, JPEG, GIF, BMP)"
            }), 400
        
        logger.info(f"Processing image: {file.filename}")
        
        # Read image data
        image_data = file.read()
        if len(image_data) == 0:
            return jsonify({
                "success": False,
                "error": "Empty image file"
            }), 400
        
        # Convert to PIL Image
        try:
            image = Image.open(io.BytesIO(image_data))
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
        except Exception as e:
            return jsonify({
                "success": False,
                "error": "Invalid image format"
            }), 400
        
        # Perform OCR
        try:
            extracted_text = pytesseract.image_to_string(image, lang='eng')
            extracted_text = extracted_text.strip()
        except Exception as e:
            logger.error(f"OCR error: {str(e)}")
            return jsonify({
                "success": False,
                "error": "Failed to extract text from image"
            }), 500
        
        if not extracted_text:
            return jsonify({
                "success": True,
                "extracted_text": "",
                "message": "No text could be extracted from the image. Please ensure the image contains clear, readable text."
            })
        
        logger.info(f"Extracted text: {extracted_text[:100]}...")
        
        return jsonify({
            "success": True,
            "extracted_text": extracted_text,
            "message": "Text successfully extracted from image"
        })
        
    except Exception as e:
        logger.error(f"Unexpected error processing image: {str(e)}")
        return jsonify({
            "success": False,
            "error": "An unexpected error occurred while processing the image"
        }), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "Solvely Lite"})

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)