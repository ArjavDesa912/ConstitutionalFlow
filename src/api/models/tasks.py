from pydantic import BaseModel
from typing import Optional, Dict, Any
import datetime

class TaskCreate(BaseModel):
    content: str
    task_type: str
    priority: int = 1

class TaskResponse(BaseModel):
    task_id: str
    content: str
    task_type: str
    complexity_score: float
    estimated_time: int
    priority_level: int
    status: str
    created_at: datetime.datetime

class TaskAssignment(BaseModel):
    task_id: str
    annotator_id: Optional[str] = None

class TaskCompletion(BaseModel):
    feedback: str
    quality_score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None 