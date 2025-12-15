import logging
from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime, timezone
import uuid
from collections import defaultdict

logger = logging.getLogger(__name__)


class KnowledgeGraphService:
    """Core service for knowledge graph operations with validation and integrity checks."""
    
    def __init__(self, db_manager, lancedb_manager=None):
        self.db = db_manager
        self.lancedb = lancedb_manager
    
    def create_concept(self, name: str, description: str = None, metadata: Dict = None) -> Dict:
        """Create a new concept with validation."""
        # Reject duplicate names
        existing_concepts = self.db.get_all_concepts()
        if any(c['name'].lower() == name.lower() for c in existing_concepts):
            raise ValueError(f"Concept with name '{name}' already exists")
        
        concept_id = str(uuid.uuid4())
        success = self.db.create_concept(concept_id, name, description, metadata)
        
        if not success:
            raise RuntimeError(f"Failed to create concept '{name}'")
        
        # Index in LanceDB if available
        if self.lancedb:
            try:
                self.lancedb.index_concept(concept_id, name, description)
            except Exception as e:
                logger.warning(f"Failed to index concept in LanceDB: {e}")
        
        return self.db.get_concept(concept_id)
    
    def update_concept(self, concept_id: str, name: str = None, 
                      description: str = None, metadata: Dict = None) -> Dict:
        """Update a concept with validation."""
        concept = self.db.get_concept(concept_id)
        if not concept:
            raise ValueError(f"Concept {concept_id} not found")
        
        # Check for duplicate names if name is being changed
        if name and name.lower() != concept['name'].lower():
            existing_concepts = self.db.get_all_concepts()
            if any(c['name'].lower() == name.lower() and c['id'] != concept_id 
                   for c in existing_concepts):
                raise ValueError(f"Concept with name '{name}' already exists")
        
        success = self.db.update_concept(concept_id, name, description, metadata)
        if not success:
            raise RuntimeError(f"Failed to update concept {concept_id}")
        
        # Update index in LanceDB if available
        if self.lancedb and (name or description):
            try:
                self.lancedb.update_concept(concept_id, name or concept['name'], 
                                          description or concept['description'])
            except Exception as e:
                logger.warning(f"Failed to update concept in LanceDB: {e}")
        
        return self.db.get_concept(concept_id)
    
    def delete_concept(self, concept_id: str) -> bool:
        """Delete a concept and validate no orphan relations are created."""
        concept = self.db.get_concept(concept_id)
        if not concept:
            raise ValueError(f"Concept {concept_id} not found")
        
        # Relations will be cascade deleted by foreign key constraints
        success = self.db.delete_concept(concept_id)
        
        # Remove from LanceDB if available
        if self.lancedb and success:
            try:
                self.lancedb.delete_concept(concept_id)
            except Exception as e:
                logger.warning(f"Failed to delete concept from LanceDB: {e}")
        
        return success
    
    def create_relation(self, source_id: str, target_id: str, 
                       relation_type: str, strength: float = 1.0, 
                       metadata: Dict = None) -> Dict:
        """Create a relation with validation to prevent orphans."""
        # Validate that both concepts exist
        source = self.db.get_concept(source_id)
        target = self.db.get_concept(target_id)
        
        if not source:
            raise ValueError(f"Source concept {source_id} not found")
        if not target:
            raise ValueError(f"Target concept {target_id} not found")
        
        # Prevent self-loops (optional constraint)
        if source_id == target_id:
            raise ValueError("Cannot create relation from concept to itself")
        
        relation_id = str(uuid.uuid4())
        success = self.db.create_relation(
            relation_id, source_id, target_id, relation_type, strength, metadata
        )
        
        if not success:
            raise RuntimeError("Failed to create relation")
        
        # Recalculate relation strengths if needed
        self._recalculate_relation_strength(relation_id)
        
        return {
            'id': relation_id,
            'source_id': source_id,
            'target_id': target_id,
            'relation_type': relation_type,
            'strength': strength
        }
    
    def delete_relation(self, relation_id: str) -> bool:
        """Delete a relation."""
        return self.db.delete_relation(relation_id)
    
    def get_graph_data(self, user_id: int = None, depth: int = None, 
                      search_term: str = None) -> Dict:
        """Get graph data formatted for D3 visualization."""
        concepts = self.db.get_all_concepts()
        relations = self.db.get_relations()
        
        # Filter by search term if provided
        if search_term:
            search_lower = search_term.lower()
            concepts = [c for c in concepts if search_lower in c['name'].lower() or 
                       (c.get('description') and search_lower in c['description'].lower())]
        
        # Get mastery data if user_id provided
        mastery_map = {}
        if user_id:
            mastery_records = self.db.get_concept_mastery(user_id)
            mastery_map = {m['concept_id']: m for m in mastery_records}
        
        # Get layout positions
        layout_positions = self.db.get_layout_positions()
        
        # Build nodes with mastery colors
        nodes = []
        concept_ids = {c['id'] for c in concepts}
        
        for concept in concepts:
            node = {
                'id': concept['id'],
                'name': concept['name'],
                'description': concept.get('description', ''),
                'metadata': concept.get('metadata', '{}')
            }
            
            # Add mastery data and color
            if concept['id'] in mastery_map:
                mastery = mastery_map[concept['id']]
                node['mastery'] = mastery['mastery_percent']
                node['review_count'] = mastery['review_count']
                node['last_assessed'] = mastery['last_assessed']
                node['color'] = self._get_mastery_color(mastery['mastery_percent'])
            else:
                node['mastery'] = 0
                node['review_count'] = 0
                node['color'] = self._get_mastery_color(0)
            
            # Add cached position if available
            if concept['id'] in layout_positions:
                pos = layout_positions[concept['id']]
                node['x'] = pos['x']
                node['y'] = pos['y']
                node['z'] = pos['z']
            
            nodes.append(node)
        
        # Build edges with prerequisite/dependency tags
        edges = []
        for relation in relations:
            # Only include relations where both concepts are in filtered set
            if relation['source_id'] in concept_ids and relation['target_id'] in concept_ids:
                edge = {
                    'id': relation['id'],
                    'source': relation['source_id'],
                    'target': relation['target_id'],
                    'type': relation['relation_type'],
                    'strength': relation.get('strength', 1.0),
                    'metadata': relation.get('metadata', '{}')
                }
                
                # Tag prerequisites and dependencies
                if relation['relation_type'] == 'prerequisite':
                    edge['is_prerequisite'] = True
                elif relation['relation_type'] == 'dependency':
                    edge['is_dependency'] = True
                
                edges.append(edge)
        
        # Apply depth filter if specified
        if depth is not None and depth > 0:
            nodes, edges = self._apply_depth_filter(nodes, edges, depth)
        
        return {
            'nodes': nodes,
            'edges': edges,
            'metadata': {
                'total_concepts': len(nodes),
                'total_relations': len(edges),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        }
    
    def get_related_concepts(self, concept_id: str, max_depth: int = 2) -> Dict:
        """Get semantically related concepts using LanceDB if available."""
        concept = self.db.get_concept(concept_id)
        if not concept:
            raise ValueError(f"Concept {concept_id} not found")
        
        # Get direct relations from graph
        relations = self.db.get_relations(concept_id=concept_id)
        direct_neighbors = set()
        
        for rel in relations:
            if rel['source_id'] == concept_id:
                direct_neighbors.add(rel['target_id'])
            else:
                direct_neighbors.add(rel['source_id'])
        
        result = {
            'concept': concept,
            'direct_neighbors': [self.db.get_concept(cid) for cid in direct_neighbors],
            'semantic_neighbors': []
        }
        
        # Get semantic neighbors from LanceDB
        if self.lancedb:
            try:
                semantic_ids = self.lancedb.find_similar_concepts(
                    concept_id, limit=10, exclude_ids=list(direct_neighbors | {concept_id})
                )
                result['semantic_neighbors'] = [
                    self.db.get_concept(cid) for cid in semantic_ids if self.db.get_concept(cid)
                ]
            except Exception as e:
                logger.warning(f"Failed to get semantic neighbors: {e}")
        
        return result
    
    def aggregate_mastery_from_reviews(self, user_id: int, concept_id: str = None) -> Dict:
        """Aggregate mastery statistics from review logs."""
        if concept_id:
            concept_ids = [concept_id]
        else:
            concepts = self.db.get_all_concepts()
            concept_ids = [c['id'] for c in concepts]
        
        results = {}
        
        for cid in concept_ids:
            reviews = self.db.get_review_logs(user_id=user_id, concept_id=cid, limit=1000)
            
            if not reviews:
                results[cid] = {
                    'mastery_percent': 0.0,
                    'review_count': 0,
                    'last_assessed': None
                }
                continue
            
            # Calculate mastery using weighted recent reviews
            total_reviews = len(reviews)
            recent_reviews = reviews[:min(20, total_reviews)]
            correct_count = sum(1 for r in recent_reviews if r['correct'])
            
            mastery_percent = (correct_count / len(recent_reviews)) * 100 if recent_reviews else 0
            
            results[cid] = {
                'mastery_percent': round(mastery_percent, 2),
                'review_count': total_reviews,
                'last_assessed': reviews[0]['timestamp'] if reviews else None
            }
            
            # Update database
            self.db.update_concept_mastery(
                user_id, cid, mastery_percent, total_reviews
            )
        
        return results
    
    def run_integrity_check(self) -> Dict:
        """Run batch integrity checks on the graph."""
        issues = {
            'orphan_relations': [],
            'cycles': [],
            'broken_refs': [],
            'duplicate_ids': [],
            'self_loops': []
        }
        
        concepts = self.db.get_all_concepts()
        relations = self.db.get_relations()
        
        concept_ids = {c['id'] for c in concepts}
        seen_ids = set()
        
        # Check for duplicate concept IDs
        for concept in concepts:
            if concept['id'] in seen_ids:
                issues['duplicate_ids'].append(concept['id'])
            seen_ids.add(concept['id'])
        
        # Check relations for issues
        for relation in relations:
            source_id = relation['source_id']
            target_id = relation['target_id']
            
            # Check for orphan relations
            if source_id not in concept_ids:
                issues['orphan_relations'].append({
                    'relation_id': relation['id'],
                    'missing_concept': source_id,
                    'type': 'source'
                })
            if target_id not in concept_ids:
                issues['orphan_relations'].append({
                    'relation_id': relation['id'],
                    'missing_concept': target_id,
                    'type': 'target'
                })
            
            # Check for self-loops
            if source_id == target_id:
                issues['self_loops'].append(relation['id'])
        
        # Check for cycles (simple DFS-based cycle detection)
        cycles = self._detect_cycles(concepts, relations)
        issues['cycles'] = cycles
        
        return {
            'has_issues': any(len(v) > 0 for v in issues.values()),
            'issues': issues,
            'summary': {
                'total_concepts': len(concepts),
                'total_relations': len(relations),
                'orphan_count': len(issues['orphan_relations']),
                'cycle_count': len(issues['cycles']),
                'duplicate_count': len(issues['duplicate_ids'])
            }
        }
    
    def save_layout_positions(self, positions: Dict[str, Dict[str, float]]) -> bool:
        """Save graph layout positions for persistence."""
        try:
            for concept_id, pos in positions.items():
                self.db.update_layout_position(
                    concept_id, 
                    pos.get('x', 0), 
                    pos.get('y', 0), 
                    pos.get('z', 0)
                )
            return True
        except Exception as e:
            logger.error(f"Failed to save layout positions: {e}")
            return False
    
    def _get_mastery_color(self, mastery_percent: float) -> str:
        """Get color based on mastery percentage."""
        if mastery_percent > 80:
            return '#10b981'  # green
        elif mastery_percent >= 50:
            return '#fbbf24'  # yellow
        elif mastery_percent >= 20:
            return '#f97316'  # orange
        else:
            return '#6b7280'  # gray
    
    def _recalculate_relation_strength(self, relation_id: str):
        """Recalculate relation strength based on review patterns."""
        # This is a placeholder for more sophisticated strength calculation
        # Could be based on co-review patterns, temporal proximity, etc.
        pass
    
    def _apply_depth_filter(self, nodes: List[Dict], edges: List[Dict], 
                           depth: int) -> Tuple[List[Dict], List[Dict]]:
        """Filter graph to specified depth from root nodes."""
        if not nodes:
            return nodes, edges
        
        # Build adjacency list
        adjacency = defaultdict(list)
        for edge in edges:
            adjacency[edge['source']].append(edge['target'])
            adjacency[edge['target']].append(edge['source'])
        
        # Start from nodes with no incoming edges (roots)
        in_degree = defaultdict(int)
        for edge in edges:
            in_degree[edge['target']] += 1
        
        root_nodes = [n['id'] for n in nodes if in_degree[n['id']] == 0]
        if not root_nodes:
            root_nodes = [nodes[0]['id']]
        
        # BFS to get nodes within depth
        visited = set()
        queue = [(node_id, 0) for node_id in root_nodes]
        
        while queue:
            node_id, current_depth = queue.pop(0)
            if node_id in visited or current_depth > depth:
                continue
            
            visited.add(node_id)
            
            if current_depth < depth:
                for neighbor in adjacency[node_id]:
                    if neighbor not in visited:
                        queue.append((neighbor, current_depth + 1))
        
        # Filter nodes and edges
        filtered_nodes = [n for n in nodes if n['id'] in visited]
        filtered_edges = [e for e in edges if e['source'] in visited and e['target'] in visited]
        
        return filtered_nodes, filtered_edges
    
    def _detect_cycles(self, concepts: List[Dict], relations: List[Dict]) -> List[List[str]]:
        """Detect cycles in the graph using DFS."""
        adjacency = defaultdict(list)
        for rel in relations:
            # Only consider directed edges for cycle detection
            if rel['relation_type'] in ['prerequisite', 'dependency']:
                adjacency[rel['source_id']].append(rel['target_id'])
        
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(node, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in adjacency[node]:
                if neighbor not in visited:
                    dfs(neighbor, path[:])
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)
            
            rec_stack.remove(node)
        
        for concept in concepts:
            if concept['id'] not in visited:
                dfs(concept['id'], [])
        
        return cycles


class LanceDBManager:
    """Mock LanceDB manager for semantic search (to be implemented)."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path
        logger.info("LanceDBManager initialized (stub implementation)")
    
    def index_concept(self, concept_id: str, name: str, description: str = None):
        """Index a concept for semantic search."""
        pass
    
    def update_concept(self, concept_id: str, name: str, description: str = None):
        """Update concept in semantic index."""
        pass
    
    def delete_concept(self, concept_id: str):
        """Remove concept from semantic index."""
        pass
    
    def find_similar_concepts(self, concept_id: str, limit: int = 10, 
                             exclude_ids: List[str] = None) -> List[str]:
        """Find semantically similar concepts."""
        return []
