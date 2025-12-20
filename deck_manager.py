"""
Deck management system.

Handles:
- Creating and deleting decks
- Adding/removing cards from decks
- Deck statistics and analytics
- Default deck management
"""

from datetime import datetime, timedelta
from typing import Dict, List

from models import db, Deck, Card, CardSRSState, ReviewLog


class DeckManager:
    """Manages decks and their cards."""
    
    DEFAULT_DECK_NAME = 'All'
    
    def __init__(self):
        self._ensure_default_deck()
    
    def _ensure_default_deck(self):
        """Create default 'All' deck if it doesn't exist."""
        default = Deck.query.filter_by(name=self.DEFAULT_DECK_NAME).first()
        if not default:
            default = Deck(name=self.DEFAULT_DECK_NAME, description='Default deck for all cards')
            db.session.add(default)
            db.session.commit()
    
    def create_deck(self, name: str, description: str = '') -> Dict:
        """
        Create a new deck.
        
        Args:
            name: Deck name
            description: Optional description
            
        Returns:
            Deck dictionary
            
        Raises:
            ValueError: If deck name already exists
        """
        existing = Deck.query.filter_by(name=name).first()
        if existing:
            raise ValueError(f"Deck '{name}' already exists")
        
        deck = Deck(name=name, description=description)
        db.session.add(deck)
        db.session.commit()
        
        return deck.to_dict()
    
    def delete_deck(self, deck_id: int, move_cards_to_default: bool = True) -> Dict:
        """
        Delete a deck.
        
        Args:
            deck_id: Deck ID
            move_cards_to_default: If True, move cards to default deck. If False, delete cards.
            
        Returns:
            Result dictionary
            
        Raises:
            ValueError: If deck not found or is default deck
        """
        deck = Deck.query.get(deck_id)
        if not deck:
            raise ValueError(f"Deck {deck_id} not found")
        
        if deck.name == self.DEFAULT_DECK_NAME:
            raise ValueError("Cannot delete the default deck")
        
        card_count = len(deck.cards)
        
        if move_cards_to_default:
            default_deck = Deck.query.filter_by(name=self.DEFAULT_DECK_NAME).first()
            for card in deck.cards:
                card.deck_id = default_deck.id
        
        db.session.delete(deck)
        db.session.commit()
        
        return {
            'deck_id': deck_id,
            'action': 'deleted',
            'cards_moved': card_count if move_cards_to_default else 0,
            'cards_deleted': 0 if move_cards_to_default else card_count,
        }
    
    def get_deck(self, deck_id: int) -> Dict:
        """
        Get deck by ID.
        
        Args:
            deck_id: Deck ID
            
        Returns:
            Deck dictionary
            
        Raises:
            ValueError: If deck not found
        """
        deck = Deck.query.get(deck_id)
        if not deck:
            raise ValueError(f"Deck {deck_id} not found")
        
        return deck.to_dict()
    
    def get_all_decks(self) -> List[Dict]:
        """
        Get all decks with statistics.
        
        Returns:
            List of deck dictionaries with stats
        """
        decks = Deck.query.all()
        
        result = []
        for deck in decks:
            stats = self.get_deck_stats(deck.id)
            deck_data = deck.to_dict()
            deck_data['stats'] = stats
            result.append(deck_data)
        
        return result
    
    def get_deck_stats(self, deck_id: int) -> Dict:
        """
        Get statistics for a deck.
        
        Args:
            deck_id: Deck ID
            
        Returns:
            Stats dictionary with:
                - total_cards: Total cards in deck
                - new_cards: Cards never reviewed
                - due_cards: Cards due today
                - reviewed_today: Cards reviewed today
                - suspended_cards: Suspended cards
                - leech_cards: Leech cards
                - average_difficulty: Average difficulty
                - average_stability: Average stability
        """
        deck = Deck.query.get(deck_id)
        if not deck:
            raise ValueError(f"Deck {deck_id} not found")
        
        cards = deck.cards
        
        if not cards:
            return {
                'total_cards': 0,
                'new_cards': 0,
                'due_cards': 0,
                'reviewed_today': 0,
                'suspended_cards': 0,
                'leech_cards': 0,
                'average_difficulty': 0,
                'average_stability': 0,
            }
        
        now = datetime.utcnow()
        today_start = datetime(now.year, now.month, now.day)
        
        new_count = 0
        due_count = 0
        reviewed_today_count = 0
        suspended_count = 0
        leech_count = 0
        difficulties = []
        stabilities = []
        
        for card in cards:
            srs_state = card.srs_state
            if not srs_state:
                new_count += 1
                continue
            
            if srs_state.suspended:
                suspended_count += 1
                continue
            
            if srs_state.is_leech:
                leech_count += 1
            
            if srs_state.reviews_count == 0:
                new_count += 1
            
            if srs_state.due_date <= now:
                due_count += 1
            
            # Check if reviewed today
            if srs_state.last_review_at and srs_state.last_review_at >= today_start:
                reviewed_today_count += 1
            
            difficulties.append(srs_state.difficulty)
            stabilities.append(srs_state.stability)
        
        avg_difficulty = sum(difficulties) / len(difficulties) if difficulties else 0
        avg_stability = sum(stabilities) / len(stabilities) if stabilities else 0
        
        return {
            'total_cards': len(cards),
            'new_cards': new_count,
            'due_cards': due_count,
            'reviewed_today': reviewed_today_count,
            'suspended_cards': suspended_count,
            'leech_cards': leech_count,
            'average_difficulty': round(avg_difficulty, 2),
            'average_stability': round(avg_stability, 2),
        }
    
    def add_card_to_deck(self, card_id: int, deck_id: int) -> Dict:
        """
        Add card to a deck.
        
        Args:
            card_id: Card ID
            deck_id: Deck ID
            
        Returns:
            Result dictionary
            
        Raises:
            ValueError: If card or deck not found
        """
        card = Card.query.get(card_id)
        if not card:
            raise ValueError(f"Card {card_id} not found")
        
        deck = Deck.query.get(deck_id)
        if not deck:
            raise ValueError(f"Deck {deck_id} not found")
        
        card.deck_id = deck_id
        db.session.commit()
        
        return {
            'card_id': card_id,
            'deck_id': deck_id,
            'action': 'moved',
        }
    
    def get_deck_by_name(self, name: str) -> Dict:
        """
        Get deck by name.
        
        Args:
            name: Deck name
            
        Returns:
            Deck dictionary
            
        Raises:
            ValueError: If deck not found
        """
        deck = Deck.query.filter_by(name=name).first()
        if not deck:
            raise ValueError(f"Deck '{name}' not found")
        
        return deck.to_dict()
    
    def rename_deck(self, deck_id: int, new_name: str) -> Dict:
        """
        Rename a deck.
        
        Args:
            deck_id: Deck ID
            new_name: New name
            
        Returns:
            Updated deck dictionary
            
        Raises:
            ValueError: If deck not found or new name already exists
        """
        deck = Deck.query.get(deck_id)
        if not deck:
            raise ValueError(f"Deck {deck_id} not found")
        
        existing = Deck.query.filter_by(name=new_name).first()
        if existing and existing.id != deck_id:
            raise ValueError(f"Deck '{new_name}' already exists")
        
        deck.name = new_name
        db.session.commit()
        
        return deck.to_dict()
