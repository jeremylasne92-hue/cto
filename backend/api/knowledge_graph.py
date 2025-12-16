"""
Knowledge Graph API Endpoints
Flask blueprint for knowledge graph operations
"""
import logging
from flask import Blueprint, request, jsonify, current_app
from typing import Dict, Any, List
import json

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.core.graph.knowledge_graph_service import KnowledgeGraphService

logger = logging.getLogger(__name__)

# Create blueprint
knowledge_graph_bp = Blueprint('knowledge_graph', __name__, url_prefix='/api')

# Initialize service
graph_service = KnowledgeGraphService()


@knowledge_graph_bp.route('/query', methods=['POST'])
def query_knowledge_graph():
    """Query knowledge graph with filtering and search"""
    try:
        data = request.get_json() or {}
        
        # Extract parameters
        depth = data.get('depth', 2)
        search_term = data.get('search_term', '')
        concept_ids = data.get('concept_ids', None)
        user_id = data.get('user_id', 'default')
        use_webgl = data.get('use_webgl', False)
        
        # Get graph data
        graph_data = graph_service.get_concept_graph_data(
            concept_ids=concept_ids,
            user_id=user_id,
            depth=depth
        )
        
        # Apply search filter if provided
        if search_term:
            search_results = graph_service.search_concepts(search_term, limit=50)
            # Filter nodes to only include matching concepts and their neighbors
            matched_ids = [result['concept_id'] for result in search_results]
            
            # Add neighbors of matched concepts
            extended_ids = set(matched_ids)
            for node in graph_data['nodes']:
                if node['id'] in matched_ids:
                    # Add connected concepts
                    for link in graph_data['links']:
                        if link['source'] == node['id']:
                            extended_ids.add(link['target'])
                        if link['target'] == node['id']:
                            extended_ids.add(link['source'])
            
            # Filter graph data
            graph_data['nodes'] = [node for node in graph_data['nodes'] if node['id'] in extended_ids]
            graph_data['links'] = [link for link in graph_data['links'] 
                                 if link['source'] in extended_ids and link['target'] in extended_ids]
            
            # Update stats
            graph_data['stats']['total_concepts'] = len(graph_data['nodes'])
            graph_data['stats']['total_relations'] = len(graph_data['links'])
        
        return jsonify({
            'success': True,
            'data': graph_data,
            'meta': {
                'search_term': search_term,
                'depth': depth,
                'use_webgl': use_webgl,
                'returned_concepts': len(graph_data['nodes']),
                'returned_relations': len(graph_data['links'])
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to query knowledge graph: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@knowledge_graph_bp.route('/related', methods=['POST'])
def find_related_concepts():
    """Find semantically related concepts"""
    try:
        data = request.get_json() or {}
        
        concept_id = data.get('concept_id')
        limit = data.get('limit', 10)
        
        if not concept_id:
            return jsonify({
                'success': False,
                'error': 'concept_id is required'
            }), 400
        
        # Find semantic neighbors
        neighbors = graph_service.find_semantic_neighbors(concept_id, limit)
        
        return jsonify({
            'success': True,
            'data': {
                'concept_id': concept_id,
                'neighbors': neighbors,
                'count': len(neighbors)
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to find related concepts: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@knowledge_graph_bp.route('/concepts', methods=['POST'])
def create_concept():
    """Create a new concept"""
    try:
        data = request.get_json() or {}
        
        # Validate required fields
        name = data.get('name', '').strip()
        if not name:
            return jsonify({
                'success': False,
                'error': 'Name is required'
            }), 400
        
        description = data.get('description', '')
        content = data.get('content', '')
        parent_id = data.get('parent_id')
        
        # Create concept
        concept = graph_service.create_concept(
            name=name,
            description=description,
            content=content,
            parent_id=parent_id
        )
        
        return jsonify({
            'success': True,
            'data': concept
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Failed to create concept: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@knowledge_graph_bp.route('/concepts/<int:concept_id>', methods=['PUT'])
def update_concept(concept_id):
    """Update an existing concept"""
    try:
        data = request.get_json() or {}
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided for update'
            }), 400
        
        # Update concept
        concept = graph_service.update_concept(concept_id, **data)
        
        return jsonify({
            'success': True,
            'data': concept
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Failed to update concept {concept_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@knowledge_graph_bp.route('/concepts/<int:concept_id>', methods=['GET'])
def get_concept(concept_id):
    """Get a specific concept"""
    try:
        concept = graph_service.db_manager.get_concept(concept_id)
        
        if not concept:
            return jsonify({
                'success': False,
                'error': 'Concept not found'
            }), 404
        
        # Get relations for this concept
        relations = graph_service.db_manager.get_concept_relations(concept_id)
        
        return jsonify({
            'success': True,
            'data': {
                'concept': concept,
                'relations': relations
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to get concept {concept_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@knowledge_graph_bp.route('/concepts/<int:concept_id>', methods=['DELETE'])
def delete_concept(concept_id):
    """Delete a concept"""
    try:
        force = request.args.get('force', 'false').lower() == 'true'
        
        # Delete concept
        success = graph_service.delete_concept(concept_id, force=force)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Concept not found or could not be deleted'
            }), 404
        
        return jsonify({
            'success': True,
            'message': f'Concept {concept_id} deleted successfully'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Failed to delete concept {concept_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@knowledge_graph_bp.route('/concepts/<int:concept_id>/relations', methods=['POST'])
def create_relation(concept_id):
    """Create a relation from a concept"""
    try:
        data = request.get_json() or {}
        
        target_concept_id = data.get('target_concept_id')
        relation_type = data.get('relation_type', 'prerequisite')
        strength = data.get('strength', 1.0)
        
        if not target_concept_id:
            return jsonify({
                'success': False,
                'error': 'target_concept_id is required'
            }), 400
        
        # Create relation
        relation = graph_service.create_relation(
            source_concept_id=concept_id,
            target_concept_id=target_concept_id,
            relation_type=relation_type,
            strength=strength
        )
        
        return jsonify({
            'success': True,
            'data': relation
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Failed to create relation from {concept_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@knowledge_graph_bp.route('/integrity-check', methods=['POST'])
def integrity_check():
    """Run integrity checks on the knowledge graph"""
    try:
        data = request.get_json() or {}
        concept_ids = data.get('concept_ids', None)
        
        # Run integrity checks
        results = graph_service.check_integrity(concept_ids)
        
        return jsonify({
            'success': True,
            'data': results
        })
        
    except Exception as e:
        logger.error(f"Failed to run integrity check: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@knowledge_graph_bp.route('/search', methods=['POST'])
def search_concepts():
    """Search concepts by text or semantic similarity"""
    try:
        data = request.get_json() or {}
        
        query = data.get('query', '').strip()
        limit = data.get('limit', 10)
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query is required'
            }), 400
        
        # Search concepts
        results = graph_service.search_concepts(query, limit)
        
        return jsonify({
            'success': True,
            'data': {
                'query': query,
                'results': results,
                'count': len(results)
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to search concepts: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@knowledge_graph_bp.route('/mastery/<user_id>/<int:concept_id>', methods=['POST'])
def update_mastery(user_id, concept_id):
    """Update user's mastery for a concept"""
    try:
        data = request.get_json() or {}
        
        mastery_percentage = data.get('mastery_percentage')
        review_scores = data.get('review_scores', [])
        
        if mastery_percentage is None and not review_scores:
            return jsonify({
                'success': False,
                'error': 'Either mastery_percentage or review_scores is required'
            }), 400
        
        # Update mastery
        if review_scores:
            result = graph_service.aggregate_mastery_from_reviews(user_id, concept_id, review_scores)
        else:
            # Direct mastery update
            graph_service.db_manager.update_mastery(user_id, concept_id, mastery_percentage)
            result = {
                'mastery_percentage': mastery_percentage,
                'review_count': 1,
                'last_updated': None
            }
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Failed to update mastery for user {user_id}, concept {concept_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@knowledge_graph_bp.route('/stats', methods=['GET'])
def get_graph_stats():
    """Get overall graph statistics"""
    try:
        # Get basic counts
        with graph_service.db_manager.db_manager.db_path as conn:
            import sqlite3
            cursor = conn.cursor()
            
            # Count concepts
            cursor.execute('SELECT COUNT(*) FROM concepts')
            concept_count = cursor.fetchone()[0]
            
            # Count relations
            cursor.execute('SELECT COUNT(*) FROM relations')
            relation_count = cursor.fetchone()[0]
            
            # Count users with mastery data
            cursor.execute('SELECT COUNT(DISTINCT user_id) FROM concept_mastery')
            user_count = cursor.fetchone()[0]
            
            # Get mastery distribution
            cursor.execute('''
                SELECT 
                    CASE 
                        WHEN mastery_percentage >= 80 THEN 'green'
                        WHEN mastery_percentage >= 50 THEN 'yellow'
                        WHEN mastery_percentage >= 20 THEN 'orange'
                        ELSE 'gray'
                    END as color_bucket,
                    COUNT(*) as count
                FROM concept_mastery
                GROUP BY color_bucket
            ''')
            mastery_distribution = {row[0]: row[1] for row in cursor.fetchall()}
        
        return jsonify({
            'success': True,
            'data': {
                'total_concepts': concept_count,
                'total_relations': relation_count,
                'total_users': user_count,
                'mastery_distribution': mastery_distribution
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to get graph stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Error handlers
@knowledge_graph_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@knowledge_graph_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500