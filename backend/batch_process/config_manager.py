#!/usr/bin/env python3
"""
Configuration Manager for Batch CV Processor

This module loads configuration from .env files and provides easy access
to all configurable settings with sensible defaults.
"""

import os
from pathlib import Path
from typing import List, Optional, Union
from dotenv import load_dotenv

class ConfigManager:
    """
    Manages configuration for the batch processor by loading settings from .env files
    and providing easy access to all configurable values.
    """
    
    def __init__(self, env_file: str = None):
        """
        Initialize the configuration manager
        
        Args:
            env_file: Path to .env file (defaults to .env in current directory)
        """
        self.env_file = env_file or ".env"
        self._load_environment()
        self._set_defaults()
    
    def _load_environment(self):
        """Load environment variables from .env file"""
        try:
            # Try to load from the specified .env file
            if os.path.exists(self.env_file):
                load_dotenv(self.env_file)
                print(f"✅ Loaded configuration from: {self.env_file}")
            else:
                # Try to load from .env in current directory
                current_env = Path.cwd() / ".env"
                if current_env.exists():
                    load_dotenv(current_env)
                    print(f"✅ Loaded configuration from: {current_env}")
                else:
                    print(f"⚠️ No .env file found. Using default configuration.")
                    print(f"   Create {self.env_file} or .env file to customize settings.")
        except Exception as e:
            print(f"⚠️ Warning: Could not load .env file: {e}")
            print("   Using default configuration.")
    
    def _set_defaults(self):
        """Set default values for configuration"""
        # These defaults will be used if not specified in .env file
        self._defaults = {
            'DEFAULT_CV_FOLDER': 'C:/CVs',
            'DEFAULT_FILE_LIMIT': 0,
            'MAX_FILE_SIZE_MB': 100,
            'MIN_FILE_SIZE_KB': 1,
            'DEFAULT_FILE_TYPES': 'pdf,docx,doc,rtf,txt,json,jpg,jpeg,png,bmp,tiff',
            'DEFAULT_LOG_FILE': 'batch_processing_log',
            'DEFAULT_ERROR_LOG_FILE': 'batch_error_log',
            'LOG_DIRECTORY': 'logs',
            'LOG_LEVEL': 'INFO',
            'SHOW_DETAILED_OUTPUT': True,
            'PROCESSING_DELAY_SECONDS': 0.5,
            'BATCH_SIZE': 50,
            'MAX_CONCURRENT_PROCESSES': 1,
            'SKIP_CORRUPTED_FILES': True,
            'CONTINUE_ON_ERROR': True,
            'MAX_ERRORS_BEFORE_STOP': 100,
            'DATABASE_TIMEOUT_SECONDS': 30,
            'MAX_RETRIES': 3,
            'ENABLE_PROGRESS_BAR': True,
            'ENABLE_PARALLEL_PROCESSING': False,
            'PARALLEL_WORKERS': 4,
            'GENERATE_SUMMARY_REPORT': True,
            'SAVE_ERROR_LOG': True,
            'SAVE_SUCCESS_LOG': False,
            'CREATE_BACKUP_COPIES': False,
            'BACKUP_DIRECTORY': 'backups',
            'CLEANUP_TEMP_FILES': True,
            'CLEANUP_FAILED_FILES': False,
            'ENABLE_EMAIL_NOTIFICATIONS': False,
            'NOTIFICATION_EMAIL': '',
            'ENABLE_WEBHOOK_NOTIFICATIONS': False,
            'WEBHOOK_URL': '',
            'ENABLE_RESUME_PROCESSING': True,
            'RESUME_CHECKPOINT_FILE': 'batch_processing_checkpoint.json',
            'ENABLE_DRY_RUN': False
        }
    
    def get(self, key: str, default: any = None) -> any:
        """
        Get a configuration value
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        # First try environment variable
        value = os.getenv(key)
        
        # If not found, try defaults
        if value is None:
            value = self._defaults.get(key, default)
        
        # Convert string values to appropriate types
        if value is not None:
            value = self._convert_value(key, value)
        
        return value
    
    def _convert_value(self, key: str, value: str) -> any:
        """
        Convert string values to appropriate Python types
        
        Args:
            key: Configuration key
            value: String value from environment
            
        Returns:
            Converted value
        """
        # Boolean conversions
        if key in ['SHOW_DETAILED_OUTPUT', 'SKIP_CORRUPTED_FILES', 'CONTINUE_ON_ERROR',
                   'ENABLE_PROGRESS_BAR', 'ENABLE_PARALLEL_PROCESSING', 'GENERATE_SUMMARY_REPORT',
                   'SAVE_ERROR_LOG', 'SAVE_SUCCESS_LOG', 'CREATE_BACKUP_COPIES',
                   'CLEANUP_TEMP_FILES', 'CLEANUP_FAILED_FILES', 'ENABLE_EMAIL_NOTIFICATIONS',
                   'ENABLE_WEBHOOK_NOTIFICATIONS', 'ENABLE_RESUME_PROCESSING', 'ENABLE_DRY_RUN']:
            return value.lower() in ['true', '1', 'yes', 'on']
        
        # Integer conversions
        if key in ['DEFAULT_FILE_LIMIT', 'MAX_FILE_SIZE_MB', 'MIN_FILE_SIZE_KB',
                   'BATCH_SIZE', 'MAX_CONCURRENT_PROCESSES', 'MAX_ERRORS_BEFORE_STOP',
                   'DATABASE_TIMEOUT_SECONDS', 'MAX_RETRIES', 'PARALLEL_WORKERS']:
            try:
                return int(value)
            except (ValueError, TypeError):
                return 0
        
        # Float conversions
        if key in ['PROCESSING_DELAY_SECONDS']:
            try:
                return float(value)
            except (ValueError, TypeError):
                return 0.5
        
        # Return as string for everything else
        return value
    
    def get_file_types(self) -> List[str]:
        """
        Get list of file types to process
        
        Returns:
            List of file extensions (with dots)
        """
        file_types_str = self.get('DEFAULT_FILE_TYPES', '')
        if not file_types_str:
            return []
        
        # Convert to list and ensure extensions have dots
        file_types = []
        for ext in file_types_str.split(','):
            ext = ext.strip().lower()
            if ext and not ext.startswith('.'):
                ext = f'.{ext}'
            if ext:
                file_types.append(ext)
        
        return file_types
    
    def get_cv_folder(self) -> str:
        """
        Get the default CV folder to process
        
        Returns:
            Path to CV folder
        """
        return self.get('DEFAULT_CV_FOLDER', 'C:/CVs')
    
    def get_file_limit(self) -> int:
        """
        Get the default file limit
        
        Returns:
            Maximum number of files to process (0 = no limit)
        """
        return self.get('DEFAULT_FILE_LIMIT', 0)
    
    def get_log_file(self) -> str:
        """
        Get the default log file name
        
        Returns:
            Log file name (without extension)
        """
        return self.get('DEFAULT_LOG_FILE', 'batch_processing_log')
    
    def get_error_log_file(self) -> str:
        """
        Get the default error log file name
        
        Returns:
            Error log file name (without extension)
        """
        return self.get('DEFAULT_ERROR_LOG_FILE', 'batch_error_log')
    
    def get_log_directory(self) -> str:
        """
        Get the log directory
        
        Returns:
            Log directory path
        """
        return self.get('LOG_DIRECTORY', 'logs')
    
    def get_processing_delay(self) -> float:
        """
        Get the processing delay between files
        
        Returns:
            Delay in seconds
        """
        return self.get('PROCESSING_DELAY_SECONDS', 0.5)
    
    def get_max_file_size(self) -> int:
        """
        Get maximum file size in bytes
        
        Returns:
            Maximum file size in bytes
        """
        max_mb = self.get('MAX_FILE_SIZE_MB', 100)
        return max_mb * 1024 * 1024 if max_mb > 0 else 0
    
    def get_min_file_size(self) -> int:
        """
        Get minimum file size in bytes
        
        Returns:
            Minimum file size in bytes
        """
        min_kb = self.get('MIN_FILE_SIZE_KB', 1)
        return min_kb * 1024 if min_kb > 0 else 0
    
    def is_dry_run(self) -> bool:
        """
        Check if dry run mode is enabled
        
        Returns:
            True if dry run mode is enabled
        """
        return self.get('ENABLE_DRY_RUN', False)
    
    def get_supported_extensions(self) -> List[str]:
        """
        Get list of supported file extensions
        
        Returns:
            List of supported file extensions
        """
        return ['.pdf', '.doc', '.docx', '.rtf', '.txt', '.json', 
                '.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    
    def print_configuration(self):
        """Print current configuration for debugging"""
        print("🔧 Batch Processor Configuration")
        print("=" * 50)
        
        config_items = [
            ("CV Folder", self.get_cv_folder()),
            ("File Limit", f"{self.get_file_limit()}" if self.get_file_limit() > 0 else "No limit"),
            ("File Types", ", ".join(self.get_file_types()) if self.get_file_types() else "All supported"),
            ("Max File Size", f"{self.get('MAX_FILE_SIZE_MB')} MB"),
            ("Min File Size", f"{self.get('MIN_FILE_SIZE_KB')} KB"),
            ("Processing Delay", f"{self.get_processing_delay()} seconds"),
            ("Log File", self.get_log_file()),
            ("Error Log File", self.get_error_log_file()),
            ("Log Directory", self.get_log_directory()),
            ("Log Level", self.get('LOG_LEVEL')),
            ("Dry Run Mode", "Enabled" if self.is_dry_run() else "Disabled"),
            ("Skip Corrupted Files", "Yes" if self.get('SKIP_CORRUPTED_FILES') else "No"),
            ("Continue On Error", "Yes" if self.get('CONTINUE_ON_ERROR') else "No"),
            ("Max Errors Before Stop", self.get('MAX_ERRORS_BEFORE_STOP')),
            ("Progress Bar", "Enabled" if self.get('ENABLE_PROGRESS_BAR') else "Disabled"),
            ("Parallel Processing", "Enabled" if self.get('ENABLE_PARALLEL_PROCESSING') else "Disabled"),
        ]
        
        for key, value in config_items:
            print(f"   {key:<25}: {value}")
        
        print("=" * 50)
    
    def create_env_template(self, output_file: str = ".env.template"):
        """
        Create a .env template file with current configuration
        
        Args:
            output_file: Output file path
        """
        try:
            with open(output_file, 'w') as f:
                f.write("# Batch CV Processor Configuration Template\n")
                f.write("# Copy this file to .env and modify the values as needed\n\n")
                
                # Write all configuration values
                for key, default_value in self._defaults.items():
                    if isinstance(default_value, bool):
                        f.write(f"{key}={str(default_value).lower()}\n")
                    elif isinstance(default_value, (int, float)):
                        f.write(f"{key}={default_value}\n")
                    else:
                        f.write(f"{key}={default_value}\n")
                
            print(f"✅ Environment template created: {output_file}")
            
        except Exception as e:
            print(f"❌ Failed to create environment template: {e}")

# Global configuration instance
config = ConfigManager()

# Convenience functions for easy access
def get_config() -> ConfigManager:
    """Get the global configuration instance"""
    return config

def get_cv_folder() -> str:
    """Get the default CV folder"""
    return config.get_cv_folder()

def get_file_limit() -> int:
    """Get the default file limit"""
    return config.get_file_limit()

def get_file_types() -> List[str]:
    """Get the default file types"""
    return config.get_file_types()

def get_log_file() -> str:
    """Get the default log file name"""
    return config.get_log_file()

def get_error_log_file() -> str:
    """Get the default error log file name"""
    return config.get_error_log_file()

def is_dry_run() -> bool:
    """Check if dry run mode is enabled"""
    return config.is_dry_run()
