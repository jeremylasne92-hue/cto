from .base import BaseAdapter
from ..models import SourceType
from typing import Dict, Any
import os


class PlainTextAdapter(BaseAdapter):
    """Adapter for plain text files"""
    
    def get_source_type(self):
        return SourceType.PLAIN_TEXT
    
    def validate_source(self, source_url: str) -> bool:
        """Validate plain text file path or URL"""
        # Check if it's a local file
        if os.path.isfile(source_url):
            # Check if it's a text file (extension or mimetype)
            text_extensions = ('.txt', '.text', '.log', '.csv', '.json', '.xml', '.yml', '.yaml')
            return source_url.lower().endswith(text_extensions)
        
        # Check if it's a URL to a text file
        if source_url.startswith(('http://', 'https://')):
            text_extensions = ('.txt', '.text', '.log', '.csv', '.json', '.xml', '.yml', '.yaml')
            return source_url.lower().endswith(text_extensions)
        
        return False
    
    async def extract_content(self, source_url: str) -> tuple[str, Dict[str, Any]]:
        """Extract content from plain text file"""
        try:
            # Handle both local files and URLs
            if source_url.startswith(('http://', 'https://')):
                # For URLs, download first
                import requests
                response = requests.get(source_url)
                response.raise_for_status()
                content = response.text
            else:
                # Read local file with proper encoding detection
                with open(source_url, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            # Use filename as title for local files
            title = None
            if not source_url.startswith(('http://', 'https://')):
                title = os.path.splitext(os.path.basename(source_url))[0]
            
            metadata = {
                "title": title,
                "url": source_url,
                "content_type": "text/plain",
                "file_size": len(content.encode('utf-8')) if not source_url.startswith(('http://', 'https://')) else None,
            }
            
            return content, metadata
            
        except Exception as e:
            raise Exception(f"Plain text extraction failed: {str(e)}")