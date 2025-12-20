"""
Main Flask Application for Social Learning Platform & Knowledge Graph
Wires together all blueprints and initializes the application
"""
import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS

# Import blueprints
from backend.api.profile import profile_bp
from backend.api.knowledge_graph import knowledge_graph_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Enable CORS
    CORS(app, origins=["*"])
    
    # Register blueprints
    app.register_blueprint(profile_bp)
    app.register_blueprint(knowledge_graph_bp)
    
    # Add root route
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Social Learning Platform & Knowledge Graph API',
            'version': '1.0.0',
            'services': ['profile', 'knowledge-graph'],
            'endpoints': {
                'profile': {
                    'base': '/api/profile',
                    'health': '/api/profile/health',
                    'public_profile': '/api/profile/public/<handle>'
                },
                'knowledge_graph': {
                    'query': '/api/query',
                    'concepts': '/api/concepts',
                    'search': '/api/search',
                    'stats': '/api/stats'
                }
            }
        })
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'services': ['profile', 'knowledge-graph'],
            'version': '1.0.0'
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
        
        # Run migrations if available (for knowledge graph)
        if hasattr(db_manager, 'migrate_database'):
            try:
                db_manager.migrate_database()
            except Exception as e:
                logger.warning(f"Migration warning: {e}")

        app.db_manager = db_manager
        app.profile_service = ProfileService(db_manager)
        
        logging.info("Database initialized successfully")
        
    except Exception as e:
        logging.error(f"Failed to initialize database: {e}")
        # We continue even if DB fails to allow basic API health checks if possible
        pass
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # Get configuration from environment
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'true').lower() == 'true'
    host = os.environ.get('HOST', '0.0.0.0')
    
    logger.info(f"Starting API on {host}:{port}")
    
    app.run(host=host, port=port, debug=debug)
