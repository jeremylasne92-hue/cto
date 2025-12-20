from typing import List, Dict, Any


class PromptTemplates:
    """Prompt templates for quiz and mind map generation"""
    
    @staticmethod
    def mcq_quiz_prompt(content: str, num_questions: int, difficulty: str = "medium") -> str:
        """Generate prompt for MCQ quiz"""
        return f"""You are an expert educational content creator. Based on the following content, generate {num_questions} multiple-choice questions at {difficulty} difficulty level.

Content:
{content}

Requirements:
1. Each question should have exactly 4 options (A, B, C, D)
2. Only ONE option should be correct
3. Questions should test understanding, not just memorization
4. Include a brief explanation for the correct answer
5. Ensure questions are clear and unambiguous

Output format (JSON):
{{
  "questions": [
    {{
      "question_text": "Question text here?",
      "options": [
        {{"text": "Option A", "is_correct": false}},
        {{"text": "Option B", "is_correct": true}},
        {{"text": "Option C", "is_correct": false}},
        {{"text": "Option D", "is_correct": false}}
      ],
      "explanation": "Explanation of why B is correct..."
    }}
  ]
}}

Generate the questions now:"""
    
    @staticmethod
    def fill_blank_quiz_prompt(content: str, num_questions: int, difficulty: str = "medium") -> str:
        """Generate prompt for fill-in-the-blank quiz"""
        return f"""You are an expert educational content creator. Based on the following content, generate {num_questions} fill-in-the-blank questions at {difficulty} difficulty level.

Content:
{content}

Requirements:
1. Each question should have a sentence with ONE blank (marked as ___)
2. Provide the correct answer and up to 3 alternative acceptable answers
3. Questions should test key concepts and terminology
4. Include a brief explanation
5. Ensure the sentence context makes the answer clear

Output format (JSON):
{{
  "questions": [
    {{
      "question_text": "What concept does this test?",
      "sentence_with_blank": "The ___ is responsible for...",
      "answer": {{
        "text": "correct answer",
        "alternatives": ["alt1", "alt2"]
      }},
      "explanation": "Explanation here..."
    }}
  ]
}}

Generate the questions now:"""
    
    @staticmethod
    def matching_quiz_prompt(content: str, num_pairs: int, difficulty: str = "medium") -> str:
        """Generate prompt for matching quiz"""
        return f"""You are an expert educational content creator. Based on the following content, generate {num_pairs} matching pairs at {difficulty} difficulty level.

Content:
{content}

Requirements:
1. Each pair should have a left item and a right item
2. Pairs should test relationships, definitions, or connections
3. All left items should be clearly distinguishable
4. All right items should be clearly distinguishable
5. Include a brief explanation

Output format (JSON):
{{
  "questions": [
    {{
      "question_text": "Match the following concepts with their descriptions:",
      "pairs": [
        {{"left": "Concept 1", "right": "Description 1"}},
        {{"left": "Concept 2", "right": "Description 2"}},
        {{"left": "Concept 3", "right": "Description 3"}}
      ],
      "explanation": "These concepts relate to..."
    }}
  ]
}}

Generate the matching pairs now:"""
    
    @staticmethod
    def mindmap_prompt(content: str, max_depth: int = 4, max_children: int = 7) -> str:
        """Generate prompt for mind map"""
        return f"""You are an expert at creating hierarchical mind maps. Based on the following content, create a structured mind map with a maximum depth of {max_depth} levels and maximum {max_children} children per node.

Content:
{content}

Requirements:
1. Start with a single root concept that captures the main topic
2. Each node should have:
   - A concise content/title (3-8 words)
   - An optional summary (1-2 sentences)
   - Child nodes representing subtopics or components
3. Organize information hierarchically from general to specific
4. Balance the tree - avoid one branch being much deeper than others
5. Use clear, descriptive labels
6. Maximum depth: {max_depth} levels
7. Maximum children per node: {max_children}

Output format (JSON):
{{
  "root": {{
    "content": "Main Topic",
    "summary": "Brief overview of the main topic",
    "children": [
      {{
        "content": "Subtopic 1",
        "summary": "Details about subtopic 1",
        "children": [
          {{
            "content": "Detail 1.1",
            "summary": "More specific information",
            "children": []
          }}
        ]
      }}
    ]
  }}
}}

Generate the mind map now:"""
    
    @staticmethod
    def post_process_instruction() -> str:
        """Instruction for JSON-only output"""
        return "\n\nIMPORTANT: Return ONLY valid JSON without any additional text or markdown formatting."


class PromptBuilder:
    """Builder for constructing prompts from multiple chunks"""
    
    @staticmethod
    def combine_chunks(chunks: List[Dict[str, Any]], max_length: int = 4000) -> str:
        """Combine multiple chunks into a single content string"""
        combined = []
        current_length = 0
        
        for chunk in chunks:
            content = chunk.get("content", "")
            if current_length + len(content) > max_length:
                if current_length == 0:
                    combined.append(content[:max_length])
                break
            combined.append(content)
            current_length += len(content)
        
        return "\n\n---\n\n".join(combined)
    
    @staticmethod
    def build_mcq_prompt(chunks: List[Dict[str, Any]], num_questions: int, difficulty: str = "medium") -> str:
        """Build MCQ prompt from chunks"""
        content = PromptBuilder.combine_chunks(chunks)
        prompt = PromptTemplates.mcq_quiz_prompt(content, num_questions, difficulty)
        prompt += PromptTemplates.post_process_instruction()
        return prompt
    
    @staticmethod
    def build_fill_blank_prompt(chunks: List[Dict[str, Any]], num_questions: int, difficulty: str = "medium") -> str:
        """Build fill-blank prompt from chunks"""
        content = PromptBuilder.combine_chunks(chunks)
        prompt = PromptTemplates.fill_blank_quiz_prompt(content, num_questions, difficulty)
        prompt += PromptTemplates.post_process_instruction()
        return prompt
    
    @staticmethod
    def build_matching_prompt(chunks: List[Dict[str, Any]], num_pairs: int, difficulty: str = "medium") -> str:
        """Build matching prompt from chunks"""
        content = PromptBuilder.combine_chunks(chunks)
        prompt = PromptTemplates.matching_quiz_prompt(content, num_pairs, difficulty)
        prompt += PromptTemplates.post_process_instruction()
        return prompt
    
    @staticmethod
    def build_mindmap_prompt(chunks: List[Dict[str, Any]], max_depth: int = 4, max_children: int = 7) -> str:
        """Build mind map prompt from chunks"""
        content = PromptBuilder.combine_chunks(chunks)
        prompt = PromptTemplates.mindmap_prompt(content, max_depth, max_children)
        prompt += PromptTemplates.post_process_instruction()
        return prompt
