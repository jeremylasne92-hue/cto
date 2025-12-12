"""
Simple Flask app for flashcard sync engine
"""

import os
from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

# Initialize extensions
db = SQLAlchemy()

def create_simple_app():
    """Create a simple Flask app"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flashcards.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SYNC_TOKEN_EXPIRE_HOURS'] = 24
    
    # Initialize extensions
    CORS(app, origins=['http://localhost:3000', 'http://localhost:19006'])
    db.init_app(app)
    
    # Simple models
    class User(db.Model):
        __tablename__ = 'users'
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(255), unique=True, nullable=False)
        password_hash = db.Column(db.String(255), nullable=False)
        device_id = db.Column(db.String(100), unique=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        last_login = db.Column(db.DateTime)
        last_sync = db.Column(db.DateTime)
    
    class Deck(db.Model):
        __tablename__ = 'decks'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(255), nullable=False)
        description = db.Column(db.Text)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        sync_version = db.Column(db.Integer, default=1)
        
        cards = db.relationship('Card', backref='deck', lazy=True, cascade='all, delete-orphan', foreign_keys='Card.deck_id')
    
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
    
    class SyncLog(db.Model):
        __tablename__ = 'sync_log'
        id = db.Column(db.Integer, primary_key=True)
        object_type = db.Column(db.String(50), nullable=False)
        object_id = db.Column(db.Integer, nullable=False)
        operation = db.Column(db.String(20), nullable=False)
        timestamp = db.Column(db.DateTime, default=datetime.utcnow)
        synced = db.Column(db.Boolean, default=False)
        sync_error = db.Column(db.Text)
    
    # Create tables
    with app.app_context():
        db.create_all()
        
        # Create default user if none exists
        if not User.query.first():
            create_default_user(User, Deck, Card)
    
    # Simple auth decorator
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
        data = request.get_json()
        if not data or not data.get('email') or not data.get('password'):
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
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'device_id': user.device_id,
                    'created_at': user.created_at.isoformat()
                },
                'token': token,
                'expires_at': (datetime.utcnow() + timedelta(hours=24)).isoformat()
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        data = request.get_json()
        if not data or not data.get('email') or not data.get('password'):
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
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'device_id': user.device_id,
                    'last_login': user.last_login.isoformat()
                },
                'token': token,
                'expires_at': (datetime.utcnow() + timedelta(hours=24)).isoformat()
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/decks', methods=['GET'])
    @require_auth
    def get_decks():
        try:
            decks = Deck.query.all()
            
            return jsonify({
                'decks': [{
                    'id': deck.id,
                    'name': deck.name,
                    'description': deck.description,
                    'created_at': deck.created_at.isoformat(),
                    'updated_at': deck.updated_at.isoformat(),
                    'sync_version': deck.sync_version,
                    'card_count': len(deck.cards)
                } for deck in decks],
                'total': len(decks)
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/cards/due', methods=['GET'])
    @require_auth
    def get_due_cards():
        try:
            now = datetime.utcnow()
            due_cards = Card.query.filter(
                Card.next_review <= now
            ).limit(50).all()
            
            return jsonify({
                'cards': [{
                    'id': card.id,
                    'deck_id': card.deck_id,
                    'question': card.question,
                    'answer': card.answer,
                    'ease_factor': card.ease_factor,
                    'interval': card.interval,
                    'repetition': card.repetition,
                    'next_review': card.next_review.isoformat() if card.next_review else None,
                    'created_at': card.created_at.isoformat(),
                    'updated_at': card.updated_at.isoformat(),
                    'sync_version': card.sync_version
                } for card in due_cards],
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
            data = request.get_json()
            
            if not data or not data.get('card_id') or data.get('grade') is None:
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
            
            # Log for sync
            sync_log = SyncLog(
                object_type='review',
                object_id=review_log.id,
                operation='CREATE',
                device_id=current_user.device_id,
                timestamp=datetime.utcnow()
            )
            db.session.add(sync_log)
            
            db.session.commit()
            
            return jsonify({
                'review': {
                    'id': review_log.id,
                    'card_id': review_log.card_id,
                    'grade': review_log.grade,
                    'review_time': review_log.review_time.isoformat(),
                    'previous_srs': {
                        'ease_factor': review_log.previous_ease_factor,
                        'interval': review_log.previous_interval,
                        'repetition': review_log.previous_repetition
                    },
                    'new_srs': {
                        'ease_factor': review_log.new_ease_factor,
                        'interval': review_log.new_interval,
                        'repetition': review_log.new_repetition
                    },
                    'created_at': review_log.created_at.isoformat(),
                    'synced': review_log.synced
                },
                'message': 'Review submitted successfully'
            }), 201
        except Exception as e:
            db.session.rollback()
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
                'device_id': current_user.device_id
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

def create_default_user(User, Deck, Card):
    """Create default user and sample data"""
    from werkzeug.security import generate_password_hash
    
    default_user = User(
        email='demo@example.com',
        password_hash=generate_password_hash('demo123'),
        device_id='desktop-demo',
        last_login=datetime.utcnow()
    )
    db.session.add(default_user)
    db.session.flush()
    
    # Create sample deck
    sample_deck = Deck(
        name='Sample Deck',
        description='A sample deck for testing sync'
    )
    db.session.add(sample_deck)
    db.session.flush()
    
    # Create sample cards
    sample_cards = [
        Card(
            deck_id=sample_deck.id,
            question='What is 2 + 2?',
            answer='4',
            next_review=datetime.utcnow() + timedelta(days=1)
        ),
        Card(
            deck_id=sample_deck.id,
            question='What is the capital of France?',
            answer='Paris',
            next_review=datetime.utcnow() + timedelta(days=1)
        ),
        Card(
            deck_id=sample_deck.id,
            question='What is Python?',
            answer='A programming language',
            next_review=datetime.utcnow() + timedelta(days=1)
        )
    ]
    
    for card in sample_cards:
        db.session.add(card)
    
    db.session.commit()
    print("✅ Created default user and sample data")

if __name__ == '__main__':
    app = create_simple_app()
    print("🚀 Starting Flashcard Sync Engine Backend...")
    print("📍 Server will be available at: http://localhost:5000")
    print("📖 Health check: http://localhost:5000/health")
    print("👤 Demo login: demo@example.com / demo123")
    app.run(debug=True, host='0.0.0.0', port=5000)