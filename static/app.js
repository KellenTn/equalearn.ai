// DOM Elements
const textForm = document.getElementById("textForm");
const imageForm = document.getElementById("imageForm");
const imageInput = document.getElementById("imageInput");
const imagePreview = document.getElementById("imagePreview");
const previewImg = document.getElementById("previewImg");
const voiceInputBtn = document.getElementById("voiceInputBtn");
const generatePracticeBtn = document.getElementById("generatePracticeBtn");

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

function showSuccess(message) {
    // Create a temporary success message
    const successDiv = document.createElement('div');
    successDiv.className = 'alert alert-success';
    successDiv.innerHTML = message;
    
    // Insert at the top of the success state
    const successState = document.getElementById('successState');
    successState.insertBefore(successDiv, successState.firstChild);
    
    showState(successState);
    
    // Remove the message after 5 seconds
    setTimeout(() => {
        if (successDiv.parentNode) {
            successDiv.parentNode.removeChild(successDiv);
        }
    }, 5000);
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

// Clean markdown formatting
function cleanMarkdown(text) {
    if (!text) return '';
    
    return text
        // Remove markdown bold markers
        .replace(/\*\*(.*?)\*\*/g, '$1')
        // Remove markdown italic markers
        .replace(/\*(.*?)\*/g, '$1')
        // Remove markdown code markers
        .replace(/`(.*?)`/g, '$1')
        // Remove markdown box markers
        .replace(/\\boxed\{(.*?)\}/g, '$1')
        // Clean up extra whitespace
        .replace(/\n\s*\n/g, '\n')
        .trim();
}

// Parse AI response and display in structured format
function parseAndDisplaySolution(latexContent) {
    const finalAnswerElement = document.getElementById('finalAnswer');
    const explanationElement = document.getElementById('explanation');
    
    // Extract final answer (look for patterns like "Final Answer:", "Answer:", "= 4", etc.)
    let finalAnswer = '';
    let explanation = latexContent;
    
    // Look for final answer patterns
    const finalAnswerPatterns = [
        /\*\*Final Answer:?\*\*\s*([^.\n]+(?:\n[^.\n]+)*)/i,
        /Final Answer:?\s*([^.\n]+(?:\n[^.\n]+)*)/i,
        /\*\*Answer:?\*\*\s*([^.\n]+(?:\n[^.\n]+)*)/i,
        /Answer:?\s*([^.\n]+(?:\n[^.\n]+)*)/i,
        /Therefore,?\s*([^.\n]+(?:\n[^.\n]+)*)/i,
        /Thus,?\s*([^.\n]+(?:\n[^.\n]+)*)/i,
        /The solution is:?\s*([^.\n]+(?:\n[^.\n]+)*)/i,
        /Result:?\s*([^.\n]+(?:\n[^.\n]+)*)/i
    ];
    
    for (const pattern of finalAnswerPatterns) {
        const match = latexContent.match(pattern);
        if (match) {
            finalAnswer = match[1].trim();
            // Remove the final answer from explanation
            explanation = latexContent.replace(pattern, '').trim();
            break;
        }
    }
    
    // If no pattern found, try to extract the last mathematical expression
    if (!finalAnswer) {
        const mathPattern = /([^.\n]*=.*?)(?=\n|$)/;
        const mathMatch = latexContent.match(mathPattern);
        if (mathMatch) {
            finalAnswer = mathMatch[1].trim();
            explanation = latexContent.replace(mathPattern, '').trim();
        }
    }
    
    // If still no final answer, use the whole content as explanation
    if (!finalAnswer) {
        finalAnswer = 'See explanation below';
    }
    
    // Clean up markdown formatting and display final answer
    const cleanFinalAnswer = cleanMarkdown(finalAnswer);
    finalAnswerElement.innerHTML = cleanFinalAnswer;
    renderMath(finalAnswerElement);
    
    // Parse explanation into structured steps
    const structuredExplanation = parseExplanationIntoSteps(explanation);
    explanationElement.innerHTML = structuredExplanation;
    renderMath(explanationElement);
}

// Parse explanation into structured steps
function parseExplanationIntoSteps(explanation) {
    // Split by common step patterns
    const stepPatterns = [
        /\*\*(\d+\.\s*[^*]+)\*\*/g,  // **1. Step Title**
        /\*\*([^*]+)\*\*/g,          // **Step Title**
        /^(\d+\.\s*[^\n]+)/gm,       // 1. Step Title
        /^([A-Z][^:\n]*:)/gm         // Step Title:
    ];
    
    let steps = [];
    let currentStep = '';
    let stepTitle = '';
    
    // Try to find structured steps
    for (const pattern of stepPatterns) {
        const matches = [...explanation.matchAll(pattern)];
        if (matches.length > 1) {
            // Found structured steps
            for (let i = 0; i < matches.length; i++) {
                const match = matches[i];
                const title = match[1].trim();
                const nextMatch = matches[i + 1];
                const startIndex = match.index + match[0].length;
                const endIndex = nextMatch ? nextMatch.index : explanation.length;
                const content = explanation.substring(startIndex, endIndex).trim();
                
                steps.push({
                    title: title,
                    content: content
                });
            }
            break;
        }
    }
    
    // If no structured steps found, create steps from sections
    if (steps.length === 0) {
        // Split by double newlines or section breaks
        const sections = explanation.split(/\n\s*\n/);
        sections.forEach((section, index) => {
            if (section.trim()) {
                const lines = section.trim().split('\n');
                const firstLine = lines[0];
                const restContent = lines.slice(1).join('\n');
                
                // Check if first line looks like a title
                if (firstLine.match(/^[A-Z][^:]*:/) || firstLine.match(/^\*\*[^*]+\*\*/)) {
                    steps.push({
                        title: firstLine.replace(/\*\*/g, ''),
                        content: restContent
                    });
                } else {
                    steps.push({
                        title: `Step ${index + 1}`,
                        content: section.trim()
                    });
                }
            }
        });
    }
    
    // Generate HTML for structured steps
    if (steps.length > 0) {
        return steps.map((step, index) => `
            <div class="solution-step mb-4">
                <h6 class="step-title text-primary mb-2">
                    <i data-feather="hash" class="me-2"></i>
                    ${step.title}
                </h6>
                <div class="step-content p-3 rounded">
                    ${step.content}
                </div>
            </div>
        `).join('');
    } else {
        // Fallback to original content
        return explanation;
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
                const sourceInfoElement = document.getElementById("sourceInfo");
                sourceInfoElement.className = "alert alert-success mb-2";
            }
            
            // Parse and display solution in structured format
            parseAndDisplaySolution(data.latex);
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

// Display selected file and automatically process it
function displaySelectedFile(file) {
    if (!isValidFile(file)) {
        alert('Please select a valid image, video, or audio file');
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
    
    // Automatically process the file for text extraction
    setTimeout(() => {
        processFileAutomatically(file);
    }, 500); // Small delay to let the preview render
    
    return true;
}

// Automatically process uploaded file
async function processFileAutomatically(file) {
    showLoading();
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch("/solve_image", {
            method: "POST",
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || "Failed to process file");
        }
        
        if (data.success) {
            resetResults();
            
            if (data.extracted_text && data.extracted_text.trim()) {
                extractedContent.textContent = data.extracted_text;
                extractedText.style.display = "block";
                
                // Store extracted text for solving
                solveExtractedBtn.setAttribute('data-text', data.extracted_text);
                
                showState(successState);
            } else {
                showError('No text could be extracted from the file. Please ensure the file contains clear, readable text.');
                return;
            }
        } else {
            showError('Failed to extract text from file. Please try again.');
        }
    } catch (error) {
        console.error("Error processing file:", error);
        showError('An error occurred while processing the file. ' + error.message);
    }
}

// Remove selected file
function removeSelectedFile() {
    imageInput.value = '';
    selectedFileInfo.style.display = 'none';
    mediaPreview.style.display = 'none';
    previewImg.src = '';
    previewVideo.src = '';
    
    // Also clear any extracted text results
    resetResults();
    showState(emptyState);
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
                const sourceInfoElement2 = document.getElementById("sourceInfo");
                sourceInfoElement2.className = "alert alert-success mb-2";
            }
            
            // Parse and display solution in structured format
            parseAndDisplaySolution(data.latex);
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

// Translation function using multiple fallback services
async function translateText(text, targetLang = 'zh') {
    try {
        console.log('Starting translation for:', text);
        
        // Try Google Translate first
        try {
            const response = await fetch(`https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=${targetLang}&dt=t&q=${encodeURIComponent(text)}`);
            const data = await response.json();
            console.log('Google Translate API response:', data);
            if (data && data[0] && data[0][0] && data[0][0][0]) {
                return data[0][0][0];
            }
        } catch (googleError) {
            console.log('Google Translate failed, trying alternative...');
        }
        
        // Fallback: Try LibreTranslate
        try {
            const response = await fetch('https://libretranslate.de/translate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    q: text,
                    source: 'en',
                    target: targetLang
                })
            });
            const data = await response.json();
            console.log('LibreTranslate API response:', data);
            if (data && data.translatedText) {
                return data.translatedText;
            }
        } catch (libreError) {
            console.log('LibreTranslate failed, trying simple mapping...');
        }
        
        // Final fallback: Simple word mapping
        const simpleTranslations = {
            'Final Answer': '最终答案',
            'Explanation': '解释',
            'Problem': '问题',
            'Step': '步骤',
            'Therefore': '因此',
            'Addition': '加法',
            'Subtraction': '减法',
            'Multiplication': '乘法',
            'Division': '除法',
            'equals': '等于',
            'plus': '加',
            'minus': '减',
            'times': '乘以',
            'divided by': '除以'
        };
        
        let translatedText = text;
        for (const [english, chinese] of Object.entries(simpleTranslations)) {
            translatedText = translatedText.replace(new RegExp(english, 'gi'), chinese);
        }
        
        console.log('Using simple translation mapping');
        return translatedText;
        
    } catch (error) {
        console.error('All translation methods failed:', error);
        return text; // Return original text if all translation methods fail
    }
}

async function translatePage(targetLang) {
    currentLanguage = targetLang;
    
    // Update translate button text
    const translateText = document.getElementById('translateText');
    translateText.textContent = targetLang === 'en' ? 'Translate to Chinese' : 'English';
    
    // Save language preference
    localStorage.setItem('preferredLanguage', targetLang);
    
    // Define translations for specific elements by ID or class
    const translations = {
        'en': {
            'app-description': 'AI tutor dedicated to eliminating inequality and achieving equal educational resources',
            'text-input-title': 'Text Input',
            'math-input-label': 'Enter your problem:',
            'math-input-placeholder': 'Example: Find the derivative of x^2 + 3x + 1',
            'solve-btn': 'Solve Problem',
            'generate-pdf-btn': 'Generate 20-Question PDF',
            'media-upload-title': 'Media Upload',
            'media-upload-label': 'Upload an image, video, or audio file of your math problem:',
            'drag-drop-text': 'Drag & drop files here, or click to browse',
            'choose-files-btn': 'Choose Files',
            'voice-input-btn': 'Voice Input',
            'test-connection-btn': 'Test Connection',
            'connection-status': 'Connection Status'
        },
        'zh': {
            'app-description': '致力于消除不平等、实现教育资源共享的AI导师',
            'text-input-title': '文本输入',
            'math-input-label': '输入你的问题：',
            'math-input-placeholder': '例如：求函数 x^2 + 3x + 1 的导数',
            'solve-btn': '解答问题',
            'generate-pdf-btn': '生成20题PDF练习册',
            'media-upload-title': '媒体上传',
            'media-upload-label': '上传包含数学问题的图片、视频或音频文件：',
            'drag-drop-text': '拖拽文件到这里，或点击浏览',
            'choose-files-btn': '选择文件',
            'voice-input-btn': '语音输入',
            'test-connection-btn': '测试连接',
            'connection-status': '连接状态'
        }
    };
    
    // Get current translations
    const currentTranslations = translations[targetLang];
    
    // Translate specific elements by data attributes
    for (const [key, translation] of Object.entries(currentTranslations)) {
        const element = document.querySelector(`[data-translate="${key}"]`);
        if (element) {
            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                element.placeholder = translation;
            } else {
                element.textContent = translation;
            }
        }
    }
    
    // Re-render feather icons
    feather.replace();
}

// Translation button event listener
const translateBtn = document.getElementById('translateBtn');
translateBtn.addEventListener('click', async () => {
    console.log('Translate button clicked');
    
    const newLang = currentLanguage === 'en' ? 'zh' : 'en';
    await translatePage(newLang);
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
            connectionStatus.innerHTML = `<span class="text-success"><i data-feather="check-circle"></i> Local service running normally</span>`;
        } else {
            connectionStatus.innerHTML = `<span class="text-danger"><i data-feather="x-circle"></i> ${data.error}</span>`;
        }
        
        // Re-render feather icons
        feather.replace();
        
    } catch (error) {
        connectionStatus.innerHTML = `<span class="text-danger"><i data-feather="x-circle"></i> Check failed: ${error.message}</span>`;
        feather.replace();
    } finally {
        setButtonLoading(testConnectionBtn, false);
    }
});

// Voice input functionality
let recognition = null;
let isRecording = false;

function initSpeechRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        
        recognition.onstart = () => {
            isRecording = true;
            voiceInputBtn.innerHTML = '<i data-feather="square"></i>';
            voiceInputBtn.classList.remove('btn-outline-secondary');
            voiceInputBtn.classList.add('btn-danger');
            feather.replace();
        };
        
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            document.getElementById('mathInput').value = transcript;
        };
        
        recognition.onend = () => {
            isRecording = false;
            voiceInputBtn.innerHTML = '<i data-feather="mic"></i>';
            voiceInputBtn.classList.remove('btn-danger');
            voiceInputBtn.classList.add('btn-outline-secondary');
            feather.replace();
        };
        
        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            isRecording = false;
            voiceInputBtn.innerHTML = '<i data-feather="mic"></i>';
            voiceInputBtn.classList.remove('btn-danger');
            voiceInputBtn.classList.add('btn-outline-secondary');
            feather.replace();
        };
    } else {
        voiceInputBtn.style.display = 'none';
        console.warn('Speech recognition not supported');
    }
}

// Voice input button event listener
voiceInputBtn.addEventListener('click', () => {
    if (!recognition) {
        alert('Speech recognition not supported in this browser');
        return;
    }
    
    if (isRecording) {
        recognition.stop();
    } else {
        recognition.start();
    }
});

// Generate practice problems
generatePracticeBtn.addEventListener('click', async () => {
    const text = document.getElementById('mathInput').value.trim();
    
    if (!text) {
        showError('Please enter a math problem first');
        return;
    }
    
    showLoading();
    setButtonLoading(generatePracticeBtn, true);
    
    try {
        const formData = new FormData();
        formData.append('text', text);
        
        const response = await fetch("/generate_practice", {
            method: "POST",
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || "Failed to generate practice problems");
        }
        
        if (data.success) {
            resetResults();
            
            // Show original problem
            problemText.textContent = data.original_text;
            originalProblem.style.display = "block";
            
            // Show success message
            if (data.message) {
                sourceMessage.textContent = data.message;
                solutionSource.style.display = "block";
                
                const sourceInfoElement3 = document.getElementById("sourceInfo");
                sourceInfoElement3.className = "alert alert-success mb-2";
            }
            
            // Download PDF automatically
            if (data.pdf_filename) {
                // Create download link
                const downloadLink = document.createElement('a');
                downloadLink.href = `/download_pdf/${data.pdf_filename}`;
                downloadLink.download = data.pdf_filename;
                downloadLink.style.display = 'none';
                document.body.appendChild(downloadLink);
                
                // Trigger download
                downloadLink.click();
                
                // Remove the link
                document.body.removeChild(downloadLink);
                
                // Show success message
                showSuccess(`Practice worksheet PDF generated and downloaded successfully!<br>
                           <small>Filename: ${data.pdf_filename}</small><br>
                           <small>Contains 20 questions: 10 multiple choice (with options), 5 true/false, 5 calculation problems.</small>`);
            } else {
                showState(successState);
            }
        } else {
            showError('Failed to generate practice problems');
        }
    } catch (error) {
        console.error("Error generating practice problems:", error);
        showError(error.message || 'An error occurred while generating practice problems');
    } finally {
        setButtonLoading(generatePracticeBtn, false);
    }
});

// Initialize the page
document.addEventListener("DOMContentLoaded", () => {
    showState(emptyState);
    
    // Initialize speech recognition
    initSpeechRecognition();
    
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
