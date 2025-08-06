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

# Ollama API configuration - Only local instance supported
OLLAMA_API_URL = 'http://localhost:11434'  # Fixed to localhost only
OLLAMA_MODEL = 'gemma:3n'  # Fixed to Gemma 3n model

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def call_ollama_api(text):
    """
    Call the local Ollama API to solve math problems using Gemma 3n model
    This function requires a local Ollama instance running with Gemma 3n model
    """
    try:
        # Enhanced prompt optimized for Gemma 3n mathematical reasoning
        enhanced_prompt = f"""你是一个数学专家，请用LaTeX格式详细解答这道数学题。

要求：
1. 使用 \\begin{{align}} 和 \\end{{align}} 包围多行数学表达式
2. 每步都要详细说明推理过程
3. 所有数学符号和公式都用LaTeX格式
4. 提供最终答案

题目：{text}

解答："""
        
        response = requests.post(
            f"{OLLAMA_API_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": enhanced_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Lower temperature for consistent math solutions
                    "top_p": 0.9,
                    "num_predict": 2048  # Allow longer responses for detailed solutions
                }
            },
            timeout=60  # Increased timeout for complex math problems
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
        return {"success": False, "error": "本地 Ollama 响应超时，请检查系统性能"}
    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to Ollama API")
        return {"success": False, "error": "无法连接本地 Ollama，请确保 Ollama 正在运行并已加载 Gemma 3n 模型"}
    except Exception as e:
        logger.error(f"Ollama API error: {str(e)}")
        return {"success": False, "error": f"Ollama 错误: {str(e)}"}



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
        
        # Call local Ollama API with Gemma 3n model
        ollama_result = call_ollama_api(text)
        
        if ollama_result["success"]:
            logger.info("Successfully solved using local Ollama + Gemma 3n")
            return jsonify({
                "success": True,
                "latex": ollama_result["latex"],
                "original_text": text,
                "source": "ollama",
                "message": "解答由本地设备上的 Ollama + Gemma 3n 模型生成"
            })
        else:
            logger.error(f"Ollama failed: {ollama_result.get('error')}")
            return jsonify({
                "success": False,
                "error": ollama_result.get('error', '本地 Ollama 不可用'),
                "troubleshooting": "请确保：1) Ollama 已安装并运行 2) 已下载 Gemma 3n 模型 3) 运行命令: ollama pull gemma:3n"
            }), 500
        
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
    """Test connection to local Ollama instance"""
    try:
        # Only test localhost connection
        response = requests.get(f"{OLLAMA_API_URL}/api/tags", timeout=10)
        
        if response.status_code == 200:
            models_data = response.json()
            models = [model.get('name', 'unknown') for model in models_data.get('models', [])]
            
            if 'gemma:3n' in models:
                return jsonify({
                    "success": True,
                    "message": "本地 Ollama 连接成功，Gemma 3n 模型可用",
                    "models": models
                })
            else:
                return jsonify({
                    "success": False,
                    "error": f"本地 Ollama 已连接但未找到 Gemma 3n 模型。请运行: ollama pull gemma:3n\n可用模型: {', '.join(models) if models else '无'}"
                })
        else:
            return jsonify({
                "success": False,
                "error": f"本地 Ollama API 返回状态码 {response.status_code}"
            })
            
    except requests.exceptions.Timeout:
        return jsonify({
            "success": False,
            "error": "连接超时 - 请检查本地 Ollama 是否正在运行"
        })
    except requests.exceptions.ConnectionError:
        return jsonify({
            "success": False,
            "error": "无法连接本地 Ollama - 请确保已安装并启动 Ollama 服务"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"连接错误: {str(e)}"
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