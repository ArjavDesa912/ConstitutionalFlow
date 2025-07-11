
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from src.core.database import get_db, ConstitutionalPrinciple
from src.constitutional.evolution_engine import evolution_engine
from src.constitutional.consensus_manager import consensus_manager
from src.api.models.constitutional import Principle, PrincipleHistory, FeedbackAnalysisRequest, PrincipleValidationRequest

router = APIRouter()

@router.post("/constitutional/analyze")
async def analyze_feedback(request: FeedbackAnalysisRequest, db: Session = Depends(get_db)):
    """
    Analyze feedback for constitutional principles.
    """
    try:
        # Analyze feedback using the evolution engine
        analysis_result = await evolution_engine.analyze_feedback_batch(request.feedback_samples)
        
        if not analysis_result['success']:
            raise HTTPException(status_code=400, detail=analysis_result['error'])
        
        # Store principles if requested
        if request.store_principles and analysis_result['principles']:
            await evolution_engine.store_principles(analysis_result['principles'])
        
        return {
            "success": True,
            "principles": analysis_result['principles'],
            "summary": analysis_result['summary'],
            "confidence": analysis_result['confidence']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/constitutional/principles", response_model=List[Principle])
async def get_constitutional_principles(
    category: str = None, 
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """
    Retrieve current constitutional principles.
    """
    try:
        query = db.query(ConstitutionalPrinciple)
        
        if active_only:
            query = query.filter(ConstitutionalPrinciple.is_active == True)
        
        if category:
            query = query.filter(ConstitutionalPrinciple.category == category)
        
        principles = query.order_by(ConstitutionalPrinciple.confidence_score.desc()).all()
        
        return [
            Principle(
                id=p.id,
                principle_text=p.principle_text,
                category=p.category,
                confidence_score=p.confidence_score,
                cultural_context=p.cultural_context,
                version_number=p.version_number,
                created_at=p.created_at,
                updated_at=p.updated_at,
                is_active=p.is_active
            )
            for p in principles
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/constitutional/validate")
async def validate_principle_changes(request: PrincipleValidationRequest):
    """
    Validate proposed principle changes.
    """
    try:
        # Get historical principles for comparison
        historical_principles = await evolution_engine._get_historical_principles()
        
        # Validate the proposed principle
        validation_result = await evolution_engine._validate_single_principle(
            request.principle, historical_principles
        )
        
        return {
            "success": True,
            "is_valid": validation_result['is_valid'],
            "confidence_score": validation_result['confidence_score'],
            "consistency_score": validation_result.get('consistency_score', 0.5),
            "recommendations": validation_result.get('recommendations', [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/constitutional/history", response_model=List[PrincipleHistory])
async def get_principle_evolution_history(
    principle_id: int = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get principle evolution history.
    """
    try:
        query = db.query(ConstitutionalPrinciple)
        
        if principle_id:
            query = query.filter(ConstitutionalPrinciple.id == principle_id)
        
        principles = query.order_by(ConstitutionalPrinciple.updated_at.desc()).limit(limit).all()
        
        return [
            PrincipleHistory(
                id=p.id,
                principle_id=p.id,
                principle_text=p.principle_text,
                version_number=p.version_number or 1,
                created_at=p.updated_at
            )
            for p in principles
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/constitutional/evolve")
async def evolve_principles(new_feedback_count: int = 100):
    """
    Evolve constitutional principles based on recent feedback.
    """
    try:
        evolution_result = await evolution_engine.evolve_principles(new_feedback_count)
        
        if not evolution_result['success']:
            raise HTTPException(status_code=400, detail=evolution_result['error'])
        
        return {
            "success": True,
            "evolved_principles": evolution_result['evolved_principles'],
            "updated_principles": evolution_result['updated_principles'],
            "confidence": evolution_result['confidence']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/constitutional/consensus")
async def validate_consensus(responses: List[Dict[str, Any]]):
    """
    Validate consensus among multiple model responses.
    """
    try:
        consensus_result = await consensus_manager.validate_consensus(responses)
        
        return {
            "success": True,
            "consensus_valid": consensus_result['consensus_valid'],
            "confidence": consensus_result['confidence'],
            "consensus": consensus_result.get('consensus', ''),
            "agreement_score": consensus_result.get('agreement_score', 0.0)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/constitutional/weighted-voting")
async def weighted_consensus_voting(
    responses: List[Dict[str, Any]], 
    weights: Dict[str, float] = None
):
    """
    Perform weighted consensus voting among model responses.
    """
    try:
        voting_result = await consensus_manager.weighted_consensus_voting(responses, weights)
        
        return {
            "success": True,
            "consensus_valid": voting_result['consensus_valid'],
            "confidence": voting_result['confidence'],
            "consensus": voting_result.get('consensus', ''),
            "weighted_scores": voting_result.get('weighted_scores', {})
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/constitutional/conflict-resolution")
async def resolve_conflicts(conflicting_responses: List[Dict[str, Any]]):
    """
    Resolve conflicts between conflicting model responses.
    """
    try:
        resolution_result = await consensus_manager.conflict_resolution(conflicting_responses)
        
        return {
            "success": True,
            "resolved": resolution_result['resolved'],
            "resolution": resolution_result.get('resolution'),
            "confidence": resolution_result.get('confidence', 0.0),
            "strategy": resolution_result.get('resolution_strategy', {})
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/constitutional/ranking")
async def rank_principles(category: str = None, db: Session = Depends(get_db)):
    """
    Rank principles by confidence and consensus strength.
    """
    try:
        query = db.query(ConstitutionalPrinciple).filter(ConstitutionalPrinciple.is_active == True)
        
        if category:
            query = query.filter(ConstitutionalPrinciple.category == category)
        
        principles = query.all()
        
        # Convert to dict format for ranking
        principle_dicts = [
            {
                'principle_text': p.principle_text,
                'confidence_score': p.confidence_score,
                'category': p.category,
                'cultural_context': p.cultural_context
            }
            for p in principles
        ]
        
        # Rank principles
        ranked_principles = await consensus_manager.principle_ranking(principle_dicts)
        
        return {
            "success": True,
            "ranked_principles": ranked_principles
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
