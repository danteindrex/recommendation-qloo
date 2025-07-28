from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


class SystemHealth(Base):
    __tablename__ = "system_health"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_name = Column(String(100), nullable=False)
    metrics = Column(JSON, nullable=False)
    alerts = Column(JSON, default=[])
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())