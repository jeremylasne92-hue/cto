"""
FSRS-5 SRS Engine - Core Scheduling and Session Management
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

from database import SRSDatabase, Card, CardSRSState, ReviewLog
from fsrs_algorithm import FSRS5Algorithm, FSRSState, FSRSOptimizer, ReviewResult

class SRSEngine:
    """
    Main SRS Engine that coordinates database operations with FSRS-5 algorithm
    """
    
    def __init__(self, db_path: str = "srs_engine.db"):
        self.db = SRSDatabase(db_path)
        self.fsrs = FSRS5Algorithm()
        self.optimizer = FSRSOptimizer()
        self.current_session = None
        self.session_start_time = None
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    # ====================
    # Deck Management
    # ====================
    
    def create_deck(self, name: str, description: str = "") -> Dict[str, Any]:
        """Create a new deck"""
        deck_id = self.db.create_deck(name, description)
        return {"deck_id": deck_id, "name": name, "description": description}
    
    def get_decks(self) -> List[Dict[str, Any]]:
        """Get all decks with statistics"""
        return self.db.get_decks()
    
    # ====================
    # Card Management
    # ====================
    
    def create_card(self, deck_id: str, front: str, back: str, 
                   card_type: str = "flashcard") -> Dict[str, Any]:
        """Create a new card with initial SRS state"""
        card_id = self.db.create_card(deck_id, front, back, card_type)
        
        # Initialize FSRS state
        fsrs_state = self.fsrs.initialize_new_card()
        
        # Get initial SRS state from database
        card_state = self.db.get_card_srs_state(card_id)
        
        return {
            "card_id": card_id,
            "deck_id": deck_id,
            "front": front,
            "back": back,
            "card_type": card_type,
            "difficulty": fsrs_state.difficulty,
            "stability": fsrs_state.stability,
            "retrievability": fsrs_state.retrievability,
            "due_date": card_state.due_date.isoformat() if card_state.due_date else None
        }
    
    def get_cards(self, deck_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get cards from a deck"""
        cards = self.db.get_cards(deck_id)
        result = []
        
        for card in cards:
            state = self.db.get_card_srs_state(card.id)
            card_dict = {
                "card_id": card.id,
                "deck_id": card.deck_id,
                "front": card.front,
                "back": card.back,
                "card_type": card.card_type,
                "created_at": card.created_at.isoformat(),
                "difficulty": state.difficulty if state else 5.0,
                "stability": state.stability if state else 1.0,
                "retrievability": state.retrievability if state else 1.0,
                "due_date": state.due_date.isoformat() if state and state.due_date else None,
                "reviews_count": state.reviews_count if state else 0,
                "lapses": state.lapses if state else 0,
                "is_leech": state.is_leech if state else False
            }
            result.append(card_dict)
        
        return result
    
    # ====================
    # Review Session Management
    # ====================
    
    def start_review_session(self, deck_id: Optional[str] = None) -> Dict[str, Any]:
        """Start a new review session"""
        # Create session
        session_id = self.db.create_review_session(deck_id or "all")
        self.current_session = session_id
        self.session_start_time = datetime.now()
        
        # Get due cards
        due_cards = self.get_due_cards(deck_id)
        
        # Optimize review order
        optimized_cards = self.optimizer.optimize_review_order(due_cards)
        
        # Add overdue prioritization
        overdue_cards = self.db.get_overdue_cards()
        
        # Calculate session statistics
        session_stats = self.optimizer.estimate_session_duration(optimized_cards)
        
        self.logger.info(f"Started review session {session_id} with {len(optimized_cards)} cards")
        
        return {
            "session_id": session_id,
            "deck_id": deck_id,
            "due_cards_count": len(optimized_cards),
            "overdue_cards_count": len(overdue_cards),
            "estimated_duration": session_stats["estimated_duration"],
            "cards": optimized_cards,
            "session_optimizer": {
                "warmup_medium": session_stats["card_breakdown"].get("medium", 0),
                "main_hard": session_stats["card_breakdown"].get("hard", 0) + 
                           session_stats["card_breakdown"].get("very_hard", 0),
                "cooldown_easy": session_stats["card_breakdown"].get("easy", 0)
            }
        }
    
    def get_due_cards(self, deck_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get cards due for review, optimized for learning"""
        due_cards = self.db.get_due_cards(deck_id)
        
        # Convert datetime objects to ISO format for JSON serialization
        for card in due_cards:
            if card.get('due_date'):
                if hasattr(card['due_date'], 'isoformat'):
                    card['due_date'] = card['due_date'].isoformat()
                # else: it's already a string
        
        return due_cards
    
    def end_review_session(self) -> Dict[str, Any]:
        """End the current review session"""
        if not self.current_session:
            return {"error": "No active session"}
        
        # Get session duration
        session_duration = (datetime.now() - self.session_start_time).total_seconds()
        
        # End session in database (we'll update cards_reviewed when we process reviews)
        # For now, we'll just reset session state
        session_info = {
            "session_id": self.current_session,
            "duration_seconds": session_duration,
            "ended_at": datetime.now().isoformat()
        }
        
        self.current_session = None
        self.session_start_time = None
        
        self.logger.info(f"Ended review session after {session_duration:.1f} seconds")
        
        return session_info
    
    # ====================
    # Card Review Processing
    # ====================
    
    def review_card(self, card_id: str, grade: int, 
                   review_duration: float = 0.0) -> Dict[str, Any]:
        """
        Process a card review using FSRS-5 algorithm
        
        Args:
            card_id: ID of the card being reviewed
            grade: Review grade (1=Again, 2=Hard, 3=Good, 4=Easy)
            review_duration: Time taken for review in seconds
            
        Returns:
            Updated card state and next review information
        """
        if not (1 <= grade <= 4):
            raise ValueError("Grade must be between 1 and 4")
        
        # Get current state
        current_state = self.db.get_card_srs_state(card_id)
        if not current_state:
            raise ValueError(f"Card {card_id} not found or no SRS state")
        
        # Convert to FSRS state
        fsrs_state = FSRSState(
            difficulty=current_state.difficulty,
            stability=current_state.stability,
            retrievability=current_state.retrievability
        )
        
        # Process review with FSRS-5
        review_result = self.fsrs.review_card(
            fsrs_state, grade, review_duration, current_state.reviews_count
        )
        
        # Calculate next due date
        next_due_date = datetime.now() + timedelta(days=review_result.next_interval)
        
        # Check for leech detection
        new_lapses = current_state.lapses + (1 if grade == 1 else 0)
        is_leech = self.fsrs.is_leech(review_result.new_difficulty, new_lapses)
        
        # Update database
        self.db.update_srs_state(
            card_id=card_id,
            difficulty=review_result.new_difficulty,
            stability=review_result.new_stability,
            retrievability=review_result.new_retrievability,
            due_date=next_due_date,
            reviews_count=current_state.reviews_count + 1,
            lapses=new_lapses,
            is_leech=is_leech
        )
        
        # Log review
        review_log = ReviewLog(
            id=str(uuid.uuid4()),
            card_id=card_id,
            grade=grade,
            review_duration=review_duration,
            timestamp=datetime.now(),
            session_id=self.current_session or "no-session",
            old_difficulty=current_state.difficulty,
            new_difficulty=review_result.new_difficulty,
            old_stability=current_state.stability,
            new_stability=review_result.new_stability,
            old_retrievability=current_state.retrievability,
            new_retrievability=review_result.new_retrievability,
            interval=review_result.next_interval
        )
        self.db.log_review(review_log)
        
        # Prepare response
        response = {
            "card_id": card_id,
            "session_id": self.current_session,
            "grade": grade,
            "review_duration": review_duration,
            "old_state": {
                "difficulty": current_state.difficulty,
                "stability": current_state.stability,
                "retrievability": current_state.retrievability
            },
            "new_state": {
                "difficulty": review_result.new_difficulty,
                "stability": review_result.new_stability,
                "retrievability": review_result.new_retrievability
            },
            "next_review": {
                "interval_days": review_result.next_interval,
                "due_date": next_due_date.isoformat()
            },
            "is_leech": is_leech,
            "should_flag": is_leech and (current_state.lapses >= 2)
        }
        
        self.logger.info(f"Reviewed card {card_id} with grade {grade}, "
                        f"next review in {review_result.next_interval:.1f} days")
        
        return response
    
    def skip_card_review(self, card_id: str, reason: str = "skipped") -> Dict[str, Any]:
        """Mark a card as reviewed without grading (useful for time constraints)"""
        # Get current state
        current_state = self.db.get_card_srs_state(card_id)
        if not current_state:
            raise ValueError(f"Card {card_id} not found")
        
        # Log as a special "skipped" review
        review_log = ReviewLog(
            id=str(uuid.uuid4()),
            card_id=card_id,
            grade=0,  # Special grade for skipped
            review_duration=0.0,
            timestamp=datetime.now(),
            session_id=self.current_session or "no-session",
            old_difficulty=current_state.difficulty,
            new_difficulty=current_state.difficulty,
            old_stability=current_state.stability,
            new_stability=current_state.stability,
            old_retrievability=current_state.retrievability,
            new_retrievability=current_state.retrievability,
            interval=0.0
        )
        self.db.log_review(review_log)
        
        return {
            "card_id": card_id,
            "status": "skipped",
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
    
    # ====================
    # Statistics and Analytics
    # ====================
    
    def get_deck_statistics(self, deck_id: str) -> Dict[str, Any]:
        """Get comprehensive statistics for a deck"""
        return self.db.get_deck_statistics(deck_id)
    
    def get_leech_cards(self) -> List[Dict[str, Any]]:
        """Get all leech cards that need manual attention"""
        import sqlite3
        with sqlite3.connect(self.db.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT c.id, c.front, c.back, c.card_type, c.deck_id,
                       s.difficulty, s.stability, s.retrievability, s.due_date,
                       s.reviews_count, s.lapses, s.is_leech, d.name as deck_name
                FROM cards c
                JOIN card_srs_state s ON c.id = s.card_id
                JOIN decks d ON c.deck_id = d.id
                WHERE s.is_leech = 1
                ORDER BY s.lapses DESC, s.difficulty DESC
            ''')
            
            leech_cards = [dict(row) for row in cursor.fetchall()]
            
            # Convert datetime objects
            for card in leech_cards:
                if card.get('due_date'):
                    card['due_date'] = card['due_date'].isoformat()
            
            return leech_cards
    
    def get_review_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get review analytics for the specified period"""
        import sqlite3
        with sqlite3.connect(self.db.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Review frequency over time
            cursor.execute('''
                SELECT date(timestamp) as review_date,
                       COUNT(*) as reviews,
                       AVG(grade) as avg_grade,
                       AVG(review_duration) as avg_duration
                FROM review_logs
                WHERE timestamp >= date('now', '-{} days')
                GROUP BY date(timestamp)
                ORDER BY review_date
            '''.format(days))
            
            daily_reviews = [dict(row) for row in cursor.fetchall()]
            
            # Grade distribution
            cursor.execute('''
                SELECT grade, COUNT(*) as count
                FROM review_logs
                WHERE timestamp >= date('now', '-{} days') AND grade > 0
                GROUP BY grade
                ORDER BY grade
            '''.format(days))
            
            grade_distribution = [dict(row) for row in cursor.fetchall()]
            
            return {
                "period_days": days,
                "daily_reviews": daily_reviews,
                "grade_distribution": grade_distribution,
                "total_reviews": sum(r['reviews'] for r in daily_reviews)
            }
    
    # ====================
    # Import/Export
    # ====================
    
    def export_deck_data(self, deck_id: str) -> Dict[str, Any]:
        """Export deck data including SRS state for backup/sync"""
        cards = self.get_cards(deck_id)
        deck_stats = self.get_deck_statistics(deck_id)
        
        return {
            "deck_id": deck_id,
            "exported_at": datetime.now().isoformat(),
            "cards_count": len(cards),
            "cards": cards,
            "statistics": deck_stats
        }
    
    def import_deck_data(self, deck_data: Dict[str, Any]) -> Dict[str, Any]:
        """Import deck data from backup/sync"""
        imported_cards = 0
        
        # Create or get deck
        deck_name = deck_data.get("name", f"Imported Deck {datetime.now().strftime('%Y-%m-%d')}")
        deck_id = self.create_deck(deck_name)["deck_id"]
        
        # Import cards
        for card_data in deck_data.get("cards", []):
            card = self.create_card(
                deck_id=deck_id,
                front=card_data["front"],
                back=card_data["back"],
                card_type=card_data.get("card_type", "flashcard")
            )
            imported_cards += 1
        
        return {
            "deck_id": deck_id,
            "imported_cards": imported_cards,
            "status": "success"
        }