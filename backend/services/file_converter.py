import asyncio
from pathlib import Path
from typing import Optional
import aiofiles
import os
import platform

class FileConverter:
    def __init__(self):
        self.supported_formats = {
            '.docx': self._convert_docx_to_pdf,
            '.doc': self._convert_doc_to_pdf,
            '.rtf': self._convert_rtf_to_pdf,
            '.txt': self._convert_txt_to_pdf,
            '.jpg': self._convert_image_to_pdf,
            '.jpeg': self._convert_image_to_pdf,
            '.png': self._convert_image_to_pdf,
            '.bmp': self._convert_image_to_pdf,
            '.tiff': self._convert_image_to_pdf
        }
    
    async def convert_to_pdf(self, file_path: Path, file_extension: str) -> Path:
        """
        Convert a file to PDF format
        """
        if file_extension.lower() not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        converter_func = self.supported_formats[file_extension.lower()]
        return await converter_func(file_path)
    
    async def _convert_docx_to_pdf(self, file_path: Path) -> Path:
        """
        Convert DOCX to PDF with multiple methods to preserve formatting
        """
        pdf_path = file_path.with_suffix('.pdf')
        
        # Method 1: Try LibreOffice (best for preserving styles)
        try:
            if await self._convert_with_libreoffice(file_path, pdf_path):
                return pdf_path
        except Exception as e:
            print(f"LibreOffice conversion failed: {e}")
        
        # Method 2: Try pandoc (good for preserving basic formatting)
        try:
            if await self._convert_with_pandoc(file_path, pdf_path):
                return pdf_path
        except Exception as e:
            print(f"Pandoc conversion failed: {e}")
        
        # Method 3: Try docx2pdf as fallback (basic conversion)
        try:
            if await self._convert_with_docx2pdf(file_path, pdf_path):
                return pdf_path
        except Exception as e:
            print(f"docx2pdf conversion failed: {e}")
        
        # Method 4: Try python-docx + reportlab (manual conversion preserving some styles)
        try:
            if await self._convert_docx_manual(file_path, pdf_path):
                return pdf_path
        except Exception as e:
            print(f"Manual conversion failed: {e}")
        
        raise Exception("All DOCX to PDF conversion methods failed")
    
    async def _convert_with_libreoffice(self, file_path: Path, pdf_path: Path) -> bool:
        """
        Convert using LibreOffice (best for preserving styles)
        """
        try:
            import subprocess
            import shutil
            
            # Check if LibreOffice is available
            libreoffice_path = shutil.which('soffice') or shutil.which('libreoffice')
            if not libreoffice_path:
                return False
            
            # Run conversion in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                subprocess.run,
                [libreoffice_path, '--headless', '--convert-to', 'pdf', '--outdir', str(pdf_path.parent), str(file_path)],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0 and pdf_path.exists():
                return True
            return False
            
        except Exception:
            return False
    
    async def _convert_with_pandoc(self, file_path: Path, pdf_path: Path) -> bool:
        """
        Convert using pandoc (good for preserving basic formatting)
        """
        try:
            import pypandoc
            
            # Run conversion in thread pool
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                pypandoc.convert_file,
                str(file_path),
                'pdf',
                outputfile=str(pdf_path)
            )
            
            return pdf_path.exists()
            
        except Exception:
            return False
    
    async def _convert_with_docx2pdf(self, file_path: Path, pdf_path: Path) -> bool:
        """
        Convert using docx2pdf (basic conversion)
        """
        try:
            from docx2pdf import convert
            
            # Check if we're on Windows (docx2pdf requirement)
            if platform.system() != "Windows":
                return False
            
            # Run conversion in thread pool
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, convert, str(file_path), str(pdf_path))
            
            return pdf_path.exists()
            
        except Exception:
            return False
    
    async def _convert_docx_manual(self, file_path: Path, pdf_path: Path) -> bool:
        """
        Manual conversion using python-docx + reportlab (preserves some styles)
        """
        try:
            from docx import Document
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.units import inch
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
            from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
            
            # Read DOCX content
            loop = asyncio.get_event_loop()
            doc_content = await loop.run_in_executor(None, self._extract_docx_content, str(file_path))
            
            if not doc_content:
                return False
            
            # Create PDF with styles
            await loop.run_in_executor(
                None,
                self._create_styled_pdf,
                str(pdf_path),
                doc_content
            )
            
            return pdf_path.exists()
            
        except Exception:
            return False
    
    def _extract_docx_content(self, docx_path: str):
        """
        Extract content and styles from DOCX (runs in thread pool)
        """
        try:
            doc = Document(docx_path)
            content = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    # Extract text and basic formatting
                    text = paragraph.text
                    alignment = paragraph.alignment
                    
                    # Determine alignment
                    if alignment == 1:  # WD_ALIGN_PARAGRAPH.CENTER
                        align = TA_CENTER
                    elif alignment == 2:  # WD_ALIGN_PARAGRAPH.RIGHT
                        align = TA_RIGHT
                    elif alignment == 3:  # WD_ALIGN_PARAGRAPH.JUSTIFY
                        align = TA_JUSTIFY
                    else:
                        align = TA_LEFT
                    
                    # Check for bold/italic
                    is_bold = any(run.bold for run in paragraph.runs)
                    is_italic = any(run.italic for run in paragraph.runs)
                    
                    content.append({
                        'text': text,
                        'alignment': align,
                        'bold': is_bold,
                        'italic': is_italic
                    })
            
            return content
            
        except Exception:
            return None
    
    def _create_styled_pdf(self, pdf_path: str, content):
        """
        Create PDF with preserved styles (runs in thread pool)
        """
        try:
            doc = SimpleDocTemplate(pdf_path, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            
            # Create custom styles
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=6
            )
            
            bold_style = ParagraphStyle(
                'CustomBold',
                parent=styles['Heading1'],
                fontSize=12,
                spaceAfter=6
            )
            
            italic_style = ParagraphStyle(
                'CustomItalic',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=6,
                fontName='Helvetica-Oblique'
            )
            
            for item in content:
                text = item['text']
                alignment = item['alignment']
                is_bold = item['bold']
                is_italic = item['italic']
                
                # Choose style based on formatting
                if is_bold and is_italic:
                    style = ParagraphStyle(
                        'CustomBoldItalic',
                        parent=styles['Heading1'],
                        fontSize=12,
                        spaceAfter=6,
                        fontName='Helvetica-BoldOblique'
                    )
                elif is_bold:
                    style = bold_style
                elif is_italic:
                    style = italic_style
                else:
                    style = normal_style
                
                # Set alignment
                style.alignment = alignment
                
                # Create paragraph
                para = Paragraph(text, style)
                story.append(para)
                story.append(Spacer(1, 6))
            
            doc.build(story)
            
        except Exception as e:
            print(f"Error creating styled PDF: {e}")
            raise
    
    async def _convert_doc_to_pdf(self, file_path: Path) -> Path:
        """
        Convert DOC to PDF (same as DOCX for now)
        """
        return await self._convert_docx_to_pdf(file_path)
    
    async def _convert_rtf_to_pdf(self, file_path: Path) -> Path:
        """
        Convert RTF to PDF using pypandoc
        """
        try:
            import pypandoc
            
            pdf_path = file_path.with_suffix('.pdf')
            
            # Run conversion in thread pool
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, 
                pypandoc.convert_file, 
                str(file_path), 
                'pdf', 
                outputfile=str(pdf_path)
            )
            
            if pdf_path.exists():
                return pdf_path
            else:
                raise Exception("PDF conversion failed - file not created")
                
        except ImportError:
            raise Exception("pypandoc not installed. Please install it with: pip install pypandoc")
        except Exception as e:
            raise Exception(f"RTF to PDF conversion failed: {str(e)}")
    
    async def _convert_txt_to_pdf(self, file_path: Path) -> Path:
        """
        Convert TXT to PDF using reportlab
        """
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.units import inch
            
            pdf_path = file_path.with_suffix('.pdf')
            
            # Read text content
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                text_content = await f.read()
            
            # Create PDF
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._create_text_pdf,
                str(pdf_path),
                text_content
            )
            
            if pdf_path.exists():
                return pdf_path
            else:
                raise Exception("PDF conversion failed - file not created")
                
        except ImportError:
            raise Exception("reportlab not installed. Please install it with: pip install reportlab")
        except Exception as e:
            raise Exception(f"TXT to PDF conversion failed: {str(e)}")
    
    def _create_text_pdf(self, pdf_path: str, text_content: str):
        """
        Helper method to create PDF from text (runs in thread pool)
        """
        c = canvas.Canvas(pdf_path, pagesize=letter)
        width, height = letter
        
        # Set font and size
        c.setFont("Helvetica", 12)
        
        # Split text into lines
        lines = text_content.split('\n')
        y_position = height - 1 * inch  # Start 1 inch from top
        
        for line in lines:
            if y_position < 1 * inch:  # If we're near bottom, add new page
                c.showPage()
                c.setFont("Helvetica", 12)
                y_position = height - 1 * inch
            
            # Handle long lines by wrapping
            if len(line) > 80:  # Wrap at 80 characters
                words = line.split()
                current_line = ""
                for word in words:
                    if len(current_line + " " + word) <= 80:
                        current_line += " " + word if current_line else word
                    else:
                        c.drawString(1 * inch, y_position, current_line)
                        y_position -= 20
                        current_line = word
                if current_line:
                    c.drawString(1 * inch, y_position, current_line)
                    y_position -= 20
            else:
                c.drawString(1 * inch, y_position, line)
                y_position -= 20
        
        c.save()
    
    async def _convert_image_to_pdf(self, file_path: Path) -> Path:
        """
        Convert image to PDF using PIL/Pillow
        """
        try:
            from PIL import Image
            
            pdf_path = file_path.with_suffix('.pdf')
            
            # Open image and convert to RGB if necessary
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._convert_image_to_pdf_sync,
                str(file_path),
                str(pdf_path)
            )
            
            if pdf_path.exists():
                return pdf_path
            else:
                raise Exception("PDF conversion failed - file not created")
                
        except ImportError:
            raise Exception("Pillow not installed. Please install it with: pip install Pillow")
        except Exception as e:
            raise Exception(f"Image to PDF conversion failed: {str(e)}")
    
    def _convert_image_to_pdf_sync(self, image_path: str, pdf_path: str):
        """
        Helper method to convert image to PDF (runs in thread pool)
        """
        with Image.open(image_path) as img:
            # Convert to RGB if necessary (PDF doesn't support RGBA)
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Save as PDF
            img.save(pdf_path, 'PDF', resolution=100.0)
