"""
Authentication service for flashcard sync engine
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps

from ..models import User, db

class AuthService:
    """Authentication service"""
    
    def __init__(self, app=None):
        self.secret_key = None  # Will be set later
        self.token_expire_hours = 24  # Default value
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize service with app context"""
        self.secret_key = app.config.get('SECRET_KEY', 'dev-secret-key')
        self.token_expire_hours = app.config.get('SYNC_TOKEN_EXPIRE_HOURS', 24)
    
    def register(self, email, password, device_id=None):
        """Register a new user"""
        try:
            # Check if user already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return {'success': False, 'error': 'User already exists'}
            
            # Hash password
            password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            
            # Generate device ID if not provided
            if not device_id:
                device_id = f"device-{email.split('@')[0]}-{datetime.utcnow().strftime('%Y%m%d')}"
            
            # Create user
            user = User(
                email=email,
                password_hash=password_hash,
                device_id=device_id,
                last_login=datetime.utcnow()
            )
            
            db.session.add(user)
            db.session.commit()
            
            # Generate token
            token = self._generate_token(user)
            
            return {
                'success': True,
                'user': user.to_dict(),
                'token': token,
                'expires_at': (datetime.utcnow() + timedelta(hours=self.token_expire_hours)).isoformat()
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def login(self, email, password):
        """Login user"""
        try:
            # Find user
            user = User.query.filter_by(email=email).first()
            if not user:
                return {'success': False, 'error': 'Invalid credentials'}
            
            # Check password
            if not bcrypt.check_password_hash(user.password_hash, password):
                return {'success': False, 'error': 'Invalid credentials'}
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Generate token
            token = self._generate_token(user)
            
            return {
                'success': True,
                'user': user.to_dict(),
                'token': token,
                'expires_at': (datetime.utcnow() + timedelta(hours=self.token_expire_hours)).isoformat()
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def verify_token(self, token):
        """Verify authentication token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            user = User.query.get(payload['user_id'])
            
            if not user:
                return {'valid': False, 'error': 'User not found'}
            
            return {
                'valid': True,
                'user': user.to_dict()
            }
            
        except jwt.ExpiredSignatureError:
            return {'valid': False, 'error': 'Token expired'}
        except jwt.InvalidTokenError:
            return {'valid': False, 'error': 'Invalid token'}
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    def get_current_user(self):
        """Get current user from token"""
        from flask import request
        
        # Try to get token from header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise ValueError("No valid authorization header")
        
        token = auth_header.split(' ')[1]
        
        # Verify token
        result = self.verify_token(token)
        if not result['valid']:
            raise ValueError(result['error'])
        
        return User.query.get(result['user']['id'])
    
    def require_auth(self, f):
        """Decorator to require authentication"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request, jsonify
            try:
                user = self.get_current_user()
                # Add user to kwargs so it can be accessed in the decorated function
                kwargs['current_user'] = user
                return f(*args, **kwargs)
            except ValueError as e:
                return jsonify({'error': str(e)}), 401
            except Exception as e:
                return jsonify({'error': 'Authentication failed'}), 401
        
        return decorated_function
    
    def _generate_token(self, user):
        """Generate JWT token for user"""
        payload = {
            'user_id': user.id,
            'email': user.email,
            'device_id': user.device_id,
            'exp': datetime.utcnow() + timedelta(hours=self.token_expire_hours)
        }
        
        return jwt.encode(payload, self.secret_key, algorithm='HS256')