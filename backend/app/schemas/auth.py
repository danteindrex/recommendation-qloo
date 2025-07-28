from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime

from app.models.user import UserRole, SubscriptionType


class UserBase(BaseModel):
    email: EmailStr
    role: UserRole = UserRole.CONSUMER
    subscription_tier: SubscriptionType = SubscriptionType.FREE


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: str
    google_id: Optional[str] = None
    has_passkey: bool = False
    privacy_settings: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class GoogleAuthRequest(BaseModel):
    token: str


class PasskeyRegistrationRequest(BaseModel):
    email: EmailStr


class PasskeyRegistrationResponse(BaseModel):
    challenge: str
    rp: Dict[str, str]
    user: Dict[str, str]
    pubKeyCredParams: list
    timeout: int
    attestation: str
    authenticatorSelection: Dict[str, str]


class PasskeyRegistrationVerification(BaseModel):
    id: str
    rawId: str
    response: Dict[str, str]
    type: str


class PasskeyAuthenticationRequest(BaseModel):
    email: EmailStr


class PasskeyAuthenticationResponse(BaseModel):
    challenge: str
    timeout: int
    rpId: str
    allowCredentials: list
    userVerification: str


class PasskeyAuthenticationVerification(BaseModel):
    email: EmailStr
    id: str
    rawId: str
    response: Dict[str, str]
    type: str


class LogoutRequest(BaseModel):
    refresh_token: Optional[str] = None