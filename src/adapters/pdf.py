from .base import BaseAdapter
from ..models import SourceType
from typing import Dict, Any
import fitz  # PyMuPDF
import os
import tempfile
import requests


class PDFAdapter(BaseAdapter):
    """Adapter for PDF documents using PyMuPDF"""
    
    def get_source_type(self):
        return SourceType.PDF
    
    def validate_source(self, source_url: str) -> bool:
        """Validate PDF file path or URL"""
        # Check if it's a local file
        if os.path.isfile(source_url):
            return source_url.lower().endswith('.pdf')
        
        # Check if it's a URL ending with .pdf
        if source_url.startswith(('http://', 'https://')):
            return source_url.lower().endswith('.pdf')
        
        return False
    
    async def extract_content(self, source_url: str) -> tuple[str, Dict[str, Any]]:
        """Extract text content from PDF"""
        try:
            # Handle both local files and URLs
            if source_url.startswith(('http://', 'https://')):
                # For URLs, we would need to download first
                # For now, this is a simplified version
                import requests
                response = requests.get(source_url)
                response.raise_for_status()
                
                # Create temporary file
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                    temp_file.write(response.content)
                    pdf_path = temp_file.name
            else:
                pdf_path = source_url
            
            # Open PDF with PyMuPDF
            doc = fitz.open(pdf_path)
            
            # Extract text from all pages
            full_text = []
            pdf_metadata = {}
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                full_text.append(text)
            
            # Extract metadata
            metadata_raw = doc.metadata
            pdf_metadata = {
                "title": metadata_raw.get("title", ""),
                "author": metadata_raw.get("author", ""),
                "subject": metadata_raw.get("subject", ""),
                "creator": metadata_raw.get("creator", ""),
                "producer": metadata_raw.get("producer", ""),
                "creation_date": metadata_raw.get("creationDate", ""),
                "modification_date": metadata_raw.get("modDate", ""),
            }
            
            doc.close()
            
            # Clean up temporary file if we created one
            if source_url.startswith(('http://', 'https://')):
                os.unlink(pdf_path)
            
            content = "\n\n".join(full_text)
            
            # Standard metadata
            metadata = {
                "title": pdf_metadata.get("title", ""),
                "author": pdf_metadata.get("author", ""),
                "url": source_url,
                "page_count": len(doc) if not source_url.startswith(('http://', 'https://')) else len(doc),
                "pdf_metadata": pdf_metadata,
                "content_type": "application/pdf",
                "file_size": os.path.getsize(pdf_path) if os.path.isfile(pdf_path) and not source_url.startswith(('http://', 'https://')) else None,
            }
            
            return content, metadata
            
        except Exception as e:
            raise Exception(f"PDF extraction failed: {str(e)}")