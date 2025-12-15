from flask import Blueprint, request, jsonify
import logging

logger = logging.getLogger(__name__)

knowledge_graph_bp = Blueprint('knowledge_graph', __name__, url_prefix='/api/knowledge-graph')


def init_knowledge_graph_routes(app, kg_service):
    """Initialize knowledge graph routes with service dependency."""
    
    @knowledge_graph_bp.route('/query', methods=['POST'])
    def query_graph():
        """Query the knowledge graph with filters."""
        try:
            data = request.get_json() or {}
            user_id = data.get('user_id')
            depth = data.get('depth')
            search_term = data.get('search_term')
            use_webgl = data.get('use_webgl', True)
            
            graph_data = kg_service.get_graph_data(
                user_id=user_id,
                depth=depth,
                search_term=search_term
            )
            
            # Add rendering hint
            graph_data['rendering'] = {
                'use_webgl': use_webgl,
                'mode': 'webgl' if use_webgl else 'canvas'
            }
            
            return jsonify(graph_data), 200
            
        except Exception as e:
            logger.error(f"Error querying graph: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    @knowledge_graph_bp.route('/related', methods=['POST'])
    def get_related():
        """Get related concepts for a given concept."""
        try:
            data = request.get_json() or {}
            concept_id = data.get('concept_id')
            max_depth = data.get('max_depth', 2)
            
            if not concept_id:
                return jsonify({'error': 'concept_id is required'}), 400
            
            related = kg_service.get_related_concepts(concept_id, max_depth)
            return jsonify(related), 200
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            logger.error(f"Error getting related concepts: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    @knowledge_graph_bp.route('/integrity-check', methods=['POST'])
    def integrity_check():
        """Run integrity check on the knowledge graph."""
        try:
            report = kg_service.run_integrity_check()
            return jsonify(report), 200
            
        except Exception as e:
            logger.error(f"Error running integrity check: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    @knowledge_graph_bp.route('/layout', methods=['POST'])
    def save_layout():
        """Save graph layout positions."""
        try:
            data = request.get_json() or {}
            positions = data.get('positions', {})
            
            success = kg_service.save_layout_positions(positions)
            
            if success:
                return jsonify({'status': 'success'}), 200
            else:
                return jsonify({'error': 'Failed to save layout'}), 500
                
        except Exception as e:
            logger.error(f"Error saving layout: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    @knowledge_graph_bp.route('/mastery/aggregate', methods=['POST'])
    def aggregate_mastery():
        """Aggregate mastery from review logs."""
        try:
            data = request.get_json() or {}
            user_id = data.get('user_id')
            concept_id = data.get('concept_id')
            
            if not user_id:
                return jsonify({'error': 'user_id is required'}), 400
            
            mastery_data = kg_service.aggregate_mastery_from_reviews(user_id, concept_id)
            return jsonify(mastery_data), 200
            
        except Exception as e:
            logger.error(f"Error aggregating mastery: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    app.register_blueprint(knowledge_graph_bp)


concepts_bp = Blueprint('concepts', __name__, url_prefix='/api/concepts')


def init_concepts_routes(app, kg_service):
    """Initialize concept CRUD routes."""
    
    @concepts_bp.route('', methods=['POST'])
    def create_concept():
        """Create a new concept."""
        try:
            data = request.get_json() or {}
            name = data.get('name')
            description = data.get('description')
            metadata = data.get('metadata')
            
            if not name:
                return jsonify({'error': 'name is required'}), 400
            
            concept = kg_service.create_concept(name, description, metadata)
            return jsonify(concept), 201
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Error creating concept: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    @concepts_bp.route('/<concept_id>', methods=['PUT'])
    def update_concept(concept_id):
        """Update an existing concept."""
        try:
            data = request.get_json() or {}
            name = data.get('name')
            description = data.get('description')
            metadata = data.get('metadata')
            
            concept = kg_service.update_concept(concept_id, name, description, metadata)
            return jsonify(concept), 200
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            logger.error(f"Error updating concept: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    @concepts_bp.route('/<concept_id>', methods=['DELETE'])
    def delete_concept(concept_id):
        """Delete a concept."""
        try:
            success = kg_service.delete_concept(concept_id)
            
            if success:
                return jsonify({'status': 'success'}), 200
            else:
                return jsonify({'error': 'Concept not found'}), 404
                
        except ValueError as e:
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            logger.error(f"Error deleting concept: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    @concepts_bp.route('/<concept_id>', methods=['GET'])
    def get_concept(concept_id):
        """Get a concept by ID."""
        try:
            concept = kg_service.db.get_concept(concept_id)
            
            if concept:
                return jsonify(concept), 200
            else:
                return jsonify({'error': 'Concept not found'}), 404
                
        except Exception as e:
            logger.error(f"Error getting concept: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    @concepts_bp.route('', methods=['GET'])
    def get_all_concepts():
        """Get all concepts."""
        try:
            concepts = kg_service.db.get_all_concepts()
            return jsonify({'concepts': concepts}), 200
            
        except Exception as e:
            logger.error(f"Error getting concepts: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    app.register_blueprint(concepts_bp)


relations_bp = Blueprint('relations', __name__, url_prefix='/api/relations')


def init_relations_routes(app, kg_service):
    """Initialize relation CRUD routes."""
    
    @relations_bp.route('', methods=['POST'])
    def create_relation():
        """Create a new relation."""
        try:
            data = request.get_json() or {}
            source_id = data.get('source_id')
            target_id = data.get('target_id')
            relation_type = data.get('relation_type', 'related')
            strength = data.get('strength', 1.0)
            metadata = data.get('metadata')
            
            if not source_id or not target_id:
                return jsonify({'error': 'source_id and target_id are required'}), 400
            
            relation = kg_service.create_relation(
                source_id, target_id, relation_type, strength, metadata
            )
            return jsonify(relation), 201
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Error creating relation: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    @relations_bp.route('/<relation_id>', methods=['DELETE'])
    def delete_relation(relation_id):
        """Delete a relation."""
        try:
            success = kg_service.delete_relation(relation_id)
            
            if success:
                return jsonify({'status': 'success'}), 200
            else:
                return jsonify({'error': 'Relation not found'}), 404
                
        except Exception as e:
            logger.error(f"Error deleting relation: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    @relations_bp.route('', methods=['GET'])
    def get_relations():
        """Get relations with optional filters."""
        try:
            concept_id = request.args.get('concept_id')
            relation_type = request.args.get('relation_type')
            
            relations = kg_service.db.get_relations(concept_id, relation_type)
            return jsonify({'relations': relations}), 200
            
        except Exception as e:
            logger.error(f"Error getting relations: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    app.register_blueprint(relations_bp)


def register_all_routes(app, kg_service):
    """Register all knowledge graph related routes."""
    init_knowledge_graph_routes(app, kg_service)
    init_concepts_routes(app, kg_service)
    init_relations_routes(app, kg_service)
