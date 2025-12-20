from .base import BaseAdapter
from .youtube import YouTubeAdapter
from .pdf import PDFAdapter
from .web_page import WebPageAdapter
from .markdown import MarkdownAdapter
from .plain_text import PlainTextAdapter


class AdapterFactory:
    """Factory for creating source adapters"""
    
    def __init__(self):
        self._adapters = {}
        # Register built-in adapters
        from ..models import SourceType
        self._adapters[SourceType.YOUTUBE] = YouTubeAdapter
        self._adapters[SourceType.PDF] = PDFAdapter
        self._adapters[SourceType.WEB_PAGE] = WebPageAdapter
        self._adapters[SourceType.MARKDOWN] = MarkdownAdapter
        self._adapters[SourceType.PLAIN_TEXT] = PlainTextAdapter
    
    def register_adapter(self, source_type, adapter_class):
        """Register a new adapter for a source type"""
        self._adapters[source_type] = adapter_class
    
    def get_adapter(self, source_type, config=None):
        """Get an adapter instance for the specified source type"""
        from ..models import SourceType
        
        if source_type not in self._adapters:
            raise ValueError(f"No adapter registered for source type: {source_type}")
        
        adapter_class = self._adapters[source_type]
        return adapter_class(config)
    
    def get_supported_types(self):
        """Get list of supported source types"""
        from ..models import SourceType
        return list(self._adapters.keys())
    
    def detect_source_type(self, source_url):
        """Attempt to detect source type from URL"""
        for source_type, adapter_class in self._adapters.items():
            adapter = adapter_class()
            if adapter.validate_source(source_url):
                return source_type
        
        return None


__all__ = [
    "YouTubeAdapter",
    "PDFAdapter", 
    "WebPageAdapter",
    "MarkdownAdapter",
    "PlainTextAdapter",
    "BaseAdapter",
    "AdapterFactory"
]