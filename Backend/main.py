import signal
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import settings
from core.logging import logger
from api import health, messages, forward, socket
from api import ws as ws_routes
from api import users
from services.socket_service import socket_server
from services.message_service import message_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting TSPO Chat API...")
    if socket_server.start():
        logger.info("Socket server started")
    else:
        logger.warning("Failed to start socket server")
    
    yield
    
    logger.info("Shutting down...")
    socket_server.stop()
    await message_service.cleanup()
    logger.info("Shutdown complete")


app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(messages.router)
app.include_router(forward.router)
app.include_router(socket.router)
app.include_router(ws_routes.router)
app.include_router(users.router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to TSPO Chat API",
        "version": settings.API_VERSION,
        "docs_url": "/docs",
        "socket_server": {
            "host": settings.SOCKET_HOST,
            "port": settings.SOCKET_PORT,
            "running": socket_server.running
        }
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


def signal_handler(signum, frame):
    logger.info(f"Received signal {signum}, shutting down...")
    socket_server.stop()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on {settings.HOST}:{settings.PORT}")
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
