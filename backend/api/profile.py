from flask import Blueprint, request, jsonify
from backend.core.social.profile_service import ProfileService
from backend.database.sqlite_manager import SQLiteManager
from functools import wraps


profile_bp = Blueprint('profile', __name__)

db_manager = None
profile_service = None


def init_profile_api(db: SQLiteManager, gamification_service=None):
    global db_manager, profile_service
    db_manager = db
    profile_service = ProfileService(db, gamification_service)


def require_user_id(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.headers.get('X-User-Id')
        if not user_id:
            user_id = request.json.get('user_id') if request.json else None
        
        if not user_id:
            return jsonify({'error': 'User ID required'}), 401
        
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid user ID'}), 400
        
        return f(user_id=user_id, *args, **kwargs)
    return decorated_function


@profile_bp.route('/api/profile/upsert', methods=['POST'])
@require_user_id
def upsert_profile(user_id):
    data = request.json or {}
    
    try:
        result = profile_service.upsert_profile(
            user_id=user_id,
            bio=data.get('bio'),
            interests=data.get('interests'),
            learning_style=data.get('learning_style')
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@profile_bp.route('/api/profile/privacy', methods=['POST'])
@require_user_id
def update_privacy(user_id):
    data = request.json or {}
    
    try:
        result = profile_service.update_privacy_settings(
            user_id=user_id,
            privacy_bio=data.get('privacy_bio'),
            privacy_interests=data.get('privacy_interests'),
            privacy_learning_style=data.get('privacy_learning_style')
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@profile_bp.route('/api/profile/skills/update', methods=['POST'])
@require_user_id
def update_skills(user_id):
    data = request.json or {}
    skills = data.get('skills', [])
    
    if not isinstance(skills, list):
        return jsonify({'error': 'Skills must be a list'}), 400
    
    try:
        result = profile_service.update_skills(user_id, skills)
        return jsonify({'skills': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@profile_bp.route('/api/profile/metrics', methods=['POST'])
@require_user_id
def update_metrics(user_id):
    try:
        result = profile_service.aggregate_metrics(user_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@profile_bp.route('/api/profile/compare', methods=['POST'])
@require_user_id
def compare_profiles(user_id):
    data = request.json or {}
    compare_with_id = data.get('compare_with_id')
    
    if not compare_with_id:
        return jsonify({'error': 'compare_with_id required'}), 400
    
    try:
        compare_with_id = int(compare_with_id)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid compare_with_id'}), 400
    
    try:
        result = profile_service.compare_skills(user_id, compare_with_id)
        if not result:
            return jsonify({'error': 'One or both users not found'}), 404
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@profile_bp.route('/api/profile/follow', methods=['POST'])
@require_user_id
def follow_user(user_id):
    data = request.json or {}
    followee_handle = data.get('handle')
    
    if not followee_handle:
        return jsonify({'error': 'handle required'}), 400
    
    try:
        result = profile_service.follow_user(user_id, followee_handle)
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@profile_bp.route('/api/profile/unfollow', methods=['POST'])
@require_user_id
def unfollow_user(user_id):
    data = request.json or {}
    followee_handle = data.get('handle')
    
    if not followee_handle:
        return jsonify({'error': 'handle required'}), 400
    
    try:
        result = profile_service.unfollow_user(user_id, followee_handle)
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@profile_bp.route('/public/profile/<handle>', methods=['GET'])
def get_public_profile(handle):
    try:
        result = profile_service.get_public_profile(handle)
        if not result:
            return jsonify({'error': 'Profile not found'}), 404
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@profile_bp.route('/api/profile/me', methods=['GET'])
@require_user_id
def get_my_profile(user_id):
    try:
        result = profile_service.get_full_profile(user_id, include_private=True)
        if not result:
            return jsonify({'error': 'Profile not found'}), 404
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
