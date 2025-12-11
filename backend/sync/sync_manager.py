from typing import List, Dict, Any
from datetime import datetime
import uuid


class SyncManager:
    def __init__(self):
        self.pending_operations: List[Dict[str, Any]] = []
    
    def log_operation(self, entity_type: str, entity_id: str, operation: str) -> str:
        log_entry = {
            'id': str(uuid.uuid4()),
            'entity_type': entity_type,
            'entity_id': entity_id,
            'operation': operation,
            'synced': False,
            'sync_timestamp': None,
            'created_at': datetime.utcnow().isoformat()
        }
        self.pending_operations.append(log_entry)
        return log_entry['id']
    
    def mark_synced(self, log_id: str):
        for op in self.pending_operations:
            if op['id'] == log_id:
                op['synced'] = True
                op['sync_timestamp'] = datetime.utcnow().isoformat()
                break
    
    def get_pending_operations(self) -> List[Dict[str, Any]]:
        return [op for op in self.pending_operations if not op['synced']]
    
    def clear_synced_operations(self):
        self.pending_operations = [op for op in self.pending_operations if not op['synced']]
