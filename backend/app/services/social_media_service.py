from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.cultural_data import SocialConnection, CulturalDataPoint, SocialPlatform, CulturalDataType
from app.integrations.social_media.instagram import InstagramClient
from app.integrations.social_media.tiktok import TikTokClient
from app.integrations.social_media.spotify import SpotifyClient
from app.integrations.social_media.base import SocialMediaData, OAuthCredentials
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class SocialMediaService:
    """Unified service for social media data processing and normalization"""
    
    def __init__(self):
        self.clients = {
            SocialPlatform.INSTAGRAM: InstagramClient(
                client_id=settings.INSTAGRAM_CLIENT_ID,
                client_secret=settings.INSTAGRAM_CLIENT_SECRET
            ),
            SocialPlatform.TIKTOK: TikTokClient(
                client_id=settings.TIKTOK_CLIENT_ID,
                client_secret=settings.TIKTOK_CLIENT_SECRET
            ),
            SocialPlatform.SPOTIFY: SpotifyClient(
                client_id=settings.SPOTIFY_CLIENT_ID,
                client_secret=settings.SPOTIFY_CLIENT_SECRET
            )
        }
    
    async def get_oauth_url(self, platform: SocialPlatform, redirect_uri: str, state: str) -> str:
        """Get OAuth authorization URL for a platform"""
        client = self.clients.get(platform)
        if not client:
            raise ValueError(f"Unsupported platform: {platform}")
        
        return await client.get_oauth_url(redirect_uri, state)
    
    async def exchange_code_for_token(
        self, 
        platform: SocialPlatform, 
        code: str, 
        redirect_uri: str
    ) -> OAuthCredentials:
        """Exchange authorization code for access token"""
        client = self.clients.get(platform)
        if not client:
            raise ValueError(f"Unsupported platform: {platform}")
        
        return await client.exchange_code_for_token(code, redirect_uri)
    
    async def refresh_access_token(
        self, 
        platform: SocialPlatform, 
        refresh_token: str
    ) -> OAuthCredentials:
        """Refresh access token for a platform"""
        client = self.clients.get(platform)
        if not client:
            raise ValueError(f"Unsupported platform: {platform}")
        
        return await client.refresh_access_token(refresh_token)
    
    async def ingest_user_data(
        self, 
        db: AsyncSession,
        user_id: str, 
        platform: SocialPlatform,
        credentials: OAuthCredentials
    ) -> List[CulturalDataPoint]:
        """Ingest and normalize user data from a social media platform"""
        client = self.clients.get(platform)
        if not client:
            raise ValueError(f"Unsupported platform: {platform}")
        
        try:
            # Fetch raw data from platform
            raw_data = await client.get_user_data(credentials)
            
            # Normalize and store data
            cultural_data_points = []
            for data_item in raw_data:
                normalized_data = self._normalize_social_media_data(data_item)
                
                # Create cultural data point
                cultural_point = CulturalDataPoint(
                    user_id=user_id,
                    platform=platform,
                    data_type=self._map_data_type(data_item.data_type),
                    content=normalized_data,
                    cultural_signals=self._extract_cultural_signals(data_item),
                    confidence_score=self._calculate_confidence_score(data_item),
                    processed_at=datetime.now(timezone.utc)
                )
                
                db.add(cultural_point)
                cultural_data_points.append(cultural_point)
            
            await db.commit()
            logger.info(f"Successfully ingested {len(cultural_data_points)} data points from {platform} for user {user_id}")
            
            return cultural_data_points
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error ingesting data from {platform} for user {user_id}: {str(e)}")
            raise
    
    def _normalize_social_media_data(self, data: SocialMediaData) -> Dict[str, Any]:
        """Normalize social media data to a common format"""
        normalized = {
            "platform": data.platform,
            "timestamp": data.timestamp.isoformat(),
            "data_type": data.data_type,
            "content": data.content
        }
        
        # Platform-specific normalization
        if data.platform == "instagram":
            normalized.update(self._normalize_instagram_data(data))
        elif data.platform == "tiktok":
            normalized.update(self._normalize_tiktok_data(data))
        elif data.platform == "spotify":
            normalized.update(self._normalize_spotify_data(data))
        
        return normalized
    
    def _normalize_instagram_data(self, data: SocialMediaData) -> Dict[str, Any]:
        """Normalize Instagram-specific data"""
        if data.data_type == "post":
            return {
                "media_type": data.content.get("media_type"),
                "caption": data.content.get("caption", ""),
                "engagement_metrics": {
                    "permalink": data.content.get("permalink")
                },
                "cultural_indicators": {
                    "visual_content": data.content.get("media_type") in ["IMAGE", "CAROUSEL_ALBUM"],
                    "video_content": data.content.get("media_type") == "VIDEO",
                    "has_caption": bool(data.content.get("caption"))
                }
            }
        elif data.data_type == "profile":
            return {
                "profile_metrics": {
                    "media_count": data.content.get("media_count", 0),
                    "account_type": data.content.get("account_type")
                },
                "cultural_indicators": {
                    "content_creator": data.content.get("account_type") == "CREATOR",
                    "business_account": data.content.get("account_type") == "BUSINESS"
                }
            }
        return {}
    
    def _normalize_tiktok_data(self, data: SocialMediaData) -> Dict[str, Any]:
        """Normalize TikTok-specific data"""
        if data.data_type == "post":
            return {
                "video_metrics": {
                    "duration": data.content.get("duration", 0),
                    "view_count": data.content.get("view_count", 0),
                    "like_count": data.content.get("like_count", 0),
                    "comment_count": data.content.get("comment_count", 0),
                    "share_count": data.content.get("share_count", 0)
                },
                "cultural_indicators": {
                    "short_form_content": data.content.get("duration", 0) < 60,
                    "viral_potential": data.content.get("view_count", 0) > 10000,
                    "engagement_rate": self._calculate_tiktok_engagement_rate(data.content)
                }
            }
        elif data.data_type == "profile":
            return {
                "profile_metrics": {
                    "follower_count": data.content.get("follower_count", 0),
                    "following_count": data.content.get("following_count", 0),
                    "likes_count": data.content.get("likes_count", 0),
                    "video_count": data.content.get("video_count", 0)
                },
                "cultural_indicators": {
                    "influencer_status": data.content.get("follower_count", 0) > 10000,
                    "content_creator": data.content.get("video_count", 0) > 50
                }
            }
        return {}
    
    def _normalize_spotify_data(self, data: SocialMediaData) -> Dict[str, Any]:
        """Normalize Spotify-specific data"""
        if data.data_type == "music":
            return {
                "music_metrics": {
                    "track_name": data.content.get("track_name"),
                    "artist_name": data.content.get("artist_name"),
                    "album_name": data.content.get("album_name"),
                    "popularity": data.content.get("popularity", 0),
                    "duration_ms": data.content.get("duration_ms", 0),
                    "explicit": data.content.get("explicit", False)
                },
                "cultural_indicators": {
                    "mainstream_music": data.content.get("popularity", 0) > 70,
                    "niche_music": data.content.get("popularity", 0) < 30,
                    "explicit_content": data.content.get("explicit", False),
                    "genres": data.content.get("genres", [])
                }
            }
        elif data.data_type == "interaction":
            return {
                "artist_metrics": {
                    "artist_name": data.content.get("artist_name"),
                    "genres": data.content.get("genres", []),
                    "popularity": data.content.get("popularity", 0),
                    "followers": data.content.get("followers", 0)
                },
                "cultural_indicators": {
                    "genre_diversity": len(data.content.get("genres", [])),
                    "mainstream_artist": data.content.get("popularity", 0) > 70,
                    "underground_artist": data.content.get("popularity", 0) < 30
                }
            }
        return {}
    
    def _extract_cultural_signals(self, data: SocialMediaData) -> Dict[str, Any]:
        """Extract cultural signals from social media data"""
        signals = {
            "timestamp": data.timestamp.isoformat(),
            "platform": data.platform,
            "data_type": data.data_type
        }
        
        # Platform-specific cultural signal extraction
        if data.platform == "instagram":
            signals.update(self._extract_instagram_cultural_signals(data))
        elif data.platform == "tiktok":
            signals.update(self._extract_tiktok_cultural_signals(data))
        elif data.platform == "spotify":
            signals.update(self._extract_spotify_cultural_signals(data))
        
        return signals
    
    def _extract_instagram_cultural_signals(self, data: SocialMediaData) -> Dict[str, Any]:
        """Extract cultural signals from Instagram data"""
        if data.data_type == "post":
            caption = data.content.get("caption", "").lower()
            return {
                "visual_storytelling": data.content.get("media_type") in ["IMAGE", "CAROUSEL_ALBUM"],
                "video_content_creation": data.content.get("media_type") == "VIDEO",
                "hashtag_usage": "#" in caption,
                "caption_length": len(data.content.get("caption", "")),
                "cultural_themes": self._detect_cultural_themes_in_text(caption)
            }
        return {}
    
    def _extract_tiktok_cultural_signals(self, data: SocialMediaData) -> Dict[str, Any]:
        """Extract cultural signals from TikTok data"""
        if data.data_type == "post":
            return {
                "short_form_video_culture": True,
                "viral_engagement": data.content.get("view_count", 0) > 10000,
                "trend_participation": data.content.get("share_count", 0) > 100,
                "generation_z_content": data.content.get("duration", 0) < 30,
                "engagement_velocity": self._calculate_tiktok_engagement_rate(data.content)
            }
        return {}
    
    def _extract_spotify_cultural_signals(self, data: SocialMediaData) -> Dict[str, Any]:
        """Extract cultural signals from Spotify data"""
        if data.data_type == "music":
            genres = data.content.get("genres", [])
            return {
                "music_discovery": data.content.get("popularity", 0) < 50,
                "mainstream_consumption": data.content.get("popularity", 0) > 70,
                "genre_diversity": len(genres),
                "cultural_genres": genres,
                "explicit_content_tolerance": data.content.get("explicit", False),
                "listening_patterns": {
                    "track_duration": data.content.get("duration_ms", 0),
                    "artist_popularity": data.content.get("popularity", 0)
                }
            }
        return {}
    
    def _calculate_confidence_score(self, data: SocialMediaData) -> float:
        """Calculate confidence score for cultural data"""
        base_score = 0.5
        
        # Increase confidence based on data completeness
        if data.content:
            base_score += 0.2
        
        # Platform-specific confidence adjustments
        if data.platform == "spotify" and data.data_type == "music":
            # Spotify data is generally more reliable for cultural analysis
            base_score += 0.2
        elif data.platform == "tiktok" and data.data_type == "post":
            # TikTok engagement metrics are good cultural indicators
            if data.content.get("view_count", 0) > 1000:
                base_score += 0.1
        elif data.platform == "instagram" and data.data_type == "post":
            # Instagram posts with captions provide more cultural context
            if data.content.get("caption"):
                base_score += 0.1
        
        return min(1.0, base_score)
    
    def _map_data_type(self, platform_data_type: str) -> CulturalDataType:
        """Map platform-specific data types to cultural data types"""
        mapping = {
            "post": CulturalDataType.POST,
            "story": CulturalDataType.STORY,
            "music": CulturalDataType.MUSIC,
            "interaction": CulturalDataType.INTERACTION,
            "profile": CulturalDataType.INTERACTION
        }
        return mapping.get(platform_data_type, CulturalDataType.INTERACTION)
    
    def _calculate_tiktok_engagement_rate(self, content: Dict[str, Any]) -> float:
        """Calculate TikTok engagement rate"""
        views = content.get("view_count", 0)
        if views == 0:
            return 0.0
        
        likes = content.get("like_count", 0)
        comments = content.get("comment_count", 0)
        shares = content.get("share_count", 0)
        
        total_engagement = likes + comments + shares
        return total_engagement / views if views > 0 else 0.0
    
    def _detect_cultural_themes_in_text(self, text: str) -> List[str]:
        """Detect cultural themes in text content"""
        # Simple keyword-based cultural theme detection
        cultural_keywords = {
            "food": ["food", "recipe", "cooking", "restaurant", "meal"],
            "travel": ["travel", "vacation", "trip", "explore", "adventure"],
            "fashion": ["fashion", "style", "outfit", "clothing", "trend"],
            "fitness": ["fitness", "workout", "gym", "health", "exercise"],
            "art": ["art", "creative", "design", "painting", "music"],
            "technology": ["tech", "digital", "app", "innovation", "gadget"],
            "lifestyle": ["lifestyle", "daily", "routine", "life", "living"]
        }
        
        detected_themes = []
        text_lower = text.lower()
        
        for theme, keywords in cultural_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_themes.append(theme)
        
        return detected_themes
    
    async def close_clients(self):
        """Close all HTTP clients"""
        for client in self.clients.values():
            await client.close()