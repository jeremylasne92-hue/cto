import sqlite3
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import json
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class SQLiteManager:
    """Manages SQLite database connections and schema for knowledge graph system."""
    
    def __init__(self, db_path: str = "knowledge_graph.db"):
        self.db_path = db_path
        self._init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def _init_database(self):
        """Initialize database schema with migration-safe guards."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Concepts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS concepts (
                    id TEXT PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Relations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS relations (
                    id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    relation_type TEXT NOT NULL,
                    strength REAL DEFAULT 1.0,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (source_id) REFERENCES concepts(id) ON DELETE CASCADE,
                    FOREIGN KEY (target_id) REFERENCES concepts(id) ON DELETE CASCADE,
                    UNIQUE(source_id, target_id, relation_type)
                )
            """)
            
            # Review logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS review_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    concept_id TEXT NOT NULL,
                    correct BOOLEAN NOT NULL,
                    review_type TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
                )
            """)
            
            # Concept mastery table (Phase 2)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS concept_mastery (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    concept_id TEXT NOT NULL,
                    mastery_percent REAL DEFAULT 0.0,
                    review_count INTEGER DEFAULT 0,
                    last_assessed TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE,
                    UNIQUE(user_id, concept_id)
                )
            """)
            
            # Concept layout cache table (Phase 2)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS concept_layout_cache (
                    concept_id TEXT PRIMARY KEY,
                    x REAL NOT NULL,
                    y REAL NOT NULL,
                    z REAL DEFAULT 0.0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
                )
            """)
            
            # Create indexes for better query performance
            self._create_indexes_safe(cursor)
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def _create_indexes_safe(self, cursor):
        """Create indexes with migration-safe guards."""
        indexes = [
            ("idx_relations_source", "relations", "source_id"),
            ("idx_relations_target", "relations", "target_id"),
            ("idx_relations_type", "relations", "relation_type"),
            ("idx_review_logs_user", "review_logs", "user_id"),
            ("idx_review_logs_concept", "review_logs", "concept_id"),
            ("idx_concept_mastery_user", "concept_mastery", "user_id"),
            ("idx_concept_mastery_concept", "concept_mastery", "concept_id"),
        ]
        
        for idx_name, table, column in indexes:
            try:
                cursor.execute(f"""
                    CREATE INDEX IF NOT EXISTS {idx_name} ON {table}({column})
                """)
            except sqlite3.OperationalError as e:
                logger.warning(f"Index {idx_name} already exists or error: {e}")
    
    def add_column_safe(self, table: str, column: str, column_type: str, default: str = None):
        """Add a column to a table if it doesn't exist (migration-safe)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if column exists
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [row[1] for row in cursor.fetchall()]
            
            if column not in columns:
                default_clause = f" DEFAULT {default}" if default else ""
                try:
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}{default_clause}")
                    logger.info(f"Added column {column} to {table}")
                except sqlite3.OperationalError as e:
                    logger.warning(f"Could not add column {column} to {table}: {e}")
    
    # Concept operations
    def create_concept(self, concept_id: str, name: str, description: str = None, metadata: Dict = None) -> bool:
        """Create a new concept."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO concepts (id, name, description, metadata)
                    VALUES (?, ?, ?, ?)
                """, (concept_id, name, description, json.dumps(metadata) if metadata else None))
                return True
        except sqlite3.IntegrityError as e:
            logger.error(f"Concept already exists: {e}")
            return False
    
    def update_concept(self, concept_id: str, name: str = None, description: str = None, metadata: Dict = None) -> bool:
        """Update an existing concept."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            updates = []
            params = []
            
            if name:
                updates.append("name = ?")
                params.append(name)
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            if metadata is not None:
                updates.append("metadata = ?")
                params.append(json.dumps(metadata))
            
            if updates:
                updates.append("updated_at = CURRENT_TIMESTAMP")
                params.append(concept_id)
                cursor.execute(f"""
                    UPDATE concepts SET {', '.join(updates)}
                    WHERE id = ?
                """, params)
                return cursor.rowcount > 0
            return False
    
    def get_concept(self, concept_id: str) -> Optional[Dict]:
        """Get a concept by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM concepts WHERE id = ?", (concept_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def get_all_concepts(self) -> List[Dict]:
        """Get all concepts."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM concepts")
            return [dict(row) for row in cursor.fetchall()]
    
    def delete_concept(self, concept_id: str) -> bool:
        """Delete a concept and its relations."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM concepts WHERE id = ?", (concept_id,))
            return cursor.rowcount > 0
    
    # Relation operations
    def create_relation(self, relation_id: str, source_id: str, target_id: str, 
                       relation_type: str, strength: float = 1.0, metadata: Dict = None) -> bool:
        """Create a new relation between concepts."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO relations (id, source_id, target_id, relation_type, strength, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (relation_id, source_id, target_id, relation_type, strength, 
                      json.dumps(metadata) if metadata else None))
                return True
        except sqlite3.IntegrityError as e:
            logger.error(f"Relation constraint violated: {e}")
            return False
    
    def get_relations(self, concept_id: str = None, relation_type: str = None) -> List[Dict]:
        """Get relations, optionally filtered by concept or type."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM relations WHERE 1=1"
            params = []
            
            if concept_id:
                query += " AND (source_id = ? OR target_id = ?)"
                params.extend([concept_id, concept_id])
            if relation_type:
                query += " AND relation_type = ?"
                params.append(relation_type)
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def delete_relation(self, relation_id: str) -> bool:
        """Delete a relation."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM relations WHERE id = ?", (relation_id,))
            return cursor.rowcount > 0
    
    def update_relation_strength(self, relation_id: str, strength: float) -> bool:
        """Update relation strength."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE relations SET strength = ? WHERE id = ?
            """, (strength, relation_id))
            return cursor.rowcount > 0
    
    # Review log operations
    def add_review_log(self, user_id: int, concept_id: str, correct: bool, review_type: str = None) -> int:
        """Add a review log entry."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO review_logs (user_id, concept_id, correct, review_type)
                VALUES (?, ?, ?, ?)
            """, (user_id, concept_id, correct, review_type))
            return cursor.lastrowid
    
    def get_review_logs(self, user_id: int = None, concept_id: str = None, 
                       limit: int = 100) -> List[Dict]:
        """Get review logs with optional filters."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM review_logs WHERE 1=1"
            params = []
            
            if user_id:
                query += " AND user_id = ?"
                params.append(user_id)
            if concept_id:
                query += " AND concept_id = ?"
                params.append(concept_id)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    # Concept mastery operations (Phase 2)
    def update_concept_mastery(self, user_id: int, concept_id: str, 
                              mastery_percent: float, review_count: int) -> bool:
        """Update or create concept mastery record."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO concept_mastery (user_id, concept_id, mastery_percent, review_count, last_assessed, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id, concept_id) DO UPDATE SET
                    mastery_percent = excluded.mastery_percent,
                    review_count = excluded.review_count,
                    last_assessed = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
            """, (user_id, concept_id, mastery_percent, review_count))
            return True
    
    def get_concept_mastery(self, user_id: int, concept_id: str = None) -> List[Dict]:
        """Get concept mastery records."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if concept_id:
                cursor.execute("""
                    SELECT * FROM concept_mastery 
                    WHERE user_id = ? AND concept_id = ?
                """, (user_id, concept_id))
            else:
                cursor.execute("""
                    SELECT * FROM concept_mastery WHERE user_id = ?
                """, (user_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    # Layout cache operations (Phase 2)
    def update_layout_position(self, concept_id: str, x: float, y: float, z: float = 0.0) -> bool:
        """Update or create layout position cache."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO concept_layout_cache (concept_id, x, y, z, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(concept_id) DO UPDATE SET
                    x = excluded.x,
                    y = excluded.y,
                    z = excluded.z,
                    updated_at = CURRENT_TIMESTAMP
            """, (concept_id, x, y, z))
            return True
    
    def get_layout_positions(self) -> Dict[str, Dict[str, float]]:
        """Get all cached layout positions."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT concept_id, x, y, z FROM concept_layout_cache")
            return {
                row['concept_id']: {'x': row['x'], 'y': row['y'], 'z': row['z']}
                for row in cursor.fetchall()
            }
    
    # User operations
    def create_user(self, username: str, email: str = None) -> Optional[int]:
        """Create a new user."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO users (username, email)
                    VALUES (?, ?)
                """, (username, email))
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            logger.error(f"User {username} already exists")
            return None
    
    def get_user(self, user_id: int = None, username: str = None) -> Optional[Dict]:
        """Get a user by ID or username."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if user_id:
                cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            elif username:
                cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            else:
                return None
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
