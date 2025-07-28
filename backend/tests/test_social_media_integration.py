import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone, timedelta
from httpx import Response
from app.integrations.social_media.instagram import InstagramClient
from app.integrations.social_media.tiktok import TikTokClient
from app.integrations.social_media.spotify import SpotifyClient
from app.integrations.social_media.base import OAuthCredentials, SocialMediaData
from app.services.social_media_service import SocialMediaService
from app.models.cultural_data import SocialPlatform


class TestInstagramClient:
    """Test Instagram API client"""
    
    @pytest.fixture
    def instagram_client(self):
        return InstagramClient(
            client_id="test_client_id",
            client_secret="test_client_secret"
        )
    
    @pytest.mark.asyncio
    async def test_get_oauth_url(self, instagram_client):
        """Test Instagram OAuth URL generation"""
        redirect_uri = "http://localhost:3000/callback"
        state = "test_state"
        
        oauth_url = await instagram_client.get_oauth_url(redirect_uri, state)
        
        assert "https://api.instagram.com/oauth/authorize" in oauth_url
        assert "client_id=test_client_id" in oauth_url
        assert "redirect_uri=http%3A//localhost%3A3000/callback" in oauth_url
        assert "state=test_state" in oauth_url
        assert "scope=user_profile%2Cuser_media" in oauth_url
    
    @pytest.mark.asyncio
    async def test_exchange_code_for_token(self, instagram_client):
        """Test Instagram code to token exchange"""
        mock_short_token_response = {
            "access_token": "short_token",
            "user_id": "12345"
        }
        
        mock_long_token_response = {
            "access_token": "long_token",
            "expires_in": 5184000
        }
        
        with patch.object(instagram_client, 'make_api_request') as mock_request:
            mock_request.side_effect = [mock_short_token_response, mock_long_token_response]
            
            credentials = await instagram_client.exchange_code_for_token(
                code="test_code",
                redirect_uri="http://localhost:3000/callback"
            )
            
            assert credentials.access_token == "long_token"
            assert credentials.platform_user_id == "12345"
            assert credentials.expires_at is not None
    
    @pytest.mark.asyncio
    async def test_get_user_data(self, instagram_client):
        """Test Instagram user data fetching"""
        mock_profile_data = {
            "id": "12345",
            "username": "testuser",
            "account_type": "PERSONAL",
            "media_count": 10
        }
        
        mock_media_data = {
            "data": [
                {
                    "id": "media1",
                    "caption": "Test post",
                    "media_type": "IMAGE",
                    "timestamp": "2024-01-01T12:00:00Z",
                    "permalink": "https://instagram.com/p/test"
                }
            ]
        }
        
        credentials = OAuthCredentials(
            access_token="test_token",
            platform_user_id="12345"
        )
        
        with patch.object(instagram_client, '_get_user_profile') as mock_profile, \
             patch.object(instagram_client, '_get_user_media') as mock_media:
            
            mock_profile.return_value = mock_profile_data
            mock_media.return_value = mock_media_data
            
            data_points = await instagram_client.get_user_data(credentials)
            
            assert len(data_points) == 2  # Profile + 1 media item
            assert data_points[0].platform == "instagram"
            assert data_points[0].data_type == "profile"
            assert data_points[1].data_type == "post"


class TestTikTokClient:
    """Test TikTok API client"""
    
    @pytest.fixture
    def tiktok_client(self):
        return TikTokClient(
            client_id="test_client_id",
            client_secret="test_client_secret"
        )
    
    @pytest.mark.asyncio
    async def test_get_oauth_url(self, tiktok_client):
        """Test TikTok OAuth URL generation"""
        redirect_uri = "http://localhost:3000/callback"
        state = "test_state"
        
        oauth_url = await tiktok_client.get_oauth_url(redirect_uri, state)
        
        assert "https://www.tiktok.com/v2/auth/authorize" in oauth_url
        assert "client_key=test_client_id" in oauth_url
        assert "scope=user.info.basic%2Cvideo.list" in oauth_url
    
    @pytest.mark.asyncio
    async def test_exchange_code_for_token(self, tiktok_client):
        """Test TikTok code to token exchange"""
        mock_response = {
            "data": {
                "access_token": "test_access_token",
                "refresh_token": "test_refresh_token",
                "expires_in": 86400,
                "open_id": "tiktok_user_123"
            }
        }
        
        with patch.object(tiktok_client, 'make_api_request') as mock_request:
            mock_request.return_value = mock_response
            
            credentials = await tiktok_client.exchange_code_for_token(
                code="test_code",
                redirect_uri="http://localhost:3000/callback"
            )
            
            assert credentials.access_token == "test_access_token"
            assert credentials.refresh_token == "test_refresh_token"
            assert credentials.platform_user_id == "tiktok_user_123"
    
    @pytest.mark.asyncio
    async def test_get_user_data(self, tiktok_client):
        """Test TikTok user data fetching"""
        mock_user_info = {
            "display_name": "Test User",
            "follower_count": 1000,
            "video_count": 50
        }
        
        mock_videos_data = {
            "videos": [
                {
                    "id": "video1",
                    "title": "Test Video",
                    "duration": 30,
                    "view_count": 5000,
                    "like_count": 100,
                    "create_time": 1640995200
                }
            ]
        }
        
        credentials = OAuthCredentials(
            access_token="test_token",
            platform_user_id="tiktok_user_123"
        )
        
        with patch.object(tiktok_client, '_get_user_info') as mock_user, \
             patch.object(tiktok_client, '_get_user_videos') as mock_videos:
            
            mock_user.return_value = mock_user_info
            mock_videos.return_value = mock_videos_data
            
            data_points = await tiktok_client.get_user_data(credentials)
            
            assert len(data_points) == 2  # Profile + 1 video
            assert data_points[0].platform == "tiktok"
            assert data_points[0].data_type == "profile"
            assert data_points[1].data_type == "post"


class TestSpotifyClient:
    """Test Spotify API client"""
    
    @pytest.fixture
    def spotify_client(self):
        return SpotifyClient(
            client_id="test_client_id",
            client_secret="test_client_secret"
        )
    
    @pytest.mark.asyncio
    async def test_get_oauth_url(self, spotify_client):
        """Test Spotify OAuth URL generation"""
        redirect_uri = "http://localhost:3000/callback"
        state = "test_state"
        
        oauth_url = await spotify_client.get_oauth_url(redirect_uri, state)
        
        assert "https://accounts.spotify.com/authorize" in oauth_url
        assert "client_id=test_client_id" in oauth_url
        assert "user-read-private" in oauth_url
        assert "user-top-read" in oauth_url
    
    @pytest.mark.asyncio
    async def test_exchange_code_for_token(self, spotify_client):
        """Test Spotify code to token exchange"""
        mock_token_response = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_in": 3600
        }
        
        mock_profile_response = {
            "id": "spotify_user_123"
        }
        
        with patch.object(spotify_client, 'make_api_request') as mock_request, \
             patch.object(spotify_client, '_get_user_profile') as mock_profile:
            
            mock_request.return_value = mock_token_response
            mock_profile.return_value = mock_profile_response
            
            credentials = await spotify_client.exchange_code_for_token(
                code="test_code",
                redirect_uri="http://localhost:3000/callback"
            )
            
            assert credentials.access_token == "test_access_token"
            assert credentials.refresh_token == "test_refresh_token"
            assert credentials.platform_user_id == "spotify_user_123"
    
    @pytest.mark.asyncio
    async def test_get_user_data(self, spotify_client):
        """Test Spotify user data fetching"""
        mock_profile_data = {
            "id": "spotify_user_123",
            "display_name": "Test User",
            "country": "US",
            "followers": {"total": 50}
        }
        
        mock_top_tracks = {
            "items": [
                {
                    "name": "Test Song",
                    "artists": [{"name": "Test Artist"}],
                    "album": {"name": "Test Album"},
                    "popularity": 80,
                    "duration_ms": 180000
                }
            ]
        }
        
        mock_top_artists = {
            "items": [
                {
                    "name": "Test Artist",
                    "genres": ["pop", "rock"],
                    "popularity": 75,
                    "followers": {"total": 1000000}
                }
            ]
        }
        
        mock_recent_tracks = {
            "items": [
                {
                    "track": {
                        "name": "Recent Song",
                        "artists": [{"name": "Recent Artist"}]
                    },
                    "played_at": "2024-01-01T12:00:00Z"
                }
            ]
        }
        
        credentials = OAuthCredentials(
            access_token="test_token",
            platform_user_id="spotify_user_123"
        )
        
        with patch.object(spotify_client, '_get_user_profile') as mock_profile, \
             patch.object(spotify_client, '_get_top_tracks') as mock_tracks, \
             patch.object(spotify_client, '_get_top_artists') as mock_artists, \
             patch.object(spotify_client, '_get_recently_played') as mock_recent:
            
            mock_profile.return_value = mock_profile_data
            mock_tracks.return_value = mock_top_tracks
            mock_artists.return_value = mock_top_artists
            mock_recent.return_value = mock_recent_tracks
            
            data_points = await spotify_client.get_user_data(credentials)
            
            assert len(data_points) == 4  # Profile + 1 track + 1 artist + 1 recent
            assert data_points[0].platform == "spotify"
            assert data_points[0].data_type == "profile"
            assert data_points[1].data_type == "music"
            assert data_points[2].data_type == "interaction"


class TestSocialMediaService:
    """Test unified social media service"""
    
    @pytest.fixture
    def social_media_service(self):
        with patch('app.services.social_media_service.settings') as mock_settings:
            mock_settings.INSTAGRAM_CLIENT_ID = "test_ig_id"
            mock_settings.INSTAGRAM_CLIENT_SECRET = "test_ig_secret"
            mock_settings.TIKTOK_CLIENT_ID = "test_tt_id"
            mock_settings.TIKTOK_CLIENT_SECRET = "test_tt_secret"
            mock_settings.SPOTIFY_CLIENT_ID = "test_sp_id"
            mock_settings.SPOTIFY_CLIENT_SECRET = "test_sp_secret"
            
            return SocialMediaService()
    
    @pytest.mark.asyncio
    async def test_get_oauth_url_instagram(self, social_media_service):
        """Test OAuth URL generation for Instagram"""
        with patch.object(social_media_service.clients[SocialPlatform.INSTAGRAM], 'get_oauth_url') as mock_oauth:
            mock_oauth.return_value = "https://instagram.com/oauth"
            
            url = await social_media_service.get_oauth_url(
                SocialPlatform.INSTAGRAM,
                "http://localhost:3000/callback",
                "test_state"
            )
            
            assert url == "https://instagram.com/oauth"
            mock_oauth.assert_called_once_with("http://localhost:3000/callback", "test_state")
    
    @pytest.mark.asyncio
    async def test_exchange_code_for_token_spotify(self, social_media_service):
        """Test token exchange for Spotify"""
        mock_credentials = OAuthCredentials(
            access_token="test_token",
            refresh_token="test_refresh",
            platform_user_id="spotify_123"
        )
        
        with patch.object(social_media_service.clients[SocialPlatform.SPOTIFY], 'exchange_code_for_token') as mock_exchange:
            mock_exchange.return_value = mock_credentials
            
            credentials = await social_media_service.exchange_code_for_token(
                SocialPlatform.SPOTIFY,
                "test_code",
                "http://localhost:3000/callback"
            )
            
            assert credentials.access_token == "test_token"
            assert credentials.platform_user_id == "spotify_123"
    
    @pytest.mark.asyncio
    async def test_normalize_instagram_data(self, social_media_service):
        """Test Instagram data normalization"""
        instagram_data = SocialMediaData(
            platform="instagram",
            user_id="12345",
            data_type="post",
            content={
                "media_type": "IMAGE",
                "caption": "Test post #hashtag",
                "permalink": "https://instagram.com/p/test"
            },
            timestamp=datetime.now(timezone.utc),
            raw_data={}
        )
        
        normalized = social_media_service._normalize_social_media_data(instagram_data)
        
        assert normalized["platform"] == "instagram"
        assert normalized["media_type"] == "IMAGE"
        assert normalized["cultural_indicators"]["visual_content"] is True
        assert normalized["cultural_indicators"]["has_caption"] is True
    
    @pytest.mark.asyncio
    async def test_normalize_tiktok_data(self, social_media_service):
        """Test TikTok data normalization"""
        tiktok_data = SocialMediaData(
            platform="tiktok",
            user_id="tiktok_123",
            data_type="post",
            content={
                "duration": 25,
                "view_count": 15000,
                "like_count": 500,
                "comment_count": 50,
                "share_count": 25
            },
            timestamp=datetime.now(timezone.utc),
            raw_data={}
        )
        
        normalized = social_media_service._normalize_social_media_data(tiktok_data)
        
        assert normalized["platform"] == "tiktok"
        assert normalized["video_metrics"]["duration"] == 25
        assert normalized["cultural_indicators"]["short_form_content"] is True
        assert normalized["cultural_indicators"]["viral_potential"] is True
    
    @pytest.mark.asyncio
    async def test_normalize_spotify_data(self, social_media_service):
        """Test Spotify data normalization"""
        spotify_data = SocialMediaData(
            platform="spotify",
            user_id="spotify_123",
            data_type="music",
            content={
                "track_name": "Test Song",
                "artist_name": "Test Artist",
                "popularity": 85,
                "explicit": False,
                "genres": ["pop", "rock"]
            },
            timestamp=datetime.now(timezone.utc),
            raw_data={}
        )
        
        normalized = social_media_service._normalize_social_media_data(spotify_data)
        
        assert normalized["platform"] == "spotify"
        assert normalized["music_metrics"]["track_name"] == "Test Song"
        assert normalized["cultural_indicators"]["mainstream_music"] is True
        assert normalized["cultural_indicators"]["explicit_content"] is False
    
    @pytest.mark.asyncio
    async def test_extract_cultural_signals_instagram(self, social_media_service):
        """Test cultural signal extraction from Instagram data"""
        instagram_data = SocialMediaData(
            platform="instagram",
            user_id="12345",
            data_type="post",
            content={
                "media_type": "VIDEO",
                "caption": "Amazing food at this restaurant! #foodie #travel"
            },
            timestamp=datetime.now(timezone.utc),
            raw_data={}
        )
        
        signals = social_media_service._extract_cultural_signals(instagram_data)
        
        assert signals["platform"] == "instagram"
        assert signals["video_content_creation"] is True
        assert signals["hashtag_usage"] is True
        assert "food" in signals["cultural_themes"]
        assert "travel" in signals["cultural_themes"]
    
    @pytest.mark.asyncio
    async def test_extract_cultural_signals_spotify(self, social_media_service):
        """Test cultural signal extraction from Spotify data"""
        spotify_data = SocialMediaData(
            platform="spotify",
            user_id="spotify_123",
            data_type="music",
            content={
                "popularity": 25,
                "explicit": True,
                "genres": ["indie", "alternative"],
                "duration_ms": 240000
            },
            timestamp=datetime.now(timezone.utc),
            raw_data={}
        )
        
        signals = social_media_service._extract_cultural_signals(spotify_data)
        
        assert signals["platform"] == "spotify"
        assert signals["music_discovery"] is True
        assert signals["mainstream_consumption"] is False
        assert signals["explicit_content_tolerance"] is True
        assert signals["cultural_genres"] == ["indie", "alternative"]
    
    @pytest.mark.asyncio
    async def test_calculate_confidence_score(self, social_media_service):
        """Test confidence score calculation"""
        # High confidence data (Spotify with complete info)
        high_confidence_data = SocialMediaData(
            platform="spotify",
            user_id="spotify_123",
            data_type="music",
            content={
                "track_name": "Test Song",
                "artist_name": "Test Artist",
                "popularity": 75
            },
            timestamp=datetime.now(timezone.utc),
            raw_data={}
        )
        
        high_score = social_media_service._calculate_confidence_score(high_confidence_data)
        assert high_score >= 0.7
        
        # Lower confidence data (empty content)
        low_confidence_data = SocialMediaData(
            platform="instagram",
            user_id="12345",
            data_type="post",
            content={},
            timestamp=datetime.now(timezone.utc),
            raw_data={}
        )
        
        low_score = social_media_service._calculate_confidence_score(low_confidence_data)
        assert low_score <= 0.5
    
    @pytest.mark.asyncio
    async def test_detect_cultural_themes_in_text(self, social_media_service):
        """Test cultural theme detection in text"""
        text_with_themes = "Love this new fashion trend! Going to the gym after this amazing meal at a restaurant."
        
        themes = social_media_service._detect_cultural_themes_in_text(text_with_themes)
        
        assert "fashion" in themes
        assert "fitness" in themes
        assert "food" in themes
    
    @pytest.mark.asyncio
    async def test_calculate_tiktok_engagement_rate(self, social_media_service):
        """Test TikTok engagement rate calculation"""
        content_high_engagement = {
            "view_count": 10000,
            "like_count": 1000,
            "comment_count": 100,
            "share_count": 50
        }
        
        high_rate = social_media_service._calculate_tiktok_engagement_rate(content_high_engagement)
        assert high_rate == 0.115  # (1000 + 100 + 50) / 10000
        
        content_no_views = {
            "view_count": 0,
            "like_count": 10,
            "comment_count": 5,
            "share_count": 2
        }
        
        zero_rate = social_media_service._calculate_tiktok_engagement_rate(content_no_views)
        assert zero_rate == 0.0


class TestRetryLogicAndErrorHandling:
    """Test retry logic and error handling"""
    
    @pytest.fixture
    def instagram_client(self):
        return InstagramClient(
            client_id="test_client_id",
            client_secret="test_client_secret"
        )
    
    @pytest.mark.asyncio
    async def test_retry_logic_on_http_error(self, instagram_client):
        """Test retry logic with exponential backoff on HTTP errors"""
        from httpx import HTTPStatusError, Request, Response
        
        # Mock a 500 error that should trigger retry
        mock_request = Request("GET", "https://api.instagram.com/test")
        mock_response = Response(500, request=mock_request)
        error = HTTPStatusError("Server Error", request=mock_request, response=mock_response)
        
        with patch.object(instagram_client.http_client, 'request') as mock_request_method:
            # First two calls fail, third succeeds
            mock_request_method.side_effect = [error, error, AsyncMock(return_value=MagicMock(json=lambda: {"success": True}))]
            
            # Mock the response.raise_for_status() and response.json() methods
            success_response = MagicMock()
            success_response.raise_for_status.return_value = None
            success_response.json.return_value = {"success": True}
            mock_request_method.side_effect = [error, error, success_response]
            
            result = await instagram_client.make_api_request("GET", "https://api.instagram.com/test")
            
            assert result == {"success": True}
            assert mock_request_method.call_count == 3
    
    @pytest.mark.asyncio
    async def test_retry_exhaustion(self, instagram_client):
        """Test that retry logic eventually gives up after max attempts"""
        from httpx import HTTPStatusError, Request, Response
        
        mock_request = Request("GET", "https://api.instagram.com/test")
        mock_response = Response(500, request=mock_request)
        error = HTTPStatusError("Server Error", request=mock_request, response=mock_response)
        
        with patch.object(instagram_client.http_client, 'request') as mock_request_method:
            mock_request_method.side_effect = error
            
            with pytest.raises(HTTPStatusError):
                await instagram_client.make_api_request("GET", "https://api.instagram.com/test")
            
            # Should have tried 3 times (initial + 2 retries)
            assert mock_request_method.call_count == 3
    
    @pytest.mark.asyncio
    async def test_unsupported_platform_error(self):
        """Test error handling for unsupported platforms"""
        service = SocialMediaService()
        
        with pytest.raises(ValueError, match="Unsupported platform"):
            await service.get_oauth_url("unsupported_platform", "redirect", "state")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])