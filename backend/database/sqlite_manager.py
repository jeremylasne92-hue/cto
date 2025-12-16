import sqlite3
from typing import Optional, Dict, Any, List
from datetime import datetime


class SQLiteManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
    
    def connect(self):
        if not self.connection:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def initialize_schema(self):
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content_sources (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                path TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content_chunks (
                id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                content TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_id) REFERENCES content_sources(id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS concepts (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                chunk_ids TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS concept_relations (
                id TEXT PRIMARY KEY,
                concept_id_1 TEXT NOT NULL,
                concept_id_2 TEXT NOT NULL,
                relation_type TEXT NOT NULL,
                strength REAL DEFAULT 0.5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (concept_id_1) REFERENCES concepts(id) ON DELETE CASCADE,
                FOREIGN KEY (concept_id_2) REFERENCES concepts(id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cards (
                id TEXT PRIMARY KEY,
                concept_id TEXT NOT NULL,
                card_type TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS card_srs_state (
                card_id TEXT PRIMARY KEY,
                ease_factor REAL DEFAULT 2.5,
                interval_days INTEGER DEFAULT 1,
                repetitions INTEGER DEFAULT 0,
                due_date TIMESTAMP NOT NULL,
                last_reviewed TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS review_logs (
                id TEXT PRIMARY KEY,
                card_id TEXT NOT NULL,
                quality INTEGER NOT NULL,
                ease_factor REAL NOT NULL,
                interval_days INTEGER NOT NULL,
                reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_log (
                id TEXT PRIMARY KEY,
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                operation TEXT NOT NULL,
                synced BOOLEAN DEFAULT 0,
                sync_timestamp TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_content_chunks_source 
            ON content_chunks(source_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_cards_concept 
            ON cards(concept_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_card_srs_due_date 
            ON card_srs_state(due_date)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_review_logs_card 
            ON review_logs(card_id)
        ''')
        
        # Phase 2: Knowledge Graph Extensions
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS concept_mastery (
                concept_id TEXT PRIMARY KEY,
                mastery_level REAL DEFAULT 0.0,
                review_count INTEGER DEFAULT 0,
                last_assessed TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS concept_layout_cache (
                concept_id TEXT PRIMARY KEY,
                x REAL NOT NULL,
                y REAL NOT NULL,
                fixed BOOLEAN DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_concept_relations_1 
            ON concept_relations(concept_id_1)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_concept_relations_2 
            ON concept_relations(concept_id_2)
        ''')
        
        conn.commit()
    
    def get_table_count(self) -> int:
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        result = cursor.fetchone()
        return result[0] if result else 0
    
    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor
    
    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
