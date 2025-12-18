"""
SQLite database schema and operations for FSRS-5 SRS Engine
"""

import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Card:
    id: str
    deck_id: str
    front: str
    back: str
    card_type: str  # quiz/flashcard/mindmap
    created_at: datetime
    updated_at: datetime

@dataclass
class CardSRSState:
    card_id: str
    difficulty: float  # 0-10
    stability: float  # days
    retrievability: float  # 0-1
    due_date: datetime
    reviews_count: int
    lapses: int
    last_review_at: Optional[datetime]
    is_leech: bool

@dataclass
class ReviewLog:
    id: str
    card_id: str
    grade: int  # 1=Again, 2=Hard, 3=Good, 4=Easy
    review_duration: float  # seconds
    timestamp: datetime
    session_id: str
    old_difficulty: float
    new_difficulty: float
    old_stability: float
    new_stability: float
    old_retrievability: float
    new_retrievability: float
    interval: float  # days

class SRSDatabase:
    def __init__(self, db_path: str = "srs_engine.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with FSRS-5 tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Cards table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cards (
                    id TEXT PRIMARY KEY,
                    deck_id TEXT NOT NULL,
                    front TEXT NOT NULL,
                    back TEXT NOT NULL,
                    card_type TEXT NOT NULL CHECK (card_type IN ('quiz', 'flashcard', 'mindmap')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (deck_id) REFERENCES decks (id)
                )
            ''')
            
            # Decks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS decks (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_default BOOLEAN DEFAULT 0
                )
            ''')
            
            # Card SRS State table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS card_srs_state (
                    card_id TEXT PRIMARY KEY,
                    difficulty REAL NOT NULL DEFAULT 5.0,
                    stability REAL NOT NULL DEFAULT 1.0,
                    retrievability REAL NOT NULL DEFAULT 1.0,
                    due_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    reviews_count INTEGER NOT NULL DEFAULT 0,
                    lapses INTEGER NOT NULL DEFAULT 0,
                    last_review_at TIMESTAMP,
                    is_leech BOOLEAN NOT NULL DEFAULT 0,
                    FOREIGN KEY (card_id) REFERENCES cards (id)
                )
            ''')
            
            # Review Logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS review_logs (
                    id TEXT PRIMARY KEY,
                    card_id TEXT NOT NULL,
                    grade INTEGER NOT NULL,
                    review_duration REAL NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    session_id TEXT NOT NULL,
                    old_difficulty REAL NOT NULL,
                    new_difficulty REAL NOT NULL,
                    old_stability REAL NOT NULL,
                    new_stability REAL NOT NULL,
                    old_retrievability REAL NOT NULL,
                    new_retrievability REAL NOT NULL,
                    interval REAL NOT NULL,
                    FOREIGN KEY (card_id) REFERENCES cards (id)
                )
            ''')
            
            # Sessions table (for grouping reviews)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS review_sessions (
                    id TEXT PRIMARY KEY,
                    deck_id TEXT NOT NULL,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    cards_reviewed INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY (deck_id) REFERENCES decks (id)
                )
            ''')
            
            # Create indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_cards_deck ON cards (deck_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_srs_due ON card_srs_state (due_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_srs_leech ON card_srs_state (is_leech)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_reviews_card ON review_logs (card_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_reviews_timestamp ON review_logs (timestamp)')
            
            conn.commit()
            
            # Create default "All" deck
            cursor.execute('INSERT OR IGNORE INTO decks (id, name, is_default) VALUES (?, ?, ?)', 
                         (str(uuid.uuid4()), "All", 1))
            conn.commit()
    
    def create_deck(self, name: str, description: str = "") -> str:
        """Create a new deck"""
        deck_id = str(uuid.uuid4())
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO decks (id, name, description) VALUES (?, ?, ?)',
                (deck_id, name, description)
            )
            conn.commit()
        return deck_id
    
    def get_decks(self) -> List[Dict[str, Any]]:
        """Get all decks with statistics"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    d.id, d.name, d.description, d.created_at, d.is_default,
                    COUNT(c.id) as total_cards,
                    COUNT(CASE WHEN s.due_date <= datetime('now') THEN 1 END) as due_cards,
                    COUNT(CASE WHEN date(s.last_review_at) = date('now') THEN 1 END) as reviewed_today
                FROM decks d
                LEFT JOIN cards c ON d.id = c.deck_id
                LEFT JOIN card_srs_state s ON c.id = s.card_id
                GROUP BY d.id
                ORDER BY d.is_default DESC, d.name
            ''')
            
            return [dict(row) for row in cursor.fetchall()]
    
    def create_card(self, deck_id: str, front: str, back: str, card_type: str = "flashcard") -> str:
        """Create a new card with initial SRS state"""
        card_id = str(uuid.uuid4())
        now = datetime.now()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create card
            cursor.execute('''
                INSERT INTO cards (id, deck_id, front, back, card_type, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (card_id, deck_id, front, back, card_type, now, now))
            
            # Create initial SRS state with due date set to now (immediately reviewable)
            cursor.execute('''
                INSERT INTO card_srs_state (card_id, difficulty, stability, retrievability, due_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (card_id, 5.0, 1.0, 1.0, now))
            
            conn.commit()
        return card_id
    
    def get_cards(self, deck_id: Optional[str] = None) -> List[Card]:
        """Get cards from a deck"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if deck_id:
                cursor.execute('SELECT * FROM cards WHERE deck_id = ? ORDER BY created_at', (deck_id,))
            else:
                cursor.execute('SELECT * FROM cards ORDER BY created_at')
            
            return [Card(
                id=row['id'],
                deck_id=row['deck_id'],
                front=row['front'],
                back=row['back'],
                card_type=row['card_type'],
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at'])
            ) for row in cursor.fetchall()]
    
    def get_card_srs_state(self, card_id: str) -> Optional[CardSRSState]:
        """Get SRS state for a card"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM card_srs_state WHERE card_id = ?', (card_id,))
            row = cursor.fetchone()
            
            if row:
                return CardSRSState(
                    card_id=row['card_id'],
                    difficulty=row['difficulty'],
                    stability=row['stability'],
                    retrievability=row['retrievability'],
                    due_date=datetime.fromisoformat(row['due_date']),
                    reviews_count=row['reviews_count'],
                    lapses=row['lapses'],
                    last_review_at=datetime.fromisoformat(row['last_review_at']) if row['last_review_at'] else None,
                    is_leech=bool(row['is_leech'])
                )
            return None
    
    def update_srs_state(self, card_id: str, difficulty: float, stability: float, 
                        retrievability: float, due_date: datetime, reviews_count: int,
                        lapses: int, is_leech: bool):
        """Update SRS state for a card"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE card_srs_state 
                SET difficulty = ?, stability = ?, retrievability = ?, due_date = ?,
                    reviews_count = ?, lapses = ?, last_review_at = ?, is_leech = ?
                WHERE card_id = ?
            ''', (difficulty, stability, retrievability, due_date, reviews_count, 
                  lapses, datetime.now(), is_leech, card_id))
            conn.commit()
    
    def log_review(self, review_log: ReviewLog):
        """Log a review action"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO review_logs (
                    id, card_id, grade, review_duration, timestamp, session_id,
                    old_difficulty, new_difficulty, old_stability, new_stability,
                    old_retrievability, new_retrievability, interval
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (review_log.id, review_log.card_id, review_log.grade, 
                  review_log.review_duration, review_log.timestamp, review_log.session_id,
                  review_log.old_difficulty, review_log.new_difficulty,
                  review_log.old_stability, review_log.new_stability,
                  review_log.old_retrievability, review_log.new_retrievability,
                  review_log.interval))
            conn.commit()
    
    def get_due_cards(self, deck_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get cards that are due for review"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = '''
                SELECT c.id, c.front, c.back, c.card_type, c.deck_id,
                       s.difficulty, s.stability, s.retrievability, s.due_date,
                       s.reviews_count, s.lapses, s.is_leech, d.name as deck_name
                FROM cards c
                JOIN card_srs_state s ON c.id = s.card_id
                JOIN decks d ON c.deck_id = d.id
                WHERE s.is_leech = 0
            '''
            params = []
            
            if deck_id:
                query += ' AND c.deck_id = ?'
                params.append(deck_id)
            
            query += ' ORDER BY s.due_date ASC, s.reviews_count ASC'
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_overdue_cards(self) -> List[Dict[str, Any]]:
        """Get cards that are overdue (due date in the past)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT c.id, c.front, c.back, c.card_type, c.deck_id,
                       s.difficulty, s.stability, s.retrievability, s.due_date,
                       s.reviews_count, s.lapses, s.is_leech, d.name as deck_name,
                       CAST((julianday('now') - julianday(s.due_date)) AS INTEGER) as days_overdue
                FROM cards c
                JOIN card_srs_state s ON c.id = s.card_id
                JOIN decks d ON c.deck_id = d.id
                WHERE s.due_date < datetime('now') AND s.is_leech = 0
                ORDER BY s.due_date ASC
            ''')
            
            return [dict(row) for row in cursor.fetchall()]
    
    def create_review_session(self, deck_id: str) -> str:
        """Create a new review session"""
        session_id = str(uuid.uuid4())
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO review_sessions (id, deck_id) VALUES (?, ?)
            ''', (session_id, deck_id))
            conn.commit()
        return session_id
    
    def end_review_session(self, session_id: str, cards_reviewed: int):
        """End a review session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE review_sessions 
                SET end_time = CURRENT_TIMESTAMP, cards_reviewed = ?
                WHERE id = ?
            ''', (cards_reviewed, session_id))
            conn.commit()
    
    def get_deck_statistics(self, deck_id: str) -> Dict[str, Any]:
        """Get comprehensive statistics for a deck"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Basic statistics
            cursor.execute('''
                SELECT 
                    COUNT(c.id) as total_cards,
                    COUNT(CASE WHEN s.due_date <= datetime('now') THEN 1 END) as due_cards,
                    COUNT(CASE WHEN date(s.last_review_at) = date('now') THEN 1 END) as reviewed_today,
                    COUNT(CASE WHEN s.is_leech = 1 THEN 1 END) as leech_cards,
                    AVG(s.difficulty) as avg_difficulty,
                    AVG(s.stability) as avg_stability,
                    AVG(s.retrievability) as avg_retrievability
                FROM cards c
                JOIN card_srs_state s ON c.id = s.card_id
                WHERE c.deck_id = ?
            ''', (deck_id,))
            
            basic_stats = dict(cursor.fetchone())
            
            # Review frequency (last 30 days)
            cursor.execute('''
                SELECT COUNT(*) as reviews_30d
                FROM review_logs rl
                JOIN cards c ON rl.card_id = c.id
                WHERE c.deck_id = ? AND rl.timestamp >= date('now', '-30 days')
            ''', (deck_id,))
            
            reviews_30d = cursor.fetchone()['reviews_30d']
            basic_stats['reviews_30d'] = reviews_30d
            
            return basic_stats