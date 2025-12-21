import pytest
import json
import time
from unittest.mock import Mock, MagicMock, patch
from backend.core.transformation.quiz_generator import QuizGenerator
from backend.core.transformation.llm_manager import LLMManager

class TestQuizGenerator:
    
    @pytest.fixture
    def mock_llm_manager(self):
        return Mock(spec=LLMManager)

    @pytest.fixture
    def generator(self, mock_llm_manager):
        return QuizGenerator(llm_manager=mock_llm_manager)

    @pytest.fixture
    def sample_content(self):
        return ["Python is a high-level, general-purpose programming language.", "Its design philosophy emphasizes code readability."]

    def test_mcq_single_generation(self, generator, mock_llm_manager, sample_content):
        # Mock response
        expected_response = [{
            "question": "What is Python?",
            "options": ["A snake", "A programming language", "A car", "A planet"],
            "answer": "A programming language"
        }]
        mock_llm_manager.generate.return_value = json.dumps(expected_response)

        result = generator.generate_quiz(sample_content, 'mcq_single', difficulty=3)
        
        assert result == expected_response
        assert mock_llm_manager.generate.called
        # Verify prompt contained instruction for mcq_single and difficulty
        args, _ = mock_llm_manager.generate.call_args
        assert "mcq_single" in args[0]
        assert "4 options" in args[0]
        assert "Difficulty level: 3/10" in args[0]

    def test_mcq_multiple_generation(self, generator, mock_llm_manager, sample_content):
        expected_response = [{
            "question": "Select valid Python characteristics",
            "options": ["High-level", "Compiled", "General-purpose", "Low-level", "Snake-based"],
            "answers": ["High-level", "General-purpose"]
        }]
        mock_llm_manager.generate.return_value = json.dumps(expected_response)

        result = generator.generate_quiz(sample_content, 'mcq_multiple')
        assert result == expected_response

    def test_fill_blank_generation(self, generator, mock_llm_manager, sample_content):
        expected_response = [{
            "question": "Python design philosophy emphasizes _____ readability.",
            "answer": "code"
        }]
        mock_llm_manager.generate.return_value = json.dumps(expected_response)
        
        result = generator.generate_quiz(sample_content, 'fill_blank')
        assert result == expected_response

    def test_matching_generation(self, generator, mock_llm_manager, sample_content):
        expected_response = [{
            "question": "Match the concepts",
            "pairs": [{"concept": "Python", "definition": "Language"}, {"concept": "Readability", "definition": "Philosophy"}]
        }]
        mock_llm_manager.generate.return_value = json.dumps(expected_response)
        
        result = generator.generate_quiz(sample_content, 'matching')
        assert result == expected_response

    def test_ordering_generation(self, generator, mock_llm_manager, sample_content):
        expected_response = [{
            "question": "Order the steps",
            "correct_order": ["Step 1", "Step 2", "Step 3"],
            "scrambled_order": ["Step 2", "Step 1", "Step 3"]
        }]
        mock_llm_manager.generate.return_value = json.dumps(expected_response)
        
        result = generator.generate_quiz(sample_content, 'ordering')
        assert result == expected_response

    def test_caching(self, generator, mock_llm_manager, sample_content):
        mock_llm_manager.generate.return_value = json.dumps([{"question": "Q1", "options": ["A","B","C","D"], "answer": "A"}])
        
        # First call
        generator.generate_quiz(sample_content, 'mcq_single')
        assert mock_llm_manager.generate.call_count == 1
        
        # Second call with same content/params
        generator.generate_quiz(sample_content, 'mcq_single')
        assert mock_llm_manager.generate.call_count == 1 # Should use cache

    def test_validation_failure(self, generator, mock_llm_manager, sample_content):
        # Invalid structure (missing options)
        mock_llm_manager.generate.return_value = json.dumps([{"question": "Q1", "answer": "A"}])
        
        with pytest.raises(ValueError, match="validation"):
            generator.generate_quiz(sample_content, 'mcq_single')

    def test_validation_failure_trivial(self, generator, mock_llm_manager, sample_content):
        # Mock empty list (trivial)
        mock_llm_manager.generate.return_value = json.dumps([])
        
        with pytest.raises(ValueError, match="validation"):
            generator.generate_quiz(sample_content, 'mcq_single')

    def test_performance(self, generator, mock_llm_manager, sample_content):
        # Mock fast response
        mock_llm_manager.generate.return_value = json.dumps([{"question": "Q1", "options": ["A","B","C","D"], "answer": "A"}])
        
        start_time = time.time()
        for i in range(100):
             # Vary content to bypass cache
             generator.generate_quiz(sample_content + [str(i)], 'mcq_single')
             
        duration = time.time() - start_time
        assert duration < 10.0

class TestLLMManager:
    def test_local_success(self):
        manager = LLMManager()
        with patch.object(manager, '_call_local_model') as mock_local:
            mock_local.return_value = "Local response"
            response = manager.generate("prompt")
            assert response == "Local response"

    def test_fallback_success(self):
        manager = LLMManager()
        with patch.object(manager, '_call_local_model') as mock_local:
            mock_local.side_effect = Exception("Local model offline")
            
            with patch.object(manager, '_call_cloud_api') as mock_cloud:
                mock_cloud.return_value = "Cloud response"
                
                response = manager.generate("prompt")
                
                assert response == "Cloud response"
                assert mock_local.called
                assert mock_cloud.called

    def test_all_fail(self):
        manager = LLMManager()
        with patch.object(manager, '_call_local_model') as mock_local:
            mock_local.side_effect = Exception("Local model offline")
            
            with patch.object(manager, '_call_cloud_api') as mock_cloud:
                mock_cloud.side_effect = Exception("Cloud offline")
                
                with pytest.raises(Exception):
                    manager.generate("prompt")
