from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseExtractor(ABC):
    
    @abstractmethod
    def extract(self, source: Any, metadata: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def extract_metadata(self, source: Any) -> Dict[str, Any]:
        pass
