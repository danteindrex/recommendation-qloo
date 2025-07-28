"""
Event projection services for creating optimized read models from events.
Implements different views for cultural intelligence data visualization.
"""

from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert, delete, and_
from app.models.events import CulturalEvent, EventType
from app.models.cultural_data import CulturalProfile, CulturalDataPoint
from app.services.event_store import EventStore
import uuid
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)


class ProjectionService(ABC):
    """Base class for all projection services."""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    @abstractmethod
    async def project_event(self, event: CulturalEvent) -> None:
        """Project an event to update the read model."""
        pass
    
    @abstractmethod
    async def rebuild_projection(self, aggregate_id: uuid.UUID) -> None:
        """Rebuild projection from all events for an aggregate."""
        pass


class CulturalProfileProjection(ProjectionService):
    """Projection service for cultural profile read model."""
    
    async def project_event(self, event: CulturalEvent) -> None:
        """Project event to update cultural profile."""
        if event.event_type == EventType.SOCIAL_DATA_INGESTED:
            await self._handle_social_data_ingested(event)
        elif event.event_type == EventType.DIVERSITY_SCORE_UPDATED:
            await self._handle_diversity_score_updated(event)
        elif event.event_type == EventType.CULTURAL_PATTERN_DETECTED:
            await self._handle_cultural_pattern_detected(event)
        elif event.event_type == EventType.INFLUENCE_NETWORK_UPDATED:
            await self._handle_influence_network_updated(event)
        elif event.event_type == EventType.BLIND_SPOT_IDENTIFIED:
            await self._handle_blind_spot_identified(event)
    
    async def rebuild_projection(self, aggregate_id: uuid.UUID) -> None:
        """Rebuild cultural profile projection from all events."""
        event_store = EventStore(self.db_session)
        events = await event_store.get_events(aggregate_id)
        
        # Clear existing projection
        await self._clear_projection(aggregate_id)
        
        # Replay all events
        for event in events:
            await self.project_event(event)
    
    async def _handle_social_data_ingested(self, event: CulturalEvent) -> None:
        """Handle social data ingestion event."""
        # Ensure cultural profile exists
        await self._ensure_profile_exists(event.aggregate_id)
        
        # Update last analysis timestamp
        stmt = update(CulturalProfile).where(
            CulturalProfile.user_id == str(event.aggregate_id)
        ).values(
            last_analysis=event.occurred_at,
            updated_at=datetime.utcnow()
        )
        await self.db_session.execute(stmt)
        await self.db_session.commit()
    
    async def _handle_diversity_score_updated(self, event: CulturalEvent) -> None:
        """Handle diversity score update event."""
        new_score = event.event_data.get("new_score", 0.0)
        
        stmt = update(CulturalProfile).where(
            CulturalProfile.user_id == str(event.aggregate_id)
        ).values(
            diversity_score=new_score,
            updated_at=datetime.utcnow()
        )
        await self.db_session.execute(stmt)
        await self.db_session.commit()
    
    async def _handle_cultural_pattern_detected(self, event: CulturalEvent) -> None:
        """Handle cultural pattern detection event."""
        # Update evolution data with new pattern
        pattern_data = event.event_data
        
        # Get current evolution data
        stmt = select(CulturalProfile.evolution_data).where(
            CulturalProfile.user_id == str(event.aggregate_id)
        )
        result = await self.db_session.execute(stmt)
        current_data = result.scalar_one_or_none() or {}
        
        # Add new pattern to evolution data
        if "patterns" not in current_data:
            current_data["patterns"] = []
        
        current_data["patterns"].append({
            "timestamp": event.occurred_at.isoformat(),
            "pattern_type": pattern_data.get("pattern_type"),
            "confidence": pattern_data.get("confidence"),
            "platforms": pattern_data.get("platforms", [])
        })
        
        # Update profile
        stmt = update(CulturalProfile).where(
            CulturalProfile.user_id == str(event.aggregate_id)
        ).values(
            evolution_data=current_data,
            updated_at=datetime.utcnow()
        )
        await self.db_session.execute(stmt)
        await self.db_session.commit()
    
    async def _handle_influence_network_updated(self, event: CulturalEvent) -> None:
        """Handle influence network update event."""
        influence_data = event.event_data
        
        stmt = update(CulturalProfile).where(
            CulturalProfile.user_id == str(event.aggregate_id)
        ).values(
            influence_network=influence_data,
            updated_at=datetime.utcnow()
        )
        await self.db_session.execute(stmt)
        await self.db_session.commit()
    
    async def _handle_blind_spot_identified(self, event: CulturalEvent) -> None:
        """Handle blind spot identification event."""
        blind_spot_data = event.event_data
        
        # Get current blind spots
        stmt = select(CulturalProfile.blind_spots).where(
            CulturalProfile.user_id == str(event.aggregate_id)
        )
        result = await self.db_session.execute(stmt)
        current_blind_spots = result.scalar_one_or_none() or []
        
        # Add new blind spot
        current_blind_spots.append({
            "identified_at": event.occurred_at.isoformat(),
            "category": blind_spot_data.get("category"),
            "description": blind_spot_data.get("description"),
            "confidence": blind_spot_data.get("confidence")
        })
        
        # Update profile
        stmt = update(CulturalProfile).where(
            CulturalProfile.user_id == str(event.aggregate_id)
        ).values(
            blind_spots=current_blind_spots,
            updated_at=datetime.utcnow()
        )
        await self.db_session.execute(stmt)
        await self.db_session.commit()
    
    async def _ensure_profile_exists(self, user_id: str) -> None:
        """Ensure cultural profile exists for user."""
        stmt = select(CulturalProfile).where(CulturalProfile.user_id == user_id)
        result = await self.db_session.execute(stmt)
        profile = result.scalar_one_or_none()
        
        if not profile:
            new_profile = CulturalProfile(
                user_id=user_id,
                diversity_score=0.0,
                evolution_data={},
                influence_network={},
                blind_spots=[]
            )
            self.db_session.add(new_profile)
            await self.db_session.commit()
    
    async def _clear_projection(self, user_id: uuid.UUID) -> None:
        """Clear existing projection for rebuild."""
        stmt = delete(CulturalProfile).where(CulturalProfile.user_id == str(user_id))
        await self.db_session.execute(stmt)
        await self.db_session.commit()


class CulturalTimelineProjection(ProjectionService):
    """Projection service for cultural evolution timeline view."""
    
    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session)
        self.timeline_cache = {}  # In-memory cache for timeline data
    
    async def project_event(self, event: CulturalEvent) -> None:
        """Project event to update timeline view."""
        if event.event_type == EventType.CULTURAL_MILESTONE_REACHED:
            await self._handle_milestone_reached(event)
        elif event.event_type == EventType.CULTURAL_PATTERN_DETECTED:
            await self._handle_pattern_detected(event)
        elif event.event_type == EventType.DIVERSITY_SCORE_UPDATED:
            await self._handle_diversity_change(event)
    
    async def rebuild_projection(self, aggregate_id: uuid.UUID) -> None:
        """Rebuild timeline projection from all events."""
        event_store = EventStore(self.db_session)
        events = await event_store.get_events(aggregate_id)
        
        # Clear cache for this user
        self.timeline_cache[str(aggregate_id)] = []
        
        # Replay timeline-relevant events
        timeline_events = [
            e for e in events 
            if e.event_type in [
                EventType.CULTURAL_MILESTONE_REACHED,
                EventType.CULTURAL_PATTERN_DETECTED,
                EventType.DIVERSITY_SCORE_UPDATED
            ]
        ]
        
        for event in timeline_events:
            await self.project_event(event)
    
    async def get_timeline_data(self, user_id: uuid.UUID) -> List[Dict[str, Any]]:
        """Get timeline data for 3D visualization."""
        user_key = str(user_id)
        
        if user_key not in self.timeline_cache:
            await self.rebuild_projection(user_id)
        
        return self.timeline_cache.get(user_key, [])
    
    async def _handle_milestone_reached(self, event: CulturalEvent) -> None:
        """Handle milestone reached event for timeline."""
        user_key = str(event.aggregate_id)
        
        if user_key not in self.timeline_cache:
            self.timeline_cache[user_key] = []
        
        milestone_data = {
            "type": "milestone",
            "timestamp": event.occurred_at.isoformat(),
            "milestone_type": event.event_data.get("milestone_type"),
            "cultural_shift": event.event_data.get("cultural_shift"),
            "confidence": event.event_data.get("confidence"),
            "platforms": event.event_data.get("platforms", []),
            "description": event.event_data.get("description")
        }
        
        self.timeline_cache[user_key].append(milestone_data)
        self.timeline_cache[user_key].sort(key=lambda x: x["timestamp"])
    
    async def _handle_pattern_detected(self, event: CulturalEvent) -> None:
        """Handle pattern detection for timeline."""
        user_key = str(event.aggregate_id)
        
        if user_key not in self.timeline_cache:
            self.timeline_cache[user_key] = []
        
        pattern_data = {
            "type": "pattern",
            "timestamp": event.occurred_at.isoformat(),
            "pattern_type": event.event_data.get("pattern_type"),
            "confidence": event.event_data.get("confidence"),
            "platforms": event.event_data.get("platforms", [])
        }
        
        self.timeline_cache[user_key].append(pattern_data)
        self.timeline_cache[user_key].sort(key=lambda x: x["timestamp"])
    
    async def _handle_diversity_change(self, event: CulturalEvent) -> None:
        """Handle diversity score change for timeline."""
        user_key = str(event.aggregate_id)
        
        if user_key not in self.timeline_cache:
            self.timeline_cache[user_key] = []
        
        diversity_data = {
            "type": "diversity_change",
            "timestamp": event.occurred_at.isoformat(),
            "old_score": event.event_data.get("old_score"),
            "new_score": event.event_data.get("new_score"),
            "contributing_factors": event.event_data.get("contributing_factors", [])
        }
        
        self.timeline_cache[user_key].append(diversity_data)
        self.timeline_cache[user_key].sort(key=lambda x: x["timestamp"])


class InfluenceNetworkProjection(ProjectionService):
    """Projection service for cultural influence network view."""
    
    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session)
        self.network_cache = {}  # In-memory cache for network data
    
    async def project_event(self, event: CulturalEvent) -> None:
        """Project event to update influence network view."""
        if event.event_type == EventType.INFLUENCE_NETWORK_UPDATED:
            await self._handle_network_updated(event)
        elif event.event_type == EventType.CULTURAL_PATTERN_DETECTED:
            await self._handle_pattern_influence(event)
    
    async def rebuild_projection(self, aggregate_id: uuid.UUID) -> None:
        """Rebuild influence network projection from all events."""
        event_store = EventStore(self.db_session)
        events = await event_store.get_events(aggregate_id)
        
        # Clear cache for this user
        self.network_cache[str(aggregate_id)] = {
            "nodes": [],
            "edges": [],
            "last_updated": None
        }
        
        # Replay network-relevant events
        network_events = [
            e for e in events 
            if e.event_type in [
                EventType.INFLUENCE_NETWORK_UPDATED,
                EventType.CULTURAL_PATTERN_DETECTED
            ]
        ]
        
        for event in network_events:
            await self.project_event(event)
    
    async def get_network_data(self, user_id: uuid.UUID) -> Dict[str, Any]:
        """Get influence network data for 3D visualization."""
        user_key = str(user_id)
        
        if user_key not in self.network_cache:
            await self.rebuild_projection(user_id)
        
        return self.network_cache.get(user_key, {
            "nodes": [],
            "edges": [],
            "last_updated": None
        })
    
    async def _handle_network_updated(self, event: CulturalEvent) -> None:
        """Handle influence network update event."""
        user_key = str(event.aggregate_id)
        
        network_data = event.event_data
        self.network_cache[user_key] = {
            "nodes": network_data.get("nodes", []),
            "edges": network_data.get("edges", []),
            "last_updated": event.occurred_at.isoformat()
        }
    
    async def _handle_pattern_influence(self, event: CulturalEvent) -> None:
        """Handle pattern detection for influence network updates."""
        user_key = str(event.aggregate_id)
        
        if user_key not in self.network_cache:
            self.network_cache[user_key] = {
                "nodes": [],
                "edges": [],
                "last_updated": None
            }
        
        # Add pattern as influence node
        pattern_data = event.event_data
        pattern_node = {
            "id": f"pattern_{event.event_id}",
            "type": "pattern",
            "label": pattern_data.get("pattern_type"),
            "confidence": pattern_data.get("confidence"),
            "platforms": pattern_data.get("platforms", []),
            "timestamp": event.occurred_at.isoformat()
        }
        
        self.network_cache[user_key]["nodes"].append(pattern_node)
        self.network_cache[user_key]["last_updated"] = event.occurred_at.isoformat()


class ProjectionManager:
    """Manages all projection services and coordinates updates."""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.projections = [
            CulturalProfileProjection(db_session),
            CulturalTimelineProjection(db_session),
            InfluenceNetworkProjection(db_session)
        ]
    
    async def project_event(self, event: CulturalEvent) -> None:
        """Project event to all relevant projections."""
        for projection in self.projections:
            try:
                await projection.project_event(event)
            except Exception as e:
                logger.error(f"Error projecting event {event.event_id} to {type(projection).__name__}: {str(e)}")
                # Continue with other projections even if one fails
    
    async def rebuild_all_projections(self, aggregate_id: uuid.UUID) -> None:
        """Rebuild all projections for an aggregate."""
        for projection in self.projections:
            try:
                await projection.rebuild_projection(aggregate_id)
                logger.info(f"Rebuilt {type(projection).__name__} for aggregate {aggregate_id}")
            except Exception as e:
                logger.error(f"Error rebuilding {type(projection).__name__} for aggregate {aggregate_id}: {str(e)}")
    
    async def get_cultural_profile_view(self, user_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """Get cultural profile view data."""
        stmt = select(CulturalProfile).where(CulturalProfile.user_id == str(user_id))
        result = await self.db_session.execute(stmt)
        profile = result.scalar_one_or_none()
        
        if not profile:
            return None
        
        return {
            "user_id": str(profile.user_id),
            "diversity_score": float(profile.diversity_score),
            "evolution_data": profile.evolution_data,
            "influence_network": profile.influence_network,
            "blind_spots": profile.blind_spots,
            "last_analysis": profile.last_analysis.isoformat() if profile.last_analysis else None
        }
    
    async def get_timeline_view(self, user_id: uuid.UUID) -> List[Dict[str, Any]]:
        """Get timeline view data for 3D visualization."""
        timeline_projection = next(
            (p for p in self.projections if isinstance(p, CulturalTimelineProjection)),
            None
        )
        
        if timeline_projection:
            return await timeline_projection.get_timeline_data(user_id)
        
        return []
    
    async def get_influence_network_view(self, user_id: uuid.UUID) -> Dict[str, Any]:
        """Get influence network view data for 3D visualization."""
        network_projection = next(
            (p for p in self.projections if isinstance(p, InfluenceNetworkProjection)),
            None
        )
        
        if network_projection:
            return await network_projection.get_network_data(user_id)
        
        return {"nodes": [], "edges": [], "last_updated": None}