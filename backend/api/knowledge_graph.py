from flask import Blueprint, request, jsonify, current_app

bp = Blueprint('knowledge_graph', __name__, url_prefix='/api')

@bp.route('/knowledge-graph/query', methods=['POST'])
def query_graph():
    data = request.json or {}
    filter_depth = data.get('filter_depth', 1)
    search_term = data.get('search_term')
    
    service = current_app.kg_service
    result = service.get_graph_data(filter_depth=filter_depth, search_term=search_term)
    return jsonify(result)

@bp.route('/knowledge-graph/related', methods=['POST'])
def get_related():
    data = request.json or {}
    concept_id = data.get('concept_id')
    if not concept_id:
        return jsonify({'error': 'concept_id is required'}), 400
        
    service = current_app.kg_service
    result = service.get_related_concepts(concept_id)
    return jsonify(result)

@bp.route('/concepts', methods=['POST'])
def create_or_update_concept():
    data = request.json or {}
    service = current_app.kg_service
    
    try:
        if 'id' in data:
            result = service.update_concept(data['id'], name=data.get('name'), description=data.get('description'))
        else:
            result = service.create_concept(name=data.get('name'), description=data.get('description'), chunk_ids=data.get('chunk_ids'))
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/concepts/<concept_id>', methods=['DELETE'])
def delete_concept(concept_id):
    service = current_app.kg_service
    service.delete_concept(concept_id)
    return jsonify({'status': 'ok'})

@bp.route('/relations', methods=['POST'])
def create_relation():
    data = request.json or {}
    service = current_app.kg_service
    
    try:
        result = service.create_relation(
            concept_id_1=data.get('source'),
            concept_id_2=data.get('target'),
            relation_type=data.get('type', 'related'),
            strength=data.get('strength', 0.5)
        )
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/knowledge-graph/integrity-check', methods=['POST'])
def integrity_check():
    service = current_app.kg_service
    result = service.run_integrity_check()
    return jsonify(result)
