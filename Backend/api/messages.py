from fastapi import APIRouter, HTTPException, Header, Query
from typing import Optional
from datetime import datetime
from core.logging import logger
from services.message_service import message_service
from storage.memory import storage
from schemas.message import MessageCreate, MessageResponse, MessageQuery, MessageListResponse
import asyncio

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("/", response_model=MessageResponse)
async def send_message(
    message_data: MessageCreate,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key")
):
    try:
        logger.info(f"API messages.send: room={message_data.room} sender={message_data.sender}")
        message = await message_service.create_message(
            message_data=message_data,
            idempotency_key=idempotency_key
        )
        logger.info(f"API messages.send.ok: id={message.id} room={message.room}")
        return message
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail="Failed to send message")


@router.get("/", response_model=MessageListResponse)
async def get_messages(
    room: Optional[str] = Query(None),
    since_ts: Optional[str] = Query(None),
    after_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=1000),
    sender: Optional[str] = Query(None)
):
    try:
        logger.info(
            f"API messages.get: room={room} since_ts={since_ts} after_id={after_id} limit={limit} sender={sender}"
        )
        since_datetime = None
        if since_ts:
            try:
                since_datetime = datetime.fromisoformat(since_ts.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid timestamp format")
        
        query = MessageQuery(
            room=room,
            since_ts=since_datetime,
            after_id=after_id,
            limit=limit,
            sender=sender
        )
        
        resp = await message_service.get_messages(query)
        logger.info(f"API messages.get.ok: count={resp.total} has_more={resp.has_more}")
        return resp
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        raise HTTPException(status_code=500, detail="Failed to get messages")
