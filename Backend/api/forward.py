from fastapi import APIRouter, HTTPException
from core.logging import logger
from storage.memory import storage
from schemas.message import ForwardConfig

router = APIRouter(prefix="/forward", tags=["forwarding"])


@router.put("/", response_model=ForwardConfig)
async def configure_forwarding(forward_config: ForwardConfig):
    try:
        config = storage.set_forward_config(
            url=forward_config.url,
            secret=forward_config.secret,
            enabled=forward_config.enabled
        )
        return ForwardConfig(url=config.url, secret=config.secret, enabled=config.enabled)
    except Exception as e:
        logger.error(f"Error configuring forwarding: {e}")
        raise HTTPException(status_code=500, detail="Failed to configure forwarding")


@router.get("/", response_model=ForwardConfig)
async def get_forwarding_config():
    try:
        config = storage.get_forward_config()
        if not config:
            raise HTTPException(status_code=404, detail="No forwarding configuration found")
        return ForwardConfig(url=config.url, secret=config.secret, enabled=config.enabled)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting forwarding config: {e}")
        raise HTTPException(status_code=500, detail="Failed to get forwarding configuration")


@router.delete("/")
async def disable_forwarding():
    try:
        config = storage.get_forward_config()
        if config:
            storage.set_forward_config(url=config.url, secret=config.secret, enabled=False)
        return {"message": "Forwarding disabled successfully"}
    except Exception as e:
        logger.error(f"Error disabling forwarding: {e}")
        raise HTTPException(status_code=500, detail="Failed to disable forwarding")
