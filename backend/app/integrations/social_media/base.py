from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import httpx
import logging

logger = logging.getLogger(__name__)


class SocialMediaData(BaseModel):
    """Base model for social media data"""
    platform: str
    user_id: str
    data_type: str
    content: Dict[str, Any]
    timestamp: datetime
    raw_data: Dict[str, Any]


class OAuthCredentials(BaseModel):
    """OAuth credentials for social media platforms"""
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    platform_user_id: str


class BaseSocialMediaClient(ABC):
    """Base class for all social media API clients"""
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    @abstractmethod
    async def get_oauth_url(self, redirect_uri: str, state: str) -> str:
        """Generate OAuth authorization URL"""
        pass
    
    @abstractmethod
    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> OAuthCredentials:
        """Exchange authorization code for access token"""
        pass
    
    @abstractmethod
    async def refresh_access_token(self, refresh_token: str) -> OAuthCredentials:
        """Refresh expired access token"""
        pass
    
    @abstractmethod
    async def get_user_data(self, credentials: OAuthCredentials) -> List[SocialMediaData]:
        """Fetch user data from the platform"""
        pass
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError))
    )
    async def make_api_request(
        self, 
        method: str, 
        url: str, 
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make API request with retry logic and exponential backoff"""
        try:
            response = await self.http_client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_data
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} for {method} {url}: {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error for {method} {url}: {str(e)}")
            raise
    
    async def close(self):
        """Close HTTP client"""
        await self.http_client.aclose()