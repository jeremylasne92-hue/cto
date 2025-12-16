"""
Profile Service for Social Learning Platform
Handles profile CRUD, metrics aggregation, skill comparison, and follow/unfollow logic
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from backend.database.sqlite_manager import SQLiteManager

logger = logging.getLogger(__name__)

class ProfileService:
    def __init__(self, db_manager: SQLiteManager):
        self.db = db_manager
    
    # Profile CRUD Operations
    def create_profile(self, handle: str, bio: str = '', interests: List[str] = None,
                      learning_style: str = '', is_private: bool = False) -> Tuple[bool, str, Optional[int]]:
        """Create a new user profile"""
        try:
            # Check if user already exists
            existing_user = self.db.get_user_by_handle(handle)
            if existing_user:
                return False, "User handle already exists", None
            
            # Create user
            user_id = self.db.create_user(handle, is_private)
            
            # Create profile
            success = self.db.upsert_user_profile(
                user_id=user_id,
                bio=bio,
                interests=interests or [],
                learning_style=learning_style,
                privacy_bio=True,
                privacy_interests=True,
                privacy_learning_style=True
            )
            
            if success:
                # Initialize metrics
                self.db.update_user_metrics(user_id)
                return True, "Profile created successfully", user_id
            else:
                return False, "Failed to create profile", None
                
        except Exception as e:
            logger.error(f"Error creating profile for handle {handle}: {e}")
            return False, f"Error creating profile: {str(e)}", None
    
    def get_profile(self, user_id: int, include_private: bool = False) -> Optional[Dict]:
        """Get user profile with optional private data"""
        try:
            # Get user info
            user = self.db.get_user_by_id(user_id)
            if not user:
                return None
            
            # Get profile
            profile = self.db.get_user_profile(user_id, include_private)
            if not profile:
                return None
            
            # Get skills
            skills = self.db.get_user_skills(user_id, public_only=not include_private)
            
            # Get metrics
            metrics = self.db.get_user_metrics(user_id)
            
            # Combine all data
            result = {
                'user': user,
                'profile': profile,
                'skills': skills,
                'metrics': metrics or {}
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting profile for user {user_id}: {e}")
            return None
    
    def update_profile_privacy(self, user_id: int, privacy_settings: Dict[str, bool]) -> bool:
        """Update profile privacy settings"""
        try:
            # Get current profile
            profile = self.db.get_user_profile(user_id, include_private=True)
            if not profile:
                return False
            
            # Update privacy settings
            success = self.db.upsert_user_profile(
                user_id=user_id,
                bio=profile.get('bio', ''),
                interests=profile.get('interests', []),
                learning_style=profile.get('learning_style', ''),
                privacy_bio=privacy_settings.get('privacy_bio', True),
                privacy_interests=privacy_settings.get('privacy_interests', True),
                privacy_learning_style=privacy_settings.get('privacy_learning_style', True)
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating privacy for user {user_id}: {e}")
            return False
    
    # Metrics Aggregation
    def update_metrics_from_logs(self, user_id: int, days_back: int = 30) -> Dict[str, Any]:
        """Update user metrics from review logs"""
        try:
            # Calculate date range
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days_back)
            
            # Aggregate from logs
            aggregated = self.db.aggregate_metrics_from_logs(
                user_id, 
                start_date.isoformat(), 
                end_date.isoformat()
            )
            
            # Get current metrics
            current_metrics = self.db.get_user_metrics(user_id) or {}
            
            # Update metrics
            updates = {
                'hours_studied': aggregated.get('total_hours', 0) or 0,
                'xp_total': (current_metrics.get('xp_total', 0) or 0) + 
                           (aggregated.get('total_xp', 0) or 0)
            }
            
            # Calculate streak days
            streak_days = self._calculate_streak(user_id)
            updates['streak_days'] = streak_days
            
            # Update in database
            success = self.db.update_user_metrics(user_id, **updates)
            
            if success:
                updated_metrics = self.db.get_user_metrics(user_id)
                return {
                    'success': True,
                    'metrics': updated_metrics,
                    'aggregated_from_logs': aggregated
                }
            else:
                return {'success': False, 'error': 'Failed to update metrics'}
                
        except Exception as e:
            logger.error(f"Error updating metrics from logs for user {user_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    def _calculate_streak(self, user_id: int, max_days: int = 365) -> int:
        """Calculate current study streak"""
        try:
            query = '''
                SELECT study_date, COUNT(*) as sessions
                FROM review_logs 
                WHERE user_id = ? AND study_date >= DATE('now', '-{} days')
                GROUP BY study_date
                ORDER BY study_date DESC
            '''.format(max_days)
            
            results = self.db.execute_query(query, (user_id,))
            
            if not results:
                return 0
            
            # Check if last study date is today or yesterday
            last_study_date = datetime.strptime(results[0]['study_date'], '%Y-%m-%d').date()
            today = datetime.now().date()
            
            if last_study_date < today - timedelta(days=1):
                return 0  # Streak broken
            
            # Count consecutive days
            streak = 0
            current_date = today
            
            for result in results:
                study_date = datetime.strptime(result['study_date'], '%Y-%m-%d').date()
                
                if study_date == current_date:
                    streak += 1
                    current_date -= timedelta(days=1)
                elif study_date == current_date + timedelta(days=1):
                    # Gap of one day (weekend), continue
                    streak += 1
                    current_date -= timedelta(days=1)
                else:
                    break
            
            return streak
            
        except Exception as e:
            logger.error(f"Error calculating streak for user {user_id}: {e}")
            return 0
    
    # Skills Management
    def update_skill(self, user_id: int, skill_id: str, mastery_level: int, 
                    visibility: bool = True) -> bool:
        """Update user skill with visibility"""
        try:
            return self.db.update_user_skill(user_id, skill_id, mastery_level, visibility)
        except Exception as e:
            logger.error(f"Error updating skill {skill_id} for user {user_id}: {e}")
            return False
    
    def compare_skills(self, user1_id: int, user2_id: int) -> Dict[str, Any]:
        """Compare skills between two users"""
        try:
            # Get skills for both users (public only)
            user1_skills = self.db.get_user_skills(user1_id, public_only=True)
            user2_skills = self.db.get_user_skills(user2_id, public_only=True)
            
            # Convert to dictionaries for easier comparison
            user1_skill_dict = {skill['skill_id']: skill['mastery_level'] for skill in user1_skills}
            user2_skill_dict = {skill['skill_id']: skill['mastery_level'] for skill in user2_skills}
            
            # Find common, unique, and skill gaps
            all_skills = set(user1_skill_dict.keys()) | set(user2_skill_dict.keys())
            
            common_skills = []
            user1_unique = []
            user2_unique = []
            skill_comparison = []
            
            for skill in all_skills:
                user1_level = user1_skill_dict.get(skill, 0)
                user2_level = user2_skill_dict.get(skill, 0)
                
                if user1_level > 0 and user2_level > 0:
                    common_skills.append({
                        'skill_id': skill,
                        'user1_level': user1_level,
                        'user2_level': user2_level,
                        'difference': user1_level - user2_level
                    })
                elif user1_level > 0:
                    user1_unique.append({
                        'skill_id': skill,
                        'mastery_level': user1_level
                    })
                elif user2_level > 0:
                    user2_unique.append({
                        'skill_id': skill,
                        'mastery_level': user2_level
                    })
                
                skill_comparison.append({
                    'skill_id': skill,
                    'user1_level': user1_level,
                    'user2_level': user2_level,
                    'both_have': user1_level > 0 and user2_level > 0
                })
            
            # Calculate learning recommendations
            recommendations = self._generate_learning_recommendations(
                user1_skill_dict, user2_skill_dict, user1_id, user2_id
            )
            
            return {
                'common_skills': common_skills,
                'user1_unique_skills': user1_unique,
                'user2_unique_skills': user2_unique,
                'skill_comparison': skill_comparison,
                'recommendations': recommendations,
                'summary': {
                    'total_common': len(common_skills),
                    'user1_unique_count': len(user1_unique),
                    'user2_unique_count': len(user2_unique),
                    'overlap_percentage': len(common_skills) / len(all_skills) * 100 if all_skills else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error comparing skills between users {user1_id} and {user2_id}: {e}")
            return {'error': str(e)}
    
    def _generate_learning_recommendations(self, user1_skills: Dict[str, int], 
                                         user2_skills: Dict[str, int],
                                         user1_id: int, user2_id: int) -> List[Dict]:
        """Generate learning recommendations based on skill comparison"""
        recommendations = []
        
        # Find skills where one user is significantly better
        for skill, user1_level in user1_skills.items():
            user2_level = user2_skills.get(skill, 0)
            
            if user1_level > user2_level + 2:  # User 1 is much better
                recommendations.append({
                    'skill_id': skill,
                    'recommended_for': user2_id,
                    'recommended_by': user1_id,
                    'reason': f'{user1_skills[skill] - user2_level} levels ahead',
                    'type': 'learning_opportunity'
                })
            elif user2_level > user1_level + 2:  # User 2 is much better
                recommendations.append({
                    'skill_id': skill,
                    'recommended_for': user1_id,
                    'recommended_by': user2_id,
                    'reason': f'{user2_level - user1_level} levels behind',
                    'type': 'learning_opportunity'
                })
        
        # Sort by most significant differences
        recommendations.sort(key=lambda x: abs(int(x['reason'].split()[0])), reverse=True)
        
        return recommendations[:5]  # Return top 5 recommendations
    
    # Follow/Unfollow Logic
    def follow_user(self, follower_id: int, followee_id: int) -> Tuple[bool, str]:
        """Follow a user with privacy checks"""
        try:
            if follower_id == followee_id:
                return False, "Cannot follow yourself"
            
            # Check if already following
            followers = self.db.get_user_followers(followee_id)
            existing_follow = any(f['id'] == follower_id for f in followers)
            if existing_follow:
                return False, "Already following this user"
            
            # Get followee info for privacy checks
            followee = self.db.get_user_by_id(followee_id)
            if not followee:
                return False, "User not found"
            
            # For private users, we could implement follow requests here
            # For now, we'll allow following but log it
            if followee['is_private']:
                logger.info(f"Following private user {followee_id} by {follower_id}")
            
            # Create follow relationship
            success = self.db.follow_user(follower_id, followee_id)
            if success:
                return True, "Successfully followed user"
            else:
                return False, "Failed to follow user"
                
        except Exception as e:
            logger.error(f"Error following user {followee_id} by {follower_id}: {e}")
            return False, f"Error following user: {str(e)}"
    
    def unfollow_user(self, follower_id: int, followee_id: int) -> Tuple[bool, str]:
        """Unfollow a user"""
        try:
            success = self.db.unfollow_user(follower_id, followee_id)
            if success:
                return True, "Successfully unfollowed user"
            else:
                return False, "Not following this user"
                
        except Exception as e:
            logger.error(f"Error unfollowing user {followee_id} by {follower_id}: {e}")
            return False, f"Error unfollowing user: {str(e)}"
    
    def get_followers(self, user_id: int) -> List[Dict]:
        """Get user's followers with basic info"""
        try:
            followers = self.db.get_user_followers(user_id)
            
            # Enhance with profile data
            for follower in followers:
                profile = self.db.get_user_profile(follower['id'])
                if profile:
                    follower['profile_summary'] = {
                        'bio': profile.get('bio', '')[:100] + '...' if len(profile.get('bio', '')) > 100 else profile.get('bio', ''),
                        'interests': profile.get('interests', [])[:3]  # First 3 interests
                    }
            
            return followers
            
        except Exception as e:
            logger.error(f"Error getting followers for user {user_id}: {e}")
            return []
    
    def get_following(self, user_id: int) -> List[Dict]:
        """Get users that this user is following"""
        try:
            following = self.db.get_user_following(user_id)
            
            # Enhance with profile data
            for followed_user in following:
                profile = self.db.get_user_profile(followed_user['id'])
                if profile:
                    followed_user['profile_summary'] = {
                        'bio': profile.get('bio', '')[:100] + '...' if len(profile.get('bio', '')) > 100 else profile.get('bio', ''),
                        'interests': profile.get('interests', [])[:3]
                    }
            
            return following
            
        except Exception as e:
            logger.error(f"Error getting following for user {user_id}: {e}")
            return []
    
    # Public API methods
    def get_public_profile_by_handle(self, handle: str) -> Optional[Dict]:
        """Get public profile by handle (external API)"""
        try:
            profile = self.db.get_public_profile(handle)
            if not profile:
                return None
            
            # Get public skills
            skills = self.db.get_public_skills(handle)
            
            # Combine data
            result = {
                'handle': profile['handle'],
                'bio': profile['bio'] or '',
                'interests': profile['interests'] or [],
                'learning_style': profile['learning_style'] or '',
                'metrics': {
                    'hours_studied': profile['hours_studied'] or 0,
                    'xp_total': profile['xp_total'] or 0,
                    'streak_days': profile['streak_days'] or 0,
                    'certifications': profile['certifications'] or []
                },
                'skills': skills,
                'social': {
                    'followers_count': profile['followers_count'] or 0,
                    'following_count': profile['following_count'] or 0
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting public profile for handle {handle}: {e}")
            return None
    
    def is_following(self, follower_id: int, followee_id: int) -> bool:
        """Check if user is following another user"""
        try:
            followers = self.db.get_user_followers(followee_id)
            return any(f['id'] == follower_id for f in followers)
        except Exception as e:
            logger.error(f"Error checking follow relationship: {e}")
            return False