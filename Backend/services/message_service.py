import asyncio
import aiohttp
from typing import List, Optional
from core.logging import logger
from storage.memory import storage
from schemas.message import MessageCreate, MessageResponse, MessageQuery, MessageListResponse


class MessageService:
    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def create_message(self, message_data: MessageCreate, idempotency_key: Optional[str] = None) -> MessageResponse:
        try:
            # Clean the content using the MessageCreate method
            cleaned_content = message_data.clean_content()
            logger.debug(f"MessageService.create: room={message_data.room} sender={message_data.sender}")
            
            message = storage.add_message(
                room=message_data.room,
                content=cleaned_content,
                sender=message_data.sender,
                idempotency_key=idempotency_key
            )
            message.processed = True
            await self._forward_message(message)
            
            return MessageResponse(
                id=message.id,
                room=message.room,
                content=message.content,
                sender=message.sender,
                timestamp=message.timestamp,
                processed=message.processed
            )
        except Exception as e:
            logger.error(f"Error creating message: {e}")
            raise
    
    async def get_messages(self, query: MessageQuery) -> MessageListResponse:
        try:
            logger.debug(
                f"MessageService.query: room={query.room} since={query.since_ts} after_id={query.after_id} limit={query.limit} sender={query.sender}"
            )
            messages = storage.get_messages(
                room=query.room or "",
                since_ts=query.since_ts,
                after_id=query.after_id,
                limit=query.limit,
                sender=query.sender
            )
            
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
            
            return MessageListResponse(
                messages=message_responses,
                total=len(message_responses),
                has_more=len(messages) == query.limit
            )
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            raise
    
    async def _forward_message(self, message):
        forward_config = storage.get_forward_config()
        if not forward_config or not forward_config.enabled:
            return
        
        try:
            if not self._session:
                self._session = aiohttp.ClientSession()
            
            payload = {
                "id": message.id,
                "room": message.room,
                "content": message.content,
                "sender": message.sender,
                "timestamp": message.timestamp.isoformat(),
                "processed": message.processed
            }
            
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {forward_config.secret}"}
            
            async with self._session.post(forward_config.url, json=payload, headers=headers) as response:
                if response.status == 200:
                    logger.info(f"Message forwarded: {message.id}")
                else:
                    logger.warning(f"Forward failed: {response.status}")
        except Exception as e:
            logger.error(f"Error forwarding message: {e}")
    
    async def cleanup(self):
        if self._session:
            await self._session.close()
            self._session = None


message_service = MessageService()
