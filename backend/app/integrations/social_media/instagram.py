from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta
import urllib.parse
from .base import BaseSocialMediaClient, SocialMediaData, OAuthCredentials
import logging

logger = logging.getLogger(__name__)


class InstagramClient(BaseSocialMediaClient):
    """Instagram Basic Display API client"""
    
    BASE_URL = "https://api.instagram.com"
    GRAPH_URL = "https://graph.instagram.com"
    
    def __init__(self, client_id: str, client_secret: str):
        super().__init__(client_id, client_secret)
        self.platform = "instagram"
    
    async def get_oauth_url(self, redirect_uri: str, state: str) -> str:
        """Generate Instagram OAuth authorization URL"""
        params = {
            'client_id': self.client_id,
            'redirect_uri': redirect_uri,
            'scope': 'user_profile,user_media',
            'response_type': 'code',
            'state': state
        }
        
        query_string = urllib.parse.urlencode(params)
        return f"{self.BASE_URL}/oauth/authorize?{query_string}"
    
    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> OAuthCredentials:
        """Exchange authorization code for access token"""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri,
            'code': code
        }
        
        response = await self.make_api_request(
            method="POST",
            url=f"{self.BASE_URL}/oauth/access_token",
            json_data=data
        )
        
        # Get long-lived token
        long_lived_token = await self._get_long_lived_token(response['access_token'])
        
        return OAuthCredentials(
            access_token=long_lived_token['access_token'],
            expires_at=datetime.now(timezone.utc).replace(
                second=0, microsecond=0
            ) + timedelta(seconds=long_lived_token.get('expires_in', 5184000)),
            platform_user_id=response['user_id']
        )
    
    async def _get_long_lived_token(self, short_lived_token: str) -> Dict[str, Any]:
        """Convert short-lived token to long-lived token"""
        params = {
            'grant_type': 'ig_exchange_token',
            'client_secret': self.client_secret,
            'access_token': short_lived_token
        }
        
        return await self.make_api_request(
            method="GET",
            url=f"{self.GRAPH_URL}/access_token",
            params=params
        )    

    async def refresh_access_token(self, refresh_token: str) -> OAuthCredentials:
        """Refresh Instagram access token (long-lived tokens can be refreshed)"""
        params = {
            'grant_type': 'ig_refresh_token',
            'access_token': refresh_token
        }
        
        response = await self.make_api_request(
            method="GET",
            url=f"{self.GRAPH_URL}/refresh_access_token",
            params=params
        )
        
        return OAuthCredentials(
            access_token=response['access_token'],
            expires_at=datetime.now(timezone.utc).replace(
                second=0, microsecond=0
            ) + timedelta(seconds=response.get('expires_in', 5184000)),
            platform_user_id=""  # Will be filled by caller
        )
    
    async def get_user_data(self, credentials: OAuthCredentials) -> List[SocialMediaData]:
        """Fetch user media and profile data from Instagram"""
        data_points = []
        
        try:
            # Get user profile
            profile_data = await self._get_user_profile(credentials.access_token)
            data_points.append(SocialMediaData(
                platform=self.platform,
                user_id=credentials.platform_user_id,
                data_type="profile",
                content={
                    "username": profile_data.get("username"),
                    "account_type": profile_data.get("account_type"),
                    "media_count": profile_data.get("media_count")
                },
                timestamp=datetime.now(timezone.utc),
                raw_data=profile_data
            ))
            
            # Get user media
            media_data = await self._get_user_media(credentials.access_token)
            for media_item in media_data.get("data", []):
                data_points.append(SocialMediaData(
                    platform=self.platform,
                    user_id=credentials.platform_user_id,
                    data_type="post",
                    content={
                        "media_type": media_item.get("media_type"),
                        "caption": media_item.get("caption"),
                        "timestamp": media_item.get("timestamp"),
                        "permalink": media_item.get("permalink")
                    },
                    timestamp=datetime.fromisoformat(
                        media_item.get("timestamp", "").replace("Z", "+00:00")
                    ) if media_item.get("timestamp") else datetime.now(timezone.utc),
                    raw_data=media_item
                ))
            
        except Exception as e:
            logger.error(f"Error fetching Instagram data: {str(e)}")
            raise
        
        return data_points
    
    async def _get_user_profile(self, access_token: str) -> Dict[str, Any]:
        """Get user profile information"""
        params = {
            'fields': 'id,username,account_type,media_count',
            'access_token': access_token
        }
        
        return await self.make_api_request(
            method="GET",
            url=f"{self.GRAPH_URL}/me",
            params=params
        )
    
    async def _get_user_media(self, access_token: str, limit: int = 25) -> Dict[str, Any]:
        """Get user media posts"""
        params = {
            'fields': 'id,caption,media_type,media_url,permalink,thumbnail_url,timestamp',
            'limit': limit,
            'access_token': access_token
        }
        
        return await self.make_api_request(
            method="GET",
            url=f"{self.GRAPH_URL}/me/media",
            params=params
        )