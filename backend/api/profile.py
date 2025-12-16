"""
Profile API Blueprint for Social Learning Platform
Provides REST API endpoints for profile management, skills, metrics, and social features
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any
import logging

from backend.core.social.profile_service import ProfileService
from backend.database.sqlite_manager import SQLiteManager

logger = logging.getLogger(__name__)

# Initialize database manager and service
db_manager = SQLiteManager()
profile_service = ProfileService(db_manager)

# Create blueprint
profile_bp = Blueprint('profile', __name__, url_prefix='/api/profile')

@profile_bp.route('/upsert', methods=['POST'])
def upsert_profile():
    """Create or update user profile"""
    try:
        data = request.get_json()
        
        # Required fields
        user_id = data.get('user_id')
        handle = data.get('handle')
        
        if not user_id and not handle:
            return jsonify({
                'success': False,
                'error': 'Either user_id or handle is required'
            }), 400
        
        if handle:
            # Find user by handle
            user = db_manager.get_user_by_handle(handle)
            if user:
                user_id = user['id']
            else:
                # Create new user profile
                bio = data.get('bio', '')
                interests = data.get('interests', [])
                learning_style = data.get('learning_style', '')
                is_private = data.get('is_private', False)
                
                success, message, user_id = profile_service.create_profile(
                    handle=handle,
                    bio=bio,
                    interests=interests,
                    learning_style=learning_style,
                    is_private=is_private
                )
                
                if not success:
                    return jsonify({
                        'success': False,
                        'error': message
                    }), 400
        else:
            # Update existing profile
            bio = data.get('bio', '')
            interests = data.get('interests', [])
            learning_style = data.get('learning_style', '')
            
            success = db_manager.upsert_user_profile(
                user_id=user_id,
                bio=bio,
                interests=interests,
                learning_style=learning_style
            )
            
            if not success:
                return jsonify({
                    'success': False,
                    'error': 'Failed to update profile'
                }), 400
        
        # Get updated profile
        profile = profile_service.get_profile(user_id, include_private=True)
        
        return jsonify({
            'success': True,
            'message': 'Profile upserted successfully',
            'profile': profile
        })
        
    except Exception as e:
        logger.error(f"Error in upsert_profile: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@profile_bp.route('/privacy', methods=['POST'])
def update_privacy():
    """Update profile privacy settings"""
    try:
        data = request.get_json()
        
        user_id = data.get('user_id')
        privacy_settings = data.get('privacy_settings', {})
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        success = profile_service.update_profile_privacy(user_id, privacy_settings)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Privacy settings updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update privacy settings'
            }), 400
            
    except Exception as e:
        logger.error(f"Error in update_privacy: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@profile_bp.route('/skills/update', methods=['POST'])
def update_skills():
    """Update user skills with visibility settings"""
    try:
        data = request.get_json()
        
        user_id = data.get('user_id')
        skills = data.get('skills', [])
        
        if not user_id or not skills:
            return jsonify({
                'success': False,
                'error': 'user_id and skills are required'
            }), 400
        
        # Update each skill
        updated_skills = []
        for skill in skills:
            skill_id = skill.get('skill_id')
            mastery_level = skill.get('mastery_level', 0)
            visibility = skill.get('visibility', True)
            
            if not skill_id:
                continue
            
            success = profile_service.update_skill(user_id, skill_id, mastery_level, visibility)
            
            if success:
                updated_skills.append({
                    'skill_id': skill_id,
                    'mastery_level': mastery_level,
                    'visibility': visibility,
                    'success': True
                })
            else:
                updated_skills.append({
                    'skill_id': skill_id,
                    'success': False
                })
        
        return jsonify({
            'success': True,
            'message': 'Skills updated successfully',
            'updated_skills': updated_skills
        })
        
    except Exception as e:
        logger.error(f"Error in update_skills: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@profile_bp.route('/metrics', methods=['POST'])
def get_metrics():
    """Get user metrics with optional aggregation from logs"""
    try:
        data = request.get_json()
        
        user_id = data.get('user_id')
        update_from_logs = data.get('update_from_logs', False)
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        # Update metrics from logs if requested
        if update_from_logs:
            result = profile_service.update_metrics_from_logs(user_id)
            if not result['success']:
                return jsonify({
                    'success': False,
                    'error': result['error']
                }), 400
        
        # Get current metrics
        metrics = db_manager.get_user_metrics(user_id)
        
        if metrics:
            return jsonify({
                'success': True,
                'metrics': metrics
            })
        else:
            return jsonify({
                'success': True,
                'metrics': None,
                'message': 'No metrics found for user'
            })
            
    except Exception as e:
        logger.error(f"Error in get_metrics: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@profile_bp.route('/compare', methods=['POST'])
def compare_profiles():
    """Compare skills between two users"""
    try:
        data = request.get_json()
        
        user1_id = data.get('user1_id')
        user2_id = data.get('user2_id')
        
        if not user1_id or not user2_id:
            return jsonify({
                'success': False,
                'error': 'user1_id and user2_id are required'
            }), 400
        
        # Validate users exist
        user1 = db_manager.get_user_by_id(user1_id)
        user2 = db_manager.get_user_by_id(user2_id)
        
        if not user1 or not user2:
            return jsonify({
                'success': False,
                'error': 'One or both users not found'
            }), 404
        
        # Compare skills
        comparison = profile_service.compare_skills(user1_id, user2_id)
        
        return jsonify({
            'success': True,
            'comparison': comparison,
            'users': {
                'user1': {'id': user1_id, 'handle': user1['handle']},
                'user2': {'id': user2_id, 'handle': user2['handle']}
            }
        })
        
    except Exception as e:
        logger.error(f"Error in compare_profiles: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@profile_bp.route('/follow', methods=['POST'])
def follow_user():
    """Follow a user"""
    try:
        data = request.get_json()
        
        follower_id = data.get('follower_id')
        followee_id = data.get('followee_id')
        
        if not follower_id or not followee_id:
            return jsonify({
                'success': False,
                'error': 'follower_id and followee_id are required'
            }), 400
        
        success, message = profile_service.follow_user(follower_id, followee_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': message
            })
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400
            
    except Exception as e:
        logger.error(f"Error in follow_user: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@profile_bp.route('/unfollow', methods=['POST'])
def unfollow_user():
    """Unfollow a user"""
    try:
        data = request.get_json()
        
        follower_id = data.get('follower_id')
        followee_id = data.get('followee_id')
        
        if not follower_id or not followee_id:
            return jsonify({
                'success': False,
                'error': 'follower_id and followee_id are required'
            }), 400
        
        success, message = profile_service.unfollow_user(follower_id, followee_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': message
            })
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400
            
    except Exception as e:
        logger.error(f"Error in unfollow_user: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@profile_bp.route('/followers/<int:user_id>', methods=['GET'])
def get_followers(user_id):
    """Get user's followers"""
    try:
        followers = profile_service.get_followers(user_id)
        
        return jsonify({
            'success': True,
            'followers': followers,
            'count': len(followers)
        })
        
    except Exception as e:
        logger.error(f"Error in get_followers: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@profile_bp.route('/following/<int:user_id>', methods=['GET'])
def get_following(user_id):
    """Get users that this user is following"""
    try:
        following = profile_service.get_following(user_id)
        
        return jsonify({
            'success': True,
            'following': following,
            'count': len(following)
        })
        
    except Exception as e:
        logger.error(f"Error in get_following: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@profile_bp.route('/<int:user_id>', methods=['GET'])
def get_profile(user_id):
    """Get user profile (authenticated)"""
    try:
        include_private = request.args.get('include_private', 'false').lower() == 'true'
        
        profile = profile_service.get_profile(user_id, include_private=include_private)
        
        if profile:
            return jsonify({
                'success': True,
                'profile': profile
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Profile not found'
            }), 404
            
    except Exception as e:
        logger.error(f"Error in get_profile: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

# Public API endpoint
@profile_bp.route('/public/<handle>', methods=['GET'])
def get_public_profile(handle):
    """Get public profile by handle (external API)"""
    try:
        profile = profile_service.get_public_profile_by_handle(handle)
        
        if profile:
            return jsonify({
                'success': True,
                'profile': profile
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Public profile not found'
            }), 404
            
    except Exception as e:
        logger.error(f"Error in get_public_profile: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

# Health check endpoint
@profile_bp.route('/health', methods=['GET'])
def health_check():
    """Health check for the profile service"""
    try:
        # Test database connection
        db_manager.execute_query("SELECT 1")
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'service': 'profile',
            'timestamp': str(db_manager.execute_query("SELECT CURRENT_TIMESTAMP")[0])
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e)
        }), 500