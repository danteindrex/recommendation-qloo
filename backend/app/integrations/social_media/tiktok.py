from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta
import urllib.parse
import hashlib
import hmac
import json
from .base import BaseSocialMediaClient, SocialMediaData, OAuthCredentials
import logging

logger = logging.getLogger(__name__)


class TikTokClient(BaseSocialMediaClient):
    """TikTok for Developers API client"""
    
    BASE_URL = "https://www.tiktok.com"
    API_URL = "https://open.tiktokapis.com"
    
    def __init__(self, client_id: str, client_secret: str):
        super().__init__(client_id, client_secret)
        self.platform = "tiktok"
    
    async def get_oauth_url(self, redirect_uri: str, state: str) -> str:
        """Generate TikTok OAuth authorization URL"""
        params = {
            'client_key': self.client_id,
            'scope': 'user.info.basic,video.list',
            'response_type': 'code',
            'redirect_uri': redirect_uri,
            'state': state
        }
        
        query_string = urllib.parse.urlencode(params)
        return f"{self.BASE_URL}/v2/auth/authorize/?{query_string}"
    
    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> OAuthCredentials:
        """Exchange authorization code for access token"""
        data = {
            'client_key': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cache-Control': 'no-cache'
        }
        
        response = await self.make_api_request(
            method="POST",
            url=f"{self.API_URL}/v2/oauth/token/",
            headers=headers,
            json_data=data
        )
        
        return OAuthCredentials(
            access_token=response['data']['access_token'],
            refresh_token=response['data']['refresh_token'],
            expires_at=datetime.now(timezone.utc) + timedelta(
                seconds=response['data']['expires_in']
            ),
            platform_user_id=response['data']['open_id']
        )
    
    async def refresh_access_token(self, refresh_token: str) -> OAuthCredentials:
        """Refresh TikTok access token"""
        data = {
            'client_key': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cache-Control': 'no-cache'
        }
        
        response = await self.make_api_request(
            method="POST",
            url=f"{self.API_URL}/v2/oauth/token/",
            headers=headers,
            json_data=data
        )
        
        return OAuthCredentials(
            access_token=response['data']['access_token'],
            refresh_token=response['data']['refresh_token'],
            expires_at=datetime.now(timezone.utc) + timedelta(
                seconds=response['data']['expires_in']
            ),
            platform_user_id=response['data']['open_id']
        )   
 
    async def get_user_data(self, credentials: OAuthCredentials) -> List[SocialMediaData]:
        """Fetch user data from TikTok"""
        data_points = []
        
        try:
            # Get user info
            user_info = await self._get_user_info(credentials.access_token)
            data_points.append(SocialMediaData(
                platform=self.platform,
                user_id=credentials.platform_user_id,
                data_type="profile",
                content={
                    "display_name": user_info.get("display_name"),
                    "bio_description": user_info.get("bio_description"),
                    "follower_count": user_info.get("follower_count"),
                    "following_count": user_info.get("following_count"),
                    "likes_count": user_info.get("likes_count"),
                    "video_count": user_info.get("video_count")
                },
                timestamp=datetime.now(timezone.utc),
                raw_data=user_info
            ))
            
            # Get user videos
            videos_data = await self._get_user_videos(credentials.access_token)
            for video in videos_data.get("videos", []):
                data_points.append(SocialMediaData(
                    platform=self.platform,
                    user_id=credentials.platform_user_id,
                    data_type="post",
                    content={
                        "title": video.get("title"),
                        "video_description": video.get("video_description"),
                        "duration": video.get("duration"),
                        "view_count": video.get("view_count"),
                        "like_count": video.get("like_count"),
                        "comment_count": video.get("comment_count"),
                        "share_count": video.get("share_count"),
                        "create_time": video.get("create_time")
                    },
                    timestamp=datetime.fromtimestamp(
                        video.get("create_time", 0), tz=timezone.utc
                    ) if video.get("create_time") else datetime.now(timezone.utc),
                    raw_data=video
                ))
            
        except Exception as e:
            logger.error(f"Error fetching TikTok data: {str(e)}")
            raise
        
        return data_points
    
    async def _get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user profile information"""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'fields': [
                'open_id',
                'union_id',
                'avatar_url',
                'display_name',
                'bio_description',
                'profile_deep_link',
                'is_verified',
                'follower_count',
                'following_count',
                'likes_count',
                'video_count'
            ]
        }
        
        response = await self.make_api_request(
            method="POST",
            url=f"{self.API_URL}/v2/user/info/",
            headers=headers,
            json_data=data
        )
        
        return response.get('data', {}).get('user', {})
    
    async def _get_user_videos(self, access_token: str, max_count: int = 20) -> Dict[str, Any]:
        """Get user videos"""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'fields': [
                'id',
                'title',
                'video_description',
                'duration',
                'cover_image_url',
                'embed_html',
                'embed_link',
                'like_count',
                'comment_count',
                'share_count',
                'view_count',
                'create_time'
            ],
            'max_count': max_count
        }
        
        response = await self.make_api_request(
            method="POST",
            url=f"{self.API_URL}/v2/video/list/",
            headers=headers,
            json_data=data
        )
        
        return response.get('data', {})