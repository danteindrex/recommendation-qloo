"""
Event store service for managing cultural intelligence events.
Implements event sourcing patterns with optimistic concurrency control.
"""

from typing import List, Optional, Dict, Any, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, asc
from sqlalchemy.exc import IntegrityError
from app.models.events import CulturalEvent, EventSnapshot, EventData
from app.core.database import get_db
import uuid
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class ConcurrencyException(Exception):
    """Raised when optimistic concurrency control fails."""
    pass


class EventStore:
    """
    Event store implementation for cultural intelligence events.
    Provides append-only storage with optimistic concurrency control.
    """
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def append_event(
        self,
        aggregate_id: uuid.UUID,
        event_type: str,
        event_data: Dict[str, Any],
        expected_version: int,
        metadata: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[uuid.UUID] = None,
        causation_id: Optional[uuid.UUID] = None,
        source_service: Optional[str] = None,
        source_version: Optional[str] = None
    ) -> CulturalEvent:
        """
        Append a new event to the event store with optimistic concurrency control.
        
        Args:
            aggregate_id: ID of the aggregate (usually user_id)
            event_type: Type of event being stored
            event_data: Event payload data
            expected_version: Expected current version for concurrency control
            metadata: Additional metadata
            correlation_id: ID for correlating related events
            causation_id: ID of the event that caused this event
            source_service: Service that generated the event
            source_version: Version of the service
            
        Returns:
            The created CulturalEvent
            
        Raises:
            ConcurrencyException: If expected_version doesn't match current version
        """
        try:
            # Check current version for optimistic concurrency control
            current_version = await self._get_current_version(aggregate_id)
            
            if current_version != expected_version:
                raise ConcurrencyException(
                    f"Expected version {expected_version}, but current version is {current_version}"
                )
            
            # Create new event
            new_version = current_version + 1
            event = CulturalEvent(
                aggregate_id=str(aggregate_id),
                event_type=event_type,
                version=new_version,
                event_data=event_data,
                event_metadata=metadata or {},
                occurred_at=datetime.utcnow(),
                correlation_id=str(correlation_id) if correlation_id else None,
                causation_id=str(causation_id) if causation_id else None,
                source_service=source_service,
                source_version=source_version
            )
            
            self.db_session.add(event)
            await self.db_session.commit()
            
            logger.info(f"Event appended: {event_type} for aggregate {aggregate_id}, version {new_version}")
            return event
            
        except IntegrityError as e:
            await self.db_session.rollback()
            raise ConcurrencyException(f"Concurrency conflict when appending event: {str(e)}")
    
    async def get_events(
        self,
        aggregate_id: uuid.UUID,
        from_version: int = 0,
        to_version: Optional[int] = None
    ) -> List[CulturalEvent]:
        """
        Retrieve events for an aggregate within a version range.
        
        Args:
            aggregate_id: ID of the aggregate
            from_version: Starting version (inclusive)
            to_version: Ending version (inclusive), None for all
            
        Returns:
            List of events ordered by version
        """
        query = select(CulturalEvent).where(
            and_(
                CulturalEvent.aggregate_id == str(aggregate_id),
                CulturalEvent.version > from_version
            )
        )
        
        if to_version is not None:
            query = query.where(CulturalEvent.version <= to_version)
        
        query = query.order_by(asc(CulturalEvent.version))
        
        result = await self.db_session.execute(query)
        events = result.scalars().all()
        
        logger.debug(f"Retrieved {len(events)} events for aggregate {aggregate_id}")
        return list(events)
    
    async def get_events_by_type(
        self,
        event_type: str,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[CulturalEvent]:
        """
        Retrieve events by type within a date range.
        
        Args:
            event_type: Type of events to retrieve
            from_date: Start date filter
            to_date: End date filter
            limit: Maximum number of events to return
            
        Returns:
            List of events ordered by occurrence time
        """
        query = select(CulturalEvent).where(CulturalEvent.event_type == event_type)
        
        if from_date:
            query = query.where(CulturalEvent.occurred_at >= from_date)
        if to_date:
            query = query.where(CulturalEvent.occurred_at <= to_date)
        
        query = query.order_by(desc(CulturalEvent.occurred_at)).limit(limit)
        
        result = await self.db_session.execute(query)
        events = result.scalars().all()
        
        logger.debug(f"Retrieved {len(events)} events of type {event_type}")
        return list(events)
    
    async def get_events_by_correlation(
        self,
        correlation_id: uuid.UUID
    ) -> List[CulturalEvent]:
        """
        Retrieve all events with the same correlation ID.
        
        Args:
            correlation_id: Correlation ID to search for
            
        Returns:
            List of correlated events ordered by occurrence time
        """
        query = select(CulturalEvent).where(
            CulturalEvent.correlation_id == str(correlation_id)
        ).order_by(asc(CulturalEvent.occurred_at))
        
        result = await self.db_session.execute(query)
        events = result.scalars().all()
        
        logger.debug(f"Retrieved {len(events)} events for correlation {correlation_id}")
        return list(events)
    
    async def save_snapshot(
        self,
        aggregate_id: uuid.UUID,
        aggregate_type: str,
        version: int,
        snapshot_data: Dict[str, Any]
    ) -> EventSnapshot:
        """
        Save a snapshot of aggregate state for performance optimization.
        
        Args:
            aggregate_id: ID of the aggregate
            aggregate_type: Type of aggregate (e.g., 'cultural_profile')
            version: Version at which snapshot was taken
            snapshot_data: Serialized aggregate state
            
        Returns:
            The created EventSnapshot
        """
        snapshot = EventSnapshot(
            aggregate_id=str(aggregate_id),
            aggregate_type=aggregate_type,
            version=version,
            snapshot_data=snapshot_data
        )
        
        self.db_session.add(snapshot)
        await self.db_session.commit()
        
        logger.info(f"Snapshot saved for aggregate {aggregate_id} at version {version}")
        return snapshot
    
    async def get_latest_snapshot(
        self,
        aggregate_id: uuid.UUID,
        aggregate_type: str
    ) -> Optional[EventSnapshot]:
        """
        Retrieve the latest snapshot for an aggregate.
        
        Args:
            aggregate_id: ID of the aggregate
            aggregate_type: Type of aggregate
            
        Returns:
            Latest snapshot or None if no snapshots exist
        """
        query = select(EventSnapshot).where(
            and_(
                EventSnapshot.aggregate_id == str(aggregate_id),
                EventSnapshot.aggregate_type == aggregate_type
            )
        ).order_by(desc(EventSnapshot.version)).limit(1)
        
        result = await self.db_session.execute(query)
        snapshot = result.scalar_one_or_none()
        
        if snapshot:
            logger.debug(f"Retrieved snapshot for aggregate {aggregate_id} at version {snapshot.version}")
        
        return snapshot
    
    async def _get_current_version(self, aggregate_id: uuid.UUID) -> int:
        """
        Get the current version of an aggregate.
        
        Args:
            aggregate_id: ID of the aggregate
            
        Returns:
            Current version number (0 if no events exist)
        """
        query = select(CulturalEvent.version).where(
            CulturalEvent.aggregate_id == str(aggregate_id)
        ).order_by(desc(CulturalEvent.version)).limit(1)
        
        result = await self.db_session.execute(query)
        version = result.scalar_one_or_none()
        
        return version or 0


class EventStoreFactory:
    """Factory for creating EventStore instances."""
    
    @staticmethod
    async def create() -> EventStore:
        """Create a new EventStore instance with database session."""
        # This would typically be injected via dependency injection
        # For now, we'll create it directly
        from app.core.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as session:
            return EventStore(session)