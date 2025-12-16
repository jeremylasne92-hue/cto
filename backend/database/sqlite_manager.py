"""
SQLite Database Manager for Social Learning Platform
Handles all database operations including social profile features
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import contextmanager
import threading

logger = logging.getLogger(__name__)

class SQLiteManager:
    def __init__(self, db_path: str = "social_learning.db"):
        self.db_path = db_path
        self._local = threading.local()
        self._lock = threading.Lock()
        self.init_database()
    
    @property
    def connection(self):
        """Get thread-local database connection"""
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn
    
    def init_database(self):
        """Initialize database with all required tables"""
        with self._lock:
            conn = self.connection
            cursor = conn.cursor()
            
            # Enable foreign key constraints
            cursor.execute('PRAGMA foreign_keys = ON')
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    handle TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_private BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # User profiles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id INTEGER PRIMARY KEY,
                    bio TEXT DEFAULT '',
                    interests TEXT DEFAULT '[]', -- JSON array
                    learning_style TEXT DEFAULT '',
                    privacy_bio INTEGER DEFAULT 1,
                    privacy_interests INTEGER DEFAULT 1,
                    privacy_learning_style INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')
            
            # User metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_metrics (
                    user_id INTEGER PRIMARY KEY,
                    hours_studied REAL DEFAULT 0.0,
                    xp_total INTEGER DEFAULT 0,
                    streak_days INTEGER DEFAULT 0,
                    certifications TEXT DEFAULT '[]', -- JSON array
                    last_study_date DATE,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')
            
            # User skills table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_skills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    skill_id TEXT NOT NULL,
                    mastery_level INTEGER DEFAULT 0,
                    visibility INTEGER DEFAULT 1, -- 1 = public, 0 = private
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    UNIQUE(user_id, skill_id)
                )
            ''')
            
            # User follows table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_follows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    follower_id INTEGER NOT NULL,
                    followee_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (follower_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (followee_id) REFERENCES users(id) ON DELETE CASCADE,
                    UNIQUE(follower_id, followee_id)
                )
            ''')
            
            # Review logs table (for metrics aggregation)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS review_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    study_duration REAL DEFAULT 0.0, -- in minutes
                    xp_earned INTEGER DEFAULT 0,
                    study_date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')
            
            # Create helper views
            self._create_helper_views(cursor)
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def _create_helper_views(self, cursor):
        """Create helper views for public skill summaries"""
        
        # Public skills view
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS public_user_skills AS
            SELECT 
                user_id,
                skill_id,
                mastery_level,
                updated_at
            FROM user_skills
            WHERE visibility = TRUE
        ''')
        
        # User profile with metrics view
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS user_profile_summary AS
            SELECT 
                u.id,
                u.handle,
                u.is_private,
                u.created_at as user_created_at,
                up.bio,
                up.interests,
                up.learning_style,
                up.privacy_bio,
                up.privacy_interests,
                up.privacy_learning_style,
                up.created_at as profile_created_at,
                up.updated_at as profile_updated_at,
                um.hours_studied,
                um.xp_total,
                um.streak_days,
                um.certifications,
                um.last_study_date,
                (SELECT COUNT(*) FROM user_follows WHERE follower_id = u.id) as following_count,
                (SELECT COUNT(*) FROM user_follows WHERE followee_id = u.id) as followers_count
            FROM users u
            LEFT JOIN user_profiles up ON u.id = up.user_id
            LEFT JOIN user_metrics um ON u.id = um.user_id
        ''')
    
    @contextmanager
    def get_cursor(self):
        """Get database cursor with automatic transaction management"""
        conn = self.connection
        try:
            yield conn.cursor()
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute a SELECT query and return results"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT query and return the last row id"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.lastrowid
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an UPDATE/DELETE query and return rows affected"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.rowcount
    
    # User management methods
    def create_user(self, handle: str, is_private: bool = False) -> int:
        """Create a new user"""
        query = '''
            INSERT INTO users (handle, is_private) 
            VALUES (?, ?)
        '''
        return self.execute_insert(query, (handle, is_private))
    
    def get_user_by_handle(self, handle: str) -> Optional[Dict]:
        """Get user by handle"""
        query = "SELECT * FROM users WHERE handle = ?"
        results = self.execute_query(query, (handle,))
        return results[0] if results else None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        query = "SELECT * FROM users WHERE id = ?"
        results = self.execute_query(query, (user_id,))
        return results[0] if results else None
    
    # Profile management methods
    def upsert_user_profile(self, user_id: int, bio: str = '', interests: List[str] = None, 
                           learning_style: str = '', privacy_bio: bool = True,
                           privacy_interests: bool = True, privacy_learning_style: bool = True) -> bool:
        """Upsert user profile"""
        interests_json = json.dumps(interests or [])
        
        query = '''
            INSERT INTO user_profiles (user_id, bio, interests, learning_style, 
                                     privacy_bio, privacy_interests, privacy_learning_style)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                bio = excluded.bio,
                interests = excluded.interests,
                learning_style = excluded.learning_style,
                privacy_bio = excluded.privacy_bio,
                privacy_interests = excluded.privacy_interests,
                privacy_learning_style = excluded.privacy_learning_style,
                updated_at = CURRENT_TIMESTAMP
        '''
        
        try:
            self.execute_insert(query, (user_id, bio, interests_json, learning_style,
                                      privacy_bio, privacy_interests, privacy_learning_style))
            return True
        except Exception as e:
            logger.error(f"Error upserting profile for user {user_id}: {e}")
            return False
    
    def get_user_profile(self, user_id: int, include_private: bool = False) -> Optional[Dict]:
        """Get user profile with privacy filtering"""
        if include_private:
            query = "SELECT * FROM user_profiles WHERE user_id = ?"
            results = self.execute_query(query, (user_id,))
        else:
            query = '''
                SELECT 
                    user_id,
                    CASE WHEN privacy_bio = 0 THEN bio ELSE '' END as bio,
                    CASE WHEN privacy_interests = 0 THEN interests ELSE '[]' END as interests,
                    CASE WHEN privacy_learning_style = 0 THEN learning_style ELSE '' END as learning_style,
                    privacy_bio,
                    privacy_interests,
                    privacy_learning_style,
                    created_at,
                    updated_at
                FROM user_profiles 
                WHERE user_id = ?
            '''
            results = self.execute_query(query, (user_id,))
        
        if results:
            profile = results[0]
            if profile['interests']:
                try:
                    profile['interests'] = json.loads(profile['interests'])
                except:
                    profile['interests'] = []
            # Convert integer booleans back to Python booleans for consistency
            profile['privacy_bio'] = bool(profile['privacy_bio'])
            profile['privacy_interests'] = bool(profile['privacy_interests'])
            profile['privacy_learning_style'] = bool(profile['privacy_learning_style'])
            return profile
        return None
    
    # Metrics management methods
    def update_user_metrics(self, user_id: int, hours_studied: float = None, xp_total: int = None,
                          streak_days: int = None, certifications: List[str] = None) -> bool:
        """Update user metrics"""
        updates = []
        params = []
        
        if hours_studied is not None:
            updates.append("hours_studied = hours_studied + ?")
            params.append(hours_studied)
        
        if xp_total is not None:
            updates.append("xp_total = ?")
            params.append(xp_total)
        
        if streak_days is not None:
            updates.append("streak_days = ?")
            params.append(streak_days)
        
        if certifications is not None:
            updates.append("certifications = ?")
            params.append(json.dumps(certifications))
        
        updates.append("last_study_date = ?")
        params.append(datetime.now().date())
        updates.append("updated_at = CURRENT_TIMESTAMP")
        
        query = f"UPDATE user_metrics SET {', '.join(updates)} WHERE user_id = ?"
        params.append(user_id)
        
        try:
            # Check if metrics record exists
            existing = self.get_user_metrics(user_id)
            if existing:
                self.execute_update(query, tuple(params))
            else:
                # Insert new metrics record
                insert_query = '''
                    INSERT INTO user_metrics (user_id, hours_studied, xp_total, streak_days, 
                                           certifications, last_study_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                '''
                self.execute_insert(insert_query, (user_id, hours_studied or 0, xp_total or 0,
                                                 streak_days or 0, json.dumps(certifications or []),
                                                 datetime.now().date()))
            return True
        except Exception as e:
            logger.error(f"Error updating metrics for user {user_id}: {e}")
            return False
    
    def get_user_metrics(self, user_id: int) -> Optional[Dict]:
        """Get user metrics"""
        query = "SELECT * FROM user_metrics WHERE user_id = ?"
        results = self.execute_query(query, (user_id,))
        if results:
            metrics = results[0]
            if metrics['certifications']:
                try:
                    metrics['certifications'] = json.loads(metrics['certifications'])
                except:
                    metrics['certifications'] = []
            return metrics
        return None
    
    def aggregate_metrics_from_logs(self, user_id: int, start_date: str = None, end_date: str = None) -> Dict:
        """Aggregate metrics from review logs"""
        where_conditions = ["user_id = ?"]
        params = [user_id]
        
        if start_date:
            where_conditions.append("study_date >= ?")
            params.append(start_date)
        
        if end_date:
            where_conditions.append("study_date <= ?")
            params.append(end_date)
        
        where_clause = " AND ".join(where_conditions)
        
        query = f'''
            SELECT 
                SUM(study_duration) / 60.0 as total_hours, -- Convert minutes to hours
                SUM(xp_earned) as total_xp,
                COUNT(DISTINCT study_date) as study_days,
                MAX(study_date) as last_study_date
            FROM review_logs
            WHERE {where_clause}
        '''
        
        results = self.execute_query(query, tuple(params))
        return results[0] if results else {}
    
    # Skills management methods
    def update_user_skill(self, user_id: int, skill_id: str, mastery_level: int, visibility: bool = True) -> bool:
        """Update user skill with visibility settings"""
        query = '''
            INSERT INTO user_skills (user_id, skill_id, mastery_level, visibility)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, skill_id) DO UPDATE SET
                mastery_level = excluded.mastery_level,
                visibility = excluded.visibility,
                updated_at = CURRENT_TIMESTAMP
        '''
        
        try:
            # Convert boolean to int for SQLite
            visibility_int = 1 if visibility else 0
            self.execute_insert(query, (user_id, skill_id, mastery_level, visibility_int))
            return True
        except Exception as e:
            logger.error(f"Error updating skill for user {user_id}: {e}")
            return False
    
    def get_user_skills(self, user_id: int, public_only: bool = False) -> List[Dict]:
        """Get user skills with privacy filtering"""
        if public_only:
            query = "SELECT skill_id, mastery_level, updated_at FROM public_user_skills WHERE user_id = ?"
        else:
            query = "SELECT skill_id, mastery_level, visibility, updated_at FROM user_skills WHERE user_id = ?"
        
        return self.execute_query(query, (user_id,))
    
    # Follow management methods
    def follow_user(self, follower_id: int, followee_id: int) -> bool:
        """Follow a user"""
        if follower_id == followee_id:
            return False  # Cannot follow yourself
        
        # Check if target user is private and implement privacy logic here
        target_user = self.get_user_by_id(followee_id)
        if target_user and target_user['is_private']:
            # For private users, you might want to implement follow requests
            # For now, we'll allow following but store it as a pending request
            pass
        
        query = '''
            INSERT OR IGNORE INTO user_follows (follower_id, followee_id)
            VALUES (?, ?)
        '''
        
        try:
            self.execute_insert(query, (follower_id, followee_id))
            return True
        except Exception as e:
            logger.error(f"Error following user {followee_id} by {follower_id}: {e}")
            return False
    
    def unfollow_user(self, follower_id: int, followee_id: int) -> bool:
        """Unfollow a user"""
        query = "DELETE FROM user_follows WHERE follower_id = ? AND followee_id = ?"
        
        try:
            rows_affected = self.execute_update(query, (follower_id, followee_id))
            return rows_affected > 0
        except Exception as e:
            logger.error(f"Error unfollowing user {followee_id} by {follower_id}: {e}")
            return False
    
    def get_user_followers(self, user_id: int) -> List[Dict]:
        """Get user's followers"""
        query = '''
            SELECT u.id, u.handle, uf.created_at as followed_at
            FROM user_follows uf
            JOIN users u ON uf.follower_id = u.id
            WHERE uf.followee_id = ?
            ORDER BY uf.created_at DESC
        '''
        return self.execute_query(query, (user_id,))
    
    def get_user_following(self, user_id: int) -> List[Dict]:
        """Get users that this user is following"""
        query = '''
            SELECT u.id, u.handle, uf.created_at as followed_at
            FROM user_follows uf
            JOIN users u ON uf.followee_id = u.id
            WHERE uf.follower_id = ?
            ORDER BY uf.created_at DESC
        '''
        return self.execute_query(query, (user_id,))
    
    # Public profile methods
    def get_public_profile(self, handle: str) -> Optional[Dict]:
        """Get public profile by handle (for external API)"""
        query = '''
            SELECT 
                u.handle,
                up.bio,
                up.interests,
                up.learning_style,
                um.hours_studied,
                um.xp_total,
                um.streak_days,
                um.certifications,
                (SELECT COUNT(*) FROM user_follows WHERE follower_id = u.id) as following_count,
                (SELECT COUNT(*) FROM user_follows WHERE followee_id = u.id) as followers_count
            FROM users u
            LEFT JOIN user_profiles up ON u.id = up.user_id
            LEFT JOIN user_metrics um ON u.id = um.user_id
            LEFT JOIN user_skills us ON u.id = us.user_id AND us.visibility = TRUE
            WHERE u.handle = ?
            GROUP BY u.id
        '''
        
        results = self.execute_query(query, (handle,))
        if results:
            profile = results[0]
            # Parse interests and certifications JSON
            if profile['interests']:
                try:
                    profile['interests'] = json.loads(profile['interests'])
                except:
                    profile['interests'] = []
            
            if profile['certifications']:
                try:
                    profile['certifications'] = json.loads(profile['certifications'])
                except:
                    profile['certifications'] = []
            
            return profile
        return None
    
    def get_public_skills(self, handle: str) -> List[Dict]:
        """Get public skills for a user"""
        query = '''
            SELECT us.skill_id, us.mastery_level
            FROM users u
            JOIN public_user_skills us ON u.id = us.user_id
            WHERE u.handle = ?
            ORDER BY us.mastery_level DESC, us.skill_id
        '''
        return self.execute_query(query, (handle,))
    
    def close(self):
        """Close all database connections"""
        if hasattr(self._local, 'conn'):
            self._local.conn.close()
            delattr(self._local, 'conn')