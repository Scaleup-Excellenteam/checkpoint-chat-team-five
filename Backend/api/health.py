from fastapi import APIRouter, HTTPException
from datetime import datetime
from core.logging import logger
from storage.memory import storage
from services.socket_service import socket_server
from schemas.message import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", response_model=HealthResponse)
async def health_check():
    try:
        socket_status = socket_server.get_status()
        status = "healthy" if socket_status.running else "degraded"
        
        return HealthResponse(
            status=status,
            uptime_seconds=storage.uptime_seconds,
            room_count=storage.room_count,
            message_count=storage.message_count,
            active_connections=socket_status.active_connections,
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")
