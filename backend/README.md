# CV Transform API Backend

A FastAPI-based backend service for processing CV documents. This service can convert various document formats to PDF and extract text content using OCR.

## Features

- **Document Upload**: Accepts PDF, DOC, DOCX, RTF, TXT, JSON, and image files (JPG, PNG, BMP, TIFF)
- **PDF Conversion**: Converts all supported formats to PDF
- **Text Extraction**: Extracts text content from documents using OCR for images
- **File Management**: Download converted PDFs and manage uploaded files
- **RESTful API**: Clean API endpoints for all operations

## Supported File Formats

### Input Formats
- **PDF** (.pdf) - Direct processing
- **Microsoft Word** (.doc, .docx) - Converted to PDF
- **Rich Text Format** (.rtf) - Converted to PDF
- **Plain Text** (.txt) - Converted to PDF
- **JSON** (.json) - Converted to PDF
- **Images** (.jpg, .jpeg, .png, .bmp, .tiff) - OCR processing and PDF conversion

### Output Formats
- **PDF** - Converted document
- **Text** - Extracted content

## Installation

### Prerequisites

1. **Python 3.8+**
2. **Tesseract OCR** (for image text extraction)

#### Installing Tesseract OCR

**Windows:**
```bash
# Download and install from: https://github.com/UB-Mannheim/tesseract/wiki
# Add to PATH: C:\Program Files\Tesseract-OCR
```

**macOS:**
```bash
brew install tesseract
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install tesseract-ocr
```

### Setup

1. **Clone the repository and navigate to backend:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure Tesseract path (if needed):**
Edit `services/text_extractor.py` and uncomment/modify the tesseract path:
```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

## Usage

### Starting the Server

```bash
# Using the startup script
python start.py

# Or directly with uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, visit:
- **Interactive API docs**: http://localhost:8000/docs
- **ReDoc documentation**: http://localhost:8000/redoc

## API Endpoints

### POST `/upload-cv`
Upload and process a CV document.

**Request:**
- Content-Type: `multipart/form-data`
- Body: File upload

**Response:**
```json
{
  "success": true,
  "file_id": "uuid-string",
  "original_filename": "document.pdf",
  "pdf_path": "/path/to/converted.pdf",
  "text_content": "Extracted text content...",
  "file_type": ".pdf"
}
```

### GET `/download-pdf/{file_id}`
Download the converted PDF file.

### GET `/document/{file_id}`
Get document information and text content.

### DELETE `/document/{file_id}`
Delete uploaded document and its processed files.

## Environment Variables

- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `RELOAD`: Enable auto-reload (default: true)

## File Storage

- **Uploads**: Stored in `uploads/` directory
- **Temporary files**: Stored in `temp/` directory
- **File naming**: `{uuid}_{original_filename}`

## Error Handling

The API includes comprehensive error handling for:
- Invalid file types
- File processing errors
- OCR failures
- File not found errors

## Development

### Project Structure
```
backend/
├── main.py                 # FastAPI application
├── start.py               # Startup script
├── requirements.txt       # Python dependencies
├── services/             # Business logic
│   ├── __init__.py
│   ├── document_processor.py
│   ├── file_converter.py
│   └── text_extractor.py
├── uploads/              # Uploaded files
└── temp/                 # Temporary files
```

### Adding New File Formats

1. Add the format to `supported_formats` in `FileConverter`
2. Implement the conversion method
3. Update the API validation

## Troubleshooting

### Common Issues

1. **Tesseract not found**: Install Tesseract OCR and configure the path
2. **File conversion fails**: Check file format support and dependencies
3. **OCR quality issues**: Ensure images are clear and well-lit
4. **Memory issues**: Large files may require more memory allocation

### Logs

Check the console output for detailed error messages and processing logs.

## License

This project is part of the CV Transform application.

