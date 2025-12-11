from datetime import datetime, timedelta
from typing import Dict, Any


class SRSAlgorithm:
    def __init__(self):
        pass
    
    def calculate_next_review(
        self,
        quality: int,
        ease_factor: float = 2.5,
        interval_days: int = 1,
        repetitions: int = 0
    ) -> Dict[str, Any]:
        if quality < 3:
            repetitions = 0
            interval_days = 1
        else:
            repetitions += 1
            
            if repetitions == 1:
                interval_days = 1
            elif repetitions == 2:
                interval_days = 6
            else:
                interval_days = int(interval_days * ease_factor)
        
        ease_factor = max(1.3, ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
        
        due_date = datetime.utcnow() + timedelta(days=interval_days)
        
        return {
            'ease_factor': ease_factor,
            'interval_days': interval_days,
            'repetitions': repetitions,
            'due_date': due_date.isoformat()
        }
    
    def get_due_cards(self, current_time: datetime = None) -> Dict[str, Any]:
        if current_time is None:
            current_time = datetime.utcnow()
        
        return {
            'timestamp': current_time.isoformat(),
            'query': f"due_date <= '{current_time.isoformat()}'"
        }
