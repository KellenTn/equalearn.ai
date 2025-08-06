// DOM Elements
const textForm = document.getElementById("textForm");
const imageForm = document.getElementById("imageForm");
const imageInput = document.getElementById("imageInput");
const imagePreview = document.getElementById("imagePreview");
const previewImg = document.getElementById("previewImg");

// State elements
const loadingState = document.getElementById("loadingState");
const errorState = document.getElementById("errorState");
const successState = document.getElementById("successState");
const emptyState = document.getElementById("emptyState");

// Content elements
const originalProblem = document.getElementById("originalProblem");
const problemText = document.getElementById("problemText");
const extractedText = document.getElementById("extractedText");
const extractedContent = document.getElementById("extractedContent");
const latexSolution = document.getElementById("latexSolution");
const mathOutput = document.getElementById("mathOutput");
const errorMessage = document.getElementById("errorMessage");
const solutionSource = document.getElementById("solutionSource");
const sourceMessage = document.getElementById("sourceMessage");

// Buttons
const solveTextBtn = document.getElementById("solveTextBtn");
const extractTextBtn = document.getElementById("extractTextBtn");
const solveExtractedBtn = document.getElementById("solveExtractedBtn");
const testConnectionBtn = document.getElementById("testConnectionBtn");

// Utility functions
function showState(state) {
    // Hide all states
    loadingState.style.display = "none";
    errorState.style.display = "none";
    successState.style.display = "none";
    emptyState.style.display = "none";
    
    // Show requested state
    if (state) {
        state.style.display = "block";
    }
}

function showError(message) {
    errorMessage.textContent = message;
    showState(errorState);
}

function showLoading() {
    showState(loadingState);
}

function resetResults() {
    originalProblem.style.display = "none";
    extractedText.style.display = "none";
    latexSolution.style.display = "none";
    solutionSource.style.display = "none";
}

function setButtonLoading(button, isLoading) {
    if (isLoading) {
        button.disabled = true;
        const originalText = button.innerHTML;
        button.setAttribute('data-original-text', originalText);
        button.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Processing...';
    } else {
        button.disabled = false;
        const originalText = button.getAttribute('data-original-text');
        if (originalText) {
            button.innerHTML = originalText;
        }
    }
}

function renderMath(element) {
    try {
        renderMathInElement(element, {
            delimiters: [
                {left: '$$', right: '$$', display: true},
                {left: '$', right: '$', display: false},
                {left: '\\[', right: '\\]', display: true},
                {left: '\\(', right: '\\)', display: false},
                {left: '\\begin{align}', right: '\\end{align}', display: true},
                {left: '\\begin{equation}', right: '\\end{equation}', display: true}
            ],
            throwOnError: false,
            strict: false
        });
    } catch (error) {
        console.error('Error rendering math:', error);
        element.innerHTML = '<div class="alert alert-warning">Error rendering mathematical notation</div>';
    }
}

// Event handlers
textForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const formData = new FormData(textForm);
    const text = formData.get('text');
    
    if (!text || !text.trim()) {
        showError("Please enter a math problem to solve.");
        return;
    }
    
    showLoading();
    setButtonLoading(solveTextBtn, true);
    
    try {
        const response = await fetch("/solve_text", {
            method: "POST",
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || "Failed to solve problem");
        }
        
        if (data.success) {
            resetResults();
            
            // Show original problem
            problemText.textContent = data.original_text;
            originalProblem.style.display = "block";
            
            // Show solution source info
            if (data.message) {
                sourceMessage.textContent = data.message;
                solutionSource.style.display = "block";
                
                // Always show success for Ollama (no fallback mode)
                const sourceInfo = document.getElementById("sourceInfo");
                sourceInfo.className = "alert alert-success mb-2";
            }
            
            // Show LaTeX solution
            mathOutput.innerHTML = data.latex;
            renderMath(mathOutput);
            latexSolution.style.display = "block";
            
            showState(successState);
        } else {
            showError("Failed to solve the problem. Please try again.");
        }
    } catch (error) {
        console.error("Error solving text problem:", error);
        showError(error.message || "An error occurred while solving the problem.");
    } finally {
        setButtonLoading(solveTextBtn, false);
    }
});

imageForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const formData = new FormData(imageForm);
    const file = formData.get('file');
    
    if (!file || file.size === 0) {
        showError("Please select an image file.");
        return;
    }
    
    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
        showError("Image file is too large. Please select a file smaller than 10MB.");
        return;
    }
    
    showLoading();
    setButtonLoading(extractTextBtn, true);
    
    try {
        const response = await fetch("/solve_image", {
            method: "POST",
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || "Failed to process image");
        }
        
        if (data.success) {
            resetResults();
            
            if (data.extracted_text) {
                extractedContent.textContent = data.extracted_text;
                extractedText.style.display = "block";
                
                // Store extracted text for solving
                solveExtractedBtn.setAttribute('data-text', data.extracted_text);
            } else {
                showError(data.message || "No text could be extracted from the image.");
                return;
            }
            
            showState(successState);
        } else {
            showError("Failed to extract text from image. Please try again.");
        }
    } catch (error) {
        console.error("Error processing image:", error);
        showError(error.message || "An error occurred while processing the image.");
    } finally {
        setButtonLoading(extractTextBtn, false);
    }
});

// Handle image preview
imageInput.addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImg.src = e.target.result;
            imagePreview.style.display = "block";
        };
        reader.readAsDataURL(file);
    } else {
        imagePreview.style.display = "none";
    }
});

// Handle solving extracted text
solveExtractedBtn.addEventListener("click", async () => {
    const text = solveExtractedBtn.getAttribute('data-text');
    if (!text) {
        showError("No extracted text available to solve.");
        return;
    }
    
    showLoading();
    setButtonLoading(solveExtractedBtn, true);
    
    try {
        const formData = new FormData();
        formData.append('text', text);
        
        const response = await fetch("/solve_text", {
            method: "POST",
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || "Failed to solve problem");
        }
        
        if (data.success) {
            // Show solution source info
            if (data.message) {
                sourceMessage.textContent = data.message;
                solutionSource.style.display = "block";
                
                // Always show success for Ollama (no fallback mode)
                const sourceInfo = document.getElementById("sourceInfo");
                sourceInfo.className = "alert alert-success mb-2";
            }
            
            // Show LaTeX solution
            mathOutput.innerHTML = data.latex;
            renderMath(mathOutput);
            latexSolution.style.display = "block";
            
            showState(successState);
        } else {
            showError("Failed to solve the extracted problem. Please try again.");
        }
    } catch (error) {
        console.error("Error solving extracted text:", error);
        showError(error.message || "An error occurred while solving the problem.");
    } finally {
        setButtonLoading(solveExtractedBtn, false);
    }
});

// Test local Ollama connection
testConnectionBtn.addEventListener("click", async () => {
    const connectionStatus = document.getElementById("connectionStatus");
    
    setButtonLoading(testConnectionBtn, true);
    
    try {
        const response = await fetch("/test_ollama_connection", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({})
        });
        
        const data = await response.json();
        
        if (data.success) {
            connectionStatus.innerHTML = '<span class="text-success"><i data-feather="check-circle"></i> 本地服务正常运行</span>';
        } else {
            connectionStatus.innerHTML = `<span class="text-danger"><i data-feather="x-circle"></i> ${data.error}</span>`;
        }
        
        // Re-render feather icons
        feather.replace();
        
    } catch (error) {
        connectionStatus.innerHTML = `<span class="text-danger"><i data-feather="x-circle"></i> 检查失败: ${error.message}</span>`;
        feather.replace();
    } finally {
        setButtonLoading(testConnectionBtn, false);
    }
});

// Initialize the page
document.addEventListener("DOMContentLoaded", () => {
    showState(emptyState);
    
    // Configure KaTeX auto-render
    if (typeof renderMathInElement !== 'undefined') {
        renderMathInElement(document.body, {
            delimiters: [
                {left: '$$', right: '$$', display: true},
                {left: '$', right: '$', display: false},
                {left: '\\[', right: '\\]', display: true},
                {left: '\\(', right: '\\)', display: false}
            ],
            throwOnError: false
        });
    }
});
