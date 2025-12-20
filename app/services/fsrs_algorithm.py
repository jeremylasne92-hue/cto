import math
from datetime import datetime, timedelta

# Default parameters for FSRS v5
class FSRSParameters:
    def __init__(self):
        self.request_retention = 0.9
        self.maximum_interval = 36500
        self.w = [
            0.40255, 1.18385, 3.173, 15.69105, 
            7.19605, 0.5345, 1.4604, 0.0046, 
            1.54575, 0.1192, 1.01925, 1.9395, 
            0.11, 0.29605, 0.22705, 0.20375, 
            0.37325, 0.1062, 2.7245
        ]

class FSRSCalculator:
    def __init__(self, params: FSRSParameters = None):
        self.p = params if params else FSRSParameters()

    def init_stability(self, grade: int) -> float:
        # grade: 1..4 (Again, Hard, Good, Easy)
        # w[0]..w[3] map to grade 1..4
        return max(self.p.w[grade - 1], 0.1)

    def init_difficulty(self, grade: int) -> float:
        # D0 = w[4] - (grade - 3) * w[5]
        # constrained to [1, 10]
        val = self.p.w[4] - (grade - 3) * self.p.w[5]
        return min(max(val, 1), 10)

    def next_difficulty(self, d: float, grade: int) -> float:
        # next_d = d - w[6] * (grade - 3)
        next_d = d - self.p.w[6] * (grade - 3)
        # mean reversion
        # w[7] is mean_reversion_factor
        # next_d = w[7] * w[4] + (1 - w[7]) * next_d
        next_d = self.p.w[7] * self.p.w[4] + (1 - self.p.w[7]) * next_d
        return min(max(next_d, 1), 10)

    def next_stability(self, s: float, d: float, r: float, grade: int) -> float:
        if grade == 1: # Again
            # S_forget = w[11] * D^(-w[12]) * ((S + 1)^w[13] - 1) * exp(w[14] * (1 - R))
            return self.p.w[11] * math.pow(d, -self.p.w[12]) * (math.pow(s + 1, self.p.w[13]) - 1) * math.exp(self.p.w[14] * (1 - r))
        
        # Recall (Hard, Good, Easy)
        # S_recall = S * (1 + exp(w[8]) * (11 - D) * S^(-w[9]) * (exp(w[10] * (1 - R)) - 1))
        # Hard penalty: w[15] if grade == 2 else 1
        # Easy bonus: w[16] if grade == 4 else 1
        
        hard_penalty = self.p.w[15] if grade == 2 else 1
        easy_bonus = self.p.w[16] if grade == 4 else 1
        
        return s * (1 + math.exp(self.p.w[8]) * 
                    (11 - d) * 
                    math.pow(s, -self.p.w[9]) * 
                    (math.exp((1 - r) * self.p.w[10]) - 1) * 
                    hard_penalty * 
                    easy_bonus)

    def forgetting_curve(self, elapsed_days: float, stability: float) -> float:
        # R = (1 + factor * elapsed / S) ^ decay
        return math.pow(1 + 19/81 * elapsed_days / stability, -0.5)

    def next_interval(self, stability: float) -> float:
        # I = S / factor * (R_req ^ (1/decay) - 1)
        new_interval = stability / (19/81) * (math.pow(self.p.request_retention, 1/-0.5) - 1)
        return min(max(new_interval, 1), self.p.maximum_interval)
