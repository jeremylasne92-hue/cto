"""
Flask application for flashcard sync engine
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# Import configurations
from .config import config

# Import models
from ..models import db, Deck, Card, ReviewLog, SyncLog, User, SyncSession

def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    CORS(app, origins=app.config['CORS_ORIGINS'])
    db.init_app(app)
    
    # Create tables
    with app.app_context():
        db.create_all()
        
        # Create default user if none exists
        if not User.query.first():
            create_default_user()
    
    # Register blueprints
    from ..api import api_bp, init_services
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Initialize services after app context is ready
    with app.app_context():
        init_services()
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected' if db.engine else 'disconnected'
        })
    
    return app

def create_default_user():
    """Create a default user for testing"""
    from werkzeug.security import generate_password_hash
    
    default_user = User(
        email='demo@example.com',
        password_hash=generate_password_hash('demo123'),
        device_id='desktop-demo',
        last_login=datetime.utcnow()
    )
    db.session.add(default_user)
    
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
    
    print("Created default user and sample data")

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)