"""
Knowledge Graph Service - Core business logic for graph operations
"""
import logging
import json
from typing import List, Dict, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
import sqlite3
from collections import defaultdict, deque

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.database.sqlite_manager import SQLiteManager
from backend.core.graph.lance_db_manager import LanceDBManager

logger = logging.getLogger(__name__)


class KnowledgeGraphService:
    """Main service for knowledge graph operations"""
    
    def __init__(self, db_path: str = "knowledge_graph.db"):
        self.db_manager = SQLiteManager(db_path)
        self.vector_manager = LanceDBManager(db_path)
        
        # Run migrations on initialization
        self.db_manager.migrate_database()
    
    # Mastery color buckets for D3 visualization
    MASTERY_BUCKETS = {
        'green': (80, 100),    # > 80%
        'yellow': (50, 80),    # 50-80%
        'orange': (20, 50),    # 20-50%
        'gray': (0, 20)        # < 20%
    }
    
    def get_mastery_color(self, mastery_percentage: float) -> str:
        """Get color bucket for mastery percentage"""
        for color, (min_pct, max_pct) in self.MASTERY_BUCKETS.items():
            if min_pct <= mastery_percentage < max_pct:
                return color
        return 'gray'
    
    def create_concept(self, name: str, description: str = "", content: str = "", parent_id: Optional[int] = None) -> Dict[str, Any]:
        """Create a new concept with validation"""
        
        # Validate name uniqueness
        if self._concept_exists_by_name(name):
            raise ValueError(f"Concept with name '{name}' already exists")
        
        # Validate parent concept exists if provided
        if parent_id and not self._concept_exists_by_id(parent_id):
            raise ValueError(f"Parent concept with ID {parent_id} does not exist")
        
        # Create the concept
        concept_id = self.db_manager.create_concept(name, description, content, parent_id)
        
        # Generate and store a simple embedding (in real implementation, use actual embedding model)
        embedding = self._generate_simple_embedding(name, description)
        self.vector_manager.store_embedding(concept_id, embedding)
        
        concept = self.db_manager.get_concept(concept_id)
        logger.info(f"Created concept: {name} (ID: {concept_id})")
        
        return concept
    
    def update_concept(self, concept_id: int, **kwargs) -> Dict[str, Any]:
        """Update concept with validation"""
        
        # Check if concept exists
        if not self._concept_exists_by_id(concept_id):
            raise ValueError(f"Concept with ID {concept_id} does not exist")
        
        # Validate name uniqueness if name is being updated
        if 'name' in kwargs and self._concept_exists_by_name(kwargs['name'], exclude_id=concept_id):
            raise ValueError(f"Concept with name '{kwargs['name']}' already exists")
        
        # Validate parent concept if being updated
        if 'parent_id' in kwargs and kwargs['parent_id']:
            if not self._concept_exists_by_id(kwargs['parent_id']):
                raise ValueError(f"Parent concept with ID {kwargs['parent_id']} does not exist")
            if kwargs['parent_id'] == concept_id:
                raise ValueError("Concept cannot be its own parent")
        
        # Update the concept
        success = self.db_manager.update_concept(concept_id, **kwargs)
        if not success:
            raise ValueError(f"Failed to update concept {concept_id}")
        
        # Update embedding if name or description changed
        if 'name' in kwargs or 'description' in kwargs:
            concept = self.db_manager.get_concept(concept_id)
            embedding = self._generate_simple_embedding(concept['name'], concept['description'])
            self.vector_manager.store_embedding(concept_id, embedding)
        
        concept = self.db_manager.get_concept(concept_id)
        logger.info(f"Updated concept {concept_id}: {kwargs}")
        
        return concept
    
    def delete_concept(self, concept_id: int, force: bool = False) -> bool:
        """Delete concept with orphan prevention"""
        
        # Check if concept exists
        if not self._concept_exists_by_id(concept_id):
            raise ValueError(f"Concept with ID {concept_id} does not exist")
        
        # Check for orphan prevention unless forced
        if not force:
            orphan_issues = self.check_orphans([concept_id])
            if orphan_issues:
                raise ValueError(f"Cannot delete concept {concept_id}: would create orphaned relations. Use force=True to override.")
        
        # Get concept info before deletion
        concept = self.db_manager.get_concept(concept_id)
        
        # Delete the concept (this will cascade delete related records)
        success = self.db_manager.delete_concept(concept_id)
        
        logger.info(f"Deleted concept {concept_id}: {concept['name'] if concept else 'Unknown'}")
        return success
    
    def create_relation(self, source_concept_id: int, target_concept_id: int, relation_type: str = "prerequisite", strength: float = 1.0) -> Dict[str, Any]:
        """Create relation between concepts with validation"""
        
        # Validate both concepts exist
        if not self._concept_exists_by_id(source_concept_id):
            raise ValueError(f"Source concept {source_concept_id} does not exist")
        if not self._concept_exists_by_id(target_concept_id):
            raise ValueError(f"Target concept {target_concept_id} does not exist")
        
        # Prevent self-referencing
        if source_concept_id == target_concept_id:
            raise ValueError("Cannot create self-referencing relation")
        
        # Check for duplicate relations
        if self._relation_exists(source_concept_id, target_concept_id, relation_type):
            raise ValueError(f"Relation already exists: {source_concept_id} -> {target_concept_id} ({relation_type})")
        
        # Create the relation
        relation_id = self.db_manager.create_relation(source_concept_id, target_concept_id, relation_type, strength)
        
        # Recalculate relation strength based on usage patterns
        self._recalculate_relation_strength(source_concept_id, target_concept_id)
        
        relation = self.get_relation(relation_id)
        logger.info(f"Created relation {relation_id}: {source_concept_id} -> {target_concept_id}")
        
        return relation
    
    def get_concept_graph_data(self, concept_ids: Optional[List[int]] = None, user_id: str = "default", depth: int = 2) -> Dict[str, Any]:
        """Get D3-ready graph data for visualization"""
        
        try:
            with sqlite3.connect(self.db_manager.db_path) as conn:
                conn.row_factory = sqlite3.Row  # Enable column access by name
                cursor = conn.cursor()
                
                # Get concepts (filter by IDs if provided)
                if concept_ids:
                    concept_placeholders = ','.join('?' * len(concept_ids))
                    cursor.execute(f'''
                        SELECT * FROM concepts WHERE id IN ({concept_placeholders})
                    ''', concept_ids)
                else:
                    cursor.execute('SELECT * FROM concepts')
                
                concepts = cursor.fetchall()
                
                # Get relations
                if concept_ids:
                    concept_placeholders = ','.join('?' * len(concept_ids))
                    cursor.execute(f'''
                        SELECT * FROM relations 
                        WHERE source_concept_id IN ({concept_placeholders}) 
                           OR target_concept_id IN ({concept_placeholders})
                    ''', concept_ids + concept_ids)
                else:
                    cursor.execute('SELECT * FROM relations')
                
                relations = cursor.fetchall()
                
                # Get mastery data
                if concept_ids:
                    mastery_placeholders = ','.join('?' * len(concept_ids))
                    cursor.execute(f'''
                        SELECT concept_id, mastery_percentage, review_count, last_assessed
                        FROM concept_mastery 
                        WHERE user_id = ? AND concept_id IN ({mastery_placeholders})
                    ''', [user_id] + concept_ids)
                else:
                    cursor.execute('''
                        SELECT concept_id, mastery_percentage, review_count, last_assessed
                        FROM concept_mastery 
                        WHERE user_id = ?
                    ''', (user_id,))
                
                mastery_data = {}
                for row in cursor.fetchall():
                    mastery_data[row['concept_id']] = {
                        'mastery_percentage': row['mastery_percentage'],
                        'review_count': row['review_count'],
                        'last_assessed': row['last_assessed'],
                        'color': self.get_mastery_color(row['mastery_percentage'])
                    }
                
                # Build D3-ready nodes
                nodes = []
                for concept_row in concepts:
                    concept_id = concept_row['id']
                    mastery_info = mastery_data.get(concept_id, {
                        'mastery_percentage': 0.0,
                        'review_count': 0,
                        'last_assessed': None,
                        'color': 'gray'
                    })
                    
                    node = {
                        'id': concept_id,
                        'name': concept_row['name'],
                        'description': concept_row['description'],
                        'content': concept_row['content'],
                        'parent_id': concept_row['parent_id'],
                        'created_at': concept_row['created_at'],
                        'updated_at': concept_row['updated_at'],
                        'mastery': mastery_info['mastery_percentage'],
                        'review_count': mastery_info['review_count'],
                        'last_assessed': mastery_info['last_assessed'],
                        'color': mastery_info['color']
                    }
                    nodes.append(node)
                
                # Build D3-ready links
                links = []
                for relation_row in relations:
                    link = {
                        'source': relation_row['source_concept_id'],
                        'target': relation_row['target_concept_id'],
                        'type': relation_row['relation_type'],
                        'strength': relation_row['strength'],
                        'created_at': relation_row['created_at']
                    }
                    links.append(link)
                
                # Add prerequisite/dependency tags
                self._add_relation_tags(nodes, links)
                
                return {
                    'nodes': nodes,
                    'links': links,
                    'stats': {
                        'total_concepts': len(nodes),
                        'total_relations': len(links),
                        'mastery_distribution': self._get_mastery_distribution(mastery_data)
                    }
                }
                
        except Exception as e:
            logger.error(f"Failed to get graph data: {e}")
            raise
    
    def find_semantic_neighbors(self, concept_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Find semantically similar concepts using vector search"""
        return self.vector_manager.find_semantic_neighbors(concept_id, limit)
    
    def search_concepts(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search concepts by name, description, or semantic similarity"""
        
        # First try direct text search
        try:
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, name, description, content
                    FROM concepts
                    WHERE name LIKE ? OR description LIKE ? OR content LIKE ?
                    LIMIT ?
                ''', (f'%{query}%', f'%{query}%', f'%{query}%', limit))
                
                text_results = []
                for row in cursor.fetchall():
                    concept_id, name, description, content = row
                    text_results.append({
                        'concept_id': concept_id,
                        'name': name,
                        'description': description,
                        'content': content,
                        'match_type': 'text',
                        'score': 1.0
                    })
                
                # If no text results, try semantic search
                if not text_results and hasattr(self, '_search_semantic'):
                    # Generate embedding for query and search
                    query_embedding = self._generate_simple_embedding(query, "")
                    semantic_results = self.vector_manager.search_concepts_by_embedding(query_embedding, limit)
                    return semantic_results
                
                return text_results
                
        except Exception as e:
            logger.error(f"Failed to search concepts: {e}")
            raise
    
    def check_integrity(self, concept_ids: Optional[List[int]] = None) -> Dict[str, Any]:
        """Run comprehensive integrity checks"""
        issues = {
            'orphans': self.check_orphans(concept_ids),
            'cycles': self.check_cycles(concept_ids),
            'broken_references': self.check_broken_references(concept_ids),
            'duplicate_ids': self.check_duplicate_ids(concept_ids),
            'strength_anomalies': self.check_strength_anomalies(concept_ids)
        }
        
        total_issues = sum(len(issue_list) for issue_list in issues.values())
        
        return {
            'status': 'healthy' if total_issues == 0 else 'issues_found',
            'total_issues': total_issues,
            'issues': issues,
            'checked_at': datetime.now().isoformat()
        }
    
    def check_orphans(self, concept_ids: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        """Check for orphaned concepts (concepts that are referenced but don't exist)"""
        try:
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                
                # Check for concepts that are referenced in relations but deleted
                cursor.execute('''
                    SELECT DISTINCT source_concept_id, target_concept_id
                    FROM relations
                    WHERE source_concept_id NOT IN (SELECT id FROM concepts)
                       OR target_concept_id NOT IN (SELECT id FROM concepts)
                ''')
                
                orphan_relations = []
                for row in cursor.fetchall():
                    source_id, target_id = row
                    if source_id not in [c['id'] for c in self._get_concepts_by_ids([source_id])]:
                        orphan_relations.append({
                            'type': 'missing_source',
                            'relation_id': None,  # Would need to get this from join
                            'concept_id': source_id,
                            'description': f"Source concept {source_id} referenced but doesn't exist"
                        })
                    if target_id not in [c['id'] for c in self._get_concepts_by_ids([target_id])]:
                        orphan_relations.append({
                            'type': 'missing_target',
                            'relation_id': None,
                            'concept_id': target_id,
                            'description': f"Target concept {target_id} referenced but doesn't exist"
                        })
                
                return orphan_relations
                
        except Exception as e:
            logger.error(f"Failed to check orphans: {e}")
            raise
    
    def check_cycles(self, concept_ids: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        """Check for circular dependencies in relations"""
        try:
            cycles = []
            
            # Build adjacency list
            adjacency = defaultdict(list)
            
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                
                if concept_ids:
                    placeholders = ','.join('?' * len(concept_ids))
                    cursor.execute(f'''
                        SELECT source_concept_id, target_concept_id
                        FROM relations
                        WHERE source_concept_id IN ({placeholders})
                          AND target_concept_id IN ({placeholders})
                          AND relation_type = 'prerequisite'
                    ''', concept_ids + concept_ids)
                else:
                    cursor.execute('''
                        SELECT source_concept_id, target_concept_id
                        FROM relations
                        WHERE relation_type = 'prerequisite'
                    ''')
                
                for row in cursor.fetchall():
                    source, target = row
                    adjacency[source].append(target)
            
            # Detect cycles using DFS
            visited = set()
            rec_stack = set()
            
            def dfs(node, path):
                if node in rec_stack:
                    # Found cycle
                    cycle_start = path.index(node)
                    cycle_path = path[cycle_start:] + [node]
                    cycles.append({
                        'type': 'circular_dependency',
                        'cycle': cycle_path,
                        'description': f"Circular dependency detected: {' -> '.join(map(str, cycle_path))}"
                    })
                    return
                
                if node in visited:
                    return
                
                visited.add(node)
                rec_stack.add(node)
                
                for neighbor in adjacency[node]:
                    dfs(neighbor, path + [node])
                
                rec_stack.remove(node)
            
            # Start DFS from all nodes
            all_nodes = set(adjacency.keys()) | set().union(*adjacency.values())
            for node in all_nodes:
                if node not in visited:
                    dfs(node, [])
            
            return cycles
            
        except Exception as e:
            logger.error(f"Failed to check cycles: {e}")
            raise
    
    def check_broken_references(self, concept_ids: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        """Check for broken references in concept hierarchy"""
        broken_refs = []
        
        try:
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                
                if concept_ids:
                    placeholders = ','.join('?' * len(concept_ids))
                    cursor.execute(f'''
                        SELECT id, parent_id FROM concepts
                        WHERE parent_id IS NOT NULL AND id IN ({placeholders})
                    ''', concept_ids)
                else:
                    cursor.execute('''
                        SELECT id, parent_id FROM concepts
                        WHERE parent_id IS NOT NULL
                    ''')
                
                for row in cursor.fetchall():
                    concept_id, parent_id = row
                    
                    # Check if parent exists
                    if not self._concept_exists_by_id(parent_id):
                        broken_refs.append({
                            'type': 'missing_parent',
                            'concept_id': concept_id,
                            'reference_id': parent_id,
                            'description': f"Concept {concept_id} references non-existent parent {parent_id}"
                        })
                    
                    # Check for circular parent references
                    if self._creates_circular_parent_reference(concept_id, parent_id):
                        broken_refs.append({
                            'type': 'circular_parent_reference',
                            'concept_id': concept_id,
                            'reference_id': parent_id,
                            'description': f"Concept {concept_id} would create circular parent reference"
                        })
                
                return broken_refs
                
        except Exception as e:
            logger.error(f"Failed to check broken references: {e}")
            raise
    
    def check_duplicate_ids(self, concept_ids: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        """Check for duplicate concept IDs or names"""
        duplicates = []
        
        try:
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                
                # Check for duplicate names
                cursor.execute('''
                    SELECT name, COUNT(*) as count
                    FROM concepts
                    GROUP BY name
                    HAVING COUNT(*) > 1
                ''')
                
                for row in cursor.fetchall():
                    name, count = row
                    duplicates.append({
                        'type': 'duplicate_names',
                        'name': name,
                        'count': count,
                        'description': f"Name '{name}' appears {count} times"
                    })
                
                return duplicates
                
        except Exception as e:
            logger.error(f"Failed to check duplicates: {e}")
            raise
    
    def check_strength_anomalies(self, concept_ids: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        """Check for anomalous relation strengths"""
        anomalies = []
        
        try:
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                
                # Check for invalid strengths
                cursor.execute('''
                    SELECT id, source_concept_id, target_concept_id, strength
                    FROM relations
                    WHERE strength < 0 OR strength > 10
                ''')
                
                for row in cursor.fetchall():
                    relation_id, source, target, strength = row
                    anomalies.append({
                        'type': 'invalid_strength',
                        'relation_id': relation_id,
                        'strength': strength,
                        'description': f"Relation {relation_id} has invalid strength {strength}"
                    })
                
                # Check for extremely weak relations that might be data errors
                cursor.execute('''
                    SELECT id, source_concept_id, target_concept_id, strength
                    FROM relations
                    WHERE strength < 0.01
                ''')
                
                for row in cursor.fetchall():
                    relation_id, source, target, strength = row
                    anomalies.append({
                        'type': 'very_weak_relation',
                        'relation_id': relation_id,
                        'strength': strength,
                        'description': f"Relation {relation_id} has very weak strength {strength}"
                    })
                
                return anomalies
                
        except Exception as e:
            logger.error(f"Failed to check strength anomalies: {e}")
            raise
    
    def aggregate_mastery_from_reviews(self, user_id: str, concept_id: int, review_scores: List[float]) -> Dict[str, Any]:
        """Aggregate mastery from review scores"""
        if not review_scores:
            return {'mastery_percentage': 0.0, 'review_count': 0}
        
        # Calculate weighted average (recent reviews have more weight)
        total_weight = 0
        weighted_sum = 0
        
        for i, score in enumerate(review_scores):
            # Use exponential decay for weights (newer reviews weigh more)
            weight = 0.8 ** (len(review_scores) - i - 1)
            weighted_sum += score * weight
            total_weight += weight
        
        mastery_percentage = (weighted_sum / total_weight) * 100 if total_weight > 0 else 0
        
        # Update mastery in database
        self.db_manager.update_mastery(user_id, concept_id, mastery_percentage, len(review_scores))
        
        return {
            'mastery_percentage': mastery_percentage,
            'review_count': len(review_scores),
            'last_updated': datetime.now().isoformat()
        }
    
    # Helper methods
    def _concept_exists_by_name(self, name: str, exclude_id: Optional[int] = None) -> bool:
        """Check if concept exists by name"""
        try:
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                if exclude_id:
                    cursor.execute('SELECT id FROM concepts WHERE name = ? AND id != ?', (name, exclude_id))
                else:
                    cursor.execute('SELECT id FROM concepts WHERE name = ?', (name,))
                return cursor.fetchone() is not None
        except Exception:
            return False
    
    def _concept_exists_by_id(self, concept_id: int) -> bool:
        """Check if concept exists by ID"""
        try:
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id FROM concepts WHERE id = ?', (concept_id,))
                return cursor.fetchone() is not None
        except Exception:
            return False
    
    def _relation_exists(self, source_id: int, target_id: int, relation_type: str) -> bool:
        """Check if relation already exists"""
        try:
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id FROM relations 
                    WHERE source_concept_id = ? AND target_concept_id = ? AND relation_type = ?
                ''', (source_id, target_id, relation_type))
                return cursor.fetchone() is not None
        except Exception:
            return False
    
    def _get_concepts_by_ids(self, concept_ids: List[int]) -> List[Dict[str, Any]]:
        """Get concepts by list of IDs"""
        if not concept_ids:
            return []
        
        try:
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                placeholders = ','.join('?' * len(concept_ids))
                cursor.execute(f'SELECT * FROM concepts WHERE id IN ({placeholders})', concept_ids)
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception:
            return []
    
    def _get_mastery_distribution(self, mastery_data: Dict[int, Dict[str, Any]]) -> Dict[str, int]:
        """Get distribution of concepts by mastery color"""
        distribution = {'green': 0, 'yellow': 0, 'orange': 0, 'gray': 0}
        
        for mastery_info in mastery_data.values():
            color = mastery_info['color']
            if color in distribution:
                distribution[color] += 1
        
        return distribution
    
    def _add_relation_tags(self, nodes: List[Dict[str, Any]], links: List[Dict[str, Any]]):
        """Add prerequisite/dependency tags to nodes and links"""
        
        # Create concept ID to node mapping
        concept_map = {node['id']: node for node in nodes}
        
        # Identify prerequisite relations
        for link in links:
            if link['type'] == 'prerequisite':
                source_node = concept_map.get(link['source'])
                target_node = concept_map.get(link['target'])
                
                if source_node and target_node:
                    # Mark source as prerequisite for target
                    if 'prerequisites' not in target_node:
                        target_node['prerequisites'] = []
                    target_node['prerequisites'].append(source_node['id'])
                    
                    # Mark target as dependent on source
                    if 'dependencies' not in source_node:
                        source_node['dependencies'] = []
                    source_node['dependencies'].append(target_node['id'])
    
    def _creates_circular_parent_reference(self, concept_id: int, parent_id: int) -> bool:
        """Check if setting parent_id would create circular reference"""
        if concept_id == parent_id:
            return True
        
        # Walk up the parent chain to detect cycles
        current_id = parent_id
        visited = set()
        
        while current_id:
            if current_id == concept_id:
                return True
            if current_id in visited:
                break
            
            visited.add(current_id)
            current_id = self._get_parent_id(current_id)
        
        return False
    
    def _get_parent_id(self, concept_id: int) -> Optional[int]:
        """Get parent ID of a concept"""
        try:
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT parent_id FROM concepts WHERE id = ?', (concept_id,))
                row = cursor.fetchone()
                return row[0] if row and row[0] else None
        except Exception:
            return None
    
    def _generate_simple_embedding(self, name: str, description: str) -> List[float]:
        """Generate a simple embedding based on text (placeholder for actual embedding model)"""
        # This is a simplified placeholder implementation
        # In a real implementation, you would use a proper embedding model
        
        import hashlib
        
        text = f"{name} {description}".lower()
        hash_object = hashlib.md5(text.encode())
        hash_hex = hash_object.hexdigest()
        
        # Convert hash to 50-dimensional vector
        embedding = []
        for i in range(0, len(hash_hex), 2):
            # Convert each pair of hex characters to a float between 0 and 1
            hex_pair = hash_hex[i:i+2]
            if len(hex_pair) == 2:
                value = int(hex_pair, 16) / 255.0
                embedding.append(value)
        
        # Pad or truncate to 50 dimensions
        while len(embedding) < 50:
            embedding.append(0.0)
        embedding = embedding[:50]
        
        return embedding
    
    def _recalculate_relation_strength(self, source_id: int, target_id: int):
        """Recalculate relation strength based on usage patterns"""
        # This would analyze review patterns, mastery correlation, etc.
        # For now, we'll use a placeholder implementation
        
        try:
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                
                # Calculate strength based on concept popularity and usage
                cursor.execute('''
                    SELECT 
                        (SELECT COUNT(*) FROM review_logs WHERE concept_id = ?) +
                        (SELECT COUNT(*) FROM review_logs WHERE concept_id = ?) as usage_score
                ''', (source_id, target_id))
                
                usage_score = cursor.fetchone()[0]
                
                # Set strength based on usage (0.1 to 5.0 range)
                strength = min(5.0, 0.1 + (usage_score * 0.1))
                
                # Update the relation strength
                cursor.execute('''
                    UPDATE relations 
                    SET strength = ?
                    WHERE source_concept_id = ? AND target_concept_id = ?
                ''', (strength, source_id, target_id))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to recalculate relation strength: {e}")
    
    def get_relation(self, relation_id: int) -> Optional[Dict[str, Any]]:
        """Get relation by ID"""
        try:
            with sqlite3.connect(self.db_manager.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT r.*, sc.name as source_name, tc.name as target_name
                    FROM relations r
                    JOIN concepts sc ON r.source_concept_id = sc.id
                    JOIN concepts tc ON r.target_concept_id = tc.id
                    WHERE r.id = ?
                ''', (relation_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Failed to get relation {relation_id}: {e}")
            raise