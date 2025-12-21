import json
import hashlib
import logging
from typing import List, Dict, Any, Optional
from .llm_manager import LLMManager

logger = logging.getLogger(__name__)

class QuizGenerator:
    def __init__(self, llm_manager: Optional[LLMManager] = None):
        self.llm_manager = llm_manager or LLMManager()
        self.cache = {}

    def generate_quiz(self, content_chunks: List[str], quiz_type: str, difficulty: int = 5, num_questions: int = 5) -> Any:
        """
        Generates a quiz based on content chunks.
        """
        # Input validation
        if not content_chunks:
            raise ValueError("Content chunks cannot be empty")
        if not (1 <= difficulty <= 10):
            raise ValueError("Difficulty must be between 1 and 10")
        
        valid_types = ['mcq_single', 'mcq_multiple', 'fill_blank', 'matching', 'ordering']
        if quiz_type not in valid_types:
            raise ValueError(f"Invalid quiz type. Must be one of {valid_types}")

        # Hash for caching
        content_combined = "\n".join(content_chunks)
        cache_key = hashlib.sha256(f"{content_combined}:{quiz_type}:{difficulty}:{num_questions}".encode()).hexdigest()
        
        if cache_key in self.cache:
            logger.info("Returning cached quiz")
            return self.cache[cache_key]

        # Construct Prompt
        prompt = self._construct_prompt(content_combined, quiz_type, difficulty, num_questions)
        system_prompt = (
            "You are an expert educational content creator. "
            "Analyze the provided text and generate a quiz in strict JSON format. "
            "Ensure questions are non-trivial and distractors are plausible."
        )

        try:
            response = self.llm_manager.generate(prompt, system_prompt=system_prompt, temperature=0.7)
            quiz_data = self._parse_response(response)
            
            # Post-processing and Validation
            if self._validate_quiz(quiz_data, quiz_type, num_questions):
                self.cache[cache_key] = quiz_data
                return quiz_data
            else:
                raise ValueError("Generated quiz failed validation")
                
        except Exception as e:
            logger.error(f"Quiz generation failed: {e}")
            raise

    def _construct_prompt(self, content: str, quiz_type: str, difficulty: int, num_questions: int) -> str:
        base_instruction = f"Generate {num_questions} questions of type '{quiz_type}' based on the text below. Difficulty level: {difficulty}/10."
        
        type_instructions = {
            'mcq_single': "Each question should have 4 options with exactly 1 correct answer. JSON format: [{'question': str, 'options': [str], 'answer': str}]",
            'mcq_multiple': "Each question should have 5+ options with 2+ correct answers. JSON format: [{'question': str, 'options': [str], 'answers': [str]}]",
            'fill_blank': "Provide a sentence with a missing key concept represented by '_____'. JSON format: [{'question': str, 'answer': str}]",
            'matching': "Generate pairs of concepts and definitions. JSON format: [{'question': str, 'pairs': [{'concept': str, 'definition': str}]}]",
            'ordering': "Provide a list of steps or events to be ordered chronologically or logically. JSON format: [{'question': str, 'correct_order': [str], 'scrambled_order': [str]}]"
        }
        
        instruction = f"{base_instruction}\n{type_instructions.get(quiz_type, '')}\n\nText:\n{content}"
        return instruction

    def _parse_response(self, response: str) -> Any:
        try:
            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.startswith("```"):
                clean_response = clean_response[3:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
            return json.loads(clean_response)
        except json.JSONDecodeError:
            raise ValueError("Failed to parse LLM response as JSON")

    def _validate_quiz(self, quiz_data: Any, quiz_type: str, num_questions: int) -> bool:
        if not isinstance(quiz_data, list):
            return False
            
        # Allow some flexibility in number of questions as LLMs can be imprecise
        if len(quiz_data) == 0:
            return False

        # Basic structure checks
        for q in quiz_data:
            if not isinstance(q, dict):
                return False
            if 'question' not in q:
                return False
            
            if quiz_type == 'mcq_single':
                if 'options' not in q or 'answer' not in q: return False
                if len(q['options']) != 4: return False 
                if q['answer'] not in q['options']: return False
            
            if quiz_type == 'mcq_multiple':
                if 'options' not in q or 'answers' not in q: return False
                if len(q['options']) < 5: return False 
                if len(q['answers']) < 2: return False 
                
            if quiz_type == 'ordering':
                 if 'correct_order' not in q: return False

            if quiz_type == 'matching':
                if 'pairs' not in q: return False
                 
        return True
