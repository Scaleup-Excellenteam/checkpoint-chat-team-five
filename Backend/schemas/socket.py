from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class SocketMessageType(str, Enum):
    CHAT = "chat"
    JOIN = "join"
    LEAVE = "leave"
    ERROR = "error"
    PING = "ping"
    PONG = "pong"


class SocketMessage(BaseModel):
    type: SocketMessageType
    room: str
    sender: str
    content: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SocketConnection(BaseModel):
    client_id: str
    room: str
    sender: str
    connected_at: datetime
    last_activity: datetime


class SocketServerStatus(BaseModel):
    running: bool
    port: int
    host: str
    active_connections: int
    total_connections: int
    uptime_seconds: float


class SocketClientConfig(BaseModel):
    server_host: str
    server_port: int = 8888
    room: str
    sender: str
    timeout: int = 30
