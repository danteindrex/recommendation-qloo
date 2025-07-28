from sqlalchemy import Column, String, DateTime, Enum, Text, JSON
from sqlalchemy.sql import func
from app.core.database import Base
import uuid
import enum


class UserRole(str, enum.Enum):
    CONSUMER = "consumer"
    ENTERPRISE = "enterprise"
    ADMIN = "admin"


class SubscriptionType(str, enum.Enum):
    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    passkey_credential = Column(Text, nullable=True)
    google_id = Column(String(255), nullable=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.CONSUMER)
    subscription_tier = Column(Enum(SubscriptionType), nullable=False, default=SubscriptionType.FREE)
    privacy_settings = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())