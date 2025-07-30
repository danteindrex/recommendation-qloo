from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import httpx
import json
import base64
from jose import JWTError, jwt
from passlib.context import CryptContext
from webauthn import generate_registration_options, verify_registration_response, generate_authentication_options, verify_authentication_response
from webauthn.helpers.structs import PublicKeyCredentialDescriptor
import secrets

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User, UserRole, SubscriptionType
from app.schemas.auth import (
    UserCreate, UserResponse, TokenResponse, RefreshTokenRequest,
    GoogleAuthRequest, PasskeyRegistrationRequest, PasskeyRegistrationResponse,
    PasskeyRegistrationVerification, PasskeyAuthenticationRequest,
    PasskeyAuthenticationResponse, PasskeyAuthenticationVerification
)

router = APIRouter()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Temporary storage for WebAuthn challenges (in production, use Redis)
webauthn_challenges: Dict[str, str] = {}


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict):
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


def create_user_response(user: User) -> UserResponse:
    """Create user response from user model."""
    return UserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        subscription_tier=user.subscription_tier,
        google_id=user.google_id,
        has_passkey=bool(user.passkey_credential),
        privacy_settings=user.privacy_settings or {},
        created_at=user.created_at,
        updated_at=user.updated_at
    )


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user with email."""
    # Check if user already exists
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = User(
        email=user_data.email,
        role=user_data.role,
        subscription_tier=user_data.subscription_tier,
        privacy_settings={}
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Create tokens
    access_token = create_access_token(data={"sub": new_user.id, "email": new_user.email})
    refresh_token = create_refresh_token(data={"sub": new_user.id})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=create_user_response(new_user)
    )


@router.post("/google/auth", response_model=TokenResponse)
async def google_auth(auth_data: GoogleAuthRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate with Google OAuth."""
    try:
        # Verify Google token
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={auth_data.token}"
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Google token"
                )
            
            google_data = response.json()
            
            # Verify the token is for our app
            if google_data.get("aud") != settings.GOOGLE_CLIENT_ID:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token audience"
                )
            
            email = google_data.get("email")
            google_id = google_data.get("sub")
            
            if not email or not google_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid Google response"
                )
            
            # Check if user exists
            user = await get_user_by_email(db, email)
            
            if not user:
                # Create new user
                user = User(
                    email=email,
                    google_id=google_id,
                    role=UserRole.CONSUMER,
                    subscription_tier=SubscriptionType.FREE,
                    privacy_settings={}
                )
                db.add(user)
                await db.commit()
                await db.refresh(user)
            else:
                # Update Google ID if not set
                if not user.google_id:
                    user.google_id = google_id
                    await db.commit()
            
            # Create tokens
            access_token = create_access_token(data={"sub": user.id, "email": user.email})
            refresh_token = create_refresh_token(data={"sub": user.id})
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user=create_user_response(user)
            )
            
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Error connecting to Google services"
        )


@router.post("/passkey/register/start", response_model=PasskeyRegistrationResponse)
async def passkey_register_start(
    request: PasskeyRegistrationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Start passkey registration process."""
    # Check if user exists
    user = await get_user_by_email(db, request.email)
    if not user:
        # Create user if doesn't exist
        user = User(
            email=request.email,
            role=UserRole.CONSUMER,
            subscription_tier=SubscriptionType.FREE,
            privacy_settings={}
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    
    # Generate registration options
    options = generate_registration_options(
        rp_id=settings.RP_ID,
        rp_name=settings.RP_NAME,
        user_id=user.id.encode(),
        user_name=user.email,
        user_display_name=user.email.split('@')[0],
        attestation="none",
        authenticator_selection={
            "authenticatorAttachment": "platform",
            "userVerification": "required"
        }
    )
    
    # Store challenge for verification
    webauthn_challenges[user.id] = options.challenge
    
    return PasskeyRegistrationResponse(
        challenge=options.challenge,
        rp={"id": settings.RP_ID, "name": settings.RP_NAME},
        user={"id": user.id, "name": user.email, "displayName": user.email.split('@')[0]},
        pubKeyCredParams=[{"type": "public-key", "alg": -7}],  # ES256
        timeout=60000,
        attestation="none",
        authenticatorSelection={
            "authenticatorAttachment": "platform",
            "userVerification": "required"
        }
    )


@router.post("/passkey/register/complete", response_model=TokenResponse)
async def passkey_register_complete(
    request: PasskeyRegistrationVerification,
    db: AsyncSession = Depends(get_db)
):
    """Complete passkey registration."""
    # Get user by parsing the user id from the request
    user_id = request.id  # This should contain the user_id
    
    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get stored challenge
    challenge = webauthn_challenges.get(user.id)
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No registration in progress"
        )
    
    try:
        # Verify registration
        verification = verify_registration_response(
            credential=request.response,
            expected_challenge=challenge.encode(),
            expected_origin=settings.RP_ORIGIN,
            expected_rp_id=settings.RP_ID
        )
        
        if verification.verified:
            # Store credential
            user.passkey_credential = json.dumps({
                "id": request.id,
                "public_key": base64.b64encode(verification.credential_public_key).decode(),
                "sign_count": verification.sign_count
            })
            await db.commit()
            
            # Clean up challenge
            del webauthn_challenges[user.id]
            
            # Create tokens
            access_token = create_access_token(data={"sub": user.id, "email": user.email})
            refresh_token = create_refresh_token(data={"sub": user.id})
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user=create_user_response(user)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passkey verification failed"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/passkey/login/start", response_model=PasskeyAuthenticationResponse)
async def passkey_login_start(
    request: PasskeyAuthenticationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Start passkey login process."""
    # Get user
    user = await get_user_by_email(db, request.email)
    if not user or not user.passkey_credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No passkey registered for this email"
        )
    
    # Parse stored credential
    cred_data = json.loads(user.passkey_credential)
    
    # Generate authentication options
    options = generate_authentication_options(
        rp_id=settings.RP_ID,
        allow_credentials=[
            PublicKeyCredentialDescriptor(
                id=cred_data["id"].encode(),
                type="public-key"
            )
        ],
        user_verification="required"
    )
    
    # Store challenge for verification (include user id)
    webauthn_challenges[f"{user.id}_auth"] = options.challenge
    
    return PasskeyAuthenticationResponse(
        challenge=options.challenge,
        timeout=60000,
        rpId=settings.RP_ID,
        allowCredentials=[{
            "id": cred_data["id"],
            "type": "public-key"
        }],
        userVerification="required"
    )


@router.post("/passkey/login/complete", response_model=TokenResponse)
async def passkey_login_complete(
    request: PasskeyAuthenticationVerification,
    db: AsyncSession = Depends(get_db)
):
    """Complete passkey login."""
    # Get user by email
    user = await get_user_by_email(db, request.email)
    
    if not user or not user.passkey_credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or no passkey registered"
        )
    
    # Get stored challenge
    challenge = webauthn_challenges.get(f"{user.id}_auth")
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No login in progress"
        )
    
    try:
        # Parse stored credential
        cred_data = json.loads(user.passkey_credential)
        
        # Verify authentication
        verification = verify_authentication_response(
            credential=request.response,
            expected_challenge=challenge.encode(),
            expected_origin=settings.RP_ORIGIN,
            expected_rp_id=settings.RP_ID,
            credential_public_key=base64.b64decode(cred_data["public_key"]),
            credential_current_sign_count=cred_data["sign_count"]
        )
        
        if verification.verified:
            # Update sign count
            cred_data["sign_count"] = verification.new_sign_count
            user.passkey_credential = json.dumps(cred_data)
            await db.commit()
            
            # Clean up challenge
            del webauthn_challenges[f"{user.id}_auth"]
            
            # Create tokens
            access_token = create_access_token(data={"sub": user.id, "email": user.email})
            refresh_token = create_refresh_token(data={"sub": user.id})
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user=create_user_response(user)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Refresh JWT token."""
    try:
        # Decode refresh token
        payload = jwt.decode(request.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Get user
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Create new tokens
        access_token = create_access_token(data={"sub": user.id, "email": user.email})
        refresh_token = create_refresh_token(data={"sub": user.id})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=create_user_response(user)
        )
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.post("/logout")
async def logout(response: Response):
    """Logout user."""
    # In a real app, you might want to blacklist the token
    # For now, we'll just return success
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Successfully logged out"}