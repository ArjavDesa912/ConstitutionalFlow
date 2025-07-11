from sqlalchemy import create_engine, Column, Integer, String, Text, Float, Boolean, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from datetime import datetime
from src.core.config import settings

# Database engine and session
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Database Models
class ConstitutionalPrinciple(Base):
    __tablename__ = "constitutional_principles"
    
    id = Column(Integer, primary_key=True, index=True)
    principle_text = Column(Text, nullable=False)
    category = Column(String(100))
    confidence_score = Column(Float)
    cultural_context = Column(JSON)
    version_number = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)

class FeedbackSample(Base):
    __tablename__ = "feedback_samples"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(255))
    original_content = Column(Text)
    human_feedback = Column(Text)
    feedback_type = Column(String(50))
    annotator_id = Column(String(255))
    quality_score = Column(Float)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=func.now())

class Annotator(Base):
    __tablename__ = "annotators"
    
    id = Column(Integer, primary_key=True, index=True)
    annotator_id = Column(String(255), unique=True, index=True)
    skill_scores = Column(JSON)
    performance_history = Column(JSON)
    cultural_background = Column(String(100))
    languages = Column(JSON)
    availability_status = Column(String(50))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(255), unique=True, index=True)
    content = Column(Text)
    task_type = Column(String(100))
    complexity_score = Column(Float)
    estimated_time = Column(Integer)
    priority_level = Column(Integer)
    status = Column(String(50))
    assigned_annotator_id = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine) 