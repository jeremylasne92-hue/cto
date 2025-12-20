import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from src.api import app
from src.models import QuizType, PedagogyStatus
from src.services.database import DatabaseManager


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_pedagogy_service():
    with patch('src.api.pedagogy.pedagogy_service') as mock_service:
        mock_service.generate_quiz = Mock(return_value="quiz-123")
        mock_service.get_quiz = Mock(return_value=Mock(
            quiz_id="quiz-123",
            status=PedagogyStatus.COMPLETED,
            quiz_type=QuizType.MCQ,
            questions=[
                {
                    "question_text": "What is AI?",
                    "question_type": "mcq",
                    "options": [
                        {"text": "Artificial Intelligence", "is_correct": True},
                        {"text": "Animal Intelligence", "is_correct": False}
                    ],
                    "explanation": "AI stands for Artificial Intelligence",
                    "metadata": {}
                }
            ],
            model_used="mistral-7b",
            metadata={},
            created_at="2024-01-01T00:00:00",
            error_message=None
        ))
        mock_service.generate_mindmap = Mock(return_value="mindmap-123")
        mock_service.get_mindmap = Mock(return_value=Mock(
            mindmap_id="mindmap-123",
            status=PedagogyStatus.COMPLETED,
            root_node=Mock(
                id="node-1",
                content="Main Topic",
                summary="Overview",
                level=0,
                parent_id=None,
                children_ids=["node-2"],
                metadata={}
            ),
            nodes=[],
            model_used="phi-2",
            metadata={},
            created_at="2024-01-01T00:00:00",
            error_message=None
        ))
        mock_service.model_manager = Mock(
            hardware_benchmark=Mock(
                cpu_score=8.0,
                ram_gb=16.0,
                gpu_available=True,
                gpu_memory_gb=8.0
            ),
            check_model_availability=Mock(return_value=Mock(
                tier="premium",
                available=True,
                loaded=False,
                ram_requirement_gb=16.0,
                gpu_requirement_gb=8.0
            )),
            cloud_api_url="https://api.example.com",
            loaded_model_name="mistral-7b"
        )
        yield mock_service


class TestPedagogyAPI:
    """Test pedagogy API endpoints"""
    
    def test_generate_mcq_quiz(self, client, mock_pedagogy_service):
        response = client.post(
            "/pedagogy/quiz",
            json={
                "source_id": "doc-123",
                "config": {
                    "quiz_type": "mcq",
                    "num_questions": 5,
                    "difficulty": "medium",
                    "include_explanations": True
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "quiz_id" in data
        assert data["quiz_id"] == "quiz-123"
        assert "message" in data
        assert "status_endpoint" in data
    
    def test_generate_quiz_with_chunk_ids(self, client, mock_pedagogy_service):
        response = client.post(
            "/pedagogy/quiz",
            json={
                "chunk_ids": ["chunk-1", "chunk-2"],
                "config": {
                    "quiz_type": "fill_blank",
                    "num_questions": 3
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "quiz_id" in data
    
    def test_generate_quiz_missing_source(self, client, mock_pedagogy_service):
        response = client.post(
            "/pedagogy/quiz",
            json={
                "config": {
                    "quiz_type": "mcq",
                    "num_questions": 5
                }
            }
        )
        
        assert response.status_code == 400
        assert "source_id or chunk_ids" in response.json()["detail"]
    
    def test_get_quiz(self, client, mock_pedagogy_service):
        response = client.get("/pedagogy/quiz/quiz-123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["quiz_id"] == "quiz-123"
        assert data["status"] == "completed"
        assert "questions" in data
        assert len(data["questions"]) > 0
    
    def test_get_quiz_not_found(self, client, mock_pedagogy_service):
        mock_pedagogy_service.get_quiz = Mock(return_value=None)
        
        response = client.get("/pedagogy/quiz/nonexistent")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_generate_mindmap(self, client, mock_pedagogy_service):
        response = client.post(
            "/pedagogy/mindmap",
            json={
                "source_id": "doc-123",
                "config": {
                    "max_depth": 4,
                    "max_children_per_node": 7,
                    "include_summaries": True
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "mindmap_id" in data
        assert data["mindmap_id"] == "mindmap-123"
        assert "message" in data
        assert "status_endpoint" in data
    
    def test_generate_mindmap_with_defaults(self, client, mock_pedagogy_service):
        response = client.post(
            "/pedagogy/mindmap",
            json={
                "source_id": "doc-123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "mindmap_id" in data
    
    def test_generate_mindmap_missing_source(self, client, mock_pedagogy_service):
        response = client.post(
            "/pedagogy/mindmap",
            json={}
        )
        
        assert response.status_code == 400
    
    def test_get_mindmap(self, client, mock_pedagogy_service):
        response = client.get("/pedagogy/mindmap/mindmap-123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["mindmap_id"] == "mindmap-123"
        assert data["status"] == "completed"
        assert "root_node" in data
        assert "nodes" in data
    
    def test_get_mindmap_not_found(self, client, mock_pedagogy_service):
        mock_pedagogy_service.get_mindmap = Mock(return_value=None)
        
        response = client.get("/pedagogy/mindmap/nonexistent")
        
        assert response.status_code == 404
    
    def test_get_models_status(self, client, mock_pedagogy_service):
        response = client.get("/pedagogy/models/status")
        
        assert response.status_code == 200
        data = response.json()
        assert "hardware" in data
        assert "models" in data
        assert "cloud_configured" in data
        assert "selected_model" in data
        
        assert "mistral-7b" in data["models"]
        assert "phi-2" in data["models"]
        
        assert data["hardware"]["cpu_score"] > 0
        assert data["hardware"]["ram_gb"] > 0
    
    def test_quiz_types_validation(self, client, mock_pedagogy_service):
        for quiz_type in ["mcq", "fill_blank", "matching"]:
            response = client.post(
                "/pedagogy/quiz",
                json={
                    "source_id": "doc-123",
                    "config": {
                        "quiz_type": quiz_type,
                        "num_questions": 3
                    }
                }
            )
            assert response.status_code == 200
    
    def test_quiz_num_questions_validation(self, client, mock_pedagogy_service):
        response = client.post(
            "/pedagogy/quiz",
            json={
                "source_id": "doc-123",
                "config": {
                    "quiz_type": "mcq",
                    "num_questions": 0
                }
            }
        )
        
        assert response.status_code == 422
    
    def test_mindmap_max_depth_validation(self, client, mock_pedagogy_service):
        response = client.post(
            "/pedagogy/mindmap",
            json={
                "source_id": "doc-123",
                "config": {
                    "max_depth": 0
                }
            }
        )
        
        assert response.status_code == 422


class TestPedagogyAPIWithRealDB:
    """Test API with real database for integration"""
    
    @pytest.fixture
    def setup_db(self, tmp_path):
        db_path = tmp_path / "test_api.db"
        db_manager = DatabaseManager(str(db_path))
        db_manager.create_tables()
        
        doc_id = "doc-api-test"
        doc_data = {
            "id": doc_id,
            "source_type": "plain_text",
            "content": "Test content for API",
            "metadata_json": {},
            "hash_sha256": "test_hash",
            "status": "completed"
        }
        db_manager.insert_document(doc_data)
        
        chunks_data = [{
            "id": "chunk-api-1",
            "document_id": doc_id,
            "content": "Machine learning is a field of AI.",
            "chunk_index": 0,
            "start_char": 0,
            "end_char": 50,
            "chunk_hash": "hash1",
            "metadata_json": {}
        }]
        db_manager.insert_chunks(chunks_data)
        
        return db_manager, doc_id
    
    def test_full_workflow(self, client, setup_db):
        db_manager, doc_id = setup_db
        
        with patch('src.api.pedagogy.pedagogy_service.model_manager.generate') as mock_generate:
            mock_generate.return_value = (
                json.dumps({
                    "questions": [
                        {
                            "question_text": "What is ML?",
                            "options": [
                                {"text": "Machine Learning", "is_correct": True},
                                {"text": "Manual Learning", "is_correct": False}
                            ],
                            "explanation": "ML stands for Machine Learning"
                        }
                    ]
                }),
                "test-model"
            )
            
            response = client.post(
                "/pedagogy/quiz",
                json={
                    "source_id": doc_id,
                    "config": {
                        "quiz_type": "mcq",
                        "num_questions": 1
                    }
                }
            )
            
            assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
