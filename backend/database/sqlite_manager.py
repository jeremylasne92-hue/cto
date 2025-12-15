import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager


class SQLiteManager:
    def __init__(self, db_path: str = "app.db"):
        self.db_path = db_path
        self.init_database()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def init_database(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    handle TEXT UNIQUE NOT NULL,
                    visibility_default TEXT DEFAULT 'public',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id INTEGER PRIMARY KEY,
                    bio TEXT,
                    interests TEXT,
                    learning_style TEXT,
                    privacy_bio INTEGER DEFAULT 0,
                    privacy_interests INTEGER DEFAULT 0,
                    privacy_learning_style INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_metrics (
                    user_id INTEGER PRIMARY KEY,
                    hours_studied REAL DEFAULT 0.0,
                    xp_total INTEGER DEFAULT 0,
                    streak_days INTEGER DEFAULT 0,
                    certifications_json TEXT DEFAULT '[]',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_skills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    skill_id TEXT NOT NULL,
                    skill_name TEXT NOT NULL,
                    mastery REAL DEFAULT 0.0,
                    visibility TEXT DEFAULT 'public',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    UNIQUE(user_id, skill_id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_follows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    follower_id INTEGER NOT NULL,
                    followee_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (follower_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (followee_id) REFERENCES users(id) ON DELETE CASCADE,
                    UNIQUE(follower_id, followee_id),
                    CHECK(follower_id != followee_id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS review_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    duration_minutes REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            
            cursor.execute("""
                CREATE VIEW IF NOT EXISTS public_skill_summaries AS
                SELECT 
                    user_id,
                    skill_id,
                    skill_name,
                    mastery
                FROM user_skills
                WHERE visibility = 'public'
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_follows_follower 
                ON user_follows(follower_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_follows_followee 
                ON user_follows(followee_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_skills_user 
                ON user_skills(user_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_review_logs_user 
                ON review_logs(user_id)
            """)

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_user_by_handle(self, handle: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE handle = ?", (handle,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def create_user(self, handle: str, visibility_default: str = 'public') -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (handle, visibility_default) VALUES (?, ?)",
                (handle, visibility_default)
            )
            return cursor.lastrowid

    def get_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def upsert_profile(self, user_id: int, bio: Optional[str] = None, 
                      interests: Optional[str] = None, 
                      learning_style: Optional[str] = None,
                      privacy_bio: Optional[int] = None,
                      privacy_interests: Optional[int] = None,
                      privacy_learning_style: Optional[int] = None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM user_profiles WHERE user_id = ?", (user_id,))
            exists = cursor.fetchone()
            
            if exists:
                updates = []
                params = []
                if bio is not None:
                    updates.append("bio = ?")
                    params.append(bio)
                if interests is not None:
                    updates.append("interests = ?")
                    params.append(interests)
                if learning_style is not None:
                    updates.append("learning_style = ?")
                    params.append(learning_style)
                if privacy_bio is not None:
                    updates.append("privacy_bio = ?")
                    params.append(privacy_bio)
                if privacy_interests is not None:
                    updates.append("privacy_interests = ?")
                    params.append(privacy_interests)
                if privacy_learning_style is not None:
                    updates.append("privacy_learning_style = ?")
                    params.append(privacy_learning_style)
                
                if updates:
                    updates.append("updated_at = ?")
                    params.append(datetime.now().isoformat())
                    params.append(user_id)
                    cursor.execute(
                        f"UPDATE user_profiles SET {', '.join(updates)} WHERE user_id = ?",
                        params
                    )
            else:
                cursor.execute("""
                    INSERT INTO user_profiles 
                    (user_id, bio, interests, learning_style, privacy_bio, privacy_interests, privacy_learning_style)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (user_id, bio, interests, learning_style, 
                      privacy_bio or 0, privacy_interests or 0, privacy_learning_style or 0))

    def get_metrics(self, user_id: int) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_metrics WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                result = dict(row)
                result['certifications'] = json.loads(result.get('certifications_json', '[]'))
                return result
            return None

    def upsert_metrics(self, user_id: int, hours_studied: Optional[float] = None,
                      xp_total: Optional[int] = None, streak_days: Optional[int] = None,
                      certifications: Optional[List[str]] = None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM user_metrics WHERE user_id = ?", (user_id,))
            exists = cursor.fetchone()
            
            if exists:
                updates = []
                params = []
                if hours_studied is not None:
                    updates.append("hours_studied = ?")
                    params.append(hours_studied)
                if xp_total is not None:
                    updates.append("xp_total = ?")
                    params.append(xp_total)
                if streak_days is not None:
                    updates.append("streak_days = ?")
                    params.append(streak_days)
                if certifications is not None:
                    updates.append("certifications_json = ?")
                    params.append(json.dumps(certifications))
                
                if updates:
                    updates.append("updated_at = ?")
                    params.append(datetime.now().isoformat())
                    params.append(user_id)
                    cursor.execute(
                        f"UPDATE user_metrics SET {', '.join(updates)} WHERE user_id = ?",
                        params
                    )
            else:
                cursor.execute("""
                    INSERT INTO user_metrics 
                    (user_id, hours_studied, xp_total, streak_days, certifications_json)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, hours_studied or 0.0, xp_total or 0, streak_days or 0,
                      json.dumps(certifications or [])))

    def get_user_skills(self, user_id: int, include_private: bool = False) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if include_private:
                cursor.execute(
                    "SELECT * FROM user_skills WHERE user_id = ? ORDER BY mastery DESC",
                    (user_id,)
                )
            else:
                cursor.execute(
                    "SELECT * FROM user_skills WHERE user_id = ? AND visibility = 'public' ORDER BY mastery DESC",
                    (user_id,)
                )
            return [dict(row) for row in cursor.fetchall()]

    def upsert_skill(self, user_id: int, skill_id: str, skill_name: str, 
                    mastery: float, visibility: str = 'public'):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_skills (user_id, skill_id, skill_name, mastery, visibility)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(user_id, skill_id) DO UPDATE SET
                    skill_name = excluded.skill_name,
                    mastery = excluded.mastery,
                    visibility = excluded.visibility,
                    updated_at = CURRENT_TIMESTAMP
            """, (user_id, skill_id, skill_name, mastery, visibility))

    def add_follow(self, follower_id: int, followee_id: int) -> bool:
        if follower_id == followee_id:
            return False
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO user_follows (follower_id, followee_id)
                    VALUES (?, ?)
                """, (follower_id, followee_id))
                return True
        except sqlite3.IntegrityError:
            return False

    def remove_follow(self, follower_id: int, followee_id: int) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM user_follows 
                WHERE follower_id = ? AND followee_id = ?
            """, (follower_id, followee_id))
            return cursor.rowcount > 0

    def get_followers(self, user_id: int) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.id, u.handle, u.visibility_default, uf.created_at as followed_at
                FROM user_follows uf
                JOIN users u ON u.id = uf.follower_id
                WHERE uf.followee_id = ?
                ORDER BY uf.created_at DESC
            """, (user_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_following(self, user_id: int) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.id, u.handle, u.visibility_default, uf.created_at as followed_at
                FROM user_follows uf
                JOIN users u ON u.id = uf.followee_id
                WHERE uf.follower_id = ?
                ORDER BY uf.created_at DESC
            """, (user_id,))
            return [dict(row) for row in cursor.fetchall()]

    def is_following(self, follower_id: int, followee_id: int) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 1 FROM user_follows 
                WHERE follower_id = ? AND followee_id = ?
            """, (follower_id, followee_id))
            return cursor.fetchone() is not None

    def add_review_log(self, user_id: int, duration_minutes: float):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO review_logs (user_id, duration_minutes)
                VALUES (?, ?)
            """, (user_id, duration_minutes))

    def get_total_study_hours(self, user_id: int) -> float:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COALESCE(SUM(duration_minutes), 0.0) / 60.0 as hours
                FROM review_logs
                WHERE user_id = ?
            """, (user_id,))
            row = cursor.fetchone()
            return row['hours'] if row else 0.0
