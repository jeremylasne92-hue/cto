from .base import BaseAdapter
from ..models import SourceType
from typing import Dict, Any
import markdown
from bs4 import BeautifulSoup
import os
import re


class MarkdownAdapter(BaseAdapter):
    """Adapter for Markdown files"""
    
    def get_source_type(self):
        return SourceType.MARKDOWN
    
    def validate_source(self, source_url: str) -> bool:
        """Validate Markdown file path or URL"""
        # Check if it's a local file
        if os.path.isfile(source_url):
            return source_url.lower().endswith(('.md', '.markdown'))
        
        # Check if it's a URL to a markdown file
        if source_url.startswith(('http://', 'https://')):
            return source_url.lower().endswith(('.md', '.markdown'))
        
        return False
    
    async def extract_content(self, source_url: str) -> tuple[str, Dict[str, Any]]:
        """Extract and convert Markdown to plain text"""
        try:
            # Handle both local files and URLs
            if source_url.startswith(('http://', 'https://')):
                # For URLs, download first
                import requests
                response = requests.get(source_url)
                response.raise_for_status()
                markdown_content = response.text
            else:
                # Read local file
                with open(source_url, 'r', encoding='utf-8') as f:
                    markdown_content = f.read()
            
            # Convert markdown to HTML, then extract text
            md = markdown.Markdown(extensions=['extra', 'codehilite', 'toc'])
            html_content = md.convert(markdown_content)
            
            # Extract text from HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            text_content = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text_content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            content = ' '.join(chunk for chunk in chunks if chunk)
            
            # Extract title from first header or filename
            title = None
            title_match = re.search(r'^#\s+(.+)$', markdown_content, re.MULTILINE)
            if title_match:
                title = title_match.group(1).strip()
            else:
                # Use filename as title for local files
                if not source_url.startswith(('http://', 'https://')):
                    title = os.path.splitext(os.path.basename(source_url))[0]
            
            metadata = {
                "title": title,
                "url": source_url,
                "content_type": "text/markdown",
                "file_size": len(markdown_content.encode('utf-8')) if not source_url.startswith(('http://', 'https://')) else None,
            }
            
            return content, metadata
            
        except Exception as e:
            raise Exception(f"Markdown extraction failed: {str(e)}")