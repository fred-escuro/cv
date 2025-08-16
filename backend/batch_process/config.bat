@echo off
REM Quick Configuration Manager for Batch CV Processor
REM This script provides quick access to configuration options

echo ========================================
echo    Batch CV Processor Configuration
echo ========================================
echo.

echo Configuration Options:
echo 1. Show current configuration
echo 2. Create .env template
echo 3. Interactive setup
echo 4. Edit .env file
echo 5. View .env file
echo 6. Exit
echo.

set /p CHOICE="Choose option (1-6): "

if "%CHOICE%"=="1" goto :show_config
if "%CHOICE%"=="2" goto :create_template
if "%CHOICE%"=="3" goto :interactive_setup
if "%CHOICE%"=="4" goto :edit_env
if "%CHOICE%"=="5" goto :view_env
if "%CHOICE%"=="6" goto :exit
goto :invalid

:show_config
echo.
echo [INFO] Showing current configuration...
python batch_cv_processor.py --show-config
goto :end

:create_template
echo.
echo [INFO] Creating .env template...
python batch_cv_processor.py --create-env
goto :end

:interactive_setup
echo.
echo [INFO] Starting interactive setup...
python setup_config.py
goto :end

:edit_env
echo.
echo [INFO] Opening .env file for editing...
if exist ".env" (
    notepad .env
    echo [OK] .env file opened in Notepad
) else (
    echo [WARNING] .env file not found. Creating one first...
    python setup_config.py
)
goto :end

:view_env
echo.
echo [INFO] Viewing .env file contents...
if exist ".env" (
    type .env
) else (
    echo [WARNING] .env file not found.
    echo To create one, run: python setup_config.py
)
goto :end

:invalid
echo.
echo [ERROR] Invalid option. Please choose 1-6.
goto :end

:end
echo.
echo ========================================
echo    Configuration completed!
echo ========================================
echo.
pause

:exit
exit /b 0
