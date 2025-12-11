import os
from typing import List, Optional, Dict, Any
import lancedb
import numpy as np


class LanceDBManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.db = None
        self.embeddings_table = None
    
    def initialize(self):
        os.makedirs(self.db_path, exist_ok=True)
        self.db = lancedb.connect(self.db_path)
        
        try:
            self.embeddings_table = self.db.open_table('embeddings')
        except Exception:
            sample_data = [{
                'id': 'sample',
                'vector': np.zeros(384).tolist(),
                'chunk_id': 'sample',
                'metadata': '{}'
            }]
            self.embeddings_table = self.db.create_table('embeddings', data=sample_data, mode='overwrite')
    
    def add_embedding(self, chunk_id: str, vector: List[float], metadata: Optional[Dict[str, Any]] = None):
        if not self.embeddings_table:
            raise RuntimeError("Embeddings table not initialized")
        
        import json
        data = [{
            'id': chunk_id,
            'vector': vector,
            'chunk_id': chunk_id,
            'metadata': json.dumps(metadata or {})
        }]
        
        self.embeddings_table.add(data)
    
    def search_similar(self, query_vector: List[float], limit: int = 10) -> List[Dict[str, Any]]:
        if not self.embeddings_table:
            raise RuntimeError("Embeddings table not initialized")
        
        results = self.embeddings_table.search(query_vector).limit(limit).to_list()
        return results
    
    def delete_embedding(self, chunk_id: str):
        if not self.embeddings_table:
            raise RuntimeError("Embeddings table not initialized")
        
        self.embeddings_table.delete(f"chunk_id = '{chunk_id}'")
    
    def get_embedding_count(self) -> int:
        if not self.embeddings_table:
            return 0
        
        try:
            return len(self.embeddings_table.to_pandas())
        except Exception:
            return 0
