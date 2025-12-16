"""
SQLite Manager for the Knowledge Graph System
Extends existing SQLite management with knowledge graph specific features
"""
import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class SQLiteManager:
    """Extended SQLite manager for knowledge graph operations"""
    
    def __init__(self, db_path: str = "knowledge_graph.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with core tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Core concepts table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS concepts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        description TEXT,
                        content TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        parent_id INTEGER REFERENCES concepts(id),
                        FOREIGN KEY (parent_id) REFERENCES concepts(id)
                    )
                ''')
                
                # Relations between concepts
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS relations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source_concept_id INTEGER NOT NULL,
                        target_concept_id INTEGER NOT NULL,
                        relation_type TEXT NOT NULL DEFAULT 'prerequisite',
                        strength REAL DEFAULT 1.0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (source_concept_id) REFERENCES concepts(id),
                        FOREIGN KEY (target_concept_id) REFERENCES concepts(id)
                    )
                ''')
                
                # Review logs for mastery calculation
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS review_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        concept_id INTEGER NOT NULL,
                        mastery_score REAL DEFAULT 0.0,
                        review_count INTEGER DEFAULT 0,
                        last_reviewed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (concept_id) REFERENCES concepts(id)
                    )
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def add_concept_mastery_table(self):
        """Add concept_mastery table with migration-safe guards"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if table exists
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='concept_mastery'
                """)
                
                if not cursor.fetchone():
                    cursor.execute('''
                        CREATE TABLE concept_mastery (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id TEXT NOT NULL,
                            concept_id INTEGER NOT NULL,
                            mastery_percentage REAL DEFAULT 0.0,
                            review_count INTEGER DEFAULT 0,
                            last_assessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE(user_id, concept_id),
                            FOREIGN KEY (concept_id) REFERENCES concepts(id)
                        )
                    ''')
                    
                    # Create indexes for performance
                    cursor.execute('''
                        CREATE INDEX idx_concept_mastery_user_concept 
                        ON concept_mastery(user_id, concept_id)
                    ''')
                    
                    cursor.execute('''
                        CREATE INDEX idx_concept_mastery_mastery 
                        ON concept_mastery(mastery_percentage)
                    ''')
                    
                    conn.commit()
                    logger.info("concept_mastery table created successfully")
                else:
                    logger.info("concept_mastery table already exists")
                    
        except Exception as e:
            logger.error(f"Failed to add concept_mastery table: {e}")
            raise
    
    def add_concept_layout_cache_table(self):
        """Add concept_layout_cache table with migration-safe guards"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if table exists
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='concept_layout_cache'
                """)
                
                if not cursor.fetchone():
                    cursor.execute('''
                        CREATE TABLE concept_layout_cache (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            concept_id INTEGER NOT NULL,
                            layout_data TEXT NOT NULL, -- JSON string with x, y, z coordinates
                            layout_algorithm TEXT DEFAULT 'force-directed',
                            zoom_level REAL DEFAULT 1.0,
                            viewport_x REAL DEFAULT 0.0,
                            viewport_y REAL DEFAULT 0.0,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE(concept_id),
                            FOREIGN KEY (concept_id) REFERENCES concepts(id)
                        )
                    ''')
                    
                    # Create indexes
                    cursor.execute('''
                        CREATE INDEX idx_concept_layout_cache_updated 
                        ON concept_layout_cache(updated_at)
                    ''')
                    
                    conn.commit()
                    logger.info("concept_layout_cache table created successfully")
                else:
                    logger.info("concept_layout_cache table already exists")
                    
        except Exception as e:
            logger.error(f"Failed to add concept_layout_cache table: {e}")
            raise
    
    def add_relation_integrity_indexes(self):
        """Add relation integrity indexes with migration-safe guards"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check and create indexes on relations table for integrity
                indexes_to_create = [
                    ('idx_relations_source', 'relations(source_concept_id)'),
                    ('idx_relations_target', 'relations(target_concept_id)'),
                    ('idx_relations_type', 'relations(relation_type)'),
                    ('idx_relations_strength', 'relations(strength)')
                ]
                
                for index_name, column_spec in indexes_to_create:
                    try:
                        cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {column_spec}")
                        logger.info(f"Index {index_name} created successfully")
                    except Exception as e:
                        logger.warning(f"Failed to create index {index_name}: {e}")
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to add relation integrity indexes: {e}")
            raise
    
    def migrate_database(self):
        """Run all migrations in safe order"""
        try:
            self.add_concept_mastery_table()
            self.add_concept_layout_cache_table()
            self.add_relation_integrity_indexes()
            logger.info("Database migration completed successfully")
        except Exception as e:
            logger.error(f"Database migration failed: {e}")
            raise
    
    # Concept CRUD operations
    def create_concept(self, name: str, description: str = "", content: str = "", parent_id: Optional[int] = None) -> int:
        """Create a new concept"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO concepts (name, description, content, parent_id)
                    VALUES (?, ?, ?, ?)
                ''', (name, description, content, parent_id))
                concept_id = cursor.lastrowid
                conn.commit()
                logger.info(f"Created concept {name} with ID {concept_id}")
                return concept_id
        except sqlite3.IntegrityError:
            logger.error(f"Concept with name '{name}' already exists")
            raise ValueError(f"Concept with name '{name}' already exists")
        except Exception as e:
            logger.error(f"Failed to create concept: {e}")
            raise
    
    def get_concept(self, concept_id: int) -> Optional[Dict[str, Any]]:
        """Get concept by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM concepts WHERE id = ?', (concept_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Failed to get concept {concept_id}: {e}")
            raise
    
    def update_concept(self, concept_id: int, **kwargs) -> bool:
        """Update concept"""
        if not kwargs:
            return False
        
        # Add updated_at timestamp
        kwargs['updated_at'] = datetime.now().isoformat()
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                set_clause = ', '.join([f"{k} = ?" for k in kwargs.keys()])
                values = list(kwargs.values()) + [concept_id]
                
                cursor.execute(f'''
                    UPDATE concepts 
                    SET {set_clause}
                    WHERE id = ?
                ''', values)
                
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Failed to update concept {concept_id}: {e}")
            raise
    
    def delete_concept(self, concept_id: int) -> bool:
        """Delete concept and related data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete related records first
                cursor.execute('DELETE FROM relations WHERE source_concept_id = ? OR target_concept_id = ?', (concept_id, concept_id))
                cursor.execute('DELETE FROM review_logs WHERE concept_id = ?', (concept_id,))
                cursor.execute('DELETE FROM concept_mastery WHERE concept_id = ?', (concept_id,))
                cursor.execute('DELETE FROM concept_layout_cache WHERE concept_id = ?', (concept_id,))
                
                # Delete the concept
                cursor.execute('DELETE FROM concepts WHERE id = ?', (concept_id,))
                
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Failed to delete concept {concept_id}: {e}")
            raise
    
    # Relation operations
    def create_relation(self, source_concept_id: int, target_concept_id: int, relation_type: str = "prerequisite", strength: float = 1.0) -> int:
        """Create a relation between concepts"""
        if source_concept_id == target_concept_id:
            raise ValueError("Cannot create self-referencing relation")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO relations (source_concept_id, target_concept_id, relation_type, strength)
                    VALUES (?, ?, ?, ?)
                ''', (source_concept_id, target_concept_id, relation_type, strength))
                relation_id = cursor.lastrowid
                conn.commit()
                logger.info(f"Created relation {relation_id}: {source_concept_id} -> {target_concept_id}")
                return relation_id
        except Exception as e:
            logger.error(f"Failed to create relation: {e}")
            raise
    
    def get_concept_relations(self, concept_id: int) -> List[Dict[str, Any]]:
        """Get all relations for a concept"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT r.*, sc.name as source_name, tc.name as target_name
                    FROM relations r
                    JOIN concepts sc ON r.source_concept_id = sc.id
                    JOIN concepts tc ON r.target_concept_id = tc.id
                    WHERE r.source_concept_id = ? OR r.target_concept_id = ?
                    ORDER BY r.strength DESC
                ''', (concept_id, concept_id))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get relations for concept {concept_id}: {e}")
            raise
    
    # Mastery operations
    def update_mastery(self, user_id: str, concept_id: int, mastery_percentage: float, review_count: int = 1):
        """Update user mastery for a concept"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO concept_mastery (user_id, concept_id, mastery_percentage, review_count, last_assessed)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(user_id, concept_id) 
                    DO UPDATE SET
                        mastery_percentage = excluded.mastery_percentage,
                        review_count = concept_mastery.review_count + excluded.review_count,
                        last_assessed = excluded.last_assessed
                ''', (user_id, concept_id, mastery_percentage, review_count, datetime.now().isoformat()))
                conn.commit()
                logger.info(f"Updated mastery for user {user_id}, concept {concept_id}: {mastery_percentage}%")
        except Exception as e:
            logger.error(f"Failed to update mastery: {e}")
            raise
    
    def get_mastery(self, user_id: str, concept_id: int) -> Optional[Dict[str, Any]]:
        """Get user's mastery for a concept"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM concept_mastery 
                    WHERE user_id = ? AND concept_id = ?
                ''', (user_id, concept_id))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Failed to get mastery: {e}")
            raise