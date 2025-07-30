from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.services.auth_service import auth_service
from app.models.user import User, UserRole


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not credentials:
        raise credentials_exception
    
    token = credentials.credentials
    
    # Check if token is blacklisted
    if await auth_service.is_token_blacklisted(token):
        raise credentials_exception
    
    # Verify token
    payload = await auth_service.verify_token(token, "access")
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # Get user from database
    user = await auth_service.get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user."""
    return current_user


def require_role(required_role: UserRole):
    """Dependency factory for role-based access control."""
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role.value}"
            )
        return current_user
    return role_checker


def require_roles(*required_roles: UserRole):
    """Dependency factory for multiple role-based access control."""
    async def roles_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in required_roles:
            roles_str = ", ".join([role.value for role in required_roles])
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {roles_str}"
            )
        return current_user
    return roles_checker


async def get_current_user_websocket(
    token: str,
    db: AsyncSession
) -> Optional[User]:
    """Get current authenticated user from JWT token for WebSocket connections."""
    try:
        # Check if token is blacklisted
        if await auth_service.is_token_blacklisted(token):
            return None
        
        # Verify token
        payload = await auth_service.verify_token(token, "access")
        if payload is None:
            return None
        
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        
        # Get user from database
        user = await auth_service.get_user_by_id(db, user_id)
        return user
        
    except Exception:
        return None


# Convenience dependencies for common role checks
require_consumer = require_role(UserRole.CONSUMER)
require_enterprise = require_role(UserRole.ENTERPRISE)
require_admin = require_role(UserRole.ADMIN)
require_enterprise_or_admin = require_roles(UserRole.ENTERPRISE, UserRole.ADMIN)
