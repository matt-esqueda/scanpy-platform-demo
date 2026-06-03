"""
WebSocket connection manager for real-time updates.
"""
import logging
import json
from typing import Dict, Set
from uuid import UUID
from fastapi import WebSocket
import redis.asyncio as aioredis

from app.core.config import settings

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections for job updates."""
    
    def __init__(self):
        self.active_connections: Dict[UUID, Set[WebSocket]] = {}
        self.redis: aioredis.Redis = None
    
    async def connect(self, websocket: WebSocket, job_id: UUID):
        """Accept and register a WebSocket connection."""
        await websocket.accept()
        
        if job_id not in self.active_connections:
            self.active_connections[job_id] = set()
        
        self.active_connections[job_id].add(websocket)
        logger.info(f"WebSocket connected for job {job_id}. Total connections: {len(self.active_connections[job_id])}")
    
    def disconnect(self, websocket: WebSocket, job_id: UUID):
        """Remove a WebSocket connection."""
        if job_id in self.active_connections:
            self.active_connections[job_id].discard(websocket)
            
            # Clean up empty sets
            if not self.active_connections[job_id]:
                del self.active_connections[job_id]
        
        logger.info(f"WebSocket disconnected for job {job_id}")
    
    async def broadcast_to_job(self, job_id: UUID, message: dict):
        """Broadcast a message to all connections for a specific job."""
        if job_id not in self.active_connections:
            return
        
        # Convert message to JSON
        json_message = json.dumps(message)
        
        # Send to all connected clients for this job
        disconnected = set()
        
        for connection in self.active_connections[job_id]:
            try:
                await connection.send_text(json_message)
            except Exception as e:
                logger.error(f"Error sending to websocket: {e}")
                disconnected.add(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection, job_id)
    
    async def setup_redis_pubsub(self):
        """Set up Redis connection for pub/sub."""
        if self.redis is None:
            self.redis = await aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
        
        return self.redis
    
    async def listen_for_updates(self):
        """Listen for job updates from Redis pub/sub and broadcast to WebSockets."""
        redis = await self.setup_redis_pubsub()
        pubsub = redis.pubsub()
        
        # Subscribe to all job update channels
        await pubsub.psubscribe("job:*:progress")
        
        logger.info("WebSocket manager listening for Redis updates")
        
        async for message in pubsub.listen():
            if message["type"] == "pmessage":
                try:
                    # Extract job_id from channel name: job:{job_id}:progress
                    channel = message["channel"]
                    job_id_str = channel.split(":")[1]
                    job_id = UUID(job_id_str)
                    
                    # Parse update data
                    data = json.loads(message["data"])
                    
                    # Broadcast to connected clients
                    await self.broadcast_to_job(job_id, data)
                    
                except Exception as e:
                    logger.error(f"Error processing Redis message: {e}")
    
    async def close(self):
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()


# Global instance
manager = ConnectionManager()