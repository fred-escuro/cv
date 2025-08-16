# Installing Tesseract OCR for Image-Based PDF Processing

This guide will help you install Tesseract OCR on your system to enable text extraction from image-based PDFs and scanned documents.

## Why Tesseract OCR?

Tesseract OCR (Optical Character Recognition) is required to extract text from:
- Scanned PDF documents
- Image-based PDFs
- Photos of documents
- Any document that contains only images

## Installation by Operating System

### Windows

1. **Download Tesseract:**
   - Go to: https://github.com/UB-Mannheim/tesseract/wiki
   - Download the latest installer for your Windows version (32-bit or 64-bit)

2. **Install Tesseract:**
   - Run the downloaded installer
   - **Important:** During installation, note the installation path (default: `C:\Program Files\Tesseract-OCR`)
   - Make sure to check "Add to PATH" during installation

3. **Verify Installation:**
   - Open Command Prompt or PowerShell
   - Run: `tesseract --version`
   - You should see version information

4. **Restart Your Application:**
   - After installation, restart your CV Transform application
   - OCR functionality should now be available

### macOS

1. **Using Homebrew (Recommended):**
   ```bash
   brew install tesseract
   ```

2. **Verify Installation:**
   ```bash
   tesseract --version
   ```

3. **Restart Your Application:**
   - After installation, restart your CV Transform application

### Ubuntu/Debian Linux

1. **Install Tesseract:**
   ```bash
   sudo apt-get update
   sudo apt-get install tesseract-ocr
   ```

2. **Verify Installation:**
   ```bash
   tesseract --version
   ```

3. **Restart Your Application:**
   - After installation, restart your CV Transform application

### CentOS/RHEL/Fedora

1. **Install Tesseract:**
   ```bash
   # CentOS/RHEL 7
   sudo yum install tesseract
   
   # CentOS/RHEL 8+
   sudo dnf install tesseract
   
   # Fedora
   sudo dnf install tesseract
   ```

2. **Verify Installation:**
   ```bash
   tesseract --version
   ```

3. **Restart Your Application:**
   - After installation, restart your CV Transform application

## Testing OCR Installation

After installing Tesseract, you can test if it's working:

1. **Run the test script:**
   ```bash
   cd backend
   python test_ocr.py
   ```

2. **Expected output:**
   ```
   🚀 Starting OCR and PDF processing tests...
   
   🔍 Testing Tesseract OCR installation...
   ✅ pytesseract Python package is installed
   ✅ Tesseract OCR is working - Version: 5.x.x
   
   🔍 Testing pdf2image...
   ✅ pdf2image is installed
   
   🔍 Testing Pillow (PIL)...
   ✅ Pillow is installed
   
   🎉 All tests passed! OCR should work for image-based PDFs.
   ```

## Troubleshooting

### Common Issues

1. **"Tesseract is not working" error:**
   - Make sure Tesseract is added to your system PATH
   - Try restarting your terminal/command prompt
   - Restart your application after installation

2. **"pytesseract not found" error:**
   - Install the Python package: `pip install pytesseract`
   - Make sure you're in the correct virtual environment

3. **"pdf2image not found" error:**
   - Install the Python package: `pip install pdf2image`
   - On Windows, you might also need to install poppler

4. **OCR quality issues:**
   - Ensure document images are clear and high resolution (300+ DPI)
   - Check that text is readable and not too small
   - Avoid documents with complex backgrounds or poor contrast

### Windows-Specific Issues

1. **PATH not updated:**
   - Manually add Tesseract installation path to system PATH
   - Default path: `C:\Program Files\Tesseract-OCR`
   - Restart your computer after updating PATH

2. **Permission issues:**
   - Run Command Prompt as Administrator
   - Check Windows Defender/antivirus isn't blocking Tesseract

### macOS-Specific Issues

1. **Homebrew not found:**
   - Install Homebrew first: https://brew.sh/
   - Then install Tesseract: `brew install tesseract`

2. **Permission denied:**
   - Check System Preferences > Security & Privacy
   - Allow Tesseract if prompted

## What Happens After Installation

Once Tesseract OCR is properly installed:

1. **Automatic Detection:** The system will automatically detect OCR availability
2. **Image Processing:** Image-based PDFs will be converted to images and processed with OCR
3. **Text Extraction:** Text will be extracted from images and made searchable
4. **Better Results:** Higher quality text extraction from scanned documents

## Supported Document Types

With OCR enabled, you can process:
- ✅ Scanned PDFs
- ✅ Image-based PDFs
- ✅ Photos of documents
- ✅ Screenshots with text
- ✅ Any document containing readable text in images

## Performance Notes

- **Processing Time:** OCR processing takes longer than text-based PDFs
- **Image Quality:** Higher resolution images (300+ DPI) produce better results
- **Text Recognition:** Clear, high-contrast text works best
- **Language Support:** Tesseract supports multiple languages (English by default)

## Need Help?

If you're still experiencing issues:

1. Check the test script output: `python test_ocr.py`
2. Verify Tesseract is in your PATH: `tesseract --version`
3. Check the application logs for specific error messages
4. Ensure all Python dependencies are installed: `pip install -r requirements.txt`
