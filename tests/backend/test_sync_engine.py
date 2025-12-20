"""
Test suite for backend flashcard sync engine
"""

import pytest
import json
from datetime import datetime
from backend.app import create_app
from backend.models import db, User, Deck, Card, ReviewLog, SyncLog

@pytest.fixture
def app():
    """Create test app"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def auth_headers(app):
    """Create authentication headers for testing"""
    with app.app_context():
        user = User(
            email='test@example.com',
            password_hash='hashed_password',
            device_id='test-device'
        )
        db.session.add(user)
        db.session.commit()
        
        # Mock auth token (simplified for testing)
        return {'Authorization': f'Bearer test_token_{user.id}'}

class TestUserAuthentication:
    """Test user authentication endpoints"""
    
    def test_user_registration(self, client):
        """Test user registration"""
        response = client.post('/api/auth/register', json={
            'email': 'newuser@example.com',
            'password': 'password123',
            'device_id': 'test-device'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'user' in data
        assert 'token' in data
    
    def test_user_login(self, client):
        """Test user login"""
        # First create a user
        client.post('/api/auth/register', json={
            'email': 'login@example.com',
            'password': 'password123'
        })
        
        # Then login
        response = client.post('/api/auth/login', json={
            'email': 'login@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'user' in data
        assert 'token' in data
    
    def test_invalid_login(self, client):
        """Test login with invalid credentials"""
        response = client.post('/api/auth/login', json={
            'email': 'invalid@example.com',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['error'] == 'Invalid credentials'

class TestDecks:
    """Test deck management endpoints"""
    
    def test_get_decks_empty(self, client, auth_headers):
        """Test getting empty decks list"""
        response = client.get('/api/decks', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'decks' in data
        assert 'total' in data
        assert data['total'] == 0
    
    def test_get_decks_with_data(self, client, auth_headers):
        """Test getting decks with sample data"""
        # Create sample deck
        deck = Deck(name='Test Deck', description='Test Description')
        db.session.add(deck)
        db.session.commit()
        
        response = client.get('/api/decks', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total'] == 1
        assert len(data['decks']) == 1
        assert data['decks'][0]['name'] == 'Test Deck'

class TestCards:
    """Test card management endpoints"""
    
    def test_get_due_cards_empty(self, client, auth_headers):
        """Test getting empty due cards"""
        response = client.get('/api/cards/due', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'cards' in data
        assert 'due_count' in data
        assert data['due_count'] == 0
    
    def test_create_card(self, client, auth_headers):
        """Test creating a new card"""
        # First create a deck
        deck = Deck(name='Test Deck')
        db.session.add(deck)
        db.session.flush()
        
        # Then create a card
        response = client.post('/api/cards', headers=auth_headers, json={
            'deck_id': deck.id,
            'question': 'Test question?',
            'answer': 'Test answer'
        })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'card' in data
        assert 'message' in data
        assert data['card']['question'] == 'Test question?'

class TestReviews:
    """Test review submission endpoints"""
    
    def test_submit_review(self, client, auth_headers):
        """Test submitting a review grade"""
        # Create deck and card first
        deck = Deck(name='Test Deck')
        db.session.add(deck)
        db.session.flush()
        
        card = Card(
            deck_id=deck.id,
            question='Test?',
            answer='Answer',
            ease_factor=2.5,
            interval=1,
            repetition=0
        )
        db.session.add(card)
        db.session.flush()
        
        # Submit review
        response = client.post('/api/reviews', headers=auth_headers, json={
            'card_id': card.id,
            'grade': 4
        })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'review' in data
        assert 'card' in data
        assert data['review']['grade'] == 4

class TestSync:
    """Test synchronization endpoints"""
    
    def test_sync_pull_empty(self, client, auth_headers):
        """Test pulling empty sync data"""
        response = client.post('/api/sync/pull', headers=auth_headers, json={})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
    
    def test_sync_status(self, client, auth_headers):
        """Test getting sync status"""
        response = client.get('/api/sync/status', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'unsynced_changes' in data
        assert 'last_sync' in data
        assert 'device_id' in data
    
    def test_force_sync(self, client, auth_headers):
        """Test force sync all pending changes"""
        response = client.post('/api/sync/force', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'synced_count' in data

class TestSyncService:
    """Test sync service logic"""
    
    def test_srs_calculation(self):
        """Test SRS algorithm calculation"""
        from backend.services.sync_service import SyncService
        
        sync_service = SyncService()
        
        # Mock card data
        card = type('Card', (), {
            'ease_factor': 2.5,
            'interval': 1,
            'repetition': 0
        })()
        
        # Test grade 4 (good recall)
        result = sync_service.calculate_srs_update(card, 4)
        
        assert result['ease_factor'] > 2.5  # Should increase
        assert result['interval'] == 6      # Should be 6 for second repetition
        assert result['repetition'] == 1    # Should increment
        
        # Test grade 2 (poor recall)
        result = sync_service.calculate_srs_update(card, 2)
        
        assert result['ease_factor'] < 2.5  # Should decrease
        assert result['interval'] == 1      # Should reset to 1
        assert result['repetition'] == 0    # Should reset to 0

class TestDataConsistency:
    """Test data validation and consistency"""
    
    def test_card_validation(self, client, auth_headers):
        """Test card creation validation"""
        # Missing required fields
        response = client.post('/api/cards', headers=auth_headers, json={
            'question': 'Only question'
        })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_review_validation(self, client, auth_headers):
        """Test review submission validation"""
        # Invalid grade
        response = client.post('/api/reviews', headers=auth_headers, json={
            'card_id': 1,
            'grade': 10  # Invalid grade
        })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_sync_log_creation(self, client, auth_headers):
        """Test that sync logs are created for changes"""
        # Create a card and verify sync log is created
        deck = Deck(name='Test Deck')
        db.session.add(deck)
        db.session.flush()
        
        initial_sync_count = SyncLog.query.count()
        
        client.post('/api/cards', headers=auth_headers, json={
            'deck_id': deck.id,
            'question': 'Test?',
            'answer': 'Answer'
        })
        
        final_sync_count = SyncLog.query.count()
        assert final_sync_count > initial_sync_count
        
        # Check the sync log
        latest_sync = SyncLog.query.order_by(SyncLog.id.desc()).first()
        assert latest_sync.object_type == 'card'
        assert latest_sync.operation == 'CREATE'