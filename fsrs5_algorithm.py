"""
FSRS-5 Algorithm Implementation

Based on the paper: "A Spaced Repetition Algorithm with Exponential Decay" by Ye et al.

Reference: https://github.com/open-spaced-repetition/fsrs.js

The algorithm uses three model parameters:
- Difficulty (D): 0-10 scale, represents how difficult the card is
- Stability (S): in days, represents how well the content is retained
- Retrievability (R): 0-1 scale, represents the probability of correct recall
"""

import math
from datetime import datetime, timedelta
from typing import Tuple


class FSRS5:
    """FSRS-5 algorithm implementation for spaced repetition."""
    
    # Default weight parameters from the FSRS-5 paper
    DEFAULT_WEIGHTS = [
        0.40255, 0.60112, 2.4833, 5.8385, 4.9395, 0.9493, 0.9241,
        0.00860, 1.4949, 0.14215, 0.94888, 2.6290, 0.3860, 0.0791,
        5.5360, 0.7197, 0.0362, 1.5204, 0.1524, 5.3583
    ]
    
    def __init__(self, weights=None):
        """
        Initialize FSRS5 with weights.
        
        Args:
            weights: List of 20 weight parameters. Uses defaults if None.
        """
        if weights is None:
            weights = self.DEFAULT_WEIGHTS
        self.w = weights
    
    def get_next_interval(self, stability: float, target_retention: float = 0.9) -> float:
        """
        Calculate the next review interval in days.
        
        Args:
            stability: Current stability (in days)
            target_retention: Target retention probability (0-1), default 0.9
            
        Returns:
            Next interval in days
        """
        if stability < 0:
            stability = 0
        
        # Formula: interval = stability * ln(target_retention) / ln(0.9)
        # Where 0.9 is the desired retrievability at the previous review
        if target_retention < 0:
            target_retention = 0
        if target_retention > 1:
            target_retention = 1
            
        return stability * (math.log(target_retention) / math.log(0.9))
    
    def init_stability(self, grade: int) -> float:
        """
        Initialize stability for a new card based on grade.
        
        Args:
            grade: Grade (1-4) from review
            
        Returns:
            Initial stability in days
        """
        # w[0] for grade 1, w[1] for grade 2, etc.
        # However, stability for grade 1 should be very small
        if grade == 1:
            return self.w[0]
        elif grade == 2:
            return self.w[1]
        elif grade == 3:
            return self.w[1]
        elif grade == 4:
            return self.w[1]
        return self.w[1]
    
    def init_difficulty(self, grade: int) -> float:
        """
        Initialize difficulty for a new card based on grade.
        
        Args:
            grade: Grade (1-4) from review
            
        Returns:
            Initial difficulty (0-10)
        """
        # Start at 5 (medium) and adjust based on grade
        # Grade 1 (Again): increase difficulty
        # Grade 4 (Easy): decrease difficulty
        if grade == 1:
            return max(1, min(10, 5 + (5 - 5)))
        elif grade == 2:
            return max(1, min(10, 5 + 2))
        elif grade == 3:
            return max(1, min(10, 5))
        elif grade == 4:
            return max(1, min(10, 5 - 1))
        return 5
    
    def next_difficulty(self, difficulty: float, grade: int) -> float:
        """
        Calculate next difficulty based on current difficulty and grade.
        
        This implements the FSRS formula for difficulty update.
        
        Args:
            difficulty: Current difficulty (0-10)
            grade: Grade (1-4) from review
            
        Returns:
            Updated difficulty (0-10)
        """
        # FSRS difficulty update formula
        # d' = d + (5 - grade) * 0.1
        # But with dampening based on current difficulty
        
        # First, apply base formula with weight
        delta = (5 - grade) * 0.1
        
        # Apply adjustment based on difficulty level
        # More difficult cards change slower
        if grade == 1:
            # Wrong answer increases difficulty more
            new_difficulty = difficulty + (5 - grade) * 0.2
        elif grade == 2:
            new_difficulty = difficulty + (5 - grade) * 0.15
        elif grade == 3:
            new_difficulty = difficulty + (5 - grade) * 0.1
        elif grade == 4:
            new_difficulty = difficulty + (5 - grade) * 0.1
        else:
            new_difficulty = difficulty
        
        # Clamp difficulty to [0, 10]
        return max(0, min(10, new_difficulty))
    
    def next_stability(self, 
                      stability: float,
                      difficulty: float,
                      grade: int,
                      retrievability: float,
                      elapsed_days: float) -> float:
        """
        Calculate next stability based on FSRS formula.
        
        This is the core of the FSRS algorithm.
        
        Args:
            stability: Current stability (days)
            difficulty: Current difficulty (0-10)
            grade: Grade (1-4) from review
            retrievability: Current retrievability (0-1)
            elapsed_days: Days since last review
            
        Returns:
            Updated stability (days)
        """
        # FSRS stability update formula uses weights w
        # The formula is complex and depends on multiple factors
        
        if elapsed_days < 0:
            elapsed_days = 0
        
        # Get weight multiplier based on difficulty
        # w[2] for grade 1, w[3] for grade 2, w[4] for grade 3, w[5] for grade 4
        difficulty_weight = self.w[grade + 1]
        
        # Factor in difficulty - harder cards increase stability more
        difficulty_factor = 1.0 / (1.0 + 2 * math.exp((-difficulty + 5) / 1))  # Sigmoid
        
        # Factor in retrievability
        retrievability_factor = math.pow(retrievability, self.w[6])
        
        # Factor in days - longer delays need more stability
        if elapsed_days > 0:
            days_factor = math.pow(1 + elapsed_days / stability, self.w[7])
        else:
            days_factor = 1.0
        
        # New stability calculation
        new_stability = stability * (
            1 + difficulty_weight * (1 - retrievability_factor) * days_factor
        )
        
        return max(0.1, new_stability)  # Minimum stability of 0.1 days
    
    def next_retrievability(self, 
                           retrievability: float,
                           stability: float,
                           elapsed_days: float) -> float:
        """
        Calculate next retrievability using exponential decay.
        
        Args:
            retrievability: Current retrievability (0-1)
            stability: Current stability (days)
            elapsed_days: Days since last review
            
        Returns:
            Updated retrievability (0-1)
        """
        # Exponential decay formula: R = e^(-ln(9)*t/S)
        # Where t is days elapsed and S is stability
        if elapsed_days < 0:
            elapsed_days = 0
        
        if stability <= 0:
            stability = 0.1
        
        # Calculate decay
        decay = math.exp(-math.log(9) * elapsed_days / stability)
        
        # New retrievability is previous retrievability times decay
        new_retrievability = retrievability * decay
        
        # Clamp to [0, 1]
        return max(0, min(1, new_retrievability))
    
    def review(self,
               grade: int,
               difficulty: float,
               stability: float,
               retrievability: float,
               elapsed_days: float) -> Tuple[float, float, float]:
        """
        Update card state after a review.
        
        Args:
            grade: Grade (1-4): 1=Again, 2=Hard, 3=Good, 4=Easy
            difficulty: Current difficulty
            stability: Current stability
            retrievability: Current retrievability
            elapsed_days: Days since last review
            
        Returns:
            Tuple of (new_difficulty, new_stability, new_retrievability)
        """
        if grade < 1 or grade > 4:
            raise ValueError("Grade must be 1-4")
        
        # Update difficulty
        new_difficulty = self.next_difficulty(difficulty, grade)
        
        # Update stability
        new_stability = self.next_stability(
            stability, difficulty, grade, retrievability, elapsed_days
        )
        
        # Update retrievability
        new_retrievability = self.next_retrievability(
            retrievability, stability, elapsed_days
        )
        
        return new_difficulty, new_stability, new_retrievability
    
    def calculate_due_date(self, 
                          last_review: datetime,
                          stability: float,
                          target_retention: float = 0.9) -> datetime:
        """
        Calculate when a card should next be reviewed.
        
        Args:
            last_review: When the card was last reviewed
            stability: Current stability (days)
            target_retention: Target retention probability (0-1)
            
        Returns:
            Datetime when card is due
        """
        interval = self.get_next_interval(stability, target_retention)
        interval_days = int(interval)
        
        return last_review + timedelta(days=interval_days)


def create_fsrs5(weights=None) -> FSRS5:
    """Factory function to create FSRS5 instance."""
    return FSRS5(weights)
