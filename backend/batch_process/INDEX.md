# Batch Process Folder - File Index

This folder contains all the batch processing related files and scripts for the CV Transform application.

## 📁 File Structure

```
batch_process/
├── batch_cv_processor.py          # Main batch processor script
├── batch_processor_config.py      # Legacy configuration file
├── config_manager.py              # 🆕 Environment-based configuration manager
├── env_example.txt                # 🆕 .env configuration template
├── setup_config.py                # 🆕 Interactive configuration setup script
├── requirements.txt                # 🆕 Python dependencies
├── example_batch_usage.py         # Example usage scripts
├── test_batch_processor.py        # Test script
├── run_batch_processor.bat        # Windows batch file runner
├── run_batch_processor.ps1        # PowerShell script runner
├── README.md                      # Comprehensive documentation
├── INDEX.md                       # This file
├── ENHANCEMENTS_SUMMARY.md        # Summary of new features
└── sample_log_structure.md        # Sample log file structures
```

## 🚀 Quick Start

### 1. **Setup Configuration (First Time)**
```bash
cd batch_process

# Interactive setup (recommended)
python setup_config.py

# Or create .env manually from template
copy env_example.txt .env
# Edit .env file with your preferences
```

### 2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 3. **Run the Processor**

#### From Backend Directory (Recommended)
```bash
# Run with .env configuration
python run_batch_processor.py

# Override specific settings
python run_batch_processor.py "C:/CVs" --limit 100 --file-types "pdf,docx"
```

#### From Batch Process Directory
```bash
cd batch_process

# Run with .env configuration
python batch_cv_processor.py

# Override specific settings
python batch_cv_processor.py "C:/CVs" --limit 50
```

#### Using Runner Scripts
```bash
# Windows Batch File (interactive)
run_batch_processor.bat

# PowerShell Script (advanced)
.\run_batch_processor.ps1
.\run_batch_processor.ps1 -ShowConfig
.\run_batch_processor.ps1 -CreateEnv

# Quick Configuration
config.bat
```

### From Batch Process Directory
```bash
cd batch_process

# Run directly
python batch_cv_processor.py "C:/CVs"

# Use Windows batch file
run_batch_processor.bat

# Use PowerShell script
.\run_batch_processor.ps1 "C:/CVs"
```

## 📋 File Descriptions

### Core Files
- **`batch_cv_processor.py`** - Main Python script that processes CV files
- **`batch_processor_config.py`** - Legacy configuration file (deprecated)
- **`config_manager.py`** - Environment-based configuration manager
- **`env_example.txt`** - Template for .env configuration file
- **`setup_config.py`** - Interactive script to create .env configuration
- **`requirements.txt`** - Python package dependencies

### Runner Scripts
- **`run_batch_processor.bat`** - Windows batch file with .env support and interactive options
- **`run_batch_processor.ps1`** - PowerShell script with advanced .env configuration features
- **`config.bat`** - Quick configuration management script for Windows users

### Examples and Testing
- **`example_batch_usage.py`** - Shows how to use the processor programmatically
- **`test_batch_processor.py`** - Tests the processor functionality

### Documentation
- **`README.md`** - Complete documentation and usage guide
- **`INDEX.md`** - This overview file
- **`ENHANCEMENTS_SUMMARY.md`** - Summary of new features and enhancements
- **`sample_log_structure.md`** - Sample log file structures and examples

## 🔧 Configuration

### Environment Variables (.env file)
The batch processor now uses a `.env` file for configuration:

```bash
# Core Settings
DEFAULT_CV_FOLDER=C:/CVs
DEFAULT_FILE_LIMIT=0
DEFAULT_FILE_TYPES=pdf,docx,doc,rtf,txt,json,jpg,jpeg,png,bmp,tiff

# Logging
DEFAULT_LOG_FILE=batch_processing_log
DEFAULT_ERROR_LOG_FILE=batch_error_log
LOG_DIRECTORY=logs

# Processing
PROCESSING_DELAY_SECONDS=0.5
BATCH_SIZE=50
MAX_FILE_SIZE_MB=100
MIN_FILE_SIZE_KB=1

# Error Handling
SKIP_CORRUPTED_FILES=true
CONTINUE_ON_ERROR=true
MAX_ERRORS_BEFORE_STOP=100
```

### Configuration Commands
```bash
# Show current configuration
python batch_cv_processor.py --show-config

# Create .env template
python batch_cv_processor.py --create-env

# Interactive setup
python setup_config.py
```

## 🔧 Usage Examples

### Basic Processing
```bash
# Process using .env configuration
python run_batch_processor.py

# Override folder from .env
python run_batch_processor.py "C:/CVs"
```

### Advanced Processing
```bash
# Process only PDF and DOCX files, limit to 50 files
python run_batch_processor.py "C:/CVs" --file-types "pdf,docx" --limit 50
```

### Programmatic Usage
```python
from batch_process.batch_cv_processor import BatchCVProcessor

processor = BatchCVProcessor()
# ... use the processor
```

## 📖 For More Information

- See `README.md` for complete documentation
- Run `python batch_cv_processor.py --help` for command-line options
- Check `example_batch_usage.py` for programming examples

## 🆘 Getting Help

If you encounter issues:
1. Check the console output for error messages
2. Review the generated log files
3. Ensure the backend is running
4. Verify file permissions and paths
5. Check the README.md for troubleshooting tips
