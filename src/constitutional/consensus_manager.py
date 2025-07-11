import json
import numpy as np
from typing import List, Dict, Any, Optional
from src.constitutional.api_client import multi_model_client
from src.constitutional.prompts import PromptTemplates
from src.core.utils import logger, log_execution_time

class ConsensusManager:
    """Manages consensus among multiple AI model responses"""
    
    def __init__(self):
        self.prompt_templates = PromptTemplates()
    
    @log_execution_time
    async def validate_consensus(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate consensus among multiple model responses"""
        try:
            # Extract content from successful responses
            successful_responses = [r for r in responses if r.get('success', False)]
            
            if not successful_responses:
                return {
                    'consensus_valid': False,
                    'confidence': 0.0,
                    'error': 'No successful responses to validate'
                }
            
            # If only one response, return it directly
            if len(successful_responses) == 1:
                return {
                    'consensus_valid': True,
                    'confidence': 1.0,
                    'consensus': successful_responses[0]['content'],
                    'agreement_score': 1.0
                }
            
            # Extract text content for consensus analysis
            response_texts = [r['content'] for r in successful_responses]
            
            # Generate consensus validation prompt
            prompt = self.prompt_templates.consensus_validation(response_texts)
            
            # Get consensus validation from a different model
            validation_response = await multi_model_client.generate_response(
                prompt,
                providers=['anthropic'],  # Use different provider for validation
                max_tokens=1500,
                temperature=0.2
            )
            
            if not validation_response['success']:
                # Fallback to simple consensus
                return self._simple_consensus(successful_responses)
            
            try:
                validation_result = json.loads(validation_response['content'])
                
                return {
                    'consensus_valid': validation_result.get('consensus_strength', 0) > 0.7,
                    'confidence': validation_result.get('confidence', 0.5),
                    'consensus': validation_result.get('synthesized_conclusion', ''),
                    'agreement_score': validation_result.get('consensus_strength', 0),
                    'agreement_areas': validation_result.get('agreement_areas', []),
                    'disagreement_areas': validation_result.get('disagreement_areas', []),
                    'potential_biases': validation_result.get('potential_biases', [])
                }
                
            except json.JSONDecodeError:
                return self._simple_consensus(successful_responses)
                
        except Exception as e:
            logger.error("Error in consensus validation", error=str(e))
            return {
                'consensus_valid': False,
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _simple_consensus(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Simple consensus calculation when validation fails"""
        try:
            # Calculate basic similarity scores
            contents = [r['content'] for r in responses]
            
            # Simple consensus: return the most common response
            content_counts = {}
            for content in contents:
                content_counts[content] = content_counts.get(content, 0) + 1
            
            most_common = max(content_counts.items(), key=lambda x: x[1])
            consensus_strength = most_common[1] / len(contents)
            
            return {
                'consensus_valid': consensus_strength > 0.5,
                'confidence': consensus_strength,
                'consensus': most_common[0],
                'agreement_score': consensus_strength
            }
            
        except Exception as e:
            logger.error("Error in simple consensus", error=str(e))
            return {
                'consensus_valid': False,
                'confidence': 0.0,
                'error': str(e)
            }
    
    @log_execution_time
    async def weighted_consensus_voting(self, responses: List[Dict[str, Any]], weights: Dict[str, float] = None) -> Dict[str, Any]:
        """Perform weighted consensus voting among model responses"""
        try:
            if not responses:
                return {
                    'consensus_valid': False,
                    'confidence': 0.0,
                    'error': 'No responses provided'
                }
            
            # Default weights if not provided
            if not weights:
                weights = {
                    'openai': 0.4,
                    'anthropic': 0.4,
                    'cohere': 0.2
                }
            
            # Calculate weighted scores
            weighted_scores = {}
            total_weight = 0
            
            for response in responses:
                if not response.get('success', False):
                    continue
                
                provider = response.get('provider', 'unknown')
                weight = weights.get(provider, 0.1)
                content = response.get('content', '')
                
                if content:
                    weighted_scores[content] = weighted_scores.get(content, 0) + weight
                    total_weight += weight
            
            if not weighted_scores:
                return {
                    'consensus_valid': False,
                    'confidence': 0.0,
                    'error': 'No valid responses for weighted voting'
                }
            
            # Find the response with highest weighted score
            best_response = max(weighted_scores.items(), key=lambda x: x[1])
            confidence = best_response[1] / total_weight if total_weight > 0 else 0
            
            return {
                'consensus_valid': confidence > 0.5,
                'confidence': confidence,
                'consensus': best_response[0],
                'weighted_scores': weighted_scores,
                'total_weight': total_weight
            }
            
        except Exception as e:
            logger.error("Error in weighted consensus voting", error=str(e))
            return {
                'consensus_valid': False,
                'confidence': 0.0,
                'error': str(e)
            }
    
    @log_execution_time
    async def conflict_resolution(self, conflicting_responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Resolve conflicts between conflicting model responses"""
        try:
            if len(conflicting_responses) < 2:
                return {
                    'resolved': True,
                    'resolution': conflicting_responses[0] if conflicting_responses else None,
                    'confidence': 1.0
                }
            
            # Analyze conflicts
            conflict_analysis = await self._analyze_conflicts(conflicting_responses)
            
            # Generate resolution strategy
            resolution = await self._generate_resolution(conflict_analysis)
            
            return {
                'resolved': True,
                'resolution': resolution['resolution'],
                'confidence': resolution['confidence'],
                'conflict_analysis': conflict_analysis,
                'resolution_strategy': resolution['strategy']
            }
            
        except Exception as e:
            logger.error("Error in conflict resolution", error=str(e))
            return {
                'resolved': False,
                'error': str(e)
            }
    
    async def _analyze_conflicts(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the nature of conflicts between responses"""
        try:
            # Extract key differences
            contents = [r.get('content', '') for r in responses]
            providers = [r.get('provider', 'unknown') for r in responses]
            
            # Simple conflict analysis
            unique_contents = set(contents)
            conflict_level = len(unique_contents) / len(contents) if contents else 0
            
            return {
                'conflict_level': conflict_level,
                'unique_responses': len(unique_contents),
                'total_responses': len(contents),
                'providers': providers,
                'response_variety': 'high' if conflict_level > 0.5 else 'low'
            }
            
        except Exception as e:
            logger.error("Error analyzing conflicts", error=str(e))
            return {
                'conflict_level': 1.0,
                'error': str(e)
            }
    
    async def _generate_resolution(self, conflict_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate resolution strategy for conflicts"""
        try:
            conflict_level = conflict_analysis.get('conflict_level', 1.0)
            
            if conflict_level < 0.3:
                # Low conflict - use simple consensus
                strategy = "simple_consensus"
                confidence = 0.8
            elif conflict_level < 0.7:
                # Medium conflict - use weighted voting
                strategy = "weighted_voting"
                confidence = 0.6
            else:
                # High conflict - use expert validation
                strategy = "expert_validation"
                confidence = 0.4
            
            return {
                'strategy': strategy,
                'confidence': confidence,
                'reasoning': f"Conflict level {conflict_level:.2f} suggests {strategy} approach"
            }
            
        except Exception as e:
            logger.error("Error generating resolution", error=str(e))
            return {
                'strategy': 'fallback',
                'confidence': 0.3,
                'error': str(e)
            }
    
    @log_execution_time
    async def principle_ranking(self, principles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank principles by confidence and consensus strength"""
        try:
            if not principles:
                return []
            
            # Calculate ranking scores
            ranked_principles = []
            
            for principle in principles:
                # Base score from confidence
                base_score = principle.get('confidence_score', 0.5)
                
                # Bonus for validation score
                validation_bonus = principle.get('validation_score', 0.5) * 0.2
                
                # Bonus for consistency
                consistency_bonus = principle.get('consistency_score', 0.5) * 0.1
                
                # Category weighting
                category = principle.get('category', 'general')
                category_weights = {
                    'safety': 1.2,
                    'helpfulness': 1.0,
                    'honesty': 1.1,
                    'cultural_sensitivity': 1.3
                }
                category_multiplier = category_weights.get(category, 1.0)
                
                # Calculate final score
                final_score = (base_score + validation_bonus + consistency_bonus) * category_multiplier
                
                ranked_principles.append({
                    **principle,
                    'ranking_score': final_score
                })
            
            # Sort by ranking score
            ranked_principles.sort(key=lambda x: x['ranking_score'], reverse=True)
            
            # Add rank position
            for i, principle in enumerate(ranked_principles):
                principle['rank'] = i + 1
            
            return ranked_principles
            
        except Exception as e:
            logger.error("Error in principle ranking", error=str(e))
            return principles  # Return original list if ranking fails

# Global consensus manager instance
consensus_manager = ConsensusManager() 