"""
Database initialization and management script
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from backend.app import create_app
from backend.models import db, User, Deck, Card, ReviewLog, SyncLog, SyncSession
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

def init_database():
    """Initialize the database with sample data"""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        print("Creating default user...")
        # Create default user
        default_user = User(
            email='demo@example.com',
            password_hash=generate_password_hash('demo123'),
            device_id='desktop-demo',
            last_login=datetime.utcnow()
        )
        db.session.add(default_user)
        db.session.flush()
        
        print("Creating sample decks...")
        # Create sample decks
        sample_decks = [
            Deck(
                name='Mathematics',
                description='Math formulas and concepts',
                sync_version=1
            ),
            Deck(
                name='Science',
                description='Biology, Chemistry, Physics',
                sync_version=1
            ),
            Deck(
                name='Languages',
                description='English, Spanish, French vocabulary',
                sync_version=1
            ),
            Deck(
                name='History',
                description='World history and important events',
                sync_version=1
            )
        ]
        
        for deck in sample_decks:
            db.session.add(deck)
        db.session.flush()
        
        print("Creating sample cards...")
        # Create sample cards for each deck
        sample_cards = [
            # Math cards
            Card(
                deck_id=sample_decks[0].id,
                question='What is the derivative of x²?',
                answer='2x',
                next_review=datetime.utcnow() + timedelta(days=1),
                sync_version=1
            ),
            Card(
                deck_id=sample_decks[0].id,
                question='What is the value of π (pi)?',
                answer='Approximately 3.14159',
                next_review=datetime.utcnow() + timedelta(days=2),
                sync_version=1
            ),
            Card(
                deck_id=sample_decks[0].id,
                question='What is the quadratic formula?',
                answer='x = (-b ± √(b² - 4ac)) / 2a',
                next_review=datetime.utcnow() + timedelta(days=3),
                sync_version=1
            ),
            
            # Science cards
            Card(
                deck_id=sample_decks[1].id,
                question='What is the powerhouse of the cell?',
                answer='Mitochondria',
                next_review=datetime.utcnow() + timedelta(days=1),
                sync_version=1
            ),
            Card(
                deck_id=sample_decks[1].id,
                question='What is the chemical formula for water?',
                answer='H₂O',
                next_review=datetime.utcnow() + timedelta(days=2),
                sync_version=1
            ),
            
            # Language cards
            Card(
                deck_id=sample_decks[2].id,
                question='How do you say "hello" in Spanish?',
                answer='Hola',
                next_review=datetime.utcnow() + timedelta(days=1),
                sync_version=1
            ),
            Card(
                deck_id=sample_decks[2].id,
                question='How do you say "thank you" in French?',
                answer='Merci',
                next_review=datetime.utcnow() + timedelta(days=4),
                sync_version=1
            ),
            
            # History cards
            Card(
                deck_id=sample_decks[3].id,
                question='In which year did World War II end?',
                answer='1945',
                next_review=datetime.utcnow() + timedelta(days=5),
                sync_version=1
            ),
            Card(
                deck_id=sample_decks[3].id,
                question='Who was the first President of the United States?',
                answer='George Washington',
                next_review=datetime.utcnow() + timedelta(days=6),
                sync_version=1
            )
        ]
        
        for card in sample_cards:
            db.session.add(card)
        
        # Create initial sync logs
        print("Creating sync logs...")
        for card in sample_cards:
            sync_log = SyncLog(
                object_type='card',
                object_id=card.id,
                operation='CREATE',
                device_id='desktop-demo',
                created_by='demo@example.com',
                synced=True
            )
            db.session.add(sync_log)
        
        # Commit all changes
        db.session.commit()
        
        print(f"✅ Database initialized successfully!")
        print(f"📧 Demo user: demo@example.com")
        print(f"🔐 Password: demo123")
        print(f"📚 Created {len(sample_decks)} decks with {len(sample_cards)} cards")
        print(f"🖥️  Default device: desktop-demo")
        print(f"🌐 API will be available at: http://localhost:5000")

def reset_database():
    """Reset the database (drop and recreate all tables)"""
    app = create_app()
    
    with app.app_context():
        db.drop_all()
        print("Database dropped.")
        init_database()

def show_stats():
    """Show database statistics"""
    app = create_app()
    
    with app.app_context():
        user_count = User.query.count()
        deck_count = Deck.query.count()
        card_count = Card.query.count()
        review_count = ReviewLog.query.count()
        sync_log_count = SyncLog.query.count()
        
        print("📊 Database Statistics:")
        print(f"   Users: {user_count}")
        print(f"   Decks: {deck_count}")
        print(f"   Cards: {card_count}")
        print(f"   Reviews: {review_count}")
        print(f"   Sync logs: {sync_log_count}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'init':
            init_database()
        elif command == 'reset':
            reset_database()
        elif command == 'stats':
            show_stats()
        else:
            print("Available commands: init, reset, stats")
    else:
        init_database()