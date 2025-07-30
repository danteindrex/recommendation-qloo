from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.api.dependencies.auth import get_current_active_user
from app.models.user import User
from app.models.cultural_data import CulturalProfile, CulturalDataPoint, SocialConnection
from app.services.cultural_intelligence_engine import get_cultural_engine, CulturalIntelligenceEngine
from app.services.social_media_service import SocialMediaService

router = APIRouter()


# Request/Response Models
class CulturalAnalysisRequest(BaseModel):
    include_social_media: bool = True
    analysis_depth: str = "comprehensive"


class CulturalCompatibilityRequest(BaseModel):
    target_user_id: str


class BenchmarkRequest(BaseModel):
    demographics: List[str] = ["global", "millennials", "gen_z"]


class CulturalChallengeRequest(BaseModel):
    difficulty: str = "medium"  # easy, medium, hard
    category: Optional[str] = None


@router.get("/profile")
async def get_cultural_profile(
    response: Response,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    cultural_engine: CulturalIntelligenceEngine = Depends(get_cultural_engine)
):
    """Get user's cultural intelligence profile."""
    try:
        # Get user's social connections
        connections_result = await db.execute(
            select(SocialConnection).where(
                SocialConnection.user_id == current_user.id,
                SocialConnection.connection_status == "active"
            )
        )
        connections = connections_result.scalars().all()
        
        # Get user's cultural data points
        data_points_result = await db.execute(
            select(CulturalDataPoint).where(
                CulturalDataPoint.user_id == current_user.id
            ).order_by(CulturalDataPoint.created_at.desc()).limit(1000)
        )
        data_points = data_points_result.scalars().all()
        
        # Build comprehensive data
        comprehensive_data = {
            "preferences": {},
            "history": [],
            "social_media": {}
        }
        
        # Process data points
        for dp in data_points:
            if dp.platform:
                if dp.platform.value not in comprehensive_data["social_media"]:
                    comprehensive_data["social_media"][dp.platform.value] = []
                comprehensive_data["social_media"][dp.platform.value].append(dp.content)
            
            comprehensive_data["history"].append({
                "date": dp.created_at.isoformat(),
                "category": dp.data_type.value,
                "data": dp.content,
                "confidence": float(dp.confidence_score) if dp.confidence_score else 0.0
            })
        
        # Build cultural profile
        profile = await cultural_engine.build_cultural_profile(
            user_id=str(current_user.id),
            comprehensive_data=comprehensive_data
        )
        
        # Cache response
        response.headers["Cache-Control"] = "public, max-age=3600"  # Cache for 1 hour
        
        return {
            "profile": profile,
            "last_updated": datetime.utcnow(),
            "data_points_analyzed": len(data_points),
            "connected_platforms": [conn.platform.value for conn in connections]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to build cultural profile: {str(e)}"
        )


@router.post("/analyze")
async def analyze_cultural_data(
    request: CulturalAnalysisRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    cultural_engine: CulturalIntelligenceEngine = Depends(get_cultural_engine)
):
    """Analyze cultural patterns from social media data."""
    try:
        social_media_data = {}
        
        if request.include_social_media:
            # Get recent social media data
            data_points_result = await db.execute(
                select(CulturalDataPoint).where(
                    CulturalDataPoint.user_id == current_user.id
                ).order_by(CulturalDataPoint.created_at.desc()).limit(500)
            )
            data_points = data_points_result.scalars().all()
            
            for dp in data_points:
                if dp.platform:
                    if dp.platform.value not in social_media_data:
                        social_media_data[dp.platform.value] = {
                            "posts": [],
                            "interactions": [],
                            "content": []
                        }
                    social_media_data[dp.platform.value]["content"].append(dp.content)
        
        # Analyze patterns
        insight = await cultural_engine.analyze_cultural_patterns(
            user_id=str(current_user.id),
            social_media_data=social_media_data,
            analysis_depth=request.analysis_depth
        )
        
        # Cache response
        response.headers["Cache-Control"] = "public, max-age=86400"  # Cache for 24 hours
        
        return insight
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze cultural patterns: {str(e)}"
        )


@router.get("/recommendations")
async def get_recommendations(
    response: Response,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    cultural_engine: CulturalIntelligenceEngine = Depends(get_cultural_engine),
    limit: int = 10
):
    """Get personalized cultural recommendations."""
    try:
        # Get user's cultural profile
        profile_result = await db.execute(
            select(CulturalProfile).where(
                CulturalProfile.user_id == current_user.id
            ).order_by(CulturalProfile.updated_at.desc())
        )
        profile = profile_result.scalar_one_or_none()
        
        # Build user preferences from profile
        user_preferences = {}
        if profile:
            user_preferences = profile.evolution_data.get("preferences", {})
        
        # Generate recommendations
        recommendations = await cultural_engine.generate_cultural_recommendations(
            user_id=str(current_user.id),
            user_preferences=user_preferences,
            recommendation_count=limit
        )
        
        # Cache response
        response.headers["Cache-Control"] = "public, max-age=43200"  # Cache for 12 hours
        
        return recommendations
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


@router.post("/compatibility")
async def get_cultural_compatibility(
    request: CulturalCompatibilityRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    cultural_engine: CulturalIntelligenceEngine = Depends(get_cultural_engine)
):
    """Get cultural compatibility score between current user and target user."""
    try:
        # Get current user's profile
        current_profile_result = await db.execute(
            select(CulturalProfile).where(
                CulturalProfile.user_id == current_user.id
            ).order_by(CulturalProfile.updated_at.desc())
        )
        current_profile = current_profile_result.scalar_one_or_none()
        
        # Get target user's profile
        target_profile_result = await db.execute(
            select(CulturalProfile).where(
                CulturalProfile.user_id == request.target_user_id
            ).order_by(CulturalProfile.updated_at.desc())
        )
        target_profile = target_profile_result.scalar_one_or_none()
        
        if not current_profile or not target_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cultural profiles not found for one or both users"
            )
        
        # Calculate compatibility
        compatibility = await cultural_engine.get_cultural_compatibility(
            user_a_profile={
                "diversity_score": float(current_profile.diversity_score) if current_profile.diversity_score else 0,
                "evolution_data": current_profile.evolution_data,
                "influence_network": current_profile.influence_network
            },
            user_b_profile={
                "diversity_score": float(target_profile.diversity_score) if target_profile.diversity_score else 0,
                "evolution_data": target_profile.evolution_data,
                "influence_network": target_profile.influence_network
            }
        )
        
        # Cache response
        response.headers["Cache-Control"] = "public, max-age=3600"  # Cache for 1 hour
        
        return compatibility
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate compatibility: {str(e)}"
        )


@router.post("/challenges")
async def get_cultural_challenges(
    request: CulturalChallengeRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    cultural_engine: CulturalIntelligenceEngine = Depends(get_cultural_engine)
):
    """Get cultural challenges for the user."""
    try:
        # Get user's cultural profile
        profile_result = await db.execute(
            select(CulturalProfile).where(
                CulturalProfile.user_id == current_user.id
            ).order_by(CulturalProfile.updated_at.desc())
        )
        profile = profile_result.scalar_one_or_none()
        
        user_profile = {}
        if profile:
            user_profile = {
                "diversity_score": float(profile.diversity_score) if profile.diversity_score else 0,
                "blind_spots": profile.blind_spots,
                "evolution_data": profile.evolution_data
            }
        
        # Get challenges
        challenges = await cultural_engine.get_cultural_challenges(
            user_id=str(current_user.id),
            user_profile=user_profile
        )
        
        # Filter by difficulty if requested
        if request.difficulty:
            challenges = {
                k: v for k, v in challenges.items()
                if v.get("difficulty", "medium") == request.difficulty
            }
        
        # Filter by category if requested
        if request.category:
            challenges = {
                k: v for k, v in challenges.items()
                if v.get("category", "").lower() == request.category.lower()
            }
        
        # Cache response
        response.headers["Cache-Control"] = "public, max-age=86400"  # Cache for 24 hours
        
        return {
            "challenges": challenges,
            "total_challenges": len(challenges),
            "filters_applied": {
                "difficulty": request.difficulty,
                "category": request.category
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cultural challenges: {str(e)}"
        )


@router.get("/influence-network")
async def get_influence_network(
    response: Response,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    cultural_engine: CulturalIntelligenceEngine = Depends(get_cultural_engine)
):
    """Get user's cultural influence network."""
    try:
        # Get recent social media data
        data_points_result = await db.execute(
            select(CulturalDataPoint).where(
                CulturalDataPoint.user_id == current_user.id
            ).order_by(CulturalDataPoint.created_at.desc()).limit(500)
        )
        data_points = data_points_result.scalars().all()
        
        social_media_data = {}
        for dp in data_points:
            if dp.platform:
                if dp.platform.value not in social_media_data:
                    social_media_data[dp.platform.value] = []
                social_media_data[dp.platform.value].append(dp.content)
        
        # Get influence network
        network = await cultural_engine.get_influence_network(
            user_id=str(current_user.id),
            social_media_data=social_media_data
        )
        
        # Cache response
        response.headers["Cache-Control"] = "public, max-age=86400"  # Cache for 24 hours
        
        return network
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get influence network: {str(e)}"
        )


@router.post("/benchmark")
async def get_anonymous_benchmark(
    request: BenchmarkRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    cultural_engine: CulturalIntelligenceEngine = Depends(get_cultural_engine)
):
    """Get anonymous benchmark against specified demographics."""
    try:
        # Get user's cultural profile
        profile_result = await db.execute(
            select(CulturalProfile).where(
                CulturalProfile.user_id == current_user.id
            ).order_by(CulturalProfile.updated_at.desc())
        )
        profile = profile_result.scalar_one_or_none()
        
        user_profile = {}
        if profile:
            user_profile = {
                "diversity_score": float(profile.diversity_score) if profile.diversity_score else 0,
                "evolution_data": profile.evolution_data,
                "influence_network": profile.influence_network
            }
        
        # Get benchmark
        benchmark = await cultural_engine.get_anonymous_benchmark(
            user_profile=user_profile,
            demographics=request.demographics
        )
        
        # Cache response
        response.headers["Cache-Control"] = "public, max-age=86400"  # Cache for 24 hours
        
        return {
            "benchmark": benchmark,
            "demographics_compared": request.demographics,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get benchmark: {str(e)}"
        )


@router.get("/evolution")
async def get_cultural_evolution(
    response: Response,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    cultural_engine: CulturalIntelligenceEngine = Depends(get_cultural_engine),
    time_range: str = "365d"
):
    """Get user's cultural evolution timeline."""
    try:
        # Get user's historical data
        data_points_result = await db.execute(
            select(CulturalDataPoint).where(
                CulturalDataPoint.user_id == current_user.id
            ).order_by(CulturalDataPoint.created_at.asc())
        )
        data_points = data_points_result.scalars().all()
        
        # Convert to history format
        user_history = []
        for dp in data_points:
            user_history.append({
                "date": dp.created_at.isoformat(),
                "platform": dp.platform.value if dp.platform else "unknown",
                "type": dp.data_type.value if dp.data_type else "unknown",
                "data": dp.content,
                "confidence": float(dp.confidence_score) if dp.confidence_score else 0.0
            })
        
        # Get evolution timeline
        evolution = await cultural_engine.get_cultural_evolution_timeline(
            user_id=str(current_user.id),
            user_history=user_history
        )
        
        # Cache response
        response.headers["Cache-Control"] = "public, max-age=86400"  # Cache for 24 hours
        
        return evolution
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cultural evolution: {str(e)}"
        )