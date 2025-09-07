from fastapi import APIRouter, HTTPException, Header, Query
from typing import Optional
from datetime import datetime
from core.logging import logger
from services.message_service import message_service
from storage.memory import storage
from schemas.message import MessageCreate, MessageResponse, MessageQuery, MessageListResponse, PollResponse
import asyncio

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("/", response_model=MessageResponse)
async def send_message(
    message_data: MessageCreate,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key")
):
    try:
        message = await message_service.create_message(
            message_data=message_data,
            idempotency_key=idempotency_key
        )
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
        
        return await message_service.get_messages(query)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        raise HTTPException(status_code=500, detail="Failed to get messages")


@router.get("/poll", response_model=PollResponse)
async def poll_messages(
    room: str = Query(...),
    user: str = Query(...),
    timeout_sec: int = Query(30, ge=1, le=300)
):
    try:
        future = asyncio.Future()
        storage.add_poll_waiter(room, future)
        
        try:
            messages = await asyncio.wait_for(future, timeout=timeout_sec)
            message_responses = [
                MessageResponse(
                    id=msg.id,
                    room=msg.room,
                    content=msg.content,
                    sender=msg.sender,
                    timestamp=msg.timestamp,
                    processed=msg.processed
                )
                for msg in messages
            ]
            
            return PollResponse(
                messages=message_responses,
                timeout=False,
                timestamp=datetime.utcnow()
            )
        except asyncio.TimeoutError:
            storage.remove_poll_waiter(room, future)
            return PollResponse(
                messages=[],
                timeout=True,
                timestamp=datetime.utcnow()
            )
    except Exception as e:
        logger.error(f"Error in polling: {e}")
        raise HTTPException(status_code=500, detail="Polling failed")
