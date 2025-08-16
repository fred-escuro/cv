import asyncio
from pathlib import Path
from typing import List, Dict, Any
import re

class TextLineProcessor:
    """
    Service to process extracted text content into searchable line segments
    """
    
    def __init__(self):
        self.min_line_length = 3  # Minimum characters for a valid line
        
    async def process_text_to_lines(self, text_content: str, file_id: str) -> List[Dict[str, Any]]:
        """
        Process extracted text content into individual searchable lines
        """
        if not text_content:
            return []
        
        lines = text_content.split('\n')
        processed_lines = []
        
        for i, line in enumerate(lines):
            # Clean and validate the line
            cleaned_line = self._clean_line(line)
            
            if self._is_valid_line(cleaned_line):
                line_type = self._classify_line_type(cleaned_line)
                
                processed_lines.append({
                    'fileId': file_id,
                    'lineNumber': i + 1,
                    'lineText': cleaned_line,
                    'lineType': line_type
                })
        
        return processed_lines
    
    def _clean_line(self, line: str) -> str:
        """
        Clean individual text line
        """
        if not line:
            return ""
        
        # Remove excessive whitespace
        cleaned = ' '.join(line.split())
        
        # Remove common OCR artifacts
        cleaned = re.sub(r'[^\w\s\-.,!?@#$%&*()_+=<>/\\[\]{}|;:"\']', '', cleaned)
        
        return cleaned.strip()
    
    def _is_valid_line(self, line: str) -> bool:
        """
        Check if a line is valid for storage
        """
        if not line:
            return False
        
        # Must have minimum length
        if len(line) < self.min_line_length:
            return False
        
        # Must contain at least one letter or number
        if not re.search(r'[a-zA-Z0-9]', line):
            return False
        
        return True
    
    def _classify_line_type(self, line: str) -> str:
        """
        Classify the type of text line for better search context
        """
        line_lower = line.lower()
        
        # Check for common patterns
        if re.match(r'^[A-Z][A-Z\s]+$', line):  # ALL CAPS lines
            return 'header'
        elif re.match(r'^\d+\.', line):  # Numbered lists
            return 'list_item'
        elif re.match(r'^[•\-*]\s', line):  # Bullet points
            return 'list_item'
        elif re.match(r'^\w+:\s', line):  # Key-value pairs
            return 'key_value'
        elif len(line) < 50 and re.search(r'@', line):  # Email addresses
            return 'contact_info'
        elif re.search(r'\d{4}', line) and re.search(r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)', line_lower):
            return 'date_info'
        else:
            return 'content'
