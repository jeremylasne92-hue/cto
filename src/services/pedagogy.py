import json
import uuid
import logging
import re
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..models import (
    QuizType, QuizRequest, QuizResponse, MindMapRequest, MindMapResponse,
    PedagogyStatus, MCQQuestion, FillBlankQuestion, MatchingQuestion, MindMapNode
)
from .database import DatabaseManager
from .model_manager import ModelManager
from .prompts import PromptBuilder

logger = logging.getLogger(__name__)


class PedagogyService:
    """Service for AI-driven pedagogical transformations"""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None, model_manager: Optional[ModelManager] = None):
        self.db_manager = db_manager or DatabaseManager()
        self.model_manager = model_manager or ModelManager()
        
        self.db_manager.create_tables()
    
    def _extract_json_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from LLM response that might have extra text"""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            try:
                json_match = re.search(r'\{[\s\S]*\}', text)
                if json_match:
                    return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
            
            try:
                code_block_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
                if code_block_match:
                    return json.loads(code_block_match.group(1))
            except json.JSONDecodeError:
                pass
            
            logger.error(f"Failed to extract JSON from response: {text[:200]}")
            return None
    
    def _get_chunks_for_generation(self, source_id: Optional[str], chunk_ids: Optional[List[str]]) -> List[Dict[str, Any]]:
        """Get chunks for quiz/mindmap generation"""
        if chunk_ids:
            chunks = self.db_manager.get_chunks_by_ids(chunk_ids)
        elif source_id:
            chunks = self.db_manager.get_chunks_by_document_id(source_id)
        else:
            raise ValueError("Either source_id or chunk_ids must be provided")
        
        if not chunks:
            raise ValueError("No chunks found for the given source/chunk IDs")
        
        return chunks
    
    def generate_quiz(self, request: QuizRequest) -> str:
        """Generate a quiz from source chunks"""
        quiz_id = str(uuid.uuid4())
        
        try:
            quiz_data = {
                "id": quiz_id,
                "source_id": request.source_id,
                "quiz_type": request.config.quiz_type.value,
                "status": PedagogyStatus.PENDING.value,
                "metadata_json": {
                    "num_questions": request.config.num_questions,
                    "difficulty": request.config.difficulty,
                    "chunk_ids": request.chunk_ids or []
                }
            }
            
            self.db_manager.insert_quiz(quiz_data)
            
            self._generate_quiz_async(quiz_id, request)
            
            return quiz_id
            
        except Exception as e:
            logger.error(f"Failed to start quiz generation: {e}")
            self.db_manager.update_quiz(quiz_id, {
                "status": PedagogyStatus.FAILED.value,
                "error_message": str(e),
                "completed_at": datetime.utcnow()
            })
            raise
    
    def _generate_quiz_async(self, quiz_id: str, request: QuizRequest):
        """Generate quiz asynchronously"""
        try:
            self.db_manager.update_quiz(quiz_id, {"status": PedagogyStatus.RUNNING.value})
            
            chunks = self._get_chunks_for_generation(request.source_id, request.chunk_ids)
            
            if request.config.quiz_type == QuizType.MCQ:
                prompt = PromptBuilder.build_mcq_prompt(
                    chunks, 
                    request.config.num_questions, 
                    request.config.difficulty or "medium"
                )
            elif request.config.quiz_type == QuizType.FILL_BLANK:
                prompt = PromptBuilder.build_fill_blank_prompt(
                    chunks, 
                    request.config.num_questions, 
                    request.config.difficulty or "medium"
                )
            elif request.config.quiz_type == QuizType.MATCHING:
                prompt = PromptBuilder.build_matching_prompt(
                    chunks, 
                    request.config.num_questions, 
                    request.config.difficulty or "medium"
                )
            else:
                raise ValueError(f"Unsupported quiz type: {request.config.quiz_type}")
            
            response_text, model_used = self.model_manager.generate(prompt, max_tokens=2048, temperature=0.7)
            
            if not response_text:
                raise ValueError("LLM generation failed")
            
            response_data = self._extract_json_from_text(response_text)
            if not response_data:
                raise ValueError("Failed to parse LLM response as JSON")
            
            questions_data = self._process_quiz_response(
                quiz_id, 
                request.config.quiz_type, 
                response_data,
                request.config.include_explanations
            )
            
            self.db_manager.insert_questions(questions_data)
            
            self.db_manager.update_quiz(quiz_id, {
                "status": PedagogyStatus.COMPLETED.value,
                "model_used": model_used,
                "completed_at": datetime.utcnow()
            })
            
            logger.info(f"Quiz {quiz_id} generated successfully with {len(questions_data)} questions")
            
        except Exception as e:
            logger.error(f"Quiz generation failed: {e}")
            self.db_manager.update_quiz(quiz_id, {
                "status": PedagogyStatus.FAILED.value,
                "error_message": str(e),
                "completed_at": datetime.utcnow()
            })
    
    def _process_quiz_response(
        self, 
        quiz_id: str, 
        quiz_type: QuizType, 
        response_data: Dict[str, Any],
        include_explanations: bool
    ) -> List[Dict[str, Any]]:
        """Process and validate quiz response from LLM"""
        questions_data = []
        questions = response_data.get("questions", [])
        
        for idx, q in enumerate(questions):
            question_id = str(uuid.uuid4())
            
            if quiz_type == QuizType.MCQ:
                question_data = {
                    "options": q.get("options", [])
                }
            elif quiz_type == QuizType.FILL_BLANK:
                question_data = {
                    "sentence_with_blank": q.get("sentence_with_blank", ""),
                    "answer": q.get("answer", {})
                }
            elif quiz_type == QuizType.MATCHING:
                pairs = q.get("pairs", [])
                question_data = {
                    "pairs": pairs,
                    "scrambled_rights": [p.get("right", "") for p in pairs]
                }
            else:
                continue
            
            questions_data.append({
                "id": question_id,
                "quiz_id": quiz_id,
                "question_text": q.get("question_text", ""),
                "question_type": quiz_type.value,
                "question_data": question_data,
                "explanation": q.get("explanation", "") if include_explanations else None,
                "metadata_json": {"index": idx}
            })
        
        return questions_data
    
    def get_quiz(self, quiz_id: str) -> Optional[QuizResponse]:
        """Retrieve a generated quiz"""
        quiz = self.db_manager.get_quiz(quiz_id)
        if not quiz:
            return None
        
        questions_raw = self.db_manager.get_questions_by_quiz_id(quiz_id)
        
        questions = []
        for q in questions_raw:
            question_dict = {
                "question_text": q["question_text"],
                "question_type": q["question_type"],
                "explanation": q["explanation"],
                "metadata": q["metadata"]
            }
            question_dict.update(q["question_data"])
            questions.append(question_dict)
        
        return QuizResponse(
            quiz_id=quiz["id"],
            status=PedagogyStatus(quiz["status"]),
            quiz_type=QuizType(quiz["quiz_type"]),
            questions=questions,
            model_used=quiz["model_used"],
            metadata=quiz["metadata"],
            created_at=quiz["created_at"],
            error_message=quiz["error_message"]
        )
    
    def generate_mindmap(self, request: MindMapRequest) -> str:
        """Generate a mind map from source chunks"""
        mindmap_id = str(uuid.uuid4())
        
        try:
            config = request.config
            
            mindmap_data = {
                "id": mindmap_id,
                "source_id": request.source_id,
                "status": PedagogyStatus.PENDING.value,
                "metadata_json": {
                    "max_depth": config.max_depth,
                    "max_children_per_node": config.max_children_per_node,
                    "chunk_ids": request.chunk_ids or []
                }
            }
            
            self.db_manager.insert_mindmap(mindmap_data)
            
            self._generate_mindmap_async(mindmap_id, request)
            
            return mindmap_id
            
        except Exception as e:
            logger.error(f"Failed to start mindmap generation: {e}")
            self.db_manager.update_mindmap(mindmap_id, {
                "status": PedagogyStatus.FAILED.value,
                "error_message": str(e),
                "completed_at": datetime.utcnow()
            })
            raise
    
    def _generate_mindmap_async(self, mindmap_id: str, request: MindMapRequest):
        """Generate mind map asynchronously"""
        try:
            self.db_manager.update_mindmap(mindmap_id, {"status": PedagogyStatus.RUNNING.value})
            
            chunks = self._get_chunks_for_generation(request.source_id, request.chunk_ids)
            
            config = request.config
            prompt = PromptBuilder.build_mindmap_prompt(
                chunks,
                config.max_depth,
                config.max_children_per_node
            )
            
            response_text, model_used = self.model_manager.generate(prompt, max_tokens=3072, temperature=0.7)
            
            if not response_text:
                raise ValueError("LLM generation failed")
            
            response_data = self._extract_json_from_text(response_text)
            if not response_data:
                raise ValueError("Failed to parse LLM response as JSON")
            
            nodes_data, root_node_id = self._process_mindmap_response(
                mindmap_id,
                response_data,
                config.include_summaries
            )
            
            self.db_manager.insert_mindmap_nodes(nodes_data)
            
            self.db_manager.update_mindmap(mindmap_id, {
                "status": PedagogyStatus.COMPLETED.value,
                "model_used": model_used,
                "root_node_id": root_node_id,
                "completed_at": datetime.utcnow()
            })
            
            logger.info(f"Mind map {mindmap_id} generated successfully with {len(nodes_data)} nodes")
            
        except Exception as e:
            logger.error(f"Mind map generation failed: {e}")
            self.db_manager.update_mindmap(mindmap_id, {
                "status": PedagogyStatus.FAILED.value,
                "error_message": str(e),
                "completed_at": datetime.utcnow()
            })
    
    def _process_mindmap_response(
        self,
        mindmap_id: str,
        response_data: Dict[str, Any],
        include_summaries: bool
    ) -> tuple[List[Dict[str, Any]], str]:
        """Process and flatten mind map tree from LLM response"""
        nodes_data = []
        root_data = response_data.get("root", {})
        
        def process_node(node: Dict[str, Any], parent_id: Optional[str], level: int) -> str:
            node_id = str(uuid.uuid4())
            
            children = node.get("children", [])
            children_ids = []
            
            for child in children:
                child_id = process_node(child, node_id, level + 1)
                children_ids.append(child_id)
            
            nodes_data.append({
                "id": node_id,
                "mindmap_id": mindmap_id,
                "parent_id": parent_id,
                "content": node.get("content", ""),
                "summary": node.get("summary", "") if include_summaries else None,
                "level": level,
                "metadata_json": {"children_count": len(children_ids)}
            })
            
            return node_id
        
        root_node_id = process_node(root_data, None, 0)
        
        return nodes_data, root_node_id
    
    def get_mindmap(self, mindmap_id: str) -> Optional[MindMapResponse]:
        """Retrieve a generated mind map"""
        mindmap = self.db_manager.get_mindmap(mindmap_id)
        if not mindmap:
            return None
        
        nodes_raw = self.db_manager.get_mindmap_nodes(mindmap_id)
        
        nodes_dict = {node["id"]: node for node in nodes_raw}
        
        def build_node(node_data: Dict[str, Any]) -> MindMapNode:
            children_ids = [n["id"] for n in nodes_raw if n["parent_id"] == node_data["id"]]
            
            return MindMapNode(
                id=node_data["id"],
                content=node_data["content"],
                summary=node_data["summary"],
                level=node_data["level"],
                parent_id=node_data["parent_id"],
                children_ids=children_ids,
                metadata=node_data["metadata"]
            )
        
        nodes = [build_node(node_data) for node_data in nodes_raw]
        
        root_node = None
        if mindmap["root_node_id"] and mindmap["root_node_id"] in nodes_dict:
            root_node = build_node(nodes_dict[mindmap["root_node_id"]])
        
        return MindMapResponse(
            mindmap_id=mindmap["id"],
            status=PedagogyStatus(mindmap["status"]),
            root_node=root_node,
            nodes=nodes,
            model_used=mindmap["model_used"],
            metadata=mindmap["metadata"],
            created_at=mindmap["created_at"],
            error_message=mindmap["error_message"]
        )
