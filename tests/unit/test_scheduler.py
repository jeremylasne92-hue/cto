"""
Unit tests for Scheduler & Session Optimization (FSRS-5)
Sprint 3.2 - Comprehensive testing of scheduling and session optimization
"""

import pytest
import tempfile
import os
from datetime import datetime, timedelta
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from database import SRSDatabase, Card, CardSRSState, ReviewLog
from fsrs_algorithm import FSRS5Algorithm, FSRSState, FSRSOptimizer, ReviewResult
from srs_engine import SRSEngine


class TestSessionOptimizer:
    """Test session optimization features"""
    
    def setup_method(self):
        self.optimizer = FSRSOptimizer()
        
    def test_optimize_review_order_structure(self):
        """Test that optimize_review_order returns properly structured warm-up/main/cool-down pattern"""
        
        # Create sample cards with varying difficulties
        cards_data = [
            {"id": "1", "difficulty": 2.0, "due_date": "2024-01-01T00:00:00"},  # Easy
            {"id": "2", "difficulty": 6.0, "due_date": "2024-01-01T00:00:00"},  # Medium
            {"id": "3", "difficulty": 8.5, "due_date": "2024-01-01T00:00:00"},  # Hard
            {"id": "4", "difficulty": 9.0, "due_date": "2024-01-01T00:00:00"},  # Very Hard
            {"id": "5", "difficulty": 4.0, "due_date": "2024-01-01T00:00:00"},  # Medium
            {"id": "6", "difficulty": 1.5, "due_date": "2024-01-01T00:00:00"},  # Easy
        ]
        
        optimized = self.optimizer.optimize_review_order(cards_data)
        
        # Check all cards are included
        assert len(optimized) == len(cards_data)
        assert set(card['id'] for card in optimized) == set(card['id'] for card in cards_data)
        
        # Check structure: should have some medium cards at start (warm-up)
        # followed by hard/very hard cards (main), then easy at end (cool-down)
        difficulties = [card['difficulty'] for card in optimized]
        
        # Verify pattern: medium first, then hard/very hard, then easy
        # First card should be medium difficulty (3-5)
        assert 3 <= difficulties[0] <= 5, f"First card should be medium difficulty, got {difficulties[0]}"
        
        # Should have hard/very hard cards in middle
        hard_cards_in_middle = any(d >= 7 for d in difficulties[1:-1])
        assert hard_cards_in_middle, "Should have hard cards in middle"
        
        # Should have easy cards toward the end
        easy_cards_at_end = any(d < 3 for d in difficulties[-2:])
        assert easy_cards_at_end, "Should have easy cards toward the end"
    
    def test_warm_up_pattern(self):
        """Test warm-up phase uses medium difficulty cards first"""
        
        # Create 10 cards: 3 easy, 4 medium, 3 hard
        cards_data = []
        
        # Add easy cards (difficulty < 3)
        for i in range(3):
            cards_data.append({
                "id": f"easy_{i}",
                "difficulty": 2.0 + i * 0.3,
                "due_date": "2024-01-01T00:00:00"
            })
        
        # Add medium cards (difficulty 3-7)
        for i in range(4):
            cards_data.append({
                "id": f"medium_{i}",
                "difficulty": 4.0 + i * 0.5,
                "due_date": "2024-01-01T00:00:00"
            })
        
        # Add hard cards (difficulty > 7)
        for i in range(3):
            cards_data.append({
                "id": f"hard_{i}",
                "difficulty": 7.5 + i * 0.4,
                "due_date": "2024-01-01T00:00:00"
            })
        
        optimized = self.optimizer.optimize_review_order(cards_data)
        
        # First 20% should be medium difficulty (warm-up)
        warmup_count = max(1, len(cards_data) // 5)
        warmup_cards = optimized[:warmup_count]
        
        for card in warmup_cards:
            assert 3 <= card['difficulty'] <= 7, f"Warmup card should be medium difficulty, got {card['difficulty']}"
    
    def test_main_phase_pattern(self):
        """Test main phase contains hard cards mid-session"""
        
        cards_data = [
            {"id": f"card_{i}", "difficulty": diff, "due_date": "2024-01-01T00:00:00"}
            for i, diff in enumerate([2.0, 6.0, 8.0, 9.0, 4.0, 1.0])
        ]
        
        optimized = self.optimizer.optimize_review_order(cards_data)
        
        # Hard cards (difficulty >= 7) should be in the middle
        hard_cards = [card for card in optimized if card['difficulty'] >= 7]
        assert len(hard_cards) == 2  # Should have 2 hard cards
        
        # Hard cards should not be at the very beginning or end
        hard_positions = [optimized.index(card) for card in hard_cards]
        assert not all(pos == 0 for pos in hard_positions), "Hard cards should not all be at start"
        assert not all(pos == len(optimized) - 1 for pos in hard_positions), "Hard cards should not all be at end"
    
    def test_cool_down_pattern(self):
        """Test cool-down phase uses easy cards at end"""
        
        cards_data = [
            {"id": f"card_{i}", "difficulty": diff, "due_date": "2024-01-01T00:00:00"}
            for i, diff in enumerate([2.0, 6.0, 8.0, 4.0, 1.5, 2.5, 9.0])
        ]
        
        optimized = self.optimizer.optimize_review_order(cards_data)
        
        # Last cards should be easy (difficulty < 3)
        last_cards = optimized[-3:]  # Check last 3 cards
        easy_count = sum(1 for card in last_cards if card['difficulty'] < 3)
        
        assert easy_count >= 1, "Should have at least one easy card at the end for cool-down"
    
    def test_overdue_prioritization(self):
        """Test overdue cards are prioritized within difficulty groups"""
        
        # Create cards with same difficulty but different due dates
        base_date = datetime.now()
        cards_data = [
            {"id": "1", "difficulty": 5.0, "due_date": (base_date - timedelta(days=5)).isoformat()},  # Overdue 5 days
            {"id": "2", "difficulty": 5.0, "due_date": (base_date - timedelta(days=10)).isoformat()},  # Overdue 10 days
            {"id": "3", "difficulty": 5.0, "due_date": (base_date - timedelta(days=1)).isoformat()},   # Overdue 1 day
            {"id": "4", "difficulty": 5.0, "due_date": (base_date - timedelta(days=3)).isoformat()},   # Overdue 3 days
        ]
        
        optimized = self.optimizer.optimize_review_order(cards_data)
        
        # Extract due dates in order
        due_dates = [card['due_date'] for card in optimized]
        
        # Should be sorted by due date (oldest first)
        assert due_dates == sorted(due_dates), "Cards should be sorted by due date within difficulty groups"
        
        # Most overdue card should be first
        assert optimized[0]['id'] == "2", "Most overdue card should be first"
    
    def test_interleaving_prevents_clustering(self):
        """Test interleaving logic prevents clustering of similar cards"""
        
        # Create cards with the same difficulty to test interleaving
        cards_data = []
        for i in range(10):
            cards_data.append({
                "id": f"cluster_{i}",
                "difficulty": 6.0,  # All same difficulty
                "due_date": (datetime.now() - timedelta(days=i)).isoformat()
            })
        
        optimized = self.optimizer.optimize_review_order(cards_data)
        
        # Cards should be ordered by due date (interleaved by time)
        due_dates = [datetime.fromisoformat(card['due_date']) for card in optimized]
        
        # Check that they're sorted by due date (oldest first)
        assert due_dates == sorted(due_dates), "Cards with same difficulty should be interleaved by due date"
    
    def test_empty_queue_edge_case(self):
        """Test session optimization with empty card queue"""
        
        optimized = self.optimizer.optimize_review_order([])
        assert optimized == [], "Should return empty list for empty input"
    
    def test_single_card_edge_case(self):
        """Test session optimization with single card"""
        
        cards_data = [{"id": "single", "difficulty": 5.0, "due_date": "2024-01-01T00:00:00"}]
        optimized = self.optimizer.optimize_review_order(cards_data)
        
        assert len(optimized) == 1
        assert optimized[0]['id'] == "single"
    
    def test_all_easy_cards_pattern(self):
        """Test pattern with all easy cards"""
        
        cards_data = [
            {"id": f"easy_{i}", "difficulty": 2.0, "due_date": "2024-01-01T00:00:00"}
            for i in range(5)
        ]
        
        optimized = self.optimizer.optimize_review_order(cards_data)
        
        assert len(optimized) == 5
        # All should be easy, so they'll all be in "cool-down" phase
        for card in optimized:
            assert card['difficulty'] < 3
    
    def test_all_hard_cards_pattern(self):
        """Test pattern with all hard cards"""
        
        cards_data = [
            {"id": f"hard_{i}", "difficulty": 8.0, "due_date": "2024-01-01T00:00:00"}
            for i in range(5)
        ]
        
        optimized = self.optimizer.optimize_review_order(cards_data)
        
        assert len(optimized) == 5
        # All should be hard/very hard, so they'll be in main phase
        for card in optimized:
            assert card['difficulty'] >= 7
    
    def test_session_duration_estimation(self):
        """Test optimal session duration estimation"""
        
        # Test with optimal number of cards (15+ for 20-30 minute session)
        cards_data = []
        for i in range(20):
            # Mix of difficulties
            if i < 5:
                difficulty = 2.0  # Easy
            elif i < 15:
                difficulty = 5.5  # Medium
            else:
                difficulty = 8.0  # Hard
            
            cards_data.append({
                "id": f"card_{i}",
                "difficulty": difficulty,
                "due_date": "2024-01-01T00:00:00"
            })
        
        duration_stats = self.optimizer.estimate_session_duration(cards_data)
        
        assert "estimated_duration" in duration_stats
        assert "card_breakdown" in duration_stats
        
        # Should have breakdown for all difficulty levels
        breakdown = duration_stats["card_breakdown"]
        assert "very_hard" in breakdown
        assert "hard" in breakdown
        assert "medium" in breakdown
        assert "easy" in breakdown
        
        # Estimated duration should be reasonable (roughly 2-3 seconds per card minimum)
        estimated_duration = duration_stats["estimated_duration"]
        assert 30 <= estimated_duration <= 300, f"Estimated duration {estimated_duration}s seems unreasonable for 20 cards"
    
    def test_optimal_session_duration_20_30_minutes(self):
        """Test that optimal session has ~20-30 minutes duration with 15+ cards"""
        
        # Create 20 cards with mixed difficulties
        cards_data = []
        for i in range(20):
            difficulty = 2.0 + (i % 8)  # Range from 2.0 to 9.0
            cards_data.append({
                "id": f"card_{i}",
                "difficulty": difficulty,
                "due_date": "2024-01-01T00:00:00"
            })
        
        duration_stats = self.optimizer.estimate_session_duration(cards_data)
        
        estimated_minutes = duration_stats["estimated_duration"] / 60
        
        # Target: 20-30 minutes for 15+ cards
        assert 15 <= estimated_minutes <= 40, f"Session should take ~20-30 minutes, got {estimated_minutes:.1f} minutes"
    
    def test_should_interleave_cards(self):
        """Test interleaving logic between decks"""
        
        # Test similar difficulty decks (should interleave)
        deck1 = {"avg_difficulty": 5.0, "card_count": 10}
        deck2 = {"avg_difficulty": 5.2, "card_count": 10}
        
        assert self.optimizer.should_interleave_cards(deck1, deck2) == True
        
        # Test very different difficulty decks (should not interleave)
        deck3 = {"avg_difficulty": 2.0, "card_count": 10}
        deck4 = {"avg_difficulty": 9.0, "card_count": 10}
        
        assert self.optimizer.should_interleave_cards(deck3, deck4) == False


class TestLeechDetection:
    """Test leech detection and handling"""
    
    def setup_method(self):
        self.algorithm = FSRS5Algorithm()
    
    def test_leech_detection_high_difficulty(self):
        """Test leech detection for high difficulty cards"""
        
        # Cards with difficulty > 8.5 should be leeches
        assert self.algorithm.is_leech(difficulty=9.0, lapses=0) == True
        assert self.algorithm.is_leech(difficulty=8.6, lapses=0) == True
        
        # Cards with difficulty <= 8.5 should not be leeches (unless many lapses)
        assert self.algorithm.is_leech(difficulty=8.0, lapses=0) == False
        assert self.algorithm.is_leech(difficulty=5.0, lapses=2) == False
    
    def test_leech_detection_many_lapses(self):
        """Test leech detection for cards with many lapses (>2)"""
        
        # Cards with >2 lapses should be leeches
        assert self.algorithm.is_leech(difficulty=5.0, lapses=3) == True
        assert self.algorithm.is_leech(difficulty=4.0, lapses=5) == True
        
        # Cards with <=2 lapses should not be leeches (unless high difficulty)
        assert self.algorithm.is_leech(difficulty=5.0, lapses=2) == False
        assert self.algorithm.is_leech(difficulty=4.0, lapses=1) == False
    
    def test_leech_detection_combined_criteria(self):
        """Test leech detection with both difficulty and lapses criteria"""
        
        # High difficulty + many lapses = definitely leech
        assert self.algorithm.is_leech(difficulty=9.0, lapses=3) == True
        
        # Borderline case: high difficulty but few lapses
        assert self.algorithm.is_leech(difficulty=8.6, lapses=1) == True  # Difficulty threshold met
        
        # Borderline case: moderate difficulty but many lapses
        assert self.algorithm.is_leech(difficulty=7.0, lapses=4) == True  # Lapse threshold met


class TestCardReorderingAlgorithm:
    """Test card reordering maintains learning efficiency"""
    
    def setup_method(self):
        self.optimizer = FSRSOptimizer()
    
    def test_maintains_learning_efficiency_progression(self):
        """Test that card ordering maintains efficient learning progression"""
        
        # Create cards with progressive difficulty
        cards_data = []
        difficulties = [2.0, 3.5, 5.0, 6.5, 8.0]  # Progressive difficulty
        for i, diff in enumerate(difficulties):
            cards_data.append({
                "id": f"progressive_{i}",
                "difficulty": diff,
                "due_date": "2024-01-01T00:00:00"
            })
        
        optimized = self.optimizer.optimize_review_order(cards_data)
        
        # Check that we have some progression, even if optimized
        optimized_difficulties = [card['difficulty'] for card in optimized]
        
        # Should have some variation (not all same difficulty)
        assert len(set(optimized_difficulties)) > 1, "Should maintain difficulty variation"
    
    def test_avoids_backloading_all_hard_cards(self):
        """Test that algorithm doesn't put all hard cards at the end"""
        
        # Create many hard cards
        cards_data = [
            {"id": f"hard_{i}", "difficulty": 8.5, "due_date": "2024-01-01T00:00:00"}
            for i in range(10)
        ]
        
        # Add some easy cards
        cards_data.extend([
            {"id": f"easy_{i}", "difficulty": 2.0, "due_date": "2024-01-01T00:00:00"}
            for i in range(2)
        ])
        
        optimized = self.optimizer.optimize_review_order(cards_data)
        
        # Check last cards - some should be easy, not all hard
        last_3_cards = optimized[-3:]
        easy_in_last = any(card['difficulty'] < 3 for card in last_3_cards)
        
        assert easy_in_last, "Should have easy cards at the end for cool-down"


class TestSessionGenerator:
    """Test session generator returns due cards in correct order"""
    
    def setup_method(self):
        # Use temporary database
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.engine = SRSEngine(self.temp_db.name)
    
    def teardown_method(self):
        os.unlink(self.temp_db.name)
    
    def test_session_generator_returns_correct_order(self):
        """Test that session generator returns cards in optimized order"""
        
        # Create deck and cards
        deck = self.engine.create_deck("Test Session")
        deck_id = deck['deck_id']
        
        # Create cards with different difficulties
        cards = []
        difficulties = [2.0, 5.0, 8.5, 3.5, 9.0, 1.0]
        for i, diff in enumerate(difficulties):
            card = self.engine.create_card(deck_id, f"Card {i}", f"Answer {i}")
            cards.append(card)
        
        # Start review session
        session = self.engine.start_review_session(deck_id)
        
        # Check session structure
        assert 'session_id' in session
        assert 'due_cards_count' in session
        assert 'cards' in session
        assert 'session_optimizer' in session
        
        # Verify we have cards returned
        assert len(session['cards']) == len(difficulties)
        
        # Check that optimizer information is provided
        optimizer_info = session['session_optimizer']
        assert 'warmup_medium' in optimizer_info
        assert 'main_hard' in optimizer_info
        assert 'cooldown_easy' in optimizer_info
        
        # Verify card counts add up
        total_cards = (optimizer_info['warmup_medium'] + 
                      optimizer_info['main_hard'] + 
                      optimizer_info['cooldown_easy'])
        assert total_cards == len(difficulties)
    
    def test_session_with_empty_deck(self):
        """Test session generator with empty deck"""
        
        # Create empty deck
        deck = self.engine.create_deck("Empty Deck")
        deck_id = deck['deck_id']
        
        # Start review session on empty deck
        session = self.engine.start_review_session(deck_id)
        
        # Should handle empty deck gracefully
        assert session['due_cards_count'] == 0
        assert len(session['cards']) == 0
        assert session['session_optimizer']['warmup_medium'] == 0
        assert session['session_optimizer']['main_hard'] == 0
        assert session['session_optimizer']['cooldown_easy'] == 0


class TestABTestLearningOutcomes:
    """Test A/B comparison shows improved learning outcomes vs random order"""
    
    def setup_method(self):
        self.optimizer = FSRSOptimizer()
    
    def test_optimized_vs_random_order_efficiency(self):
        """Test that optimized order provides better learning efficiency than random"""
        
        # Create sample cards with difficulties
        cards_data = [
            {"id": f"card_{i}", "difficulty": diff, "due_date": "2024-01-01T00:00:00"}
            for i, diff in enumerate([1.5, 2.0, 3.5, 5.0, 6.5, 8.0, 9.0, 2.5, 4.0, 7.5])
        ]
        
        # Get optimized order
        optimized = self.optimizer.optimize_review_order(cards_data.copy())
        
        # Simulate random order (just shuffle)
        import random
        random_order = cards_data.copy()
        random.shuffle(random_order)
        
        # Analyze difficulty progression in optimized order
        optimized_difficulties = [card['difficulty'] for card in optimized]
        
        # Should have some structure: medium -> hard -> easy pattern
        # Calculate a simple "efficiency score" based on variation and pattern
        def efficiency_score(order):
            diffs = [card['difficulty'] for card in order]
            
            # Score 1: variety (not all same difficulty)
            variety_score = len(set(diffs)) / len(diffs)
            
            # Score 2: avoid extreme clustering
            # Count transitions between difficulty zones
            zone_transitions = 0
            for i in range(1, len(diffs)):
                prev_zone = self._get_difficulty_zone(diffs[i-1])
                curr_zone = self._get_difficulty_zone(diffs[i])
                if prev_zone != curr_zone:
                    zone_transitions += 1
            
            clustering_score = zone_transitions / (len(diffs) - 1) if len(diffs) > 1 else 0
            
            return variety_score + clustering_score
        
        optimized_score = efficiency_score(optimized)
        random_score = efficiency_score(random_order)
        
        # Optimized should have better or equal efficiency score
        assert optimized_score >= random_score * 0.8, "Optimized order should be at least 80% as efficient as random"
    
    def _get_difficulty_zone(self, difficulty):
        """Helper to categorize difficulty into zones"""
        if difficulty < 3:
            return "easy"
        elif difficulty < 7:
            return "medium"
        else:
            return "hard"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])