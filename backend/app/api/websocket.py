"""
WebSocket endpoints for real-time job updates.
"""
import logging
from uuid import UUID
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.websocket import manager

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/jobs/{job_id}")
async def websocket_job_updates(
    websocket: WebSocket,
    job_id: UUID
):
    """
    WebSocket endpoint for real-time job progress updates.
    
    Connect to: ws://localhost:8000/ws/jobs/{job_id}
    
    Receives JSON messages with job updates.
    """
    try:
        # Accept connection immediately (no database query needed)
        await manager.connect(websocket, job_id)
        
        # Send a simple initial message
        initial_state = {
            "type": "connected",
            "job_id": str(job_id),
            "message": "WebSocket connected, waiting for updates..."
        }
        await websocket.send_json(initial_state)
        
        # Keep connection alive and wait for client messages (ping/pong)
        while True:
            # Wait for client messages (optional - can be used for ping/pong)
            data = await websocket.receive_text()
            
            # Echo back for keepalive
            if data == "ping":
                await websocket.send_text("pong")
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, job_id)
        logger.info(f"Client disconnected from job {job_id}")
    
    except Exception as e:
        logger.error(f"WebSocket error for job {job_id}: {e}")
        manager.disconnect(websocket, job_id)