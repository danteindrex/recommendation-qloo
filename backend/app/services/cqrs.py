"""
CQRS (Command Query Responsibility Segregation) implementation for cultural intelligence.
Separates read and write models for optimal performance and scalability.
"""

from typing import Dict, Any, List, Optional, Union
from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.models.events import CulturalEvent, EventType
from app.models.cultural_data import CulturalProfile, CulturalDataPoint
from app.services.event_store import EventStore, ConcurrencyException
from app.services.event_handlers import EventDispatcher
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


# Command side (Write Model)
class Command(ABC):
    """Base class for all commands."""
    pass


class IngestSocialDataCommand(Command):
    """Command to ingest social media data."""
    
    def __init__(
        self,
        user_id: uuid.UUID,
        platform: str,
        data_type: str,
        content: Dict[str, Any],
        cultural_signals: Dict[str, Any],
        confidence_score: float
    ):
        self.user_id = user_id
        self.platform = platform
        self.data_type = data_type
        self.content = content
        self.cultural_signals = cultural_signals
        self.confidence_score = confidence_score


class UpdateDiversityScoreCommand(Command):
    """Command to update user's diversity score."""
    
    def __init__(
        self,
        user_id: uuid.UUID,
        new_score: float,
        contributing_factors: List[str],
        analysis_data: Dict[str, Any]
    ):
        self.user_id = user_id
        self.new_score = new_score
        self.contributing_factors = contributing_factors
        self.analysis_data = analysis_data


class GenerateRecommendationCommand(Command):
    """Command to generate a cultural recommendation."""
    
    def __init__(
        self,
        user_id: uuid.UUID,
        recommendation_type: str,
        title: str,
        description: str,
        confidence_score: float,
        cultural_category: str,
        external_data: Dict[str, Any]
    ):
        self.user_id = user_id
        self.recommendation_type = recommendation_type
        self.title = title
        self.description = description
        self.confidence_score = confidence_score
        self.cultural_category = cultural_category
        self.external_data = external_data


class CommandHandler(ABC):
    """Base class for command handlers."""
    
    @abstractmethod
    async def handle(self, command: Command) -> Any:
        """Handle a command."""
        pass


class IngestSocialDataCommandHandler(CommandHandler):
    """Handler for social data ingestion commands."""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.event_store = EventStore(db_session)
    
    async def handle(self, command: IngestSocialDataCommand) -> CulturalEvent:
        """Handle social data ingestion command."""
        try:
            # Get current version for optimistic concurrency control
            current_version = await self.event_store._get_current_version(command.user_id)
            
            # Create event data
            event_data = {
                "platform": command.platform,
                "data_type": command.data_type,
                "content": command.content,
                "cultural_signals": command.cultural_signals,
                "confidence_score": command.confidence_score
            }
            
            # Append event to event store
            event = await self.event_store.append_event(
                aggregate_id=command.user_id,
                event_type=EventType.SOCIAL_DATA_INGESTED,
                event_data=event_data,
                expected_version=current_version,
                source_service="cultural_intelligence",
                correlation_id=uuid.uuid4()
            )
            
            logger.info(f"Social data ingestion event created for user {command.user_id}")
            return event
            
        except ConcurrencyException as e:
            logger.error(f"Concurrency error in social data ingestion: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error handling social data ingestion command: {str(e)}")
            raise


class UpdateDiversityScoreCommandHandler(CommandHandler):
    """Handler for diversity score update commands."""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.event_store = EventStore(db_session)
    
    async def handle(self, command: UpdateDiversityScoreCommand) -> CulturalEvent:
        """Handle diversity score update command."""
        try:
            # Get current diversity score for comparison
            current_score = await self._get_current_diversity_score(command.user_id)
            current_version = await self.event_store._get_current_version(command.user_id)
            
            # Create event data
            event_data = {
                "old_score": current_score,
                "new_score": command.new_score,
                "contributing_factors": command.contributing_factors,
                "analysis_data": command.analysis_data
            }
            
            # Append event to event store
            event = await self.event_store.append_event(
                aggregate_id=command.user_id,
                event_type=EventType.DIVERSITY_SCORE_UPDATED,
                event_data=event_data,
                expected_version=current_version,
                source_service="cultural_intelligence",
                correlation_id=uuid.uuid4()
            )
            
            logger.info(f"Diversity score update event created for user {command.user_id}")
            return event
            
        except Exception as e:
            logger.error(f"Error handling diversity score update command: {str(e)}")
            raise
    
    async def _get_current_diversity_score(self, user_id: uuid.UUID) -> float:
        """Get current diversity score from read model."""
        query = select(CulturalProfile.diversity_score).where(
            CulturalProfile.user_id == str(user_id)
        )
        result = await self.db_session.execute(query)
        score = result.scalar_one_or_none()
        return float(score) if score else 0.0


class GenerateRecommendationCommandHandler(CommandHandler):
    """Handler for recommendation generation commands."""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.event_store = EventStore(db_session)
    
    async def handle(self, command: GenerateRecommendationCommand) -> CulturalEvent:
        """Handle recommendation generation command."""
        try:
            current_version = await self.event_store._get_current_version(command.user_id)
            
            # Create event data
            event_data = {
                "recommendation_type": command.recommendation_type,
                "title": command.title,
                "description": command.description,
                "confidence_score": command.confidence_score,
                "cultural_category": command.cultural_category,
                "external_data": command.external_data
            }
            
            # Append event to event store
            event = await self.event_store.append_event(
                aggregate_id=command.user_id,
                event_type=EventType.RECOMMENDATION_GENERATED,
                event_data=event_data,
                expected_version=current_version,
                source_service="cultural_intelligence",
                correlation_id=uuid.uuid4()
            )
            
            logger.info(f"Recommendation generation event created for user {command.user_id}")
            return event
            
        except Exception as e:
            logger.error(f"Error handling recommendation generation command: {str(e)}")
            raise


# Query side (Read Model)
class Query(ABC):
    """Base class for all queries."""
    pass


class GetCulturalProfileQuery(Query):
    """Query to get user's cultural profile."""
    
    def __init__(self, user_id: uuid.UUID):
        self.user_id = user_id


class GetCulturalEvolutionQuery(Query):
    """Query to get user's cultural evolution timeline."""
    
    def __init__(self, user_id: uuid.UUID, from_date: Optional[datetime] = None):
        self.user_id = user_id
        self.from_date = from_date


class GetRecommendationsQuery(Query):
    """Query to get user's recommendations."""
    
    def __init__(self, user_id: uuid.UUID, limit: int = 10):
        self.user_id = user_id
        self.limit = limit


class QueryHandler(ABC):
    """Base class for query handlers."""
    
    @abstractmethod
    async def handle(self, query: Query) -> Any:
        """Handle a query."""
        pass


class GetCulturalProfileQueryHandler(QueryHandler):
    """Handler for cultural profile queries."""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def handle(self, query: GetCulturalProfileQuery) -> Optional[Dict[str, Any]]:
        """Handle cultural profile query."""
        try:
            # Query read model
            stmt = select(CulturalProfile).where(
                CulturalProfile.user_id == str(query.user_id)
            )
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
            
        except Exception as e:
            logger.error(f"Error handling cultural profile query: {str(e)}")
            raise


class GetCulturalEvolutionQueryHandler(QueryHandler):
    """Handler for cultural evolution queries."""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.event_store = EventStore(db_session)
    
    async def handle(self, query: GetCulturalEvolutionQuery) -> List[Dict[str, Any]]:
        """Handle cultural evolution query."""
        try:
            # Get milestone events from event store
            events = await self.event_store.get_events_by_type(
                EventType.CULTURAL_MILESTONE_REACHED,
                from_date=query.from_date
            )
            
            # Filter by user and format response
            user_events = [e for e in events if e.aggregate_id == str(query.user_id)]
            
            evolution_timeline = []
            for event in user_events:
                evolution_timeline.append({
                    "timestamp": event.occurred_at.isoformat(),
                    "milestone_type": event.event_data.get("milestone_type"),
                    "cultural_shift": event.event_data.get("cultural_shift"),
                    "confidence": event.event_data.get("confidence"),
                    "platforms": event.event_data.get("platforms", []),
                    "description": event.event_data.get("description")
                })
            
            return evolution_timeline
            
        except Exception as e:
            logger.error(f"Error handling cultural evolution query: {str(e)}")
            raise


class GetRecommendationsQueryHandler(QueryHandler):
    """Handler for recommendations queries."""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.event_store = EventStore(db_session)
    
    async def handle(self, query: GetRecommendationsQuery) -> List[Dict[str, Any]]:
        """Handle recommendations query."""
        try:
            # Get recommendation events from event store
            events = await self.event_store.get_events_by_type(
                EventType.RECOMMENDATION_GENERATED,
                limit=query.limit
            )
            
            # Filter by user and format response
            user_events = [e for e in events if e.aggregate_id == str(query.user_id)]
            
            recommendations = []
            for event in user_events:
                recommendations.append({
                    "id": str(event.event_id),
                    "recommendation_type": event.event_data.get("recommendation_type"),
                    "title": event.event_data.get("title"),
                    "description": event.event_data.get("description"),
                    "confidence_score": event.event_data.get("confidence_score"),
                    "cultural_category": event.event_data.get("cultural_category"),
                    "external_data": event.event_data.get("external_data", {}),
                    "created_at": event.occurred_at.isoformat()
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error handling recommendations query: {str(e)}")
            raise


class CQRSMediator:
    """Mediator for CQRS pattern - routes commands and queries to appropriate handlers."""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.command_handlers = self._register_command_handlers()
        self.query_handlers = self._register_query_handlers()
        self.event_dispatcher = EventDispatcher(db_session)
    
    def _register_command_handlers(self) -> Dict[type, CommandHandler]:
        """Register command handlers."""
        return {
            IngestSocialDataCommand: IngestSocialDataCommandHandler(self.db_session),
            UpdateDiversityScoreCommand: UpdateDiversityScoreCommandHandler(self.db_session),
            GenerateRecommendationCommand: GenerateRecommendationCommandHandler(self.db_session),
        }
    
    def _register_query_handlers(self) -> Dict[type, QueryHandler]:
        """Register query handlers."""
        return {
            GetCulturalProfileQuery: GetCulturalProfileQueryHandler(self.db_session),
            GetCulturalEvolutionQuery: GetCulturalEvolutionQueryHandler(self.db_session),
            GetRecommendationsQuery: GetRecommendationsQueryHandler(self.db_session),
        }
    
    async def send_command(self, command: Command) -> Any:
        """Send a command to its handler."""
        handler = self.command_handlers.get(type(command))
        if not handler:
            raise ValueError(f"No handler registered for command type: {type(command)}")
        
        # Execute command and get resulting event
        event = await handler.handle(command)
        
        # Dispatch event to update read models
        await self.event_dispatcher.dispatch(event)
        
        return event
    
    async def send_query(self, query: Query) -> Any:
        """Send a query to its handler."""
        handler = self.query_handlers.get(type(query))
        if not handler:
            raise ValueError(f"No handler registered for query type: {type(query)}")
        
        return await handler.handle(query)