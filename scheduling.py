"""
Scheduling system for organizing review sessions.

Features:
- Session optimizer: Reorder cards for optimal learning
- Warmup: Medium difficulty first
- Main: Hard cards in middle
- Cool-down: Easy cards at end
- Overdue prioritization: Old reviews before new
- Interleaving: Mix related concepts
- Leech detection: Cards with >2 lapses flagged
"""

from datetime import datetime, timedelta
from typing import List, Tuple
from models import Card, CardSRSState
import config


class SessionScheduler:
    """Optimizes review session order for better learning outcomes."""
    
    def __init__(self):
        self.warmup_diff_range = config.WARMUP_DIFFICULTY_RANGE
        self.main_diff_min = config.MAIN_DIFFICULTY_MIN
        self.cooldown_diff_max = config.COOLDOWN_DIFFICULTY_MAX
        self.leech_threshold = config.LEECH_THRESHOLD_LAPSES
    
    def get_due_cards(self, deck_id: int = None) -> List[Card]:
        """
        Get all cards that are due for review today.
        
        Args:
            deck_id: Optional deck to filter by. If None, returns cards from all decks.
            
        Returns:
            List of Card objects that are due
        """
        now = datetime.utcnow()
        
        query = Card.query.join(CardSRSState).filter(
            CardSRSState.due_date <= now,
            CardSRSState.suspended == False
        )
        
        if deck_id:
            query = query.filter(Card.deck_id == deck_id)
        
        return query.all()
    
    def categorize_cards(self, cards: List[Card]) -> Tuple[List[Card], List[Card], List[Card], List[Card]]:
        """
        Categorize cards into warmup, main, and cooldown groups.
        
        Args:
            cards: List of Card objects to categorize
            
        Returns:
            Tuple of (warmup_cards, main_cards, cooldown_cards, leeches)
        """
        warmup = []
        main = []
        cooldown = []
        leeches = []
        
        for card in cards:
            srs_state = card.srs_state
            if not srs_state:
                continue
            
            # Check for leeches first
            if srs_state.lapses > self.leech_threshold:
                leeches.append(card)
                continue
            
            difficulty = srs_state.difficulty
            
            # Categorize by difficulty
            if self.warmup_diff_range[0] <= difficulty <= self.warmup_diff_range[1]:
                warmup.append(card)
            elif difficulty >= self.main_diff_min:
                main.append(card)
            elif difficulty <= self.cooldown_diff_max:
                cooldown.append(card)
            else:
                # Medium-high difficulty cards go to main
                main.append(card)
        
        return warmup, main, cooldown, leeches
    
    def prioritize_overdue(self, cards: List[Card]) -> List[Card]:
        """
        Sort cards by how overdue they are (oldest first).
        
        Args:
            cards: List of Card objects
            
        Returns:
            Sorted list (most overdue first)
        """
        return sorted(cards, key=lambda c: c.srs_state.due_date if c.srs_state else datetime.utcnow())
    
    def interleave_cards(self, cards: List[Card], max_same_category: int = 3) -> List[Card]:
        """
        Interleave cards by category to mix related concepts.
        
        Args:
            cards: List of Card objects
            max_same_category: Max consecutive cards from same category
            
        Returns:
            Interleaved list of cards
        """
        if len(cards) <= max_same_category:
            return cards
        
        # Group by category
        by_category = {}
        for card in cards:
            cat = card.category or 'default'
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(card)
        
        # Interleave
        result = []
        category_indices = {cat: 0 for cat in by_category}
        category_list = list(by_category.keys())
        category_idx = 0
        
        while len(result) < len(cards):
            # Try to pick from next category
            attempts = 0
            while attempts < len(category_list):
                current_category = category_list[category_idx % len(category_list)]
                
                if category_indices[current_category] < len(by_category[current_category]):
                    result.append(by_category[current_category][category_indices[current_category]])
                    category_indices[current_category] += 1
                    category_idx += 1
                    break
                
                category_idx += 1
                attempts += 1
        
        return result
    
    def build_session_order(self, cards: List[Card], use_warmup_cooldown: bool = True) -> List[Card]:
        """
        Build optimal session order with warmup, main, and cooldown sections.
        
        Algorithm:
        1. Separate cards into warmup, main, cooldown
        2. Prioritize by overdue status
        3. Interleave by category
        4. Combine: warmup -> main -> cooldown
        
        Args:
            cards: List of Card objects
            use_warmup_cooldown: Whether to use warmup/cooldown sections
            
        Returns:
            Ordered list of cards for review
        """
        if not cards:
            return []
        
        warmup, main, cooldown, leeches = self.categorize_cards(cards)
        
        # Prioritize by overdue
        warmup = self.prioritize_overdue(warmup)
        main = self.prioritize_overdue(main)
        cooldown = self.prioritize_overdue(cooldown)
        leeches = self.prioritize_overdue(leeches)
        
        # Interleave by category
        warmup = self.interleave_cards(warmup)
        main = self.interleave_cards(main)
        cooldown = self.interleave_cards(cooldown)
        
        # Combine sections
        if use_warmup_cooldown:
            result = warmup + main + cooldown
        else:
            # If not using warmup/cooldown, just use main order
            result = main + warmup + cooldown
        
        # Add leeches at end for manual review
        if leeches:
            result.extend(leeches)
        
        return result
    
    def estimate_session_duration(self, cards: List[Card], avg_duration_seconds: int = 30) -> int:
        """
        Estimate session duration based on card count.
        
        Args:
            cards: List of Card objects
            avg_duration_seconds: Average seconds per card (default 30)
            
        Returns:
            Estimated duration in seconds
        """
        return len(cards) * avg_duration_seconds
    
    def select_session_cards(self, cards: List[Card], target_count: int = 20) -> Tuple[List[Card], List[Card]]:
        """
        Select a subset of cards for today's session.
        
        Prioritizes due cards, then newer cards.
        
        Args:
            cards: List of Card objects
            target_count: Target number of cards for session (default 20)
            
        Returns:
            Tuple of (selected_cards, remaining_cards)
        """
        if len(cards) <= target_count:
            return cards, []
        
        # Order cards
        ordered = self.build_session_order(cards)
        
        # Split
        selected = ordered[:target_count]
        remaining = ordered[target_count:]
        
        return selected, remaining


class CardSelector:
    """Utilities for selecting and filtering cards."""
    
    @staticmethod
    def get_leeches(cards: List[Card], threshold: int = 2) -> List[Card]:
        """
        Get leech cards (cards with many lapses).
        
        Args:
            cards: List of Card objects
            threshold: Number of lapses to flag as leech
            
        Returns:
            List of leech cards
        """
        return [
            c for c in cards
            if c.srs_state and c.srs_state.lapses > threshold
        ]
    
    @staticmethod
    def get_new_cards(cards: List[Card]) -> List[Card]:
        """
        Get cards that have never been reviewed.
        
        Args:
            cards: List of Card objects
            
        Returns:
            List of new cards
        """
        return [
            c for c in cards
            if c.srs_state and c.srs_state.reviews_count == 0
        ]
    
    @staticmethod
    def get_suspended_cards(cards: List[Card]) -> List[Card]:
        """
        Get suspended cards.
        
        Args:
            cards: List of Card objects
            
        Returns:
            List of suspended cards
        """
        return [
            c for c in cards
            if c.srs_state and c.srs_state.suspended
        ]
    
    @staticmethod
    def filter_by_difficulty_range(cards: List[Card], min_diff: float, max_diff: float) -> List[Card]:
        """
        Filter cards by difficulty range.
        
        Args:
            cards: List of Card objects
            min_diff: Minimum difficulty
            max_diff: Maximum difficulty
            
        Returns:
            Filtered list
        """
        return [
            c for c in cards
            if c.srs_state and min_diff <= c.srs_state.difficulty <= max_diff
        ]
