"""
API routes for cultural intelligence engine.
Provides endpoints for cultural analysis, recommendations, and insights.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.dependencies.auth import get_current_active_user
from app.models.user import User
from app.services.cultural_intelligence_engine import (
    get_cultural_engine, CulturalIntelligenceEngine,
    CulturalAnalysisType, CulturalInsight, CulturalProfile
)
from app.integrations.qloo_api import QlooCategory

router = APIRouter()


# Request/Response Models
class CulturalAnalysisRequest(BaseModel):
    analysis_type: str
    social_media_data: Optional[Dict[str, Any]] = None
    user_preferences: Optional[Dict[str, Any]] = None
    user_history: Optional[List[Dict[str, Any]]] = None
    categories: Optional[List[str]] = None
    time_horizon: Optional[str] = "90d"
    analysis_depth: str = "comprehensive"


class CulturalInsightResponse(BaseModel):
    insight_id: str
    insight_type: str
    ai_explanation: str
    confidence_score: float
    cultural_factors: List[str]
    actionable_recommendations: List[str]
    generated_at: str
    expires_at: Optional[str] = None


class CulturalProfileResponse(BaseModel):
    user_id: str
    cultural_dimensions: Dict[str, float]
    dominant_categories: List[str]
    diversity_score: float
    cultural_evolution_trend: str
    influence_network: Dict[str, Any]
    blind_spots: List[str]
    last_updated: str


class RecommendationRequest(BaseModel):
    user_preferences: Dict[str, Any]
    categories: Optional[List[str]] = None
    recommendation_count: int = 10


class TrendAnalysisRequest(BaseModel):
    categories: List[str]
    time_horizon: str = "90d"
    geographic_scope: Optional[List[str]] = None


@router.post("/analyze/patterns", response_model=CulturalInsightResponse)
async def analyze_cultural_patterns(
    request: CulturalAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    cultural_engine: CulturalIntelligenceEngine = Depends(get_cultural_engine)
):
    """Analyze cultural patterns from user's social media data."""
    try:
        if not request.social_media_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Social media data is required for pattern analysis"
            )
        
        insight = await cultural_engine.analyze_cultural_patterns(
            user_id=current_user.id,
            social_media_data=request.social_media_data,
            analysis_depth=request.analysis_depth
        )
        
        return CulturalInsightResponse(
            insight_id=insight.insight_id,
            insight_type=insight.insight_type.value,
            ai_explanation=insight.ai_explanation,
            confidence_score=insight.confidence_score,
            cultural_factors=insight.cultural_factors,
            actionable_recommendations=insight.actionable_recommendations,
            generated_at=insight.generated_at.isoformat(),
            expires_at=insight.expires_at.isoformat() if insight.expires_at else None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze cultural patterns: {str(e)}"
        )


@router.post("/analyze/trends", response_model=CulturalInsightResponse)
async def predict_cultural_trends(
    request: TrendAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    cultural_engine: CulturalIntelligenceEngine = Depends(get_cultural_engine)
):
    """Predict cultural trends for specified categories."""
    try:
        # Convert string categories to QlooCategory enums
        qloo_categories = []
        for cat_str in request.categories:
            try:
                qloo_categories.append(QlooCategory(cat_str.lower()))
            except ValueError:
                # Skip invalid categories
                continue
        
        if not qloo_categories:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one valid category is required"
            )
        
        insight = await cultural_engine.predict_cultural_trends(
            user_id=current_user.id,
            categories=qloo_categories,
            time_horizon=request.time_horizon
        )
        
        return CulturalInsightResponse(
            insight_id=insight.insight_id,
            insight_type=insight.insight_type.value,
            ai_explanation=insight.ai_explanation,
            confidence_score=insight.confidence_score,
            cultural_factors=insight.cultural_factors,
            actionable_recommendations=insight.actionable_recommendations,
            generated_at=insight.generated_at.isoformat(),
            expires_at=insight.expires_at.isoformat() if insight.expires_at else None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to predict cultural trends: {str(e)}"
        )


@router.post("/recommendations", response_model=CulturalInsightResponse)
async def generate_cultural_recommendations(
    request: RecommendationRequest,
    current_user: User = Depends(get_current_active_user),
    cultural_engine: CulturalIntelligenceEngine = Depends(get_cultural_engine)
):
    """Generate cultural recommendations based on user preferences."""
    try:
        insight = await cultural_engine.generate_cultural_recommendations(
            user_id=current_user.id,
            user_preferences=request.user_preferences,
            recommendation_count=request.recommendation_count
        )
        
        return CulturalInsightResponse(
            insight_id=insight.insight_id,
            insight_type=insight.insight_type.value,
            ai_explanation=insight.ai_explanation,
            confidence_score=insight.confidence_score,
            cultural_factors=insight.cultural_factors,
            actionable_recommendations=insight.actionable_recommendations,
            generated_at=insight.generated_at.isoformat(),
            expires_at=insight.expires_at.isoformat() if insight.expires_at else None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


@router.post("/analyze/diversity", response_model=CulturalInsightResponse)
async def assess_cultural_diversity(
    request: CulturalAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    cultural_engine: CulturalIntelligenceEngine = Depends(get_cultural_engine)
):
    """Assess user's cultural diversity."""
    try:
        if not request.user_history:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User history is required for diversity assessment"
            )
        
        insight = await cultural_engine.assess_cultural_diversity(
            user_id=current_user.id,
            user_history=request.user_history
        )
        
        return CulturalInsightResponse(
            insight_id=insight.insight_id,
            insight_type=insight.insight_type.value,
            ai_explanation=insight.ai_explanation,
            confidence_score=insight.confidence_score,
            cultural_factors=insight.cultural_factors,
            actionable_recommendations=insight.actionable_recommendations,
            generated_at=insight.generated_at.isoformat(),
            expires_at=insight.expires_at.isoformat() if insight.expires_at else None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assess cultural diversity: {str(e)}"
        )


@router.post("/analyze/blind-spots", response_model=CulturalInsightResponse)
async def detect_cultural_blind_spots(
    request: CulturalAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    cultural_engine: CulturalIntelligenceEngine = Depends(get_cultural_engine)
):
    """Detect cultural blind spots in user's profile."""
    try:
        if not request.user_preferences:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User preferences are required for blind spot detection"
            )
        
        insight = await cultural_engine.detect_cultural_blind_spots(
            user_id=current_user.id,
            user_profile=request.user_preferences
        )
        
        return CulturalInsightResponse(
            insight_id=insight.insight_id,
            insight_type=insight.insight_type.value,
            ai_explanation=insight.ai_explanation,
            confidence_score=insight.confidence_score,
            cultural_factors=insight.cultural_factors,
            actionable_recommendations=insight.actionable_recommendations,
            generated_at=insight.generated_at.isoformat(),
            expires_at=insight.expires_at.isoformat() if insight.expires_at else None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to detect cultural blind spots: {str(e)}"
        )


@router.post("/profile/build", response_model=CulturalProfileResponse)
async def build_cultural_profile(
    request: CulturalAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    cultural_engine: CulturalIntelligenceEngine = Depends(get_cultural_engine)
):
    """Build comprehensive cultural profile for user."""
    try:
        comprehensive_data = {
            "preferences": request.user_preferences or {},
            "history": request.user_history or [],
            "social_media": request.social_media_data or {}
        }
        
        profile = await cultural_engine.build_cultural_profile(
            user_id=current_user.id,
            comprehensive_data=comprehensive_data
        )
        
        return CulturalProfileResponse(
            user_id=profile.user_id,
            cultural_dimensions=profile.cultural_dimensions,
            dominant_categories=[cat.value for cat in profile.dominant_categories],
            diversity_score=profile.diversity_score,
            cultural_evolution_trend=profile.cultural_evolution_trend,
            influence_network=profile.influence_network,
            blind_spots=profile.blind_spots,
            last_updated=profile.last_updated.isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to build cultural profile: {str(e)}"
        )


@router.get("/profile", response_model=Optional[CulturalProfileResponse])
async def get_cultural_profile(
    current_user: User = Depends(get_current_active_user),
    cultural_engine: CulturalIntelligenceEngine = Depends(get_cultural_engine)
):
    """Get cached cultural profile for user."""
    try:
        # In a real implementation, you'd fetch from cache/database
        # For now, return None to indicate no cached profile
        return None
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cultural profile: {str(e)}"
        )


@router.get("/insights/{insight_id}", response_model=CulturalInsightResponse)
async def get_cultural_insight(
    insight_id: str,
    current_user: User = Depends(get_current_active_user),
    cultural_engine: CulturalIntelligenceEngine = Depends(get_cultural_engine)
):
    """Get specific cultural insight by ID."""
    try:
        # In a real implementation, you'd fetch from cache/database
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insight not found"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cultural insight: {str(e)}"
        )


@router.get("/categories", response_model=List[str])
async def get_supported_categories():
    """Get list of supported cultural categories."""
    return [category.value for category in QlooCategory]


@router.get("/analysis-types", response_model=List[str])
async def get_analysis_types():
    """Get list of supported analysis types."""
    return [analysis_type.value for analysis_type in CulturalAnalysisType]


@router.post("/analyze/comprehensive", response_model=Dict[str, Any])
async def comprehensive_cultural_analysis(
    request: CulturalAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    cultural_engine: CulturalIntelligenceEngine = Depends(get_cultural_engine)
):
    """Perform comprehensive cultural analysis including all types."""
    try:
        results = {}
        
        # Pattern analysis
        if request.social_media_data:
            pattern_insight = await cultural_engine.analyze_cultural_patterns(
                user_id=current_user.id,
                social_media_data=request.social_media_data,
                analysis_depth=request.analysis_depth
            )
            results["pattern_analysis"] = {
                "insight_id": pattern_insight.insight_id,
                "explanation": pattern_insight.ai_explanation,
                "confidence": pattern_insight.confidence_score,
                "recommendations": pattern_insight.actionable_recommendations
            }
        
        # Diversity assessment
        if request.user_history:
            diversity_insight = await cultural_engine.assess_cultural_diversity(
                user_id=current_user.id,
                user_history=request.user_history
            )
            results["diversity_assessment"] = {
                "insight_id": diversity_insight.insight_id,
                "explanation": diversity_insight.ai_explanation,
                "confidence": diversity_insight.confidence_score,
                "recommendations": diversity_insight.actionable_recommendations
            }
        
        # Recommendations
        if request.user_preferences:
            rec_insight = await cultural_engine.generate_cultural_recommendations(
                user_id=current_user.id,
                user_preferences=request.user_preferences
            )
            results["recommendations"] = {
                "insight_id": rec_insight.insight_id,
                "explanation": rec_insight.ai_explanation,
                "confidence": rec_insight.confidence_score,
                "recommendations": rec_insight.actionable_recommendations
            }
            
            # Blind spot detection
            blind_spot_insight = await cultural_engine.detect_cultural_blind_spots(
                user_id=current_user.id,
                user_profile=request.user_preferences
            )
            results["blind_spot_detection"] = {
                "insight_id": blind_spot_insight.insight_id,
                "explanation": blind_spot_insight.ai_explanation,
                "confidence": blind_spot_insight.confidence_score,
                "recommendations": blind_spot_insight.actionable_recommendations
            }
        
        # Trend analysis
        if request.categories:
            qloo_categories = []
            for cat_str in request.categories:
                try:
                    qloo_categories.append(QlooCategory(cat_str.lower()))
                except ValueError:
                    continue
            
            if qloo_categories:
                trend_insight = await cultural_engine.predict_cultural_trends(
                    user_id=current_user.id,
                    categories=qloo_categories,
                    time_horizon=request.time_horizon
                )
                results["trend_analysis"] = {
                    "insight_id": trend_insight.insight_id,
                    "explanation": trend_insight.ai_explanation,
                    "confidence": trend_insight.confidence_score,
                    "recommendations": trend_insight.actionable_recommendations
                }
        
        return {
            "user_id": current_user.id,
            "analysis_timestamp": insight.generated_at.isoformat() if 'insight' in locals() else None,
            "comprehensive_results": results,
            "total_analyses": len(results)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform comprehensive analysis: {str(e)}"
        )
