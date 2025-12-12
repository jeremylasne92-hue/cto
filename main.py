"""
SRS Engine - Main Flask Application

Entry point for the Spaced Repetition System with FSRS-5 algorithm.
"""

import os
from flask import Flask, jsonify
from models import db
from database import init_db
from api import register_blueprints
import config


def create_app(config_name='development'):
    """
    Create and configure Flask application.
    
    Args:
        config_name: Configuration environment (development, testing, production)
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['JSON_SORT_KEYS'] = False
    
    # Initialize database
    db.init_app(app)
    
    # Initialize database tables
    with app.app_context():
        init_db(app)
    
    # Register API blueprints
    register_blueprints(app)
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({
            'success': True,
            'status': 'healthy',
            'service': 'SRS Engine - FSRS-5',
            'version': '1.0.0'
        }), 200
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def index():
        return jsonify({
            'service': 'SRS Engine - FSRS-5 Algorithm',
            'version': '1.0.0',
            'description': 'Spaced Repetition System with optimal scheduling',
            'endpoints': {
                'decks': '/api/decks',
                'cards': '/api/cards',
                'reviews': '/api/reviews',
                'sessions': '/api/sessions',
                'health': '/health',
            }
        }), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Not found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    
    # Run development server
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    port = int(os.environ.get('PORT', 5000))
    
    print(f"Starting SRS Engine (FSRS-5)")
    print(f"Debug mode: {debug}")
    print(f"Port: {port}")
    
    app.run(debug=debug, host='0.0.0.0', port=port)
