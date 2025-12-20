from .base import BaseAdapter
from ..models import SourceType
from typing import Dict, Any
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


class WebPageAdapter(BaseAdapter):
    """Adapter for generic web pages using requests and BeautifulSoup"""
    
    def get_source_type(self):
        return SourceType.WEB_PAGE
    
    def validate_source(self, source_url: str) -> bool:
        """Validate web page URL"""
        try:
            result = urlparse(source_url)
            return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
        except:
            return False
    
    async def extract_content(self, source_url: str) -> tuple[str, Dict[str, Any]]:
        """Extract text content from web page"""
        try:
            # Fetch the page
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(source_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            content = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            content = ' '.join(chunk for chunk in chunks if chunk)
            
            # Extract metadata
            title = soup.title.string if soup.title else None
            
            # Try to get description from meta tags
            description = None
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                description = meta_desc.get('content')
            
            # Get author if available
            author = None
            meta_author = soup.find('meta', attrs={'name': 'author'})
            if meta_author:
                author = meta_author.get('content')
            
            # Parse URL for domain
            parsed_url = urlparse(source_url)
            domain = parsed_url.netloc
            
            metadata = {
                "title": title,
                "url": source_url,
                "domain": domain,
                "html_title": title,
                "content_type": response.headers.get('content-type', 'text/html'),
                "content_length": len(response.content),
            }
            
            if description:
                metadata["description"] = description
            if author:
                metadata["author"] = author
            
            return content, metadata
            
        except Exception as e:
            raise Exception(f"Web page extraction failed: {str(e)}")