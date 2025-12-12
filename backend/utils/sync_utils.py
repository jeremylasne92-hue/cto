"""
Utility functions for flashcard sync engine
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

def retry_with_backoff(func, max_attempts=3, base_delay=1.0):
    """Retry function with exponential backoff"""
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise e
            
            delay = base_delay * (2 ** attempt)
            time.sleep(delay)
    
    raise Exception("Max retry attempts reached")

def validate_sync_data(data: Dict[str, Any]) -> bool:
    """Validate sync data structure"""
    required_fields = ['object_type', 'operation', 'data']
    
    for field in required_fields:
        if field not in data:
            return False
    
    valid_operations = ['CREATE', 'UPDATE', 'DELETE']
    if data['operation'] not in valid_operations:
        return False
    
    valid_types = ['deck', 'card', 'review']
    if data['object_type'] not in valid_types:
        return False
    
    return True

def serialize_datetime(obj):
    """JSON serializer for datetime objects"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def calculate_next_review(ease_factor: float, interval: int, repetition: int, grade: int) -> Dict[str, int]:
    """Calculate next review parameters using SuperMemo 2 algorithm"""
    import math
    
    # Update ease factor
    ease_factor = ease_factor + (0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02))
    
    if ease_factor < 1.3:
        ease_factor = 1.3
    
    # Update repetition and interval
    if grade < 3:
        repetition = 0
        interval = 1
    else:
        if repetition == 0:
            interval = 1
        elif repetition == 1:
            interval = 6
        else:
            interval = round(interval * ease_factor)
        repetition += 1
    
    return {
        'ease_factor': round(ease_factor, 2),
        'interval': interval,
        'repetition': repetition
    }

def format_sync_status(unsynced_count: int, last_sync: Optional[datetime]) -> str:
    """Format sync status for display"""
    if unsynced_count == 0:
        return "Synced ✓"
    elif unsynced_count > 0:
        return f"Syncing... {unsynced_count} pending"
    else:
        return "Offline ⊘"

def get_time_until_next_sync(last_sync: Optional[datetime], sync_interval_hours: int = 24) -> Optional[int]:
    """Get seconds until next scheduled sync"""
    if not last_sync:
        return None
    
    next_sync = last_sync + timedelta(hours=sync_interval_hours)
    now = datetime.utcnow()
    
    if next_sync <= now:
        return 0
    
    return int((next_sync - now).total_seconds())

def create_sync_payload(changes: List[Dict[str, Any]], last_sync: Optional[datetime] = None) -> Dict[str, Any]:
    """Create sync payload with metadata"""
    payload = {
        'device_info': {
            'platform': 'desktop',  # or 'mobile'
            'app_version': '1.0.0',
            'sync_version': '1.0'
        },
        'sync_info': {
            'last_sync': last_sync.isoformat() if last_sync else None,
            'sync_timestamp': datetime.utcnow().isoformat(),
            'changes_count': len(changes)
        },
        'changes': changes
    }
    
    return payload

def parse_sync_response(response_data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse sync response and extract data"""
    if not response_data.get('success'):
        raise Exception(response_data.get('error', 'Sync failed'))
    
    return {
        'pulled_data': response_data.get('data', {}),
        'session_info': response_data.get('session', {}),
        'conflicts': response_data.get('conflicts', 0)
    }