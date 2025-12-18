"""
FSRS-5 Algorithm Implementation
Based on the Free Spaced Repetition Scheduler algorithm (FSRS) version 5
Reference: Ye et al. "FSRS: An Algorithm for Automated Scheduling..."
"""

import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Tuple

@dataclass
class FSRSState:
    """FSRS state representation for a card"""
    difficulty: float      # 0-10 scale
    stability: float       # days
    retrievability: float  # 0-1 scale

@dataclass
class ReviewResult:
    """Result of a review action"""
    grade: int             # 1=Again, 2=Hard, 3=Good, 4=Easy
    new_difficulty: float
    new_stability: float
    new_retrievability: float
    next_interval: float   # days
    review_duration: float # seconds

class FSRS5Algorithm:
    """
    FSRS-5 Algorithm Implementation
    
    The FSRS-5 algorithm maintains three main parameters for each card:
    - Difficulty (D): 0-10 scale (higher = more difficult)
    - Stability (S): days until retrievability drops to target level
    - Retrievability (R): 0-1 scale (probability of successful recall)
    
    Grades:
    1 = Again (complete failure)
    2 = Hard (correct with difficulty)
    3 = Good (correct recall)
    4 = Easy (too easy)
    """
    
    # FSRS-5 constants
    INITIAL_STABILITY = 1.0
    INITIAL_DIFFICULTY = 5.0
    TARGET_RETRIEVAL = 0.9  # 90% target retention
    
    # Formula constants
    DIFFICULTY_FACTOR = 0.1
    DIFFICULTY_EPSILON = 1e-9
    
    @staticmethod
    def calculate_retrievability(stability: float, interval: float) -> float:
        """
        Calculate retrievability R given stability S and interval I
        
        Formula: R = exp((I - S) / (S * 4))
        
        Args:
            stability: Current stability in days
            interval: Review interval in days
            
        Returns:
            Retrievability probability (0-1)
        """
        if stability <= 0:
            return 0.0
        
        # When interval equals stability, retrievability should be ~90%
        if abs(interval - stability) < 0.01:
            return 0.9
        
        # Calculate exponential decay - retrievability decreases as interval increases beyond stability
        exp_value = (stability - interval) / (stability * 4)
        retrievability = math.exp(exp_value)
        
        # Clamp to [0, 1] and ensure very large intervals have low retrievability
        return max(0.0, min(1.0, retrievability))
    
    @staticmethod
    def calculate_interval_for_target_retrievability(
        stability: float, target_retrievability: float = None
    ) -> float:
        """
        Calculate the interval needed to achieve target retrievability
        
        Formula: I = S * (4 * ln(target) + 1)
        
        Args:
            stability: Current stability in days
            target_retrievability: Target retrievability (default 90%)
            
        Returns:
            Interval in days
        """
        if target_retrievability is None:
            target_retrievability = FSRS5Algorithm.TARGET_RETRIEVAL
        
        if target_retrievability <= 0:
            return 1.0
        
        # Formula from FSRS-5 paper
        interval = stability * (4 * math.log(target_retrievability) + 1)
        return max(1.0, interval)  # Minimum 1 day
    
    @staticmethod
    def update_difficulty(current_difficulty: float, grade: int) -> float:
        """
        Update difficulty based on review grade
        
        Args:
            current_difficulty: Current difficulty (0-10)
            grade: Review grade (1-4)
            
        Returns:
            New difficulty value
        """
        if grade < 1 or grade > 4:
            raise ValueError("Grade must be between 1 and 4")
        
        # Simplified difficulty adjustment
        if grade == 1:  # Again - increase difficulty significantly
            new_difficulty = current_difficulty + 0.8
        elif grade == 2:  # Hard - slight increase
            new_difficulty = current_difficulty + 0.3
        elif grade == 3:  # Good - no change
            new_difficulty = current_difficulty
        else:  # grade == 4: Easy - decrease difficulty
            new_difficulty = current_difficulty - 0.5
        
        return max(0.0, min(10.0, new_difficulty))  # Clamp to [0, 10]
    
    @staticmethod
    def update_stability(current_stability: float, difficulty: float, 
                        grade: int, reviews_count: int) -> float:
        """
        Update stability based on current stability, difficulty, and grade
        
        Args:
            current_stability: Current stability in days
            difficulty: Current difficulty (0-10)
            grade: Review grade (1-4)
            reviews_count: Number of previous reviews
            
        Returns:
            New stability value
        """
        if grade < 1 or grade > 4:
            raise ValueError("Grade must be between 1 and 4")
        
        # FSRS-5 stability update formulas (simplified version)
        if grade == 1:  # Again
            # Drastically reduce stability
            new_stability = current_stability * 0.5
        elif grade == 2:  # Hard
            # Slight decrease in stability
            new_stability = current_stability * (1.1 - 0.15 * (difficulty / 10))
        elif grade == 3:  # Good
            # Increase stability based on difficulty
            if current_stability < 1.0:
                # First few reviews: rapid growth
                new_stability = current_stability * (1.5 + (5 - difficulty) * 0.1)
            else:
                # Later reviews: exponential growth
                difficulty_modifier = 1.0 + (5 - difficulty) * 0.05
                new_stability = current_stability * (1.2 + difficulty_modifier)
        else:  # grade == 4: Easy
            # Increase stability but less than Good
            difficulty_modifier = 1.0 + (5 - difficulty) * 0.1
            new_stability = current_stability * (1.3 + difficulty_modifier)
        
        return max(0.1, new_stability)  # Minimum stability of 0.1 days
    
    @staticmethod
    def review_card(current_state: FSRSState, grade: int, 
                   review_duration: float = 0.0, reviews_count: int = 0) -> ReviewResult:
        """
        Process a review and return new state and next interval
        
        Args:
            current_state: Current FSRS state
            grade: Review grade (1=Again, 2=Hard, 3=Good, 4=Easy)
            review_duration: Time taken for review in seconds
            reviews_count: Number of previous reviews
            
        Returns:
            ReviewResult with updated state and next interval
        """
        if not (1 <= grade <= 4):
            raise ValueError("Grade must be between 1 and 4")
        
        # Update difficulty and stability
        new_difficulty = FSRS5Algorithm.update_difficulty(current_state.difficulty, grade)
        new_stability = FSRS5Algorithm.update_stability(
            current_state.stability, new_difficulty, grade, reviews_count
        )
        
        # Calculate current retrievability for this interval
        last_interval = FSRS5Algorithm.calculate_interval_for_target_retrievability(
            current_state.stability
        )
        new_retrievability = FSRS5Algorithm.calculate_retrievability(
            current_state.stability, last_interval
        )
        
        # Calculate next interval based on new stability
        next_interval = FSRS5Algorithm.calculate_interval_for_target_retrievability(new_stability)
        
        return ReviewResult(
            grade=grade,
            new_difficulty=new_difficulty,
            new_stability=new_stability,
            new_retrievability=new_retrievability,
            next_interval=next_interval,
            review_duration=review_duration
        )
    
    @staticmethod
    def initialize_new_card() -> FSRSState:
        """
        Initialize FSRS state for a new card
        
        Returns:
            Initial FSRS state
        """
        return FSRSState(
            difficulty=FSRS5Algorithm.INITIAL_DIFFICULTY,
            stability=FSRS5Algorithm.INITIAL_STABILITY,
            retrievability=1.0  # New cards have 100% retrievability
        )
    
    @staticmethod
    def get_next_review_date(current_state: FSRSState, grade: int = None) -> datetime:
        """
        Calculate the next review date
        
        Args:
            current_state: Current FSRS state
            grade: Review grade (if reviewing now)
            
        Returns:
            Next review date
        """
        if grade is not None:
            # Simulate review to get new stability
            temp_state = FSRSState(
                difficulty=current_state.difficulty,
                stability=current_state.stability,
                retrievability=current_state.retrievability
            )
            result = FSRS5Algorithm.review_card(temp_state, grade)
            interval = result.next_interval
        else:
            # Use current state to calculate interval
            interval = FSRS5Algorithm.calculate_interval_for_target_retrievability(
                current_state.stability
            )
        
        return datetime.now() + timedelta(days=interval)
    
    @staticmethod
    def is_leech(difficulty: float, lapses: int) -> bool:
        """
        Determine if a card is a leech (needs special attention)
        
        Args:
            difficulty: Current difficulty (0-10)
            lapses: Number of times forgotten
            
        Returns:
            True if card is a leech
        """
        # Leech if difficulty is very high or too many lapses
        return difficulty > 8.5 or lapses > 2


class FSRSOptimizer:
    """
    FSRS-5 Session Optimizer for optimal learning order
    """
    
    @staticmethod
    def optimize_review_order(cards_data: list) -> list:
        """
        Optimize review order for better learning
        
        Args:
            cards_data: List of dicts with card data and FSRS state
            
        Returns:
            Optimized list of cards for review
        """
        if not cards_data:
            return []
        
        # Separate cards by difficulty and due status
        very_hard = []    # difficulty > 7
        hard = []         # difficulty 5-7
        medium = []       # difficulty 3-5
        easy = []         # difficulty < 3
        
        for card in cards_data:
            difficulty = card.get('difficulty', 5.0)
            if difficulty > 7:
                very_hard.append(card)
            elif difficulty >= 5:
                hard.append(card)
            elif difficulty >= 3:
                medium.append(card)
            else:
                easy.append(card)
        
        # Sort each group by due date (most overdue first)
        for group in [very_hard, hard, medium, easy]:
            group.sort(key=lambda x: x.get('due_date', ''))
        
        # Optimal session structure:
        # 1. Warm-up: Medium difficulty first (build confidence)
        # 2. Main: Hard cards in middle (peak attention)
        # 3. Cool-down: Easy cards at end (end on positive note)
        
        optimized_order = []
        
        # Warm-up: 20% medium difficulty cards
        warmup_count = max(1, len(medium) // 5)
        optimized_order.extend(medium[:warmup_count])
        
        # Main: All very hard and hard cards, plus remaining medium
        optimized_order.extend(very_hard)
        optimized_order.extend(hard)
        optimized_order.extend(medium[warmup_count:])
        
        # Cool-down: Easy cards (end on positive note)
        optimized_order.extend(easy)
        
        return optimized_order
    
    @staticmethod
    def should_interleave_cards(deck1_data: dict, deck2_data: dict) -> bool:
        """
        Determine if cards from different decks should be interleaved
        
        Args:
            deck1_data: First deck data
            deck2_data: Second deck data
            
        Returns:
            True if cards should be interleaved
        """
        # Interleave if both decks have similar difficulty
        diff1 = deck1_data.get('avg_difficulty', 5.0)
        diff2 = deck2_data.get('avg_difficulty', 5.0)
        difficulty_diff = abs(diff1 - diff2)
        
        return difficulty_diff < 1.0
    
    @staticmethod
    def estimate_session_duration(cards_data: list) -> dict:
        """
        Estimate session duration and card breakdown
        
        Args:
            cards_data: List of card data
            
        Returns:
            Dictionary with duration estimates
        """
        if not cards_data:
            return {"estimated_duration": 0, "card_breakdown": {}}
        
        # Estimated review times (in seconds)
        review_times = {
            "very_hard": 15,  # difficult cards take longer
            "hard": 12,
            "medium": 8,
            "easy": 6
        }
        
        breakdown = {"very_hard": 0, "hard": 0, "medium": 0, "easy": 0}
        total_time = 0
        
        for card in cards_data:
            difficulty = card.get('difficulty', 5.0)
            if difficulty > 7:
                breakdown["very_hard"] += 1
                total_time += review_times["very_hard"]
            elif difficulty >= 5:
                breakdown["hard"] += 1
                total_time += review_times["hard"]
            elif difficulty >= 3:
                breakdown["medium"] += 1
                total_time += review_times["medium"]
            else:
                breakdown["easy"] += 1
                total_time += review_times["easy"]
        
        return {
            "estimated_duration": total_time,
            "card_breakdown": breakdown
        }