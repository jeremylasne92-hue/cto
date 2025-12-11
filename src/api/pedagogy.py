from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional
import logging

from ..models import (
    QuizRequest, QuizResponse, MindMapRequest, MindMapResponse,
    PedagogyStatus
)
from ..services.pedagogy import PedagogyService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pedagogy", tags=["pedagogy"])

pedagogy_service = PedagogyService()


@router.post("/quiz", response_model=dict)
async def generate_quiz(request: QuizRequest, background_tasks: BackgroundTasks):
    """
    Generate a quiz from ingested chunks
    
    Supports three quiz types:
    - mcq: Multiple choice questions
    - fill_blank: Fill in the blank questions
    - matching: Match pairs questions
    
    Either source_id (document ID) or chunk_ids (specific chunks) must be provided.
    """
    try:
        if not request.source_id and not request.chunk_ids:
            raise HTTPException(
                status_code=400, 
                detail="Either source_id or chunk_ids must be provided"
            )
        
        quiz_id = pedagogy_service.generate_quiz(request)
        
        return {
            "quiz_id": quiz_id,
            "message": f"Quiz generation started ({request.config.quiz_type.value})",
            "status_endpoint": f"/pedagogy/quiz/{quiz_id}",
            "config": {
                "quiz_type": request.config.quiz_type.value,
                "num_questions": request.config.num_questions,
                "difficulty": request.config.difficulty
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Quiz generation failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/quiz/{quiz_id}", response_model=QuizResponse)
async def get_quiz(quiz_id: str):
    """
    Retrieve a generated quiz by ID
    
    Returns the quiz with all questions and answers.
    Check the status field to see if generation is complete.
    """
    try:
        quiz = pedagogy_service.get_quiz(quiz_id)
        
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        return quiz
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve quiz: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/mindmap", response_model=dict)
async def generate_mindmap(request: MindMapRequest, background_tasks: BackgroundTasks):
    """
    Generate a hierarchical mind map from ingested chunks
    
    The mind map will organize content into a tree structure with:
    - A root node representing the main topic
    - Child nodes for subtopics and details
    - Configurable max depth and branching factor
    
    Either source_id (document ID) or chunk_ids (specific chunks) must be provided.
    """
    try:
        if not request.source_id and not request.chunk_ids:
            raise HTTPException(
                status_code=400,
                detail="Either source_id or chunk_ids must be provided"
            )
        
        mindmap_id = pedagogy_service.generate_mindmap(request)
        
        return {
            "mindmap_id": mindmap_id,
            "message": "Mind map generation started",
            "status_endpoint": f"/pedagogy/mindmap/{mindmap_id}",
            "config": {
                "max_depth": request.config.max_depth,
                "max_children_per_node": request.config.max_children_per_node,
                "include_summaries": request.config.include_summaries
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Mind map generation failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/mindmap/{mindmap_id}", response_model=MindMapResponse)
async def get_mindmap(mindmap_id: str):
    """
    Retrieve a generated mind map by ID
    
    Returns the mind map with all nodes organized hierarchically.
    Check the status field to see if generation is complete.
    """
    try:
        mindmap = pedagogy_service.get_mindmap(mindmap_id)
        
        if not mindmap:
            raise HTTPException(status_code=404, detail="Mind map not found")
        
        return mindmap
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve mind map: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/models/status", response_model=dict)
async def get_models_status():
    """
    Get status of available models (local and cloud)
    
    Returns information about:
    - Local model availability based on hardware
    - Currently loaded model
    - Cloud API configuration
    """
    try:
        model_manager = pedagogy_service.model_manager
        
        mistral_availability = model_manager.check_model_availability("mistral-7b")
        phi_availability = model_manager.check_model_availability("phi-2")
        
        return {
            "hardware": {
                "cpu_score": model_manager.hardware_benchmark.cpu_score,
                "ram_gb": model_manager.hardware_benchmark.ram_gb,
                "gpu_available": model_manager.hardware_benchmark.gpu_available,
                "gpu_memory_gb": model_manager.hardware_benchmark.gpu_memory_gb
            },
            "models": {
                "mistral-7b": {
                    "tier": mistral_availability.tier.value,
                    "available": mistral_availability.available,
                    "loaded": mistral_availability.loaded,
                    "requirements": {
                        "ram_gb": mistral_availability.ram_requirement_gb,
                        "gpu_gb": mistral_availability.gpu_requirement_gb
                    }
                },
                "phi-2": {
                    "tier": phi_availability.tier.value,
                    "available": phi_availability.available,
                    "loaded": phi_availability.loaded,
                    "requirements": {
                        "ram_gb": phi_availability.ram_requirement_gb,
                        "gpu_gb": phi_availability.gpu_requirement_gb
                    }
                }
            },
            "cloud_configured": bool(model_manager.cloud_api_url),
            "selected_model": model_manager.loaded_model_name or "none"
        }
        
    except Exception as e:
        logger.error(f"Failed to get models status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
