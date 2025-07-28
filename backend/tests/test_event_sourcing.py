"""
Tests for event sourcing and CQRS implementation.
Tests event store, event handlers, CQRS mediator, and projections.
"""

import pytest
import uuid
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.events import CulturalEvent, EventSnapshot, EventType
from app.models.cultural_data import CulturalProfile
from app.services.event_store import EventStore, ConcurrencyException
from app.services.event_handlers import (
    EventDispatcher, SocialDataIngestedHandler, CulturalPatternDetectedHandler
)
from app.services.cqrs import (
    CQRSMediator, IngestSocialDataCommand, UpdateDiversityScoreCommand,
    GetCulturalProfileQuery, GetCulturalEvolutionQuery
)
from app.services.projections import (
    ProjectionManager, CulturalProfileProjection, CulturalTimelineProjection
)


class TestEventStore:
    """Test event store functionality."""
    
    @pytest.mark.asyncio
    async def test_append_event_success(self, db_session: AsyncSession):
        """Test successful event appending."""
        event_store = EventStore(db_session)
        user_id = uuid.uuid4()
        
        event_data = {
            "platform": "instagram",
            "data_type": "post",
            "content": {"text": "test post"},
            "cultural_signals": {"sentiment": "positive"},
            "confidence_score": 0.85
        }
        
        event = await event_store.append_event(
            aggregate_id=user_id,
            event_type=EventType.SOCIAL_DATA_INGESTED,
            event_data=event_data,
            expected_version=0,
            source_service="test_service"
        )
        
        assert event.aggregate_id == str(user_id)
        assert event.event_type == EventType.SOCIAL_DATA_INGESTED
        assert event.version == 1
        assert event.event_data == event_data
        assert event.source_service == "test_service"
    
    @pytest.mark.asyncio
    async def test_append_event_concurrency_conflict(self, db_session: AsyncSession):
        """Test concurrency conflict handling."""
        event_store = EventStore(db_session)
        user_id = uuid.uuid4()
        
        # First event
        await event_store.append_event(
            aggregate_id=user_id,
            event_type=EventType.SOCIAL_DATA_INGESTED,
            event_data={"test": "data1"},
            expected_version=0
        )
        
        # Second event with wrong expected version should fail
        with pytest.raises(ConcurrencyException):
            await event_store.append_event(
                aggregate_id=user_id,
                event_type=EventType.SOCIAL_DATA_INGESTED,
                event_data={"test": "data2"},
                expected_version=0  # Should be 1
            )
    
    @pytest.mark.asyncio
    async def test_get_events(self, db_session: AsyncSession):
        """Test retrieving events for an aggregate."""
        event_store = EventStore(db_session)
        user_id = uuid.uuid4()
        
        # Add multiple events
        for i in range(3):
            await event_store.append_event(
                aggregate_id=user_id,
                event_type=EventType.SOCIAL_DATA_INGESTED,
                event_data={"sequence": i},
                expected_version=i
            )
        
        # Retrieve all events
        events = await event_store.get_events(user_id)
        assert len(events) == 3
        assert events[0].version == 1
        assert events[2].version == 3
        
        # Retrieve events from version 2
        events_from_2 = await event_store.get_events(user_id, from_version=1)
        assert len(events_from_2) == 2
        assert events_from_2[0].version == 2
    
    @pytest.mark.asyncio
    async def test_get_events_by_type(self, db_session: AsyncSession):
        """Test retrieving events by type."""
        event_store = EventStore(db_session)
        user_id = uuid.uuid4()
        
        # Add different types of events
        await event_store.append_event(
            aggregate_id=user_id,
            event_type=EventType.SOCIAL_DATA_INGESTED,
            event_data={"test": "data1"},
            expected_version=0
        )
        
        await event_store.append_event(
            aggregate_id=user_id,
            event_type=EventType.DIVERSITY_SCORE_UPDATED,
            event_data={"old_score": 0.5, "new_score": 0.7},
            expected_version=1
        )
        
        # Retrieve only social data events
        social_events = await event_store.get_events_by_type(
            EventType.SOCIAL_DATA_INGESTED
        )
        assert len(social_events) == 1
        assert social_events[0].event_type == EventType.SOCIAL_DATA_INGESTED
    
    @pytest.mark.asyncio
    async def test_save_and_get_snapshot(self, db_session: AsyncSession):
        """Test snapshot functionality."""
        event_store = EventStore(db_session)
        user_id = uuid.uuid4()
        
        snapshot_data = {
            "diversity_score": 0.75,
            "evolution_data": {"patterns": []},
            "influence_network": {"nodes": []}
        }
        
        # Save snapshot
        snapshot = await event_store.save_snapshot(
            aggregate_id=user_id,
            aggregate_type="cultural_profile",
            version=5,
            snapshot_data=snapshot_data
        )
        
        assert snapshot.aggregate_id == str(user_id)
        assert snapshot.version == 5
        assert snapshot.snapshot_data == snapshot_data
        
        # Retrieve snapshot
        retrieved_snapshot = await event_store.get_latest_snapshot(
            user_id, "cultural_profile"
        )
        
        assert retrieved_snapshot is not None
        assert retrieved_snapshot.version == 5
        assert retrieved_snapshot.snapshot_data == snapshot_data


class TestEventHandlers:
    """Test event handlers."""
    
    @pytest.mark.asyncio
    async def test_social_data_ingested_handler(self, db_session: AsyncSession):
        """Test social data ingestion handler."""
        handler = SocialDataIngestedHandler(db_session)
        
        event = CulturalEvent(
            aggregate_id=uuid.uuid4(),
            event_type=EventType.SOCIAL_DATA_INGESTED,
            version=1,
            event_data={
                "platform": "instagram",
                "data_type": "post",
                "content": {"text": "test post"},
                "cultural_signals": {"sentiment": "positive"},
                "confidence_score": 0.85
            },
            occurred_at=datetime.utcnow()
        )
        
        # Handler should process without error
        await handler.handle(event)
        
        # Verify handler can handle this event type
        assert handler.can_handle(EventType.SOCIAL_DATA_INGESTED)
        assert not handler.can_handle(EventType.DIVERSITY_SCORE_UPDATED)
    
    @pytest.mark.asyncio
    async def test_cultural_pattern_detected_handler(self, db_session: AsyncSession):
        """Test cultural pattern detection handler."""
        handler = CulturalPatternDetectedHandler(db_session)
        
        event = CulturalEvent(
            aggregate_id=uuid.uuid4(),
            event_type=EventType.CULTURAL_PATTERN_DETECTED,
            version=1,
            event_data={
                "pattern_type": "cross_platform_trend",
                "pattern_data": {"trend": "minimalism"},
                "confidence": 0.9,
                "platforms": ["instagram", "tiktok"],
                "timeframe": {"start": "2024-01-01", "end": "2024-01-07"}
            },
            occurred_at=datetime.utcnow()
        )
        
        # Handler should process without error
        await handler.handle(event)
        
        # Verify handler can handle this event type
        assert handler.can_handle(EventType.CULTURAL_PATTERN_DETECTED)
    
    @pytest.mark.asyncio
    async def test_event_dispatcher(self, db_session: AsyncSession):
        """Test event dispatcher."""
        dispatcher = EventDispatcher(db_session)
        
        event = CulturalEvent(
            aggregate_id=uuid.uuid4(),
            event_type=EventType.SOCIAL_DATA_INGESTED,
            version=1,
            event_data={
                "platform": "instagram",
                "data_type": "post",
                "content": {"text": "test post"},
                "cultural_signals": {"sentiment": "positive"},
                "confidence_score": 0.85
            },
            occurred_at=datetime.utcnow()
        )
        
        # Dispatch should complete without error
        await dispatcher.dispatch(event)


class TestCQRS:
    """Test CQRS implementation."""
    
    @pytest.mark.asyncio
    async def test_ingest_social_data_command(self, db_session: AsyncSession):
        """Test social data ingestion command."""
        mediator = CQRSMediator(db_session)
        user_id = uuid.uuid4()
        
        command = IngestSocialDataCommand(
            user_id=user_id,
            platform="instagram",
            data_type="post",
            content={"text": "test post"},
            cultural_signals={"sentiment": "positive"},
            confidence_score=0.85
        )
        
        # Execute command
        event = await mediator.send_command(command)
        
        assert event.aggregate_id == str(user_id)
        assert event.event_type == EventType.SOCIAL_DATA_INGESTED
        assert event.event_data["platform"] == "instagram"
    
    @pytest.mark.asyncio
    async def test_update_diversity_score_command(self, db_session: AsyncSession):
        """Test diversity score update command."""
        mediator = CQRSMediator(db_session)
        user_id = uuid.uuid4()
        
        # First create a cultural profile
        profile = CulturalProfile(
            user_id=str(user_id),
            diversity_score=0.5
        )
        db_session.add(profile)
        await db_session.commit()
        
        command = UpdateDiversityScoreCommand(
            user_id=user_id,
            new_score=0.75,
            contributing_factors=["new_platform_engagement"],
            analysis_data={"detailed_analysis": "improved diversity"}
        )
        
        # Execute command
        event = await mediator.send_command(command)
        
        assert event.aggregate_id == str(user_id)
        assert event.event_type == EventType.DIVERSITY_SCORE_UPDATED
        assert event.event_data["new_score"] == 0.75
        assert event.event_data["old_score"] == 0.5
    
    @pytest.mark.asyncio
    async def test_get_cultural_profile_query(self, db_session: AsyncSession):
        """Test cultural profile query."""
        mediator = CQRSMediator(db_session)
        user_id = uuid.uuid4()
        
        # Create test profile
        profile = CulturalProfile(
            user_id=str(user_id),
            diversity_score=0.75,
            evolution_data={"patterns": []},
            influence_network={"nodes": []},
            blind_spots=[]
        )
        db_session.add(profile)
        await db_session.commit()
        
        query = GetCulturalProfileQuery(user_id=user_id)
        result = await mediator.send_query(query)
        
        assert result is not None
        assert result["user_id"] == str(user_id)
        assert result["diversity_score"] == 0.75
        assert "evolution_data" in result
        assert "influence_network" in result
    
    @pytest.mark.asyncio
    async def test_get_cultural_evolution_query(self, db_session: AsyncSession):
        """Test cultural evolution query."""
        mediator = CQRSMediator(db_session)
        user_id = uuid.uuid4()
        
        # Create test milestone event
        event_store = EventStore(db_session)
        await event_store.append_event(
            aggregate_id=user_id,
            event_type=EventType.CULTURAL_MILESTONE_REACHED,
            event_data={
                "milestone_type": "diversity_breakthrough",
                "cultural_shift": 0.3,
                "confidence": 0.9,
                "platforms": ["instagram", "tiktok"],
                "description": "Significant cultural diversity improvement"
            },
            expected_version=0
        )
        
        query = GetCulturalEvolutionQuery(user_id=user_id)
        result = await mediator.send_query(query)
        
        assert len(result) == 1
        assert result[0]["milestone_type"] == "diversity_breakthrough"
        assert result[0]["cultural_shift"] == 0.3


class TestProjections:
    """Test projection services."""
    
    @pytest.mark.asyncio
    async def test_cultural_profile_projection(self, db_session: AsyncSession):
        """Test cultural profile projection."""
        projection = CulturalProfileProjection(db_session)
        user_id = uuid.uuid4()
        
        # Create diversity score update event
        event = CulturalEvent(
            aggregate_id=str(user_id),
            event_type=EventType.DIVERSITY_SCORE_UPDATED,
            version=1,
            event_data={
                "old_score": 0.5,
                "new_score": 0.75,
                "contributing_factors": ["new_engagement"],
                "analysis_data": {"details": "improved"}
            },
            occurred_at=datetime.utcnow()
        )
        
        # Project event
        await projection.project_event(event)
        
        # Verify projection was updated
        from sqlalchemy import select
        stmt = select(CulturalProfile).where(CulturalProfile.user_id == str(user_id))
        result = await db_session.execute(stmt)
        profile = result.scalar_one_or_none()
        
        assert profile is not None
        assert float(profile.diversity_score) == 0.75
    
    @pytest.mark.asyncio
    async def test_cultural_timeline_projection(self, db_session: AsyncSession):
        """Test cultural timeline projection."""
        projection = CulturalTimelineProjection(db_session)
        user_id = uuid.uuid4()
        
        # Create milestone event
        event = CulturalEvent(
            aggregate_id=user_id,
            event_type=EventType.CULTURAL_MILESTONE_REACHED,
            version=1,
            event_data={
                "milestone_type": "diversity_breakthrough",
                "cultural_shift": 0.3,
                "confidence": 0.9,
                "platforms": ["instagram", "tiktok"],
                "description": "Significant improvement"
            },
            occurred_at=datetime.utcnow()
        )
        
        # Project event
        await projection.project_event(event)
        
        # Get timeline data
        timeline_data = await projection.get_timeline_data(user_id)
        
        assert len(timeline_data) == 1
        assert timeline_data[0]["type"] == "milestone"
        assert timeline_data[0]["milestone_type"] == "diversity_breakthrough"
        assert timeline_data[0]["cultural_shift"] == 0.3
    
    @pytest.mark.asyncio
    async def test_projection_manager(self, db_session: AsyncSession):
        """Test projection manager."""
        manager = ProjectionManager(db_session)
        user_id = uuid.uuid4()
        
        # Create test event
        event = CulturalEvent(
            aggregate_id=user_id,
            event_type=EventType.DIVERSITY_SCORE_UPDATED,
            version=1,
            event_data={
                "old_score": 0.5,
                "new_score": 0.75,
                "contributing_factors": ["new_engagement"],
                "analysis_data": {"details": "improved"}
            },
            occurred_at=datetime.utcnow()
        )
        
        # Project to all projections
        await manager.project_event(event)
        
        # Verify cultural profile view
        profile_view = await manager.get_cultural_profile_view(user_id)
        assert profile_view is not None
        assert profile_view["diversity_score"] == 0.75
        
        # Verify timeline view
        timeline_view = await manager.get_timeline_view(user_id)
        assert len(timeline_view) == 1
        assert timeline_view[0]["type"] == "diversity_change"
    
    @pytest.mark.asyncio
    async def test_rebuild_projections(self, db_session: AsyncSession):
        """Test rebuilding projections from events."""
        manager = ProjectionManager(db_session)
        user_id = uuid.uuid4()
        
        # Create multiple events
        event_store = EventStore(db_session)
        
        await event_store.append_event(
            aggregate_id=user_id,
            event_type=EventType.SOCIAL_DATA_INGESTED,
            event_data={"platform": "instagram", "data_type": "post"},
            expected_version=0
        )
        
        await event_store.append_event(
            aggregate_id=user_id,
            event_type=EventType.DIVERSITY_SCORE_UPDATED,
            event_data={"old_score": 0.0, "new_score": 0.5},
            expected_version=1
        )
        
        # Rebuild all projections
        await manager.rebuild_all_projections(user_id)
        
        # Verify projections were rebuilt
        profile_view = await manager.get_cultural_profile_view(user_id)
        assert profile_view is not None
        assert profile_view["diversity_score"] == 0.5


class TestEventSourcingIntegration:
    """Integration tests for complete event sourcing flow."""
    
    @pytest.mark.asyncio
    async def test_complete_event_sourcing_flow(self, db_session: AsyncSession):
        """Test complete flow from command to projection."""
        mediator = CQRSMediator(db_session)
        user_id = uuid.uuid4()
        
        # 1. Execute command
        command = IngestSocialDataCommand(
            user_id=user_id,
            platform="instagram",
            data_type="post",
            content={"text": "cultural content"},
            cultural_signals={"sentiment": "positive", "cultural_markers": ["art"]},
            confidence_score=0.85
        )
        
        event = await mediator.send_command(command)
        assert event is not None
        
        # 2. Execute diversity score update
        diversity_command = UpdateDiversityScoreCommand(
            user_id=user_id,
            new_score=0.75,
            contributing_factors=["art_engagement"],
            analysis_data={"category": "visual_arts"}
        )
        
        diversity_event = await mediator.send_command(diversity_command)
        assert diversity_event is not None
        
        # 3. Query updated profile
        profile_query = GetCulturalProfileQuery(user_id=user_id)
        profile_result = await mediator.send_query(profile_query)
        
        assert profile_result is not None
        assert profile_result["diversity_score"] == 0.75
        assert profile_result["user_id"] == str(user_id)
        
        # 4. Verify event store contains events
        event_store = EventStore(db_session)
        events = await event_store.get_events(user_id)
        
        assert len(events) == 2
        assert events[0].event_type == EventType.SOCIAL_DATA_INGESTED
        assert events[1].event_type == EventType.DIVERSITY_SCORE_UPDATED