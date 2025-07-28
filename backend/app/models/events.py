"""
Event sourcing models and infrastructure for cultural intelligence platform.
Implements immutable event store for cultural data changes and analysis.
"""

from sqlalchemy import Column, String, DateTime, Text, JSON, Integer, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
import uuid
import enum
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel
import os

# Use String for UUID in SQLite (for tests), UUID for PostgreSQL (production)
def get_uuid_column():
    if "sqlite" in os.environ.get("DATABASE_URL", ""):
        return String(36)
    return UUID(as_uuid=True)


class EventType(str, enum.Enum):
    """Types of cultural events that can be stored."""
    SOCIAL_DATA_INGESTED = "social_data_ingested"
    CULTURAL_PATTERN_DETECTED = "cultural_pattern_detected"
    DIVERSITY_SCORE_UPDATED = "diversity_score_updated"
    RECOMMENDATION_GENERATED = "recommendation_generated"
    CULTURAL_MILESTONE_REACHED = "cultural_milestone_reached"
    INFLUENCE_NETWORK_UPDATED = "influence_network_updated"
    BLIND_SPOT_IDENTIFIED = "blind_spot_identified"
    PREDICTION_MADE = "prediction_made"
    USER_INTERACTION = "user_interaction"


class CulturalEvent(Base):
    """
    Immutable event store for all cultural intelligence events.
    Supports event sourcing pattern for complete audit trail and replay capability.
    """
    __tablename__ = "cultural_events"

    # Event identification
    event_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    aggregate_id = Column(String(36), nullable=False, index=True)  # Usually user_id
    event_type = Column(String(100), nullable=False, index=True)
    
    # Event versioning and ordering
    version = Column(Integer, nullable=False)
    sequence_number = Column(Integer, nullable=True, autoincrement=True)
    
    # Event data
    event_data = Column(JSON, nullable=False)
    event_metadata = Column(JSON, default={})
    
    # Timestamps
    occurred_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Correlation and causation tracking
    correlation_id = Column(String(36), index=True)
    causation_id = Column(String(36), index=True)
    
    # Source information
    source_service = Column(String(100))
    source_version = Column(String(50))

    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_aggregate_version', 'aggregate_id', 'version'),
        Index('idx_event_type_occurred', 'event_type', 'occurred_at'),
        Index('idx_correlation_id', 'correlation_id'),
        Index('idx_sequence_occurred', 'sequence_number', 'occurred_at'),
    )


class EventSnapshot(Base):
    """
    Snapshots of aggregate state for performance optimization.
    Reduces need to replay all events from beginning.
    """
    __tablename__ = "event_snapshots"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    aggregate_id = Column(String(36), nullable=False, index=True)
    aggregate_type = Column(String(100), nullable=False)
    version = Column(Integer, nullable=False)
    snapshot_data = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_aggregate_snapshot', 'aggregate_id', 'version'),
    )


# Pydantic models for event handling
class EventData(BaseModel):
    """Base event data structure."""
    event_id: uuid.UUID
    aggregate_id: uuid.UUID
    event_type: str
    version: int
    event_data: Dict[str, Any]
    event_metadata: Dict[str, Any] = {}
    occurred_at: datetime
    correlation_id: Optional[uuid.UUID] = None
    causation_id: Optional[uuid.UUID] = None
    source_service: Optional[str] = None
    source_version: Optional[str] = None


class SocialDataIngestedEvent(BaseModel):
    """Event for when social media data is ingested."""
    platform: str
    data_type: str
    content: Dict[str, Any]
    cultural_signals: Dict[str, Any]
    confidence_score: float


class CulturalPatternDetectedEvent(BaseModel):
    """Event for when a cultural pattern is detected."""
    pattern_type: str
    pattern_data: Dict[str, Any]
    confidence: float
    platforms: list[str]
    timeframe: Dict[str, Any]


class DiversityScoreUpdatedEvent(BaseModel):
    """Event for when diversity score is updated."""
    old_score: float
    new_score: float
    contributing_factors: list[str]
    analysis_data: Dict[str, Any]


class CulturalMilestoneReachedEvent(BaseModel):
    """Event for when a cultural milestone is reached."""
    milestone_type: str
    cultural_shift: float
    confidence: float
    platforms: list[str]
    description: str


class RecommendationGeneratedEvent(BaseModel):
    """Event for when a recommendation is generated."""
    recommendation_type: str
    title: str
    description: str
    confidence_score: float
    cultural_category: str
    external_data: Dict[str, Any]