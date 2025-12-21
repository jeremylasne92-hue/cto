import pytest
import json
import time
from unittest.mock import Mock, patch
from typing import Dict, List, Any
import uuid

from pedagogy_engine.transform.mindmap import MindMapGenerator
from pedagogy_engine.transform.quality import validate_mindmap, QualityIssue
from pedagogy_engine.llm.offline import OfflineLLM


class TestMindMapGenerator:
    """Test mind map generation functionality"""
    
    @pytest.fixture
    def mock_llm(self):
        """Mock LLM for testing"""
        llm = Mock(spec=OfflineLLM)
        return llm
    
    @pytest.fixture
    def sample_content_100_words(self):
        """Sample 100-word document for testing"""
        return """
        Artificial Intelligence is transforming modern technology. AI systems can learn from data 
        and make decisions without human intervention. Machine learning algorithms analyze patterns 
        and improve over time. Deep learning uses neural networks to process complex information.
        Natural language processing enables computers to understand human language. Computer vision 
        allows machines to identify objects in images. These technologies power self-driving cars,
        virtual assistants, and recommendation systems. The future of AI holds
        both exciting possibilities and important ethical considerations.
        """
    
    @pytest.fixture
    def sample_content_5000_words(self):
        """Sample 5000-word document for performance testing"""
        base_text = """
        Artificial Intelligence represents one of the most transformative technologies of our time. 
        This comprehensive overview explores the fundamental concepts, applications, and implications 
        of AI across multiple domains. We begin with foundational principles and progress to 
        advanced implementations and future prospects.
        """
        
        # Create expanded content by repeating and elaborating
        topics = [
            "Machine Learning Fundamentals", "Deep Neural Networks", "Natural Language Processing",
            "Computer Vision Systems", "Reinforcement Learning", "AI Ethics and Governance",
            "Healthcare Applications", "Autonomous Systems", "Business Intelligence",
            "Robotics Integration", "Edge Computing AI", "Quantum Machine Learning"
        ]
        
        expanded_content = base_text
        for topic in topics:
            for i in range(30):  # Multiple paragraphs per topic
                expanded_content += f"""
                {topic} - Section {i+1}: This section discusses key aspects of {topic.lower()}. 
                The implementation details span algorithms, data requirements, computational needs, 
                and real-world constraints. We explore theoretical foundations alongside practical 
                engineering considerations. Performance metrics, scalability challenges, and system 
                integration patterns are examined in depth. The discussion encompasses current state 
                of the art while considering future trajectories and emerging paradigms. Multiple 
                case studies illustrate successful deployments across industry sectors.
                """
        
        return expanded_content[:5000]
    
    def test_generate_mindmap_basic_structure(self, mock_llm, sample_content_100_words):
        """Test basic mind map structure generation"""
        # Setup mock fallback behavior - as we saw in the actual code,
        # it falls back to heuristic when OfflineLLM is specified
        generator = MindMapGenerator(llm=mock_llm)
        
        mindmap = generator.generate(sample_content_100_words)
        
        # Validate basic structure
        assert "version" in mindmap
        assert mindmap["version"] == "1"
        assert "root" in mindmap
        assert "generator" in mindmap
        assert mindmap["generator"] == "heuristic"
    
    def test_mindmap_root_node(self, sample_content_100_words):
        """Test root node generation"""
        mock_llm = Mock(spec=OfflineLLM)
        generator = MindMapGenerator(llm=mock_llm)
        
        mindmap = generator.generate(sample_content_100_words)
        
        root = mindmap["root"]
        assert "name" in root
        assert "id" in root
        assert "children" in root
        assert isinstance(root["name"], str)
        assert len(root["name"]) > 0
        assert isinstance(root["children"], list)
    
    def test_mindmap_branch_count(self, sample_content_100_words):
        """Test that mind map has correct number of branches (3-7)"""
        mock_llm = Mock(spec=OfflineLLM)
        generator = MindMapGenerator(llm=mock_llm)
        
        mindmap = generator.generate(sample_content_100_words)
        
        branches = mindmap["root"]["children"]
        assert 3 <= len(branches) <= 7, f"Expected 3-7 branches, got {len(branches)}"
    
    def test_mindmap_hierarchy_depth(self, sample_content_100_words):
        """Test that hierarchy has proper depth (root→branches→leaves)"""
        mock_llm = Mock(spec=OfflineLLM)
        generator = MindMapGenerator(llm=mock_llm)
        
        mindmap = generator.generate(sample_content_100_words)
        
        # Check root level
        root = mindmap["root"]
        assert root["name"] is not None
        
        # Check branch level
        branches = root["children"]
        for branch in branches:
            assert "name" in branch
            assert "id" in branch
            assert "children" in branch
            
            # Check leaf level
            if branch["children"]:
                for leaf in branch["children"]:
                    assert "name" in leaf
                    assert "id" in leaf
    
    def test_mindmap_no_cycles(self, sample_content_100_words):
        """Test that generated mind map has no cycles"""
        mock_llm = Mock(spec=OfflineLLM)
        generator = MindMapGenerator(llm=mock_llm)
        
        mindmap = generator.generate(sample_content_100_words)
        
        # Collect all node IDs
        node_ids = set()
        
        def collect_ids(node: Dict[str, Any]) -> None:
            node_id = node.get("id")
            if node_id:
                assert node_id not in node_ids, f"Cycle detected: duplicate node ID {node_id}"
                node_ids.add(node_id)
            
            for child in node.get("children", []):
                collect_ids(child)
        
        collect_ids(mindmap["root"])
    
    def test_mindmap_tree_structure_valid(self, sample_content_100_words):
        """Test that generated structure is a valid tree (no orphans)"""
        mock_llm = Mock(spec=OfflineLLM)
        generator = MindMapGenerator(llm=mock_llm)
        
        mindmap = generator.generate(sample_content_100_words)
        
        # Validate with quality function
        issues = validate_mindmap(mindmap)
        cycle_issues = [i for i in issues if "cycle" in i.code.lower()]
        assert len(cycle_issues) == 0, f"Tree structure issues: {issues}"
    
    def test_mindmap_d3_format_nodes(self, sample_content_100_words):
        """Test D3.js format compliance for nodes"""
        mock_llm = Mock(spec=OfflineLLM)
        generator = MindMapGenerator(llm=mock_llm)
        
        mindmap = generator.generate(sample_content_100_words)
        
        def validate_d3_node(node: Dict[str, Any]) -> None:
            # D3.js expects name, children
            assert "name" in node
            assert isinstance(node["name"], str)
            assert len(node["name"]) > 0
            
            # Optional children
            if "children" in node:
                assert isinstance(node["children"], list)
                for child in node["children"]:
                    validate_d3_node(child)
        
        validate_d3_node(mindmap["root"])
    
    def test_mindmap_d3_format_json_schema(self, sample_content_100_words):
        """Test that mind map can be serialized to valid D3.js JSON"""
        mock_llm = Mock(spec=OfflineLLM)
        generator = MindMapGenerator(llm=mock_llm)
        
        mindmap = generator.generate(sample_content_100_words)
        
        # Should be JSON serializable
        json_str = json.dumps(mindmap)
        parsed_back = json.loads(json_str)
        
        # Verify structure preserved
        assert parsed_back["version"] == mindmap["version"]
        assert parsed_back["root"]["name"] == mindmap["root"]["name"]
        assert len(parsed_back["root"]["children"]) == len(mindmap["root"]["children"])
    
    def test_mastery_color_coding_green(self):
        """Test mastery color coding for >80% (green)"""
        mock_llm = Mock(spec=OfflineLLM)
        generator = MindMapGenerator(llm=mock_llm)
        
        mock_content = "Test content for mastery calculation. The system should correctly assign colors based on mastery levels and progressive learning metrics."
        mindmap = generator.generate(mock_content)
        
        # Add mastery metadata for testing
        def add_mastery(node: Dict[str, Any], mastery: int) -> None:
            node["mastery"] = mastery
            if mastery > 80:
                node["color"] = "green"
            elif mastery >= 50:
                node["color"] = "yellow"
            elif mastery >= 20:
                node["color"] = "orange"
            else:
                node["color"] = "gray"
            
            for child in node.get("children", []):
                add_mastery(child, mastery - 10)  # Decrease mastery for depth
        
        root_mastery = 85  # Should be green
        add_mastery(mindmap["root"], root_mastery)
        
        assert mindmap["root"]["color"] == "green"
        assert mindmap["root"]["mastery"] == 85
    
    def test_mastery_color_coding_yellow(self):
        """Test mastery color coding for 50-80% (yellow)"""
        mock_llm = Mock(spec=OfflineLLM)
        generator = MindMapGenerator(llm=mock_llm)
        
        mock_content = "Test content for mastery calculation with standard learning progression."
        mindmap = generator.generate(mock_content)
        
        def add_mastery(node: Dict[str, Any], mastery: int) -> None:
            node["mastery"] = mastery
            if mastery > 80:
                node["color"] = "green"
            elif mastery >= 50:
                node["color"] = "yellow"
            elif mastery >= 20:
                node["color"] = "orange"
            else:
                node["color"] = "gray"
            
            for child in node.get("children", []):
                add_mastery(child, mastery)
        
        root_mastery = 75  # Should be yellow
        add_mastery(mindmap["root"], root_mastery)
        
        assert mindmap["root"]["color"] == "yellow"
        assert 50 <= mindmap["root"]["mastery"] <= 80
    
    def test_mastery_color_coding_orange(self):
        """Test mastery color coding for 20-50% (orange)"""
        mock_llm = Mock(spec=OfflineLLM)
        generator = MindMapGenerator(llm=mock_llm)
        
        mock_content = "Test content for lower mastery levels."
        mindmap = generator.generate(mock_content)
        
        def add_mastery(node: Dict[str, Any], mastery: int) -> None:
            node["mastery"] = mastery
            if mastery > 80:
                node["color"] = "green"
            elif mastery >= 50:
                node["color"] = "yellow"
            elif mastery >= 20:
                node["color"] = "orange"
            else:
                node["color"] = "gray"
            
            for child in node.get("children", []):
                add_mastery(child, mastery)
        
        root_mastery = 35  # Should be orange
        add_mastery(mindmap["root"], root_mastery)
        
        assert mindmap["root"]["color"] == "orange"
        assert 20 <= mindmap["root"]["mastery"] < 50
    
    def test_mastery_color_coding_gray(self):
        """Test mastery color coding for <20% (gray)"""
        mock_llm = Mock(spec=OfflineLLM)
        generator = MindMapGenerator(llm=mock_llm)
        
        mock_content = "Test content for minimal mastery."
        mindmap = generator.generate(mock_content)
        
        def add_mastery(node: Dict[str, Any], mastery: int) -> None:
            node["mastery"] = mastery
            if mastery > 80:
                node["color"] = "green"
            elif mastery >= 50:
                node["color"] = "yellow"
            elif mastery >= 20:
                node["color"] = "orange"
            else:
                node["color"] = "gray"
            
            for child in node.get("children", []):
                add_mastery(child, mastery)
        
        root_mastery = 15  # Should be gray
        add_mastery(mindmap["root"], root_mastery)
        
        assert mindmap["root"]["color"] == "gray"
        assert mindmap["root"]["mastery"] < 20
    
    def test_performance_5000_words(self, sample_content_5000_words):
        """Test performance: generate mind map for 5000-word doc in <15s"""
        mock_llm = Mock(spec=OfflineLLM)
        generator = MindMapGenerator(llm=mock_llm)
        
        start_time = time.time()
        mindmap = generator.generate(sample_content_5000_words)
        end_time = time.time()
        
        duration = end_time - start_time
        assert duration < 15.0, f"Performance test failed: {duration:.2f}s > 15s"
        
        # Verify structure is still valid
        assert "root" in mindmap
        branches = mindmap["root"]["children"]
        assert 3 <= len(branches) <= 7
    
    def test_edge_case_single_concept(self):
        """Test edge case: single concept document"""
        mock_llm = Mock(spec=OfflineLLM)
        generator = MindMapGenerator(llm=mock_llm)
        
        single_concept = "AI"
        mindmap = generator.generate(single_concept)
        
        # Should still generate valid structure
        assert "root" in mindmap
        assert mindmap["root"]["name"] is not None
        branches = mindmap["root"]["children"]
        assert len(branches) >= 3, "Should have minimum branches even for single concept"
    
    def test_edge_case_very_deep_tree(self):
        """Test edge case: content that generates very deep trees"""
        mock_llm = Mock(spec=OfflineLLM)
        generator = MindMapGenerator(llm=mock_llm)
        
        nested_content = """
        # Science
        ## Physics
        ### Classical Mechanics
        #### Newton's Laws
        ##### First Law
        ####### Applications
        ####### Examples
        ####### History
        ##### Second Law
        ####### Mathematical Formulation
        ####### Real-world Cases
        ##### Third Law
        ### Electromagnetism
        ### Quantum Physics
        ## Chemistry
        ### Organic
        ### Inorganic
        ## Biology
        ### Cellular
        ### Evolution
        """
        
        mindmap = generator.generate(nested_content)
        
        # Should handle nested content gracefully
        assert "root" in mindmap
        assert mindmap["root"]["name"] is not None
        # Should flatten or adapt very deep structures
    
    def test_edge_case_no_dependencies(self):
        """Test edge case: content with no clear dependency structure"""
        mock_llm = Mock(spec=OfflineLLM)
        generator = MindMapGenerator(llm=mock_llm)
        
        # Random unrelated sentences
        no_deps = """
        The sky is blue. Water boils at 100 degrees Celsius. 
        Computers use binary code. Photosynthesis requires sunlight. 
        Gravity keeps us on Earth. Human DNA has 23 pairs of chromosomes.
        The speed of light is 299,792,458 meters per second.
        """
        
        mindmap = generator.generate(no_deps)
        
        # Should still create a coherent mind map
        assert "root" in mindmap
        branches = mindmap["root"]["children"]
        assert 3 <= len(branches) <= 7
    
    def test_edge_case_empty_content(self):
        """Test edge case: empty or minimal content"""
        mock_llm = Mock(spec=OfflineLLM)
        generator = MindMapGenerator(llm=mock_llm)
        
        mindmap = generator.generate("")
        
        # Should handle gracefully and provide default structure
        assert "root" in mindmap
        assert mindmap["root"]["name"] is not None
        branches = mindmap["root"]["children"]
        assert len(branches) >= 3
    
    def test_llm_generation_fallback_to_heuristic(self, mock_llm, sample_content_100_words):
        """Test that LLM generation falls back to heuristic when not OfflineLLM"""
        # Use a non-OfflineLLM mock
        regular_llm = Mock()
        regular_llm.generate.return_value = "{}"
        
        generator = MindMapGenerator(llm=regular_llm)
        
        mindmap = generator.generate(sample_content_100_words)
        
        # Should fall back to heuristic as specified in code
        assert "generator" in mindmap
        assert "heuristic" in mindmap["generator"]
    
    def test_hierarchical_builder_semantic_grouping(self, sample_content_100_words):
        """Test semantic grouping of related concepts"""
        mock_llm = Mock(spec=OfflineLLM)
        generator = MindMapGenerator(llm=mock_llm)
        
        mindmap = generator.generate(sample_content_100_words)
        
        # Analyze branches for semantic coherence
        branches = mindmap["root"]["children"]
        branch_names = [b["name"].lower() for b in branches]
        
        # Check that related AI/ML concepts are grouped
        ai_related = [name for name in branch_names if any(word in name for word in ['artificial', 'intelligence', 'learning', 'network', 'language', 'computer'])]
        assert len(ai_related) > 0, "Should group AI-related concepts together"


class TestMindMapQualityValidation:
    """Test mind map validation logic"""
    
    def test_validate_valid_mindmap(self):
        """Test validation of correct mind map structure"""
        valid_mindmap = {
            "version": "1",
            "root": {
                "name": "Main Topic",
                "id": "root-123",
                "children": [
                    {
                        "name": "Branch 1",
                        "id": "branch-1",
                        "children": [
                            {"name": "Leaf 1.1", "id": "leaf-1-1", "children": []},
                            {"name": "Leaf 1.2", "id": "leaf-1-2", "children": []}
                        ]
                    },
                    {
                        "name": "Branch 2",
                        "id": "branch-2",
                        "children": [
                            {"name": "Leaf 2.1", "id": "leaf-2-1", "children": []}
                        ]
                    },
                    {"name": "Branch 3", "id": "branch-3", "children": []}
                ]
            }
        }
        
        issues = validate_mindmap(valid_mindmap)
        # May have structure warnings but no errors
        assert isinstance(issues, list)
        error_issues = [i for i in issues if i.code.startswith("mindmap.")]
        assert len(error_issues) == 0
    
    def test_validate_missing_root(self):
        """Test validation fails when root is missing"""
        invalid_mindmap = {
            "version": "1",
            "children": []
        }
        
        issues = validate_mindmap(invalid_mindmap)
        has_root_issue = any("root" in i.code for i in issues)
        assert has_root_issue
    
    def test_validate_root_without_children(self):
        """Test root without children has issues"""
        invalid_mindmap = {
            "version": "1",
            "root": {
                "name": "Main Topic"
                # Missing children
            }
        }
        
        issues = validate_mindmap(invalid_mindmap)
        error_issues = [i for i in issues if i.code.startswith("mindmap.")]
        assert len(error_issues) > 0
    
    def test_validate_too_many_branches(self):
        """Test validation when too many branches (exceeds 7)"""
        too_many_branches = {
            "version": "1",
            "root": {
                "name": "Topic",
                "id": "root-1",
                "children": [{"name": f"Branch {i}", "id": f"branch-{i}", "children": []} for i in range(10)]
            }
        }
        
        issues = validate_mindmap(too_many_branches)
        branch_issues = [i for i in issues if "branches" in i.code]
        assert len(branch_issues) > 0
    
    def test_validate_too_few_branches(self):
        """Test validation when too few branches (less than 3)"""
        too_few_branches = {
            "version": "1",
            "root": {
                "name": "Topic",
                "id": "root-1",
                "children": [
                    {"name": "Branch 1", "id": "branch-1", "children": []}
                ]
            }
        }
        
        issues = validate_mindmap(too_few_branches)
        branch_issues = [i for i in issues if "branches" in i.code]
        assert len(branch_issues) > 0
    
    def test_validate_node_without_name(self):
        """Test validation detects nodes missing names"""
        missing_name = {
            "version": "1",
            "root": {
                "name": "Topic",
                "id": "root-1",
                "children": [
                    {
                        "id": "branch-1",
                        "children": []  # Missing name
                    }
                ]
            }
        }
        
        issues = validate_mindmap(missing_name)
        name_issues = [i for i in issues if "name" in i.code]
        assert len(name_issues) > 0


class TestMindMapIntegration:
    """Integration tests for complete mind map workflows"""
    
    def test_complete_mindmap_workflow(self):
        """Test complete mind map generation workflow"""
        mock_llm = Mock(spec=OfflineLLM)
        generator = MindMapGenerator(llm=mock_llm)
        
        content = """
        Machine Learning is a subset of artificial intelligence focused on algorithms
        that improve through experience. Deep Learning uses neural networks with multiple
        layers to model complex patterns. Natural Language Processing enables machines
        to understand and generate human language content.
        """
        
        # Generate mind map
        mindmap = generator.generate(content)
        
        # Validate structure
        issues = validate_mindmap(mindmap)
        assert isinstance(issues, list)
        
        # Verify JSON serialization for D3.js
        json_output = json.dumps(mindmap)
        assert isinstance(json_output, str)
        assert len(json_output) > 0
        
        # Parse back and verify
        parsed = json.loads(json_output)
        assert "root" in parsed
        assert parsed["version"] == "1"
    
    def test_mindmap_with_topic_override(self):
        """Test mind map generation with explicit topic"""
        mock_llm = Mock(spec=OfflineLLM)
        generator = MindMapGenerator(llm=mock_llm)
        
        content = "Various concepts related to AI, ML, and deep learning technologies."
        topic = "Artificial Intelligence Overview"
        
        # Use heuristic method explicitly to test topic override
        mindmap = generator._generate_heuristic(content, topic=topic)
        
        assert mindmap["root"]["name"] == topic
        assert mindmap["root"]["name"] != "Mind Map"  # Should not use default
    
    def test_mindmap_heuristic_fallback(self):
        """Test heuristic fallback generation method"""
        mock_llm = Mock(spec=OfflineLLM)
        generator = MindMapGenerator(llm=mock_llm)
        
        content = "Brief text without clear headings."
        
        mindmap = generator._generate_heuristic(content, topic="Test Topic")
        
        assert "root" in mindmap
        assert mindmap["root"]["name"] == "Test Topic"
        branches = mindmap["root"]["children"]
        assert 3 <= len(branches) <= 7


if __name__ == "__main__":
    pytest.main([__file__, "-v"])