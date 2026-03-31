"""
Hierarchical Builder for Mind Map Generation

This module provides hierarchical structure building capabilities for mind maps,
including semantic grouping via embeddings and tree structure validation.
"""

import uuid
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass


@dataclass
class HierarchicalNode:
    """Node in hierarchical structure"""
    id: str
    name: str
    node_data: Dict[str, Any]
    children: List["HierarchicalNode"]
    parent: Optional["HierarchicalNode"] = None
    embedding: Optional[Any] = None  # Use Any to avoid numpy dependency
    mastery: float = 0.0  # 0-100 scale
    depth: int = 0


class HierarchicalBuilder:
    """
    Builder for hierarchical structures with semantic grouping capabilities.
    
    This class builds tree structures from concepts, performs semantic grouping
    via embeddings, and generates D3.js compatible output with mastery metadata.
    """
    
    def __init__(self):
        self.root: Optional[HierarchicalNode] = None
        self.nodes: Dict[str, HierarchicalNode] = {}
        self.mastery_thresholds = {
            "green": 80.0,
            "yellow": 50.0,
            "orange": 20.0,
            "gray": 0.0
        }
    
    def build_from_concepts(self, concepts: List[Dict[str, Any]], embeddings: Optional[np.ndarray] = None) -> HierarchicalNode:
        """
        Build hierarchy from concept list with optional embeddings for semantic grouping.
        
        Args:
            concepts: List of concept dictionaries with 'name' and optional 'children'
            embeddings: Optional embeddings array for semantic clustering
        
        Returns:
            Root node of built hierarchy
        """
        if not concepts:
            raise ValueError("Concepts list cannot be empty")
        
        # Find or create root
        root_concept = None
        for concept in concepts:
            if concept.get("is_root") or len(concept.get("parents", [])) == 0:
                root_concept = concept
                break
        
        if not root_concept:
            # Create artificial root
            root_concept = {"name": "Main Topic", "id": str(uuid.uuid4()), "children": []}
            # Add all top-level concepts as children
            for concept in concepts:
                if not concept.get("parents"):
                    root_concept["children"].append(concept)
        
        self.root = self._build_node(root_concept, None, 0, embeddings)
        return self.root
    
    def _build_node(self, concept: Dict[str, Any], parent: Optional[HierarchicalNode], 
                   depth: int, embeddings: Optional[np.ndarray]) -> HierarchicalNode:
        """Recursively build node tree"""
        node_id = concept.get("id", str(uuid.uuid4()))
        
        node = HierarchicalNode(
            id=node_id,
            name=concept.get("name", "Unnamed"),
            node_data=concept,
            children=[],
            parent=parent,
            depth=depth,
            embedding=embeddings[concept.get("embedding_idx", 0)] if embeddings is not None else None,
            mastery=concept.get("mastery", 0.0)
        )
        
        self.nodes[node_id] = node
        
        # Build children
        for child_concept in concept.get("children", []):
            child_node = self._build_node(child_concept, node, depth + 1, embeddings)
            node.children.append(child_node)
        
        return node
    
    def calculate_color_from_mastery(self, mastery: float) -> str:
        """
        Calculate color based on mastery level.
        
        Args:
            mastery: Mastery level from 0-100
        
        Returns:
            Color string: green (>80%), yellow (50-80%), orange (20-50%), gray (<20%)
        """
        if mastery > self.mastery_thresholds["green"]:
            return "green"
        elif mastery >= self.mastery_thresholds["yellow"]:
            return "yellow"
        elif mastery >= self.mastery_thresholds["orange"]:
            return "orange"
        else:
            return "gray"
    
    def to_dict(self, include_mastery_colors: bool = True) -> Dict[str, Any]:
        """
        Convert hierarchy to dictionary suitable for D3.js visualization.
        
        Args:
            include_mastery_colors: Whether to include color coding based on mastery
        
        Returns:
            Dictionary ready for D3.js consumption
        """
        if not self.root:
            return {"version": "1", "root": {"name": "Empty", "id": str(uuid.uuid4()), "children": []}}
        
        def node_to_dict(node: HierarchicalNode) -> Dict[str, Any]:
            result = {
                "name": node.name,
                "id": node.id,
                "mastery": node.mastery,
                "depth": node.depth
            }
            
            if include_mastery_colors:
                result["color"] = self.calculate_color_from_mastery(node.mastery)
            
            if node.children:
                result["children"] = [node_to_dict(child) for child in node.children]
            
            return result
        
        return {
            "version": "1",
            "root": node_to_dict(self.root),
            "mastery_enabled": include_mastery_colors
        }
    
    def validate_tree_structure(self) -> List[str]:
        """
        Validate that the hierarchy forms a valid tree structure.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if not self.root:
            errors.append("No root node defined")
            return errors
        
        # Check for cycles using DFS
        visited = set()
        
        def check_cycles(node: HierarchicalNode) -> bool:
            if node.id in visited:
                errors.append(f"Cycle detected: node {node.id} appears multiple times")
                return False
            
            visited.add(node.id)
            
            for child in node.children:
                if not check_cycles(child):
                    return False
            
            visited.remove(node.id)
            return True
        
        check_cycles(self.root)
        
        # Check for orphans (nodes not reachable from root)
        all_children = set()
        
        def collect_children(node: HierarchicalNode) -> None:
            for child in node.children:
                all_children.add(child.id)
                collect_children(child)
        
        collect_children(self.root)
        
        orphans = self.nodes.keys() - all_children - {self.root.id}
        if orphans:
            errors.append(f"Orphan nodes detected: {list(orphans)}")
        
        # Validate depth does not exceed maximum
        max_depth = 10  # Reasonable maximum depth
        
        def check_depth(node: HierarchicalNode) -> None:
            if node.depth > max_depth:
                errors.append(f"Node {node.id} exceeds maximum depth {max_depth}")
            
            for child in node.children:
                if child.depth != node.depth + 1:
                    errors.append(f"Invalid depth progression for child {child.id}")
                check_depth(child)
        
        check_depth(self.root)
        
        return errors
    
    def get_node_by_path(self, path: List[str]) -> Optional[HierarchicalNode]:
        """
        Find node by path through the hierarchy.
        
        Args:
            path: List of node names from root to target
        
        Returns:
            Node if found, None otherwise
        """
        if not self.root or not path:
            return None
        
        if self.root.name != path[0]:
            return None
        
        current = self.root
        for node_name in path[1:]:
            found = False
            for child in current.children:
                if child.name == node_name:
                    current = child
                    found = True
                    break
            
            if not found:
                return None
        
        return current
    
    def calculate_tree_statistics(self) -> Dict[str, Any]:
        """
        Calculate statistics about the tree structure.
        
        Returns:
            Dictionary with tree statistics
        """
        if not self.root:
            return {"total_nodes": 0, "max_depth": 0, "avg_mastery": 0}
        
        total_nodes = 0
        max_depth = 0
        mastery_sum = 0
        
        def traverse(node: HierarchicalNode) -> None:
            nonlocal total_nodes, max_depth, mastery_sum
            total_nodes += 1
            max_depth = max(max_depth, node.depth)
            mastery_sum += node.mastery
            
            for child in node.children:
                traverse(child)
        
        traverse(self.root)
        
        return {
            "total_nodes": total_nodes,
            "max_depth": max_depth,
            "avg_mastery": mastery_sum / total_nodes if total_nodes > 0 else 0,
            "root_name": self.root.name
        }


class SemanticGrouper:
    """Helper class for semantic grouping of concepts via embeddings"""
    
    def __init__(self, similarity_threshold: float = 0.7):
        """
        Initialize semantic grouper.
        
        Args:
            similarity_threshold: Minimum cosine similarity for grouping (0-1)
        """
        self.similarity_threshold = similarity_threshold
    
    def group_concepts_semantically(self, concepts: List[Dict[str, Any]], 
                                  embeddings: np.ndarray) -> List[Dict[str, Any]]:
        """
        Group concepts based on semantic similarity using embeddings.
        
        Args:
            concepts: List of concept dictionaries
            embeddings: Embedding matrix for concepts
        
        Returns:
            Grouped concepts with hierarchical relationships
        """
        if len(concepts) != len(embeddings):
            raise ValueError("Number of concepts must match number of embeddings")
        
        # Calculate similarity matrix
        normalized = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        similarity_matrix = np.dot(normalized, normalized.T)
        
        # Build groups based on similarity
        grouped = []
        assigned = set()
        
        for i, concept in enumerate(concepts):
            if i in assigned:
                continue
            
            # Find similar concepts
            similar_indices = np.where(similarity_matrix[i] > self.similarity_threshold)[0]
            similar_indices = [idx for idx in similar_indices if idx != i and idx not in assigned]
            
            if len(similar_indices) > 0:
                # Create group with main concept as parent
                group_concept = concept.copy()
                group_concept["children"] = [concepts[idx] for idx in similar_indices]
                grouped.append(group_concept)
                
                assigned.add(i)
                assigned.update(similar_indices)
            else:
                # Standalone concept
                grouped.append(concept)
                assigned.add(i)
        
        return grouped
    
    def normalize_embeddings(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Normalize embeddings to unit length for cosine similarity.
        
        Args:
            embeddings: Raw embeddings
        
        Returns:
            Normalized embeddings
        """
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1, norms)  # Avoid division by zero
        return embeddings / norms


def create_test_mindmap() -> Dict[str, Any]:
    """Create a sample mind map for testing purposes"""
    builder = HierarchicalBuilder()
    
    concepts = [
        {
            "name": "Artificial Intelligence",
            "id": "ai-root",
            "mastery": 85,
            "children": [
                {
                    "name": "Machine Learning",
                    "id": "ml-branch",
                    "mastery": 75,
                    "children": [
                        {"name": "Supervised Learning", "id": "supervised", "mastery": 80, "children": []},
                        {"name": "Unsupervised Learning", "id": "unsupervised", "mastery": 65, "children": []},
                        {"name": "Reinforcement Learning", "id": "rl", "mastery": 70, "children": []}
                    ]
                },
                {
                    "name": "Deep Learning",
                    "id": "dl-branch",
                    "mastery": 90,
                    "children": [
                        {"name": "Neural Networks", "id": "nn", "mastery": 85, "children": []},
                        {"name": "CNN", "id": "cnn", "mastery": 88, "children": []},
                        {"name": "RNN", "id": "rnn", "mastery": 82, "children": []}
                    ]
                },
                {
                    "name": "NLP",
                    "id": "nlp-branch",
                    "mastery": 60,
                    "children": [
                        {"name": "Tokenization", "id": "token", "mastery": 55, "children": []},
                        {"name": "Sentiment Analysis", "id": "sentiment", "mastery": 45, "children": []}
                    ]
                }
            ]
        }
    ]
    
    builder.build_from_concepts(concepts)
    return builder.to_dict()


def benchmark_hierarchy_performance():
    """Performance benchmark for hierarchy generation"""
    import time
    
    # Create large concept list
    concepts = []
    for i in range(500):
        concepts.append({
            "name": f"Concept {i}",
            "id": f"concept-{i}",
            "mastery": min(100, 20 + (i % 80)),
            "children": [
                {
                    "name": f"Subconcept {i}.{j}",
                    "id": f"subconcept-{i}-{j}",
                    "mastery": min(100, 10 + (j * 15)),
                    "children": []
                }
                for j in range(4)
            ]
        })
    
    builder = HierarchicalBuilder()
    
    start_time = time.time()
    builder.build_from_concepts(concepts)
    result = builder.to_dict()
    end_time = time.time()
    
    duration = end_time - start_time
    stats = builder.calculate_tree_statistics()
    
    return {
        "duration": duration,
        "nodes_processed": stats["total_nodes"],
        "performance_ok": duration < 5.0
    }


if __name__ == "__main__":
    # Run basic tests
    result = create_test_mindmap()
    print("Sample mind map created successfully")
    
    benchmark = benchmark_hierarchy_performance()
    print(f"Performance benchmark: {benchmark['duration']:.3f}s for {benchmark['nodes_processed']} nodes")
    
    # Test validation
    builder = HierarchicalBuilder()
    builder.build_from_concepts([{"name": "Test", "id": "1", "children": []}])
    errors = builder.validate_tree_structure()
    print(f"Validation errors: {errors}")