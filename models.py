from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Deck(db.Model):
    """Represents a collection of cards."""
    __tablename__ = 'decks'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cards = db.relationship('Card', backref='deck', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }


class Card(db.Model):
    """Represents a single flashcard."""
    __tablename__ = 'cards'

    id = db.Column(db.Integer, primary_key=True)
    deck_id = db.Column(db.Integer, db.ForeignKey('decks.id'), nullable=False)
    front = db.Column(db.Text, nullable=False)
    back = db.Column(db.Text, nullable=False)
    card_type = db.Column(db.String(50), default='flashcard')  # quiz, flashcard, mindmap
    category = db.Column(db.String(50), default='default')  # For retention mechanics
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    srs_state = db.relationship('CardSRSState', uselist=False, backref='card', cascade='all, delete-orphan')
    review_logs = db.relationship('ReviewLog', backref='card', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'deck_id': self.deck_id,
            'front': self.front,
            'back': self.back,
            'card_type': self.card_type,
            'category': self.category,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }


class CardSRSState(db.Model):
    """Tracks the SRS state of a card."""
    __tablename__ = 'card_srs_state'

    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id'), nullable=False, unique=True)
    
    # FSRS-5 model parameters
    difficulty = db.Column(db.Float, default=5.0)  # D: 0-10
    stability = db.Column(db.Float, default=0.0)   # S: days
    retrievability = db.Column(db.Float, default=1.0)  # R: 0-1
    
    # Review tracking
    due_date = db.Column(db.DateTime, default=datetime.utcnow)
    reviews_count = db.Column(db.Integer, default=0)
    lapses = db.Column(db.Integer, default=0)
    last_review_at = db.Column(db.DateTime)
    
    # State flags
    is_leech = db.Column(db.Boolean, default=False)
    suspended = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'card_id': self.card_id,
            'difficulty': round(self.difficulty, 2),
            'stability': round(self.stability, 2),
            'retrievability': round(self.retrievability, 4),
            'due_date': self.due_date.isoformat(),
            'reviews_count': self.reviews_count,
            'lapses': self.lapses,
            'last_review_at': self.last_review_at.isoformat() if self.last_review_at else None,
            'is_leech': self.is_leech,
            'suspended': self.suspended,
        }


class ReviewLog(db.Model):
    """Append-only log of all reviews (for sync)."""
    __tablename__ = 'review_logs'

    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id'), nullable=False)
    
    # Review data
    grade = db.Column(db.Integer, nullable=False)  # 1-4: Again, Hard, Good, Easy
    review_duration = db.Column(db.Integer)  # seconds
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    session_id = db.Column(db.String(36))  # For grouping reviews in a session
    
    # State at time of review (for history)
    difficulty_before = db.Column(db.Float)
    stability_before = db.Column(db.Float)
    retrievability_before = db.Column(db.Float)
    
    difficulty_after = db.Column(db.Float)
    stability_after = db.Column(db.Float)
    retrievability_after = db.Column(db.Float)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'card_id': self.card_id,
            'grade': self.grade,
            'review_duration': self.review_duration,
            'timestamp': self.timestamp.isoformat(),
            'session_id': self.session_id,
            'difficulty_before': round(self.difficulty_before, 2) if self.difficulty_before else None,
            'stability_before': round(self.stability_before, 2) if self.stability_before else None,
            'retrievability_before': round(self.retrievability_before, 4) if self.retrievability_before else None,
            'difficulty_after': round(self.difficulty_after, 2) if self.difficulty_after else None,
            'stability_after': round(self.stability_after, 2) if self.stability_after else None,
            'retrievability_after': round(self.retrievability_after, 4) if self.retrievability_after else None,
        }


class SessionState(db.Model):
    """Tracks active review sessions."""
    __tablename__ = 'session_states'

    id = db.Column(db.String(36), primary_key=True)
    deck_id = db.Column(db.Integer, db.ForeignKey('decks.id'))
    
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime)
    
    cards_reviewed = db.Column(db.Integer, default=0)
    total_duration = db.Column(db.Integer, default=0)  # seconds
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'deck_id': self.deck_id,
            'started_at': self.started_at.isoformat(),
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'cards_reviewed': self.cards_reviewed,
            'total_duration': self.total_duration,
        }
