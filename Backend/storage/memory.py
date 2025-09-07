import uuid
import time
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict
from threading import Lock
from dataclasses import dataclass
from core.logging import logger
from core.config import settings


@dataclass
class Message:
    id: str
    room: str
    content: str
    sender: str
    timestamp: datetime
    processed: bool = False


@dataclass
class Room:
    name: str
    created_at: datetime
    message_count: int = 0


@dataclass
class ForwardConfig:
    url: str
    secret: str
    enabled: bool = True


class InMemoryStorage:
    def __init__(self):
        self._messages: Dict[str, List[Message]] = defaultdict(list)
        self._rooms: Dict[str, Room] = {}
        self._forward_config: Optional[ForwardConfig] = None
        self._idempotency_keys: set = set()
        self._poll_waiters: Dict[str, List] = defaultdict(list)
        self._start_time = time.time()
        self._lock = Lock()
        logger.info("Storage initialized")
    
    @property
    def uptime_seconds(self) -> float:
        return time.time() - self._start_time
    
    @property
    def room_count(self) -> int:
        return len(self._rooms)
    
    @property
    def message_count(self) -> int:
        return sum(len(messages) for messages in self._messages.values())
    
    def create_room(self, room_name: str) -> Room:
        if room_name not in self._rooms:
            self._rooms[room_name] = Room(name=room_name, created_at=datetime.utcnow())
        return self._rooms[room_name]
    
    def add_message(self, room: str, content: str, sender: str, idempotency_key: Optional[str] = None) -> Message:
        if idempotency_key and idempotency_key in self._idempotency_keys:
            raise ValueError("Duplicate idempotency key")
        
        with self._lock:
            self.create_room(room)
            message = Message(
                id=str(uuid.uuid4()),
                room=room,
                content=content,
                sender=sender,
                timestamp=datetime.utcnow()
            )
            self._messages[room].append(message)
            self._rooms[room].message_count += 1
            
            if idempotency_key:
                self._idempotency_keys.add(idempotency_key)
            
            self._notify_poll_waiters(room, message)
            return message
    
    def get_messages(self, room: str, since_ts: Optional[datetime] = None,
                    after_id: Optional[str] = None, limit: int = 50,
                    sender: Optional[str] = None) -> List[Message]:
        messages = self._messages.get(room, [])
        filtered_messages = []
        found_after_id = after_id is None
        
        for message in messages:
            if not found_after_id:
                if message.id == after_id:
                    found_after_id = True
                continue
            
            if since_ts and message.timestamp <= since_ts:
                continue
            
            if sender and message.sender != sender:
                continue
            
            filtered_messages.append(message)
            if len(filtered_messages) >= limit:
                break
        
        return filtered_messages
    
    def set_forward_config(self, url: str, secret: str, enabled: bool = True) -> ForwardConfig:
        self._forward_config = ForwardConfig(url=url, secret=secret, enabled=enabled)
        return self._forward_config
    
    def get_forward_config(self) -> Optional[ForwardConfig]:
        return self._forward_config
    
    def add_poll_waiter(self, room: str, waiter):
        self._poll_waiters[room].append(waiter)
    
    def remove_poll_waiter(self, room: str, waiter):
        if waiter in self._poll_waiters[room]:
            self._poll_waiters[room].remove(waiter)
    
    def _notify_poll_waiters(self, room: str, message: Message):
        waiters = self._poll_waiters[room].copy()
        self._poll_waiters[room].clear()
        for waiter in waiters:
            try:
                waiter.set_result([message])
            except Exception as e:
                logger.error(f"Error notifying poll waiter: {e}")


storage = InMemoryStorage()
