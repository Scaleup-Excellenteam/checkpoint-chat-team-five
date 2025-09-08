from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
import re


class MessageCreate(BaseModel):
    room: str = Field(..., min_length=1, max_length=20)
    content: str = Field(..., min_length=1, max_length=100)
    sender: str = Field(..., min_length=1, max_length=20)
    
    def clean_content(self):
        if not self.content or not self.content.strip():
            raise ValueError('Message content cannot be empty')
        cleaned = re.sub(r'[^\w\s.,!?@#$%^&*()_+\-=\[\]{}|;:"<>/\\]', '', self.content)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        if len(cleaned) < 1:
            raise ValueError('Message content is too short after cleaning')
        return cleaned


class MessageResponse(BaseModel):
    id: str
    room: str
    content: str
    sender: str
    timestamp: datetime
    processed: bool = False


class MessageQuery(BaseModel):
    room: Optional[str] = None
    since_ts: Optional[datetime] = None
    after_id: Optional[str] = None
    limit: int = Field(default=50, ge=1, le=1000)
    sender: Optional[str] = None


class MessageListResponse(BaseModel):
    messages: List[MessageResponse]
    total: int
    has_more: bool


class HealthResponse(BaseModel):
    status: str
    uptime_seconds: float
    room_count: int
    message_count: int
    timestamp: datetime


class ForwardConfig(BaseModel):
    url: str
    secret: str
    enabled: bool = True

