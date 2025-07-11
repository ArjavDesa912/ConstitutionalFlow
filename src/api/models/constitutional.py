
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import datetime

class Principle(BaseModel):
    id: int
    principle_text: str
    category: Optional[str] = None
    confidence_score: Optional[float] = None
    cultural_context: Optional[dict] = None
    version_number: Optional[int] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    is_active: bool

    class Config:
        orm_mode = True

class PrincipleHistory(BaseModel):
    id: int
    principle_id: int
    principle_text: str
    version_number: int
    created_at: datetime.datetime

    class Config:
        orm_mode = True

class FeedbackSample(BaseModel):
    original_content: str
    human_feedback: str
    feedback_type: Optional[str] = None
    quality_score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class FeedbackAnalysisRequest(BaseModel):
    feedback_samples: List[FeedbackSample]
    store_principles: bool = True

class PrincipleValidationRequest(BaseModel):
    principle: Dict[str, Any]
    validation_context: Optional[Dict[str, Any]] = None
