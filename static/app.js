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
        const errorMsg = currentLanguage === 'en' ? 
            'Please select an image or video file.' : 
            '请选择图片或视频文件。';
        showError(errorMsg);
        return;
    }
    
    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
        const errorMsg = currentLanguage === 'en' ? 
            'File is too large. Please select a file smaller than 10MB.' : 
            '文件过大。请选择小于10MB的文件。';
        showError(errorMsg);
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

// Drag and Drop functionality
const dragDropZone = document.getElementById("dragDropZone");
const dragDropOverlay = dragDropZone.querySelector(".drag-drop-overlay");
const browseBtn = document.getElementById("browseBtn");
const selectedFileInfo = document.getElementById("selectedFileInfo");
const fileName = document.getElementById("fileName");
const fileSize = document.getElementById("fileSize");
const removeFileBtn = document.getElementById("removeFileBtn");
const mediaPreview = document.getElementById("mediaPreview");
const previewVideo = document.getElementById("previewVideo");

// File size formatter
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// File type checker
function isValidFile(file) {
    const validTypes = [
        'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp', 'image/webp',
        'video/mp4', 'video/avi', 'video/mov', 'video/wmv', 'video/webm'
    ];
    return validTypes.includes(file.type);
}

// Display selected file
function displaySelectedFile(file) {
    if (!isValidFile(file)) {
        const errorMsg = currentLanguage === 'en' ? 
            'Please select a valid image or video file' : 
            '请选择有效的图片或视频文件';
        alert(errorMsg);
        return false;
    }
    
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    selectedFileInfo.style.display = 'block';
    
    // Show preview
    if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImg.src = e.target.result;
            previewImg.style.display = 'block';
            previewVideo.style.display = 'none';
            mediaPreview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    } else if (file.type.startsWith('video/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
            previewVideo.src = e.target.result;
            previewVideo.style.display = 'block';
            previewImg.style.display = 'none';
            mediaPreview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }
    
    return true;
}

// Remove selected file
function removeSelectedFile() {
    imageInput.value = '';
    selectedFileInfo.style.display = 'none';
    mediaPreview.style.display = 'none';
    previewImg.src = '';
    previewVideo.src = '';
}

// Browse button click
browseBtn.addEventListener('click', () => {
    imageInput.click();
});

// Drag drop zone click
dragDropZone.addEventListener('click', (e) => {
    if (e.target === dragDropZone || e.target.closest('.drag-drop-content')) {
        imageInput.click();
    }
});

// Remove file button
removeFileBtn.addEventListener('click', removeSelectedFile);

// File input change
imageInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        displaySelectedFile(file);
    }
});

// Drag and drop events
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dragDropZone.addEventListener(eventName, preventDefaults, false);
    document.body.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

// Highlight drop area
['dragenter', 'dragover'].forEach(eventName => {
    dragDropZone.addEventListener(eventName, highlight, false);
});

['dragleave', 'drop'].forEach(eventName => {
    dragDropZone.addEventListener(eventName, unhighlight, false);
});

function highlight() {
    dragDropZone.classList.add('drag-over');
    dragDropOverlay.style.display = 'flex';
}

function unhighlight() {
    dragDropZone.classList.remove('drag-over');
    dragDropOverlay.style.display = 'none';
}

// Handle dropped files
dragDropZone.addEventListener('drop', handleDrop, false);

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    
    if (files.length > 0) {
        const file = files[0];
        imageInput.files = files;
        displaySelectedFile(file);
    }
}

// Handle image preview (updated for media files)
imageInput.addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (file) {
        displaySelectedFile(file);
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

// Translation functionality
let currentLanguage = 'en';

function translatePage(targetLang) {
    currentLanguage = targetLang;
    
    // Update all elements with translation data attributes
    const elements = document.querySelectorAll('[data-en], [data-zh]');
    elements.forEach(element => {
        if (element.hasAttribute(`data-${targetLang}`)) {
            element.textContent = element.getAttribute(`data-${targetLang}`);
        }
    });
    
    // Update placeholders
    const placeholderElements = document.querySelectorAll('[data-placeholder-en], [data-placeholder-zh]');
    placeholderElements.forEach(element => {
        if (element.hasAttribute(`data-placeholder-${targetLang}`)) {
            element.placeholder = element.getAttribute(`data-placeholder-${targetLang}`);
        }
    });
    
    // Update translate button text
    const translateText = document.getElementById('translateText');
    translateText.textContent = targetLang === 'en' ? '中文' : 'English';
    
    // Save language preference
    localStorage.setItem('preferredLanguage', targetLang);
    
    // Re-render feather icons
    feather.replace();
}

// Translation button event listener
const translateBtn = document.getElementById('translateBtn');
translateBtn.addEventListener('click', () => {
    const newLang = currentLanguage === 'en' ? 'zh' : 'en';
    translatePage(newLang);
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
            const successMsg = currentLanguage === 'en' ? 'Local service running normally' : '本地服务正常运行';
            connectionStatus.innerHTML = `<span class="text-success"><i data-feather="check-circle"></i> ${successMsg}</span>`;
        } else {
            connectionStatus.innerHTML = `<span class="text-danger"><i data-feather="x-circle"></i> ${data.error}</span>`;
        }
        
        // Re-render feather icons
        feather.replace();
        
    } catch (error) {
        const errorMsg = currentLanguage === 'en' ? `Check failed: ${error.message}` : `检查失败: ${error.message}`;
        connectionStatus.innerHTML = `<span class="text-danger"><i data-feather="x-circle"></i> ${errorMsg}</span>`;
        feather.replace();
    } finally {
        setButtonLoading(testConnectionBtn, false);
    }
});

// Initialize the page
document.addEventListener("DOMContentLoaded", () => {
    showState(emptyState);
    
    // Load saved language preference
    const savedLanguage = localStorage.getItem('preferredLanguage') || 'en';
    if (savedLanguage !== 'en') {
        translatePage(savedLanguage);
    }
    
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
