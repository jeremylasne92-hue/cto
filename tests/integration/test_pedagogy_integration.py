import pytest
import json
import time
from unittest.mock import Mock, patch
from datetime import datetime

from src.models import (
    QuizType, QuizRequest, QuizConfig, MindMapRequest, MindMapConfig,
    PedagogyStatus
)
from src.services.pedagogy import PedagogyService
from src.services.database import DatabaseManager


class TestPedagogyIntegration:
    """Integration tests for pedagogy service with database"""
    
    @pytest.fixture
    def db_manager(self, tmp_path):
        db_path = tmp_path / "test_pedagogy.db"
        manager = DatabaseManager(str(db_path))
        manager.create_tables()
        return manager
    
    @pytest.fixture
    def mock_model_manager(self):
        model_manager = Mock()
        
        def mock_generate(prompt, max_tokens=2048, temperature=0.7):
            if "multiple-choice" in prompt:
                return (json.dumps({
                    "questions": [
                        {
                            "question_text": "What is machine learning?",
                            "options": [
                                {"text": "A subset of AI", "is_correct": True},
                                {"text": "A programming language", "is_correct": False},
                                {"text": "A database system", "is_correct": False},
                                {"text": "An operating system", "is_correct": False}
                            ],
                            "explanation": "Machine learning is a subset of artificial intelligence"
                        },
                        {
                            "question_text": "What is supervised learning?",
                            "options": [
                                {"text": "Learning with labeled data", "is_correct": True},
                                {"text": "Learning without data", "is_correct": False},
                                {"text": "Learning with unlabeled data", "is_correct": False},
                                {"text": "Learning by trial and error", "is_correct": False}
                            ],
                            "explanation": "Supervised learning uses labeled training data"
                        }
                    ]
                }), "mistral-7b")
            elif "fill-in-the-blank" in prompt:
                return (json.dumps({
                    "questions": [
                        {
                            "question_text": "Complete the sentence about neural networks",
                            "sentence_with_blank": "A ___ is the basic unit of a neural network",
                            "answer": {
                                "text": "neuron",
                                "alternatives": ["node", "perceptron"]
                            },
                            "explanation": "A neuron is the fundamental building block"
                        }
                    ]
                }), "phi-2")
            elif "matching" in prompt:
                return (json.dumps({
                    "questions": [
                        {
                            "question_text": "Match the ML algorithms with their types",
                            "pairs": [
                                {"left": "Linear Regression", "right": "Supervised"},
                                {"left": "K-Means", "right": "Unsupervised"},
                                {"left": "Decision Tree", "right": "Supervised"}
                            ],
                            "explanation": "Classification of common ML algorithms"
                        }
                    ]
                }), "mistral-7b")
            elif "hierarchical" in prompt:
                return (json.dumps({
                    "root": {
                        "content": "Machine Learning",
                        "summary": "Overview of machine learning concepts",
                        "children": [
                            {
                                "content": "Supervised Learning",
                                "summary": "Learning with labeled data",
                                "children": [
                                    {
                                        "content": "Classification",
                                        "summary": "Predicting categories",
                                        "children": []
                                    },
                                    {
                                        "content": "Regression",
                                        "summary": "Predicting continuous values",
                                        "children": []
                                    }
                                ]
                            },
                            {
                                "content": "Unsupervised Learning",
                                "summary": "Learning patterns from unlabeled data",
                                "children": [
                                    {
                                        "content": "Clustering",
                                        "summary": "Grouping similar data",
                                        "children": []
                                    }
                                ]
                            }
                        ]
                    }
                }), "phi-2")
        
        model_manager.generate = Mock(side_effect=mock_generate)
        return model_manager
    
    @pytest.fixture
    def service_with_data(self, db_manager, mock_model_manager):
        doc_id = "doc-test-123"
        doc_data = {
            "id": doc_id,
            "source_type": "plain_text",
            "content": "Machine learning is a subset of AI...",
            "metadata_json": {"title": "ML Intro"},
            "hash_sha256": "test_hash_123",
            "status": "completed"
        }
        db_manager.insert_document(doc_data)
        
        chunks_data = [
            {
                "id": "chunk-1",
                "document_id": doc_id,
                "content": "Machine learning is a subset of artificial intelligence that focuses on training algorithms.",
                "chunk_index": 0,
                "start_char": 0,
                "end_char": 100,
                "chunk_hash": "hash1",
                "metadata_json": {}
            },
            {
                "id": "chunk-2",
                "document_id": doc_id,
                "content": "Supervised learning uses labeled data to train models for prediction tasks.",
                "chunk_index": 1,
                "start_char": 100,
                "end_char": 200,
                "chunk_hash": "hash2",
                "metadata_json": {}
            }
        ]
        db_manager.insert_chunks(chunks_data)
        
        service = PedagogyService(
            db_manager=db_manager,
            model_manager=mock_model_manager
        )
        
        return service, doc_id
    
    def test_generate_mcq_quiz_end_to_end(self, service_with_data):
        service, doc_id = service_with_data
        
        request = QuizRequest(
            source_id=doc_id,
            config=QuizConfig(
                quiz_type=QuizType.MCQ,
                num_questions=2,
                difficulty="medium"
            )
        )
        
        quiz_id = service.generate_quiz(request)
        assert quiz_id is not None
        
        time.sleep(0.1)
        
        quiz = service.get_quiz(quiz_id)
        assert quiz is not None
        assert quiz.quiz_id == quiz_id
        assert quiz.quiz_type == QuizType.MCQ
    
    def test_generate_fill_blank_quiz_end_to_end(self, service_with_data):
        service, doc_id = service_with_data
        
        request = QuizRequest(
            source_id=doc_id,
            config=QuizConfig(
                quiz_type=QuizType.FILL_BLANK,
                num_questions=1,
                difficulty="easy"
            )
        )
        
        quiz_id = service.generate_quiz(request)
        assert quiz_id is not None
        
        time.sleep(0.1)
        
        quiz = service.get_quiz(quiz_id)
        assert quiz is not None
        assert quiz.quiz_type == QuizType.FILL_BLANK
    
    def test_generate_matching_quiz_end_to_end(self, service_with_data):
        service, doc_id = service_with_data
        
        request = QuizRequest(
            source_id=doc_id,
            config=QuizConfig(
                quiz_type=QuizType.MATCHING,
                num_questions=3,
                difficulty="hard"
            )
        )
        
        quiz_id = service.generate_quiz(request)
        assert quiz_id is not None
        
        time.sleep(0.1)
        
        quiz = service.get_quiz(quiz_id)
        assert quiz is not None
        assert quiz.quiz_type == QuizType.MATCHING
    
    def test_generate_quiz_with_chunk_ids(self, service_with_data):
        service, doc_id = service_with_data
        
        request = QuizRequest(
            chunk_ids=["chunk-1"],
            config=QuizConfig(
                quiz_type=QuizType.MCQ,
                num_questions=1
            )
        )
        
        quiz_id = service.generate_quiz(request)
        assert quiz_id is not None
        
        quiz = service.get_quiz(quiz_id)
        assert quiz is not None
    
    def test_generate_mindmap_end_to_end(self, service_with_data):
        service, doc_id = service_with_data
        
        request = MindMapRequest(
            source_id=doc_id,
            config=MindMapConfig(
                max_depth=3,
                max_children_per_node=5,
                include_summaries=True
            )
        )
        
        mindmap_id = service.generate_mindmap(request)
        assert mindmap_id is not None
        
        time.sleep(0.1)
        
        mindmap = service.get_mindmap(mindmap_id)
        assert mindmap is not None
        assert mindmap.mindmap_id == mindmap_id
        assert mindmap.root_node is not None
        assert len(mindmap.nodes) > 0
    
    def test_mindmap_hierarchy_structure(self, service_with_data):
        service, doc_id = service_with_data
        
        request = MindMapRequest(
            source_id=doc_id,
            config=MindMapConfig(max_depth=4)
        )
        
        mindmap_id = service.generate_mindmap(request)
        time.sleep(0.1)
        
        mindmap = service.get_mindmap(mindmap_id)
        
        assert mindmap.root_node.level == 0
        
        child_nodes = [n for n in mindmap.nodes if n.parent_id == mindmap.root_node.id]
        assert len(child_nodes) > 0
        
        for child in child_nodes:
            assert child.level > mindmap.root_node.level
    
    def test_quiz_validation_formats(self, service_with_data):
        service, doc_id = service_with_data
        
        request = QuizRequest(
            source_id=doc_id,
            config=QuizConfig(
                quiz_type=QuizType.MCQ,
                num_questions=2
            )
        )
        
        quiz_id = service.generate_quiz(request)
        time.sleep(0.1)
        
        quiz = service.get_quiz(quiz_id)
        
        for question in quiz.questions:
            assert "question_text" in question
            assert question["question_type"] == QuizType.MCQ.value
            if question["question_type"] == QuizType.MCQ.value:
                assert "options" in question
                assert len(question["options"]) > 0
    
    def test_multiple_quizzes_from_same_source(self, service_with_data):
        service, doc_id = service_with_data
        
        quiz_ids = []
        for quiz_type in [QuizType.MCQ, QuizType.FILL_BLANK, QuizType.MATCHING]:
            request = QuizRequest(
                source_id=doc_id,
                config=QuizConfig(
                    quiz_type=quiz_type,
                    num_questions=1
                )
            )
            quiz_id = service.generate_quiz(request)
            quiz_ids.append(quiz_id)
        
        time.sleep(0.2)
        
        for quiz_id in quiz_ids:
            quiz = service.get_quiz(quiz_id)
            assert quiz is not None
            assert quiz.quiz_id == quiz_id
    
    def test_quiz_error_handling_invalid_source(self, db_manager, mock_model_manager):
        service = PedagogyService(
            db_manager=db_manager,
            model_manager=mock_model_manager
        )
        
        request = QuizRequest(
            source_id="nonexistent-doc",
            config=QuizConfig(quiz_type=QuizType.MCQ, num_questions=5)
        )
        
        with pytest.raises(ValueError):
            service.generate_quiz(request)
    
    def test_mindmap_persistence(self, service_with_data):
        service, doc_id = service_with_data
        
        request = MindMapRequest(source_id=doc_id)
        mindmap_id = service.generate_mindmap(request)
        time.sleep(0.1)
        
        mindmap1 = service.get_mindmap(mindmap_id)
        mindmap2 = service.get_mindmap(mindmap_id)
        
        assert mindmap1.mindmap_id == mindmap2.mindmap_id
        assert len(mindmap1.nodes) == len(mindmap2.nodes)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
