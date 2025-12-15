from typing import Optional, Dict, Any, List
from datetime import datetime
from backend.database.sqlite_manager import SQLiteManager


class ProfileService:
    def __init__(self, db_manager: SQLiteManager, gamification_service=None):
        self.db = db_manager
        self.gamification_service = gamification_service

    def create_or_get_user(self, handle: str, visibility_default: str = 'public') -> Dict[str, Any]:
        user = self.db.get_user_by_handle(handle)
        if not user:
            user_id = self.db.create_user(handle, visibility_default)
            user = self.db.get_user_by_id(user_id)
        return user

    def upsert_profile(self, user_id: int, bio: Optional[str] = None,
                      interests: Optional[str] = None,
                      learning_style: Optional[str] = None) -> Dict[str, Any]:
        self.db.upsert_profile(user_id, bio=bio, interests=interests, 
                              learning_style=learning_style)
        return self.get_full_profile(user_id)

    def update_privacy_settings(self, user_id: int, 
                               privacy_bio: Optional[int] = None,
                               privacy_interests: Optional[int] = None,
                               privacy_learning_style: Optional[int] = None) -> Dict[str, Any]:
        self.db.upsert_profile(user_id, 
                              privacy_bio=privacy_bio,
                              privacy_interests=privacy_interests,
                              privacy_learning_style=privacy_learning_style)
        return self.get_full_profile(user_id)

    def update_skills(self, user_id: int, skills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for skill in skills:
            self.db.upsert_skill(
                user_id=user_id,
                skill_id=skill['skill_id'],
                skill_name=skill['skill_name'],
                mastery=skill.get('mastery', 0.0),
                visibility=skill.get('visibility', 'public')
            )
        return self.db.get_user_skills(user_id, include_private=True)

    def aggregate_metrics(self, user_id: int) -> Dict[str, Any]:
        hours_studied = self.db.get_total_study_hours(user_id)
        
        xp_total = 0
        streak_days = 0
        if self.gamification_service:
            try:
                xp_total = self.gamification_service.get_xp(user_id)
                streak_days = self.gamification_service.get_streak(user_id)
            except Exception:
                pass
        
        self.db.upsert_metrics(
            user_id=user_id,
            hours_studied=hours_studied,
            xp_total=xp_total,
            streak_days=streak_days
        )
        
        return self.db.get_metrics(user_id)

    def get_full_profile(self, user_id: int, include_private: bool = True) -> Dict[str, Any]:
        user = self.db.get_user_by_id(user_id)
        if not user:
            return None
        
        profile = self.db.get_profile(user_id)
        metrics = self.db.get_metrics(user_id)
        skills = self.db.get_user_skills(user_id, include_private=include_private)
        followers = self.db.get_followers(user_id)
        following = self.db.get_following(user_id)
        
        return {
            'user': user,
            'profile': profile or {},
            'metrics': metrics or {},
            'skills': skills,
            'followers': followers,
            'following': following,
            'follower_count': len(followers),
            'following_count': len(following)
        }

    def get_public_profile(self, handle: str) -> Optional[Dict[str, Any]]:
        user = self.db.get_user_by_handle(handle)
        if not user:
            return None
        
        user_id = user['id']
        profile = self.db.get_profile(user_id)
        metrics = self.db.get_metrics(user_id)
        skills = self.db.get_user_skills(user_id, include_private=False)
        
        result = {
            'handle': user['handle'],
            'visibility_default': user['visibility_default'],
            'skills': skills
        }
        
        if profile:
            if not profile.get('privacy_bio'):
                result['bio'] = profile.get('bio')
            if not profile.get('privacy_interests'):
                result['interests'] = profile.get('interests')
            if not profile.get('privacy_learning_style'):
                result['learning_style'] = profile.get('learning_style')
        
        if metrics:
            result['metrics'] = {
                'hours_studied': metrics.get('hours_studied', 0.0),
                'xp_total': metrics.get('xp_total', 0),
                'streak_days': metrics.get('streak_days', 0),
                'certifications': metrics.get('certifications', [])
            }
        
        followers = self.db.get_followers(user_id)
        result['follower_count'] = len(followers)
        
        return result

    def compare_skills(self, user_id_1: int, user_id_2: int) -> Dict[str, Any]:
        user1 = self.db.get_user_by_id(user_id_1)
        user2 = self.db.get_user_by_id(user_id_2)
        
        if not user1 or not user2:
            return None
        
        skills1 = {s['skill_id']: s for s in self.db.get_user_skills(user_id_1, include_private=False)}
        skills2 = {s['skill_id']: s for s in self.db.get_user_skills(user_id_2, include_private=False)}
        
        common_skills = []
        user1_unique = []
        user2_unique = []
        
        all_skill_ids = set(skills1.keys()) | set(skills2.keys())
        
        for skill_id in all_skill_ids:
            if skill_id in skills1 and skill_id in skills2:
                common_skills.append({
                    'skill_id': skill_id,
                    'skill_name': skills1[skill_id]['skill_name'],
                    'user1_mastery': skills1[skill_id]['mastery'],
                    'user2_mastery': skills2[skill_id]['mastery'],
                    'difference': skills1[skill_id]['mastery'] - skills2[skill_id]['mastery']
                })
            elif skill_id in skills1:
                user1_unique.append(skills1[skill_id])
            else:
                user2_unique.append(skills2[skill_id])
        
        common_skills.sort(key=lambda x: abs(x['difference']), reverse=True)
        
        return {
            'user1': {'id': user_id_1, 'handle': user1['handle']},
            'user2': {'id': user_id_2, 'handle': user2['handle']},
            'common_skills': common_skills,
            'user1_unique_skills': user1_unique,
            'user2_unique_skills': user2_unique
        }

    def follow_user(self, follower_id: int, followee_handle: str) -> Dict[str, Any]:
        followee = self.db.get_user_by_handle(followee_handle)
        if not followee:
            return {'success': False, 'error': 'User not found'}
        
        if follower_id == followee['id']:
            return {'success': False, 'error': 'Cannot follow yourself'}
        
        followee_profile = self.db.get_profile(followee['id'])
        if followee_profile and followee_profile.get('privacy_bio') == 2:
            return {'success': False, 'error': 'User profile is private'}
        
        success = self.db.add_follow(follower_id, followee['id'])
        if not success:
            return {'success': False, 'error': 'Already following this user'}
        
        return {'success': True, 'followee_id': followee['id']}

    def unfollow_user(self, follower_id: int, followee_handle: str) -> Dict[str, Any]:
        followee = self.db.get_user_by_handle(followee_handle)
        if not followee:
            return {'success': False, 'error': 'User not found'}
        
        success = self.db.remove_follow(follower_id, followee['id'])
        if not success:
            return {'success': False, 'error': 'Not following this user'}
        
        return {'success': True, 'followee_id': followee['id']}

    def is_following(self, follower_id: int, followee_id: int) -> bool:
        return self.db.is_following(follower_id, followee_id)
