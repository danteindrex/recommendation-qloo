"""
WebSocket server for real-time cultural intelligence updates.
Integrates with Kafka for real-time event streaming and notifications.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, List, Optional
import json
import asyncio
import logging
from datetime import datetime

from app.services.kafka_service import get_kafka_service, KafkaService
from app.api.dependencies.auth import get_current_user_websocket

router = APIRouter()
logger = logging.getLogger(__name__)


class CulturalWebSocketManager:
    """Enhanced WebSocket manager for cultural intelligence updates."""
    
    def __init__(self):
        # User-specific connections: user_id -> List[WebSocket]
        self.user_connections: Dict[str, List[WebSocket]] = {}
        # All active connections for broadcasting
        self.active_connections: List[WebSocket] = []
        # Connection metadata
        self.connection_metadata: Dict[WebSocket, Dict] = {}
        self.kafka_service: Optional[KafkaService] = None
        self.kafka_subscribed = False

    async def initialize_kafka(self):
        """Initialize Kafka subscriptions for real-time updates."""
        if self.kafka_subscribed:
            return
            
        try:
            self.kafka_service = await get_kafka_service()
            
            # Subscribe to cultural insights
            await self.kafka_service.subscribe_to_topic(
                "cultural-insights",
                self._handle_cultural_insight,
                "websocket-insights"
            )
            
            # Subscribe to notifications
            await self.kafka_service.subscribe_to_topic(
                "cultural-notifications", 
                self._handle_notification,
                "websocket-notifications"
            )
            
            self.kafka_subscribed = True
            logger.info("WebSocket manager initialized with Kafka subscriptions")
            
        except Exception as e:
            logger.error(f"Failed to initialize Kafka for WebSocket: {e}")

    async def connect(self, websocket: WebSocket, user_id: str, connection_type: str = "general"):
        """Connect a user's WebSocket with metadata."""
        await websocket.accept()
        
        # Add to user-specific connections
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        self.user_connections[user_id].append(websocket)
        
        # Add to all connections
        self.active_connections.append(websocket)
        
        # Store connection metadata
        self.connection_metadata[websocket] = {
            "user_id": user_id,
            "connection_type": connection_type,
            "connected_at": datetime.utcnow(),
            "last_activity": datetime.utcnow()
        }
        
        # Initialize Kafka if not already done
        await self.initialize_kafka()
        
        logger.info(f"User {user_id} connected via WebSocket ({connection_type})")

    async def disconnect(self, websocket: WebSocket):
        """Disconnect a WebSocket and clean up."""
        metadata = self.connection_metadata.get(websocket, {})
        user_id = metadata.get("user_id")
        
        # Remove from user connections
        if user_id and user_id in self.user_connections:
            if websocket in self.user_connections[user_id]:
                self.user_connections[user_id].remove(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        # Remove from active connections
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # Remove metadata
        if websocket in self.connection_metadata:
            del self.connection_metadata[websocket]
        
        logger.info(f"User {user_id} disconnected from WebSocket")

    async def send_to_user(self, user_id: str, message: Dict):
        """Send a message to all connections of a specific user."""
        if user_id not in self.user_connections:
            return
        
        message_str = json.dumps(message, default=str)
        disconnected = []
        
        for websocket in self.user_connections[user_id]:
            try:
                await websocket.send_text(message_str)
                # Update last activity
                if websocket in self.connection_metadata:
                    self.connection_metadata[websocket]["last_activity"] = datetime.utcnow()
            except Exception as e:
                logger.warning(f"Failed to send message to user {user_id}: {e}")
                disconnected.append(websocket)
        
        # Clean up disconnected websockets
        for ws in disconnected:
            await self.disconnect(ws)

    async def broadcast(self, message: Dict, connection_type: Optional[str] = None):
        """Broadcast a message to all or filtered connections."""
        message_str = json.dumps(message, default=str)
        disconnected = []
        
        for websocket in self.active_connections:
            # Filter by connection type if specified
            if connection_type:
                metadata = self.connection_metadata.get(websocket, {})
                if metadata.get("connection_type") != connection_type:
                    continue
            
            try:
                await websocket.send_text(message_str)
                # Update last activity
                if websocket in self.connection_metadata:
                    self.connection_metadata[websocket]["last_activity"] = datetime.utcnow()
            except Exception as e:
                logger.warning(f"Failed to broadcast message: {e}")
                disconnected.append(websocket)
        
        # Clean up disconnected websockets
        for ws in disconnected:
            await self.disconnect(ws)

    async def _handle_cultural_insight(self, message: Dict):
        """Handle cultural insight messages from Kafka."""
        try:
            user_id = message.get("user_id")
            insight = message.get("insight", {})
            
            if user_id:
                websocket_message = {
                    "type": "cultural_insight",
                    "data": insight,
                    "timestamp": message.get("timestamp"),
                    "user_id": user_id
                }
                await self.send_to_user(user_id, websocket_message)
                logger.debug(f"Sent cultural insight to user {user_id}")
            
        except Exception as e:
            logger.error(f"Error handling cultural insight: {e}")

    async def _handle_notification(self, message: Dict):
        """Handle notification messages from Kafka."""
        try:
            user_id = message.get("user_id")
            notification = message.get("notification", {})
            
            if user_id:
                websocket_message = {
                    "type": "notification",
                    "data": notification,
                    "timestamp": message.get("timestamp"),
                    "user_id": user_id
                }
                await self.send_to_user(user_id, websocket_message)
                logger.debug(f"Sent notification to user {user_id}")
            
        except Exception as e:
            logger.error(f"Error handling notification: {e}")

    async def send_heartbeat(self):
        """Send heartbeat to all connections to keep them alive."""
        heartbeat_message = {
            "type": "heartbeat",
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(heartbeat_message)

    def get_connection_stats(self) -> Dict:
        """Get statistics about active connections."""
        return {
            "total_connections": len(self.active_connections),
            "unique_users": len(self.user_connections),
            "connections_by_type": {
                conn_type: sum(1 for meta in self.connection_metadata.values() 
                              if meta.get("connection_type") == conn_type)
                for conn_type in set(meta.get("connection_type", "unknown") 
                                   for meta in self.connection_metadata.values())
            }
        }


# Global WebSocket manager
manager = CulturalWebSocketManager()


@router.websocket("/cultural-updates/{user_id}")
async def cultural_updates_websocket(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time cultural updates."""
    await manager.connect(websocket, user_id, "cultural_updates")
    
    try:
        # Send initial connection confirmation
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "message": "Connected to cultural updates stream",
            "timestamp": datetime.utcnow().isoformat()
        }))
        
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                message_type = message.get("type")
                
                if message_type == "ping":
                    # Respond to ping with pong
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    }))
                elif message_type == "subscribe":
                    # Handle subscription requests
                    subscription_type = message.get("subscription_type", "all")
                    await websocket.send_text(json.dumps({
                        "type": "subscription_confirmed",
                        "subscription_type": subscription_type,
                        "timestamp": datetime.utcnow().isoformat()
                    }))
                
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format",
                    "timestamp": datetime.utcnow().isoformat()
                }))
                
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        await manager.disconnect(websocket)


@router.websocket("/analytics-updates/{user_id}")
async def analytics_updates_websocket(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time analytics updates."""
    await manager.connect(websocket, user_id, "analytics_updates")
    
    try:
        # Send initial connection confirmation
        await websocket.send_text(json.dumps({
            "type": "analytics_connection_established",
            "message": "Connected to analytics updates stream",
            "timestamp": datetime.utcnow().isoformat()
        }))
        
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                # Handle analytics-specific messages
                await websocket.send_text(json.dumps({
                    "type": "analytics_response",
                    "data": message,
                    "timestamp": datetime.utcnow().isoformat()
                }))
                
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format",
                    "timestamp": datetime.utcnow().isoformat()
                }))
                
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Analytics WebSocket error for user {user_id}: {e}")
        await manager.disconnect(websocket)


@router.get("/ws/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics."""
    return manager.get_connection_stats()