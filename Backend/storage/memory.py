import uuid
import time
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict
from threading import Lock
from dataclasses import dataclass
from core.logging import logger
from core.config import settings
from pathlib import Path
import json


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
        self._start_time = time.time()
        self._lock = Lock()
        # simple JSON-backed user store
        repo_root = Path(__file__).resolve().parents[2]
        self._data_dir = repo_root / "Data"
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._users_path = self._data_dir / "users.json"
        self._users: Dict[str, Dict] = self._load_users()
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

    # === DLP Guard: URL validation (לפני lock, ללא רשת) ===
    try:
        validate_urls_in_text(content)  # יזרוק InvalidUrl אם יש לפחות URL אחד לא תקין
    except InvalidUrl as e:
        # בשכבת ה-API/route נמפה ל-422/400; כאן רק מונעים כניסה לחדר
        logger.warning(f"DLP invalid URL blocked: {e}")
        raise
    # === END DLP Guard ===

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

    # ---- Users (JSON-backed) ----
    def _load_users(self) -> Dict[str, Dict]:
        try:
            if self._users_path.exists():
                return json.loads(self._users_path.read_text(encoding="utf-8")) or {}
        except Exception as e:
            logger.error(f"Failed to load users.json: {e}")
        return {}

    def _persist_users(self) -> None:
        try:
            self._users_path.write_text(json.dumps(self._users, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to persist users.json: {e}")

    def create_user(self, email: str, full_name: str, password: str) -> Dict:
        if email in self._users:
            raise ValueError("User already exists")
        user = {"email": email, "full_name": full_name, "password": password}
        self._users[email] = user
        self._persist_users()
        logger.info(f"Storage.user.created: email={email}")
        return user

    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        user = self._users.get(email)
        if user and user.get("password") == password:
            logger.debug(f"Storage.user.auth.ok: email={email}")
            return user
        logger.debug(f"Storage.user.auth.fail: email={email}")
        return None

    def get_user(self, email: str) -> Optional[Dict]:
        return self._users.get(email)
    
    def set_forward_config(self, url: str, secret: str, enabled: bool = True) -> ForwardConfig:
        self._forward_config = ForwardConfig(url=url, secret=secret, enabled=enabled)
        return self._forward_config
    
    def get_forward_config(self) -> Optional[ForwardConfig]:
        return self._forward_config
    
    


storage = InMemoryStorage()
