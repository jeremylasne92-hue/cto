from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from ..models import Document, SourceMetadata
import hashlib
import json


class BaseAdapter(ABC):
    """Base class for all source adapters"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
    
    def _generate_hash(self, content: str, source_url: str) -> str:
        """Generate SHA256 hash for content + source"""
        combined = f"{source_url}:{content}"
        return hashlib.sha256(combined.encode('utf-8')).hexdigest()
    
    def _extract_metadata(self, raw_metadata: Dict[str, Any]) -> SourceMetadata:
        """Convert raw metadata to standardized SourceMetadata"""
        return SourceMetadata(**raw_metadata)
    
    @abstractmethod
    async def extract_content(self, source_url: str) -> tuple[str, Dict[str, Any]]:
        """
        Extract content from source
        
        Args:
            source_url: URL or path to the source
            
        Returns:
            Tuple of (content, raw_metadata)
        """
        pass
    
    async def adapt(self, source_url: str) -> Document:
        """
        Adapt source to normalized Document
        
        Args:
            source_url: URL or path to the source
            
        Returns:
            Normalized Document
        """
        content, raw_metadata = await self.extract_content(source_url)
        metadata = self._extract_metadata(raw_metadata)
        
        document = Document(
            source_type=self.get_source_type(),
            content=content,
            metadata=metadata,
            hash_sha256=self._generate_hash(content, source_url)
        )
        
        return document
    
    @abstractmethod
    def get_source_type(self):
        """Return the source type this adapter handles"""
        pass
    
    @abstractmethod
    def validate_source(self, source_url: str) -> bool:
        """
        Validate if the source URL/path is valid for this adapter
        
        Args:
            source_url: URL or path to validate
            
        Returns:
            True if valid, False otherwise
        """
        pass