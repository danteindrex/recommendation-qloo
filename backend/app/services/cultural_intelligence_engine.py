"""
Cultural Intelligence Engine with Qloo API and Google Gemini integration.
Combines Qloo's cultural data with AI-generated explanations and insights.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import json
import google.generativeai as genai

from app.integrations.qloo_api import (
    get_qloo_client, QlooAPIClient, QlooCategory, 
    QlooCorrelation, QlooRecommendation, QlooTrendInsight
)
from app.services.cache_service import get_cache_service
from app.core.config import settings

logger = logging.getLogger(__name__)

# Configure Google Gemini
genai.configure(api_key=settings.GOOGLE_GEMINI_API_KEY)


class CulturalAnalysisType(Enum):
    """Types of cultural analysis."""
    PATTERN_ANALYSIS = "pattern_analysis"
    TREND_PREDICTION = "trend_prediction"
    CULTURAL_MAPPING = "cultural_mapping"
    DIVERSITY_ASSESSMENT = "diversity_assessment"
    RECOMMENDATION_ENGINE = "recommendation_engine"
    BLIND_SPOT_DETECTION = "blind_spot_detection"


@dataclass
class CulturalInsight:
    """Cultural insight with AI-enhanced explanation."""
    insight_id: str
    user_id: str
    insight_type: CulturalAnalysisType
    qloo_data: Dict[str, Any]
    ai_explanation: str
    confidence_score: float
    cultural_factors: List[str]
    actionable_recommendations: List[str]
    generated_at: datetime
    expires_at: Optional[datetime] = None


@dataclass
class CulturalProfile:
    """Comprehensive cultural profile."""
    user_id: str
    cultural_dimensions: Dict[str, float]
    dominant_categories: List[QlooCategory]
    diversity_score: float
    cultural_evolution_trend: str
    influence_network: Dict[str, Any]
    blind_spots: List[str]
    last_updated: datetime


class CulturalIntelligenceEngine:
    """Advanced cultural intelligence engine powered by Qloo and Gemini."""
    
    def __init__(self):
        self.qloo_client: Optional[QlooAPIClient] = None
        self.cache_service = None
        self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Analysis templates for Gemini
        self.gemini_prompts = {
            CulturalAnalysisType.PATTERN_ANALYSIS: """
                Analyze the following cultural pattern data from Qloo and provide insights:
                
                Data: {qloo_data}
                
                Please provide:
                1. A clear explanation of what this cultural pattern means
                2. Why this pattern is significant for the user
                3. How this pattern compares to broader cultural trends
                4. 3 specific actionable recommendations based on this pattern
                
                Keep the explanation engaging and accessible while being culturally insightful.
            """,
            
            CulturalAnalysisType.TREND_PREDICTION: """
                Based on this cultural trend data from Qloo, provide trend analysis:
                
                Data: {qloo_data}
                
                Please analyze:
                1. The significance of this trend in the cultural landscape
                2. Potential future developments and timeline
                3. How users can leverage or adapt to this trend
                4. Cultural implications and broader impact
                
                Focus on actionable insights and future-oriented recommendations.
            """,
            
            CulturalAnalysisType.CULTURAL_MAPPING: """
                Interpret this cultural mapping data from Qloo:
                
                Data: {qloo_data}
                
                Provide insights on:
                1. The user's cultural identity and preferences
                2. Unique aspects of their cultural profile
                3. How they fit within broader cultural clusters
                4. Opportunities for cultural exploration and growth
                
                Make it personal and encouraging while being analytically rigorous.
            """,
            
            CulturalAnalysisType.DIVERSITY_ASSESSMENT: """
                Analyze this cultural diversity data from Qloo:
                
                Data: {qloo_data}
                
                Please assess:
                1. The user's current level of cultural diversity
                2. Strengths and potential areas for improvement
                3. Benefits of increasing cultural diversity
                4. Specific strategies to broaden cultural horizons
                
                Be constructive and motivational in your analysis.
            """,
            
            CulturalAnalysisType.RECOMMENDATION_ENGINE: """
                Based on these cultural recommendations from Qloo:
                
                Data: {qloo_data}
                
                Explain:
                1. Why these recommendations are culturally relevant
                2. How they connect to the user's existing preferences
                3. The cultural journey these recommendations represent
                4. Expected benefits and experiences from following these recommendations
                
                Make the recommendations compelling and well-reasoned.
            """,
            
            CulturalAnalysisType.BLIND_SPOT_DETECTION: """
                Analyze these cultural blind spots identified by Qloo:
                
                Data: {qloo_data}
                
                Provide insights on:
                1. What these blind spots reveal about cultural exposure
                2. Why addressing these gaps could be valuable
                3. Gentle suggestions for cultural exploration
                4. How to approach new cultural territories comfortably
                
                Be encouraging and non-judgmental while highlighting opportunities.
            """
        }
    
    async def _get_services(self):
        """Initialize service dependencies."""
        if not self.qloo_client:
            self.qloo_client = await get_qloo_client()
        if not self.cache_service:
            self.cache_service = await get_cache_service()
    
    async def _generate_ai_explanation(
        self, 
        analysis_type: CulturalAnalysisType,
        qloo_data: Dict[str, Any]
    ) -> str:
        """Generate AI explanation using Google Gemini."""
        try:
            prompt = self.gemini_prompts[analysis_type]
            formatted_prompt = prompt.format(qloo_data=json.dumps(qloo_data, indent=2))
            
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.gemini_model.generate_content(formatted_prompt)
            )
            
            explanation = response.text.strip()
            logger.debug(f"Generated AI explanation for {analysis_type.value}")
            return explanation
            
        except Exception as e:
            logger.error(f"Failed to generate AI explanation: {e}")
            return f"Cultural analysis based on Qloo data: {json.dumps(qloo_data, indent=2)}"
    
    async def analyze_cultural_patterns(
        self,
        user_id: str,
        social_media_data: Dict[str, Any],
        analysis_depth: str = "comprehensive"
    ) -> CulturalInsight:
        """Analyze cultural patterns using Qloo API and enhance with AI insights."""
        await self._get_services()

        # Cache-aside: Check cache first
        cache_key = f"cultural_insight:{user_id}:pattern_analysis"
        cached_insight = await self.cache_service.get(cache_key)
        if cached_insight:
            return CulturalInsight(**cached_insight)

        try:
            # Extract entities from social media data
            entities = self._extract_cultural_entities(social_media_data)

            # Get cultural correlations from Qloo
            correlations = await self.qloo_client.get_cultural_correlations(
                entities=entities,
                min_correlation=0.4
            )
            
            # Prepare Qloo data for AI analysis
            qloo_data = {
                "correlations": [
                    {
                        "entity_a": corr.entity_a.name,
                        "entity_b": corr.entity_b.name,
                        "strength": corr.correlation_strength,
                        "type": corr.correlation_type,
                        "cultural_context": corr.cultural_context
                    }
                    for corr in correlations
                ],
                "analysis_metadata": {
                    "total_entities": len(entities),
                    "strong_correlations": len([c for c in correlations if c.correlation_strength > 0.7]),
                    "cross_category_patterns": len(set(c.entity_a.category for c in correlations))
                }
            }
            
            # Generate AI explanation
            ai_explanation = await self._generate_ai_explanation(
                CulturalAnalysisType.PATTERN_ANALYSIS,
                qloo_data
            )
            
            # Extract actionable recommendations from AI response
            recommendations = self._extract_recommendations(ai_explanation)
            
            # Calculate confidence score
            confidence = self.qloo_client.calculate_confidence_score(
                {"data": qloo_data, "confidence": 0.8},
                {
                    "entity_coverage": min(len(entities) / 20, 1.0),
                    "temporal_relevance": 0.9,
                    "data_freshness": 0.85
                }
            )
            
            insight = CulturalInsight(
                insight_id=f"pattern_{user_id}_{int(datetime.now().timestamp())}",
                user_id=user_id,
                insight_type=CulturalAnalysisType.PATTERN_ANALYSIS,
                qloo_data=qloo_data,
                ai_explanation=ai_explanation,
                confidence_score=confidence,
                cultural_factors=[c.correlation_type for c in correlations[:5]],
                actionable_recommendations=recommendations,
                generated_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=24)
            )
            
            # Cache the insight
            await self._cache_insight(insight)
            
            logger.info(f"Generated cultural pattern insight for user {user_id}")
            return insight
            
        except Exception as e:
            logger.error(f"Failed to analyze cultural patterns: {e}")
            raise
    
    async def predict_cultural_trends(
        self,
        user_id: str,
        categories: List[QlooCategory],
        time_horizon: str = "90d"
    ) -> CulturalInsight:
        """Predict cultural trends using Qloo API with AI-enhanced analysis."""
        await self._get_services()

        # Cache-aside: Check cache first
        cache_key = f"cultural_insight:{user_id}:trend_prediction"
        cached_insight = await self.cache_service.get(cache_key)
        if cached_insight:
            return CulturalInsight(**cached_insight)

        try:
            # Get trend analysis from Qloo
            trends = await self.qloo_client.get_trend_analysis(
                categories=categories,
                time_horizon=time_horizon,
                geographic_scope=["US", "global"]
            )
            
            # Prepare trend data for AI analysis
            qloo_data = {
                "trends": [
                    {
                        "category": trend.category.value,
                        "strength": trend.trend_strength,
                        "direction": trend.trend_direction,
                        "predicted_peak": trend.predicted_peak.isoformat() if trend.predicted_peak else None,
                        "geographic_relevance": trend.geographic_relevance,
                        "demographic_segments": trend.demographic_segments
                    }
                    for trend in trends
                ],
                "trend_summary": {
                    "rising_trends": len([t for t in trends if t.trend_direction == "rising"]),
                    "declining_trends": len([t for t in trends if t.trend_direction == "declining"]),
                    "strongest_trend": max(trends, key=lambda t: t.trend_strength).category.value if trends else None
                }
            }
            
            # Generate AI explanation
            ai_explanation = await self._generate_ai_explanation(
                CulturalAnalysisType.TREND_PREDICTION,
                qloo_data
            )
            
            recommendations = self._extract_recommendations(ai_explanation)
            
            confidence = self.qloo_client.calculate_confidence_score(
                {"data": qloo_data, "confidence": 0.85}
            )
            
            insight = CulturalInsight(
                insight_id=f"trend_{user_id}_{int(datetime.now().timestamp())}",
                user_id=user_id,
                insight_type=CulturalAnalysisType.TREND_PREDICTION,
                qloo_data=qloo_data,
                ai_explanation=ai_explanation,
                confidence_score=confidence,
                cultural_factors=[t.category.value for t in trends[:3]],
                actionable_recommendations=recommendations,
                generated_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=6)
            )
            
            await self._cache_insight(insight)
            
            logger.info(f"Generated trend prediction insight for user {user_id}")
            return insight
            
        except Exception as e:
            logger.error(f"Failed to predict cultural trends: {e}")
            raise
    
    async def generate_cultural_recommendations(
        self,
        user_id: str,
        user_preferences: Dict[str, Any],
        recommendation_count: int = 10
    ) -> CulturalInsight:
        """Generate cultural recommendations using Qloo API with AI enhancement."""
        await self._get_services()

        # Cache-aside: Check cache first
        cache_key = f"cultural_insight:{user_id}:recommendation_engine"
        cached_insight = await self.cache_service.get(cache_key)
        if cached_insight:
            return CulturalInsight(**cached_insight)

        try:
            # Extract seed entities from preferences
            seed_entities = self._extract_seed_entities(user_preferences)

            # Get recommendations from Qloo
            recommendations = await self.qloo_client.get_recommendations(
                seed_entities=seed_entities,
                categories=[QlooCategory.MUSIC, QlooCategory.MOVIES, QlooCategory.BOOKS],
                limit=recommendation_count
            )
            
            # Prepare recommendation data for AI analysis
            qloo_data = {
                "recommendations": [
                    {
                        "entity": rec.recommended_entity.name,
                        "category": rec.recommended_entity.category.value,
                        "reason": rec.reason,
                        "confidence": rec.confidence,
                        "cultural_factors": rec.cultural_factors,
                        "seasonal_relevance": rec.seasonal_relevance
                    }
                    for rec in recommendations
                ],
                "recommendation_metadata": {
                    "seed_entities": seed_entities,
                    "categories_covered": len(set(r.recommended_entity.category for r in recommendations)),
                    "avg_confidence": sum(r.confidence for r in recommendations) / len(recommendations) if recommendations else 0
                }
            }
            
            # Generate AI explanation
            ai_explanation = await self._generate_ai_explanation(
                CulturalAnalysisType.RECOMMENDATION_ENGINE,
                qloo_data
            )
            
            recommendations_text = self._extract_recommendations(ai_explanation)
            
            confidence = self.qloo_client.calculate_confidence_score(
                {"data": qloo_data, "confidence": 0.8}
            )
            
            insight = CulturalInsight(
                insight_id=f"rec_{user_id}_{int(datetime.now().timestamp())}",
                user_id=user_id,
                insight_type=CulturalAnalysisType.RECOMMENDATION_ENGINE,
                qloo_data=qloo_data,
                ai_explanation=ai_explanation,
                confidence_score=confidence,
                cultural_factors=[r.recommended_entity.category.value for r in recommendations[:5]],
                actionable_recommendations=recommendations_text,
                generated_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=12)
            )
            
            await self._cache_insight(insight)
            
            logger.info(f"Generated cultural recommendations for user {user_id}")
            return insight
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            raise
    
    async def get_cultural_evolution_timeline(
        self,
        user_id: str,
        user_history: List[Dict[str, Any]]
    ) -> CulturalInsight:
        """Get cultural evolution timeline using Qloo API with AI-enhanced analysis."""
        await self._get_services()

        # Cache-aside: Check cache first
        cache_key = f"cultural_insight:{user_id}:evolution_timeline"
        cached_insight = await self.cache_service.get(cache_key)
        if cached_insight:
            return CulturalInsight(**cached_insight)

        try:
            # Analyze cultural evolution
            evolution_data = await self.qloo_client.analyze_cultural_evolution(
                user_history=user_history,
                time_window="365d"
            )

            # Prepare data for AI analysis
            qloo_data = {
                "evolution_timeline": evolution_data,
                "summary": {
                    "total_events": len(user_history),
                    "start_date": user_history[0]["date"] if user_history else None,
                    "end_date": user_history[-1]["date"] if user_history else None,
                }
            }

            # Generate AI explanation
            ai_explanation = await self._generate_ai_explanation(
                CulturalAnalysisType.CULTURAL_MAPPING, # Using CULTURAL_MAPPING for a timeline explanation
                qloo_data
            )

            recommendations = self._extract_recommendations(ai_explanation)

            confidence = self.qloo_client.calculate_confidence_score(
                {"data": qloo_data, "confidence": 0.9}
            )

            insight = CulturalInsight(
                insight_id=f"evolution_{user_id}_{int(datetime.now().timestamp())}",
                user_id=user_id,
                insight_type=CulturalAnalysisType.CULTURAL_MAPPING,
                qloo_data=qloo_data,
                ai_explanation=ai_explanation,
                confidence_score=confidence,
                cultural_factors=list(evolution_data.get("key_milestones", {}).keys())[:5],
                actionable_recommendations=recommendations,
                generated_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=7)
            )

            await self._cache_insight(insight)

            logger.info(f"Generated cultural evolution timeline for user {user_id}")
            return insight

        except Exception as e:
            logger.error(f"Failed to get cultural evolution timeline: {e}")
            raise

    async def assess_cultural_diversity(
        self,
        user_id: str,
        user_history: List[Dict[str, Any]]
    ) -> CulturalInsight:
        """Assess cultural diversity using Qloo's analysis."""
        await self._get_services()

        # Cache-aside: Check cache first
        cache_key = f"cultural_insight:{user_id}:diversity_assessment"
        cached_insight = await self.cache_service.get(cache_key)
        if cached_insight:
            return CulturalInsight(**cached_insight)

        try:
            # Analyze cultural evolution
            evolution_data = await self.qloo_client.analyze_cultural_evolution(
                user_history=user_history,
                time_window="90d"
            )
            
            # Get cultural mapping
            user_preferences = self._aggregate_preferences(user_history)
            cultural_map = await self.qloo_client.get_cultural_mapping(
                user_preferences=user_preferences
            )
            
            # Combine data for analysis
            qloo_data = {
                "diversity_metrics": {
                    "diversity_score": cultural_map.get("diversity_score", 0.0),
                    "openness_to_experience": cultural_map.get("openness_to_experience", 0.0),
                    "cultural_clusters": len(cultural_map.get("cultural_clusters", [])),
                    "category_breadth": len(set(item.get("category") for item in user_history if item.get("category")))
                },
                "evolution_analysis": evolution_data,
                "cultural_dimensions": cultural_map.get("cultural_dimensions", {})
            }
            
            # Generate AI explanation
            ai_explanation = await self._generate_ai_explanation(
                CulturalAnalysisType.DIVERSITY_ASSESSMENT,
                qloo_data
            )
            
            recommendations = self._extract_recommendations(ai_explanation)
            
            confidence = self.qloo_client.calculate_confidence_score(
                {"data": qloo_data, "confidence": 0.85}
            )
            
            insight = CulturalInsight(
                insight_id=f"diversity_{user_id}_{int(datetime.now().timestamp())}",
                user_id=user_id,
                insight_type=CulturalAnalysisType.DIVERSITY_ASSESSMENT,
                qloo_data=qloo_data,
                ai_explanation=ai_explanation,
                confidence_score=confidence,
                cultural_factors=list(cultural_map.get("cultural_dimensions", {}).keys())[:5],
                actionable_recommendations=recommendations,
                generated_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=7)
            )
            
            await self._cache_insight(insight)
            
            logger.info(f"Generated diversity assessment for user {user_id}")
            return insight
            
        except Exception as e:
            logger.error(f"Failed to assess cultural diversity: {e}")
            raise
    
    async def detect_cultural_blind_spots(
        self,
        user_id: str,
        user_profile: Dict[str, Any]
    ) -> CulturalInsight:
        """Detect cultural blind spots using Qloo's gap analysis."""
        await self._get_services()

        # Cache-aside: Check cache first
        cache_key = f"cultural_insight:{user_id}:blind_spot_detection"
        cached_insight = await self.cache_service.get(cache_key)
        if cached_insight:
            return CulturalInsight(**cached_insight)

        try:
            # Get blind spots analysis from Qloo
            blind_spots = await self.qloo_client.get_cultural_blind_spots(
                user_profile=user_profile,
                reference_demographics=["millennials", "gen_z", "global"]
            )
            
            # Prepare blind spots data for AI analysis
            qloo_data = {
                "blind_spots_analysis": blind_spots,
                "summary": {
                    "unexplored_categories": len(blind_spots.get("unexplored_categories", [])),
                    "expansion_opportunities": len(blind_spots.get("expansion_opportunities", [])),
                    "diversity_gaps": list(blind_spots.get("cultural_gaps", {}).keys())
                }
            }
            
            # Generate AI explanation
            ai_explanation = await self._generate_ai_explanation(
                CulturalAnalysisType.BLIND_SPOT_DETECTION,
                qloo_data
            )
            
            recommendations = self._extract_recommendations(ai_explanation)
            
            confidence = self.qloo_client.calculate_confidence_score(
                {"data": qloo_data, "confidence": 0.75}
            )
            
            insight = CulturalInsight(
                insight_id=f"blindspots_{user_id}_{int(datetime.now().timestamp())}",
                user_id=user_id,
                insight_type=CulturalAnalysisType.BLIND_SPOT_DETECTION,
                qloo_data=qloo_data,
                ai_explanation=ai_explanation,
                confidence_score=confidence,
                cultural_factors=blind_spots.get("unexplored_categories", [])[:5],
                actionable_recommendations=recommendations,
                generated_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=3)
            )
            
            await self._cache_insight(insight)
            
            logger.info(f"Generated blind spots analysis for user {user_id}")
            return insight
            
        except Exception as e:
            logger.error(f"Failed to detect cultural blind spots: {e}")
            raise
    
    async def get_cultural_compatibility(
        self,
        user_a_profile: Dict[str, Any],
        user_b_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get cultural compatibility score between two users."""
        await self._get_services()

        try:
            compatibility_score = await self.qloo_client.get_cultural_compatibility(
                profile_a=user_a_profile,
                profile_b=user_b_profile
            )

            logger.info(f"Generated cultural compatibility score")
            return compatibility_score

        except Exception as e:
            logger.error(f"Failed to get cultural compatibility score: {e}")
            raise

    async def get_cultural_challenges(
        self,
        user_id: str,
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get cultural challenges using Qloo's expansion recommendations."""
        await self._get_services()

        try:
            challenges = await self.qloo_client.get_cultural_expansion_recommendations(
                user_profile=user_profile
            )

            logger.info(f"Generated cultural challenges for user {user_id}")
            return challenges

        except Exception as e:
            logger.error(f"Failed to get cultural challenges: {e}")
            raise

    async def get_influence_network(
        self,
        user_id: str,
        social_media_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get cultural influence network using Qloo's correlation data."""
        await self._get_services()

        try:
            entities = self._extract_cultural_entities(social_media_data)
            correlations = await self.qloo_client.get_cultural_correlations(
                entities=entities,
                min_correlation=0.2
            )

            # Build a graph-like structure for the network
            network = {"nodes": [], "links": []}
            node_set = set()

            for corr in correlations:
                if corr.entity_a.name not in node_set:
                    network["nodes"].append({"id": corr.entity_a.name, "category": corr.entity_a.category.value})
                    node_set.add(corr.entity_a.name)
                if corr.entity_b.name not in node_set:
                    network["nodes"].append({"id": corr.entity_b.name, "category": corr.entity_b.category.value})
                    node_set.add(corr.entity_b.name)
                
                network["links"].append({
                    "source": corr.entity_a.name,
                    "target": corr.entity_b.name,
                    "strength": corr.correlation_strength
                })

            logger.info(f"Generated influence network for user {user_id}")
            return network

        except Exception as e:
            logger.error(f"Failed to get influence network: {e}")
            raise

    async def get_anonymous_benchmark(
        self,
        user_profile: Dict[str, Any],
        demographics: List[str]
    ) -> Dict[str, Any]:
        """Get anonymous benchmark against specified demographics."""
        await self._get_services()

        try:
            benchmark_data = await self.qloo_client.get_demographic_insights(
                user_profile=user_profile,
                demographics=demographics
            )

            logger.info(f"Generated anonymous benchmark for demographics: {demographics}")
            return benchmark_data

        except Exception as e:
            logger.error(f"Failed to get anonymous benchmark: {e}")
            raise

    async def build_cultural_profile(
        self,
        user_id: str,
        comprehensive_data: Dict[str, Any]
    ) -> CulturalProfile:
        """Build comprehensive cultural profile using all available analysis."""
        await self._get_services()
        
        try:
            # Get various analyses
            user_preferences = comprehensive_data.get("preferences", {})
            user_history = comprehensive_data.get("history", [])
            social_media_data = comprehensive_data.get("social_media", {})
            
            # Get cultural mapping
            cultural_map = await self.qloo_client.get_cultural_mapping(
                user_preferences=user_preferences
            )
            
            # Get cultural evolution
            evolution_data = await self.qloo_client.analyze_cultural_evolution(
                user_history=user_history
            )
            
            # Get blind spots
            blind_spots_data = await self.qloo_client.get_cultural_blind_spots(
                user_profile=user_preferences
            )
            
            # Extract entities and get correlations
            entities = self._extract_cultural_entities(social_media_data)
            correlations = await self.qloo_client.get_cultural_correlations(entities)
            
            # Build comprehensive profile
            profile = CulturalProfile(
                user_id=user_id,
                cultural_dimensions=cultural_map.get("cultural_dimensions", {}),
                dominant_categories=self._extract_dominant_categories(correlations, user_history),
                diversity_score=cultural_map.get("diversity_score", 0.0),
                cultural_evolution_trend=self._determine_evolution_trend(evolution_data),
                influence_network=cultural_map.get("influence_network", {}),
                blind_spots=blind_spots_data.get("unexplored_categories", []),
                last_updated=datetime.now()
            )
            
            # Cache the profile
            await self._cache_profile(profile)
            
            logger.info(f"Built comprehensive cultural profile for user {user_id}")
            return profile
            
        except Exception as e:
            logger.error(f"Failed to build cultural profile: {e}")
            raise
    
    def _extract_cultural_entities(self, social_media_data: Dict[str, Any]) -> List[str]:
        """Extract cultural entities from social media data."""
        entities = []
        
        # Extract from different platforms
        for platform, data in social_media_data.items():
            if isinstance(data, dict):
                entities.extend(data.get("artists", []))
                entities.extend(data.get("tracks", []))
                entities.extend(data.get("hashtags", []))
                entities.extend(data.get("interests", []))
        
        return list(set(entities))[:50]  # Limit to 50 entities
    
    def _extract_seed_entities(self, user_preferences: Dict[str, Any]) -> List[str]:
        """Extract seed entities from user preferences."""
        seeds = []
        
        for category, prefs in user_preferences.items():
            if isinstance(prefs, list):
                seeds.extend(prefs[:5])
            elif isinstance(prefs, dict):
                seeds.extend(list(prefs.keys())[:5])
        
        return list(set(seeds))[:20]
    
    def _aggregate_preferences(self, user_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate user preferences from history."""
        preferences = {}
        
        for item in user_history:
            category = item.get("category", "general")
            if category not in preferences:
                preferences[category] = []
            
            if "name" in item:
                preferences[category].append(item["name"])
        
        return preferences
    
    def _extract_recommendations(self, ai_explanation: str) -> List[str]:
        """Extract actionable recommendations from AI explanation."""
        # Simple extraction - in production, use more sophisticated NLP
        lines = ai_explanation.split("\n")
        recommendations = []
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ["recommend", "suggest", "try", "explore", "consider"]):
                if len(line) > 20 and len(line) < 200:  # Reasonable length
                    recommendations.append(line)
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    def _extract_dominant_categories(
        self, 
        correlations: List[QlooCorrelation],
        user_history: List[Dict[str, Any]]
    ) -> List[QlooCategory]:
        """Extract dominant cultural categories."""
        category_counts = {}
        
        # Count from correlations
        for corr in correlations:
            cat_a = corr.entity_a.category
            cat_b = corr.entity_b.category
            category_counts[cat_a] = category_counts.get(cat_a, 0) + 1
            category_counts[cat_b] = category_counts.get(cat_b, 0) + 1
        
        # Count from history
        for item in user_history:
            if "category" in item:
                try:
                    cat = QlooCategory(item["category"])
                    category_counts[cat] = category_counts.get(cat, 0) + 1
                except ValueError:
                    pass
        
        # Return top 5 categories
        sorted_cats = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        return [cat for cat, _ in sorted_cats[:5]]
    
    def _determine_evolution_trend(self, evolution_data: Dict[str, Any]) -> str:
        """Determine cultural evolution trend."""
        diversity_timeline = evolution_data.get("diversity_timeline", [])
        
        if len(diversity_timeline) < 2:
            return "stable"
        
        recent_diversity = diversity_timeline[-1].get("diversity_score", 0)
        past_diversity = diversity_timeline[0].get("diversity_score", 0)
        
        if recent_diversity > past_diversity * 1.1:
            return "expanding"
        elif recent_diversity < past_diversity * 0.9:
            return "focusing"
        else:
            return "stable"
    
    async def invalidate_user_cache(self, user_id: str):
        """Invalidate all cache entries for a user."""
        try:
            await self._get_services()
            # Invalidate all insights
            for insight_type in CulturalAnalysisType:
                cache_key = f"cultural_insight:{user_id}:{insight_type.value}"
                await self.cache_service.delete(cache_key)

            # Invalidate profile
            profile_key = f"cultural_profile:{user_id}"
            await self.cache_service.delete(profile_key)

            logger.info(f"Invalidated cache for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to invalidate cache for user {user_id}: {e}")

    async def _cache_insight(self, insight: CulturalInsight):
        """Cache cultural insight."""
        try:
            cache_key = f"cultural_insight:{insight.user_id}:{insight.insight_type.value}"
            cache_data = json.dumps(asdict(insight), default=str)
            
            await self.cache_service.set(
                cache_key,
                cache_data,
                expire=int(insight.expires_at.timestamp() - datetime.now().timestamp())
            )
        except Exception as e:
            logger.error(f"Failed to cache insight: {e}")
    
    async def _cache_profile(self, profile: CulturalProfile):
        """Cache cultural profile."""
        try:
            cache_key = f"cultural_profile:{profile.user_id}"
            cache_data = json.dumps(asdict(profile), default=str)
            
            await self.cache_service.set(
                cache_key,
                cache_data,
                expire=86400 * 7  # 7 days
            )
        except Exception as e:
            logger.error(f"Failed to cache profile: {e}")
    
    async def get_cached_insight(self, user_id: str, insight_type: CulturalAnalysisType) -> Optional[CulturalInsight]:
        """Get cached cultural insight."""
        try:
            await self._get_services()
            
            cache_pattern = f"cultural_insight:{user_id}:*"
            # This would require a more sophisticated cache search
            # For now, return None to force fresh analysis
            return None
            
        except Exception as e:
            logger.error(f"Failed to get cached insight: {e}")
            return None


# Global cultural intelligence engine instance
cultural_engine = CulturalIntelligenceEngine()


async def get_cultural_engine() -> CulturalIntelligenceEngine:
    """Get the global cultural intelligence engine instance."""
    return cultural_engine
