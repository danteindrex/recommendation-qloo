from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.config import settings
from app.services.auth_service import auth_service
from app.schemas.auth import (
    UserCreate, UserResponse, TokenResponse, RefreshTokenRequest,
    GoogleAuthRequest, PasskeyRegistrationRequest, PasskeyRegistrationResponse,
    PasskeyRegistrationVerification, PasskeyAuthenticationRequest,
    PasskeyAuthenticationResponse, PasskeyAuthenticationVerification,
    LogoutRequest
)
from app.api.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = await auth_service.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create new user
    user = await auth_service.create_user(db, user_data.email, user_data.role)
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        role=user.role,
        subscription_tier=user.subscription_tier,
        google_id=user.google_id,
        has_passkey=bool(user.passkey_credential),
        privacy_settings=user.privacy_settings,
        created_at=user.created_at,
        updated_at=user.updated_at
    )


@router.post("/google", response_model=TokenResponse)
async def google_auth(auth_data: GoogleAuthRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate with Google OAuth."""
    user = await auth_service.authenticate_with_google(db, auth_data.token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token"
        )
    
    # Generate tokens
    access_token = await auth_service.create_access_token({"sub": str(user.id)})
    refresh_token = await auth_service.create_refresh_token({"sub": str(user.id)})
    
    user_response = UserResponse(
        id=str(user.id),
        email=user.email,
        role=user.role,
        subscription_tier=user.subscription_tier,
        google_id=user.google_id,
        has_passkey=bool(user.passkey_credential),
        privacy_settings=user.privacy_settings,
        created_at=user.created_at,
        updated_at=user.updated_at
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_response
    )


@router.post("/passkey/register/begin", response_model=PasskeyRegistrationResponse)
async def begin_passkey_registration(
    request: PasskeyRegistrationRequest, 
    db: AsyncSession = Depends(get_db)
):
    """Begin passkey registration process."""
    # Check if user exists
    user = await auth_service.get_user_by_email(db, request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Generate registration options
    options = await auth_service.generate_passkey_registration_options(
        str(user.id), user.email
    )
    
    return PasskeyRegistrationResponse(**options)


@router.post("/passkey/register/complete")
async def complete_passkey_registration(
    verification: PasskeyRegistrationVerification,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Complete passkey registration process."""
    success = await auth_service.verify_passkey_registration(
        db, str(current_user.id), verification.dict()
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passkey registration failed"
        )
    
    return {"message": "Passkey registered successfully"}


@router.post("/passkey/authenticate/begin", response_model=PasskeyAuthenticationResponse)
async def begin_passkey_authentication(
    request: PasskeyAuthenticationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Begin passkey authentication process."""
    options = await auth_service.generate_passkey_authentication_options(
        request.email, db
    )
    
    if not options:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or no passkey registered"
        )
    
    return PasskeyAuthenticationResponse(**options)


@router.post("/passkey/authenticate/complete", response_model=TokenResponse)
async def complete_passkey_authentication(
    verification: PasskeyAuthenticationVerification,
    db: AsyncSession = Depends(get_db)
):
    """Complete passkey authentication process."""
    user = await auth_service.verify_passkey_authentication(
        db, verification.email, verification.dict(exclude={"email"})
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Passkey authentication failed"
        )
    
    # Generate tokens
    access_token = await auth_service.create_access_token({"sub": str(user.id)})
    refresh_token = await auth_service.create_refresh_token({"sub": str(user.id)})
    
    user_response = UserResponse(
        id=str(user.id),
        email=user.email,
        role=user.role,
        subscription_tier=user.subscription_tier,
        google_id=user.google_id,
        has_passkey=bool(user.passkey_credential),
        privacy_settings=user.privacy_settings,
        created_at=user.created_at,
        updated_at=user.updated_at
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_response
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Refresh JWT token."""
    # Verify refresh token
    payload = await auth_service.verify_token(request.refresh_token, "refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Get user
    user = await auth_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Generate new tokens
    access_token = await auth_service.create_access_token({"sub": str(user.id)})
    new_refresh_token = await auth_service.create_refresh_token({"sub": str(user.id)})
    
    # Blacklist old refresh token
    exp_timestamp = datetime.utcfromtimestamp(payload["exp"])
    await auth_service.blacklist_token(request.refresh_token, exp_timestamp)
    
    user_response = UserResponse(
        id=str(user.id),
        email=user.email,
        role=user.role,
        subscription_tier=user.subscription_tier,
        google_id=user.google_id,
        has_passkey=bool(user.passkey_credential),
        privacy_settings=user.privacy_settings,
        created_at=user.created_at,
        updated_at=user.updated_at
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_response
    )


@router.post("/logout")
async def logout(
    request: LogoutRequest,
    current_user: User = Depends(get_current_user)
):
    """Logout user and blacklist tokens."""
    # If refresh token provided, blacklist it
    if request.refresh_token:
        payload = await auth_service.verify_token(request.refresh_token, "refresh")
        if payload:
            exp_timestamp = datetime.utcfromtimestamp(payload["exp"])
            await auth_service.blacklist_token(request.refresh_token, exp_timestamp)
    
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        role=current_user.role,
        subscription_tier=current_user.subscription_tier,
        google_id=current_user.google_id,
        has_passkey=bool(current_user.passkey_credential),
        privacy_settings=current_user.privacy_settings,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )