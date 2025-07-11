import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.core.database import get_db, Annotator, FeedbackSample, Task
from src.core.utils import logger, log_execution_time
from src.core.cache import cache

class AnnotatorManager:
    """Manages annotator profiles, skills, and performance tracking"""
    
    def __init__(self):
        pass
    
    @log_execution_time
    async def register_annotator(self, annotator_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new annotator"""
        try:
            db = next(get_db())
            
            # Check if annotator already exists
            existing = db.query(Annotator).filter(
                Annotator.annotator_id == annotator_data['annotator_id']
            ).first()
            
            if existing:
                return {
                    'success': False,
                    'error': 'Annotator already exists'
                }
            
            # Create new annotator
            annotator = Annotator(
                annotator_id=annotator_data['annotator_id'],
                skill_scores=annotator_data.get('skill_scores', {}),
                performance_history={
                    'total_tasks': 0,
                    'average_quality': 0.0,
                    'recent_performance': [],
                    'months_active': 0
                },
                cultural_background=annotator_data.get('cultural_background', ''),
                languages=annotator_data.get('languages', []),
                availability_status='available'
            )
            
            db.add(annotator)
            db.commit()
            
            logger.info("Annotator registered successfully", annotator_id=annotator_data['annotator_id'])
            
            return {
                'success': True,
                'annotator_id': annotator_data['annotator_id'],
                'message': 'Annotator registered successfully'
            }
            
        except Exception as e:
            logger.error("Error registering annotator", error=str(e))
            return {
                'success': False,
                'error': str(e)
            }
    
    @log_execution_time
    async def get_annotator_profile(self, annotator_id: str) -> Dict[str, Any]:
        """Get annotator profile and performance data"""
        try:
            db = next(get_db())
            
            annotator = db.query(Annotator).filter(
                Annotator.annotator_id == annotator_id
            ).first()
            
            if not annotator:
                return {
                    'success': False,
                    'error': 'Annotator not found'
                }
            
            # Get recent performance data
            recent_tasks = await self._get_recent_tasks(annotator_id, db)
            performance_metrics = await self._calculate_performance_metrics(annotator_id, db)
            
            profile = {
                'annotator_id': annotator.annotator_id,
                'skill_scores': annotator.skill_scores or {},
                'performance_history': annotator.performance_history or {},
                'cultural_background': annotator.cultural_background,
                'languages': annotator.languages or [],
                'availability_status': annotator.availability_status,
                'created_at': annotator.created_at.isoformat(),
                'updated_at': annotator.updated_at.isoformat(),
                'recent_tasks': recent_tasks,
                'performance_metrics': performance_metrics
            }
            
            return {
                'success': True,
                'profile': profile
            }
            
        except Exception as e:
            logger.error("Error getting annotator profile", error=str(e))
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _get_recent_tasks(self, annotator_id: str, db: Session) -> List[Dict[str, Any]]:
        """Get recent tasks for an annotator"""
        try:
            # Get completed tasks in last 30 days
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            
            tasks = db.query(Task).filter(
                Task.assigned_annotator_id == annotator_id,
                Task.status == 'completed',
                Task.completed_at >= thirty_days_ago
            ).order_by(Task.completed_at.desc()).limit(10).all()
            
            task_list = []
            for task in tasks:
                task_list.append({
                    'task_id': task.task_id,
                    'task_type': task.task_type,
                    'complexity_score': task.complexity_score,
                    'completed_at': task.completed_at.isoformat(),
                    'estimated_time': task.estimated_time
                })
            
            return task_list
            
        except Exception as e:
            logger.error("Error getting recent tasks", error=str(e))
            return []
    
    async def _calculate_performance_metrics(self, annotator_id: str, db: Session) -> Dict[str, Any]:
        """Calculate performance metrics for an annotator"""
        try:
            # Get all feedback samples for this annotator
            feedback_samples = db.query(FeedbackSample).filter(
                FeedbackSample.annotator_id == annotator_id,
                FeedbackSample.quality_score.isnot(None)
            ).all()
            
            if not feedback_samples:
                return {
                    'total_tasks': 0,
                    'average_quality': 0.0,
                    'quality_trend': 'stable',
                    'completion_rate': 0.0
                }
            
            # Calculate metrics
            total_tasks = len(feedback_samples)
            quality_scores = [sample.quality_score for sample in feedback_samples]
            average_quality = np.mean(quality_scores)
            
            # Calculate quality trend
            if len(quality_scores) >= 5:
                recent_avg = np.mean(quality_scores[-5:])
                overall_avg = np.mean(quality_scores[:-5]) if len(quality_scores) > 5 else recent_avg
                
                if recent_avg > overall_avg + 0.1:
                    quality_trend = 'improving'
                elif recent_avg < overall_avg - 0.1:
                    quality_trend = 'declining'
                else:
                    quality_trend = 'stable'
            else:
                quality_trend = 'insufficient_data'
            
            # Calculate completion rate
            total_assigned = db.query(Task).filter(
                Task.assigned_annotator_id == annotator_id
            ).count()
            
            completed_tasks = db.query(Task).filter(
                Task.assigned_annotator_id == annotator_id,
                Task.status == 'completed'
            ).count()
            
            completion_rate = completed_tasks / total_assigned if total_assigned > 0 else 0.0
            
            return {
                'total_tasks': total_tasks,
                'average_quality': average_quality,
                'quality_trend': quality_trend,
                'completion_rate': completion_rate,
                'recent_performance': quality_scores[-10:] if len(quality_scores) >= 10 else quality_scores
            }
            
        except Exception as e:
            logger.error("Error calculating performance metrics", error=str(e))
            return {
                'total_tasks': 0,
                'average_quality': 0.0,
                'quality_trend': 'error',
                'completion_rate': 0.0
            }
    
    @log_execution_time
    async def update_availability(self, annotator_id: str, status: str) -> Dict[str, Any]:
        """Update annotator availability status"""
        try:
            db = next(get_db())
            
            annotator = db.query(Annotator).filter(
                Annotator.annotator_id == annotator_id
            ).first()
            
            if not annotator:
                return {
                    'success': False,
                    'error': 'Annotator not found'
                }
            
            # Validate status
            valid_statuses = ['available', 'busy', 'unavailable', 'on_break']
            if status not in valid_statuses:
                return {
                    'success': False,
                    'error': f'Invalid status. Must be one of: {valid_statuses}'
                }
            
            # Update status
            annotator.availability_status = status
            annotator.updated_at = datetime.utcnow()
            db.commit()
            
            logger.info("Annotator availability updated", 
                       annotator_id=annotator_id, 
                       status=status)
            
            return {
                'success': True,
                'annotator_id': annotator_id,
                'new_status': status,
                'updated_at': annotator.updated_at.isoformat()
            }
            
        except Exception as e:
            logger.error("Error updating availability", error=str(e))
            return {
                'success': False,
                'error': str(e)
            }
    
    @log_execution_time
    async def update_skills(self, annotator_id: str, skill_updates: Dict[str, float]) -> Dict[str, Any]:
        """Update annotator skill scores"""
        try:
            db = next(get_db())
            
            annotator = db.query(Annotator).filter(
                Annotator.annotator_id == annotator_id
            ).first()
            
            if not annotator:
                return {
                    'success': False,
                    'error': 'Annotator not found'
                }
            
            # Update skill scores
            current_skills = annotator.skill_scores or {}
            current_skills.update(skill_updates)
            
            # Validate skill scores (should be between 0 and 1)
            for skill, score in current_skills.items():
                if not 0 <= score <= 1:
                    return {
                        'success': False,
                        'error': f'Invalid skill score for {skill}: {score}. Must be between 0 and 1.'
                    }
            
            annotator.skill_scores = current_skills
            annotator.updated_at = datetime.utcnow()
            db.commit()
            
            logger.info("Annotator skills updated", 
                       annotator_id=annotator_id, 
                       updated_skills=list(skill_updates.keys()))
            
            return {
                'success': True,
                'annotator_id': annotator_id,
                'updated_skills': skill_updates,
                'total_skills': len(current_skills)
            }
            
        except Exception as e:
            logger.error("Error updating skills", error=str(e))
            return {
                'success': False,
                'error': str(e)
            }
    
    @log_execution_time
    async def get_matching_annotators(self, task_requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get annotators that match specific task requirements"""
        try:
            db = next(get_db())
            
            # Get available annotators
            available_annotators = db.query(Annotator).filter(
                Annotator.availability_status == 'available'
            ).all()
            
            matching_annotators = []
            
            for annotator in available_annotators:
                match_score = await self._calculate_match_score(annotator, task_requirements)
                
                if match_score > 0.5:  # Minimum match threshold
                    matching_annotators.append({
                        'annotator_id': annotator.annotator_id,
                        'match_score': match_score,
                        'skill_scores': annotator.skill_scores or {},
                        'cultural_background': annotator.cultural_background,
                        'languages': annotator.languages or [],
                        'performance_history': annotator.performance_history or {}
                    })
            
            # Sort by match score
            matching_annotators.sort(key=lambda x: x['match_score'], reverse=True)
            
            return {
                'success': True,
                'matching_annotators': matching_annotators,
                'count': len(matching_annotators)
            }
            
        except Exception as e:
            logger.error("Error finding matching annotators", error=str(e))
            return {
                'success': False,
                'error': str(e),
                'matching_annotators': []
            }
    
    async def _calculate_match_score(self, annotator: Annotator, requirements: Dict[str, Any]) -> float:
        """Calculate match score between annotator and task requirements"""
        try:
            score = 0.0
            total_weight = 0.0
            
            # Skill match
            required_skills = requirements.get('required_skills', [])
            skill_scores = annotator.skill_scores or {}
            
            for skill in required_skills:
                skill_score = skill_scores.get(skill, 0.0)
                score += skill_score * 0.4  # 40% weight for skills
                total_weight += 0.4
            
            # Cultural match
            required_cultural_context = requirements.get('cultural_context', '')
            if required_cultural_context and annotator.cultural_background:
                cultural_match = self._calculate_cultural_similarity(
                    required_cultural_context, annotator.cultural_background
                )
                score += cultural_match * 0.3  # 30% weight for cultural match
                total_weight += 0.3
            
            # Language match
            required_languages = requirements.get('required_languages', [])
            annotator_languages = annotator.languages or []
            
            if required_languages and annotator_languages:
                language_match = len(set(required_languages) & set(annotator_languages)) / len(required_languages)
                score += language_match * 0.2  # 20% weight for language match
                total_weight += 0.2
            
            # Performance match
            performance_history = annotator.performance_history or {}
            avg_quality = performance_history.get('average_quality', 0.5)
            score += avg_quality * 0.1  # 10% weight for performance
            total_weight += 0.1
            
            return score / total_weight if total_weight > 0 else 0.0
            
        except Exception as e:
            logger.error("Error calculating match score", error=str(e))
            return 0.0
    
    def _calculate_cultural_similarity(self, required_context: str, annotator_background: str) -> float:
        """Calculate cultural similarity between required context and annotator background"""
        try:
            # Simple keyword-based similarity
            required_words = set(required_context.lower().split())
            background_words = set(annotator_background.lower().split())
            
            if not required_words or not background_words:
                return 0.5
            
            intersection = required_words & background_words
            union = required_words | background_words
            
            return len(intersection) / len(union) if union else 0.5
            
        except Exception:
            return 0.5
    
    @log_execution_time
    async def update_performance_history(self, annotator_id: str, task_result: Dict[str, Any]) -> bool:
        """Update annotator performance history after task completion"""
        try:
            db = next(get_db())
            
            annotator = db.query(Annotator).filter(
                Annotator.annotator_id == annotator_id
            ).first()
            
            if not annotator:
                return False
            
            # Get current performance history
            performance_history = annotator.performance_history or {
                'total_tasks': 0,
                'average_quality': 0.0,
                'recent_performance': [],
                'months_active': 0
            }
            
            # Update metrics
            quality_score = task_result.get('quality_score', 0.5)
            performance_history['total_tasks'] += 1
            performance_history['recent_performance'].append(quality_score)
            
            # Keep only last 20 performance scores
            if len(performance_history['recent_performance']) > 20:
                performance_history['recent_performance'] = performance_history['recent_performance'][-20:]
            
            # Update average quality
            performance_history['average_quality'] = np.mean(performance_history['recent_performance'])
            
            # Update months active
            created_date = annotator.created_at
            months_active = (datetime.utcnow() - created_date).days / 30
            performance_history['months_active'] = max(performance_history['months_active'], months_active)
            
            # Save updated history
            annotator.performance_history = performance_history
            annotator.updated_at = datetime.utcnow()
            db.commit()
            
            logger.info("Performance history updated", 
                       annotator_id=annotator_id, 
                       new_quality=quality_score)
            
            return True
            
        except Exception as e:
            logger.error("Error updating performance history", error=str(e))
            return False
    
    @log_execution_time
    async def get_annotator_analytics(self, annotator_id: str = None) -> Dict[str, Any]:
        """Get analytics for specific annotator or all annotators"""
        try:
            db = next(get_db())
            
            if annotator_id:
                # Get specific annotator analytics
                annotator = db.query(Annotator).filter(
                    Annotator.annotator_id == annotator_id
                ).first()
                
                if not annotator:
                    return {
                        'success': False,
                        'error': 'Annotator not found'
                    }
                
                analytics = await self._calculate_annotator_analytics(annotator, db)
                
                return {
                    'success': True,
                    'annotator_id': annotator_id,
                    'analytics': analytics
                }
            else:
                # Get analytics for all annotators
                annotators = db.query(Annotator).all()
                
                all_analytics = []
                for annotator in annotators:
                    analytics = await self._calculate_annotator_analytics(annotator, db)
                    all_analytics.append({
                        'annotator_id': annotator.annotator_id,
                        'analytics': analytics
                    })
                
                return {
                    'success': True,
                    'annotators': all_analytics,
                    'count': len(all_analytics)
                }
                
        except Exception as e:
            logger.error("Error getting annotator analytics", error=str(e))
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _calculate_annotator_analytics(self, annotator: Annotator, db: Session) -> Dict[str, Any]:
        """Calculate detailed analytics for an annotator"""
        try:
            # Get performance metrics
            performance_metrics = await self._calculate_performance_metrics(annotator.annotator_id, db)
            
            # Get task type distribution
            task_types = db.query(Task.task_type).filter(
                Task.assigned_annotator_id == annotator.annotator_id,
                Task.status == 'completed'
            ).all()
            
            type_counts = {}
            for task_type in task_types:
                type_counts[task_type[0]] = type_counts.get(task_type[0], 0) + 1
            
            # Calculate skill utilization
            skill_scores = annotator.skill_scores or {}
            skill_utilization = {}
            for skill, score in skill_scores.items():
                if skill in type_counts:
                    skill_utilization[skill] = {
                        'score': score,
                        'tasks_completed': type_counts[skill],
                        'utilization_rate': type_counts[skill] / performance_metrics['total_tasks'] if performance_metrics['total_tasks'] > 0 else 0
                    }
            
            return {
                'performance_metrics': performance_metrics,
                'task_type_distribution': type_counts,
                'skill_utilization': skill_utilization,
                'availability_status': annotator.availability_status,
                'cultural_background': annotator.cultural_background,
                'languages': annotator.languages or []
            }
            
        except Exception as e:
            logger.error("Error calculating annotator analytics", error=str(e))
            return {
                'performance_metrics': {},
                'task_type_distribution': {},
                'skill_utilization': {},
                'error': str(e)
            }

# Global annotator manager instance
annotator_manager = AnnotatorManager() 