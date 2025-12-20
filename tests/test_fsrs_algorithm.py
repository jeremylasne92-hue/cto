import pytest
from app.services.fsrs_algorithm import FSRSCalculator, FSRSParameters

class TestFSRSAlgorithm:
    def setup_method(self):
        self.fsrs = FSRSCalculator()
        
    def test_initial_values(self):
        # Good (3)
        # S0 = w[2] = 3.173
        # D0 = w[4] = 7.19605
        s = self.fsrs.init_stability(3)
        d = self.fsrs.init_difficulty(3)
        
        assert abs(s - 3.173) < 1e-5
        assert abs(d - 7.19605) < 1e-5
        
        # Easy (4)
        # S0 = w[3] = 15.69105
        # D0 = w[4] - 1 * w[5] = 7.19605 - 0.5345 = 6.66155
        s = self.fsrs.init_stability(4)
        d = self.fsrs.init_difficulty(4)
        
        assert abs(s - 15.69105) < 1e-5
        assert abs(d - 6.66155) < 1e-5

    def test_interval_calculation(self):
        # Interval should equal stability when R=0.9 (implicit in default params)
        s = 10.0
        i = self.fsrs.next_interval(s)
        # I = S
        assert abs(i - 10.0) < 1e-5
        
    def test_review_stability_increase(self):
        # New card rated Good
        s = self.fsrs.init_stability(3)
        d = self.fsrs.init_difficulty(3)
        
        # Review after 3 days (approx interval), rated Good
        elapsed = 3.0
        r = self.fsrs.forgetting_curve(elapsed, s)
        
        next_d = self.fsrs.next_difficulty(d, 3)
        next_s = self.fsrs.next_stability(s, d, r, 3)
        
        assert next_s > s, "Stability should increase after a Good review"
        assert next_d <= d, "Difficulty should typically decrease or stay similar on Good"

    def test_forgetting_curve(self):
        s = 10.0
        # at elapsed = 0, R = 1
        assert self.fsrs.forgetting_curve(0, s) == 1.0
        # at elapsed = S, R = 0.9
        assert abs(self.fsrs.forgetting_curve(s, s) - 0.9) < 1e-5
