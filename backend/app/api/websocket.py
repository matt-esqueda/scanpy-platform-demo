"""
WebSocket endpoints for real-time job updates.
"""
import logging
from uuid import UUID
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.scanpy import ScanpyJob
from app.core.websocket import manager

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/jobs/{job_id}")
async def websocket_job_updates(
    websocket: WebSocket,
    job_id: UUID,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time job progress updates.
    
    Connect to: ws://localhost:8000/ws/jobs/{job_id}
    
    Receives JSON messages:
    {
        "status": "executing",
        "progress_percent": 50,
        "current_step": "normalization"
    }
    """
    # Verify job exists
    job = db.query(ScanpyJob).filter(ScanpyJob.id == job_id).first()
    
    if not job:
        await websocket.close(code=4004, reason="Job not found")
        return
    
    # Accept connection
    await manager.connect(websocket, job_id)
    
    try:
        # Send initial job state
        initial_state = {
            "status": job.status.value,
            "progress_percent": job.progress_percent,
            "current_step": job.current_step,
            "type": "initial"
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