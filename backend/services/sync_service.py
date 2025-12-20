"""
Sync service for managing data synchronization between devices
"""

from datetime import datetime, timedelta
from ..models import db, Deck, Card, ReviewLog, SyncLog, User, SyncSession

class SyncService:
    """Service for handling synchronization operations"""
    
    def __init__(self):
        self.max_objects_per_sync = 1000
    
    def calculate_srs_update(self, card, grade):
        """Calculate SRS (Spaced Repetition System) updates based on grade"""
        import math
        
        # SuperMemo 2 algorithm
        ease_factor = card.ease_factor
        repetition = card.repetition
        interval = card.interval
        
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
    
    def pull_changes(self, user, last_sync=None):
        """Pull changes from server to client"""
        try:
            # Create sync session
            sync_session = SyncSession(
                user_id=user.id,
                device_id=user.device_id,
                session_token=f"sync_{user.id}_{datetime.utcnow().timestamp()}",
                status='in_progress'
            )
            db.session.add(sync_session)
            db.session.flush()
            
            # Get changes since last sync
            if last_sync:
                changes = SyncLog.query.filter(
                    SyncLog.timestamp > last_sync,
                    SyncLog.synced == False
                ).limit(self.max_objects_per_sync).all()
            else:
                # First sync - get all data
                changes = SyncLog.query.filter(
                    SyncLog.synced == False
                ).limit(self.max_objects_per_sync).all()
            
            pulled_data = {
                'decks': [],
                'cards': [],
                'reviews': [],
                'metadata': {
                    'last_sync': datetime.utcnow().isoformat(),
                    'changes_count': len(changes),
                    'sync_session_id': sync_session.id
                }
            }
            
            # Process changes
            for change in changes:
                try:
                    if change.object_type == 'deck':
                        obj = Deck.query.get(change.object_id)
                        if obj:
                            pulled_data['decks'].append(obj.to_dict())
                    
                    elif change.object_type == 'card':
                        obj = Card.query.get(change.object_id)
                        if obj:
                            pulled_data['cards'].append(obj.to_dict())
                    
                    elif change.object_type == 'review':
                        obj = ReviewLog.query.get(change.object_id)
                        if obj:
                            pulled_data['reviews'].append(obj.to_dict())
                    
                    # Mark as synced
                    change.synced = True
                    
                except Exception as e:
                    change.sync_error = str(e)
                    sync_session.conflicts += 1
            
            # Update user last sync time
            user.last_sync = datetime.utcnow()
            
            # Complete sync session
            sync_session.completed_at = datetime.utcnow()
            sync_session.status = 'completed'
            sync_session.pulled_objects = len(changes) - sync_session.conflicts
            
            db.session.commit()
            
            return {
                'success': True,
                'data': pulled_data,
                'session': sync_session.to_dict(),
                'conflicts': sync_session.conflicts
            }
            
        except Exception as e:
            db.session.rollback()
            if 'sync_session' in locals():
                sync_session.status = 'failed'
                sync_session.completed_at = datetime.utcnow()
                db.session.commit()
            
            return {'success': False, 'error': str(e)}
    
    def push_changes(self, user, changes):
        """Push local changes from client to server"""
        try:
            # Create sync session
            sync_session = SyncSession(
                user_id=user.id,
                device_id=user.device_id,
                session_token=f"push_{user.id}_{datetime.utcnow().timestamp()}",
                status='in_progress'
            )
            db.session.add(sync_session)
            db.session.flush()
            
            pushed_count = 0
            conflict_count = 0
            
            # Process each change
            for change_data in changes[:self.max_objects_per_sync]:
                try:
                    result = self._apply_change(user, change_data)
                    
                    if result['success']:
                        pushed_count += 1
                    elif result.get('conflict'):
                        conflict_count += 1
                    
                except Exception as e:
                    conflict_count += 1
                    print(f"Error applying change: {e}")
            
            # Complete sync session
            sync_session.completed_at = datetime.utcnow()
            sync_session.status = 'completed'
            sync_session.pushed_objects = pushed_count
            sync_session.conflicts = conflict_count
            
            db.session.commit()
            
            return {
                'success': True,
                'pushed_objects': pushed_count,
                'conflicts': conflict_count,
                'session': sync_session.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            if 'sync_session' in locals():
                sync_session.status = 'failed'
                sync_session.completed_at = datetime.utcnow()
                db.session.commit()
            
            return {'success': False, 'error': str(e)}
    
    def _apply_change(self, user, change_data):
        """Apply a single change with conflict resolution"""
        try:
            object_type = change_data.get('object_type')
            operation = change_data.get('operation')
            data = change_data.get('data', {})
            
            # Conflict resolution: Last-Write-Wins (LWW)
            if object_type == 'deck':
                return self._apply_deck_change(user, operation, data)
            elif object_type == 'card':
                return self._apply_card_change(user, operation, data)
            elif object_type == 'review':
                return self._apply_review_change(user, operation, data)
            else:
                return {'success': False, 'error': f'Unknown object type: {object_type}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _apply_deck_change(self, user, operation, data):
        """Apply deck change"""
        try:
            if operation == 'CREATE':
                deck = Deck(
                    name=data['name'],
                    description=data.get('description', ''),
                    sync_version=1
                )
                db.session.add(deck)
                db.session.flush()
                
                # Log for sync
                self._log_sync_change('deck', deck.id, 'CREATE', user)
                
                return {'success': True, 'object_id': deck.id}
            
            elif operation == 'UPDATE':
                deck_id = data.get('id')
                if not deck_id:
                    return {'success': False, 'error': 'Deck ID required for update'}
                
                deck = Deck.query.get(deck_id)
                if not deck:
                    return {'success': False, 'error': 'Deck not found'}
                
                # LWW: Check timestamps
                if 'updated_at' in data and deck.updated_at:
                    client_time = datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00'))
                    if client_time < deck.updated_at:
                        return {'success': False, 'conflict': True, 'error': 'Conflict detected: server version is newer'}
                
                # Apply updates
                for field in ['name', 'description']:
                    if field in data:
                        setattr(deck, field, data[field])
                
                deck.sync_version += 1
                deck.updated_at = datetime.utcnow()
                
                # Log for sync
                self._log_sync_change('deck', deck.id, 'UPDATE', user)
                
                return {'success': True, 'object_id': deck.id}
            
            elif operation == 'DELETE':
                deck_id = data.get('id')
                if not deck_id:
                    return {'success': False, 'error': 'Deck ID required for delete'}
                
                deck = Deck.query.get(deck_id)
                if deck:
                    db.session.delete(deck)
                    
                    # Log for sync
                    self._log_sync_change('deck', deck.id, 'DELETE', user)
                
                return {'success': True, 'object_id': deck_id}
            
            else:
                return {'success': False, 'error': f'Unknown operation: {operation}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _apply_card_change(self, user, operation, data):
        """Apply card change"""
        try:
            if operation == 'CREATE':
                # Validate deck exists
                deck_id = data.get('deck_id')
                if not deck_id or not Deck.query.get(deck_id):
                    return {'success': False, 'error': 'Valid deck_id required'}
                
                card = Card(
                    deck_id=deck_id,
                    question=data['question'],
                    answer=data['answer'],
                    ease_factor=data.get('ease_factor', 2.5),
                    interval=data.get('interval', 1),
                    repetition=data.get('repetition', 0),
                    sync_version=1
                )
                
                # Set next review date
                if not card.next_review:
                    card.next_review = datetime.utcnow()
                
                db.session.add(card)
                db.session.flush()
                
                # Log for sync
                self._log_sync_change('card', card.id, 'CREATE', user)
                
                return {'success': True, 'object_id': card.id}
            
            elif operation == 'UPDATE':
                card_id = data.get('id')
                if not card_id:
                    return {'success': False, 'error': 'Card ID required for update'}
                
                card = Card.query.get(card_id)
                if not card:
                    return {'success': False, 'error': 'Card not found'}
                
                # LWW: Check timestamps
                if 'updated_at' in data and card.updated_at:
                    client_time = datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00'))
                    if client_time < card.updated_at:
                        return {'success': False, 'conflict': True, 'error': 'Conflict detected: server version is newer'}
                
                # Apply updates (excluding SRS fields from sync)
                for field in ['question', 'answer', 'deck_id']:
                    if field in data:
                        setattr(card, field, data[field])
                
                card.sync_version += 1
                card.updated_at = datetime.utcnow()
                
                # Log for sync
                self._log_sync_change('card', card.id, 'UPDATE', user)
                
                return {'success': True, 'object_id': card.id}
            
            elif operation == 'DELETE':
                card_id = data.get('id')
                if not card_id:
                    return {'success': False, 'error': 'Card ID required for delete'}
                
                card = Card.query.get(card_id)
                if card:
                    db.session.delete(card)
                    
                    # Log for sync
                    self._log_sync_change('card', card.id, 'DELETE', user)
                
                return {'success': True, 'object_id': card_id}
            
            else:
                return {'success': False, 'error': f'Unknown operation: {operation}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _apply_review_change(self, user, operation, data):
        """Apply review change - reviews are append-only"""
        try:
            if operation == 'CREATE':
                # Validate card exists
                card_id = data.get('card_id')
                if not card_id or not Card.query.get(card_id):
                    return {'success': False, 'error': 'Valid card_id required'}
                
                # Calculate SRS update for the card
                card = Card.query.get(card_id)
                grade = data.get('grade', 0)
                
                if not 0 <= grade <= 5:
                    return {'success': False, 'error': 'Grade must be between 0 and 5'}
                
                new_srs = self.calculate_srs_update(card, grade)
                
                # Create review log
                review_log = ReviewLog(
                    card_id=card_id,
                    grade=grade,
                    review_time=datetime.utcnow(),
                    previous_ease_factor=card.ease_factor,
                    previous_interval=card.interval,
                    previous_repetition=card.repetition,
                    new_ease_factor=new_srs['ease_factor'],
                    new_interval=new_srs['interval'],
                    new_repetition=new_srs['repetition'],
                    synced=True  # Mark as synced since this is the source
                )
                
                # Update card SRS values
                card.ease_factor = new_srs['ease_factor']
                card.interval = new_srs['interval']
                card.repetition = new_srs['repetition']
                card.next_review = datetime.utcnow() + timedelta(days=new_srs['interval'])
                card.updated_at = datetime.utcnow()
                
                db.session.add(review_log)
                db.session.flush()
                
                # Log for sync
                self._log_sync_change('review', review_log.id, 'CREATE', user)
                
                return {'success': True, 'object_id': review_log.id}
            
            else:
                return {'success': False, 'error': 'Reviews are append-only, no updates or deletes allowed'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _log_sync_change(self, object_type, object_id, operation, user):
        """Log a change for synchronization"""
        sync_log = SyncLog(
            object_type=object_type,
            object_id=object_id,
            operation=operation,
            device_id=user.device_id,
            created_by=user.email,
            synced=False
        )
        db.session.add(sync_log)
    
    def force_sync_all(self, user):
        """Force sync all pending changes for a user"""
        try:
            # Mark all unsynced changes as synced
            unsynced_changes = SyncLog.query.filter_by(synced=False).all()
            
            for change in unsynced_changes:
                change.synced = True
            
            # Update user last sync time
            user.last_sync = datetime.utcnow()
            
            db.session.commit()
            
            return {
                'success': True,
                'synced_count': len(unsynced_changes),
                'last_sync': user.last_sync.isoformat()
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def get_sync_status(self, user):
        """Get comprehensive sync status for a user"""
        try:
            # Count unsynced changes by type
            unsynced_counts = {}
            for obj_type in ['deck', 'card', 'review']:
                count = SyncLog.query.filter_by(object_type=obj_type, synced=False).count()
                unsynced_counts[obj_type] = count
            
            total_unsynced = sum(unsynced_counts.values())
            
            # Get recent sync sessions
            recent_sessions = SyncSession.query.filter_by(user_id=user.id)\
                .order_by(SyncSession.started_at.desc()).limit(10).all()
            
            return {
                'unsynced_changes': unsynced_counts,
                'total_unsynced': total_unsynced,
                'last_sync': user.last_sync.isoformat() if user.last_sync else None,
                'recent_sessions': [session.to_dict() for session in recent_sessions]
            }
            
        except Exception as e:
            return {'error': str(e)}