import asyncio
from pathlib import Path
from typing import Dict, Any
import aiofiles

from .file_converter import FileConverter
from .text_extractor import TextExtractor

class DocumentProcessor:
    def __init__(self):
        self.file_converter = FileConverter()
        self.text_extractor = TextExtractor()
    
    async def process_document(self, file_path: Path, file_extension: str) -> Dict[str, Any]:
        """
        Process a document: convert to PDF and extract text
        """
        try:
            # Step 1: Convert to PDF if not already PDF
            if file_extension.lower() == '.pdf':
                pdf_path = file_path
                print(f"📄 Document is already PDF: {pdf_path}")
            else:
                print(f"🔄 Converting {file_extension} document to PDF...")
                pdf_path = await self.file_converter.convert_to_pdf(file_path, file_extension)
                print(f"✅ Conversion completed: {pdf_path}")
            
            # Validate PDF was created
            if not pdf_path.exists():
                raise Exception(f"PDF conversion failed - file not created at {pdf_path}")
            
            # Step 2: Extract text from the PDF
            print(f"🔍 Extracting text from PDF: {pdf_path}")
            text_content = await self.text_extractor.extract_text_from_pdf(pdf_path)
            print(f"📝 Extracted text length: {len(text_content) if text_content else 0}")
            
            # The text extractor now raises exceptions instead of returning error messages
            # So we don't need to check for error message strings anymore
            
            # Validate text extraction
            if not text_content or text_content.strip() == "":
                print("❌ Text extraction failed - no text content was extracted")
                raise Exception("Text extraction failed - no text content was extracted. This document might be image-based or have security restrictions.")
            
            print(f"✅ Text extraction successful - Content preview: {text_content[:100]}...")
            
            # Step 3: Save text content to file
            # Extract file_id from filename - it's the UUID part before the first underscore
            # The filename format is: {file_id}_{original_filename}
            # Use a more robust method to extract file_id (UUID is always 36 characters)
            filename_stem = file_path.stem
            if len(filename_stem) >= 36:
                file_id = filename_stem[:36]  # UUID is exactly 36 characters
            else:
                # Fallback to underscore split method
                file_id = filename_stem.split('_')[0]
            
            text_file_path = file_path.parent / f"{file_id}_text.txt"
            
            async with aiofiles.open(text_file_path, 'w', encoding='utf-8') as f:
                await f.write(text_content)
            
            print(f"💾 Text content saved to: {text_file_path}")
            
            return {
                "pdf_path": str(pdf_path),
                "text_content": text_content,
                "text_file_path": str(text_file_path),
                "conversion_method": "pdf_direct" if file_extension.lower() == '.pdf' else "converted"
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Document processing failed: {error_msg}")
            
            # Provide more helpful error messages for common OCR scenarios
            if "OCR" in error_msg and "not available" in error_msg:
                raise Exception(f"OCR Required: {error_msg}\n\nTo fix this:\n1. Install Tesseract OCR from https://github.com/UB-Mannheim/tesseract/wiki\n2. Restart the application\n3. Try uploading your document again")
            elif "OCR" in error_msg and "failed" in error_msg:
                raise Exception(f"OCR Processing Failed: {error_msg}\n\nPossible solutions:\n1. Ensure the document images are clear and high quality\n2. Try a different document\n3. Check if the document has security restrictions")
            else:
                raise Exception(f"Error processing document: {error_msg}")
