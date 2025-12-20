"""
API routes for flashcard sync engine
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
import jwt
import bcrypt

# Import models
from ..models import db, Deck, Card, ReviewLog, SyncLog, User, SyncSession
from ..services.sync_service import SyncService
from ..services.auth_service import AuthService

api_bp = Blueprint('api', __name__)

# Service instances (will be initialized after app context is ready)
sync_service = None
auth_service = None

def init_services():
    """Initialize services after app context is ready"""
    global sync_service, auth_service
    sync_service = SyncService()
    
    # Initialize services with app context
    from flask import current_app
    auth_service = AuthService(current_app)

@api_bp.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

# Authentication endpoints

@api_bp.route('/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    try:
        result = auth_service.login(data['email'], data['password'])
        if result['success']:
            return jsonify(result)
        else:
            return jsonify({'error': result['error']}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/auth/register', methods=['POST'])
def register():
    """User registration endpoint"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    try:
        result = auth_service.register(data['email'], data['password'], data.get('device_id'))
        if result['success']:
            return jsonify(result)
        else:
            return jsonify({'error': result['error']}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/auth/verify', methods=['POST'])
def verify_token():
    """Verify auth token"""
    data = request.get_json()
    token = data.get('token') if data else None
    
    if not token:
        return jsonify({'error': 'Token required'}), 400
    
    try:
        result = auth_service.verify_token(token)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Deck endpoints

@api_bp.route('/decks', methods=['GET'])
def get_decks():
    """Get all decks"""
    try:
        if not auth_service:
            return jsonify({'error': 'Service not initialized'}), 500
        
        user = auth_service.get_current_user()
        decks = Deck.query.all()
        
        return jsonify({
            'decks': [deck.to_dict() for deck in decks],
            'total': len(decks)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/decks/<int:deck_id>/cards', methods=['GET'])
@auth_service.require_auth
def get_deck_cards(deck_id):
    """Get cards for a specific deck"""
    try:
        deck = Deck.query.get_or_404(deck_id)
        cards = Card.query.filter_by(deck_id=deck_id).all()
        
        return jsonify({
            'deck': deck.to_dict(),
            'cards': [card.to_dict() for card in cards],
            'total': len(cards)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Cards endpoints

@api_bp.route('/cards/due', methods=['GET'])
@auth_service.require_auth
def get_due_cards():
    """Get cards due for review"""
    try:
        user = auth_service.get_current_user()
        now = datetime.utcnow()
        
        # Get due cards
        due_cards = Card.query.filter(
            Card.next_review <= now
        ).limit(50).all()  # Limit to 50 cards for performance
        
        return jsonify({
            'cards': [card.to_dict() for card in due_cards],
            'due_count': len(due_cards),
            'query_time': now.isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/cards', methods=['POST'])
@auth_service.require_auth
def create_card():
    """Create a new card"""
    try:
        user = auth_service.get_current_user()
        data = request.get_json()
        
        if not data or not data.get('question') or not data.get('answer') or not data.get('deck_id'):
            return jsonify({'error': 'Question, answer, and deck_id required'}), 400
        
        card = Card(
            deck_id=data['deck_id'],
            question=data['question'],
            answer=data['answer'],
            ease_factor=data.get('ease_factor', 2.5),
            interval=data.get('interval', 1),
            repetition=data.get('repetition', 0)
        )
        
        # Set next review date
        if card.next_review is None:
            card.next_review = datetime.utcnow()
        
        db.session.add(card)
        db.session.flush()
        
        # Log for sync
        sync_log = SyncLog(
            object_type='card',
            object_id=card.id,
            operation='CREATE',
            device_id=user.device_id,
            created_by=user.email
        )
        db.session.add(sync_log)
        
        db.session.commit()
        
        return jsonify({
            'card': card.to_dict(),
            'message': 'Card created successfully'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Review endpoints

@api_bp.route('/reviews', methods=['POST'])
@auth_service.require_auth
def submit_review():
    """Submit a review result"""
    try:
        user = auth_service.get_current_user()
        data = request.get_json()
        
        if not data or not data.get('card_id') or data.get('grade') is None:
            return jsonify({'error': 'card_id and grade required'}), 400
        
        card = Card.query.get_or_404(data['card_id'])
        grade = data['grade']
        
        if not 0 <= grade <= 5:
            return jsonify({'error': 'Grade must be between 0 and 5'}), 400
        
        # Calculate new SRS values
        new_srs = sync_service.calculate_srs_update(card, grade)
        
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
            new_repetition=new_srs['repetition'],
            synced=False
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
            device_id=user.device_id,
            created_by=user.email
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

@api_bp.route('/reviews/<int:card_id>', methods=['GET'])
@auth_service.require_auth
def get_card_reviews(card_id):
    """Get review history for a card"""
    try:
        card = Card.query.get_or_404(card_id)
        reviews = ReviewLog.query.filter_by(card_id=card_id).order_by(ReviewLog.review_time.desc()).all()
        
        return jsonify({
            'card': card.to_dict(),
            'reviews': [review.to_dict() for review in reviews],
            'total': len(reviews)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Content endpoints

@api_bp.route('/content', methods=['GET'])
@auth_service.require_auth
def get_content():
    """Get ingested content metadata"""
    try:
        # For now, return decks as content metadata
        decks = Deck.query.all()
        
        content_metadata = {
            'decks': [deck.to_dict() for deck in decks],
            'total_decks': len(decks),
            'total_cards': Card.query.count(),
            'last_updated': datetime.utcnow().isoformat()
        }
        
        return jsonify(content_metadata)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Sync endpoints

@api_bp.route('/sync/pull', methods=['POST'])
@auth_service.require_auth
def sync_pull():
    """Pull changes from server"""
    try:
        user = auth_service.get_current_user()
        data = request.get_json() or {}
        last_sync = data.get('last_sync')
        
        # Parse last sync timestamp
        if last_sync:
            try:
                last_sync = datetime.fromisoformat(last_sync.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid last_sync timestamp format'}), 400
        
        result = sync_service.pull_changes(user, last_sync)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/sync/push', methods=['POST'])
@auth_service.require_auth
def sync_push():
    """Push local changes to server"""
    try:
        user = auth_service.get_current_user()
        data = request.get_json()
        
        if not data or 'changes' not in data:
            return jsonify({'error': 'Changes data required'}), 400
        
        result = sync_service.push_changes(user, data['changes'])
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/sync/status', methods=['GET'])
@auth_service.require_auth
def sync_status():
    """Get sync status"""
    try:
        user = auth_service.get_current_user()
        
        # Get unsynced changes
        unsynced_count = SyncLog.query.filter_by(synced=False).count()
        
        # Get last sync time
        last_sync = user.last_sync
        
        # Get recent sync sessions
        recent_sessions = SyncSession.query.filter_by(user_id=user.id)\
            .order_by(SyncSession.started_at.desc()).limit(5).all()
        
        return jsonify({
            'unsynced_changes': unsynced_count,
            'last_sync': last_sync.isoformat() if last_sync else None,
            'device_id': user.device_id,
            'recent_sessions': [session.to_dict() for session in recent_sessions]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/sync/force', methods=['POST'])
@auth_service.require_auth
def force_sync():
    """Force sync all pending changes"""
    try:
        user = auth_service.get_current_user()
        
        result = sync_service.force_sync_all(user)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500