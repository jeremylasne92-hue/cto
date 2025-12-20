"""
Test suite for SRS Engine.

Tests FSRS-5 algorithm, scheduling, and API endpoints.
"""

import unittest
from datetime import datetime, timedelta
import os
import tempfile

from main import create_app
from models import db, Deck, Card, CardSRSState, ReviewLog
from fsrs5_algorithm import FSRS5
from review_manager import ReviewManager
from scheduling import SessionScheduler
from deck_manager import DeckManager
from card_manager import CardManager


class TestFSRS5Algorithm(unittest.TestCase):
    """Test FSRS-5 algorithm implementation."""
    
    def setUp(self):
        self.fsrs = FSRS5()
    
    def test_next_interval_calculation(self):
        """Test interval calculation."""
        stability = 10.0
        interval = self.fsrs.get_next_interval(stability, target_retention=0.9)
        
        self.assertGreater(interval, 0)
        self.assertLess(interval, stability * 2)  # Should be reasonable
    
    def test_difficulty_update(self):
        """Test difficulty update formula."""
        # Grade 1 (wrong) should increase difficulty
        new_diff = self.fsrs.next_difficulty(5.0, grade=1)
        self.assertGreater(new_diff, 5.0)
        
        # Grade 4 (easy) should decrease difficulty
        new_diff = self.fsrs.next_difficulty(5.0, grade=4)
        self.assertLess(new_diff, 5.0)
    
    def test_stability_increase(self):
        """Test that stability increases with correct answers."""
        initial_stability = 2.0
        
        # Grade 4 (easy) should increase stability significantly
        new_stability = self.fsrs.next_stability(
            stability=initial_stability,
            difficulty=5.0,
            grade=4,
            retrievability=0.9,
            elapsed_days=2.0
        )
        
        self.assertGreater(new_stability, initial_stability)
    
    def test_retrievability_decay(self):
        """Test retrievability exponential decay."""
        initial_r = 1.0
        stability = 10.0
        
        # After 10 days, retrievability should decay significantly
        new_r = self.fsrs.next_retrievability(initial_r, stability, elapsed_days=10)
        self.assertLess(new_r, initial_r)
        self.assertGreater(new_r, 0)
    
    def test_review_state_update(self):
        """Test complete review state update."""
        difficulty, stability, retrievability = self.fsrs.review(
            grade=3,
            difficulty=5.0,
            stability=4.0,
            retrievability=0.9,
            elapsed_days=2.0
        )
        
        self.assertGreater(difficulty, 0)
        self.assertLess(difficulty, 10)
        self.assertGreater(stability, 0)
        self.assertGreater(retrievability, 0)
        self.assertLess(retrievability, 1)


class TestSRSEngine(unittest.TestCase):
    """Test SRS engine with Flask app."""
    
    def setUp(self):
        """Set up test app and database."""
        self.db_fd, self.db_path = tempfile.mkstemp()
        os.environ['DATABASE_URL'] = f'sqlite:///{self.db_path}'
        
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Clean up test database."""
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
    
    def test_create_deck(self):
        """Test deck creation."""
        response = self.client.post('/api/decks', json={
            'name': 'Test Deck',
            'description': 'A test deck'
        })
        
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['name'], 'Test Deck')
    
    def test_create_card(self):
        """Test card creation."""
        # Create a deck first
        response = self.client.post('/api/decks', json={
            'name': 'Test Deck'
        })
        deck_id = response.get_json()['data']['id']
        
        # Create a card
        response = self.client.post('/api/cards', json={
            'front': 'What is 2+2?',
            'back': '4',
            'deck_id': deck_id,
            'card_type': 'flashcard',
            'category': 'math'
        })
        
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['front'], 'What is 2+2?')
        self.assertEqual(data['data']['back'], '4')
    
    def test_get_due_cards(self):
        """Test getting due cards."""
        response = self.client.post('/api/decks', json={'name': 'Test Deck'})
        deck_id = response.get_json()['data']['id']
        
        # Create multiple cards
        for i in range(5):
            self.client.post('/api/cards', json={
                'front': f'Question {i}',
                'back': f'Answer {i}',
                'deck_id': deck_id
            })
        
        response = self.client.get('/api/reviews/due?deck_id=' + str(deck_id))
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertGreaterEqual(len(data['data']['cards']), 0)
    
    def test_submit_review(self):
        """Test submitting a review."""
        # Create deck and card
        response = self.client.post('/api/decks', json={'name': 'Test Deck'})
        deck_id = response.get_json()['data']['id']
        
        response = self.client.post('/api/cards', json={
            'front': 'Q',
            'back': 'A',
            'deck_id': deck_id
        })
        card_id = response.get_json()['data']['id']
        
        # Submit a review
        response = self.client.post('/api/reviews/submit', json={
            'card_id': card_id,
            'grade': 3,
            'duration_seconds': 30
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['grade'], 3)
        self.assertIn('state_after', data['data'])
    
    def test_card_suspension(self):
        """Test card suspension."""
        response = self.client.post('/api/decks', json={'name': 'Test Deck'})
        deck_id = response.get_json()['data']['id']
        
        response = self.client.post('/api/cards', json={
            'front': 'Q',
            'back': 'A',
            'deck_id': deck_id
        })
        card_id = response.get_json()['data']['id']
        
        # Suspend card
        response = self.client.post(f'/api/cards/{card_id}/suspend')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertTrue(data['data']['suspended'])
    
    def test_bulk_create_cards(self):
        """Test bulk card creation."""
        response = self.client.post('/api/decks', json={'name': 'Test Deck'})
        deck_id = response.get_json()['data']['id']
        
        cards_data = [
            {'front': 'Q1', 'back': 'A1'},
            {'front': 'Q2', 'back': 'A2'},
            {'front': 'Q3', 'back': 'A3'},
        ]
        
        response = self.client.post('/api/cards/bulk', json={
            'cards': cards_data,
            'deck_id': deck_id
        })
        
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['created_count'], 3)
    
    def test_deck_statistics(self):
        """Test deck statistics."""
        response = self.client.post('/api/decks', json={'name': 'Test Deck'})
        deck_id = response.get_json()['data']['id']
        
        # Create cards
        for i in range(3):
            self.client.post('/api/cards', json={
                'front': f'Q{i}',
                'back': f'A{i}',
                'deck_id': deck_id
            })
        
        response = self.client.get(f'/api/decks/{deck_id}/stats')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        stats = data['data']
        self.assertEqual(stats['total_cards'], 3)
    
    def test_session_creation(self):
        """Test session creation."""
        response = self.client.post('/api/sessions', json={
            'deck_id': 1
        })
        
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('session_id', data['data'])


class TestScheduling(unittest.TestCase):
    """Test scheduling system."""
    
    def setUp(self):
        """Set up test app."""
        self.db_fd, self.db_path = tempfile.mkstemp()
        os.environ['DATABASE_URL'] = f'sqlite:///{self.db_path}'
        
        self.app = create_app()
        
        with self.app.app_context():
            db.create_all()
            self.scheduler = SessionScheduler()
    
    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_session_ordering(self):
        """Test that session ordering works."""
        with self.app.app_context():
            # Create test data
            deck = Deck(name='Test')
            db.session.add(deck)
            db.session.commit()
            
            cards = []
            for i in range(5):
                card = Card(
                    deck_id=deck.id,
                    front=f'Q{i}',
                    back=f'A{i}',
                    category='default'
                )
                db.session.add(card)
                db.session.flush()
                
                srs = CardSRSState(
                    card_id=card.id,
                    difficulty=5.0 + i,
                    stability=1.0,
                    retrievability=0.9,
                    due_date=datetime.utcnow() - timedelta(hours=i),
                    reviews_count=i
                )
                db.session.add(srs)
                db.session.commit()
                cards.append(card)
            
            # Test ordering
            ordered = self.scheduler.build_session_order(cards)
            self.assertEqual(len(ordered), len(cards))


if __name__ == '__main__':
    unittest.main()
