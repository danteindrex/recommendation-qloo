"""
Kafka service for event streaming and message queuing.
Handles cultural event streaming and real-time data processing.
"""

import json
import asyncio
import logging
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from aiokafka.errors import KafkaError
from pydantic import BaseModel
import os

logger = logging.getLogger(__name__)


class CulturalEvent(BaseModel):
    """Cultural event model for Kafka messages."""
    event_id: str
    user_id: str
    event_type: str
    platform: str
    data: Dict[str, Any]
    timestamp: datetime
    confidence: float = 0.0
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class KafkaService:
    """Kafka service for cultural event streaming."""
    
    def __init__(self):
        self.bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self.producer: Optional[AIOKafkaProducer] = None
        self.consumers: Dict[str, AIOKafkaConsumer] = {}
        self.running = False
        
        # Topic configurations
        self.topics = {
            "cultural-events": "Raw cultural events from social media",
            "cultural-insights": "Processed cultural insights and patterns",
            "cultural-notifications": "Real-time notifications for users",
            "cultural-analytics": "Analytics events for dashboards"
        }
    
    async def start(self):
        """Start Kafka producer and initialize topics."""
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                compression_type="gzip"
            )
            await self.producer.start()
            self.running = True
            logger.info("Kafka producer started successfully")
            
            # Create topics if they don't exist
            await self._create_topics()
            
        except Exception as e:
            logger.error(f"Failed to start Kafka producer: {e}")
            raise
    
    async def stop(self):
        """Stop Kafka producer and consumers."""
        self.running = False
        
        if self.producer:
            await self.producer.stop()
            
        for consumer in self.consumers.values():
            await consumer.stop()
        
        self.consumers.clear()
        logger.info("Kafka service stopped")
    
    async def _create_topics(self):
        """Create Kafka topics if they don't exist."""
        # Topics are auto-created in our Kafka configuration
        # This is a placeholder for explicit topic creation if needed
        pass
    
    async def publish_cultural_event(self, event: CulturalEvent) -> bool:
        """Publish a cultural event to Kafka."""
        if not self.producer or not self.running:
            logger.error("Kafka producer not available")
            return False
        
        try:
            event_data = event.dict()
            await self.producer.send(
                "cultural-events",
                value=event_data,
                key=event.user_id.encode('utf-8')
            )
            logger.debug(f"Published cultural event: {event.event_type} for user {event.user_id}")
            return True
            
        except KafkaError as e:
            logger.error(f"Failed to publish cultural event: {e}")
            return False
    
    async def publish_cultural_insight(self, user_id: str, insight: Dict[str, Any]) -> bool:
        """Publish a cultural insight to Kafka."""
        if not self.producer or not self.running:
            logger.error("Kafka producer not available")
            return False
        
        try:
            insight_data = {
                "user_id": user_id,
                "insight": insight,
                "timestamp": datetime.utcnow().isoformat(),
                "type": "cultural_insight"
            }
            
            await self.producer.send(
                "cultural-insights",
                value=insight_data,
                key=user_id.encode('utf-8')
            )
            logger.debug(f"Published cultural insight for user {user_id}")
            return True
            
        except KafkaError as e:
            logger.error(f"Failed to publish cultural insight: {e}")
            return False
    
    async def publish_notification(self, user_id: str, notification: Dict[str, Any]) -> bool:
        """Publish a real-time notification to Kafka."""
        if not self.producer or not self.running:
            logger.error("Kafka producer not available")
            return False
        
        try:
            notification_data = {
                "user_id": user_id,
                "notification": notification,
                "timestamp": datetime.utcnow().isoformat(),
                "type": "cultural_notification"
            }
            
            await self.producer.send(
                "cultural-notifications",
                value=notification_data,
                key=user_id.encode('utf-8')
            )
            logger.debug(f"Published notification for user {user_id}")
            return True
            
        except KafkaError as e:
            logger.error(f"Failed to publish notification: {e}")
            return False
    
    async def subscribe_to_topic(
        self, 
        topic: str, 
        handler: Callable[[Dict[str, Any]], None],
        group_id: str = "cultural-processor"
    ) -> bool:
        """Subscribe to a Kafka topic with a message handler."""
        if topic in self.consumers:
            logger.warning(f"Already subscribed to topic: {topic}")
            return True
        
        try:
            consumer = AIOKafkaConsumer(
                topic,
                bootstrap_servers=self.bootstrap_servers,
                group_id=group_id,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='latest',
                enable_auto_commit=True
            )
            
            await consumer.start()
            self.consumers[topic] = consumer
            
            # Start consuming messages in background
            asyncio.create_task(self._consume_messages(topic, handler))
            
            logger.info(f"Subscribed to topic: {topic}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to subscribe to topic {topic}: {e}")
            return False
    
    async def _consume_messages(self, topic: str, handler: Callable[[Dict[str, Any]], None]):
        """Consume messages from a Kafka topic."""
        consumer = self.consumers.get(topic)
        if not consumer:
            return
        
        try:
            async for message in consumer:
                if not self.running:
                    break
                
                try:
                    await handler(message.value)
                except Exception as e:
                    logger.error(f"Error processing message from {topic}: {e}")
                    
        except Exception as e:
            logger.error(f"Error consuming from topic {topic}: {e}")
        finally:
            if topic in self.consumers:
                await self.consumers[topic].stop()
                del self.consumers[topic]


# Global Kafka service instance
kafka_service = KafkaService()


async def get_kafka_service() -> KafkaService:
    """Get the global Kafka service instance."""
    return kafka_service