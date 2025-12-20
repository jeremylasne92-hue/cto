"""
Main Flask Application for Social Learning Platform
Wires together all blueprints and initializes the application
"""

import logging
from flask import Flask, jsonify
from flask_cors import CORS

# Import blueprints
from backend.api.profile import profile_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Enable CORS
    CORS(app, origins=["http://localhost:3000", "http://localhost:19006"])
    
    # Register blueprints
    app.register_blueprint(profile_bp)
    
    # Add root route
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Social Learning Platform API',
            'version': '1.0.0',
            'endpoints': {
                'profile': '/api/profile',
                'health': '/api/profile/health',
                'public_profile': '/api/profile/public/<handle>'
            }
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Endpoint not found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
    
    # Initialize database
    try:
        # Import database manager to initialize it
        from backend.database.sqlite_manager import SQLiteManager
        from backend.core.social.profile_service import ProfileService
        
        # Test database connection
        db_manager = SQLiteManager()
        app.db_manager = db_manager
        app.profile_service = ProfileService(db_manager)
        
        logging.info("Database initialized successfully")
        
    except Exception as e:
        logging.error(f"Failed to initialize database: {e}")
        raise
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)