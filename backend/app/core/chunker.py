import hashlib
from typing import List, Dict, Any
from app.config import settings


class SemanticChunker:
    
    def __init__(self, chunk_size: int = None, overlap: int = None):
        self.chunk_size = chunk_size or settings.chunk_size
        self.overlap = overlap or settings.chunk_overlap
    
    def chunk_text(self, text: str, chunk_type: str = "text", metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        if metadata is None:
            metadata = {}
        
        tokens = text.split()
        chunks = []
        position = 0
        chunk_order = 0
        
        while position < len(tokens):
            chunk_tokens = tokens[position:position + self.chunk_size]
            chunk_text = ' '.join(chunk_tokens)
            
            chunk_id = self._generate_chunk_id(chunk_text, chunk_order)
            
            chunks.append({
                'chunk_id': chunk_id,
                'text': chunk_text,
                'chunk_type': chunk_type,
                'position': position,
                'chunk_order': chunk_order,
                'metadata': metadata.copy()
            })
            
            chunk_order += 1
            position += self.chunk_size - self.overlap
        
        return chunks
    
    def chunk_with_structure(self, content: str, structure_type: str = "markdown") -> List[Dict[str, Any]]:
        if structure_type == "markdown":
            return self._chunk_markdown(content)
        elif structure_type == "code":
            return self._chunk_code(content)
        else:
            return self.chunk_text(content)
    
    def _chunk_markdown(self, content: str) -> List[Dict[str, Any]]:
        lines = content.split('\n')
        chunks = []
        current_chunk = []
        current_heading = ""
        chunk_order = 0
        position = 0
        
        for line in lines:
            if line.startswith('#'):
                if current_chunk:
                    chunk_text = '\n'.join(current_chunk)
                    chunk_id = self._generate_chunk_id(chunk_text, chunk_order)
                    chunks.append({
                        'chunk_id': chunk_id,
                        'text': chunk_text,
                        'chunk_type': 'markdown_section',
                        'position': position,
                        'chunk_order': chunk_order,
                        'metadata': {'heading': current_heading}
                    })
                    chunk_order += 1
                    position += len(current_chunk)
                    current_chunk = []
                current_heading = line
            
            current_chunk.append(line)
        
        if current_chunk:
            chunk_text = '\n'.join(current_chunk)
            chunk_id = self._generate_chunk_id(chunk_text, chunk_order)
            chunks.append({
                'chunk_id': chunk_id,
                'text': chunk_text,
                'chunk_type': 'markdown_section',
                'position': position,
                'chunk_order': chunk_order,
                'metadata': {'heading': current_heading}
            })
        
        return chunks
    
    def _chunk_code(self, content: str) -> List[Dict[str, Any]]:
        lines = content.split('\n')
        chunk_size = 50
        chunks = []
        position = 0
        chunk_order = 0
        
        for i in range(0, len(lines), chunk_size):
            chunk_lines = lines[i:i + chunk_size]
            chunk_text = '\n'.join(chunk_lines)
            chunk_id = self._generate_chunk_id(chunk_text, chunk_order)
            
            chunks.append({
                'chunk_id': chunk_id,
                'text': chunk_text,
                'chunk_type': 'code',
                'position': position,
                'chunk_order': chunk_order,
                'metadata': {'start_line': i, 'end_line': i + len(chunk_lines)}
            })
            
            chunk_order += 1
            position += len(chunk_lines)
        
        return chunks
    
    def _generate_chunk_id(self, text: str, order: int) -> str:
        content = f"{text}_{order}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
