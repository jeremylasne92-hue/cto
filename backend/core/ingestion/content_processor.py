from typing import List, Dict, Any
import uuid
from datetime import datetime


class ContentProcessor:
    def __init__(self):
        pass
    
    def process_content(self, content: str, source_id: str, chunk_size: int = 1000) -> List[Dict[str, Any]]:
        chunks = self._chunk_text(content, chunk_size)
        
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            processed_chunks.append({
                'id': str(uuid.uuid4()),
                'source_id': source_id,
                'content': chunk,
                'chunk_index': i,
                'metadata': '{}',
                'created_at': datetime.utcnow().isoformat()
            })
        
        return processed_chunks
    
    def _chunk_text(self, text: str, chunk_size: int) -> List[str]:
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            current_chunk.append(word)
            current_size += len(word) + 1
            
            if current_size >= chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_size = 0
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
