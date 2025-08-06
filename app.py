import os
import io
import logging
import requests
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

# Ollama API configuration
OLLAMA_API_URL = os.environ.get('OLLAMA_API_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'gemma:3n')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def call_ollama_api(text):
    """
    Call the local Ollama API to solve math problems using Gemma model
    """
    try:
        # Enhanced prompt to ensure LaTeX output
        enhanced_prompt = f"""请用LaTeX数学格式回答这道题并逐步推理。请将所有数学表达式用LaTeX格式包围，使用 \\begin{{align}} 和 \\end{{align}} 来包围多行数学表达式。

问题：{text}

请提供详细的解题步骤和最终答案，所有数学符号和公式都要用LaTeX格式。"""
        
        response = requests.post(
            f"{OLLAMA_API_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": enhanced_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Lower temperature for more consistent math output
                    "top_p": 0.9
                }
            },
            timeout=30  # 30 second timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "latex": result.get("response", ""),
                "source": "ollama"
            }
        else:
            logger.error(f"Ollama API error: {response.status_code}")
            return {"success": False, "error": f"Ollama API returned status {response.status_code}"}
            
    except requests.exceptions.Timeout:
        logger.error("Ollama API timeout")
        return {"success": False, "error": "Ollama API timeout"}
    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to Ollama API")
        return {"success": False, "error": "Cannot connect to local Ollama instance"}
    except Exception as e:
        logger.error(f"Ollama API error: {str(e)}")
        return {"success": False, "error": str(e)}

def generate_fallback_solution(text):
    """
    Generate a fallback solution when Ollama is not available
    """
    # Simulate math problem solving with LaTeX output
    if "derivative" in text.lower() or "differentiate" in text.lower() or "导数" in text:
        latex_answer = r"""\begin{align}
        \text{解题步骤（模拟解答）:} \\
        \frac{d}{dx}[f(x)] &= \lim_{h \to 0} \frac{f(x+h) - f(x)}{h} \\
        \text{应用求导法则进行计算} \\
        \text{注意：这是模拟解答，请连接本地 Ollama 获取真实解答}
        \end{align}"""
    elif "integral" in text.lower() or "integrate" in text.lower() or "积分" in text:
        latex_answer = r"""\begin{align}
        \text{解题步骤（模拟解答）:} \\
        \int f(x) \, dx &= F(x) + C \\
        \text{其中 } F'(x) &= f(x) \\
        \text{注意：这是模拟解答，请连接本地 Ollama 获取真实解答}
        \end{align}"""
    elif "limit" in text.lower() or "极限" in text:
        latex_answer = r"""\begin{align}
        \text{解题步骤（模拟解答）:} \\
        \lim_{x \to a} f(x) &= L \\
        \text{应用极限定理和技巧} \\
        \text{注意：这是模拟解答，请连接本地 Ollama 获取真实解答}
        \end{align}"""
    else:
        # Escape special characters in the input text for LaTeX
        escaped_text = text.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")
        latex_answer = r"""\begin{align}
        \text{问题分析（模拟解答）:} \\
        \text{输入: } & \text{""" + escaped_text + r"""} \\
        \text{解题方法: } & \text{识别数学概念} \\
        & \text{应用相应方法} \\
        & \text{验证结果} \\
        \text{注意：这是模拟解答，请连接本地 Ollama 获取真实解答}
        \end{align}"""
    
    return {
        "success": True,
        "latex": latex_answer,
        "source": "fallback"
    }

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
        
        # Try to use Ollama API first
        ollama_result = call_ollama_api(text)
        
        if ollama_result["success"]:
            logger.info("Successfully solved using Ollama API")
            return jsonify({
                "success": True,
                "latex": ollama_result["latex"],
                "original_text": text,
                "source": "ollama",
                "message": "解答由本地 Ollama + Gemma 模型生成"
            })
        else:
            logger.warning(f"Ollama API failed: {ollama_result.get('error')}, using fallback")
            fallback_result = generate_fallback_solution(text)
            return jsonify({
                "success": True,
                "latex": fallback_result["latex"],
                "original_text": text,
                "source": "fallback",
                "message": f"使用模拟解答（Ollama 不可用: {ollama_result.get('error', '未知错误')}）",
                "ollama_error": ollama_result.get('error')
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

@app.route('/test_ollama_connection', methods=['POST'])
def test_ollama_connection():
    """Test connection to Ollama API"""
    try:
        data = request.get_json()
        ollama_url = data.get('ollama_url', 'http://localhost:11434')
        
        # Test connection to Ollama
        response = requests.get(f"{ollama_url}/api/tags", timeout=10)
        
        if response.status_code == 200:
            models_data = response.json()
            models = [model.get('name', 'unknown') for model in models_data.get('models', [])]
            
            if 'gemma:3n' in models:
                return jsonify({
                    "success": True,
                    "message": "Connected successfully and Gemma 3n model is available",
                    "models": models
                })
            else:
                return jsonify({
                    "success": False,
                    "error": f"Connected but Gemma 3n model not found. Available models: {', '.join(models) if models else 'None'}"
                })
        else:
            return jsonify({
                "success": False,
                "error": f"Ollama API returned status {response.status_code}"
            })
            
    except requests.exceptions.Timeout:
        return jsonify({
            "success": False,
            "error": "Connection timeout - Ollama may not be running"
        })
    except requests.exceptions.ConnectionError:
        return jsonify({
            "success": False,
            "error": "Cannot connect to Ollama - check if it's running and accessible"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

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