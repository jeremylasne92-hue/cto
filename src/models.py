from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


# Existing enums for ingestion
class SourceType(str, Enum):
    YOUTUBE = "youtube"
    PDF = "pdf"
    WEB_PAGE = "web_page"
    MARKDOWN = "markdown"
    PLAIN_TEXT = "plain_text"


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Ingestion models
class IngestionConfig(BaseModel):
    max_chunk_size: int = Field(default=1000, ge=50, le=5000)
    chunk_overlap: int = Field(default=100, ge=0, le=500)
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)


class IngestionRequest(BaseModel):
    source_type: SourceType
    source_url: str
    config: Optional[IngestionConfig] = None


# Pedagogy engine enums
class QuizType(str, Enum):
    MCQ = "mcq"  # Multiple choice
    FILL_BLANK = "fill_blank"  # Fill in the blank
    MATCHING = "matching"  # Match pairs


class ModelTier(str, Enum):
    PREMIUM = "premium"  # Mistral-7B
    STANDARD = "standard"  # Phi-2
    CLOUD = "cloud"  # Cloud API fallback


class PedagogyStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# Quiz models
class QuizConfig(BaseModel):
    quiz_type: QuizType
    num_questions: int = Field(default=5, ge=1, le=50)
    difficulty: Optional[str] = Field(default="medium")
    include_explanations: bool = Field(default=True)


class QuizRequest(BaseModel):
    source_id: Optional[str] = None  # Document ID
    chunk_ids: Optional[List[str]] = None  # Specific chunks
    config: QuizConfig


class MCQOption(BaseModel):
    text: str
    is_correct: bool


class FillBlankAnswer(BaseModel):
    text: str
    alternatives: List[str] = Field(default_factory=list)


class MatchingPair(BaseModel):
    left: str
    right: str


class QuestionBase(BaseModel):
    question_text: str
    question_type: QuizType
    explanation: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MCQQuestion(QuestionBase):
    question_type: QuizType = QuizType.MCQ
    options: List[MCQOption]


class FillBlankQuestion(QuestionBase):
    question_type: QuizType = QuizType.FILL_BLANK
    answer: FillBlankAnswer
    sentence_with_blank: str


class MatchingQuestion(QuestionBase):
    question_type: QuizType = QuizType.MATCHING
    pairs: List[MatchingPair]
    scrambled_rights: List[str]  # Shuffled right-side items


class QuizResponse(BaseModel):
    quiz_id: str
    status: PedagogyStatus
    quiz_type: QuizType
    questions: List[Dict[str, Any]] = Field(default_factory=list)
    model_used: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    error_message: Optional[str] = None


# Mind map models
class MindMapConfig(BaseModel):
    max_depth: int = Field(default=4, ge=1, le=10)
    max_children_per_node: int = Field(default=7, ge=2, le=20)
    include_summaries: bool = Field(default=True)


class MindMapRequest(BaseModel):
    source_id: Optional[str] = None
    chunk_ids: Optional[List[str]] = None
    config: Optional[MindMapConfig] = Field(default_factory=MindMapConfig)


class MindMapNode(BaseModel):
    id: str
    content: str
    summary: Optional[str] = None
    level: int
    parent_id: Optional[str] = None
    children_ids: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MindMapResponse(BaseModel):
    mindmap_id: str
    status: PedagogyStatus
    root_node: Optional[MindMapNode] = None
    nodes: List[MindMapNode] = Field(default_factory=list)
    model_used: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    error_message: Optional[str] = None


# Hardware benchmark models
class HardwareBenchmark(BaseModel):
    cpu_score: float
    ram_gb: float
    gpu_available: bool
    gpu_memory_gb: float = 0.0
    disk_speed_mbps: float = 0.0


class ModelAvailability(BaseModel):
    model_name: str
    tier: ModelTier
    available: bool
    loaded: bool = False
    ram_requirement_gb: float
    gpu_requirement_gb: float = 0.0
    last_checked: datetime
