"""
Qloo API integration service for cultural intelligence.
Provides cultural pattern analysis, trend forecasting, and recommendation services.
"""

import httpx
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.services.cache_service import get_cache_service

from pybreaker import CircuitBreaker, CircuitBreakerError

logger = logging.getLogger(__name__)


class QlooCategory(Enum):
    """Qloo cultural categories."""
    MUSIC = "music"
    MOVIES = "movies"
    TV = "tv"
    RESTAURANTS = "restaurants"
    FASHION = "fashion"
    BOOKS = "books"
    TRAVEL = "travel"
    NIGHTLIFE = "nightlife"
    BRANDS = "brands"


class QlooAnalysisType(Enum):
    """Types of Qloo analysis."""
    CORRELATION = "correlation"
    RECOMMENDATION = "recommendation"
    TREND_ANALYSIS = "trend_analysis"
    CULTURAL_MAPPING = "cultural_mapping"
    DEMOGRAPHIC_INSIGHT = "demographic_insight"


@dataclass
class QlooEntity:
    """Qloo entity representation."""
    entity_id: str
    name: str
    category: QlooCategory
    metadata: Dict[str, Any]
    confidence_score: float = 0.0


@dataclass
class QlooCorrelation:
    """Qloo correlation result."""
    entity_a: QlooEntity
    entity_b: QlooEntity
    correlation_strength: float
    correlation_type: str
    cultural_context: Dict[str, Any]


@dataclass
class QlooRecommendation:
    """Qloo recommendation result."""
    recommended_entity: QlooEntity
    reason: str
    confidence: float
    cultural_factors: List[str]
    seasonal_relevance: Optional[str] = None


@dataclass
class QlooTrendInsight:
    """Qloo trend analysis insight."""
    trend_id: str
    category: QlooCategory
    trend_strength: float
    trend_direction: str  # "rising", "declining", "stable"
    predicted_peak: Optional[datetime]
    geographic_relevance: List[str]
    demographic_segments: List[str]


class QlooAPIClient:
    """Qloo API client for cultural intelligence."""
    
    def __init__(self):
        self.base_url = "https://hackathon.api.qloo.com"
        self.api_key = settings.QLOO_API_KEY
        self.client_id = settings.QLOO_CLIENT_ID
        self.cache_service = None
        
        # Rate limiting
        self.rate_limit_per_minute = 1000
        self.rate_limit_requests = []
        
        # HTTP client configuration
        self.timeout = httpx.Timeout(30.0)
        self.circuit_breaker = CircuitBreaker(fail_max=5, reset_timeout=60)
        
    async def _get_cache_service(self):
        """Get cache service instance."""
        if not self.cache_service:
            self.cache_service = await get_cache_service()
        return self.cache_service
    
    def _generate_cache_key(self, endpoint: str, params: Dict[str, Any]) -> str:
        """Generate cache key for request."""
        params_str = json.dumps(params, sort_keys=True)
        return f"qloo:{endpoint}:{hashlib.md5(params_str.encode()).hexdigest()}"
    
    async def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits."""
        now = datetime.now()
        one_minute_ago = now - timedelta(minutes=1)
        
        # Remove old requests
        self.rate_limit_requests = [
            req_time for req_time in self.rate_limit_requests 
            if req_time > one_minute_ago
        ]
        
        return len(self.rate_limit_requests) < self.rate_limit_per_minute
    
    def _record_request(self):
        """Record a request for rate limiting."""
        self.rate_limit_requests.append(datetime.now())
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _make_request(
        self, 
        endpoint: str, 
        params: Dict[str, Any] = None,
        method: str = "GET"
    ) -> Dict[str, Any]:
        """Make authenticated request to Qloo API."""
        try:
            with self.circuit_breaker:
                if not await self._check_rate_limit():
                    logger.warning("Qloo API rate limit reached, waiting...")
                    await asyncio.sleep(60)
                
                self._record_request()
                
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "X-Client-ID": self.client_id
                }
                
                url = f"{self.base_url}/{endpoint}"
                
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    if method == "GET":
                        response = await client.get(url, headers=headers, params=params)
                    else:
                        response = await client.post(url, headers=headers, json=params)
                    
                    response.raise_for_status()
                    return response.json()
        except CircuitBreakerError:
            logger.error(f"Circuit breaker is open for Qloo API. Skipping request to {endpoint}")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"Qloo API HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Qloo API request error: {e}")
            raise
    
    async def _cached_request(
        self, 
        endpoint: str, 
        params: Dict[str, Any] = None,
        cache_ttl: int = 3600
    ) -> Dict[str, Any]:
        """Make cached request to Qloo API."""
        cache_service = await self._get_cache_service()
        cache_key = self._generate_cache_key(endpoint, params or {})
        
        # Try to get from cache first
        cached_result = await cache_service.get(cache_key)
        if cached_result:
            logger.debug(f"Qloo API cache hit for {endpoint}")
            return json.loads(cached_result)
        
        # Make API request
        result = await self._make_request(endpoint, params)
        
        # Cache the result
        await cache_service.set(
            cache_key, 
            json.dumps(result, default=str), 
            expire=cache_ttl
        )
        
        logger.debug(f"Qloo API cache miss for {endpoint}, cached for {cache_ttl}s")
        return result
    
    async def get_cultural_correlations(
        self, 
        entities: List[str],
        categories: List[QlooCategory] = None,
        min_correlation: float = 0.3
    ) -> List[QlooCorrelation]:
        """Get cultural correlations between entities."""
        try:
            params = {
                "entities": entities,
                "min_correlation": min_correlation,
                "include_metadata": True
            }
            
            if categories:
                params["categories"] = [cat.value for cat in categories]
            
            response = await self._cached_request("correlations", params, cache_ttl=1800)
            
            correlations = []
            for corr_data in response.get("correlations", []):
                entity_a = QlooEntity(
                    entity_id=corr_data["entity_a"]["id"],
                    name=corr_data["entity_a"]["name"],
                    category=QlooCategory(corr_data["entity_a"]["category"]),
                    metadata=corr_data["entity_a"].get("metadata", {}),
                    confidence_score=corr_data["entity_a"].get("confidence", 0.0)
                )
                
                entity_b = QlooEntity(
                    entity_id=corr_data["entity_b"]["id"],
                    name=corr_data["entity_b"]["name"],
                    category=QlooCategory(corr_data["entity_b"]["category"]),
                    metadata=corr_data["entity_b"].get("metadata", {}),
                    confidence_score=corr_data["entity_b"].get("confidence", 0.0)
                )
                
                correlation = QlooCorrelation(
                    entity_a=entity_a,
                    entity_b=entity_b,
                    correlation_strength=corr_data["strength"],
                    correlation_type=corr_data["type"],
                    cultural_context=corr_data.get("cultural_context", {})
                )
                correlations.append(correlation)
            
            logger.info(f"Retrieved {len(correlations)} cultural correlations from Qloo")
            return correlations
            
        except Exception as e:
            logger.error(f"Failed to get cultural correlations: {e}")
            return []
    
    async def get_recommendations(
        self,
        seed_entities: List[str],
        categories: List[QlooCategory] = None,
        demographic_filters: Dict[str, Any] = None,
        limit: int = 20
    ) -> List[QlooRecommendation]:
        """Get cultural recommendations based on seed entities."""
        try:
            params = {
                "seed_entities": seed_entities,
                "limit": limit,
                "include_reasoning": True,
                "include_cultural_factors": True
            }
            
            if categories:
                params["categories"] = [cat.value for cat in categories]
            
            if demographic_filters:
                params["demographic_filters"] = demographic_filters
            
            response = await self._cached_request("recommendations", params, cache_ttl=900)
            
            recommendations = []
            for rec_data in response.get("recommendations", []):
                entity = QlooEntity(
                    entity_id=rec_data["entity"]["id"],
                    name=rec_data["entity"]["name"],
                    category=QlooCategory(rec_data["entity"]["category"]),
                    metadata=rec_data["entity"].get("metadata", {}),
                    confidence_score=rec_data["entity"].get("confidence", 0.0)
                )
                
                recommendation = QlooRecommendation(
                    recommended_entity=entity,
                    reason=rec_data.get("reason", ""),
                    confidence=rec_data.get("confidence", 0.0),
                    cultural_factors=rec_data.get("cultural_factors", []),
                    seasonal_relevance=rec_data.get("seasonal_relevance")
                )
                recommendations.append(recommendation)
            
            logger.info(f"Retrieved {len(recommendations)} recommendations from Qloo")
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to get recommendations: {e}")
            return []
    
    async def get_trend_analysis(
        self,
        categories: List[QlooCategory],
        time_horizon: str = "30d",
        geographic_scope: List[str] = None
    ) -> List[QlooTrendInsight]:
        """Get trend analysis for cultural categories."""
        try:
            params = {
                "categories": [cat.value for cat in categories],
                "time_horizon": time_horizon,
                "include_predictions": True,
                "include_demographics": True
            }
            
            if geographic_scope:
                params["geographic_scope"] = geographic_scope
            
            response = await self._cached_request("trends", params, cache_ttl=3600)
            
            trends = []
            for trend_data in response.get("trends", []):
                predicted_peak = None
                if trend_data.get("predicted_peak"):
                    predicted_peak = datetime.fromisoformat(trend_data["predicted_peak"])
                
                trend = QlooTrendInsight(
                    trend_id=trend_data["id"],
                    category=QlooCategory(trend_data["category"]),
                    trend_strength=trend_data["strength"],
                    trend_direction=trend_data["direction"],
                    predicted_peak=predicted_peak,
                    geographic_relevance=trend_data.get("geographic_relevance", []),
                    demographic_segments=trend_data.get("demographic_segments", [])
                )
                trends.append(trend)
            
            logger.info(f"Retrieved {len(trends)} trend insights from Qloo")
            return trends
            
        except Exception as e:
            logger.error(f"Failed to get trend analysis: {e}")
            return []
    
    async def get_cultural_mapping(
        self,
        user_preferences: Dict[str, Any],
        cross_category_analysis: bool = True
    ) -> Dict[str, Any]:
        """Get cultural mapping based on user preferences."""
        try:
            params = {
                "preferences": user_preferences,
                "cross_category_analysis": cross_category_analysis,
                "include_cultural_dimensions": True,
                "include_personality_insights": True
            }
            
            response = await self._cached_request("cultural-mapping", params, cache_ttl=1800)
            
            cultural_map = {
                "cultural_dimensions": response.get("cultural_dimensions", {}),
                "personality_insights": response.get("personality_insights", {}),
                "cultural_clusters": response.get("cultural_clusters", []),
                "influence_network": response.get("influence_network", {}),
                "diversity_score": response.get("diversity_score", 0.0),
                "openness_to_experience": response.get("openness_to_experience", 0.0)
            }
            
            logger.info("Retrieved cultural mapping from Qloo")
            return cultural_map
            
        except Exception as e:
            logger.error(f"Failed to get cultural mapping: {e}")
            return {}
    
    async def get_demographic_insights(
        self,
        entities: List[str],
        demographic_breakdown: bool = True
    ) -> Dict[str, Any]:
        """Get demographic insights for entities."""
        try:
            params = {
                "entities": entities,
                "demographic_breakdown": demographic_breakdown,
                "include_cultural_indices": True,
                "include_geographic_data": True
            }
            
            response = await self._cached_request("demographics", params, cache_ttl=7200)
            
            insights = {
                "demographic_breakdown": response.get("demographic_breakdown", {}),
                "cultural_indices": response.get("cultural_indices", {}),
                "geographic_distribution": response.get("geographic_distribution", {}),
                "age_segments": response.get("age_segments", {}),
                "cultural_affinity_scores": response.get("cultural_affinity_scores", {})
            }
            
            logger.info("Retrieved demographic insights from Qloo")
            return insights
            
        except Exception as e:
            logger.error(f"Failed to get demographic insights: {e}")
            return {}
    
    async def analyze_cultural_evolution(
        self,
        user_history: List[Dict[str, Any]],
        time_window: str = "90d"
    ) -> Dict[str, Any]:
        """Analyze cultural evolution patterns."""
        try:
            params = {
                "user_history": user_history,
                "time_window": time_window,
                "evolution_metrics": [
                    "diversity_change",
                    "category_drift",
                    "influence_network_evolution",
                    "cultural_exploration_pattern"
                ]
            }
            
            response = await self._cached_request("cultural-evolution", params, cache_ttl=3600)
            
            evolution_analysis = {
                "diversity_timeline": response.get("diversity_timeline", []),
                "category_drift_analysis": response.get("category_drift_analysis", {}),
                "exploration_patterns": response.get("exploration_patterns", {}),
                "cultural_milestones": response.get("cultural_milestones", []),
                "predicted_trajectory": response.get("predicted_trajectory", {}),
                "influence_network_changes": response.get("influence_network_changes", {})
            }
            
            logger.info("Retrieved cultural evolution analysis from Qloo")
            return evolution_analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze cultural evolution: {e}")
            return {}
    
    async def get_cultural_blind_spots(
        self,
        user_profile: Dict[str, Any],
        reference_demographics: List[str] = None
    ) -> Dict[str, Any]:
        """Identify cultural blind spots using Qloo's gap analysis."""
        try:
            params = {
                "user_profile": user_profile,
                "gap_analysis": True,
                "recommendation_gaps": True,
                "cultural_exposure_analysis": True
            }
            
            if reference_demographics:
                params["reference_demographics"] = reference_demographics
            
            response = await self._cached_request("blind-spots", params, cache_ttl=3600)
            
            blind_spots = {
                "unexplored_categories": response.get("unexplored_categories", []),
                "cultural_gaps": response.get("cultural_gaps", {}),
                "expansion_opportunities": response.get("expansion_opportunities", []),
                "diversity_improvement_suggestions": response.get("diversity_improvement_suggestions", []),
                "comparative_analysis": response.get("comparative_analysis", {})
            }
            
            logger.info("Retrieved cultural blind spots analysis from Qloo")
            return blind_spots
            
        except Exception as e:
            logger.error(f"Failed to get cultural blind spots: {e}")
            return {}
    
    def calculate_confidence_score(
        self,
        qloo_response: Dict[str, Any],
        data_quality_factors: Dict[str, float] = None
    ) -> float:
        """Calculate confidence score based on Qloo API response quality."""
        base_confidence = qloo_response.get("confidence", 0.5)
        
        # Quality factors
        factors = data_quality_factors or {}
        
        # Response completeness
        completeness = len(qloo_response.get("data", {})) / 10.0
        completeness = min(completeness, 1.0)
        
        # Entity coverage
        entity_coverage = factors.get("entity_coverage", 0.8)
        
        # Temporal relevance
        temporal_relevance = factors.get("temporal_relevance", 0.9)
        
        # Data freshness
        data_freshness = factors.get("data_freshness", 0.85)
        
        # Calculate weighted confidence
        weighted_confidence = (
            base_confidence * 0.4 +
            completeness * 0.2 +
            entity_coverage * 0.2 +
            temporal_relevance * 0.1 +
            data_freshness * 0.1
        )
        
        return min(weighted_confidence, 1.0)


# Global Qloo client instance
qloo_client = QlooAPIClient()


async def get_qloo_client() -> QlooAPIClient:
    """Get the global Qloo client instance."""
    return qloo_client
