import signal
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import settings
from core.logging import logger
from api import health, messages, forward
from api import ws as ws_routes
from api import users
from services.message_service import message_service
from services.dlp.text_validator import DLPViolation
from services.dlp.ip_validator import enforce_ip_allowed, InvalidIP


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting TSPO Chat API...")
    
    yield
    
    logger.info("Shutting down...")
    await message_service.cleanup()
    logger.info("Shutdown complete")


app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    lifespan=lifespan
)

@app.middleware("http")
async def ip_block_middleware(request: Request, call_next):
    try:
        client_ip = request.client.host if request.client else ""
        enforce_ip_allowed(client_ip)
    except InvalidIP:
        return JSONResponse(status_code=403, content={"detail": "Blocked client IP"})
    return await call_next(request)

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
app.include_router(ws_routes.router)
app.include_router(users.router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to TSPO Chat API",
        "version": settings.API_VERSION,
        "docs_url": "/docs",
    }


@app.exception_handler(DLPViolation)
async def dlp_violation_handler(request, exc: DLPViolation):
    return JSONResponse(status_code=403, content={"detail": "DLP policy violation"})


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


def signal_handler(signum, frame):
    logger.info(f"Received signal {signum}, shutting down...")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on {settings.HOST}:{settings.PORT}")
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
