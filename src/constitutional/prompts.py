from typing import List, Dict, Any

class PromptTemplates:
    """Structured prompt templates for constitutional AI operations"""
    
    @staticmethod
    def constitutional_principle_extraction(feedback_samples: List[Dict[str, Any]]) -> str:
        """Template for extracting constitutional principles from feedback"""
        feedback_text = "\n".join([
            f"Original: {sample.get('original_content', '')}\n"
            f"Feedback: {sample.get('human_feedback', '')}\n"
            f"Type: {sample.get('feedback_type', '')}\n"
            for sample in feedback_samples
        ])
        
        return f"""
        Analyze the following human feedback samples and extract implicit constitutional principles that guide AI behavior.
        
        Feedback Samples:
        {feedback_text}
        
        Instructions:
        1. Identify recurring patterns in the feedback
        2. Extract general principles that could guide AI behavior
        3. Categorize principles by type (safety, helpfulness, honesty, etc.)
        4. Provide confidence scores for each principle (0-1)
        5. Consider cultural context and sensitivity
        
        Format your response as a JSON object with the following structure:
        {{
            "principles": [
                {{
                    "principle_text": "Clear, actionable principle statement",
                    "category": "safety|helpfulness|honesty|cultural_sensitivity",
                    "confidence_score": 0.85,
                    "cultural_context": {{"regions": ["global"], "considerations": ["..."]}},
                    "supporting_evidence": ["specific feedback examples that support this principle"]
                }}
            ],
            "summary": "Brief summary of key insights",
            "confidence_overall": 0.8
        }}
        """
    
    @staticmethod
    def principle_validation(principle: Dict[str, Any], historical_principles: List[Dict[str, Any]]) -> str:
        """Template for validating proposed principles against historical data"""
        historical_text = "\n".join([
            f"Principle {i+1}: {p.get('principle_text', '')} (Confidence: {p.get('confidence_score', 0)})"
            for i, p in enumerate(historical_principles)
        ])
        
        return f"""
        Validate the following proposed constitutional principle against historical principles and best practices.
        
        Proposed Principle:
        {principle.get('principle_text', '')}
        Category: {principle.get('category', '')}
        Confidence: {principle.get('confidence_score', 0)}
        
        Historical Principles:
        {historical_text}
        
        Instructions:
        1. Check for consistency with existing principles
        2. Identify potential conflicts or contradictions
        3. Assess cultural sensitivity and inclusivity
        4. Evaluate clarity and actionability
        5. Provide specific recommendations for improvement
        
        Format your response as a JSON object:
        {{
            "is_valid": true/false,
            "confidence_score": 0.85,
            "consistency_score": 0.9,
            "conflicts": ["list of conflicts if any"],
            "recommendations": ["specific improvement suggestions"],
            "cultural_assessment": {{"sensitivity": "high|medium|low", "concerns": ["..."]}},
            "final_principle": "improved principle text if needed"
        }}
        """
    
    @staticmethod
    def task_complexity_analysis(task_content: str) -> str:
        """Template for analyzing task complexity"""
        return f"""
        Analyze the complexity of the following annotation task.
        
        Task Content:
        {task_content}
        
        Instructions:
        1. Assess the cognitive complexity (1-10 scale)
        2. Estimate required expertise level (beginner|intermediate|expert)
        3. Identify potential challenges or ambiguities
        4. Estimate completion time in minutes
        5. Suggest optimal annotator characteristics
        
        Format your response as a JSON object:
        {{
            "complexity_score": 7.5,
            "expertise_level": "intermediate",
            "estimated_time_minutes": 15,
            "challenges": ["list of potential challenges"],
            "required_skills": ["list of required skills"],
            "cultural_considerations": ["any cultural factors to consider"],
            "confidence": 0.85
        }}
        """
    
    @staticmethod
    def quality_prediction(annotator_profile: Dict[str, Any], task_details: Dict[str, Any]) -> str:
        """Template for predicting annotation quality"""
        return f"""
        Predict the quality of annotation for the following annotator-task pairing.
        
        Annotator Profile:
        - Skills: {annotator_profile.get('skill_scores', {})}
        - Performance History: {annotator_profile.get('performance_history', {})}
        - Cultural Background: {annotator_profile.get('cultural_background', '')}
        - Languages: {annotator_profile.get('languages', [])}
        
        Task Details:
        - Type: {task_details.get('task_type', '')}
        - Complexity: {task_details.get('complexity_score', 0)}
        - Content: {task_details.get('content', '')[:200]}...
        
        Instructions:
        1. Assess skill-task match (0-1 scale)
        2. Predict quality score (0-1 scale)
        3. Identify potential issues or risks
        4. Suggest alternative annotators if needed
        5. Provide confidence in prediction
        
        Format your response as a JSON object:
        {{
            "skill_match_score": 0.85,
            "predicted_quality": 0.92,
            "confidence": 0.88,
            "risks": ["potential quality issues"],
            "recommendations": ["suggestions for improvement"],
            "alternative_annotators": ["list of better matches if any"]
        }}
        """
    
    @staticmethod
    def cultural_context_analysis(content: str, target_regions: List[str] = None) -> str:
        """Template for analyzing cultural context and sensitivity"""
        regions_text = ", ".join(target_regions) if target_regions else "global"
        
        return f"""
        Analyze the cultural context and sensitivity of the following content for {regions_text} audiences.
        
        Content:
        {content}
        
        Instructions:
        1. Identify cultural references and implications
        2. Assess potential sensitivity issues
        3. Evaluate inclusivity and accessibility
        4. Suggest cultural adaptations if needed
        5. Provide region-specific considerations
        
        Format your response as a JSON object:
        {{
            "cultural_references": ["list of cultural elements"],
            "sensitivity_level": "low|medium|high",
            "potential_issues": ["list of potential problems"],
            "inclusivity_score": 0.85,
            "adaptations_needed": ["suggested changes"],
            "region_specific": {{
                "region": "specific considerations for each region"
            }},
            "overall_assessment": "summary of cultural appropriateness"
        }}
        """
    
    @staticmethod
    def consensus_validation(responses: List[str]) -> str:
        """Template for validating consensus among multiple model responses"""
        responses_text = "\n".join([
            f"Response {i+1}: {response}"
            for i, response in enumerate(responses)
        ])
        
        return f"""
        Analyze the consensus among the following AI model responses and identify the most reliable conclusion.
        
        Responses:
        {responses_text}
        
        Instructions:
        1. Identify areas of agreement and disagreement
        2. Assess the strength of consensus (0-1 scale)
        3. Identify potential biases or errors
        4. Provide a synthesized conclusion
        5. Suggest additional validation if needed
        
        Format your response as a JSON object:
        {{
            "consensus_strength": 0.85,
            "agreement_areas": ["points of agreement"],
            "disagreement_areas": ["points of disagreement"],
            "synthesized_conclusion": "best combined conclusion",
            "confidence": 0.9,
            "validation_needed": ["additional checks if any"],
            "potential_biases": ["identified biases or errors"]
        }}
        """ 