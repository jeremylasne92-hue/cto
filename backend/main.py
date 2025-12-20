import os
import sys
from flask import Flask, jsonify, request
from flask_cors import CORS
from config.hardware_detection import HardwareDetector
from config.tier_selection import TierSelector
from database.sqlite_manager import SQLiteManager
from core.graph.knowledge_graph_service import KnowledgeGraphService
from api.knowledge_graph import bp as knowledge_graph_bp

try:
    from database.lancedb_manager import LanceDBManager
    LANCEDB_AVAILABLE = True
except ImportError:
    LANCEDB_AVAILABLE = False
    LanceDBManager = None

app = Flask(__name__)
CORS(app)

hardware_detector = None
tier_selector = None
sqlite_manager = None
lancedb_manager = None


def initialize_app():
    global hardware_detector, tier_selector, sqlite_manager, lancedb_manager
    
    app_dir = os.path.join(os.path.expanduser('~'), '.cognisphere')
    os.makedirs(app_dir, exist_ok=True)
    os.makedirs(os.path.join(app_dir, 'models'), exist_ok=True)
    os.makedirs(os.path.join(app_dir, 'data'), exist_ok=True)
    os.makedirs(os.path.join(app_dir, 'cache'), exist_ok=True)
    
    hardware_detector = HardwareDetector()
    hardware_info = hardware_detector.detect()
    
    tier_selector = TierSelector(hardware_info)
    selected_tier = tier_selector.select_tier()
    
    sqlite_manager = SQLiteManager(os.path.join(app_dir, 'data', 'cognisphere.db'))
    sqlite_manager.initialize_schema()
    
    if LANCEDB_AVAILABLE:
        lancedb_manager = LanceDBManager(os.path.join(app_dir, 'data', 'embeddings'))
        lancedb_manager.initialize()
    else:
        print("Warning: LanceDB not available, embedding functionality disabled")
    
    app.kg_service = KnowledgeGraphService(sqlite_manager, lancedb_manager)
    app.register_blueprint(knowledge_graph_bp)
    
    print(f"Hardware detected: RAM={hardware_info['ram_gb']:.1f}GB, GPU={hardware_info['has_gpu']}")
    print(f"Selected tier: {selected_tier}")
    print("Backend started successfully")
    sys.stdout.flush()


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Backend is running'}), 200


@app.route('/api/hardware-info', methods=['GET'])
def get_hardware_info():
    if hardware_detector:
        return jsonify(hardware_detector.detect()), 200
    return jsonify({'error': 'Hardware detector not initialized'}), 500


@app.route('/api/tier-info', methods=['GET'])
def get_tier_info():
    if tier_selector:
        return jsonify({'tier': tier_selector.get_current_tier()}), 200
    return jsonify({'error': 'Tier selector not initialized'}), 500


@app.route('/api/database-status', methods=['GET'])
def get_database_status():
    try:
        if sqlite_manager:
            tables = sqlite_manager.get_table_count()
            lancedb_status = 'ok' if LANCEDB_AVAILABLE and lancedb_manager else 'unavailable'
            return jsonify({
                'sqlite': {'status': 'ok', 'tables': tables},
                'lancedb': {'status': lancedb_status}
            }), 200
        return jsonify({'error': 'Database not initialized'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    initialize_app()
    app.run(host='127.0.0.1', port=8765, debug=False)
