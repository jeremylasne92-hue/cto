"""
Database models for the flashcard sync system
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Deck(db.Model):
    """Deck model for organizing flashcards"""
    __tablename__ = 'decks'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Sync tracking
    last_synced = db.Column(db.DateTime)
    sync_version = db.Column(db.Integer, default=1)
    
    cards = db.relationship('Card', backref='deck', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_synced': self.last_synced.isoformat() if self.last_synced else None,
            'sync_version': self.sync_version,
            'card_count': len(self.cards)
        }

class Card(db.Model):
    """Flashcard model"""
    __tablename__ = 'cards'
    
    id = db.Column(db.Integer, primary_key=True)
    deck_id = db.Column(db.Integer, db.ForeignKey('decks.id'), nullable=False)
    
    # Card content
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    
    # SRS (Spaced Repetition System) data
    ease_factor = db.Column(db.Float, default=2.5)
    interval = db.Column(db.Integer, default=1)  # days
    repetition = db.Column(db.Integer, default=0)
    next_review = db.Column(db.DateTime)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Sync tracking
    last_synced = db.Column(db.DateTime)
    sync_version = db.Column(db.Integer, default=1)
    
    # Reviews relationship
    reviews = db.relationship('ReviewLog', backref='card', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_reviews=False):
        data = {
            'id': self.id,
            'deck_id': self.deck_id,
            'question': self.question,
            'answer': self.answer,
            'ease_factor': self.ease_factor,
            'interval': self.interval,
            'repetition': self.repetition,
            'next_review': self.next_review.isoformat() if self.next_review else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_synced': self.last_synced.isoformat() if self.last_synced else None,
            'sync_version': self.sync_version
        }
        
        if include_reviews:
            data['reviews'] = [review.to_dict() for review in self.reviews]
            
        return data

class ReviewLog(db.Model):
    """Review log for tracking study sessions"""
    __tablename__ = 'review_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id'), nullable=False)
    
    # Review data
    grade = db.Column(db.Integer, nullable=False)  # 0-5 quality rating
    review_time = db.Column(db.DateTime, default=datetime.utcnow)
    
    # SRS data at time of review
    previous_ease_factor = db.Column(db.Float)
    previous_interval = db.Column(db.Integer)
    previous_repetition = db.Column(db.Integer)
    new_ease_factor = db.Column(db.Float)
    new_interval = db.Column(db.Integer)
    new_repetition = db.Column(db.Integer)
    
    # Sync tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    synced = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'card_id': self.card_id,
            'grade': self.grade,
            'review_time': self.review_time.isoformat() if self.review_time else None,
            'previous_srs': {
                'ease_factor': self.previous_ease_factor,
                'interval': self.previous_interval,
                'repetition': self.previous_repetition
            },
            'new_srs': {
                'ease_factor': self.new_ease_factor,
                'interval': self.new_interval,
                'repetition': self.new_repetition
            },
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'synced': self.synced
        }

class SyncLog(db.Model):
    """Sync log for tracking changes that need to be synchronized"""
    __tablename__ = 'sync_log'
    
    id = db.Column(db.Integer, primary_key=True)
    object_type = db.Column(db.String(50), nullable=False)  # 'card', 'deck', 'review'
    object_id = db.Column(db.Integer, nullable=False)
    operation = db.Column(db.String(20), nullable=False)  # 'CREATE', 'UPDATE', 'DELETE'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    synced = db.Column(db.Boolean, default=False)
    sync_error = db.Column(db.Text)
    
    # Device tracking
    device_id = db.Column(db.String(100))
    created_by = db.Column(db.String(100))
    
    def to_dict(self):
        return {
            'id': self.id,
            'object_type': self.object_type,
            'object_id': self.object_id,
            'operation': self.operation,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'synced': self.synced,
            'sync_error': self.sync_error,
            'device_id': self.device_id,
            'created_by': self.created_by
        }

class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # OAuth placeholders
    oauth_provider = db.Column(db.String(50))
    oauth_id = db.Column(db.String(255))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Sync tracking
    last_sync = db.Column(db.DateTime)
    device_id = db.Column(db.String(100), unique=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'device_id': self.device_id
        }

class SyncSession(db.Model):
    """Sync session tracking"""
    __tablename__ = 'sync_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    device_id = db.Column(db.String(100), nullable=False)
    session_token = db.Column(db.String(255), unique=True, nullable=False)
    
    # Sync statistics
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='in_progress')  # 'in_progress', 'completed', 'failed'
    
    # Sync metrics
    pulled_objects = db.Column(db.Integer, default=0)
    pushed_objects = db.Column(db.Integer, default=0)
    conflicts = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'device_id': self.device_id,
            'session_token': self.session_token,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'status': self.status,
            'pulled_objects': self.pulled_objects,
            'pushed_objects': self.pushed_objects,
            'conflicts': self.conflicts
        }