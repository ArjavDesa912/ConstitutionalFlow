
from pydantic import BaseModel
from typing import Optional, List
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
