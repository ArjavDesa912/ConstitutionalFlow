import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from src.core.database import get_db, ConstitutionalPrinciple
from src.constitutional.api_client import multi_model_client
from src.constitutional.prompts import PromptTemplates
from src.core.utils import logger, log_execution_time
from src.core.cache import cache

class ConstitutionalEvolutionEngine:
    """Core engine for analyzing feedback and evolving constitutional principles"""
    
    def __init__(self):
        self.prompt_templates = PromptTemplates()
    
    @log_execution_time
    async def analyze_feedback_batch(self, feedback_samples: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze a batch of feedback samples to extract constitutional principles"""
        try:
            # Generate prompt for principle extraction
            prompt = self.prompt_templates.constitutional_principle_extraction(feedback_samples)
            
            # Get consensus from multiple models
            consensus_response = await multi_model_client.generate_consensus(
                prompt,
                max_tokens=2000,
                temperature=0.3
            )
            
            if not consensus_response['success']:
                logger.error("Failed to get consensus for principle extraction")
                return {
                    'success': False,
                    'error': 'Failed to extract principles from feedback',
                    'principles': []
                }
            
            # Parse the consensus response
            try:
                parsed_response = json.loads(consensus_response['consensus'])
                principles = parsed_response.get('principles', [])
                
                # Validate and store principles
                validated_principles = await self._validate_principles(principles)
                
                return {
                    'success': True,
                    'principles': validated_principles,
                    'summary': parsed_response.get('summary', ''),
                    'confidence': consensus_response['confidence']
                }
                
            except json.JSONDecodeError as e:
                logger.error("Failed to parse consensus response", error=str(e))
                return {
                    'success': False,
                    'error': 'Invalid response format',
                    'principles': []
                }
                
        except Exception as e:
            logger.error("Error in feedback analysis", error=str(e))
            return {
                'success': False,
                'error': str(e),
                'principles': []
            }
    
    async def _validate_principles(self, principles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate extracted principles against existing ones"""
        validated_principles = []
        
        for principle in principles:
            # Get historical principles for comparison
            historical_principles = await self._get_historical_principles()
            
            # Validate the principle
            validation_result = await self._validate_single_principle(principle, historical_principles)
            
            if validation_result['is_valid']:
                validated_principles.append({
                    **principle,
                    'validation_score': validation_result['confidence_score'],
                    'consistency_score': validation_result['consistency_score']
                })
            else:
                logger.warning("Principle validation failed", principle=principle.get('principle_text', ''))
        
        return validated_principles
    
    async def _validate_single_principle(self, principle: Dict[str, Any], historical_principles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate a single principle against historical data"""
        try:
            prompt = self.prompt_templates.principle_validation(principle, historical_principles)
            
            response = await multi_model_client.generate_response(
                prompt,
                providers=['openai', 'anthropic'],
                max_tokens=1500,
                temperature=0.2
            )
            
            if response['success']:
                try:
                    return json.loads(response['content'])
                except json.JSONDecodeError:
                    return {
                        'is_valid': True,
                        'confidence_score': principle.get('confidence_score', 0.5),
                        'consistency_score': 0.5
                    }
            else:
                return {
                    'is_valid': True,
                    'confidence_score': principle.get('confidence_score', 0.5),
                    'consistency_score': 0.5
                }
                
        except Exception as e:
            logger.error("Error validating principle", error=str(e))
            return {
                'is_valid': True,
                'confidence_score': principle.get('confidence_score', 0.5),
                'consistency_score': 0.5
            }
    
    async def _get_historical_principles(self) -> List[Dict[str, Any]]:
        """Get historical principles from database"""
        try:
            # Check cache first
            cache_key = "historical_principles"
            cached_principles = cache.get(cache_key)
            if cached_principles:
                return cached_principles
            
            # Get from database
            db = next(get_db())
            principles = db.query(ConstitutionalPrinciple).filter(
                ConstitutionalPrinciple.is_active == True
            ).order_by(ConstitutionalPrinciple.confidence_score.desc()).limit(20).all()
            
            historical_data = [
                {
                    'principle_text': p.principle_text,
                    'confidence_score': p.confidence_score,
                    'category': p.category
                }
                for p in principles
            ]
            
            # Cache for 1 hour
            cache.set(cache_key, historical_data, expire=3600)
            return historical_data
            
        except Exception as e:
            logger.error("Error getting historical principles", error=str(e))
            return []
    
    @log_execution_time
    async def evolve_principles(self, new_feedback_count: int = 100) -> Dict[str, Any]:
        """Evolve constitutional principles based on recent feedback"""
        try:
            # Get recent feedback samples
            recent_feedback = await self._get_recent_feedback(new_feedback_count)
            
            if not recent_feedback:
                return {
                    'success': False,
                    'error': 'No recent feedback available for evolution',
                    'evolved_principles': []
                }
            
            # Analyze feedback for new principles
            analysis_result = await self.analyze_feedback_batch(recent_feedback)
            
            if not analysis_result['success']:
                return analysis_result
            
            # Compare with existing principles and identify evolution
            evolution_result = await self._identify_principle_evolution(analysis_result['principles'])
            
            return {
                'success': True,
                'evolved_principles': evolution_result['new_principles'],
                'updated_principles': evolution_result['updated_principles'],
                'confidence': analysis_result['confidence']
            }
            
        except Exception as e:
            logger.error("Error in principle evolution", error=str(e))
            return {
                'success': False,
                'error': str(e),
                'evolved_principles': []
            }
    
    async def _get_recent_feedback(self, count: int) -> List[Dict[str, Any]]:
        """Get recent feedback samples from database"""
        try:
            from src.core.database import FeedbackSample
            
            db = next(get_db())
            feedback_samples = db.query(FeedbackSample).order_by(
                FeedbackSample.created_at.desc()
            ).limit(count).all()
            
            return [
                {
                    'original_content': sample.original_content,
                    'human_feedback': sample.human_feedback,
                    'feedback_type': sample.feedback_type,
                    'quality_score': sample.quality_score
                }
                for sample in feedback_samples
            ]
            
        except Exception as e:
            logger.error("Error getting recent feedback", error=str(e))
            return []
    
    async def _identify_principle_evolution(self, new_principles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify which principles are new or need updates"""
        try:
            existing_principles = await self._get_historical_principles()
            existing_texts = {p['principle_text'] for p in existing_principles}
            
            new_principles_list = []
            updated_principles_list = []
            
            for principle in new_principles:
                principle_text = principle.get('principle_text', '')
                
                if principle_text not in existing_texts:
                    new_principles_list.append(principle)
                else:
                    # Check if confidence has changed significantly
                    existing_principle = next(
                        (p for p in existing_principles if p['principle_text'] == principle_text),
                        None
                    )
                    
                    if existing_principle:
                        confidence_diff = abs(
                            principle.get('confidence_score', 0) - existing_principle.get('confidence_score', 0)
                        )
                        
                        if confidence_diff > 0.1:  # Significant change threshold
                            updated_principles_list.append({
                                **principle,
                                'previous_confidence': existing_principle.get('confidence_score', 0)
                            })
            
            return {
                'new_principles': new_principles_list,
                'updated_principles': updated_principles_list
            }
            
        except Exception as e:
            logger.error("Error identifying principle evolution", error=str(e))
            return {
                'new_principles': [],
                'updated_principles': []
            }
    
    async def store_principles(self, principles: List[Dict[str, Any]]) -> bool:
        """Store new principles in the database"""
        try:
            db = next(get_db())
            
            for principle_data in principles:
                # Check if principle already exists
                existing = db.query(ConstitutionalPrinciple).filter(
                    ConstitutionalPrinciple.principle_text == principle_data['principle_text']
                ).first()
                
                if existing:
                    # Update existing principle
                    existing.confidence_score = principle_data.get('confidence_score', existing.confidence_score)
                    existing.category = principle_data.get('category', existing.category)
                    existing.cultural_context = principle_data.get('cultural_context', existing.cultural_context)
                    existing.version_number = (existing.version_number or 0) + 1
                    existing.updated_at = datetime.utcnow()
                else:
                    # Create new principle
                    new_principle = ConstitutionalPrinciple(
                        principle_text=principle_data['principle_text'],
                        category=principle_data.get('category'),
                        confidence_score=principle_data.get('confidence_score', 0.5),
                        cultural_context=principle_data.get('cultural_context'),
                        version_number=1
                    )
                    db.add(new_principle)
            
            db.commit()
            
            # Clear cache
            cache.delete("historical_principles")
            
            logger.info("Successfully stored principles", count=len(principles))
            return True
            
        except Exception as e:
            logger.error("Error storing principles", error=str(e))
            return False

# Global engine instance
evolution_engine = ConstitutionalEvolutionEngine() 