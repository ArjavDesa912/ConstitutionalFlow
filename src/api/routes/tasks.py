from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from src.core.database import get_db, Task
from src.feedback.task_router import task_router
from src.api.models.tasks import TaskCreate, TaskResponse, TaskAssignment, TaskCompletion
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/tasks/create", response_model=TaskResponse)
async def create_task(request: TaskCreate, db: Session = Depends(get_db)):
    """
    Create a new annotation task.
    """
    try:
        result = await task_router.create_task(
            content=request.content,
            task_type=request.task_type,
            priority=request.priority
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return TaskResponse(
            task_id=result['task_id'],
            content=request.content,
            task_type=request.task_type,
            complexity_score=result['complexity_analysis'].get('complexity_score', 0.5),
            estimated_time=result['complexity_analysis'].get('estimated_time_minutes', 30),
            priority_level=request.priority,
            status='pending',
            created_at=result['task_data']['created_at']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/queue")
async def get_task_queue(
    annotator_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get tasks for specific annotator or all pending tasks.
    """
    try:
        result = await task_router.get_task_queue(annotator_id)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        # Filter by status if provided
        tasks = result['tasks']
        if status:
            tasks = [task for task in tasks if task['status'] == status]
        
        # Apply limit
        tasks = tasks[:limit]
        
        return {
            "success": True,
            "tasks": tasks,
            "count": len(tasks),
            "annotator_id": annotator_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tasks/assign")
async def assign_task(request: TaskAssignment, db: Session = Depends(get_db)):
    """
    Intelligently assign a task to an annotator.
    """
    try:
        result = await task_router.assign_task(
            task_id=request.task_id,
            annotator_id=request.annotator_id
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return {
            "success": True,
            "task_id": request.task_id,
            "assigned_annotator": result['assigned_annotator'],
            "assignment_time": result['assignment_time']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/tasks/{task_id}/complete")
async def complete_task(
    task_id: str,
    request: TaskCompletion,
    db: Session = Depends(get_db)
):
    """
    Mark task as completed with feedback.
    """
    try:
        result = await task_router.complete_task(
            task_id=task_id,
            feedback=request.feedback,
            quality_score=request.quality_score
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return {
            "success": True,
            "task_id": task_id,
            "completion_time": result['completion_time'],
            "feedback_stored": result['feedback_stored']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/{task_id}")
async def get_task(task_id: str, db: Session = Depends(get_db)):
    """
    Get details of a specific task.
    """
    try:
        task = db.query(Task).filter(Task.task_id == task_id).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {
            "success": True,
            "task": {
                "task_id": task.task_id,
                "content": task.content,
                "task_type": task.task_type,
                "complexity_score": task.complexity_score,
                "estimated_time": task.estimated_time,
                "priority_level": task.priority_level,
                "status": task.status,
                "assigned_annotator_id": task.assigned_annotator_id,
                "created_at": task.created_at.isoformat(),
                "completed_at": task.completed_at.isoformat() if task.completed_at else None
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/tasks/{task_id}/status")
async def update_task_status(
    task_id: str,
    status: str,
    db: Session = Depends(get_db)
):
    """
    Update task status.
    """
    try:
        task = db.query(Task).filter(Task.task_id == task_id).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Validate status
        valid_statuses = ['pending', 'assigned', 'in_progress', 'completed', 'cancelled']
        if status not in valid_statuses:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status. Must be one of: {valid_statuses}"
            )
        
        task.status = status
        
        # Update completion time if completing
        if status == 'completed':
            task.completed_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "success": True,
            "task_id": task_id,
            "new_status": status,
            "updated_at": task.updated_at.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/analytics")
async def get_task_analytics(
    annotator_id: Optional[str] = None,
    task_type: Optional[str] = None,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get task analytics and statistics.
    """
    try:
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Build query
        query = db.query(Task).filter(Task.created_at >= start_date)
        
        if annotator_id:
            query = query.filter(Task.assigned_annotator_id == annotator_id)
        
        if task_type:
            query = query.filter(Task.task_type == task_type)
        
        tasks = query.all()
        
        # Calculate statistics
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.status == 'completed'])
        pending_tasks = len([t for t in tasks if t.status == 'pending'])
        in_progress_tasks = len([t for t in tasks if t.status == 'in_progress'])
        
        # Calculate average complexity and time
        completed_tasks_with_time = [t for t in tasks if t.status == 'completed' and t.completed_at]
        avg_complexity = sum(t.complexity_score for t in tasks) / len(tasks) if tasks else 0
        
        # Calculate completion time statistics
        completion_times = []
        for task in completed_tasks_with_time:
            if task.created_at and task.completed_at:
                completion_time = (task.completed_at - task.created_at).total_seconds() / 60  # minutes
                completion_times.append(completion_time)
        
        avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
        
        # Task type distribution
        task_type_counts = {}
        for task in tasks:
            task_type_counts[task.task_type] = task_type_counts.get(task.task_type, 0) + 1
        
        return {
            "success": True,
            "analytics": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "pending_tasks": pending_tasks,
                "in_progress_tasks": in_progress_tasks,
                "completion_rate": completed_tasks / total_tasks if total_tasks > 0 else 0,
                "average_complexity": avg_complexity,
                "average_completion_time_minutes": avg_completion_time,
                "task_type_distribution": task_type_counts,
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": days
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 