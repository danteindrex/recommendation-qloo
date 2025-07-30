"""
Mock Cultural Intelligence API with realistic data simulation.
This provides working endpoints while Qloo integration is being finalized.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from app.services.gemini_service import gemini_service
import random
from datetime import datetime, timedelta
import json
import asyncio

router = APIRouter()

# Mock user data with realistic cultural profiles
MOCK_USERS = {
    "1": {
        "id": "1",
        "name": "Alex Chen",
        "email": "alex.chen@example.com",
        "location": "San Francisco, CA",
        "age": 28,
        "joinDate": "2024-01-15",
        "status": "active",
        "cultural_profile": {
            "music_preferences": ["indie rock", "electronic", "k-pop", "jazz"],
            "content_languages": ["english", "korean", "mandarin"],
            "geographic_interests": ["asia", "north_america", "europe"],
            "activity_patterns": {
                "spotify": {"daily_hours": 4.2, "genres_explored": 23, "new_artists_monthly": 12},
                "instagram": {"posts_per_week": 3, "story_engagement": 0.85, "cultural_hashtags": 45},
                "tiktok": {"videos_watched_daily": 45, "creators_followed": 234, "cultural_content_ratio": 0.67}
            }
        }
    },
    "2": {
        "id": "2",
        "name": "Maria Rodriguez",
        "email": "maria.rodriguez@example.com",
        "location": "Mexico City, MX",
        "age": 24,
        "joinDate": "2024-02-03",
        "status": "active",
        "cultural_profile": {
            "music_preferences": ["reggaeton", "pop latino", "indie", "electronic"],
            "content_languages": ["spanish", "english", "portuguese"],
            "geographic_interests": ["latin_america", "north_america", "spain"],
            "activity_patterns": {
                "spotify": {"daily_hours": 5.1, "genres_explored": 18, "new_artists_monthly": 15},
                "instagram": {"posts_per_week": 5, "story_engagement": 0.92, "cultural_hashtags": 67},
                "tiktok": {"videos_watched_daily": 62, "creators_followed": 189, "cultural_content_ratio": 0.73}
            }
        }
    },
    "3": {
        "id": "3",
        "name": "Kenji Tanaka",
        "email": "kenji.tanaka@example.com",
        "location": "Tokyo, JP",
        "age": 31,
        "joinDate": "2024-01-28",
        "status": "active",
        "cultural_profile": {
            "music_preferences": ["j-pop", "city pop", "electronic", "ambient"],
            "content_languages": ["japanese", "english"],
            "geographic_interests": ["asia", "north_america"],
            "activity_patterns": {
                "spotify": {"daily_hours": 3.8, "genres_explored": 15, "new_artists_monthly": 8},
                "instagram": {"posts_per_week": 2, "story_engagement": 0.71, "cultural_hashtags": 32},
                "tiktok": {"videos_watched_daily": 28, "creators_followed": 156, "cultural_content_ratio": 0.54}
            }
        }
    },
    "4": {
        "id": "4",
        "name": "Emma Thompson",
        "email": "emma.thompson@example.com",
        "location": "London, UK",
        "age": 26,
        "joinDate": "2024-03-10",
        "status": "active",
        "cultural_profile": {
            "music_preferences": ["indie", "brit-pop", "electronic", "world music"],
            "content_languages": ["english", "french", "spanish"],
            "geographic_interests": ["europe", "africa", "south_america"],
            "activity_patterns": {
                "spotify": {"daily_hours": 4.5, "genres_explored": 28, "new_artists_monthly": 18},
                "instagram": {"posts_per_week": 4, "story_engagement": 0.88, "cultural_hashtags": 52},
                "tiktok": {"videos_watched_daily": 35, "creators_followed": 201, "cultural_content_ratio": 0.81}
            }
        }
    }
}

class PlatformData(BaseModel):
    connected: bool
    tracks: Optional[int] = None
    genres: Optional[int] = None
    daily_hours: Optional[float] = None
    new_artists_monthly: Optional[int] = None
    posts: Optional[int] = None
    engagement: Optional[float] = None
    cultural_hashtags: Optional[int] = None
    posts_per_week: Optional[int] = None
    videos: Optional[int] = None
    views: Optional[int] = None
    creators_followed: Optional[int] = None
    cultural_content_ratio: Optional[float] = None

class TrendPrediction(BaseModel):
    nextTrend: str
    probability: int
    timeframe: str
    category: str
    reasoning: str
    ai_explanation: Optional[str] = None

class CulturalInsight(BaseModel):
    category: str
    finding: str
    confidence: int
    impact: str
    recommendation: str
    ai_explanation: Optional[str] = None

class QlooCorrelation(BaseModel):
    source_entity: str
    target_entity: str
    correlation_strength: float
    correlation_type: str
    cultural_context: str

class CulturalRecommendation(BaseModel):
    category: str
    title: str
    description: str
    examples: Optional[List[str]] = None
    confidence: float
    cultural_impact: int
    ai_explanation: Optional[str] = None

class TodoRecommendation(BaseModel):
    category: str
    priority: str
    title: str
    description: str
    estimated_time: str
    cultural_impact: int
    specific_actions: List[str]
    due_date: str
    reasoning: str
    ai_explanation: Optional[str] = None

class CulturalAnalysisResponse(BaseModel):
    user_id: str
    cultural_score: int
    diversity_index: int
    platforms: Dict[str, PlatformData]
    predictions: List[TrendPrediction]
    insights: List[CulturalInsight]
    qloo_correlations: List[QlooCorrelation]
    trend_analysis: Dict[str, Any]
    recommendations: List[CulturalRecommendation]

class TodoAnalysisResponse(BaseModel):
    user_id: str
    analysis_type: str
    total_recommendations: int
    todos: List[TodoRecommendation]
    analysis_metadata: Dict[str, Any]

class ListeningHistoryResponse(BaseModel):
    user_id: str
    total_songs: int
    period_days: int
    listening_history: List[Dict[str, Any]]
    analysis_summary: Dict[str, Any]

def calculate_cultural_score(profile: Dict[str, Any]) -> int:
    """Calculate cultural score based on user profile."""
    base_score = 60
    
    # Music diversity bonus
    music_bonus = min(len(profile["music_preferences"]) * 5, 20)
    
    # Language diversity bonus
    language_bonus = min(len(profile["content_languages"]) * 8, 25)
    
    # Geographic interest bonus
    geo_bonus = min(len(profile["geographic_interests"]) * 6, 18)
    
    # Activity engagement bonus
    activity_patterns = profile["activity_patterns"]
    engagement_score = 0
    for platform, data in activity_patterns.items():
        if platform == "spotify":
            engagement_score += min(data["genres_explored"], 15)
        elif platform == "instagram":
            engagement_score += min(data["cultural_hashtags"] / 2, 15)
        elif platform == "tiktok":
            engagement_score += min(data["cultural_content_ratio"] * 20, 15)
    
    total_score = base_score + music_bonus + language_bonus + geo_bonus + min(engagement_score, 30)
    return min(int(total_score), 100)

def calculate_diversity_index(profile: Dict[str, Any]) -> int:
    """Calculate diversity index based on cultural exposure."""
    diversity_factors = [
        len(profile["music_preferences"]) * 4,
        len(profile["content_languages"]) * 12,
        len(profile["geographic_interests"]) * 8,
        profile["activity_patterns"]["tiktok"]["cultural_content_ratio"] * 25
    ]
    
    base_diversity = sum(diversity_factors)
    return min(int(base_diversity), 100)

async def generate_predictions(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate realistic trend predictions with AI explanations."""
    music_prefs = profile["music_preferences"]
    
    predictions = []
    
    # Music-based predictions
    if "k-pop" in music_prefs:
        base_prediction = {
            "nextTrend": "K-Pop x Latin Collaborations",
            "probability": random.randint(75, 90),
            "timeframe": "2-3 weeks",
            "category": "music",
            "reasoning": "Strong K-Pop engagement correlates with Latin fusion trends"
        }
        
        try:
            ai_explanation = await gemini_service.generate_trend_prediction_explanation(base_prediction, profile)
            base_prediction["ai_explanation"] = ai_explanation
        except Exception as e:
            base_prediction["ai_explanation"] = "Your K-Pop interest aligns perfectly with the emerging Latin collaboration trend, offering exciting cross-cultural musical discoveries."
        
        predictions.append(base_prediction)
    
    if "electronic" in music_prefs:
        base_prediction = {
            "nextTrend": "Afrobeats Electronic Fusion",
            "probability": random.randint(70, 85),
            "timeframe": "1 month",
            "category": "music",
            "reasoning": "Electronic listeners show high adoption of Afrobeats hybrid genres"
        }
        
        try:
            ai_explanation = await gemini_service.generate_trend_prediction_explanation(base_prediction, profile)
            base_prediction["ai_explanation"] = ai_explanation
        except Exception as e:
            base_prediction["ai_explanation"] = "Electronic music fans like you are driving the Afrobeats fusion movement, creating innovative soundscapes that blend cultures."
        
        predictions.append(base_prediction)
    
    if "indie" in music_prefs:
        base_prediction = {
            "nextTrend": "Bedroom Pop Revival",
            "probability": random.randint(65, 80),
            "timeframe": "6-8 weeks",
            "category": "music",
            "reasoning": "Indie preference patterns indicate nostalgic genre cycles"
        }
        
        try:
            ai_explanation = await gemini_service.generate_trend_prediction_explanation(base_prediction, profile)
            base_prediction["ai_explanation"] = ai_explanation
        except Exception as e:
            base_prediction["ai_explanation"] = "Your indie sensibilities position you to appreciate the upcoming bedroom pop revival's nostalgic yet innovative approach."
        
        predictions.append(base_prediction)
    
    # Content predictions based on languages
    if "spanish" in profile["content_languages"]:
        base_prediction = {
            "nextTrend": "Spanish-Language Podcasts",
            "probability": random.randint(80, 95),
            "timeframe": "2 weeks",
            "category": "content",
            "reasoning": "Bilingual users drive cross-cultural content consumption"
        }
        
        try:
            ai_explanation = await gemini_service.generate_trend_prediction_explanation(base_prediction, profile)
            base_prediction["ai_explanation"] = ai_explanation
        except Exception as e:
            base_prediction["ai_explanation"] = "Your bilingual abilities make you an ideal early adopter of the exploding Spanish podcast ecosystem."
        
        predictions.append(base_prediction)
    
    # Geographic predictions
    if "asia" in profile["geographic_interests"]:
        base_prediction = {
            "nextTrend": "Asian Streetwear Aesthetics",
            "probability": random.randint(70, 88),
            "timeframe": "3-4 weeks",
            "category": "fashion",
            "reasoning": "Asian cultural interest correlates with fashion trend adoption"
        }
        
        try:
            ai_explanation = await gemini_service.generate_trend_prediction_explanation(base_prediction, profile)
            base_prediction["ai_explanation"] = ai_explanation
        except Exception as e:
            base_prediction["ai_explanation"] = "Your interest in Asian culture aligns with the rising streetwear aesthetic that's reshaping global fashion."
        
        predictions.append(base_prediction)
    
    return predictions[:3]  # Return top 3 predictions

async def generate_insights(profile: Dict[str, Any], cultural_score: int) -> List[Dict[str, Any]]:
    """Generate AI-powered cultural insights with explanations."""
    insights = []
    
    # Music evolution insight
    if len(profile["music_preferences"]) > 3:
        base_insight = {
            "category": "Music Evolution",
            "finding": f"Your taste spans {len(profile['music_preferences'])} genres, indicating high musical curiosity and openness to cultural exploration",
            "confidence": random.randint(85, 95),
            "impact": "positive",
            "recommendation": "Continue exploring fusion genres to maximize cultural discovery"
        }
        
        try:
            user_context = {"cultural_score": cultural_score, "diversity_index": random.randint(80, 95)}
            ai_explanation = await gemini_service.generate_cultural_insight_explanation(base_insight, user_context)
            base_insight["ai_explanation"] = ai_explanation
        except Exception as e:
            base_insight["ai_explanation"] = "Your diverse musical preferences demonstrate exceptional cultural curiosity, making you well-positioned for discovering emerging fusion genres and cross-cultural musical innovations."
        
        insights.append(base_insight)
    
    # Language diversity insight
    if len(profile["content_languages"]) > 2:
        base_insight = {
            "category": "Cultural Bridge",
            "finding": f"Multilingual content consumption ({', '.join(profile['content_languages'])}) positions you as a cultural connector",
            "confidence": random.randint(80, 92),
            "impact": "positive",
            "recommendation": "Leverage language skills to discover niche cultural content"
        }
        
        try:
            user_context = {"cultural_score": cultural_score, "diversity_index": random.randint(85, 98)}
            ai_explanation = await gemini_service.generate_cultural_insight_explanation(base_insight, user_context)
            base_insight["ai_explanation"] = ai_explanation
        except Exception as e:
            base_insight["ai_explanation"] = "Your multilingual abilities create unique opportunities to bridge different cultural communities and discover content that monolingual users miss."
        
        insights.append(base_insight)
    
    # Activity pattern insight
    tiktok_ratio = profile["activity_patterns"]["tiktok"]["cultural_content_ratio"]
    if tiktok_ratio > 0.7:
        base_insight = {
            "category": "Trend Sensitivity",
            "finding": f"High cultural content ratio ({tiktok_ratio:.0%}) suggests strong trend prediction abilities",
            "confidence": random.randint(88, 96),
            "impact": "positive",
            "recommendation": "Consider content creation to influence cultural trends"
        }
        
        try:
            user_context = {"cultural_score": cultural_score, "diversity_index": random.randint(90, 98)}
            ai_explanation = await gemini_service.generate_cultural_insight_explanation(base_insight, user_context)
            base_insight["ai_explanation"] = ai_explanation
        except Exception as e:
            base_insight["ai_explanation"] = "Your high engagement with cultural content positions you as an early trend detector who could influence others' cultural discoveries."
        
        insights.append(base_insight)
    elif tiktok_ratio < 0.5:
        base_insight = {
            "category": "Cultural Expansion Opportunity",
            "finding": f"Cultural content ratio ({tiktok_ratio:.0%}) indicates potential for broader cultural engagement",
            "confidence": random.randint(75, 87),
            "impact": "neutral", 
            "recommendation": "Gradually increase exposure to diverse cultural creators"
        }
        
        try:
            user_context = {"cultural_score": cultural_score, "diversity_index": random.randint(70, 85)}
            ai_explanation = await gemini_service.generate_cultural_insight_explanation(base_insight, user_context)
            base_insight["ai_explanation"] = ai_explanation
        except Exception as e:
            base_insight["ai_explanation"] = "Increasing your cultural content consumption could unlock new perspectives and significantly boost your cultural intelligence score."
        
        insights.append(base_insight)
    
    return insights

def generate_qloo_correlations(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate mock Qloo-style correlations."""
    correlations = []
    
    music_prefs = profile["music_preferences"]
    
    # Generate realistic correlations based on music preferences
    correlation_map = {
        "k-pop": [
            {"entity": "BTS", "correlation": 0.89, "type": "genre_affinity"},
            {"entity": "Korean Beauty Products", "correlation": 0.76, "type": "cultural_crossover"},
            {"entity": "Anime", "correlation": 0.68, "type": "cultural_cluster"}
        ],
        "electronic": [
            {"entity": "Techno Festivals", "correlation": 0.84, "type": "lifestyle_alignment"},
            {"entity": "Digital Art", "correlation": 0.72, "type": "aesthetic_preference"},
            {"entity": "Gaming Culture", "correlation": 0.65, "type": "demographic_overlap"}
        ],
        "indie": [
            {"entity": "Vinyl Records", "correlation": 0.81, "type": "consumption_pattern"},
            {"entity": "Independent Films", "correlation": 0.77, "type": "taste_correlation"},
            {"entity": "Craft Coffee", "correlation": 0.63, "type": "lifestyle_indicator"}
        ],
        "reggaeton": [
            {"entity": "Latin Dance", "correlation": 0.86, "type": "cultural_activity"},
            {"entity": "Spanish TV Shows", "correlation": 0.74, "type": "language_correlation"},
            {"entity": "Caribbean Cuisine", "correlation": 0.69, "type": "cultural_immersion"}
        ]
    }
    
    for genre in music_prefs:
        if genre in correlation_map:
            for corr in correlation_map[genre][:2]:  # Top 2 correlations per genre
                correlations.append({
                    "source_entity": genre.title(),
                    "target_entity": corr["entity"],
                    "correlation_strength": corr["correlation"],
                    "correlation_type": corr["type"],
                    "cultural_context": f"Users with {genre} preferences show {corr['correlation']:.0%} correlation with {corr['entity']}"
                })
    
    return correlations[:5]  # Return top 5 correlations

async def generate_recommendations(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate personalized cultural recommendations with AI explanations."""
    recommendations = []
    
    music_prefs = profile["music_preferences"]
    languages = profile["content_languages"]
    
    # Music recommendations
    if "k-pop" in music_prefs and "electronic" in music_prefs:
        base_rec = {
            "category": "Music Discovery",
            "title": "K-Electronic Fusion Artists",
            "description": "Explore artists blending K-Pop with electronic elements",
            "examples": ["LOONA/Odd Eye Circle", "f(x)", "Red Velvet - Perfect Velvet"],
            "confidence": 0.87,
            "cultural_impact": 85
        }
        
        # Generate AI explanation
        try:
            ai_explanation = await gemini_service.generate_recommendation_explanation(
                profile, base_rec, "k_electronic_fusion"
            )
            base_rec["ai_explanation"] = ai_explanation
        except Exception as e:
            base_rec["ai_explanation"] = "Bridges Eastern and Western electronic music scenes through innovative fusion"
        
        recommendations.append(base_rec)
    
    if "spanish" in languages:
        base_rec = {
            "category": "Content Expansion", 
            "title": "Latin American Indie Films",
            "description": "Discover critically acclaimed films from Latin America",
            "examples": ["Roma", "The Platform", "Wild Tales"],
            "confidence": 0.82,
            "cultural_impact": 78
        }
        
        try:
            ai_explanation = await gemini_service.generate_recommendation_explanation(
                profile, base_rec, "latin_cinema"
            )
            base_rec["ai_explanation"] = ai_explanation
        except Exception as e:
            base_rec["ai_explanation"] = "Deepens understanding of Latin American perspectives through powerful storytelling"
        
        recommendations.append(base_rec)
    
    # Geographic-based recommendations
    if "asia" in profile["geographic_interests"]:
        base_rec = {
            "category": "Cultural Immersion",
            "title": "Asian Street Food Culture", 
            "description": "Explore authentic street food traditions across Asia",
            "examples": ["Korean Night Markets", "Japanese Ramen Culture", "Thai Street Food"],
            "confidence": 0.79,
            "cultural_impact": 82
        }
        
        try:
            ai_explanation = await gemini_service.generate_recommendation_explanation(
                profile, base_rec, "asian_cuisine"
            )
            base_rec["ai_explanation"] = ai_explanation
        except Exception as e:
            base_rec["ai_explanation"] = "Authentic cultural experience through the rich traditions of Asian street food"
        
        recommendations.append(base_rec)
    
    return recommendations

@router.get("/users", response_model=List[Dict[str, Any]])
async def get_users():
    """
    Get list of available users for cultural intelligence analysis.
    
    Returns a list of user profiles that can be analyzed for cultural intelligence insights.
    Each user has different musical preferences, languages, and geographic interests to 
    demonstrate the variety of cultural profiles the system can analyze.
    
    Returns:
        List of user objects with basic profile information
    """
    return [
        {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "location": user["location"],
            "joinDate": user["joinDate"],
            "status": user["status"]
        }
        for user in MOCK_USERS.values()
    ]

@router.get("/analyze/{user_id}", response_model=CulturalAnalysisResponse)
async def analyze_user_culture(user_id: str):
    """
    Perform comprehensive cultural intelligence analysis for a specific user.
    
    This endpoint analyzes a user's cultural profile and generates:
    - Cultural intelligence score and diversity index
    - Platform-specific engagement metrics (Spotify, Instagram, TikTok)
    - AI-powered trend predictions with personalized explanations
    - Cultural insights with confidence scores and AI explanations
    - Qloo-style entity correlations for cultural discovery
    - Personalized recommendations with AI-generated explanations
    
    Args:
        user_id: The unique identifier for the user to analyze
        
    Returns:
        Comprehensive cultural analysis including scores, predictions, insights, and recommendations
        
    Raises:
        HTTPException: 404 if user not found
    """
    if user_id not in MOCK_USERS:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = MOCK_USERS[user_id]
    profile = user["cultural_profile"]
    
    # Calculate scores
    cultural_score = calculate_cultural_score(profile)
    diversity_index = calculate_diversity_index(profile)
    
    # Generate platform data
    platforms = {
        "spotify": {
            "connected": True,
            "tracks": int(profile["activity_patterns"]["spotify"]["daily_hours"] * 365 * 2),
            "genres": profile["activity_patterns"]["spotify"]["genres_explored"],
            "daily_hours": profile["activity_patterns"]["spotify"]["daily_hours"],
            "new_artists_monthly": profile["activity_patterns"]["spotify"]["new_artists_monthly"]
        },
        "instagram": {
            "connected": True,
            "posts": int(profile["activity_patterns"]["instagram"]["posts_per_week"] * 52),
            "engagement": profile["activity_patterns"]["instagram"]["story_engagement"] * 100,
            "cultural_hashtags": profile["activity_patterns"]["instagram"]["cultural_hashtags"],
            "posts_per_week": profile["activity_patterns"]["instagram"]["posts_per_week"]
        },
        "tiktok": {
            "connected": user_id != "3",  # Kenji has TikTok disconnected
            "videos": int(profile["activity_patterns"]["tiktok"]["videos_watched_daily"] * 365) if user_id != "3" else 0,
            "views": int(profile["activity_patterns"]["tiktok"]["videos_watched_daily"] * 365 * 1000) if user_id != "3" else 0,
            "creators_followed": profile["activity_patterns"]["tiktok"]["creators_followed"] if user_id != "3" else 0,
            "cultural_content_ratio": profile["activity_patterns"]["tiktok"]["cultural_content_ratio"] if user_id != "3" else 0
        }
    }
    
    # Generate analysis components
    predictions = await generate_predictions(profile)
    insights = await generate_insights(profile, cultural_score)
    correlations = generate_qloo_correlations(profile)  # This remains sync
    recommendations = await generate_recommendations(profile)
    
    # Trend analysis
    trend_analysis = {
        "rising_trends": [
            {"name": "Cross-Cultural Collaborations", "strength": 0.89, "timeframe": "3 months"},
            {"name": "Multilingual Content", "strength": 0.76, "timeframe": "2 months"},
            {"name": "Fusion Genres", "strength": 0.82, "timeframe": "6 weeks"}
        ],
        "user_alignment": {
            "trend_sensitivity": cultural_score / 100,
            "early_adopter_score": diversity_index / 100,
            "influence_potential": (cultural_score + diversity_index) / 200
        }
    }
    
    return CulturalAnalysisResponse(
        user_id=user_id,
        cultural_score=cultural_score,
        diversity_index=diversity_index,
        platforms=platforms,
        predictions=predictions,
        insights=insights,
        qloo_correlations=correlations,
        trend_analysis=trend_analysis,
        recommendations=recommendations
    )

@router.get("/trends/global", response_model=Dict[str, Any])
async def get_global_trends():
    """Get global cultural trends."""
    return {
        "trending_now": [
            {"name": "Afrobeats Global Expansion", "growth_rate": 0.34, "regions": ["North America", "Europe", "Asia"]},
            {"name": "K-Pop x Latin Fusion", "growth_rate": 0.28, "regions": ["Americas", "Asia"]},
            {"name": "Sustainable Fashion", "growth_rate": 0.42, "regions": ["Global"]},
            {"name": "Multilingual Podcasts", "growth_rate": 0.31, "regions": ["North America", "Europe"]}
        ],
        "emerging_trends": [
            {"name": "AI-Generated Music", "probability": 0.76, "timeframe": "6 months"},
            {"name": "Virtual Cultural Experiences", "probability": 0.68, "timeframe": "4 months"},
            {"name": "Micro-Regional Cuisines", "probability": 0.71, "timeframe": "8 months"}
        ],
        "cultural_shifts": {
            "digital_native_preferences": 0.89,
            "cross_cultural_adoption_rate": 0.73,
            "traditional_media_decline": 0.45
        }
    }

@router.get("/listening-history/{user_id}", response_model=ListeningHistoryResponse)
async def get_listening_history(user_id: str, days: int = 30):
    """
    Retrieve user's music listening history for cultural analysis.
    
    Generates realistic listening history based on the user's cultural profile,
    including songs, genres, and cultural markers. This data is used for 
    todo generation and cultural pattern analysis.
    
    Args:
        user_id: The unique identifier for the user
        days: Number of days of listening history to generate (default: 30)
        
    Returns:
        Listening history with analysis summary including top genres,
        listening patterns, and cultural indicators
        
    Raises:
        HTTPException: 404 if user not found
    """
    if user_id not in MOCK_USERS:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = MOCK_USERS[user_id]
    profile = user["cultural_profile"]
    
    # Generate realistic listening history based on user preferences
    listening_history = []
    music_prefs = profile["music_preferences"]
    
    # Generate songs for each day
    for day in range(days):
        date = datetime.now() - timedelta(days=day)
        daily_songs = []
        
        # Generate 20-40 songs per day based on user activity
        daily_hours = profile["activity_patterns"]["spotify"]["daily_hours"]
        songs_per_day = int(daily_hours * 12)  # ~3 min per song
        
        for _ in range(songs_per_day):
            genre = random.choice(music_prefs)
            song_data = generate_song_by_genre(genre, date)
            daily_songs.append(song_data)
        
        listening_history.extend(daily_songs)
    
    return {
        "user_id": user_id,
        "total_songs": len(listening_history),
        "period_days": days,
        "listening_history": listening_history[:100],  # Return last 100 for performance
        "analysis_summary": {
            "top_genres": get_top_genres_from_history(listening_history),
            "listening_patterns": analyze_listening_patterns(listening_history),
            "cultural_indicators": extract_cultural_indicators(listening_history)
        }
    }

@router.post("/todo-analysis/{user_id}", response_model=TodoAnalysisResponse)
async def analyze_todos_from_music(user_id: str, analysis_depth: str = "standard"):
    """
    Generate personalized cultural todo recommendations based on music listening history.
    
    This endpoint analyzes the user's listening patterns and generates actionable cultural
    discovery tasks. Each todo includes AI-generated explanations from Google Gemini that
    explain why the recommendation is relevant and culturally beneficial.
    
    Todo categories include:
    - Music Discovery: Explore underrepresented genres from user preferences
    - Cultural Immersion: Discover music in user's secondary languages  
    - Trend Adoption: Get ahead of predicted cultural trends
    - Cultural Sharing: Document and share musical cultural journey
    
    Args:
        user_id: The unique identifier for the user
        analysis_depth: Depth of analysis ("standard" or "comprehensive")
        
    Returns:
        Personalized todo recommendations with AI explanations, cultural impact scores,
        specific actions, timelines, and metadata about the analysis
        
    Raises:
        HTTPException: 404 if user not found
    """
    if user_id not in MOCK_USERS:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = MOCK_USERS[user_id]
    profile = user["cultural_profile"]
    
    # Get listening history first
    history_response = await get_listening_history(user_id, 30)
    listening_history = history_response["listening_history"]
    
    # Analyze music patterns for todo generation
    todo_recommendations = []
    
    # Music exploration todos
    top_genres = history_response["analysis_summary"]["top_genres"]
    underexplored_genres = find_underexplored_genres(profile["music_preferences"], top_genres)
    
    for genre in underexplored_genres[:3]:
        base_todo = {
            "category": "Music Discovery",
            "priority": "medium",
            "title": f"Explore {genre.title()} Music",
            "description": f"Discover new artists and tracks in {genre} based on your cultural profile",
            "estimated_time": "30 minutes",
            "cultural_impact": calculate_cultural_impact(genre, profile),
            "specific_actions": [
                f"Listen to 3 new {genre} artists",
                f"Create a {genre} playlist",
                f"Read about {genre} cultural origins"
            ],
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "reasoning": f"Your listening history shows limited exposure to {genre}, which could enhance your cultural diversity score"
        }
        
        # Generate AI explanation for the todo
        try:
            ai_explanation = await gemini_service.generate_recommendation_explanation(
                profile, base_todo, f"{genre}_exploration"
            )
            base_todo["ai_explanation"] = ai_explanation
        except Exception as e:
            base_todo["ai_explanation"] = f"Exploring {genre} will complement your existing preferences and open new cultural pathways for discovery."
        
        todo_recommendations.append(base_todo)
    
    # Cultural immersion todos
    languages = profile["content_languages"]
    for lang in languages[:2]:
        if lang != "english":
            todo_recommendations.append({
                "category": "Cultural Immersion",
                "priority": "high",
                "title": f"Discover {lang.title()} Music Artists",
                "description": f"Explore contemporary and traditional music from {lang}-speaking regions",
                "estimated_time": "45 minutes",
                "cultural_impact": 85,
                "specific_actions": [
                    f"Find 5 trending {lang} artists",
                    f"Learn about {lang} music history",
                    f"Add {lang} songs to daily rotation"
                ],
                "due_date": (datetime.now() + timedelta(days=5)).isoformat(),
                "reasoning": f"Your multilingual profile suggests high cultural adaptability - leverage this for deeper music exploration"
            })
    
    # Trend prediction todos
    predictions = generate_predictions(profile)
    for prediction in predictions[:2]:
        if prediction["category"] == "music":
            todo_recommendations.append({
                "category": "Trend Adoption",
                "priority": "low",
                "title": f"Explore {prediction['nextTrend']}",
                "description": f"Get ahead of the trend: {prediction['nextTrend']}",
                "estimated_time": "25 minutes",
                "cultural_impact": prediction["probability"],
                "specific_actions": [
                    f"Research {prediction['nextTrend']} artists",
                    f"Follow relevant playlists",
                    f"Share discoveries with friends"
                ],
                "due_date": (datetime.now() + timedelta(weeks=2)).isoformat(),
                "reasoning": prediction["reasoning"]
            })
    
    # Social sharing todos based on listening patterns
    if profile["activity_patterns"]["instagram"]["posts_per_week"] > 2:
        todo_recommendations.append({
            "category": "Cultural Sharing",
            "priority": "medium",
            "title": "Share Musical Cultural Journey",
            "description": "Document and share your musical discoveries to influence your network",
            "estimated_time": "20 minutes",
            "cultural_impact": 70,
            "specific_actions": [
                "Create Instagram story with new discovery",
                "Write about cultural significance",
                "Use relevant cultural hashtags"
            ],
            "due_date": (datetime.now() + timedelta(days=3)).isoformat(),
            "reasoning": "Your high social engagement suggests you could influence others' cultural exploration"
        })
    
    return {
        "user_id": user_id,
        "analysis_type": "music_based_todos",
        "total_recommendations": len(todo_recommendations),
        "todos": todo_recommendations,
        "analysis_metadata": {
            "based_on_days": 30,
            "listening_patterns_analyzed": len(listening_history),
            "cultural_score_impact": calculate_todo_impact_on_score(todo_recommendations),
            "estimated_total_time": sum(int(todo.get("estimated_time", "30").split()[0]) for todo in todo_recommendations),
            "generated_at": datetime.now().isoformat()
        }
    }

def generate_song_by_genre(genre: str, date: datetime) -> Dict[str, Any]:
    """Generate a realistic song entry for a given genre."""
    song_database = {
        "k-pop": [
            {"title": "Dynamite", "artist": "BTS", "album": "BE"},
            {"title": "How You Like That", "artist": "BLACKPINK", "album": "THE ALBUM"},
            {"title": "Next Level", "artist": "aespa", "album": "Savage"},
        ],
        "electronic": [
            {"title": "Strobe", "artist": "Deadmau5", "album": "For Lack of a Better Name"},
            {"title": "Language", "artist": "Porter Robinson", "album": "Worlds"},
            {"title": "Clarity", "artist": "Zedd", "album": "Clarity"},
        ],
        "indie": [
            {"title": "Electric Feel", "artist": "MGMT", "album": "Oracular Spectacular"},
            {"title": "Two Weeks", "artist": "FKA twigs", "album": "LP1"},
            {"title": "Holocene", "artist": "Bon Iver", "album": "Bon Iver, Bon Iver"},
        ],
        "reggaeton": [
            {"title": "Dákiti", "artist": "Bad Bunny", "album": "El Último Tour Del Mundo"},
            {"title": "Con Altura", "artist": "Rosalía", "album": "Single"},
            {"title": "La Botella", "artist": "Ozuna", "album": "Nibiru"},
        ]
    }
    
    songs = song_database.get(genre, song_database["indie"])
    song = random.choice(songs)
    
    return {
        "title": song["title"],
        "artist": song["artist"],
        "album": song["album"],
        "genre": genre,
        "played_at": date.isoformat(),
        "duration_ms": random.randint(180000, 300000),  # 3-5 minutes
        "cultural_markers": extract_cultural_markers(genre, song["artist"])
    }

def extract_cultural_markers(genre: str, artist: str) -> List[str]:
    """Extract cultural markers from genre and artist."""
    markers = []
    
    if genre == "k-pop":
        markers.extend(["korean", "asian", "pop", "global"])
    elif genre == "reggaeton":
        markers.extend(["latin", "urban", "caribbean", "spanish"])
    elif genre == "electronic":
        markers.extend(["digital", "synthetic", "club", "dance"])
    elif genre == "indie":
        markers.extend(["alternative", "independent", "artistic", "niche"])
    
    return markers

def get_top_genres_from_history(history: List[Dict]) -> List[Dict[str, Any]]:
    """Analyze top genres from listening history."""
    genre_counts = {}
    for song in history:
        genre = song.get("genre", "unknown")
        genre_counts[genre] = genre_counts.get(genre, 0) + 1
    
    return [{"genre": genre, "count": count, "percentage": count/len(history)*100} 
            for genre, count in sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)]

def analyze_listening_patterns(history: List[Dict]) -> Dict[str, Any]:
    """Analyze listening patterns from history."""
    return {
        "peak_listening_hours": ["19:00-21:00", "22:00-24:00"],
        "average_session_length": random.randint(45, 120),
        "skip_rate": random.uniform(0.15, 0.35),
        "repeat_rate": random.uniform(0.25, 0.45)
    }

def extract_cultural_indicators(history: List[Dict]) -> Dict[str, Any]:
    """Extract cultural indicators from listening history."""
    markers = []
    for song in history:
        markers.extend(song.get("cultural_markers", []))
    
    marker_counts = {}
    for marker in markers:
        marker_counts[marker] = marker_counts.get(marker, 0) + 1
    
    return {
        "dominant_cultures": list(marker_counts.keys())[:5],
        "cultural_diversity_score": len(set(markers)) * 10,
        "cross_cultural_exposure": random.uniform(0.6, 0.9)
    }

def find_underexplored_genres(preferences: List[str], top_genres: List[Dict]) -> List[str]:
    """Find genres that are underexplored based on preferences vs actual listening."""
    listened_genres = {g["genre"] for g in top_genres[:3]}
    return [genre for genre in preferences if genre not in listened_genres]

def calculate_cultural_impact(genre: str, profile: Dict) -> int:
    """Calculate potential cultural impact of exploring a genre."""
    base_impact = 60
    
    # Higher impact for genres that align with user's geographic interests
    if genre == "k-pop" and "asia" in profile.get("geographic_interests", []):
        base_impact += 20
    elif genre == "reggaeton" and "latin_america" in profile.get("geographic_interests", []):
        base_impact += 20
    
    # Language bonus
    if genre in ["reggaeton"] and "spanish" in profile.get("content_languages", []):
        base_impact += 15
    
    return min(base_impact, 95)

def calculate_todo_impact_on_score(todos: List[Dict]) -> int:
    """Calculate potential impact of completing todos on cultural score."""
    total_impact = sum(todo.get("cultural_impact", 0) for todo in todos)
    return min(int(total_impact / len(todos) * 0.3), 25)  # Max 25 point boost

@router.post("/predict", response_model=Dict[str, Any])
async def predict_user_behavior(user_id: str, prediction_horizon: str = "30d"):
    """Predict user behavior based on cultural profile."""
    if user_id not in MOCK_USERS:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = MOCK_USERS[user_id]
    profile = user["cultural_profile"]
    
    # Generate behavioral predictions
    behavioral_predictions = {
        "content_consumption": {
            "music_discovery_rate": random.uniform(0.15, 0.35),
            "cross_cultural_content": random.uniform(0.25, 0.45),
            "new_platform_adoption": random.uniform(0.05, 0.25)
        },
        "engagement_patterns": {
            "peak_activity_hours": ["19:00-21:00", "22:00-24:00"],
            "cultural_content_share_rate": random.uniform(0.08, 0.18),
            "trend_adoption_speed": random.uniform(0.6, 0.9)
        },
        "influence_metrics": {
            "cultural_influence_score": random.uniform(0.3, 0.8),
            "trend_setting_potential": random.uniform(0.2, 0.7),
            "community_impact": random.uniform(0.4, 0.9)
        }
    }
    
    return {
        "user_id": user_id,
        "prediction_horizon": prediction_horizon,
        "behavioral_predictions": behavioral_predictions,
        "confidence_score": random.uniform(0.75, 0.95),
        "generated_at": datetime.now().isoformat()
    }