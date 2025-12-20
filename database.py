"""
Database initialization and management.
"""

import os
from flask import Flask
from models import db, Deck, Card, CardSRSState, ReviewLog, SessionState


def init_db(app: Flask):
    """
    Initialize the database.
    
    Creates all tables if they don't exist.
    
    Args:
        app: Flask application instance
    """
    with app.app_context():
        db.create_all()
        
        # Ensure default deck exists
        default_deck = Deck.query.filter_by(name='All').first()
        if not default_deck:
            default_deck = Deck(
                name='All',
                description='Default deck for all cards'
            )
            db.session.add(default_deck)
            db.session.commit()


def reset_db(app: Flask):
    """
    Reset the database (dangerous - for testing only).
    
    Args:
        app: Flask application instance
    """
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        # Recreate default deck
        default_deck = Deck(
            name='All',
            description='Default deck for all cards'
        )
        db.session.add(default_deck)
        db.session.commit()


def get_db_path():
    """Get the database file path."""
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///srs_engine.db')
    if db_url.startswith('sqlite:///'):
        return db_url.replace('sqlite:///', '')
    return db_url
