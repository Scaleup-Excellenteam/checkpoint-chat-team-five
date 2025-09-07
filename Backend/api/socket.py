from fastapi import APIRouter, HTTPException
from core.logging import logger
from services.socket_service import socket_server
from schemas.socket import SocketServerStatus

router = APIRouter(prefix="/socket", tags=["socket"])


@router.post("/start", response_model=SocketServerStatus)
async def start_socket_server():
    try:
        if socket_server.running:
            return socket_server.get_status()
        
        success = socket_server.start()
        if success:
            return socket_server.get_status()
        else:
            raise HTTPException(status_code=500, detail="Failed to start socket server")
    except Exception as e:
        logger.error(f"Error starting socket server: {e}")
        raise HTTPException(status_code=500, detail="Failed to start socket server")


@router.post("/stop")
async def stop_socket_server():
    try:
        if not socket_server.running:
            return {"message": "Socket server was not running"}
        
        socket_server.stop()
        return {"message": "Socket server stopped successfully"}
    except Exception as e:
        logger.error(f"Error stopping socket server: {e}")
        raise HTTPException(status_code=500, detail="Failed to stop socket server")


@router.get("/status", response_model=SocketServerStatus)
async def get_socket_server_status():
    try:
        return socket_server.get_status()
    except Exception as e:
        logger.error(f"Error getting socket server status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get server status")
