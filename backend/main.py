from flask import Flask, jsonify
from flask_cors import CORS
import logging
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.sqlite_manager import SQLiteManager
from backend.core.graph.knowledge_graph_service import KnowledgeGraphService, LanceDBManager
from backend.api.knowledge_graph import register_all_routes

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config=None):
    """Application factory."""
    app = Flask(__name__)
    
    # Enable CORS for desktop and mobile clients
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Configuration
    if config:
        app.config.update(config)
    
    db_path = app.config.get('DATABASE_PATH', 'data/knowledge_graph.db')
    
    # Ensure data directory exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Initialize database and services
    db_manager = SQLiteManager(db_path)
    lancedb_manager = LanceDBManager()
    kg_service = KnowledgeGraphService(db_manager, lancedb_manager)
    
    # Store service in app context for access in routes
    app.kg_service = kg_service
    
    # Register routes
    register_all_routes(app, kg_service)
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'knowledge-graph-backend'
        }), 200
    
    @app.route('/', methods=['GET'])
    def root():
        return jsonify({
            'service': 'Knowledge Graph Backend',
            'version': '2.0.0',
            'endpoints': [
                '/health',
                '/api/knowledge-graph/query',
                '/api/knowledge-graph/related',
                '/api/knowledge-graph/integrity-check',
                '/api/knowledge-graph/layout',
                '/api/knowledge-graph/mastery/aggregate',
                '/api/concepts',
                '/api/relations'
            ]
        }), 200
    
    logger.info("Knowledge Graph Backend initialized")
    
    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    
    logger.info(f"Starting server on {host}:{port}")
    app.run(host=host, port=port, debug=True)
