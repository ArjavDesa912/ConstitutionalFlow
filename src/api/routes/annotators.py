from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from src.core.database import get_db, Annotator
from src.feedback.annotator_manager import annotator_manager
from src.api.models.annotators import AnnotatorRegister, AnnotatorUpdate, AnnotatorResponse

router = APIRouter()

@router.post("/annotators/register")
async def register_annotator(request: AnnotatorRegister, db: Session = Depends(get_db)):
    """
    Register a new annotator.
    """
    try:
        result = await annotator_manager.register_annotator(request.dict())
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return {
            "success": True,
            "annotator_id": result['annotator_id'],
            "message": result['message']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/annotators/{annotator_id}/profile")
async def get_annotator_profile(annotator_id: str, db: Session = Depends(get_db)):
    """
    Get annotator profile and performance data.
    """
    try:
        result = await annotator_manager.get_annotator_profile(annotator_id)
        
        if not result['success']:
            raise HTTPException(status_code=404, detail=result['error'])
        
        return {
            "success": True,
            "profile": result['profile']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/annotators/{annotator_id}/availability")
async def update_annotator_availability(
    annotator_id: str,
    status: str,
    db: Session = Depends(get_db)
):
    """
    Update annotator availability status.
    """
    try:
        result = await annotator_manager.update_availability(annotator_id, status)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return {
            "success": True,
            "annotator_id": result['annotator_id'],
            "new_status": result['new_status'],
            "updated_at": result['updated_at']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/annotators/{annotator_id}/skills")
async def update_annotator_skills(
    annotator_id: str,
    skill_updates: Dict[str, float],
    db: Session = Depends(get_db)
):
    """
    Update annotator skill scores.
    """
    try:
        result = await annotator_manager.update_skills(annotator_id, skill_updates)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return {
            "success": True,
            "annotator_id": result['annotator_id'],
            "updated_skills": result['updated_skills'],
            "total_skills": result['total_skills']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/annotators/matching")
async def get_matching_annotators(
    task_type: Optional[str] = None,
    required_skills: Optional[List[str]] = None,
    cultural_context: Optional[str] = None,
    required_languages: Optional[List[str]] = None,
    db: Session = Depends(get_db)
):
    """
    Get best annotators for specific tasks.
    """
    try:
        task_requirements = {
            'required_skills': required_skills or [],
            'cultural_context': cultural_context or '',
            'required_languages': required_languages or []
        }
        
        if task_type:
            task_requirements['task_type'] = task_type
        
        result = await annotator_manager.get_matching_annotators(task_requirements)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return {
            "success": True,
            "matching_annotators": result['matching_annotators'],
            "count": result['count']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/annotators")
async def get_all_annotators(
    status: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all annotators with optional filtering.
    """
    try:
        query = db.query(Annotator)
        
        if status:
            query = query.filter(Annotator.availability_status == status)
        
        annotators = query.limit(limit).all()
        
        annotator_list = []
        for annotator in annotators:
            annotator_list.append({
                "annotator_id": annotator.annotator_id,
                "skill_scores": annotator.skill_scores or {},
                "cultural_background": annotator.cultural_background,
                "languages": annotator.languages or [],
                "availability_status": annotator.availability_status,
                "created_at": annotator.created_at.isoformat(),
                "updated_at": annotator.updated_at.isoformat()
            })
        
        return {
            "success": True,
            "annotators": annotator_list,
            "count": len(annotator_list)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/annotators/analytics")
async def get_annotator_analytics(
    annotator_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get annotator analytics and performance metrics.
    """
    try:
        result = await annotator_manager.get_annotator_analytics(annotator_id)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return {
            "success": True,
            "analytics": result.get('analytics') or result.get('annotators', [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/annotators/{annotator_id}")
async def delete_annotator(annotator_id: str, db: Session = Depends(get_db)):
    """
    Delete an annotator (soft delete by setting availability to unavailable).
    """
    try:
        result = await annotator_manager.update_availability(annotator_id, "unavailable")
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return {
            "success": True,
            "annotator_id": annotator_id,
            "message": "Annotator deleted successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/annotators/{annotator_id}/performance")
async def get_annotator_performance(
    annotator_id: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get detailed performance metrics for an annotator.
    """
    try:
        from datetime import datetime, timedelta
        from src.core.database import Task, FeedbackSample
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get tasks assigned to this annotator
        tasks = db.query(Task).filter(
            Task.assigned_annotator_id == annotator_id,
            Task.created_at >= start_date
        ).all()
        
        # Get feedback samples for this annotator
        feedback_samples = db.query(FeedbackSample).filter(
            FeedbackSample.annotator_id == annotator_id,
            FeedbackSample.created_at >= start_date,
            FeedbackSample.quality_score.isnot(None)
        ).all()
        
        # Calculate performance metrics
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.status == 'completed'])
        pending_tasks = len([t for t in tasks if t.status == 'pending'])
        in_progress_tasks = len([t for t in tasks if t.status == 'in_progress'])
        
        # Quality metrics
        quality_scores = [f.quality_score for f in feedback_samples]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        
        # Task type performance
        task_type_performance = {}
        for task in tasks:
            if task.task_type not in task_type_performance:
                task_type_performance[task.task_type] = {
                    'total': 0,
                    'completed': 0,
                    'avg_quality': 0.0,
                    'quality_scores': []
                }
            
            task_type_performance[task.task_type]['total'] += 1
            if task.status == 'completed':
                task_type_performance[task.task_type]['completed'] += 1
        
        # Calculate quality per task type
        for feedback in feedback_samples:
            task = db.query(Task).filter(Task.task_id == feedback.task_id).first()
            if task and task.task_type in task_type_performance:
                task_type_performance[task.task_type]['quality_scores'].append(feedback.quality_score)
        
        # Calculate averages
        for task_type, metrics in task_type_performance.items():
            if metrics['quality_scores']:
                metrics['avg_quality'] = sum(metrics['quality_scores']) / len(metrics['quality_scores'])
            else:
                metrics['avg_quality'] = 0.0
        
        return {
            "success": True,
            "annotator_id": annotator_id,
            "performance": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "pending_tasks": pending_tasks,
                "in_progress_tasks": in_progress_tasks,
                "completion_rate": completed_tasks / total_tasks if total_tasks > 0 else 0.0,
                "average_quality": avg_quality,
                "task_type_performance": task_type_performance,
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": days
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 