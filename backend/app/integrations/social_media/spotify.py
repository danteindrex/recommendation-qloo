from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta
import urllib.parse
import base64
from .base import BaseSocialMediaClient, SocialMediaData, OAuthCredentials
import logging

logger = logging.getLogger(__name__)


class SpotifyClient(BaseSocialMediaClient):
    """Spotify Web API client"""
    
    BASE_URL = "https://accounts.spotify.com"
    API_URL = "https://api.spotify.com/v1"
    
    def __init__(self, client_id: str, client_secret: str):
        super().__init__(client_id, client_secret)
        self.platform = "spotify"
    
    async def get_oauth_url(self, redirect_uri: str, state: str) -> str:
        """Generate Spotify OAuth authorization URL"""
        scopes = [
            'user-read-private',
            'user-read-email',
            'user-top-read',
            'user-read-recently-played',
            'user-library-read',
            'playlist-read-private',
            'user-follow-read'
        ]
        
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': redirect_uri,
            'scope': ' '.join(scopes),
            'state': state,
            'show_dialog': 'false'
        }
        
        query_string = urllib.parse.urlencode(params)
        return f"{self.BASE_URL}/authorize?{query_string}"
    
    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> OAuthCredentials:
        """Exchange authorization code for access token"""
        auth_header = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()
        
        headers = {
            'Authorization': f'Basic {auth_header}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri
        }
        
        response = await self.make_api_request(
            method="POST",
            url=f"{self.BASE_URL}/api/token",
            headers=headers,
            json_data=data
        )
        
        # Get user profile to get user ID
        user_profile = await self._get_user_profile(response['access_token'])
        
        return OAuthCredentials(
            access_token=response['access_token'],
            refresh_token=response['refresh_token'],
            expires_at=datetime.now(timezone.utc) + timedelta(
                seconds=response['expires_in']
            ),
            platform_user_id=user_profile['id']
        )
    
    async def refresh_access_token(self, refresh_token: str) -> OAuthCredentials:
        """Refresh Spotify access token"""
        auth_header = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()
        
        headers = {
            'Authorization': f'Basic {auth_header}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        
        response = await self.make_api_request(
            method="POST",
            url=f"{self.BASE_URL}/api/token",
            headers=headers,
            json_data=data
        )
        
        return OAuthCredentials(
            access_token=response['access_token'],
            refresh_token=response.get('refresh_token', refresh_token),
            expires_at=datetime.now(timezone.utc) + timedelta(
                seconds=response['expires_in']
            ),
            platform_user_id=""  # Will be filled by caller
        )    

    async def get_user_data(self, credentials: OAuthCredentials) -> List[SocialMediaData]:
        """Fetch user data from Spotify"""
        data_points = []
        
        try:
            # Get user profile
            profile_data = await self._get_user_profile(credentials.access_token)
            data_points.append(SocialMediaData(
                platform=self.platform,
                user_id=credentials.platform_user_id,
                data_type="profile",
                content={
                    "display_name": profile_data.get("display_name"),
                    "country": profile_data.get("country"),
                    "followers": profile_data.get("followers", {}).get("total", 0),
                    "product": profile_data.get("product")
                },
                timestamp=datetime.now(timezone.utc),
                raw_data=profile_data
            ))
            
            # Get top tracks
            top_tracks = await self._get_top_tracks(credentials.access_token)
            for track in top_tracks.get("items", []):
                data_points.append(SocialMediaData(
                    platform=self.platform,
                    user_id=credentials.platform_user_id,
                    data_type="music",
                    content={
                        "track_name": track.get("name"),
                        "artist_name": track.get("artists", [{}])[0].get("name"),
                        "album_name": track.get("album", {}).get("name"),
                        "popularity": track.get("popularity"),
                        "duration_ms": track.get("duration_ms"),
                        "explicit": track.get("explicit"),
                        "genres": track.get("album", {}).get("genres", [])
                    },
                    timestamp=datetime.now(timezone.utc),
                    raw_data=track
                ))
            
            # Get top artists
            top_artists = await self._get_top_artists(credentials.access_token)
            for artist in top_artists.get("items", []):
                data_points.append(SocialMediaData(
                    platform=self.platform,
                    user_id=credentials.platform_user_id,
                    data_type="interaction",
                    content={
                        "artist_name": artist.get("name"),
                        "genres": artist.get("genres", []),
                        "popularity": artist.get("popularity"),
                        "followers": artist.get("followers", {}).get("total", 0)
                    },
                    timestamp=datetime.now(timezone.utc),
                    raw_data=artist
                ))
            
            # Get recently played tracks
            recent_tracks = await self._get_recently_played(credentials.access_token)
            for item in recent_tracks.get("items", []):
                track = item.get("track", {})
                data_points.append(SocialMediaData(
                    platform=self.platform,
                    user_id=credentials.platform_user_id,
                    data_type="music",
                    content={
                        "track_name": track.get("name"),
                        "artist_name": track.get("artists", [{}])[0].get("name"),
                        "played_at": item.get("played_at"),
                        "context": item.get("context", {}).get("type")
                    },
                    timestamp=datetime.fromisoformat(
                        item.get("played_at", "").replace("Z", "+00:00")
                    ) if item.get("played_at") else datetime.now(timezone.utc),
                    raw_data=item
                ))
            
        except Exception as e:
            logger.error(f"Error fetching Spotify data: {str(e)}")
            raise
        
        return data_points
    
    async def _get_user_profile(self, access_token: str) -> Dict[str, Any]:
        """Get user profile information"""
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        return await self.make_api_request(
            method="GET",
            url=f"{self.API_URL}/me",
            headers=headers
        )
    
    async def _get_top_tracks(self, access_token: str, limit: int = 20, time_range: str = "medium_term") -> Dict[str, Any]:
        """Get user's top tracks"""
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        params = {
            'limit': limit,
            'time_range': time_range
        }
        
        return await self.make_api_request(
            method="GET",
            url=f"{self.API_URL}/me/top/tracks",
            headers=headers,
            params=params
        )
    
    async def _get_top_artists(self, access_token: str, limit: int = 20, time_range: str = "medium_term") -> Dict[str, Any]:
        """Get user's top artists"""
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        params = {
            'limit': limit,
            'time_range': time_range
        }
        
        return await self.make_api_request(
            method="GET",
            url=f"{self.API_URL}/me/top/artists",
            headers=headers,
            params=params
        )
    
    async def _get_recently_played(self, access_token: str, limit: int = 50) -> Dict[str, Any]:
        """Get recently played tracks"""
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        params = {
            'limit': limit
        }
        
        return await self.make_api_request(
            method="GET",
            url=f"{self.API_URL}/me/player/recently-played",
            headers=headers,
            params=params
        )