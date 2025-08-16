#!/usr/bin/env python3
"""
Configuration file for the Batch CV Processor

This file contains all the configurable settings for the batch processing script.
Modify these values according to your needs.
"""

# File processing settings
SUPPORTED_EXTENSIONS = {
    '.pdf', '.doc', '.docx', '.rtf', '.txt', '.json', 
    '.jpg', '.jpeg', '.png', '.bmp', '.tiff'
}

# File size limits (in bytes)
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
MIN_FILE_SIZE = 1024  # 1KB

# Processing settings
PROCESSING_DELAY = 0.5  # Delay between files in seconds
BATCH_SIZE = 50  # Process files in batches of this size

# Database settings
DATABASE_TIMEOUT = 30  # Database connection timeout in seconds
MAX_RETRIES = 3  # Maximum retry attempts for failed operations

# Logging settings
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
SAVE_DETAILED_LOGS = True
LOG_DIRECTORY = "logs"

# Performance settings
MAX_CONCURRENT_PROCESSES = 1  # Set to 1 for sequential processing
ENABLE_PROGRESS_BAR = True
SHOW_DETAILED_OUTPUT = True

# Error handling
SKIP_CORRUPTED_FILES = True
CONTINUE_ON_ERROR = True
MAX_ERRORS_BEFORE_STOP = 100

# Output settings
GENERATE_SUMMARY_REPORT = True
SAVE_ERROR_LOG = True
SAVE_SUCCESS_LOG = False

# File handling
CREATE_BACKUP_COPIES = False
BACKUP_DIRECTORY = "backups"
CLEANUP_TEMP_FILES = True
CLEANUP_FAILED_FILES = False

# Notification settings (future feature)
ENABLE_EMAIL_NOTIFICATIONS = False
ENABLE_WEBHOOK_NOTIFICATIONS = False
NOTIFICATION_EMAIL = ""
WEBHOOK_URL = ""

# Advanced settings
ENABLE_PARALLEL_PROCESSING = False
PARALLEL_WORKERS = 4
ENABLE_RESUME_PROCESSING = True
RESUME_CHECKPOINT_FILE = "batch_processing_checkpoint.json"
