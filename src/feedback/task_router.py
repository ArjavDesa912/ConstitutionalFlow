import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.core.database import get_db, Task, Annotator
from src.constitutional.api_client import multi_model_client
from src.constitutional.prompts import PromptTemplates
from src.core.utils import logger, log_execution_time, calculate_complexity_score, generate_task_id

class SmartTaskRouter:
    """AI-powered task routing and assignment system"""
    
    def __init__(self):
        self.prompt_templates = PromptTemplates()
    
    @log_execution_time
    async def create_task(self, content: str, task_type: str, priority: int = 1) -> Dict[str, Any]:
        """Create a new annotation task with AI-powered complexity analysis"""
        try:
            # Generate task ID
            task_id = generate_task_id()
            
            # Analyze task complexity using AI
            complexity_analysis = await self._analyze_task_complexity(content, task_type)
            
            # Create task record
            task_data = {
                'task_id': task_id,
                'content': content,
                'task_type': task_type,
                'complexity_score': complexity_analysis.get('complexity_score', 0.5),
                'estimated_time': complexity_analysis.get('estimated_time_minutes', 30),
                'priority_level': priority,
                'status': 'pending',
                'created_at': datetime.utcnow()
            }
            
            # Store in database
            db = next(get_db())
            task = Task(**task_data)
            db.add(task)
            db.commit()
            
            logger.info("Task created successfully", task_id=task_id, complexity=complexity_analysis.get('complexity_score'))
            
            return {
                'success': True,
                'task_id': task_id,
                'complexity_analysis': complexity_analysis,
                'task_data': task_data
            }
            
        except Exception as e:
            logger.error("Error creating task", error=str(e))
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _analyze_task_complexity(self, content: str, task_type: str) -> Dict[str, Any]:
        """Analyze task complexity using AI"""
        try:
            # Generate complexity analysis prompt
            prompt = self.prompt_templates.task_complexity_analysis(content)
            
            # Get AI analysis
            response = await multi_model_client.generate_response(
                prompt,
                providers=['openai', 'anthropic'],
                max_tokens=1000,
                temperature=0.3
            )
            
            if response['success']:
                try:
                    import json
                    analysis = json.loads(response['content'])
                    return analysis
                except json.JSONDecodeError:
                    # Fallback to basic analysis
                    return self._basic_complexity_analysis(content, task_type)
            else:
                return self._basic_complexity_analysis(content, task_type)
                
        except Exception as e:
            logger.error("Error in AI complexity analysis", error=str(e))
            return self._basic_complexity_analysis(content, task_type)
    
    def _basic_complexity_analysis(self, content: str, task_type: str) -> Dict[str, Any]:
        """Basic complexity analysis when AI fails"""
        complexity_score = calculate_complexity_score(content)
        
        # Estimate time based on content length and type
        base_time = len(content.split()) * 0.1  # 0.1 minutes per word
        type_multipliers = {
            'sentiment': 0.8,
            'classification': 1.0,
            'translation': 1.5,
            'summarization': 1.2,
            'qa': 1.3
        }
        estimated_time = base_time * type_multipliers.get(task_type, 1.0)
        
        return {
            'complexity_score': complexity_score,
            'expertise_level': 'intermediate' if complexity_score > 0.5 else 'beginner',
            'estimated_time_minutes': int(estimated_time),
            'challenges': ['Basic analysis - AI analysis failed'],
            'required_skills': [task_type],
            'confidence': 0.5
        }
    
    @log_execution_time
    async def assign_task(self, task_id: str, annotator_id: str = None) -> Dict[str, Any]:
        """Assign a task to the best available annotator"""
        try:
            db = next(get_db())
            
            # Get task details
            task = db.query(Task).filter(Task.task_id == task_id).first()
            if not task:
                return {
                    'success': False,
                    'error': 'Task not found'
                }
            
            # If specific annotator requested, assign directly
            if annotator_id:
                return await self._assign_to_specific_annotator(task, annotator_id, db)
            
            # Find best annotator using AI-powered matching
            best_annotator = await self._find_best_annotator(task, db)
            
            if not best_annotator:
                return {
                    'success': False,
                    'error': 'No suitable annotator available'
                }
            
            # Assign task
            task.assigned_annotator_id = best_annotator['annotator_id']
            task.status = 'assigned'
            db.commit()
            
            logger.info("Task assigned successfully", 
                       task_id=task_id, 
                       annotator_id=best_annotator['annotator_id'],
                       match_score=best_annotator['match_score'])
            
            return {
                'success': True,
                'assigned_annotator': best_annotator,
                'assignment_time': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Error assigning task", error=str(e))
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _find_best_annotator(self, task: Task, db: Session) -> Optional[Dict[str, Any]]:
        """Find the best annotator for a task using AI matching"""
        try:
            # Get available annotators
            available_annotators = db.query(Annotator).filter(
                Annotator.availability_status == 'available'
            ).all()
            
            if not available_annotators:
                return None
            
            # Get task details for matching
            task_details = {
                'task_type': task.task_type,
                'complexity_score': task.complexity_score,
                'content': task.content[:500]  # First 500 chars for analysis
            }
            
            # Score each annotator
            annotator_scores = []
            
            for annotator in available_annotators:
                annotator_profile = {
                    'skill_scores': annotator.skill_scores or {},
                    'performance_history': annotator.performance_history or {},
                    'cultural_background': annotator.cultural_background,
                    'languages': annotator.languages or []
                }
                
                # Get AI-powered quality prediction
                quality_prediction = await self._predict_annotation_quality(
                    annotator_profile, task_details
                )
                
                if quality_prediction['predicted_quality'] > 0.5:  # Minimum quality threshold
                    annotator_scores.append({
                        'annotator_id': annotator.annotator_id,
                        'annotator': annotator,
                        'match_score': quality_prediction['skill_match_score'],
                        'predicted_quality': quality_prediction['predicted_quality'],
                        'confidence': quality_prediction['confidence']
                    })
            
            if not annotator_scores:
                return None
            
            # Sort by match score and return best
            annotator_scores.sort(key=lambda x: x['match_score'], reverse=True)
            return annotator_scores[0]
            
        except Exception as e:
            logger.error("Error finding best annotator", error=str(e))
            return None
    
    async def _predict_annotation_quality(self, annotator_profile: Dict[str, Any], task_details: Dict[str, Any]) -> Dict[str, Any]:
        """Predict annotation quality using AI"""
        try:
            prompt = self.prompt_templates.quality_prediction(annotator_profile, task_details)
            
            response = await multi_model_client.generate_response(
                prompt,
                providers=['openai'],
                max_tokens=1000,
                temperature=0.2
            )
            
            if response['success']:
                try:
                    import json
                    return json.loads(response['content'])
                except json.JSONDecodeError:
                    return self._basic_quality_prediction(annotator_profile, task_details)
            else:
                return self._basic_quality_prediction(annotator_profile, task_details)
                
        except Exception as e:
            logger.error("Error in quality prediction", error=str(e))
            return self._basic_quality_prediction(annotator_profile, task_details)
    
    def _basic_quality_prediction(self, annotator_profile: Dict[str, Any], task_details: Dict[str, Any]) -> Dict[str, Any]:
        """Basic quality prediction when AI fails"""
        task_type = task_details.get('task_type', 'general')
        skill_scores = annotator_profile.get('skill_scores', {})
        
        # Calculate skill match
        skill_match = skill_scores.get(task_type, 0.5)
        
        # Adjust for complexity
        complexity = task_details.get('complexity_score', 0.5)
        if complexity > 0.8 and skill_match < 0.7:
            skill_match *= 0.8  # Penalty for complex tasks with low skills
        
        # Predict quality (simple heuristic)
        predicted_quality = skill_match * 0.8 + 0.2  # Base quality of 0.2
        
        return {
            'skill_match_score': skill_match,
            'predicted_quality': min(predicted_quality, 1.0),
            'confidence': 0.6,
            'risks': ['Basic prediction - AI analysis failed'],
            'recommendations': ['Consider manual review for complex tasks']
        }
    
    async def _assign_to_specific_annotator(self, task: Task, annotator_id: str, db: Session) -> Dict[str, Any]:
        """Assign task to a specific annotator"""
        try:
            # Check if annotator exists and is available
            annotator = db.query(Annotator).filter(
                Annotator.annotator_id == annotator_id,
                Annotator.availability_status == 'available'
            ).first()
            
            if not annotator:
                return {
                    'success': False,
                    'error': 'Annotator not found or not available'
                }
            
            # Assign task
            task.assigned_annotator_id = annotator_id
            task.status = 'assigned'
            db.commit()
            
            return {
                'success': True,
                'assigned_annotator': {
                    'annotator_id': annotator_id,
                    'match_score': 1.0,  # Direct assignment
                    'predicted_quality': 0.8,
                    'confidence': 1.0
                }
            }
            
        except Exception as e:
            logger.error("Error in specific annotator assignment", error=str(e))
            return {
                'success': False,
                'error': str(e)
            }
    
    @log_execution_time
    async def get_task_queue(self, annotator_id: str = None) -> Dict[str, Any]:
        """Get tasks for specific annotator or all pending tasks"""
        try:
            db = next(get_db())
            
            if annotator_id:
                # Get tasks assigned to specific annotator
                tasks = db.query(Task).filter(
                    Task.assigned_annotator_id == annotator_id,
                    Task.status.in_(['assigned', 'in_progress'])
                ).order_by(Task.priority_level.desc(), Task.created_at.asc()).all()
            else:
                # Get all pending tasks
                tasks = db.query(Task).filter(
                    Task.status == 'pending'
                ).order_by(Task.priority_level.desc(), Task.created_at.asc()).all()
            
            task_list = []
            for task in tasks:
                task_list.append({
                    'task_id': task.task_id,
                    'content': task.content[:200] + '...' if len(task.content) > 200 else task.content,
                    'task_type': task.task_type,
                    'complexity_score': task.complexity_score,
                    'estimated_time': task.estimated_time,
                    'priority_level': task.priority_level,
                    'status': task.status,
                    'assigned_annotator_id': task.assigned_annotator_id,
                    'created_at': task.created_at.isoformat()
                })
            
            return {
                'success': True,
                'tasks': task_list,
                'count': len(task_list)
            }
            
        except Exception as e:
            logger.error("Error getting task queue", error=str(e))
            return {
                'success': False,
                'error': str(e),
                'tasks': []
            }
    
    @log_execution_time
    async def complete_task(self, task_id: str, feedback: str, quality_score: float = None) -> Dict[str, Any]:
        """Mark task as completed with feedback"""
        try:
            db = next(get_db())
            
            # Get task
            task = db.query(Task).filter(Task.task_id == task_id).first()
            if not task:
                return {
                    'success': False,
                    'error': 'Task not found'
                }
            
            # Update task status
            task.status = 'completed'
            task.completed_at = datetime.utcnow()
            db.commit()
            
            # Store feedback sample
            from src.core.database import FeedbackSample
            feedback_sample = FeedbackSample(
                task_id=task_id,
                original_content=task.content,
                human_feedback=feedback,
                feedback_type='completion',
                annotator_id=task.assigned_annotator_id,
                quality_score=quality_score,
                metadata={
                    'task_type': task.task_type,
                    'complexity_score': task.complexity_score,
                    'completion_time': datetime.utcnow().isoformat()
                }
            )
            db.add(feedback_sample)
            db.commit()
            
            logger.info("Task completed successfully", task_id=task_id)
            
            return {
                'success': True,
                'completion_time': datetime.utcnow().isoformat(),
                'feedback_stored': True
            }
            
        except Exception as e:
            logger.error("Error completing task", error=str(e))
            return {
                'success': False,
                'error': str(e)
            }

# Global task router instance
task_router = SmartTaskRouter() 