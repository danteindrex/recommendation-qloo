from sqlalchemy import Column, String, DateTime, Enum, JSON, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID, DATERANGE
from sqlalchemy.sql import func
from app.core.database import Base
import uuid
import enum


class EnterpriseType(str, enum.Enum):
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class AnalyticsMetricType(str, enum.Enum):
    USER_ENGAGEMENT = "user_engagement"
    CULTURAL_TRENDS = "cultural_trends"
    PLATFORM_USAGE = "platform_usage"
    DIVERSITY_METRICS = "diversity_metrics"


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), unique=True)
    subscription_tier = Column(Enum(EnterpriseType), nullable=False)
    settings = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class TeamAnalytics(Base):
    __tablename__ = "team_analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    team_name = Column(String(255), nullable=False)
    cultural_metrics = Column(JSON, nullable=False)
    diversity_scores = Column(JSON, nullable=False)
    trend_analysis = Column(JSON, nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PlatformAnalytics(Base):
    __tablename__ = "platform_analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    metric_type = Column(Enum(AnalyticsMetricType), nullable=False)
    aggregated_data = Column(JSON, nullable=False)  # No individual user data
    demographic_breakdown = Column(JSON, default={})  # Anonymized demographics
    time_period = Column(DATERANGE, nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())