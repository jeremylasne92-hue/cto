"""
Clean Flashcard Sync Engine - Working Backend
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import json

# Initialize extensions
db = SQLAlchemy()

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flashcards.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SYNC_TOKEN_EXPIRE_HOURS'] = 24
    
    # Initialize extensions
    CORS(app, origins=['http://localhost:3000', 'http://localhost:19006'])
    db.init_app(app)
    
    # Define models with proper relationship handling
    class User(db.Model):
        __tablename__ = 'users'
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(255), unique=True, nullable=False)
        password_hash = db.Column(db.String(255), nullable=False)
        device_id = db.Column(db.String(100), unique=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        last_login = db.Column(db.DateTime)
        last_sync = db.Column(db.DateTime)
        
        def to_dict(self):
            return {
                'id': self.id,
                'email': self.email,
                'device_id': self.device_id,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'last_login': self.last_login.isoformat() if self.last_login else None,
                'last_sync': self.last_sync.isoformat() if self.last_sync else None
            }
    
    class Deck(db.Model):
        __tablename__ = 'decks'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(255), nullable=False)
        description = db.Column(db.Text)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        sync_version = db.Column(db.Integer, default=1)
        
        def to_dict(self):
            return {
                'id': self.id,
                'name': self.name,
                'description': self.description,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None,
                'sync_version': self.sync_version,
                'card_count': len(self.cards) if hasattr(self, 'cards') else 0
            }
    
    class Card(db.Model):
        __tablename__ = 'cards'
        id = db.Column(db.Integer, primary_key=True)
        deck_id = db.Column(db.Integer, db.ForeignKey('decks.id'), nullable=False)
        question = db.Column(db.Text, nullable=False)
        answer = db.Column(db.Text, nullable=False)
        ease_factor = db.Column(db.Float, default=2.5)
        interval = db.Column(db.Integer, default=1)
        repetition = db.Column(db.Integer, default=0)
        next_review = db.Column(db.DateTime)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        sync_version = db.Column(db.Integer, default=1)
        
        deck = db.relationship('Deck', backref='cards')
        
        def to_dict(self):
            return {
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
                'sync_version': self.sync_version
            }
    
    class ReviewLog(db.Model):
        __tablename__ = 'review_logs'
        id = db.Column(db.Integer, primary_key=True)
        card_id = db.Column(db.Integer, db.ForeignKey('cards.id'), nullable=False)
        grade = db.Column(db.Integer, nullable=False)
        review_time = db.Column(db.DateTime, default=datetime.utcnow)
        previous_ease_factor = db.Column(db.Float)
        previous_interval = db.Column(db.Integer)
        previous_repetition = db.Column(db.Integer)
        new_ease_factor = db.Column(db.Float)
        new_interval = db.Column(db.Integer)
        new_repetition = db.Column(db.Integer)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        synced = db.Column(db.Boolean, default=False)
        
        card = db.relationship('Card', backref='reviews')
        
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
        __tablename__ = 'sync_log'
        id = db.Column(db.Integer, primary_key=True)
        object_type = db.Column(db.String(50), nullable=False)
        object_id = db.Column(db.Integer, nullable=False)
        operation = db.Column(db.String(20), nullable=False)
        timestamp = db.Column(db.DateTime, default=datetime.utcnow)
        synced = db.Column(db.Boolean, default=False)
        sync_error = db.Column(db.Text)
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
    
    # Create tables and initialize data
    with app.app_context():
        db.create_all()
        initialize_data(User, Deck, Card)
    
    # Authentication decorator
    def require_auth(f):
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': 'No valid authorization header'}), 401
            
            try:
                token = auth_header.split(' ')[1]
                payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
                user = User.query.get(payload['user_id'])
                if not user:
                    return jsonify({'error': 'User not found'}), 401
                kwargs['current_user'] = user
                return f(*args, **kwargs)
            except jwt.ExpiredSignatureError:
                return jsonify({'error': 'Token expired'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'error': 'Invalid token'}), 401
            except Exception as e:
                return jsonify({'error': 'Authentication failed'}), 401
        
        decorated_function.__name__ = f.__name__
        return decorated_function
    
    # Routes
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected' if db.engine else 'disconnected',
            'version': '1.0.0'
        })
    
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        data = request.get_json() or {}
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400
        
        try:
            # Check if user already exists
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user:
                return jsonify({'error': 'User already exists'}), 400
            
            # Hash password
            password_hash = generate_password_hash(data['password'])
            
            # Generate device ID if not provided
            device_id = data.get('device_id') or f"device-{data['email'].split('@')[0]}-{datetime.utcnow().strftime('%Y%m%d')}"
            
            # Create user
            user = User(
                email=data['email'],
                password_hash=password_hash,
                device_id=device_id,
                last_login=datetime.utcnow()
            )
            
            db.session.add(user)
            db.session.flush()
            
            # Generate token
            token = generate_token(user, app.config)
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'user': user.to_dict(),
                'token': token,
                'expires_at': (datetime.utcnow() + timedelta(hours=24)).isoformat()
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        data = request.get_json() or {}
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400
        
        try:
            # Find user
            user = User.query.filter_by(email=data['email']).first()
            if not user:
                return jsonify({'error': 'Invalid credentials'}), 401
            
            # Check password
            if not check_password_hash(user.password_hash, data['password']):
                return jsonify({'error': 'Invalid credentials'}), 401
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Generate token
            token = generate_token(user, app.config)
            
            return jsonify({
                'success': True,
                'user': user.to_dict(),
                'token': token,
                'expires_at': (datetime.utcnow() + timedelta(hours=24)).isoformat()
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/decks', methods=['GET'])
    @require_auth
    def get_decks(*args, **kwargs):
        try:
            decks = Deck.query.all()
            
            return jsonify({
                'decks': [deck.to_dict() for deck in decks],
                'total': len(decks)
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/cards/due', methods=['GET'])
    @require_auth
    def get_due_cards(*args, **kwargs):
        try:
            now = datetime.utcnow()
            due_cards = Card.query.filter(
                Card.next_review <= now
            ).limit(50).all()
            
            return jsonify({
                'cards': [card.to_dict() for card in due_cards],
                'due_count': len(due_cards),
                'query_time': now.isoformat()
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/reviews', methods=['POST'])
    @require_auth
    def submit_review(*args, **kwargs):
        try:
            current_user = kwargs.get('current_user')
            data = request.get_json() or {}
            
            if not data.get('card_id') or data.get('grade') is None:
                return jsonify({'error': 'card_id and grade required'}), 400
            
            card = Card.query.get_or_404(data['card_id'])
            grade = data['grade']
            
            if not 0 <= grade <= 5:
                return jsonify({'error': 'Grade must be between 0 and 5'}), 400
            
            # Calculate new SRS values
            new_srs = calculate_srs_update(card, grade)
            
            # Create review log
            review_log = ReviewLog(
                card_id=card.id,
                grade=grade,
                review_time=datetime.utcnow(),
                previous_ease_factor=card.ease_factor,
                previous_interval=card.interval,
                previous_repetition=card.repetition,
                new_ease_factor=new_srs['ease_factor'],
                new_interval=new_srs['interval'],
                new_repetition=new_srs['repetition']
            )
            
            # Update card SRS values
            card.ease_factor = new_srs['ease_factor']
            card.interval = new_srs['interval']
            card.repetition = new_srs['repetition']
            card.next_review = datetime.utcnow() + timedelta(days=new_srs['interval'])
            card.updated_at = datetime.utcnow()
            
            db.session.add(review_log)
            db.session.flush()  # Get the review_log.id
            
            # Log for sync
            sync_log = SyncLog(
                object_type='review',
                object_id=review_log.id,
                operation='CREATE',
                device_id=current_user.device_id,
                created_by=current_user.email
            )
            db.session.add(sync_log)
            
            db.session.commit()
            
            return jsonify({
                'review': review_log.to_dict(),
                'card': card.to_dict(),
                'message': 'Review submitted successfully'
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/sync/pull', methods=['POST'])
    @require_auth
    def sync_pull(*args, **kwargs):
        try:
            current_user = kwargs.get('current_user')
            data = request.get_json() or {}
            last_sync = data.get('last_sync')
            
            # For MVP, return all cards and decks
            decks = Deck.query.all()
            cards = Card.query.limit(100).all()
            reviews = ReviewLog.query.limit(50).all()
            
            # Update last sync time
            current_user.last_sync = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'success': True,
                'data': {
                    'decks': [deck.to_dict() for deck in decks],
                    'cards': [card.to_dict() for card in cards],
                    'reviews': [review.to_dict() for review in reviews],
                    'metadata': {
                        'last_sync': current_user.last_sync.isoformat(),
                        'changes_count': 0,
                        'sync_session_id': 1
                    }
                }
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/sync/push', methods=['POST'])
    @require_auth
    def sync_push(*args, **kwargs):
        try:
            data = request.get_json() or {}
            changes = data.get('changes', [])
            
            # For MVP, just mark all sync logs as synced
            unsynced_logs = SyncLog.query.filter_by(synced=False).all()
            for log in unsynced_logs:
                log.synced = True
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'pushed_objects': len(unsynced_logs),
                'conflicts': 0,
                'session': {
                    'id': 1,
                    'status': 'completed',
                    'pushed_objects': len(unsynced_logs)
                }
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/sync/status', methods=['GET'])
    @require_auth
    def sync_status(*args, **kwargs):
        try:
            current_user = kwargs.get('current_user')
            unsynced_count = SyncLog.query.filter_by(synced=False).count()
            
            return jsonify({
                'unsynced_changes': unsynced_count,
                'last_sync': current_user.last_sync.isoformat() if current_user.last_sync else None,
                'device_id': current_user.device_id,
                'recent_sessions': []
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app

def generate_token(user, config):
    """Generate JWT token"""
    payload = {
        'user_id': user.id,
        'email': user.email,
        'device_id': user.device_id,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, config['SECRET_KEY'], algorithm='HS256')

def calculate_srs_update(card, grade):
    """Calculate SRS update using SuperMemo 2 algorithm"""
    ease_factor = card.ease_factor + (0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02))
    
    if ease_factor < 1.3:
        ease_factor = 1.3
    
    if grade < 3:
        repetition = 0
        interval = 1
    else:
        if card.repetition == 0:
            interval = 1
        elif card.repetition == 1:
            interval = 6
        else:
            interval = round(card.interval * ease_factor)
        repetition = card.repetition + 1
    
    return {
        'ease_factor': round(ease_factor, 2),
        'interval': interval,
        'repetition': repetition
    }

def initialize_data(User, Deck, Card):
    """Initialize database with sample data"""
    # Check if we already have data
    if User.query.first():
        return
    
    print("🔧 Initializing database with sample data...")
    
    # Create default user
    default_user = User(
        email='demo@example.com',
        password_hash=generate_password_hash('demo123'),
        device_id='desktop-demo',
        last_login=datetime.utcnow()
    )
    db.session.add(default_user)
    db.session.flush()
    
    # Create sample decks
    sample_decks = [
        Deck(name='Mathematics', description='Math formulas and concepts'),
        Deck(name='Science', description='Biology, Chemistry, Physics'),
        Deck(name='Languages', description='English, Spanish, French vocabulary'),
        Deck(name='History', description='World history and important events')
    ]
    
    for deck in sample_decks:
        db.session.add(deck)
    db.session.flush()
    
    # Create sample cards
    sample_cards = [
        # Math cards
        Card(deck_id=sample_decks[0].id, question='What is the derivative of x²?', answer='2x'),
        Card(deck_id=sample_decks[0].id, question='What is the value of π (pi)?', answer='Approximately 3.14159'),
        
        # Science cards
        Card(deck_id=sample_decks[1].id, question='What is the powerhouse of the cell?', answer='Mitochondria'),
        Card(deck_id=sample_decks[1].id, question='What is the chemical formula for water?', answer='H₂O'),
        
        # Language cards
        Card(deck_id=sample_decks[2].id, question='How do you say "hello" in Spanish?', answer='Hola'),
        
        # History cards
        Card(deck_id=sample_decks[3].id, question='In which year did World War II end?', answer='1945'),
    ]
    
    # Set cards to be due for review
    for card in sample_cards:
        card.next_review = datetime.utcnow()  # Due now
    
    for card in sample_cards:
        db.session.add(card)
    
    db.session.commit()
    print("✅ Database initialized successfully!")
    print("👤 Demo user: demo@example.com")
    print("🔐 Password: demo123")

if __name__ == '__main__':
    app = create_app()
    print("🚀 Starting Flashcard Sync Engine Backend...")
    print("📍 Server will be available at: http://localhost:5000")
    print("📖 Health check: http://localhost:5000/health")
    print("🏁 Press Ctrl+C to stop the server")
    print("")
    
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)