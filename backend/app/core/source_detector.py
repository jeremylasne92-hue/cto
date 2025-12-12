import re
from pathlib import Path
from typing import Tuple, Optional
from urllib.parse import urlparse


class SourceDetector:
    
    YOUTUBE_PATTERNS = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
    ]
    
    FILE_EXTENSIONS = {
        'pdf': 'pdf',
        'epub': 'epub',
        'docx': 'docx',
        'doc': 'docx',
        'md': 'markdown',
        'txt': 'text',
        'html': 'html',
    }
    
    @classmethod
    def detect(cls, source: str, file_path: Optional[str] = None) -> Tuple[str, dict]:
        if cls.is_youtube_url(source):
            return 'youtube', {'url': source, 'video_id': cls.extract_youtube_id(source)}
        
        if cls.is_url(source):
            return 'web', {'url': source}
        
        if file_path:
            ext = Path(file_path).suffix.lower().lstrip('.')
            source_type = cls.FILE_EXTENSIONS.get(ext, 'unknown')
            return source_type, {'file_path': file_path, 'extension': ext}
        
        return 'text', {'content': source}
    
    @classmethod
    def is_youtube_url(cls, url: str) -> bool:
        for pattern in cls.YOUTUBE_PATTERNS:
            if re.search(pattern, url):
                return True
        return False
    
    @classmethod
    def extract_youtube_id(cls, url: str) -> Optional[str]:
        for pattern in cls.YOUTUBE_PATTERNS:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    @classmethod
    def is_url(cls, text: str) -> bool:
        try:
            result = urlparse(text)
            return all([result.scheme, result.netloc])
        except:
            return False
