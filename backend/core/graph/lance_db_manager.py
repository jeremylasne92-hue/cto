"""
LanceDB Manager for semantic neighbor lookup in knowledge graph
"""
import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import sqlite3

logger = logging.getLogger(__name__)


class LanceDBManager:
    """Manages vector embeddings and semantic search for knowledge graph concepts"""
    
    def __init__(self, db_path: str = "knowledge_graph.db", lance_db_path: str = "./lance_db"):
        self.db_path = db_path
        self.lance_db_path = lance_db_path
        
        # For this implementation, we'll use SQLite to store embeddings
        # In a real implementation, you would use the LanceDB library
        self.init_embedding_storage()
    
    def init_embedding_storage(self):
        """Initialize storage for concept embeddings"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create embeddings table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS concept_embeddings (
                        concept_id INTEGER PRIMARY KEY,
                        embedding_vector TEXT NOT NULL, -- JSON array of floats
                        embedding_model TEXT DEFAULT 'text-embedding-ada-002',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (concept_id) REFERENCES concepts(id)
                    )
                ''')
                
                conn.commit()
                logger.info("Embedding storage initialized successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize embedding storage: {e}")
            raise
    
    def store_embedding(self, concept_id: int, embedding: List[float], model: str = "text-embedding-ada-002"):
        """Store or update concept embedding"""
        try:
            embedding_json = json.dumps(embedding)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO concept_embeddings (concept_id, embedding_vector, embedding_model, updated_at)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(concept_id) 
                    DO UPDATE SET
                        embedding_vector = excluded.embedding_vector,
                        embedding_model = excluded.embedding_model,
                        updated_at = excluded.updated_at
                ''', (concept_id, embedding_json, model, datetime.now().isoformat()))
                conn.commit()
                logger.info(f"Stored embedding for concept {concept_id}")
                
        except Exception as e:
            logger.error(f"Failed to store embedding for concept {concept_id}: {e}")
            raise
    
    def get_embedding(self, concept_id: int) -> Optional[List[float]]:
        """Get embedding for a concept"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT embedding_vector FROM concept_embeddings 
                    WHERE concept_id = ?
                ''', (concept_id,))
                row = cursor.fetchone()
                
                if row:
                    return json.loads(row[0])
                return None
                
        except Exception as e:
            logger.error(f"Failed to get embedding for concept {concept_id}: {e}")
            raise
    
    def find_semantic_neighbors(self, concept_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Find semantically similar concepts (simplified implementation)"""
        try:
            # Get the concept's embedding
            target_embedding = self.get_embedding(concept_id)
            if not target_embedding:
                logger.warning(f"No embedding found for concept {concept_id}")
                return []
            
            # For this simplified implementation, we'll use name similarity
            # In a real implementation, you would calculate cosine similarity with vector embeddings
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT c.id, c.name, c.description, ce.embedding_vector,
                           (LENGTH(c.name) - LENGTH(REPLACE(LOWER(c.name), LOWER((
                               SELECT name FROM concepts WHERE id = ?
                           )), ''))) / LENGTH(c.name) as name_similarity
                    FROM concepts c
                    JOIN concept_embeddings ce ON c.id = ce.concept_id
                    WHERE c.id != ?
                    ORDER BY name_similarity DESC
                    LIMIT ?
                ''', (concept_id, concept_id, limit))
                
                results = []
                for row in cursor.fetchall():
                    concept_id, name, description, embedding_vector, similarity = row
                    results.append({
                        'concept_id': concept_id,
                        'name': name,
                        'description': description,
                        'similarity_score': similarity,
                        'distance': 1 - similarity  # Convert similarity to distance
                    })
                
                return results
                
        except Exception as e:
            logger.error(f"Failed to find semantic neighbors for concept {concept_id}: {e}")
            raise
    
    def search_concepts_by_embedding(self, query_embedding: List[float], limit: int = 10) -> List[Dict[str, Any]]:
        """Search concepts by embedding similarity (simplified implementation)"""
        try:
            # For this simplified implementation, we'll use text search
            # In a real implementation, you would compare embeddings using cosine similarity
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT c.id, c.name, c.description, ce.embedding_vector
                    FROM concepts c
                    JOIN concept_embeddings ce ON c.id = ce.concept_id
                    ORDER BY RANDOM()
                    LIMIT ?
                ''', (limit,))
                
                results = []
                for row in cursor.fetchall():
                    concept_id, name, description, embedding_vector = row
                    # In real implementation, calculate actual similarity
                    results.append({
                        'concept_id': concept_id,
                        'name': name,
                        'description': description,
                        'similarity_score': 0.5,  # Placeholder
                        'distance': 0.5  # Placeholder
                    })
                
                return results
                
        except Exception as e:
            logger.error(f"Failed to search concepts by embedding: {e}")
            raise
    
    def get_all_embeddings(self) -> Dict[int, List[float]]:
        """Get all concept embeddings"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT concept_id, embedding_vector FROM concept_embeddings
                ''')
                
                embeddings = {}
                for row in cursor.fetchall():
                    concept_id, embedding_json = row
                    embeddings[concept_id] = json.loads(embedding_json)
                
                return embeddings
                
        except Exception as e:
            logger.error(f"Failed to get all embeddings: {e}")
            raise