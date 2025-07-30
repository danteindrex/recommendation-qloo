"""
Real-time notification system for cultural insights.
Manages user notifications and real-time delivery via WebSocket and Kafka.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
import json
import uuid

from app.services.kafka_service import get_kafka_service
from app.services.cache_service import get_cache_service

logger = logging.getLogger(__name__)


class NotificationPriority(Enum):
    """Notification priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class NotificationType(Enum):
    """Types of cultural notifications."""
    CULTURAL_INSIGHT = "cultural_insight"
    TREND_ALERT = "trend_alert"
    DIVERSITY_MILESTONE = "diversity_milestone"
    RECOMMENDATION = "recommendation"
    PATTERN_DETECTED = "pattern_detected"
    SOCIAL_UPDATE = "social_update"
    SYSTEM_ALERT = "system_alert"


@dataclass
class CulturalNotification:
    """Cultural intelligence notification model."""
    notification_id: str
    user_id: str
    notification_type: NotificationType
    priority: NotificationPriority
    title: str
    message: str
    data: Dict[str, Any]
    created_at: datetime
    expires_at: Optional[datetime] = None
    read: bool = False
    delivered: bool = False
    delivery_attempts: int = 0
    max_delivery_attempts: int = 3


class CulturalNotificationService:
    """Service for managing cultural intelligence notifications."""
    
    def __init__(self):
        self.kafka_service = None
        self.cache_service = None
        self.running = False
        
        # Notification queues by priority
        self.notification_queues: Dict[NotificationPriority, List[CulturalNotification]] = {
            priority: [] for priority in NotificationPriority
        }
        
        # User notification preferences
        self.user_preferences: Dict[str, Dict[str, Any]] = {}
        
        # Delivery statistics
        self.stats = {
            "notifications_created": 0,
            "notifications_delivered": 0,
            "notifications_failed": 0,
            "delivery_attempts": 0,
            "last_delivery": None
        }
        
        # Rate limiting
        self.rate_limits = {
            NotificationPriority.LOW: timedelta(minutes=30),
            NotificationPriority.MEDIUM: timedelta(minutes=15),
            NotificationPriority.HIGH: timedelta(minutes=5),
            NotificationPriority.URGENT: timedelta(seconds=30)
        }
        
        self.last_notification_time: Dict[str, Dict[NotificationPriority, datetime]] = {}
    
    async def start(self):
        """Start the notification service."""
        try:
            self.kafka_service = await get_kafka_service()
            self.cache_service = await get_cache_service()
            
            # Load user preferences from cache
            await self._load_user_preferences()
            
            self.running = True
            
            # Start background tasks
            asyncio.create_task(self._notification_delivery_loop())
            asyncio.create_task(self._cleanup_expired_notifications())
            
            logger.info("Cultural notification service started")
            
        except Exception as e:
            logger.error(f"Failed to start notification service: {e}")
            raise
    
    async def stop(self):
        """Stop the notification service."""
        self.running = False
        logger.info("Cultural notification service stopped")
    
    async def create_notification(
        self,
        user_id: str,
        notification_type: NotificationType,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        expires_in: Optional[timedelta] = None
    ) -> str:
        """Create a new cultural notification."""
        try:
            # Check rate limiting
            if not await self._check_rate_limit(user_id, priority):
                logger.debug(f"Rate limit exceeded for user {user_id}, priority {priority.value}")
                return None
            
            # Check user preferences
            if not await self._should_send_notification(user_id, notification_type):
                logger.debug(f"User {user_id} has disabled {notification_type.value} notifications")
                return None
            
            notification_id = str(uuid.uuid4())
            expires_at = None
            if expires_in:
                expires_at = datetime.utcnow() + expires_in
            
            notification = CulturalNotification(
                notification_id=notification_id,
                user_id=user_id,
                notification_type=notification_type,
                priority=priority,
                title=title,
                message=message,
                data=data or {},
                created_at=datetime.utcnow(),
                expires_at=expires_at
            )
            
            # Add to appropriate priority queue
            self.notification_queues[priority].append(notification)
            
            # Update rate limiting
            await self._update_rate_limit(user_id, priority)
            
            # Update statistics
            self.stats["notifications_created"] += 1
            
            # Cache notification
            await self._cache_notification(notification)
            
            logger.debug(f"Created notification {notification_id} for user {user_id}")
            return notification_id
            
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            return None
    
    async def create_cultural_insight_notification(
        self,
        user_id: str,
        insight: Dict[str, Any]
    ) -> str:
        """Create a notification for a cultural insight."""
        return await self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.CULTURAL_INSIGHT,
            title="New Cultural Insight",
            message=insight.get("description", "You have a new cultural insight available"),
            data={
                "insight_id": insight.get("insight_id"),
                "insight_type": insight.get("insight_type"),
                "confidence": insight.get("confidence", 0)
            },
            priority=NotificationPriority.MEDIUM,
            expires_in=timedelta(hours=24)
        )
    
    async def create_trend_alert_notification(
        self,
        user_id: str,
        trend_data: Dict[str, Any]
    ) -> str:
        """Create a notification for a trend alert."""
        return await self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.TREND_ALERT,
            title="Cultural Trend Alert",
            message=f"New trend detected: {trend_data.get('category', 'Unknown')}",
            data=trend_data,
            priority=NotificationPriority.HIGH,
            expires_in=timedelta(hours=6)
        )
    
    async def create_diversity_milestone_notification(
        self,
        user_id: str,
        milestone_data: Dict[str, Any]
    ) -> str:
        """Create a notification for a diversity milestone."""
        return await self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.DIVERSITY_MILESTONE,
            title="Cultural Diversity Milestone",
            message=f"Congratulations! You've reached a new diversity milestone",
            data=milestone_data,
            priority=NotificationPriority.MEDIUM,
            expires_in=timedelta(hours=48)
        )
    
    async def create_recommendation_notification(
        self,
        user_id: str,
        recommendation: Dict[str, Any]
    ) -> str:
        """Create a notification for a cultural recommendation."""
        return await self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.RECOMMENDATION,
            title="Cultural Recommendation",
            message=recommendation.get("title", "You have a new cultural recommendation"),
            data=recommendation,
            priority=NotificationPriority.LOW,
            expires_in=timedelta(days=7)
        )
    
    async def _notification_delivery_loop(self):
        """Background loop for delivering notifications."""
        while self.running:
            try:
                # Process notifications by priority (highest first)
                for priority in [NotificationPriority.URGENT, NotificationPriority.HIGH, 
                               NotificationPriority.MEDIUM, NotificationPriority.LOW]:
                    
                    queue = self.notification_queues[priority]
                    if not queue:
                        continue
                    
                    # Process up to 10 notifications per priority per cycle
                    notifications_to_process = queue[:10]
                    self.notification_queues[priority] = queue[10:]
                    
                    for notification in notifications_to_process:
                        await self._deliver_notification(notification)
                
                # Wait before next delivery cycle
                await asyncio.sleep(5)  # Process every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in notification delivery loop: {e}")
                await asyncio.sleep(30)  # Wait longer on error
    
    async def _deliver_notification(self, notification: CulturalNotification):
        """Deliver a single notification."""
        try:
            # Check if notification has expired
            if notification.expires_at and notification.expires_at < datetime.utcnow():
                logger.debug(f"Notification {notification.notification_id} expired, skipping delivery")
                return
            
            # Check delivery attempts
            if notification.delivery_attempts >= notification.max_delivery_attempts:
                logger.warning(f"Max delivery attempts reached for notification {notification.notification_id}")
                self.stats["notifications_failed"] += 1
                return
            
            notification.delivery_attempts += 1
            self.stats["delivery_attempts"] += 1
            
            # Prepare notification data for Kafka
            notification_data = {
                "notification_id": notification.notification_id,
                "user_id": notification.user_id,
                "type": notification.notification_type.value,
                "priority": notification.priority.value,
                "title": notification.title,
                "message": notification.message,
                "data": notification.data,
                "created_at": notification.created_at.isoformat(),
                "delivery_attempt": notification.delivery_attempts
            }
            
            # Send to Kafka for WebSocket delivery
            success = await self.kafka_service.publish_notification(
                notification.user_id,
                notification_data
            )
            
            if success:
                notification.delivered = True
                self.stats["notifications_delivered"] += 1
                self.stats["last_delivery"] = datetime.utcnow()
                
                # Update cached notification
                await self._cache_notification(notification)
                
                logger.debug(f"Delivered notification {notification.notification_id} to user {notification.user_id}")
            else:
                # Re-queue for retry if not at max attempts
                if notification.delivery_attempts < notification.max_delivery_attempts:
                    self.notification_queues[notification.priority].append(notification)
                else:
                    self.stats["notifications_failed"] += 1
                    logger.error(f"Failed to deliver notification {notification.notification_id} after {notification.delivery_attempts} attempts")
        
        except Exception as e:
            logger.error(f"Error delivering notification {notification.notification_id}: {e}")
            # Re-queue for retry
            if notification.delivery_attempts < notification.max_delivery_attempts:
                self.notification_queues[notification.priority].append(notification)
    
    async def _check_rate_limit(self, user_id: str, priority: NotificationPriority) -> bool:
        """Check if user has exceeded rate limit for priority level."""
        if user_id not in self.last_notification_time:
            return True
        
        user_times = self.last_notification_time[user_id]
        if priority not in user_times:
            return True
        
        time_since_last = datetime.utcnow() - user_times[priority]
        return time_since_last >= self.rate_limits[priority]
    
    async def _update_rate_limit(self, user_id: str, priority: NotificationPriority):
        """Update rate limit tracking for user and priority."""
        if user_id not in self.last_notification_time:
            self.last_notification_time[user_id] = {}
        
        self.last_notification_time[user_id][priority] = datetime.utcnow()
    
    async def _should_send_notification(self, user_id: str, notification_type: NotificationType) -> bool:
        """Check if user wants to receive this type of notification."""
        preferences = self.user_preferences.get(user_id, {})
        
        # Default to enabled if no preference set
        return preferences.get(notification_type.value, True)
    
    async def _cache_notification(self, notification: CulturalNotification):
        """Cache notification for retrieval."""
        try:
            cache_key = f"notification:{notification.user_id}:{notification.notification_id}"
            await self.cache_service.set(
                cache_key,
                json.dumps(asdict(notification), default=str),
                expire=86400  # 24 hours
            )
        except Exception as e:
            logger.error(f"Error caching notification: {e}")
    
    async def _load_user_preferences(self):
        """Load user notification preferences from cache."""
        try:
            # This would typically load from database
            # For now, using default preferences
            pass
        except Exception as e:
            logger.error(f"Error loading user preferences: {e}")
    
    async def _cleanup_expired_notifications(self):
        """Clean up expired notifications from queues."""
        while self.running:
            try:
                current_time = datetime.utcnow()
                
                for priority in NotificationPriority:
                    queue = self.notification_queues[priority]
                    # Remove expired notifications
                    self.notification_queues[priority] = [
                        n for n in queue 
                        if n.expires_at is None or n.expires_at > current_time
                    ]
                
                # Wait before next cleanup
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in notification cleanup: {e}")
                await asyncio.sleep(600)  # Wait longer on error
    
    async def get_user_notifications(
        self, 
        user_id: str, 
        limit: int = 50,
        unread_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Get notifications for a user."""
        try:
            # This would typically query from database
            # For now, return from cache
            notifications = []
            
            # Get from all priority queues
            for priority in NotificationPriority:
                queue = self.notification_queues[priority]
                user_notifications = [
                    asdict(n) for n in queue 
                    if n.user_id == user_id and (not unread_only or not n.read)
                ]
                notifications.extend(user_notifications)
            
            # Sort by created_at descending
            notifications.sort(key=lambda x: x['created_at'], reverse=True)
            
            return notifications[:limit]
            
        except Exception as e:
            logger.error(f"Error getting user notifications: {e}")
            return []
    
    async def mark_notification_read(self, user_id: str, notification_id: str) -> bool:
        """Mark a notification as read."""
        try:
            # Find and update notification in queues
            for priority in NotificationPriority:
                queue = self.notification_queues[priority]
                for notification in queue:
                    if (notification.user_id == user_id and 
                        notification.notification_id == notification_id):
                        notification.read = True
                        await self._cache_notification(notification)
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            return False
    
    async def update_user_preferences(self, user_id: str, preferences: Dict[str, bool]) -> bool:
        """Update user notification preferences."""
        try:
            self.user_preferences[user_id] = preferences
            
            # Cache preferences
            cache_key = f"notification_preferences:{user_id}"
            await self.cache_service.set(
                cache_key,
                json.dumps(preferences),
                expire=86400 * 30  # 30 days
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get notification service statistics."""
        return {
            **self.stats,
            "queue_sizes": {
                priority.value: len(queue) 
                for priority, queue in self.notification_queues.items()
            },
            "active_users": len(self.user_preferences),
            "running": self.running
        }


# Global notification service instance
notification_service = CulturalNotificationService()


async def get_notification_service() -> CulturalNotificationService:
    """Get the global notification service instance."""
    return notification_service