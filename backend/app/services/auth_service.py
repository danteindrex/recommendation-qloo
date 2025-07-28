from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from webauthn import generate_registration_options, verify_registration_response, generate_authentication_options, verify_authentication_response
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    UserVerificationRequirement,
    RegistrationCredential,
    AuthenticationCredential,
    PublicKeyCredentialDescriptor,
    AuthenticatorTransport
)
from google.auth.transport import requests
from google.oauth2 import id_token
import json
import base64
import secrets
import redis.asyncio as redis

from app.core.config import settings
from app.models.user import User, UserRole
from app.core.database import get_redis


class AuthService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
    async def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    async def create_refresh_token(self, data: dict):
        """Create JWT refresh token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    async def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """Verify JWT token."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            if payload.get("type") != token_type:
                return None
            return payload
        except JWTError:
            return None
    
    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email."""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def get_user_by_id(self, db: AsyncSession, user_id: str) -> Optional[User]:
        """Get user by ID."""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def get_user_by_google_id(self, db: AsyncSession, google_id: str) -> Optional[User]:
        """Get user by Google ID."""
        result = await db.execute(select(User).where(User.google_id == google_id))
        return result.scalar_one_or_none()
    
    async def create_user(self, db: AsyncSession, email: str, role: UserRole = UserRole.CONSUMER, google_id: Optional[str] = None) -> User:
        """Create new user."""
        user = User(
            email=email,
            role=role,
            google_id=google_id
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    
    # Passkey/WebAuthn methods
    async def generate_passkey_registration_options(self, user_id: str, email: str) -> dict:
        """Generate passkey registration options."""
        redis_client = await get_redis()
        
        # Generate challenge
        challenge = secrets.token_bytes(32)
        
        # Store challenge in Redis with expiration
        await redis_client.setex(
            f"passkey_challenge:{user_id}",
            300,  # 5 minutes
            base64.b64encode(challenge).decode()
        )
        
        user_id_bytes = user_id.encode('utf-8') if isinstance(user_id, str) else user_id
        
        options = generate_registration_options(
            rp_id=settings.RP_ID,
            rp_name=settings.RP_NAME,
            user_id=user_id_bytes,
            user_name=email,
            user_display_name=email,
            challenge=challenge,
            authenticator_selection=AuthenticatorSelectionCriteria(
                user_verification=UserVerificationRequirement.REQUIRED
            )
        )
        
        return {
            "challenge": base64.b64encode(options.challenge).decode(),
            "rp": {"id": options.rp.id, "name": options.rp.name},
            "user": {
                "id": base64.b64encode(options.user.id).decode(),
                "name": options.user.name,
                "displayName": options.user.display_name
            },
            "pubKeyCredParams": [
                {"type": param.type, "alg": param.alg} 
                for param in options.pub_key_cred_params
            ],
            "timeout": options.timeout,
            "attestation": options.attestation,
            "authenticatorSelection": {
                "userVerification": options.authenticator_selection.user_verification
            }
        }
    
    async def verify_passkey_registration(self, db: AsyncSession, user_id: str, credential_data: dict) -> bool:
        """Verify passkey registration response."""
        redis_client = await get_redis()
        
        # Get stored challenge
        stored_challenge = await redis_client.get(f"passkey_challenge:{user_id}")
        if not stored_challenge:
            return False
        
        challenge = base64.b64decode(stored_challenge)
        
        try:
            # Create RegistrationCredential object
            credential = RegistrationCredential(
                id=credential_data["id"],
                raw_id=base64.b64decode(credential_data["rawId"]),
                response={
                    "client_data_json": base64.b64decode(credential_data["response"]["clientDataJSON"]),
                    "attestation_object": base64.b64decode(credential_data["response"]["attestationObject"])
                },
                type=credential_data["type"]
            )
            
            verification = verify_registration_response(
                credential=credential,
                expected_challenge=challenge,
                expected_origin=settings.RP_ORIGIN,
                expected_rp_id=settings.RP_ID
            )
            
            if verification.verified:
                # Store credential in database
                user = await self.get_user_by_id(db, user_id)
                if user:
                    credential_json = {
                        "id": credential_data["id"],
                        "public_key": base64.b64encode(verification.credential_public_key).decode(),
                        "sign_count": verification.sign_count,
                        "credential_id": base64.b64encode(verification.credential_id).decode()
                    }
                    user.passkey_credential = json.dumps(credential_json)
                    await db.commit()
                
                # Clean up challenge
                await redis_client.delete(f"passkey_challenge:{user_id}")
                return True
            
        except Exception as e:
            print(f"Passkey registration verification failed: {e}")
            return False
        
        return False
    
    async def generate_passkey_authentication_options(self, email: str, db: AsyncSession) -> Optional[dict]:
        """Generate passkey authentication options."""
        user = await self.get_user_by_email(db, email)
        if not user or not user.passkey_credential:
            return None
        
        redis_client = await get_redis()
        
        # Generate challenge
        challenge = secrets.token_bytes(32)
        
        # Store challenge in Redis
        await redis_client.setex(
            f"passkey_auth_challenge:{user.id}",
            300,  # 5 minutes
            base64.b64encode(challenge).decode()
        )
        
        # Parse stored credential
        credential_data = json.loads(user.passkey_credential)
        
        options = generate_authentication_options(
            rp_id=settings.RP_ID,
            challenge=challenge,
            allow_credentials=[
                PublicKeyCredentialDescriptor(
                    id=base64.b64decode(credential_data["credential_id"]),
                    type="public-key",
                    transports=[AuthenticatorTransport.INTERNAL]
                )
            ],
            user_verification=UserVerificationRequirement.REQUIRED
        )
        
        return {
            "challenge": base64.b64encode(options.challenge).decode(),
            "timeout": options.timeout,
            "rpId": options.rp_id,
            "allowCredentials": [
                {
                    "id": base64.b64encode(cred.id).decode(),
                    "type": cred.type,
                    "transports": [t.value for t in cred.transports] if cred.transports else []
                }
                for cred in options.allow_credentials
            ],
            "userVerification": options.user_verification
        }
    
    async def verify_passkey_authentication(self, db: AsyncSession, email: str, credential_data: dict) -> Optional[User]:
        """Verify passkey authentication response."""
        user = await self.get_user_by_email(db, email)
        if not user or not user.passkey_credential:
            return None
        
        redis_client = await get_redis()
        
        # Get stored challenge
        stored_challenge = await redis_client.get(f"passkey_auth_challenge:{user.id}")
        if not stored_challenge:
            return None
        
        challenge = base64.b64decode(stored_challenge)
        
        try:
            # Parse stored credential
            stored_cred = json.loads(user.passkey_credential)
            
            # Create AuthenticationCredential object
            credential = AuthenticationCredential(
                id=credential_data["id"],
                raw_id=base64.b64decode(credential_data["rawId"]),
                response={
                    "client_data_json": base64.b64decode(credential_data["response"]["clientDataJSON"]),
                    "authenticator_data": base64.b64decode(credential_data["response"]["authenticatorData"]),
                    "signature": base64.b64decode(credential_data["response"]["signature"])
                },
                type=credential_data["type"]
            )
            
            verification = verify_authentication_response(
                credential=credential,
                expected_challenge=challenge,
                expected_origin=settings.RP_ORIGIN,
                expected_rp_id=settings.RP_ID,
                credential_public_key=base64.b64decode(stored_cred["public_key"]),
                credential_current_sign_count=stored_cred["sign_count"]
            )
            
            if verification.verified:
                # Update sign count
                stored_cred["sign_count"] = verification.new_sign_count
                user.passkey_credential = json.dumps(stored_cred)
                await db.commit()
                
                # Clean up challenge
                await redis_client.delete(f"passkey_auth_challenge:{user.id}")
                return user
            
        except Exception as e:
            print(f"Passkey authentication verification failed: {e}")
            return None
        
        return None
    
    # Google OAuth methods
    async def verify_google_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify Google OAuth token."""
        try:
            idinfo = id_token.verify_oauth2_token(
                token, 
                requests.Request(), 
                settings.GOOGLE_CLIENT_ID
            )
            
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                return None
            
            return idinfo
        except ValueError:
            return None
    
    async def authenticate_with_google(self, db: AsyncSession, token: str) -> Optional[User]:
        """Authenticate user with Google OAuth token."""
        google_data = await self.verify_google_token(token)
        if not google_data:
            return None
        
        google_id = google_data['sub']
        email = google_data['email']
        
        # Check if user exists
        user = await self.get_user_by_google_id(db, google_id)
        if not user:
            # Check if user exists with same email
            user = await self.get_user_by_email(db, email)
            if user:
                # Link Google account to existing user
                user.google_id = google_id
                await db.commit()
            else:
                # Create new user
                user = await self.create_user(db, email, google_id=google_id)
        
        return user
    
    async def blacklist_token(self, token: str, expires_at: datetime):
        """Add token to blacklist."""
        redis_client = await get_redis()
        ttl = int((expires_at - datetime.utcnow()).total_seconds())
        if ttl > 0:
            await redis_client.setex(f"blacklist:{token}", ttl, "1")
    
    async def is_token_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted."""
        redis_client = await get_redis()
        result = await redis_client.get(f"blacklist:{token}")
        return result is not None


# Global auth service instance
auth_service = AuthService()