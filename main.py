from fastapi import FastAPI, File, UploadFile, Form, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pytesseract
from PIL import Image
import io
import os
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(title="Solvely Lite - Offline Math Solver")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    """Serve the main application page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/solve_text")
async def solve_text(text: str = Form(...)):
    """
    Process text input for math problem solving
    In a real implementation, this would integrate with a local LLM
    """
    try:
        if not text or not text.strip():
            raise HTTPException(status_code=400, detail="Please provide a math problem to solve")
        
        logger.info(f"Processing text problem: {text[:100]}...")
        
        # Simulate math problem solving with LaTeX output
        # In production, this would be replaced with actual LLM inference
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
            latex_answer = r"""\begin{align}
            \text{Problem Analysis:} \\
            \text{Input: } & \text{""" + text.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}") + r"""} \\
            \text{Solution approach:} & \text{ Identify the mathematical concept} \\
            & \text{ Apply appropriate methods} \\
            & \text{ Verify the result}
            \end{align}"""
        
        return {
            "success": True,
            "latex": latex_answer,
            "original_text": text
        }
        
    except Exception as e:
        logger.error(f"Error processing text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing math problem: {str(e)}")

@app.post("/solve_image")
async def solve_image(file: UploadFile = File(...)):
    """
    Process uploaded image using OCR to extract text
    """
    try:
        if not file:
            raise HTTPException(status_code=400, detail="No image file provided")
        
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Please upload a valid image file")
        
        logger.info(f"Processing image: {file.filename}")
        
        # Read and process image
        image_data = await file.read()
        if len(image_data) == 0:
            raise HTTPException(status_code=400, detail="Empty image file")
        
        # Convert to PIL Image
        try:
            image = Image.open(io.BytesIO(image_data))
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
        except Exception as e:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Perform OCR
        try:
            extracted_text = pytesseract.image_to_string(image, lang='eng')
            extracted_text = extracted_text.strip()
        except Exception as e:
            logger.error(f"OCR error: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to extract text from image")
        
        if not extracted_text:
            return {
                "success": True,
                "extracted_text": "",
                "message": "No text could be extracted from the image. Please ensure the image contains clear, readable text."
            }
        
        logger.info(f"Extracted text: {extracted_text[:100]}...")
        
        return {
            "success": True,
            "extracted_text": extracted_text,
            "message": "Text successfully extracted from image"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing image: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while processing the image")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Solvely Lite"}

if __name__ == "__main__":
    # Run on port 5000 for frontend access as specified in guidelines
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=5000, 
        reload=True,
        log_level="info"
    )
