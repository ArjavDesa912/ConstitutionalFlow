from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import datetime

class FeedbackSubmit(BaseModel):
    task_id: str
    original_content: str
    human_feedback: str
    feedback_type: Optional[str] = None
    annotator_id: Optional[str] = None
    quality_score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class FeedbackBatch(BaseModel):
    feedback_samples: List[FeedbackSubmit]

class QualityPrediction(BaseModel):
    task_data: Dict[str, Any]
    annotator_data: Dict[str, Any] 