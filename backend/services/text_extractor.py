import asyncio
from pathlib import Path
from typing import Optional, List
import aiofiles
import os
import platform
from PIL import Image

# Import text extraction libraries
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import fitz
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False

class TextExtractor:
    def __init__(self):
        self.ocr_available = self._check_ocr_availability()
        print(f"OCR available: {self.ocr_available}")
        print(f"pdfplumber available: {PDFPLUMBER_AVAILABLE}")
        print(f"PyPDF2 available: {PYPDF2_AVAILABLE}")
        print(f"fitz available: {FITZ_AVAILABLE}")
    
    def _check_ocr_availability(self) -> bool:
        """
        Check if Tesseract OCR is available
        """
        try:
            import pytesseract
            # Try to get tesseract version to verify it's working
            pytesseract.get_tesseract_version()
            print("✅ Tesseract OCR is available and working")
            return True
        except (ImportError, Exception) as e:
            print(f"❌ OCR not available: {e}")
            print("💡 To enable OCR for image-based PDFs, install Tesseract OCR:")
            print("   Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
            print("   macOS: brew install tesseract")
            print("   Ubuntu: sudo apt-get install tesseract-ocr")
            return False
    
    async def _has_text_content(self, pdf_path: Path) -> bool:
        """
        Check if PDF contains actual text content (not just images)
        """
        try:
            if FITZ_AVAILABLE:
                # Use PyMuPDF to check if there are text objects
                doc = fitz.open(str(pdf_path))
                has_text = False
                
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    # Check if page has text objects
                    text_dict = page.get_text("dict")
                    if text_dict.get("blocks"):
                        for block in text_dict["blocks"]:
                            if block.get("type") == 0:  # Text block
                                if block.get("lines"):
                                    for line in block["lines"]:
                                        if line.get("spans"):
                                            for span in line["spans"]:
                                                if span.get("text") and len(span["text"].strip()) > 0:
                                                    has_text = True
                                                    break
                                            if has_text:
                                                break
                                    if has_text:
                                        break
                        if has_text:
                            break
                
                doc.close()
                print(f"PDF text object detection: {'Has text objects' if has_text else 'No text objects (likely image-based)'}")
                return has_text
            
            return True  # Assume it has text if we can't check
        except Exception as e:
            print(f"Error checking PDF text content: {e}")
            return True  # Assume it has text if we can't check
    
    async def _force_text_extraction(self, pdf_path: Path) -> str:
        """
        Force text extraction with different settings when normal extraction fails
        """
        try:
            if FITZ_AVAILABLE:
                print("Trying forced text extraction with PyMuPDF...")
                doc = fitz.open(str(pdf_path))
                text_content = ""
                
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    # Try different text extraction methods
                    try:
                        # Method 1: Get text with specific flags
                        page_text = page.get_text("text", flags=fitz.TEXTFLAGS_TEXT)
                        if page_text and len(page_text.strip()) > 0:
                            text_content += page_text + "\n"
                            continue
                    except:
                        pass
                    
                    try:
                        # Method 2: Get text with different flags
                        page_text = page.get_text("text", flags=fitz.TEXTFLAGS_WORDS)
                        if page_text and len(page_text.strip()) > 0:
                            text_content += page_text + "\n"
                            continue
                    except:
                        pass
                    
                    try:
                        # Method 3: Get text with no flags
                        page_text = page.get_text("text")
                        if page_text and len(page_text.strip()) > 0:
                            text_content += page_text + "\n"
                            continue
                    except:
                        pass
                
                doc.close()
                return text_content
            
            return ""
        except Exception as e:
            print(f"Forced text extraction failed: {e}")
            return ""
    
    async def _log_pdf_structure(self, pdf_path: Path) -> None:
        """
        Log detailed information about PDF structure for debugging
        """
        try:
            if FITZ_AVAILABLE:
                print(f"📋 Analyzing PDF structure: {pdf_path}")
                doc = fitz.open(str(pdf_path))
                
                print(f"   Pages: {len(doc)}")
                
                for page_num in range(min(3, len(doc))):  # Only check first 3 pages
                    page = doc.load_page(page_num)
                    page_dict = page.get_text("dict")
                    
                    text_blocks = 0
                    image_blocks = 0
                    total_text_length = 0
                    
                    if page_dict.get("blocks"):
                        for block in page_dict["blocks"]:
                            if block.get("type") == 0:  # Text block
                                text_blocks += 1
                                if block.get("lines"):
                                    for line in block["lines"]:
                                        if line.get("spans"):
                                            for span in line["spans"]:
                                                if span.get("text"):
                                                    total_text_length += len(span["text"])
                            elif block.get("type") == 1:  # Image block
                                image_blocks += 1
                    
                    print(f"   Page {page_num + 1}: {text_blocks} text blocks, {image_blocks} image blocks, {total_text_length} text chars")
                
                doc.close()
                print(f"📋 PDF structure analysis complete")
        except Exception as e:
            print(f"Error analyzing PDF structure: {e}")
    
    async def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """
        Extract text from PDF file, using OCR only when absolutely necessary
        """
        try:
            print(f"Starting text extraction from: {pdf_path}")
            
            # First check if the PDF actually contains text objects (not just images)
            has_text_objects = await self._has_text_content(pdf_path)
            print(f"PDF contains text objects: {has_text_objects}")
            
            # Log PDF structure for debugging
            await self._log_pdf_structure(pdf_path)
            
            # First try to extract text directly using multiple methods
            text_content = await self._extract_text_direct(pdf_path)
            print(f"Direct text extraction result length: {len(text_content) if text_content else 0}")
            
            # Check if we got meaningful text content (not just whitespace or very short content)
            if text_content and len(text_content.strip()) > 10:  # Require at least 10 non-whitespace characters
                print(f"✅ Direct text extraction successful - found {len(text_content.strip())} characters")
                return text_content
            
            # If the PDF has text objects but we couldn't extract them, there might be an issue
            if has_text_objects and (not text_content or len(text_content.strip()) == 0):
                print("⚠️  PDF has text objects but extraction failed - trying alternative methods...")
                # Try to force extraction with different settings
                text_content = await self._force_text_extraction(pdf_path)
                if text_content and len(text_content.strip()) > 10:
                    print(f"✅ Force extraction successful - found {len(text_content.strip())} characters")
                    return text_content
            
            # If we got some text but it's very short, we'll try to combine with other methods
            # The _extract_text_direct method already tries multiple methods and combines results
            
            # Only use OCR if we have no meaningful text, no text objects detected, and OCR is available
            if self.ocr_available and not has_text_objects:
                print("No meaningful text found and no text objects detected - attempting OCR...")
                try:
                    ocr_text = await self._extract_text_with_ocr(pdf_path)
                    print(f"OCR text extraction result length: {len(ocr_text) if ocr_text else 0}")
                    if ocr_text and len(ocr_text.strip()) > 10:
                        print("✅ OCR successfully extracted meaningful text")
                        return ocr_text
                    else:
                        print("⚠️  OCR extracted text but it's too short or empty")
                except Exception as ocr_error:
                    print(f"❌ OCR failed: {ocr_error}")
                    # Continue with whatever text we have
            elif self.ocr_available and has_text_objects:
                print("⚠️  PDF has text objects but extraction failed - OCR not recommended for text-based PDFs")
            else:
                print("⚠️  OCR not available - cannot process image-based PDFs")
            
            # Final check - if we still have no meaningful text, provide a helpful error message
            print("⚠️  WARNING: All text extraction methods failed to find meaningful content!")
            print("   This usually means the PDF contains only images or has security restrictions.")
            
            # IMPORTANT: If we have no meaningful text and OCR is not available, we MUST return an error
            # This ensures the application properly handles the failure case
            if not self.ocr_available:
                print("   💡 OCR is not available - install Tesseract OCR to extract text from images")
                raise Exception("Text extraction failed - This document appears to be image-based. To extract text from images, please install Tesseract OCR on your system.")
            else:
                print("   💡 OCR was attempted but failed - the images might be too low quality or corrupted")
                raise Exception("Text extraction failed - This document appears to be image-based but OCR extraction failed. Please try a different file or ensure the images are clear and readable.")
            
        except Exception as e:
            print(f"Text extraction failed: {str(e)}")
            raise Exception(f"Text extraction failed: {str(e)}")
    
    def _extract_text_with_fitz(self, pdf_path: str) -> str:
        """
        Extract text using PyMuPDF (fitz) - runs in thread pool
        """
        try:
            doc = fitz.open(pdf_path)
            text_content = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text_content += page.get_text()
            
            doc.close()
            return text_content
        except Exception as e:
            print(f"fitz text extraction error: {e}")
            return ""
    
    async def _extract_text_direct(self, pdf_path: Path) -> str:
        """
        Try to extract text directly from PDF using multiple methods
        """
        text_content = ""
        
        # Try pdfplumber first (usually best for text extraction)
        if PDFPLUMBER_AVAILABLE:
            try:
                print("Trying pdfplumber text extraction...")
                pdfplumber_text = await self._extract_text_with_pdfplumber(str(pdf_path))
                if pdfplumber_text and len(pdfplumber_text.strip()) > 10:
                    print("✅ pdfplumber text extraction successful")
                    return pdfplumber_text
                elif pdfplumber_text and len(pdfplumber_text.strip()) > 0:
                    text_content = pdfplumber_text
                    print(f"⚠️  pdfplumber found some text ({len(pdfplumber_text.strip())} chars), but it's short")
            except Exception as e:
                print(f"pdfplumber extraction failed: {e}")
        
        # Try PyPDF2 as fallback
        if PYPDF2_AVAILABLE:
            try:
                print("Trying PyPDF2 text extraction...")
                pypdf2_text = await self._extract_text_with_pypdf2(str(pdf_path))
                if pypdf2_text and len(pypdf2_text.strip()) > 10:
                    print("✅ PyPDF2 text extraction successful")
                    return pypdf2_text
                elif pypdf2_text and len(pypdf2_text.strip()) > 0:
                    # If we already have some text from pdfplumber, combine them
                    if text_content:
                        combined_text = text_content + "\n" + pypdf2_text
                        if len(combined_text.strip()) > 10:
                            print(f"✅ Combined text extraction successful ({len(combined_text.strip())} chars)")
                            return combined_text
                    else:
                        text_content = pypdf2_text
                        print(f"⚠️  PyPDF2 found some text ({len(pypdf2_text.strip())} chars), but it's short")
            except Exception as e:
                print(f"PyPDF2 extraction failed: {e}")
        
        # Try PyMuPDF (fitz) as another alternative
        if FITZ_AVAILABLE:
            try:
                print("Trying PyMuPDF (fitz) text extraction...")
                fitz_text = await self._extract_text_with_fitz(str(pdf_path))
                if fitz_text and len(fitz_text.strip()) > 10:
                    print("✅ PyMuPDF text extraction successful")
                    return fitz_text
                elif fitz_text and len(fitz_text.strip()) > 0:
                    # If we already have some text from other methods, combine them
                    if text_content:
                        combined_text = text_content + "\n" + fitz_text
                        if len(combined_text.strip()) > 10:
                            print(f"✅ Combined text extraction successful ({len(combined_text.strip())} chars)")
                            return combined_text
                    else:
                        text_content = fitz_text
                        print(f"⚠️  PyMuPDF found some text ({len(fitz_text.strip())} chars), but it's short")
            except Exception as e:
                print(f"PyMuPDF extraction failed: {e}")
        
        return text_content
    
    def _extract_text_with_pdfplumber(self, pdf_path: str) -> str:
        """
        Extract text using pdfplumber - runs in thread pool
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text_content = ""
                for page in pdf.pages:
                    if page.extract_text():
                        text_content += page.extract_text() + "\n"
                return text_content
        except Exception as e:
            print(f"pdfplumber text extraction error: {e}")
            return ""
    
    def _extract_text_with_pypdf2(self, pdf_path: str) -> str:
        """
        Extract text using PyPDF2 - runs in thread pool
        """
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text_content = ""
                for page in reader.pages:
                    text_content += page.extract_text() + "\n"
                return text_content
        except Exception as e:
            print(f"PyPDF2 text extraction error: {e}")
            return ""
    
    async def _extract_text_with_ocr(self, pdf_path: Path) -> str:
        """
        Extract text from PDF using OCR (for image-based PDFs)
        """
        if not self.ocr_available:
            raise Exception("OCR not available. Please install Tesseract OCR and pytesseract")
        
        try:
            import pytesseract
            from pdf2image import convert_from_path
            
            print("🔄 Converting PDF to images for OCR processing...")
            
            # Convert PDF pages to images
            loop = asyncio.get_event_loop()
            images = await loop.run_in_executor(
                None,
                self._convert_pdf_to_images,
                str(pdf_path)
            )
            
            if not images:
                raise Exception("Failed to convert PDF to images")
            
            print(f"📄 Converted {len(images)} pages to images")
            
            # Extract text from each image using OCR
            all_text = []
            for i, image in enumerate(images):
                print(f"🔍 Processing page {i+1}/{len(images)} with OCR...")
                
                # Preprocess image for better OCR
                processed_image = await loop.run_in_executor(
                    None,
                    self._preprocess_image_for_ocr,
                    image
                )
                
                # Extract text using Tesseract with optimized settings
                page_text = await loop.run_in_executor(
                    None,
                    pytesseract.image_to_string,
                    processed_image,
                    config='--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,!?@#$%&*()_+-=[]{}|;:"\'<>?/\\ '
                )
                
                if page_text and page_text.strip():
                    # Clean up the extracted text
                    cleaned_text = self._clean_ocr_text(page_text)
                    if cleaned_text:
                        all_text.append(f"--- Page {i+1} ---\n{cleaned_text}")
                        print(f"✅ Page {i+1}: Extracted {len(cleaned_text)} characters")
                    else:
                        print(f"⚠️  Page {i+1}: No text extracted after cleaning")
                else:
                    print(f"⚠️  Page {i+1}: No text extracted")
            
            if all_text:
                final_text = "\n\n".join(all_text)
                print(f"🎉 OCR completed successfully! Total text length: {len(final_text)}")
                return final_text
            else:
                raise Exception("OCR extracted no text from any page")
            
        except ImportError as e:
            if "pdf2image" in str(e):
                raise Exception("pdf2image not installed. Please install it with: pip install pdf2image")
            elif "pytesseract" in str(e):
                raise Exception("pytesseract not installed. Please install it with: pip install pytesseract")
            else:
                raise Exception(f"OCR dependency not available: {str(e)}")
        except Exception as e:
            print(f"OCR processing failed: {str(e)}")
            raise Exception(f"OCR processing failed: {str(e)}")
    
    def _clean_ocr_text(self, text: str) -> str:
        """
        Clean up OCR extracted text to remove noise and improve readability
        """
        if not text:
            return ""
        
        # Remove excessive whitespace and normalize
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove lines that are mostly whitespace or very short
            if len(line.strip()) > 2:
                # Clean up the line
                cleaned_line = line.strip()
                # Remove excessive spaces
                cleaned_line = ' '.join(cleaned_line.split())
                if cleaned_line:
                    cleaned_lines.append(cleaned_line)
        
        return '\n'.join(cleaned_lines)
    
    def _convert_pdf_to_images(self, pdf_path: str) -> List[Image.Image]:
        """
        Convert PDF pages to PIL Images (runs in thread pool)
        """
        try:
            print(f"Converting PDF to images with higher DPI for better OCR...")
            # Try to use poppler if available (better quality)
            try:
                images = convert_from_path(pdf_path, dpi=400, poppler_path=None)
                print(f"✅ Converted to {len(images)} images at 400 DPI")
            except Exception:
                # Fallback to default conversion
                images = convert_from_path(pdf_path, dpi=300)
                print(f"✅ Converted to {len(images)} images at 300 DPI")
            
            return images
        except Exception as e:
            print(f"PDF to image conversion failed: {e}")
            raise Exception(f"Failed to convert PDF to images: {str(e)}")
    
    def _preprocess_image_for_ocr(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR results (runs in thread pool)
        """
        try:
            # Convert to grayscale if not already
            if image.mode != 'L':
                image = image.convert('L')
            
            # Enhance contrast
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.8)  # Increased contrast
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.5)  # Increased sharpness
            
            # Enhance brightness slightly
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.1)
            
            return image
        except Exception as e:
            print(f"Image preprocessing failed: {e}")
            # Return original image if preprocessing fails
            return image
    
    async def extract_text_from_image(self, image_path: Path) -> str:
        """
        Extract text from image file using OCR
        """
        if not self.ocr_available:
            raise Exception("OCR not available. Please install Tesseract OCR and pytesseract")
        
        try:
            import pytesseract
            
            # Open and preprocess image
            loop = asyncio.get_event_loop()
            processed_image = await loop.run_in_executor(
                None,
                self._preprocess_image_for_ocr,
                Image.open(image_path)
            )
            
            # Extract text using Tesseract
            text_content = await loop.run_in_executor(
                None,
                pytesseract.image_to_string,
                processed_image,
                config='--psm 6'
            )
            
            return text_content.strip()
            
        except Exception as e:
            raise Exception(f"Image OCR failed: {str(e)}")
    
    def is_ocr_available(self) -> bool:
        """
        Check if OCR functionality is available
        """
        return self.ocr_available
