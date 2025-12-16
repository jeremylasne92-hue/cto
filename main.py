"""
Main Flask application entry point
Registers all API blueprints and starts the server
"""
import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS

from backend.api.knowledge_graph import knowledge_graph_bp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Enable CORS for desktop app communication
    CORS(app, origins=["*"])
    
    # Register blueprints
    app.register_blueprint(knowledge_graph_bp)
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'knowledge-graph',
            'version': '1.0.0'
        })
    
    # Root endpoint
    @app.route('/')
    def root():
        return jsonify({
            'service': 'Knowledge Graph API',
            'version': '1.0.0',
            'endpoints': {
                'knowledge_graph': '/api/query',
                'create_concept': '/api/concepts',
                'update_concept': '/api/concepts/<id>',
                'delete_concept': '/api/concepts/<id>',
                'create_relation': '/api/concepts/<id>/relations',
                'find_related': '/api/related',
                'integrity_check': '/api/integrity-check',
                'search': '/api/search',
                'update_mastery': '/api/mastery/<user_id>/<concept_id>',
                'stats': '/api/stats'
            }
        })
    
    return app


if __name__ == '__main__':
    app = create_app()
    
    # Get configuration from environment
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    host = os.environ.get('HOST', '0.0.0.0')
    
    logger.info(f"Starting Knowledge Graph API on {host}:{port}")
    
    app.run(
        host=host,
        port=port,
        debug=debug
    )