from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any
from app.core.database import get_db
from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.models.cultural_data import SocialPlatform, SocialConnection, ConnectionStatus
from app.services.social_media_service import SocialMediaService
from app.integrations.social_media.base import OAuthCredentials
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["social-media"])


@router.get("/oauth/{platform}/url")
async def get_oauth_url(
    platform: SocialPlatform,
    redirect_uri: str,
    state: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """Get OAuth authorization URL for a social media platform"""
    try:
        service = SocialMediaService()
        oauth_url = await service.get_oauth_url(platform, redirect_uri, state)
        
        return {
            "oauth_url": oauth_url,
            "platform": platform.value,
            "state": state
        }
    except Exception as e:
        logger.error(f"Error generating OAuth URL for {platform}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate OAuth URL for {platform}"
        )


@router.post("/oauth/{platform}/callback")
async def oauth_callback(
    platform: SocialPlatform,
    code: str,
    redirect_uri: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Handle OAuth callback and store connection"""
    try:
        service = SocialMediaService()
        
        # Exchange code for token
        credentials = await service.exchange_code_for_token(platform, code, redirect_uri)
        
        # Check if connection already exists
        existing_connection = await db.execute(
            select(SocialConnection).where(
                SocialConnection.user_id == current_user.id,
                SocialConnection.platform == platform
            )
        )
        connection = existing_connection.scalar_one_or_none()
        
        if connection:
            # Update existing connection
            connection.access_token = credentials.access_token
            connection.refresh_token = credentials.refresh_token
            connection.token_expires_at = credentials.expires_at
            connection.platform_user_id = credentials.platform_user_id
            connection.connection_status = ConnectionStatus.ACTIVE
            connection.last_sync = datetime.now(timezone.utc)
        else:
            # Create new connection
            connection = SocialConnection(
                user_id=current_user.id,
                platform=platform,
                platform_user_id=credentials.platform_user_id,
                access_token=credentials.access_token,
                refresh_token=credentials.refresh_token,
                token_expires_at=credentials.expires_at,
                connection_status=ConnectionStatus.ACTIVE,
                last_sync=datetime.now(timezone.utc)
            )
            db.add(connection)
        
        await db.commit()
        
        return {
            "message": f"Successfully connected {platform.value} account",
            "platform": platform.value,
            "platform_user_id": credentials.platform_user_id,
            "connected_at": connection.last_sync.isoformat()
        }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error handling OAuth callback for {platform}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect {platform} account"
        )


@router.post("/sync/{platform}")
async def sync_platform_data(
    platform: SocialPlatform,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Sync data from a connected social media platform"""
    try:
        # Get user's connection for this platform
        result = await db.execute(
            select(SocialConnection).where(
                SocialConnection.user_id == current_user.id,
                SocialConnection.platform == platform,
                SocialConnection.connection_status == ConnectionStatus.ACTIVE
            )
        )
        connection = result.scalar_one_or_none()
        
        if not connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No active {platform} connection found"
            )
        
        # Check if token needs refresh
        if connection.token_expires_at and connection.token_expires_at <= datetime.now(timezone.utc):
            if not connection.refresh_token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"{platform} token expired and no refresh token available"
                )
            
            # Refresh token
            service = SocialMediaService()
            new_credentials = await service.refresh_access_token(platform, connection.refresh_token)
            
            connection.access_token = new_credentials.access_token
            connection.refresh_token = new_credentials.refresh_token or connection.refresh_token
            connection.token_expires_at = new_credentials.expires_at
            await db.commit()
        
        # Create credentials object
        credentials = OAuthCredentials(
            access_token=connection.access_token,
            refresh_token=connection.refresh_token,
            expires_at=connection.token_expires_at,
            platform_user_id=connection.platform_user_id
        )
        
        # Ingest data
        service = SocialMediaService()
        cultural_data_points = await service.ingest_user_data(
            db=db,
            user_id=str(current_user.id),
            platform=platform,
            credentials=credentials
        )
        
        # Update last sync time
        connection.last_sync = datetime.now(timezone.utc)
        await db.commit()
        
        return {
            "message": f"Successfully synced {len(cultural_data_points)} data points from {platform.value}",
            "platform": platform.value,
            "data_points_count": len(cultural_data_points),
            "last_sync": connection.last_sync.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error syncing data from {platform}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync data from {platform}"
        )


@router.get("/connections")
async def get_user_connections(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get user's social media connections"""
    try:
        result = await db.execute(
            select(SocialConnection).where(
                SocialConnection.user_id == current_user.id
            )
        )
        connections = result.scalars().all()
        
        connection_data = []
        for conn in connections:
            connection_data.append({
                "platform": conn.platform.value,
                "platform_user_id": conn.platform_user_id,
                "status": conn.connection_status.value,
                "last_sync": conn.last_sync.isoformat() if conn.last_sync else None,
                "token_expires_at": conn.token_expires_at.isoformat() if conn.token_expires_at else None,
                "connected_at": conn.created_at.isoformat()
            })
        
        return {
            "connections": connection_data,
            "total_connections": len(connection_data)
        }
        
    except Exception as e:
        logger.error(f"Error fetching user connections: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch social media connections"
        )


@router.delete("/connections/{platform}")
async def disconnect_platform(
    platform: SocialPlatform,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """Disconnect a social media platform"""
    try:
        result = await db.execute(
            select(SocialConnection).where(
                SocialConnection.user_id == current_user.id,
                SocialConnection.platform == platform
            )
        )
        connection = result.scalar_one_or_none()
        
        if not connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No {platform} connection found"
            )
        
        # Update status to inactive instead of deleting
        connection.connection_status = ConnectionStatus.INACTIVE
        await db.commit()
        
        return {
            "message": f"Successfully disconnected {platform.value} account",
            "platform": platform.value
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error disconnecting {platform}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disconnect {platform} account"
        )