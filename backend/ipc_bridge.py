import json
from typing import Dict, Any, Optional
from backend.database.sqlite_manager import SQLiteManager
from backend.core.social.profile_service import ProfileService


class IPCBridge:
    def __init__(self, db_manager: SQLiteManager):
        self.db = db_manager
        self.profile_service = ProfileService(db_manager)
    
    def handle_message(self, channel: str, data: Dict[str, Any]) -> Dict[str, Any]:
        handlers = {
            'profile:get': self._get_profile,
            'profile:upsert': self._upsert_profile,
            'profile:update-privacy': self._update_privacy,
            'profile:update-skills': self._update_skills,
            'profile:aggregate-metrics': self._aggregate_metrics,
            'profile:compare': self._compare_profiles,
            'profile:follow': self._follow_user,
            'profile:unfollow': self._unfollow_user,
            'profile:get-public': self._get_public_profile,
        }
        
        handler = handlers.get(channel)
        if not handler:
            return {'error': f'Unknown channel: {channel}'}
        
        try:
            return handler(data)
        except Exception as e:
            return {'error': str(e)}
    
    def _get_profile(self, data: Dict[str, Any]) -> Dict[str, Any]:
        user_id = data.get('user_id')
        if not user_id:
            return {'error': 'user_id required'}
        
        result = self.profile_service.get_full_profile(user_id, include_private=True)
        return result or {'error': 'Profile not found'}
    
    def _upsert_profile(self, data: Dict[str, Any]) -> Dict[str, Any]:
        user_id = data.get('user_id')
        if not user_id:
            return {'error': 'user_id required'}
        
        return self.profile_service.upsert_profile(
            user_id=user_id,
            bio=data.get('bio'),
            interests=data.get('interests'),
            learning_style=data.get('learning_style')
        )
    
    def _update_privacy(self, data: Dict[str, Any]) -> Dict[str, Any]:
        user_id = data.get('user_id')
        if not user_id:
            return {'error': 'user_id required'}
        
        return self.profile_service.update_privacy_settings(
            user_id=user_id,
            privacy_bio=data.get('privacy_bio'),
            privacy_interests=data.get('privacy_interests'),
            privacy_learning_style=data.get('privacy_learning_style')
        )
    
    def _update_skills(self, data: Dict[str, Any]) -> Dict[str, Any]:
        user_id = data.get('user_id')
        skills = data.get('skills', [])
        
        if not user_id:
            return {'error': 'user_id required'}
        
        result = self.profile_service.update_skills(user_id, skills)
        return {'skills': result}
    
    def _aggregate_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        user_id = data.get('user_id')
        if not user_id:
            return {'error': 'user_id required'}
        
        return self.profile_service.aggregate_metrics(user_id)
    
    def _compare_profiles(self, data: Dict[str, Any]) -> Dict[str, Any]:
        user_id = data.get('user_id')
        compare_with_id = data.get('compare_with_id')
        
        if not user_id or not compare_with_id:
            return {'error': 'user_id and compare_with_id required'}
        
        result = self.profile_service.compare_skills(user_id, compare_with_id)
        return result or {'error': 'One or both users not found'}
    
    def _follow_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        user_id = data.get('user_id')
        handle = data.get('handle')
        
        if not user_id or not handle:
            return {'error': 'user_id and handle required'}
        
        return self.profile_service.follow_user(user_id, handle)
    
    def _unfollow_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        user_id = data.get('user_id')
        handle = data.get('handle')
        
        if not user_id or not handle:
            return {'error': 'user_id and handle required'}
        
        return self.profile_service.unfollow_user(user_id, handle)
    
    def _get_public_profile(self, data: Dict[str, Any]) -> Dict[str, Any]:
        handle = data.get('handle')
        if not handle:
            return {'error': 'handle required'}
        
        result = self.profile_service.get_public_profile(handle)
        return result or {'error': 'Profile not found'}
