"""
Card management system.

Handles:
- Creating and deleting cards
- Updating card content
- Suspending/unsuspending cards
- Bulk operations
"""

from datetime import datetime
from typing import Dict, List

from models import db, Card, CardSRSState, Deck
from deck_manager import DeckManager


class CardManager:
    """Manages cards."""
    
    def __init__(self):
        self.deck_manager = DeckManager()
    
    def create_card(self,
                   front: str,
                   back: str,
                   deck_id: int = None,
                   card_type: str = 'flashcard',
                   category: str = 'default') -> Dict:
        """
        Create a new card.
        
        Args:
            front: Front side of card
            back: Back side of card
            deck_id: Deck ID (if None, adds to default deck)
            card_type: Type of card (flashcard, quiz, mindmap)
            category: Category for retention mechanics
            
        Returns:
            Card dictionary
            
        Raises:
            ValueError: If deck not found
        """
        if not deck_id:
            # Use default deck
            default_deck = Deck.query.filter_by(name=DeckManager.DEFAULT_DECK_NAME).first()
            if not default_deck:
                default_deck = Deck(name=DeckManager.DEFAULT_DECK_NAME)
                db.session.add(default_deck)
                db.session.commit()
            deck_id = default_deck.id
        
        deck = Deck.query.get(deck_id)
        if not deck:
            raise ValueError(f"Deck {deck_id} not found")
        
        card = Card(
            deck_id=deck_id,
            front=front,
            back=back,
            card_type=card_type,
            category=category,
        )
        
        db.session.add(card)
        db.session.commit()
        
        return card.to_dict()
    
    def delete_card(self, card_id: int) -> Dict:
        """
        Delete a card and its review logs.
        
        Args:
            card_id: Card ID
            
        Returns:
            Result dictionary
            
        Raises:
            ValueError: If card not found
        """
        card = Card.query.get(card_id)
        if not card:
            raise ValueError(f"Card {card_id} not found")
        
        db.session.delete(card)
        db.session.commit()
        
        return {
            'card_id': card_id,
            'action': 'deleted',
        }
    
    def get_card(self, card_id: int) -> Dict:
        """
        Get a card with full details.
        
        Args:
            card_id: Card ID
            
        Returns:
            Card dictionary with SRS state
        """
        card = Card.query.get(card_id)
        if not card:
            raise ValueError(f"Card {card_id} not found")
        
        result = card.to_dict()
        if card.srs_state:
            result['srs_state'] = card.srs_state.to_dict()
        else:
            result['srs_state'] = None
        
        return result
    
    def update_card(self,
                   card_id: int,
                   front: str = None,
                   back: str = None,
                   card_type: str = None,
                   category: str = None) -> Dict:
        """
        Update card content.
        
        Args:
            card_id: Card ID
            front: New front content (if None, unchanged)
            back: New back content (if None, unchanged)
            card_type: New card type (if None, unchanged)
            category: New category (if None, unchanged)
            
        Returns:
            Updated card dictionary
            
        Raises:
            ValueError: If card not found
        """
        card = Card.query.get(card_id)
        if not card:
            raise ValueError(f"Card {card_id} not found")
        
        if front is not None:
            card.front = front
        if back is not None:
            card.back = back
        if card_type is not None:
            card.card_type = card_type
        if category is not None:
            card.category = category
        
        card.updated_at = datetime.utcnow()
        db.session.commit()
        
        return card.to_dict()
    
    def suspend_card(self, card_id: int) -> Dict:
        """
        Suspend a card (won't show in reviews).
        
        Args:
            card_id: Card ID
            
        Returns:
            Result dictionary
            
        Raises:
            ValueError: If card not found
        """
        card = Card.query.get(card_id)
        if not card:
            raise ValueError(f"Card {card_id} not found")
        
        if not card.srs_state:
            srs_state = CardSRSState(card_id=card_id)
            db.session.add(srs_state)
        else:
            srs_state = card.srs_state
        
        srs_state.suspended = True
        db.session.commit()
        
        return {
            'card_id': card_id,
            'suspended': True,
        }
    
    def unsuspend_card(self, card_id: int) -> Dict:
        """
        Unsuspend a card.
        
        Args:
            card_id: Card ID
            
        Returns:
            Result dictionary
            
        Raises:
            ValueError: If card not found
        """
        card = Card.query.get(card_id)
        if not card:
            raise ValueError(f"Card {card_id} not found")
        
        if card.srs_state:
            card.srs_state.suspended = False
            db.session.commit()
        
        return {
            'card_id': card_id,
            'suspended': False,
        }
    
    def reset_card(self, card_id: int) -> Dict:
        """
        Reset a card's SRS state (like brand new).
        
        Args:
            card_id: Card ID
            
        Returns:
            Result dictionary
            
        Raises:
            ValueError: If card not found
        """
        card = Card.query.get(card_id)
        if not card:
            raise ValueError(f"Card {card_id} not found")
        
        if card.srs_state:
            db.session.delete(card.srs_state)
        
        db.session.commit()
        
        return {
            'card_id': card_id,
            'action': 'reset',
        }
    
    def get_cards_by_deck(self, deck_id: int) -> List[Dict]:
        """
        Get all cards in a deck.
        
        Args:
            deck_id: Deck ID
            
        Returns:
            List of card dictionaries
            
        Raises:
            ValueError: If deck not found
        """
        deck = Deck.query.get(deck_id)
        if not deck:
            raise ValueError(f"Deck {deck_id} not found")
        
        return [card.to_dict() for card in deck.cards]
    
    def get_all_cards(self) -> List[Dict]:
        """
        Get all cards.
        
        Returns:
            List of all card dictionaries
        """
        return [card.to_dict() for card in Card.query.all()]
    
    def search_cards(self, query: str, deck_id: int = None) -> List[Dict]:
        """
        Search cards by front or back content.
        
        Args:
            query: Search query
            deck_id: Optional deck ID to filter
            
        Returns:
            List of matching card dictionaries
        """
        base_query = Card.query.filter(
            (Card.front.ilike(f'%{query}%')) | (Card.back.ilike(f'%{query}%'))
        )
        
        if deck_id:
            base_query = base_query.filter_by(deck_id=deck_id)
        
        return [card.to_dict() for card in base_query.all()]
    
    def bulk_create_cards(self, cards_data: List[Dict], deck_id: int = None) -> Dict:
        """
        Bulk create cards from a list.
        
        Args:
            cards_data: List of card data dictionaries
            deck_id: Deck ID (if None, uses default)
            
        Returns:
            Result dictionary with created count
        """
        if not deck_id:
            default_deck = Deck.query.filter_by(name=DeckManager.DEFAULT_DECK_NAME).first()
            if not default_deck:
                default_deck = Deck(name=DeckManager.DEFAULT_DECK_NAME)
                db.session.add(default_deck)
                db.session.commit()
            deck_id = default_deck.id
        
        deck = Deck.query.get(deck_id)
        if not deck:
            raise ValueError(f"Deck {deck_id} not found")
        
        created_count = 0
        for card_data in cards_data:
            card = Card(
                deck_id=deck_id,
                front=card_data['front'],
                back=card_data['back'],
                card_type=card_data.get('card_type', 'flashcard'),
                category=card_data.get('category', 'default'),
            )
            db.session.add(card)
            created_count += 1
        
        db.session.commit()
        
        return {
            'created_count': created_count,
            'deck_id': deck_id,
        }
