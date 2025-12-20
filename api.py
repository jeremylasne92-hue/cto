"""
Flask API endpoints for SRS engine.

Provides REST API for:
- Deck management
- Card management
- Review submission
- Statistics
"""

from flask import Blueprint, request, jsonify
from datetime import datetime

from deck_manager import DeckManager
from card_manager import CardManager
from review_manager import ReviewManager
from scheduling import SessionScheduler, CardSelector
from models import db, Card, Deck, CardSRSState

# Create blueprints
deck_bp = Blueprint('decks', __name__, url_prefix='/api/decks')
card_bp = Blueprint('cards', __name__, url_prefix='/api/cards')
review_bp = Blueprint('reviews', __name__, url_prefix='/api/reviews')
session_bp = Blueprint('sessions', __name__, url_prefix='/api/sessions')

# Managers will be lazily initialized
_managers = {}

def get_deck_manager():
    if 'deck_manager' not in _managers:
        _managers['deck_manager'] = DeckManager()
    return _managers['deck_manager']

def get_card_manager():
    if 'card_manager' not in _managers:
        _managers['card_manager'] = CardManager()
    return _managers['card_manager']

def get_review_manager():
    if 'review_manager' not in _managers:
        _managers['review_manager'] = ReviewManager()
    return _managers['review_manager']

def get_scheduler():
    if 'scheduler' not in _managers:
        _managers['scheduler'] = SessionScheduler()
    return _managers['scheduler']


# ============================================================================
# Deck Management Endpoints
# ============================================================================

@deck_bp.route('', methods=['GET'])
def list_decks():
    """Get all decks with statistics."""
    try:
        decks = get_deck_manager().get_all_decks()
        return jsonify({'success': True, 'data': decks}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@deck_bp.route('', methods=['POST'])
def create_deck():
    """Create a new deck."""
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'success': False, 'error': 'Name is required'}), 400
        
        deck = get_deck_manager().create_deck(
            name=data['name'],
            description=data.get('description', '')
        )
        return jsonify({'success': True, 'data': deck}), 201
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 409
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@deck_bp.route('/<int:deck_id>', methods=['GET'])
def get_deck(deck_id):
    """Get a specific deck with statistics."""
    try:
        deck = get_deck_manager().get_deck(deck_id)
        stats = get_deck_manager().get_deck_stats(deck_id)
        deck['stats'] = stats
        return jsonify({'success': True, 'data': deck}), 200
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@deck_bp.route('/<int:deck_id>', methods=['DELETE'])
def delete_deck(deck_id):
    """Delete a deck."""
    try:
        move_cards = request.args.get('move_cards', 'true').lower() == 'true'
        result = get_deck_manager().delete_deck(deck_id, move_cards)
        return jsonify({'success': True, 'data': result}), 200
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@deck_bp.route('/<int:deck_id>/stats', methods=['GET'])
def get_deck_stats(deck_id):
    """Get deck statistics."""
    try:
        stats = get_deck_manager().get_deck_stats(deck_id)
        return jsonify({'success': True, 'data': stats}), 200
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# Card Management Endpoints
# ============================================================================

@card_bp.route('', methods=['GET'])
def list_cards():
    """Get all cards, optionally filtered by deck."""
    try:
        deck_id = request.args.get('deck_id', type=int)
        if deck_id:
            cards = get_card_manager().get_cards_by_deck(deck_id)
        else:
            cards = get_card_manager().get_all_cards()
        return jsonify({'success': True, 'data': cards}), 200
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@card_bp.route('', methods=['POST'])
def create_card():
    """Create a new card."""
    try:
        data = request.get_json()
        if not data or 'front' not in data or 'back' not in data:
            return jsonify({'success': False, 'error': 'Front and back are required'}), 400
        
        card = get_card_manager().create_card(
            front=data['front'],
            back=data['back'],
            deck_id=data.get('deck_id'),
            card_type=data.get('card_type', 'flashcard'),
            category=data.get('category', 'default')
        )
        return jsonify({'success': True, 'data': card}), 201
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@card_bp.route('/bulk', methods=['POST'])
def bulk_create_cards():
    """Bulk create cards."""
    try:
        data = request.get_json()
        if not data or 'cards' not in data:
            return jsonify({'success': False, 'error': 'Cards list is required'}), 400
        
        result = get_card_manager().bulk_create_cards(
            cards_data=data['cards'],
            deck_id=data.get('deck_id')
        )
        return jsonify({'success': True, 'data': result}), 201
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@card_bp.route('/<int:card_id>', methods=['GET'])
def get_card(card_id):
    """Get a specific card with SRS state."""
    try:
        card = get_card_manager().get_card(card_id)
        return jsonify({'success': True, 'data': card}), 200
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@card_bp.route('/<int:card_id>', methods=['PUT'])
def update_card(card_id):
    """Update a card."""
    try:
        data = request.get_json()
        card = get_card_manager().update_card(
            card_id=card_id,
            front=data.get('front'),
            back=data.get('back'),
            card_type=data.get('card_type'),
            category=data.get('category')
        )
        return jsonify({'success': True, 'data': card}), 200
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@card_bp.route('/<int:card_id>', methods=['DELETE'])
def delete_card(card_id):
    """Delete a card."""
    try:
        result = get_card_manager().delete_card(card_id)
        return jsonify({'success': True, 'data': result}), 200
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@card_bp.route('/<int:card_id>/suspend', methods=['POST'])
def suspend_card(card_id):
    """Suspend a card."""
    try:
        result = get_card_manager().suspend_card(card_id)
        return jsonify({'success': True, 'data': result}), 200
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@card_bp.route('/<int:card_id>/unsuspend', methods=['POST'])
def unsuspend_card(card_id):
    """Unsuspend a card."""
    try:
        result = get_card_manager().unsuspend_card(card_id)
        return jsonify({'success': True, 'data': result}), 200
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@card_bp.route('/<int:card_id>/reset', methods=['POST'])
def reset_card(card_id):
    """Reset a card's SRS state."""
    try:
        result = get_card_manager().reset_card(card_id)
        return jsonify({'success': True, 'data': result}), 200
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@card_bp.route('/search', methods=['GET'])
def search_cards():
    """Search cards."""
    try:
        query = request.args.get('q', '')
        deck_id = request.args.get('deck_id', type=int)
        
        if not query:
            return jsonify({'success': False, 'error': 'Query parameter q is required'}), 400
        
        results = get_card_manager().search_cards(query, deck_id)
        return jsonify({'success': True, 'data': results}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# Review Endpoints
# ============================================================================

@review_bp.route('/due', methods=['GET'])
def get_due_cards():
    """Get cards due for review today."""
    try:
        deck_id = request.args.get('deck_id', type=int)
        limit = request.args.get('limit', 20, type=int)
        
        scheduler = get_scheduler()
        due_cards = scheduler.get_due_cards(deck_id)
        ordered_cards = scheduler.build_session_order(due_cards)
        selected_cards, remaining = scheduler.select_session_cards(ordered_cards, limit)
        
        card_data = []
        for card in selected_cards:
            card_dict = card.to_dict()
            if card.srs_state:
                card_dict['srs_state'] = card.srs_state.to_dict()
            card_data.append(card_dict)
        
        return jsonify({
            'success': True,
            'data': {
                'cards': card_data,
                'total_due': len(due_cards),
                'selected_count': len(selected_cards),
                'remaining_count': len(remaining),
                'estimated_duration_seconds': scheduler.estimate_session_duration(selected_cards),
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@review_bp.route('/submit', methods=['POST'])
def submit_review():
    """Submit a review for a card."""
    try:
        data = request.get_json()
        if not data or 'card_id' not in data or 'grade' not in data:
            return jsonify({'success': False, 'error': 'card_id and grade are required'}), 400
        
        result = get_review_manager().submit_review(
            card_id=data['card_id'],
            grade=data['grade'],
            duration_seconds=data.get('duration_seconds', 0),
            session_id=data.get('session_id')
        )
        return jsonify({'success': True, 'data': result}), 200
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@review_bp.route('/skip', methods=['POST'])
def skip_review():
    """Skip reviewing a card."""
    try:
        data = request.get_json()
        if not data or 'card_id' not in data:
            return jsonify({'success': False, 'error': 'card_id is required'}), 400
        
        result = get_review_manager().skip_review(
            card_id=data['card_id'],
            session_id=data.get('session_id')
        )
        return jsonify({'success': True, 'data': result}), 200
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@review_bp.route('/<int:card_id>/history', methods=['GET'])
def get_review_history(card_id):
    """Get review history for a card."""
    try:
        limit = request.args.get('limit', 10, type=int)
        history = get_review_manager().get_review_history(card_id, limit)
        return jsonify({'success': True, 'data': history}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# Session Endpoints
# ============================================================================

@session_bp.route('', methods=['POST'])
def create_session():
    """Create a new review session."""
    try:
        data = request.get_json() or {}
        session_id = get_review_manager().create_session(deck_id=data.get('deck_id'))
        return jsonify({'success': True, 'data': {'session_id': session_id}}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@session_bp.route('/<session_id>', methods=['POST'])
def end_session(session_id):
    """End a review session."""
    try:
        data = request.get_json() or {}
        result = get_review_manager().end_session(
            session_id=session_id,
            total_duration=data.get('total_duration', 0)
        )
        return jsonify({'success': True, 'data': result}), 200
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@session_bp.route('/<session_id>/stats', methods=['GET'])
def get_session_stats(session_id):
    """Get statistics for a session."""
    try:
        stats = get_review_manager().get_session_stats(session_id)
        return jsonify({'success': True, 'data': stats}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# Health Check
# ============================================================================

@review_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'success': True, 'status': 'healthy'}), 200


def register_blueprints(app):
    """Register all blueprints with the Flask app."""
    app.register_blueprint(deck_bp)
    app.register_blueprint(card_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(session_bp)
