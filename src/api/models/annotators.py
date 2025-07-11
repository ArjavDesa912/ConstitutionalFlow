from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import datetime

class AnnotatorRegister(BaseModel):
    annotator_id: str
    skill_scores: Optional[Dict[str, float]] = {}
    cultural_background: Optional[str] = ""
    languages: Optional[List[str]] = []

class AnnotatorUpdate(BaseModel):
    skill_scores: Optional[Dict[str, float]] = None
    cultural_background: Optional[str] = None
    languages: Optional[List[str]] = None
    availability_status: Optional[str] = None

class AnnotatorResponse(BaseModel):
    annotator_id: str
    skill_scores: Dict[str, float]
    cultural_background: str
    languages: List[str]
    availability_status: str
    created_at: datetime.datetime
    updated_at: datetime.datetime 