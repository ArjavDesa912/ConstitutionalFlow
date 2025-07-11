from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from src.core.database import get_db, FeedbackSample
from src.feedback.quality_predictor import quality_predictor
from src.api.models.feedback import FeedbackSubmit, FeedbackBatch, QualityPrediction

router = APIRouter()

@router.post("/feedback/submit")
async def submit_feedback(request: FeedbackSubmit, db: Session = Depends(get_db)):
    """
    Submit human feedback for analysis.
    """
    try:
        # Create feedback sample
        feedback_sample = FeedbackSample(
            task_id=request.task_id,
            original_content=request.original_content,
            human_feedback=request.human_feedback,
            feedback_type=request.feedback_type,
            annotator_id=request.annotator_id,
            quality_score=request.quality_score,
            metadata=request.metadata
        )
        
        db.add(feedback_sample)
        db.commit()
        
        # Update annotator performance if quality score provided
        if request.quality_score and request.annotator_id:
            from src.feedback.annotator_manager import annotator_manager
            await annotator_manager.update_performance_history(
                request.annotator_id,
                {'quality_score': request.quality_score}
            )
        
        return {
            "success": True,
            "feedback_id": feedback_sample.id,
            "message": "Feedback submitted successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback/batch")
async def submit_batch_feedback(request: FeedbackBatch, db: Session = Depends(get_db)):
    """
    Submit batch feedback for processing.
    """
    try:
        feedback_ids = []
        
        for feedback_data in request.feedback_samples:
            feedback_sample = FeedbackSample(
                task_id=feedback_data.task_id,
                original_content=feedback_data.original_content,
                human_feedback=feedback_data.human_feedback,
                feedback_type=feedback_data.feedback_type,
                annotator_id=feedback_data.annotator_id,
                quality_score=feedback_data.quality_score,
                metadata=feedback_data.metadata
            )
            
            db.add(feedback_sample)
            feedback_ids.append(feedback_sample.id)
        
        db.commit()
        
        return {
            "success": True,
            "feedback_ids": feedback_ids,
            "count": len(feedback_ids),
            "message": f"Batch feedback submitted successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/feedback/quality")
async def get_quality_prediction(
    task_id: str,
    annotator_id: str,
    db: Session = Depends(get_db)
):
    """
    Get quality prediction for a task-annotator pairing.
    """
    try:
        # Get task data
        from src.core.database import Task
        task = db.query(Task).filter(Task.task_id == task_id).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Get annotator data
        from src.core.database import Annotator
        annotator = db.query(Annotator).filter(Annotator.annotator_id == annotator_id).first()
        
        if not annotator:
            raise HTTPException(status_code=404, detail="Annotator not found")
        
        # Prepare data for prediction
        task_data = {
            'complexity_score': task.complexity_score,
            'content': task.content,
            'task_type': task.task_type
        }
        
        annotator_data = {
            'skill_scores': annotator.skill_scores or {},
            'performance_history': annotator.performance_history or {},
            'cultural_background': annotator.cultural_background,
            'languages': annotator.languages or []
        }
        
        # Get quality prediction
        prediction = await quality_predictor.predict_quality(task_data, annotator_data)
        
        return {
            "success": True,
            "task_id": task_id,
            "annotator_id": annotator_id,
            "prediction": prediction
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/feedback/analytics")
async def get_feedback_analytics(
    annotator_id: Optional[str] = None,
    feedback_type: Optional[str] = None,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get feedback analytics and insights.
    """
    try:
        from datetime import datetime, timedelta
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Build query
        query = db.query(FeedbackSample).filter(FeedbackSample.created_at >= start_date)
        
        if annotator_id:
            query = query.filter(FeedbackSample.annotator_id == annotator_id)
        
        if feedback_type:
            query = query.filter(FeedbackSample.feedback_type == feedback_type)
        
        feedback_samples = query.all()
        
        # Calculate statistics
        total_feedback = len(feedback_samples)
        feedback_with_quality = [f for f in feedback_samples if f.quality_score is not None]
        
        if feedback_with_quality:
            avg_quality = sum(f.quality_score for f in feedback_with_quality) / len(feedback_with_quality)
            quality_distribution = {
                'excellent': len([f for f in feedback_with_quality if f.quality_score >= 0.9]),
                'good': len([f for f in feedback_with_quality if 0.7 <= f.quality_score < 0.9]),
                'fair': len([f for f in feedback_with_quality if 0.5 <= f.quality_score < 0.7]),
                'poor': len([f for f in feedback_with_quality if f.quality_score < 0.5])
            }
        else:
            avg_quality = 0.0
            quality_distribution = {'excellent': 0, 'good': 0, 'fair': 0, 'poor': 0}
        
        # Feedback type distribution
        type_counts = {}
        for sample in feedback_samples:
            feedback_type = sample.feedback_type or 'unknown'
            type_counts[feedback_type] = type_counts.get(feedback_type, 0) + 1
        
        # Annotator performance (if specific annotator not provided)
        if not annotator_id:
            annotator_performance = {}
            for sample in feedback_samples:
                if sample.annotator_id and sample.quality_score:
                    if sample.annotator_id not in annotator_performance:
                        annotator_performance[sample.annotator_id] = []
                    annotator_performance[sample.annotator_id].append(sample.quality_score)
            
            # Calculate average quality per annotator
            for annotator_id, scores in annotator_performance.items():
                annotator_performance[annotator_id] = sum(scores) / len(scores)
        else:
            annotator_performance = None
        
        return {
            "success": True,
            "analytics": {
                "total_feedback": total_feedback,
                "feedback_with_quality": len(feedback_with_quality),
                "average_quality": avg_quality,
                "quality_distribution": quality_distribution,
                "feedback_type_distribution": type_counts,
                "annotator_performance": annotator_performance,
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": days
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/feedback/{feedback_id}")
async def get_feedback_details(feedback_id: int, db: Session = Depends(get_db)):
    """
    Get details of a specific feedback sample.
    """
    try:
        feedback = db.query(FeedbackSample).filter(FeedbackSample.id == feedback_id).first()
        
        if not feedback:
            raise HTTPException(status_code=404, detail="Feedback not found")
        
        return {
            "success": True,
            "feedback": {
                "id": feedback.id,
                "task_id": feedback.task_id,
                "original_content": feedback.original_content,
                "human_feedback": feedback.human_feedback,
                "feedback_type": feedback.feedback_type,
                "annotator_id": feedback.annotator_id,
                "quality_score": feedback.quality_score,
                "metadata": feedback.metadata,
                "created_at": feedback.created_at.isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback/quality-prediction")
async def predict_quality(request: QualityPrediction):
    """
    Predict quality for a task-annotator pairing.
    """
    try:
        prediction = await quality_predictor.predict_quality(
            request.task_data, 
            request.annotator_data
        )
        
        return {
            "success": True,
            "prediction": prediction
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 