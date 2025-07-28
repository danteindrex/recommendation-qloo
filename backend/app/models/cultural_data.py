from sqlalchemy import Column, String, DateTime, Enum, Text, JSON, ForeignKey, DECIMAL, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
import enum


class SocialPlatform(str, enum.Enum):
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    SPOTIFY = "spotify"


class CulturalDataType(str, enum.Enum):
    POST = "post"
    STORY = "story"
    MUSIC = "music"
    INTERACTION = "interaction"


class ConnectionStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"


class CulturalProfile(Base):
    __tablename__ = "cultural_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    diversity_score = Column(DECIMAL(5, 2), default=0.0)
    evolution_data = Column(JSON, default={})
    influence_network = Column(JSON, default={})
    blind_spots = Column(JSON, default=[])
    last_analysis = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class SocialConnection(Base):
    __tablename__ = "social_connections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    platform = Column(Enum(SocialPlatform), nullable=False)
    platform_user_id = Column(String(255), nullable=False)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text)
    token_expires_at = Column(DateTime(timezone=True))
    connection_status = Column(Enum(ConnectionStatus), default=ConnectionStatus.ACTIVE)
    last_sync = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CulturalDataPoint(Base):
    __tablename__ = "cultural_data_points"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    platform = Column(Enum(SocialPlatform), nullable=False)
    data_type = Column(Enum(CulturalDataType), nullable=False)
    content = Column(JSON, nullable=False)
    cultural_signals = Column(JSON, default={})
    confidence_score = Column(DECIMAL(5, 2), default=0.0)
    processed_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())