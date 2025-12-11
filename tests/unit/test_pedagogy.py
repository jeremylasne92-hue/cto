import pytest
import json
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from src.models import (
    QuizType, QuizRequest, QuizConfig, MindMapRequest, MindMapConfig,
    PedagogyStatus, ModelTier
)
from src.services.pedagogy import PedagogyService
from src.services.model_manager import ModelManager, HardwareBenchmark
from src.services.prompts import PromptBuilder, PromptTemplates


class TestPromptTemplates:
    """Test prompt template generation"""
    
    def test_mcq_quiz_prompt(self):
        prompt = PromptTemplates.mcq_quiz_prompt("Test content", 5, "medium")
        assert "Test content" in prompt
        assert "5" in prompt
        assert "medium" in prompt
        assert "multiple-choice" in prompt
        assert "JSON" in prompt
    
    def test_fill_blank_quiz_prompt(self):
        prompt = PromptTemplates.fill_blank_quiz_prompt("Test content", 3, "easy")
        assert "Test content" in prompt
        assert "3" in prompt
        assert "easy" in prompt
        assert "fill-in-the-blank" in prompt
    
    def test_matching_quiz_prompt(self):
        prompt = PromptTemplates.matching_quiz_prompt("Test content", 4, "hard")
        assert "Test content" in prompt
        assert "4" in prompt
        assert "hard" in prompt
        assert "matching" in prompt
    
    def test_mindmap_prompt(self):
        prompt = PromptTemplates.mindmap_prompt("Test content", 4, 7)
        assert "Test content" in prompt
        assert "4" in prompt
        assert "7" in prompt
        assert "hierarchical" in prompt


class TestPromptBuilder:
    """Test prompt building from chunks"""
    
    def test_combine_chunks(self):
        chunks = [
            {"content": "First chunk"},
            {"content": "Second chunk"},
            {"content": "Third chunk"}
        ]
        
        combined = PromptBuilder.combine_chunks(chunks, max_length=1000)
        assert "First chunk" in combined
        assert "Second chunk" in combined
        assert "Third chunk" in combined
    
    def test_combine_chunks_max_length(self):
        chunks = [
            {"content": "A" * 100},
            {"content": "B" * 100},
            {"content": "C" * 100}
        ]
        
        combined = PromptBuilder.combine_chunks(chunks, max_length=150)
        assert len(combined) <= 150
    
    def test_build_mcq_prompt(self):
        chunks = [{"content": "Test content"}]
        prompt = PromptBuilder.build_mcq_prompt(chunks, 5, "medium")
        assert "Test content" in prompt
        assert "JSON" in prompt


class TestModelManager:
    """Test model selection and management"""
    
    @patch('src.services.model_manager.psutil')
    def test_hardware_benchmark(self, mock_psutil):
        mock_psutil.cpu_count.return_value = 4
        mock_psutil.cpu_freq.return_value = Mock(current=2500)
        mock_psutil.virtual_memory.return_value = Mock(total=16 * 1024 ** 3)
        
        from src.services.model_manager import HardwareBenchmarker
        benchmark = HardwareBenchmarker.get_benchmark()
        
        assert benchmark.cpu_score > 0
        assert benchmark.ram_gb > 0
    
    def test_model_availability_check(self):
        manager = ModelManager()
        
        availability = manager.check_model_availability("mistral-7b")
        assert availability.model_name == "mistral-7b"
        assert availability.tier == ModelTier.PREMIUM
        assert isinstance(availability.available, bool)
    
    def test_model_selection_fallback(self):
        manager = ModelManager()
        manager.hardware_benchmark = HardwareBenchmark(
            cpu_score=2.0,
            ram_gb=4.0,
            gpu_available=False,
            gpu_memory_gb=0.0,
            disk_speed_mbps=50.0
        )
        
        model_name, tier = manager.select_model()
        assert tier == ModelTier.CLOUD


class TestPedagogyService:
    """Test pedagogy service functionality"""
    
    @pytest.fixture
    def mock_db_manager(self):
        db_manager = Mock()
        db_manager.create_tables = Mock()
        db_manager.insert_quiz = Mock(return_value="quiz-123")
        db_manager.update_quiz = Mock()
        db_manager.get_quiz = Mock(return_value={
            "id": "quiz-123",
            "source_id": "doc-1",
            "quiz_type": "mcq",
            "status": "completed",
            "model_used": "mistral-7b",
            "metadata": {},
            "created_at": datetime.utcnow(),
            "completed_at": datetime.utcnow(),
            "error_message": None
        })
        db_manager.get_chunks_by_document_id = Mock(return_value=[
            {"id": "chunk-1", "content": "Test content", "metadata_json": {}}
        ])
        db_manager.get_questions_by_quiz_id = Mock(return_value=[])
        return db_manager
    
    @pytest.fixture
    def mock_model_manager(self):
        model_manager = Mock()
        model_manager.generate = Mock(return_value=(
            json.dumps({
                "questions": [
                    {
                        "question_text": "What is AI?",
                        "options": [
                            {"text": "Artificial Intelligence", "is_correct": True},
                            {"text": "Animal Intelligence", "is_correct": False},
                            {"text": "Alien Intelligence", "is_correct": False},
                            {"text": "Automated Intelligence", "is_correct": False}
                        ],
                        "explanation": "AI stands for Artificial Intelligence"
                    }
                ]
            }),
            "mistral-7b"
        ))
        return model_manager
    
    def test_generate_quiz_creates_quiz(self, mock_db_manager, mock_model_manager):
        service = PedagogyService(
            db_manager=mock_db_manager,
            model_manager=mock_model_manager
        )
        
        request = QuizRequest(
            source_id="doc-1",
            config=QuizConfig(quiz_type=QuizType.MCQ, num_questions=5)
        )
        
        quiz_id = service.generate_quiz(request)
        
        assert quiz_id is not None
        mock_db_manager.insert_quiz.assert_called_once()
    
    def test_generate_quiz_validates_input(self, mock_db_manager, mock_model_manager):
        service = PedagogyService(
            db_manager=mock_db_manager,
            model_manager=mock_model_manager
        )
        
        request = QuizRequest(
            source_id=None,
            chunk_ids=None,
            config=QuizConfig(quiz_type=QuizType.MCQ, num_questions=5)
        )
        
        with pytest.raises(ValueError):
            service._get_chunks_for_generation(None, None)
    
    def test_extract_json_from_text(self, mock_db_manager, mock_model_manager):
        service = PedagogyService(
            db_manager=mock_db_manager,
            model_manager=mock_model_manager
        )
        
        text = '{"key": "value"}'
        result = service._extract_json_from_text(text)
        assert result == {"key": "value"}
    
    def test_extract_json_with_markdown(self, mock_db_manager, mock_model_manager):
        service = PedagogyService(
            db_manager=mock_db_manager,
            model_manager=mock_model_manager
        )
        
        text = '```json\n{"key": "value"}\n```'
        result = service._extract_json_from_text(text)
        assert result == {"key": "value"}
    
    def test_get_quiz_retrieves_quiz(self, mock_db_manager, mock_model_manager):
        service = PedagogyService(
            db_manager=mock_db_manager,
            model_manager=mock_model_manager
        )
        
        quiz = service.get_quiz("quiz-123")
        
        assert quiz is not None
        assert quiz.quiz_id == "quiz-123"
        assert quiz.status == PedagogyStatus.COMPLETED
    
    def test_get_quiz_returns_none_for_missing(self, mock_db_manager, mock_model_manager):
        mock_db_manager.get_quiz = Mock(return_value=None)
        
        service = PedagogyService(
            db_manager=mock_db_manager,
            model_manager=mock_model_manager
        )
        
        quiz = service.get_quiz("nonexistent")
        assert quiz is None
    
    def test_generate_mindmap_creates_mindmap(self, mock_db_manager, mock_model_manager):
        mock_db_manager.insert_mindmap = Mock(return_value="mindmap-123")
        mock_db_manager.get_mindmap = Mock(return_value={
            "id": "mindmap-123",
            "source_id": "doc-1",
            "status": "completed",
            "model_used": "phi-2",
            "root_node_id": "node-1",
            "metadata": {},
            "created_at": datetime.utcnow(),
            "completed_at": datetime.utcnow(),
            "error_message": None
        })
        mock_db_manager.get_mindmap_nodes = Mock(return_value=[])
        
        mock_model_manager.generate = Mock(return_value=(
            json.dumps({
                "root": {
                    "content": "Main Topic",
                    "summary": "Overview",
                    "children": [
                        {
                            "content": "Subtopic 1",
                            "summary": "Details",
                            "children": []
                        }
                    ]
                }
            }),
            "phi-2"
        ))
        
        service = PedagogyService(
            db_manager=mock_db_manager,
            model_manager=mock_model_manager
        )
        
        request = MindMapRequest(
            source_id="doc-1",
            config=MindMapConfig(max_depth=4)
        )
        
        mindmap_id = service.generate_mindmap(request)
        
        assert mindmap_id is not None
        mock_db_manager.insert_mindmap.assert_called_once()
    
    def test_process_quiz_response_mcq(self, mock_db_manager, mock_model_manager):
        service = PedagogyService(
            db_manager=mock_db_manager,
            model_manager=mock_model_manager
        )
        
        response_data = {
            "questions": [
                {
                    "question_text": "What is AI?",
                    "options": [
                        {"text": "Artificial Intelligence", "is_correct": True},
                        {"text": "Animal Intelligence", "is_correct": False}
                    ],
                    "explanation": "AI stands for Artificial Intelligence"
                }
            ]
        }
        
        questions = service._process_quiz_response(
            "quiz-123",
            QuizType.MCQ,
            response_data,
            True
        )
        
        assert len(questions) == 1
        assert questions[0]["question_text"] == "What is AI?"
        assert "options" in questions[0]["question_data"]
    
    def test_process_mindmap_response(self, mock_db_manager, mock_model_manager):
        service = PedagogyService(
            db_manager=mock_db_manager,
            model_manager=mock_model_manager
        )
        
        response_data = {
            "root": {
                "content": "Main Topic",
                "summary": "Overview",
                "children": [
                    {
                        "content": "Subtopic",
                        "summary": "Details",
                        "children": []
                    }
                ]
            }
        }
        
        nodes, root_id = service._process_mindmap_response(
            "mindmap-123",
            response_data,
            True
        )
        
        assert len(nodes) == 2
        assert root_id is not None
        assert any(node["content"] == "Main Topic" for node in nodes)
        assert any(node["content"] == "Subtopic" for node in nodes)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
