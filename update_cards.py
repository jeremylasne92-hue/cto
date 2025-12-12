#!/usr/bin/env python3
"""
Update sample cards to be due for review
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app import create_app, db
from datetime import datetime

def update_cards():
    app = create_app()
    
    with app.app_context():
        # Update all cards to be due for review
        from app import Card
        
        cards = Card.query.all()
        for card in cards:
            card.next_review = datetime.utcnow()  # Due now
        
        db.session.commit()
        print(f"✅ Updated {len(cards)} cards to be due for review")

if __name__ == '__main__':
    update_cards()