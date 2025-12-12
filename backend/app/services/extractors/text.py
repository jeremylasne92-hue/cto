from typing import Dict, Any
from app.services.extractors.base import BaseExtractor


class TextExtractor(BaseExtractor):
    
    def extract(self, source: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        if 'content' in metadata:
            text = metadata['content']
        else:
            file_path = metadata.get('file_path', source)
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        
        content = {
            'text': text,
            'title': '',
            'author': '',
        }
        
        return content
    
    def extract_metadata(self, source: str) -> Dict[str, Any]:
        return {
            'title': '',
            'author': '',
        }
