"""
Review management system.

Handles:
- Recording review grades
- Updating SRS state using FSRS-5 algorithm
- Detecting leeches
- Logging reviews for sync
"""

from datetime import datetime, timedelta
from uuid import uuid4
from typing import Dict, Tuple

from models import db, Card, CardSRSState, ReviewLog, SessionState
from fsrs5_algorithm import FSRS5
import config


class ReviewManager:
    """Manages card reviews and SRS state updates."""
    
    GRADE_NAMES = {
        1: 'Again',
        2: 'Hard',
        3: 'Good',
        4: 'Easy',
    }
    
    def __init__(self):
        self.fsrs = FSRS5()
        self.target_retention = config.TARGET_RETENTION
        self.leech_threshold = config.LEECH_THRESHOLD_LAPSES
    
    def submit_review(self,
                     card_id: int,
                     grade: int,
                     duration_seconds: int = 0,
                     session_id: str = None) -> Dict:
        """
        Submit a review for a card and update its SRS state.
        
        Args:
            card_id: ID of the card being reviewed
            grade: Grade (1-4): 1=Again, 2=Hard, 3=Good, 4=Easy
            duration_seconds: Time spent reviewing this card
            session_id: Session ID for grouping reviews
            
        Returns:
            Dictionary with review result and updated state
            
        Raises:
            ValueError: If grade is invalid or card not found
        """
        if grade < 1 or grade > 4:
            raise ValueError(f"Grade must be 1-4, got {grade}")
        
        card = Card.query.get(card_id)
        if not card:
            raise ValueError(f"Card {card_id} not found")
        
        srs_state = card.srs_state
        if not srs_state:
            # Initialize SRS state if not present
            srs_state = self._init_srs_state(card, grade)
        
        # Calculate elapsed time since last review
        now = datetime.utcnow()
        last_review = srs_state.last_review_at or card.created_at
        elapsed_days = (now - last_review).total_seconds() / (24 * 3600)
        
        # Store state before review
        state_before = {
            'difficulty': srs_state.difficulty,
            'stability': srs_state.stability,
            'retrievability': srs_state.retrievability,
        }
        
        # Update SRS state based on FSRS-5 algorithm
        new_difficulty, new_stability, new_retrievability = self.fsrs.review(
            grade=grade,
            difficulty=srs_state.difficulty,
            stability=srs_state.stability,
            retrievability=srs_state.retrievability,
            elapsed_days=elapsed_days,
        )
        
        # Update card state
        srs_state.difficulty = new_difficulty
        srs_state.stability = new_stability
        srs_state.retrievability = new_retrievability
        srs_state.reviews_count += 1
        srs_state.last_review_at = now
        
        # Track lapses (missed reviews)
        if grade == 1:  # Wrong answer
            srs_state.lapses += 1
        
        # Update due date
        srs_state.due_date = self.fsrs.calculate_due_date(
            now, new_stability, self.target_retention
        )
        
        # Check for leeches
        if srs_state.lapses > self.leech_threshold:
            srs_state.is_leech = True
        
        # Create review log
        review_log = ReviewLog(
            card_id=card_id,
            grade=grade,
            review_duration=duration_seconds,
            timestamp=now,
            session_id=session_id,
            difficulty_before=state_before['difficulty'],
            stability_before=state_before['stability'],
            retrievability_before=state_before['retrievability'],
            difficulty_after=new_difficulty,
            stability_after=new_stability,
            retrievability_after=new_retrievability,
        )
        
        # Save to database
        db.session.add(review_log)
        db.session.commit()
        
        return {
            'card_id': card_id,
            'grade': grade,
            'grade_name': self.GRADE_NAMES[grade],
            'state_before': state_before,
            'state_after': {
                'difficulty': round(new_difficulty, 2),
                'stability': round(new_stability, 2),
                'retrievability': round(new_retrievability, 4),
            },
            'due_date': srs_state.due_date.isoformat(),
            'is_leech': srs_state.is_leech,
            'reviews_count': srs_state.reviews_count,
            'lapses': srs_state.lapses,
        }
    
    def _init_srs_state(self, card: Card, initial_grade: int) -> CardSRSState:
        """
        Initialize SRS state for a new card.
        
        Args:
            card: Card object
            initial_grade: Initial grade (1-4)
            
        Returns:
            New CardSRSState object
        """
        now = datetime.utcnow()
        
        # Initialize difficulty and stability based on first grade
        difficulty = self._init_difficulty(initial_grade)
        stability = self._init_stability(initial_grade)
        
        # First review has full retrievability
        retrievability = 1.0
        
        # Calculate initial due date
        due_date = self.fsrs.calculate_due_date(now, stability, self.target_retention)
        
        srs_state = CardSRSState(
            card_id=card.id,
            difficulty=difficulty,
            stability=stability,
            retrievability=retrievability,
            due_date=due_date,
            reviews_count=1,
            lapses=0 if initial_grade != 1 else 1,
            last_review_at=now,
        )
        
        db.session.add(srs_state)
        db.session.commit()
        
        return srs_state
    
    def _init_difficulty(self, grade: int) -> float:
        """Initialize difficulty for new card based on first grade."""
        if grade == 1:
            return 5.0  # Medium
        elif grade == 2:
            return 4.0  # Slightly easy
        elif grade == 3:
            return 5.0  # Medium
        elif grade == 4:
            return 3.0  # Easy
        return 5.0
    
    def _init_stability(self, grade: int) -> float:
        """Initialize stability for new card based on first grade."""
        if grade == 1:
            return 0.5  # Very short interval
        elif grade == 2:
            return 2.0  # 2 days
        elif grade == 3:
            return 4.0  # 4 days
        elif grade == 4:
            return 7.0  # 7 days
        return 4.0
    
    def skip_review(self, card_id: int, session_id: str = None) -> Dict:
        """
        Skip a card without grading it.
        
        Marks as reviewed without changing SRS state.
        
        Args:
            card_id: ID of the card
            session_id: Session ID
            
        Returns:
            Result dictionary
        """
        card = Card.query.get(card_id)
        if not card:
            raise ValueError(f"Card {card_id} not found")
        
        # Create log entry but don't update SRS state
        review_log = ReviewLog(
            card_id=card_id,
            grade=0,  # 0 means skipped
            review_duration=0,
            timestamp=datetime.utcnow(),
            session_id=session_id,
        )
        
        db.session.add(review_log)
        db.session.commit()
        
        return {
            'card_id': card_id,
            'action': 'skipped',
        }
    
    def get_review_history(self, card_id: int, limit: int = 10) -> list:
        """
        Get review history for a card.
        
        Args:
            card_id: Card ID
            limit: Max number of reviews to return
            
        Returns:
            List of review log dictionaries
        """
        reviews = ReviewLog.query.filter_by(card_id=card_id).order_by(
            ReviewLog.timestamp.desc()
        ).limit(limit).all()
        
        return [r.to_dict() for r in reviews]
    
    def get_session_stats(self, session_id: str) -> Dict:
        """
        Get statistics for a review session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Stats dictionary
        """
        reviews = ReviewLog.query.filter_by(session_id=session_id).all()
        
        if not reviews:
            return {
                'session_id': session_id,
                'card_count': 0,
                'total_duration': 0,
                'grades': {},
            }
        
        grades = {1: 0, 2: 0, 3: 0, 4: 0}
        total_duration = 0
        
        for review in reviews:
            if review.grade > 0:
                grades[review.grade] = grades.get(review.grade, 0) + 1
            total_duration += review.review_duration or 0
        
        return {
            'session_id': session_id,
            'card_count': len(reviews),
            'total_duration': total_duration,
            'grades': {
                'again': grades[1],
                'hard': grades[2],
                'good': grades[3],
                'easy': grades[4],
            },
            'accuracy': sum(grades[g] for g in [2, 3, 4]) / len([r for r in reviews if r.grade > 0]) if any(r.grade > 0 for r in reviews) else 0,
        }
    
    def create_session(self, deck_id: int = None) -> str:
        """
        Create a new review session.
        
        Args:
            deck_id: Optional deck ID
            
        Returns:
            Session ID
        """
        session_id = str(uuid4())
        session = SessionState(
            id=session_id,
            deck_id=deck_id,
        )
        db.session.add(session)
        db.session.commit()
        return session_id
    
    def end_session(self, session_id: str, total_duration: int = 0) -> Dict:
        """
        End a review session.
        
        Args:
            session_id: Session ID
            total_duration: Total session duration in seconds
            
        Returns:
            Session stats
        """
        session = SessionState.query.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        session.ended_at = datetime.utcnow()
        session.total_duration = total_duration
        
        # Count reviews in session
        reviews = ReviewLog.query.filter_by(session_id=session_id).all()
        session.cards_reviewed = len(reviews)
        
        db.session.commit()
        
        return session.to_dict()
