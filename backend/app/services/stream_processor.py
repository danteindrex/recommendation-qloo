"""
Stream processing service for cultural pattern analysis.
Processes real-time cultural events and generates insights.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json
from dataclasses import dataclass, asdict

from app.services.kafka_service import get_kafka_service, CulturalEvent
from app.services.cache_service import get_cache_service

logger = logging.getLogger(__name__)


@dataclass
class CulturalPattern:
    """Represents a detected cultural pattern."""
    pattern_id: str
    user_id: str
    pattern_type: str
    confidence: float
    platforms: List[str]
    data: Dict[str, Any]
    detected_at: datetime
    expires_at: Optional[datetime] = None


@dataclass
class CulturalInsight:
    """Represents a generated cultural insight."""
    insight_id: str
    user_id: str
    insight_type: str
    title: str
    description: str
    confidence: float
    data: Dict[str, Any]
    generated_at: datetime


class CulturalStreamProcessor:
    """Real-time stream processor for cultural intelligence."""
    
    def __init__(self):
        self.kafka_service = None
        self.cache_service = None
        self.running = False
        
        # Pattern detection windows
        self.event_windows: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.pattern_cache: Dict[str, List[CulturalPattern]] = defaultdict(list)
        
        # Processing statistics
        self.stats = {
            "events_processed": 0,
            "patterns_detected": 0,
            "insights_generated": 0,
            "processing_errors": 0,
            "last_processed": None
        }
        
        # Pattern detection thresholds
        self.thresholds = {
            "cross_platform_correlation": 0.7,
            "cultural_shift_significance": 0.6,
            "trend_emergence": 0.8,
            "diversity_change": 0.5
        }
    
    async def start(self):
        """Start the stream processor."""
        try:
            self.kafka_service = await get_kafka_service()
            self.cache_service = await get_cache_service()
            
            # Subscribe to cultural events
            await self.kafka_service.subscribe_to_topic(
                "cultural-events",
                self._process_cultural_event,
                "stream-processor"
            )
            
            self.running = True
            
            # Start background tasks
            asyncio.create_task(self._pattern_analysis_loop())
            asyncio.create_task(self._cleanup_expired_patterns())
            
            logger.info("Cultural stream processor started")
            
        except Exception as e:
            logger.error(f"Failed to start stream processor: {e}")
            raise
    
    async def stop(self):
        """Stop the stream processor."""
        self.running = False
        logger.info("Cultural stream processor stopped")
    
    async def _process_cultural_event(self, event_data: Dict[str, Any]):
        """Process a single cultural event from Kafka."""
        try:
            # Parse event
            event = CulturalEvent(**event_data)
            user_id = event.user_id
            
            # Add to event window
            self.event_windows[user_id].append(event)
            
            # Update statistics
            self.stats["events_processed"] += 1
            self.stats["last_processed"] = datetime.utcnow()
            
            # Trigger pattern analysis for this user
            await self._analyze_user_patterns(user_id)
            
            logger.debug(f"Processed cultural event: {event.event_type} for user {user_id}")
            
        except Exception as e:
            self.stats["processing_errors"] += 1
            logger.error(f"Error processing cultural event: {e}")
    
    async def _analyze_user_patterns(self, user_id: str):
        """Analyze patterns for a specific user."""
        try:
            events = list(self.event_windows[user_id])
            if len(events) < 2:
                return
            
            # Detect various pattern types
            patterns = []
            
            # Cross-platform correlation
            cross_platform = await self._detect_cross_platform_correlation(user_id, events)
            if cross_platform:
                patterns.extend(cross_platform)
            
            # Cultural shift detection
            cultural_shifts = await self._detect_cultural_shifts(user_id, events)
            if cultural_shifts:
                patterns.extend(cultural_shifts)
            
            # Trend emergence
            trend_patterns = await self._detect_trend_emergence(user_id, events)
            if trend_patterns:
                patterns.extend(trend_patterns)
            
            # Diversity changes
            diversity_patterns = await self._detect_diversity_changes(user_id, events)
            if diversity_patterns:
                patterns.extend(diversity_patterns)
            
            # Store detected patterns
            if patterns:
                self.pattern_cache[user_id].extend(patterns)
                self.stats["patterns_detected"] += len(patterns)
                
                # Generate insights from patterns
                await self._generate_insights_from_patterns(user_id, patterns)
            
        except Exception as e:
            logger.error(f"Error analyzing patterns for user {user_id}: {e}")
    
    async def _detect_cross_platform_correlation(self, user_id: str, events: List[CulturalEvent]) -> List[CulturalPattern]:
        """Detect cross-platform behavioral correlations."""
        patterns = []
        
        try:
            # Group events by time windows (5-minute windows)
            time_windows = defaultdict(list)
            for event in events[-20:]:  # Last 20 events
                window_key = int(event.timestamp.timestamp() // 300)  # 5-minute windows
                time_windows[window_key].append(event)
            
            for window_key, window_events in time_windows.items():
                platforms = set(event.platform for event in window_events)
                
                if len(platforms) >= 2:  # Cross-platform activity
                    # Calculate correlation strength
                    correlation_strength = min(len(platforms) / 3.0, 1.0)  # Max 3 platforms
                    
                    if correlation_strength >= self.thresholds["cross_platform_correlation"]:
                        pattern = CulturalPattern(
                            pattern_id=f"cross_platform_{user_id}_{window_key}",
                            user_id=user_id,
                            pattern_type="cross_platform_correlation",
                            confidence=correlation_strength,
                            platforms=list(platforms),
                            data={
                                "window_start": datetime.fromtimestamp(window_key * 300),
                                "event_count": len(window_events),
                                "platforms": list(platforms),
                                "correlation_strength": correlation_strength
                            },
                            detected_at=datetime.utcnow(),
                            expires_at=datetime.utcnow() + timedelta(hours=1)
                        )
                        patterns.append(pattern)
            
        except Exception as e:
            logger.error(f"Error detecting cross-platform correlation: {e}")
        
        return patterns
    
    async def _detect_cultural_shifts(self, user_id: str, events: List[CulturalEvent]) -> List[CulturalPattern]:
        """Detect significant cultural behavior shifts."""
        patterns = []
        
        try:
            if len(events) < 10:
                return patterns
            
            # Analyze recent vs historical behavior
            recent_events = events[-5:]
            historical_events = events[-15:-5]
            
            # Calculate cultural diversity scores
            recent_diversity = self._calculate_diversity_score(recent_events)
            historical_diversity = self._calculate_diversity_score(historical_events)
            
            shift_magnitude = abs(recent_diversity - historical_diversity)
            
            if shift_magnitude >= self.thresholds["cultural_shift_significance"]:
                pattern = CulturalPattern(
                    pattern_id=f"cultural_shift_{user_id}_{int(datetime.utcnow().timestamp())}",
                    user_id=user_id,
                    pattern_type="cultural_shift",
                    confidence=min(shift_magnitude, 1.0),
                    platforms=list(set(event.platform for event in recent_events)),
                    data={
                        "shift_magnitude": shift_magnitude,
                        "recent_diversity": recent_diversity,
                        "historical_diversity": historical_diversity,
                        "shift_direction": "increase" if recent_diversity > historical_diversity else "decrease"
                    },
                    detected_at=datetime.utcnow(),
                    expires_at=datetime.utcnow() + timedelta(hours=2)
                )
                patterns.append(pattern)
        
        except Exception as e:
            logger.error(f"Error detecting cultural shifts: {e}")
        
        return patterns
    
    async def _detect_trend_emergence(self, user_id: str, events: List[CulturalEvent]) -> List[CulturalPattern]:
        """Detect emerging cultural trends."""
        patterns = []
        
        try:
            # Group events by cultural categories
            category_counts = defaultdict(int)
            recent_events = events[-10:]
            
            for event in recent_events:
                categories = event.data.get("cultural_categories", [])
                for category in categories:
                    category_counts[category] += 1
            
            # Find emerging trends (categories with high recent activity)
            total_events = len(recent_events)
            for category, count in category_counts.items():
                trend_strength = count / total_events if total_events > 0 else 0
                
                if trend_strength >= self.thresholds["trend_emergence"]:
                    pattern = CulturalPattern(
                        pattern_id=f"trend_emergence_{user_id}_{category}_{int(datetime.utcnow().timestamp())}",
                        user_id=user_id,
                        pattern_type="trend_emergence",
                        confidence=trend_strength,
                        platforms=list(set(event.platform for event in recent_events 
                                         if category in event.data.get("cultural_categories", []))),
                        data={
                            "category": category,
                            "trend_strength": trend_strength,
                            "event_count": count,
                            "total_events": total_events
                        },
                        detected_at=datetime.utcnow(),
                        expires_at=datetime.utcnow() + timedelta(hours=3)
                    )
                    patterns.append(pattern)
        
        except Exception as e:
            logger.error(f"Error detecting trend emergence: {e}")
        
        return patterns
    
    async def _detect_diversity_changes(self, user_id: str, events: List[CulturalEvent]) -> List[CulturalPattern]:
        """Detect changes in cultural diversity."""
        patterns = []
        
        try:
            if len(events) < 8:
                return patterns
            
            # Compare diversity over time windows
            window_size = 4
            windows = [events[i:i+window_size] for i in range(0, len(events)-window_size+1, window_size)]
            
            if len(windows) >= 2:
                diversity_scores = [self._calculate_diversity_score(window) for window in windows]
                
                # Check for significant diversity changes
                for i in range(1, len(diversity_scores)):
                    change = abs(diversity_scores[i] - diversity_scores[i-1])
                    
                    if change >= self.thresholds["diversity_change"]:
                        pattern = CulturalPattern(
                            pattern_id=f"diversity_change_{user_id}_{i}_{int(datetime.utcnow().timestamp())}",
                            user_id=user_id,
                            pattern_type="diversity_change",
                            confidence=min(change, 1.0),
                            platforms=list(set(event.platform for event in windows[i])),
                            data={
                                "change_magnitude": change,
                                "previous_diversity": diversity_scores[i-1],
                                "current_diversity": diversity_scores[i],
                                "window_index": i
                            },
                            detected_at=datetime.utcnow(),
                            expires_at=datetime.utcnow() + timedelta(hours=1)
                        )
                        patterns.append(pattern)
        
        except Exception as e:
            logger.error(f"Error detecting diversity changes: {e}")
        
        return patterns
    
    def _calculate_diversity_score(self, events: List[CulturalEvent]) -> float:
        """Calculate cultural diversity score for a set of events."""
        if not events:
            return 0.0
        
        # Count unique cultural categories
        categories = set()
        platforms = set()
        
        for event in events:
            categories.update(event.data.get("cultural_categories", []))
            platforms.add(event.platform)
        
        # Simple diversity calculation
        category_diversity = len(categories) / 10.0  # Normalize to max 10 categories
        platform_diversity = len(platforms) / 3.0   # Normalize to max 3 platforms
        
        return min((category_diversity + platform_diversity) / 2.0, 1.0)
    
    async def _generate_insights_from_patterns(self, user_id: str, patterns: List[CulturalPattern]):
        """Generate cultural insights from detected patterns."""
        try:
            for pattern in patterns:
                insight = await self._create_insight_from_pattern(pattern)
                if insight:
                    # Publish insight to Kafka
                    await self.kafka_service.publish_cultural_insight(
                        user_id,
                        asdict(insight)
                    )
                    
                    # Cache insight
                    cache_key = f"insight:{user_id}:{insight.insight_id}"
                    await self.cache_service.set(
                        cache_key,
                        json.dumps(asdict(insight), default=str),
                        expire=3600  # 1 hour
                    )
                    
                    self.stats["insights_generated"] += 1
                    logger.debug(f"Generated insight {insight.insight_type} for user {user_id}")
        
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
    
    async def _create_insight_from_pattern(self, pattern: CulturalPattern) -> Optional[CulturalInsight]:
        """Create a cultural insight from a detected pattern."""
        try:
            insight_id = f"insight_{pattern.pattern_id}"
            
            if pattern.pattern_type == "cross_platform_correlation":
                return CulturalInsight(
                    insight_id=insight_id,
                    user_id=pattern.user_id,
                    insight_type="cross_platform_behavior",
                    title="Cross-Platform Cultural Activity Detected",
                    description=f"You're showing consistent cultural behavior across {len(pattern.platforms)} platforms, indicating strong cultural preferences.",
                    confidence=pattern.confidence,
                    data={
                        "platforms": pattern.platforms,
                        "correlation_strength": pattern.data.get("correlation_strength", 0)
                    },
                    generated_at=datetime.utcnow()
                )
            
            elif pattern.pattern_type == "cultural_shift":
                shift_direction = pattern.data.get("shift_direction", "change")
                return CulturalInsight(
                    insight_id=insight_id,
                    user_id=pattern.user_id,
                    insight_type="cultural_evolution",
                    title=f"Cultural Diversity {shift_direction.title()} Detected",
                    description=f"Your cultural diversity has shown a significant {shift_direction}, suggesting evolving interests and preferences.",
                    confidence=pattern.confidence,
                    data={
                        "shift_magnitude": pattern.data.get("shift_magnitude", 0),
                        "shift_direction": shift_direction
                    },
                    generated_at=datetime.utcnow()
                )
            
            elif pattern.pattern_type == "trend_emergence":
                category = pattern.data.get("category", "unknown")
                return CulturalInsight(
                    insight_id=insight_id,
                    user_id=pattern.user_id,
                    insight_type="emerging_trend",
                    title=f"Emerging Interest in {category.title()}",
                    description=f"You're showing increased engagement with {category} content, indicating a potential new cultural interest.",
                    confidence=pattern.confidence,
                    data={
                        "category": category,
                        "trend_strength": pattern.data.get("trend_strength", 0)
                    },
                    generated_at=datetime.utcnow()
                )
            
            elif pattern.pattern_type == "diversity_change":
                return CulturalInsight(
                    insight_id=insight_id,
                    user_id=pattern.user_id,
                    insight_type="diversity_shift",
                    title="Cultural Diversity Pattern Change",
                    description="Your cultural engagement patterns are shifting, showing changes in how you explore different cultural categories.",
                    confidence=pattern.confidence,
                    data={
                        "change_magnitude": pattern.data.get("change_magnitude", 0),
                        "diversity_trend": "expanding" if pattern.data.get("current_diversity", 0) > pattern.data.get("previous_diversity", 0) else "focusing"
                    },
                    generated_at=datetime.utcnow()
                )
        
        except Exception as e:
            logger.error(f"Error creating insight from pattern: {e}")
        
        return None
    
    async def _pattern_analysis_loop(self):
        """Background loop for periodic pattern analysis."""
        while self.running:
            try:
                # Analyze patterns for all active users
                for user_id in list(self.event_windows.keys()):
                    if len(self.event_windows[user_id]) > 0:
                        await self._analyze_user_patterns(user_id)
                
                # Wait before next analysis cycle
                await asyncio.sleep(30)  # Analyze every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in pattern analysis loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _cleanup_expired_patterns(self):
        """Clean up expired patterns from cache."""
        while self.running:
            try:
                current_time = datetime.utcnow()
                
                for user_id in list(self.pattern_cache.keys()):
                    patterns = self.pattern_cache[user_id]
                    # Remove expired patterns
                    self.pattern_cache[user_id] = [
                        p for p in patterns 
                        if p.expires_at is None or p.expires_at > current_time
                    ]
                    
                    # Remove empty entries
                    if not self.pattern_cache[user_id]:
                        del self.pattern_cache[user_id]
                
                # Wait before next cleanup
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in pattern cleanup: {e}")
                await asyncio.sleep(600)  # Wait longer on error
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return {
            **self.stats,
            "active_users": len(self.event_windows),
            "cached_patterns": sum(len(patterns) for patterns in self.pattern_cache.values()),
            "running": self.running
        }
    
    async def get_user_patterns(self, user_id: str) -> List[Dict[str, Any]]:
        """Get current patterns for a user."""
        patterns = self.pattern_cache.get(user_id, [])
        return [asdict(pattern) for pattern in patterns]


# Global stream processor instance
stream_processor = CulturalStreamProcessor()


async def get_stream_processor() -> CulturalStreamProcessor:
    """Get the global stream processor instance."""
    return stream_processor