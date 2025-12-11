import lancedb
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import uuid
import logging


class VectorService:
    """Service for managing vector embeddings with LanceDB"""
    
    def __init__(self, db_path: str = "lancedb", model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.db_path = db_path
        self.model_name = model_name
        self.db = None
        self.table = None
        self.model = None
        self.logger = logging.getLogger(__name__)
    
    def initialize(self):
        """Initialize LanceDB connection and embedding model"""
        try:
            # Initialize LanceDB
            self.db = lancedb.connect(self.db_path)
            
            # Load embedding model
            self.model = SentenceTransformer(self.model_name)
            
            # Create or open table
            try:
                self.table = self.db.open_table("document_chunks")
                self.logger.info("Connected to existing LanceDB table")
            except:
                # Create new table with schema
                self.table = self.db.create_table(
                    "document_chunks",
                    schema={
                        "id": "varchar",
                        "document_id": "varchar",
                        "chunk_id": "varchar",
                        "content": "varchar",
                        "embedding": "vector(384)",  # all-MiniLM-L6-v2 has 384 dimensions
                        "metadata": "json",
                        "created_at": "timestamp"
                    },
                    mode="create"
                )
                self.logger.info("Created new LanceDB table")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize vector service: {e}")
            raise
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts"""
        if not self.model:
            raise ValueError("Model not initialized. Call initialize() first.")
        
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return embeddings
    
    def upsert_chunks(self, chunks: List[Dict[str, Any]]) -> bool:
        """Upsert document chunks with embeddings to LanceDB"""
        try:
            if not self.table:
                raise ValueError("Table not initialized. Call initialize() first.")
            
            # Prepare data for LanceDB
            texts = [chunk["content"] for chunk in chunks]
            embeddings = self.embed_texts(texts)
            
            # Format data
            data = []
            for i, chunk in enumerate(chunks):
                data.append({
                    "id": chunk.get("id", str(uuid.uuid4())),
                    "document_id": chunk["document_id"],
                    "chunk_id": chunk["id"],
                    "content": chunk["content"],
                    "embedding": embeddings[i],
                    "metadata": chunk.get("metadata", {}),
                    "created_at": chunk.get("created_at")
                })
            
            # Upsert to LanceDB
            # LanceDB doesn't have direct upsert, so we handle it manually
            try:
                self.table.add(data)
                self.logger.info(f"Added {len(data)} chunks to LanceDB")
            except Exception as e:
                self.logger.error(f"Failed to add chunks to LanceDB: {e}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to upsert chunks: {e}")
            return False
    
    def search_similar(self, query: str, limit: int = 10, filter_conditions: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for similar chunks using vector similarity"""
        try:
            if not self.table:
                raise ValueError("Table not initialized. Call initialize() first.")
            
            # Generate query embedding
            query_embedding = self.embed_texts([query])
            
            # Build search query
            search_args = {
                "query_vector": query_embedding[0],
                "nprobes": 10,  # Search parameters for better recall
                "refine_factor": 10
            }
            
            if filter_conditions:
                # Add filter conditions if provided
                # Note: LanceDB filter syntax is specific
                filter_str = self._build_filter_string(filter_conditions)
                if filter_str:
                    search_args["where"] = filter_str
            
            # Execute search
            results = self.table.search(**search_args).limit(limit).to_pydantic()
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "id": result.id,
                    "document_id": result.document_id,
                    "chunk_id": result.chunk_id,
                    "content": result.content,
                    "metadata": result.metadata,
                    "created_at": result.created_at,
                    "score": getattr(result, 'score', None)
                })
            
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"Failed to search similar chunks: {e}")
            return []
    
    def _build_filter_string(self, conditions: Dict[str, Any]) -> str:
        """Build LanceDB filter string from conditions"""
        # This is a simplified version - LanceDB has complex filter syntax
        # For now, we'll handle basic equality conditions
        filters = []
        for key, value in conditions.items():
            if isinstance(value, str):
                filters.append(f"{key} = '{value}'")
            else:
                filters.append(f"{key} = {value}")
        
        return " AND ".join(filters) if filters else ""
    
    def get_chunks_by_document(self, document_id: str) -> List[Dict[str, Any]]:
        """Get all chunks for a specific document"""
        try:
            if not self.table:
                raise ValueError("Table not initialized. Call initialize() first.")
            
            results = self.table.search().where(f"document_id = '{document_id}'").to_pydantic()
            
            return [
                {
                    "id": result.id,
                    "document_id": result.document_id,
                    "chunk_id": result.chunk_id,
                    "content": result.content,
                    "metadata": result.metadata,
                    "created_at": result.created_at
                }
                for result in results
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to get chunks by document: {e}")
            return []
    
    def delete_chunks_by_document(self, document_id: str) -> bool:
        """Delete all chunks for a specific document"""
        try:
            if not self.table:
                raise ValueError("Table not initialized. Call initialize() first.")
            
            # Note: LanceDB doesn't have direct delete, so we'd need to handle this differently
            # For now, this is a placeholder implementation
            self.logger.warning("Delete functionality not fully implemented for LanceDB")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to delete chunks by document: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector database"""
        try:
            if not self.table:
                return {"error": "Table not initialized"}
            
            # Get count
            count = len(self.table)
            
            # Get sample of data to analyze
            sample_data = self.table.limit(10).to_pandas()
            
            return {
                "total_chunks": count,
                "model_name": self.model_name,
                "embedding_dimensions": 384,  # all-MiniLM-L6-v2 dimension
                "sample_documents": len(sample_data['document_id'].unique()) if not sample_data.empty else 0
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get stats: {e}")
            return {"error": str(e)}