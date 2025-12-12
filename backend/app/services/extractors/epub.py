import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from typing import Dict, Any
from app.services.extractors.base import BaseExtractor


class EPUBExtractor(BaseExtractor):
    
    def extract(self, source: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        file_path = metadata.get('file_path', source)
        
        book = epub.read_epub(file_path)
        
        title = book.get_metadata('DC', 'title')
        title = title[0][0] if title else ''
        
        author = book.get_metadata('DC', 'creator')
        author = author[0][0] if author else ''
        
        content = {
            'text': '',
            'title': title,
            'author': author,
            'chapters': [],
        }
        
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                chapter_text = soup.get_text(separator='\n', strip=True)
                
                chapter_title = ''
                h1 = soup.find(['h1', 'h2', 'h3'])
                if h1:
                    chapter_title = h1.get_text().strip()
                
                content['chapters'].append({
                    'title': chapter_title,
                    'text': chapter_text
                })
                
                content['text'] += f"\n\n{chapter_text}"
        
        return content
    
    def extract_metadata(self, source: str) -> Dict[str, Any]:
        book = epub.read_epub(source)
        
        metadata = {
            'title': '',
            'author': '',
            'language': '',
            'publisher': '',
            'isbn': '',
        }
        
        title = book.get_metadata('DC', 'title')
        if title:
            metadata['title'] = title[0][0]
        
        author = book.get_metadata('DC', 'creator')
        if author:
            metadata['author'] = author[0][0]
        
        language = book.get_metadata('DC', 'language')
        if language:
            metadata['language'] = language[0][0]
        
        publisher = book.get_metadata('DC', 'publisher')
        if publisher:
            metadata['publisher'] = publisher[0][0]
        
        isbn = book.get_metadata('DC', 'identifier')
        if isbn:
            metadata['isbn'] = isbn[0][0]
        
        return metadata
