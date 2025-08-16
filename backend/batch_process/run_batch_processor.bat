@echo off
REM Batch CV Processor Runner
REM This batch file makes it easy to run the batch processor on Windows
REM Supports .env configuration with command line overrides

echo ========================================
echo    Batch CV Processor
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if the script exists
if not exist "batch_cv_processor.py" (
    echo ERROR: batch_cv_processor.py not found
    echo Please ensure you're running this from the batch_process directory
    pause
    exit /b 1
)

echo Python found: 
python --version
echo.

REM Check if .env file exists
if exist ".env" (
    echo [OK] .env configuration file found
    echo.
    echo Current configuration:
    python batch_cv_processor.py --show-config
    echo.
) else (
    echo [WARNING] No .env file found. Using default configuration.
    echo.
    echo To create a .env file, run: python setup_config.py
    echo Or copy env_example.txt to .env and edit it.
    echo.
)

echo Configuration Options:
echo 1. Use .env settings (if available)
echo 2. Override with command line arguments
echo 3. Interactive input
echo.

set /p CHOICE="Choose option (1-3, default: 1): "

if "%CHOICE%"=="" set CHOICE=1

if "%CHOICE%"=="1" goto :use_env
if "%CHOICE%"=="2" goto :use_args
if "%CHOICE%"=="3" goto :interactive
goto :use_env

:use_env
echo.
echo [INFO] Using .env configuration...
echo.
echo Available commands:
echo   python batch_cv_processor.py                    # Use .env settings
echo   python batch_cv_processor.py --show-config     # Show current config
echo   python batch_cv_processor.py --create-env      # Create .env template
echo.
set /p EXECUTE="Press Enter to run with .env settings, or type a command: "
if "%EXECUTE%"=="" (
    echo [INFO] Running with .env settings...
    python batch_cv_processor.py
) else (
    echo [INFO] Running custom command: %EXECUTE%
    %EXECUTE%
)
goto :end

:use_args
echo.
echo [INFO] Command Line Arguments Mode
echo.
echo Usage examples:
echo   python batch_cv_processor.py "C:\CVs" --limit 100
echo   python batch_cv_processor.py "C:\CVs" --file-types "pdf,docx"
echo   python batch_cv_processor.py "C:\CVs" --limit 50 --file-types "pdf"
echo.
set /p COMMAND="Enter your command: "
if not "%COMMAND%"=="" (
    echo [INFO] Running command: %COMMAND%
    %COMMAND%
) else (
    echo [WARNING] No command entered. Exiting.
)
goto :end

:interactive
echo.
echo [INFO] Interactive Configuration Mode
echo.

REM Get folder path from user
set /p FOLDER_PATH="Enter the path to your CV folder (e.g., C:\CVs): "

REM Check if folder exists
if not exist "%FOLDER_PATH%" (
    echo ERROR: Folder does not exist: %FOLDER_PATH%
    pause
    exit /b 1
)

echo.
echo Processing folder: %FOLDER_PATH%
echo.

REM Get file type filter from user
set /p FILE_TYPES="Enter file types to process (e.g., pdf,docx,doc) or press Enter for all: "

REM Get limit from user
set /p LIMIT="Enter maximum number of files to process or press Enter for no limit: "

REM Get log file name
set /p LOG_FILE="Enter custom log file name (without extension) or press Enter for default: "

echo.
echo Starting batch processing...
echo.

REM Build command
set COMMAND=python batch_cv_processor.py "%FOLDER_PATH%"

if not "%FILE_TYPES%"=="" (
    set COMMAND=%COMMAND% --file-types "%FILE_TYPES%"
)

if not "%LIMIT%"=="" (
    set COMMAND=%COMMAND% --limit %LIMIT%
)

if not "%LOG_FILE%"=="" (
    set COMMAND=%COMMAND% --log-file "%LOG_FILE%"
)

REM Run the processor
echo Command: %COMMAND%
echo.
%COMMAND%

:end
echo.
echo ========================================
echo    Processing completed!
echo ========================================
echo.
echo Check the console output above for results
echo Log files are saved in the logs directory
echo.
echo Configuration files:
echo   .env                    - Main configuration
echo   env_example.txt         - Configuration template
echo   setup_config.py         - Interactive setup
echo.
pause
