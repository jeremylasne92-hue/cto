import lancedb
from typing import List, Dict, Any, Optional
from app.config import settings
import pyarrow as pa


class VectorStore:
    _instance = None
    _db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorStore, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._db is None:
            self._db = lancedb.connect(settings.lance_db_path)
    
    def create_table_if_not_exists(self):
        try:
            self._db.open_table("embeddings")
        except:
            schema = pa.schema([
                pa.field("chunk_id", pa.string()),
                pa.field("source_id", pa.int32()),
                pa.field("text", pa.string()),
                pa.field("vector", pa.list_(pa.float32(), settings.embedding_dimension)),
                pa.field("chunk_type", pa.string()),
                pa.field("chunk_order", pa.int32()),
            ])
            self._db.create_table("embeddings", schema=schema)
    
    def add_embeddings(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]], source_id: int):
        self.create_table_if_not_exists()
        table = self._db.open_table("embeddings")
        
        data = []
        for chunk, embedding in zip(chunks, embeddings):
            data.append({
                "chunk_id": chunk['chunk_id'],
                "source_id": source_id,
                "text": chunk['text'],
                "vector": embedding,
                "chunk_type": chunk['chunk_type'],
                "chunk_order": chunk['chunk_order'],
            })
        
        table.add(data)
    
    def search(self, query_embedding: List[float], limit: int = 10, source_id: Optional[int] = None) -> List[Dict[str, Any]]:
        table = self._db.open_table("embeddings")
        
        results = table.search(query_embedding).limit(limit)
        
        if source_id:
            results = results.where(f"source_id = {source_id}")
        
        return results.to_list()
    
    def delete_by_source(self, source_id: int):
        table = self._db.open_table("embeddings")
        table.delete(f"source_id = {source_id}")
