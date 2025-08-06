"""
equalearn.ai. Configuration File
Users can modify various application settings here
"""

import os

# Ollama配置
OLLAMA_CONFIG = {
    "api_url": "http://localhost:11434",
    "model": "gemma3:4b",
    "timeout": 120,  # 秒
    "temperature": 0.1,  # 解题时的温度
    "practice_temperature": 0.3,  # 生成练习题时的温度
    "max_tokens": 2048
}

# 文件上传配置
UPLOAD_CONFIG = {
    "max_file_size": 32 * 1024 * 1024,  # 32MB
    "allowed_extensions": {
        "images": {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'},
        "videos": {'mp4', 'avi', 'mov', 'wmv', 'webm'},
        "audio": {'wav', 'mp3', 'm4a', 'ogg'}
    },
    "upload_folder": "uploads"
}

# OCR配置
OCR_CONFIG = {
    "languages": ['eng', 'chi_sim'],  # 支持的语言
    "video_frame_interval": 30,  # 视频帧提取间隔（帧数）
    "max_video_duration": 10  # 最大处理视频时长（秒）
}

# 语音识别配置
SPEECH_CONFIG = {
    "languages": {
        "en": "en-US",
        "zh": "zh-CN"
    },
    "timeout": 10  # 语音识别超时时间（秒）
}

# 应用配置
APP_CONFIG = {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": True,
    "secret_key": os.environ.get("SESSION_SECRET", "dev-secret-key")
}

# AI prompt configuration
PROMPT_CONFIG = {
    "solve_prompt": """You are a professional mathematics teacher. Please solve this math problem step by step with the following requirements:

1. Use LaTeX format for all mathematical formulas
2. Provide detailed step-by-step explanations with clear reasoning
3. Use \\begin{{align}} and \\end{{align}} to wrap multi-line mathematical expressions
4. Add clear explanations for each key step
5. Provide a clear final answer

Math Problem: {text}

Please begin solving:""",

    "practice_prompt": """Based on this math problem, generate 3 related practice problems with the following requirements:

1. Increasing difficulty levels (easy, medium, hard)
2. Each problem should have detailed solution steps
3. Use LaTeX format for mathematical formulas
4. Diversify problem types (calculation, proof, application problems)

Original Problem: {text}

Please generate practice problems:"""
}

# Interface configuration
UI_CONFIG = {
    "default_language": "en",  # Default language
    "supported_languages": ["en"],
    "theme": "dark",  # Theme: dark or light
    "auto_translate": True  # Whether to auto-translate
}

# Logging configuration
LOGGING_CONFIG = {
    "level": "DEBUG",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "app.log"
}

# Security configuration
SECURITY_CONFIG = {
    "max_requests_per_minute": 60,
    "enable_rate_limiting": False,
    "allowed_hosts": ["localhost", "127.0.0.1"]
} 