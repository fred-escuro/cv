"""
Configuration file for CV processing parameters
"""

# Text processing configuration
TEXT_PROCESSING_CONFIG = {
    # Note: All chunking functionality has been removed
    # The system now sends entire CVs to AI in one request
}

# AI model configuration
AI_MODEL_CONFIG = {
    # Token limits for different models (approximate)
    "MODEL_TOKEN_LIMITS": {
        'anthropic/claude-3.5-sonnet': 200000,
        'openai/gpt-4o': 128000,
        'anthropic/claude-3-haiku': 200000,
        'meta-llama/llama-3.1-8b-instruct': 8192,
        'anthropic/claude-3-opus': 200000,
        'openai/gpt-4-turbo': 128000,
    },
    
    # Default max tokens for response
    "DEFAULT_MAX_TOKENS": 8000,
    
    # Minimum max tokens for response
    "MIN_MAX_TOKENS": 2000,
    
    # Buffer tokens to reserve for safety
    "SAFETY_BUFFER_TOKENS": 1000,
    
    # Temperature setting for AI responses
    "TEMPERATURE": 0.1,
}

# Processing configuration
PROCESSING_CONFIG = {
    # Note: All chunking functionality has been removed
    # The system now sends entire CVs to AI in one request
    
    # Enable/disable detailed logging
    "ENABLE_DETAILED_LOGGING": True,
    
    # Retry attempts for failed API calls
    "MAX_CHUNK_RETRIES": 2,
    
    # Timeout for AI API calls (seconds) - increased for long CVs
    "AI_API_TIMEOUT": 180,  # 3 minutes for very long CVs
    
    # Enable fallback models
    "ENABLE_FALLBACK_MODELS": True,
}

# File handling configuration
FILE_CONFIG = {
    # Maximum file size (in bytes) - 50MB
    "MAX_FILE_SIZE": 50 * 1024 * 1024,
    
    # Supported file extensions
    "SUPPORTED_EXTENSIONS": {
        '.pdf', '.doc', '.docx', '.rtf', '.txt', '.json',
        '.jpg', '.jpeg', '.png', '.bmp', '.tiff'
    },
    
    # Temporary file cleanup (in seconds)
    "TEMP_FILE_CLEANUP_DELAY": 3600,
}

# Logging configuration
LOGGING_CONFIG = {
    # Log level
    "LOG_LEVEL": "INFO",
    
    # Enable emoji in logs
    "ENABLE_EMOJI": True,
    
    # Log file path
    "LOG_FILE": "cv_transform.log",
    
    # Maximum log file size (in MB)
    "MAX_LOG_SIZE": 10,
    
    # Number of log files to keep
    "LOG_BACKUP_COUNT": 5,
}
