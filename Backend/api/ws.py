from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from core.logging import logger
from storage.memory import storage


router = APIRouter()


class RoomManager:
    def __init__(self):
        self.room_to_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, room: str, websocket: WebSocket):
        await websocket.accept()
        if room not in self.room_to_connections:
            self.room_to_connections[room] = set()
        self.room_to_connections[room].add(websocket)

    def disconnect(self, room: str, websocket: WebSocket):
        if room in self.room_to_connections:
            self.room_to_connections[room].discard(websocket)
            if not self.room_to_connections[room]:
                del self.room_to_connections[room]

    async def broadcast(self, room: str, message: dict):
        if room not in self.room_to_connections:
            return
        dead: Set[WebSocket] = set()
        for ws in self.room_to_connections[room]:
            try:
                await ws.send_json(message)
            except Exception:
                dead.add(ws)
        for ws in dead:
            self.disconnect(room, ws)


manager = RoomManager()


@router.websocket("/ws/{room}/{sender}")
async def websocket_endpoint(websocket: WebSocket, room: str, sender: str):
    await manager.connect(room, websocket)
    logger.info(f"WS.connect: sender={sender} room={room}")
    try:
        # notify join
        await manager.broadcast(room, {"type": "join", "room": room, "sender": sender})
        while True:
            data = await websocket.receive_text()
            # store message for history via REST
            msg = storage.add_message(room=room, content=data, sender=sender)
            payload = {
                "type": "chat",
                "id": msg.id,
                "room": msg.room,
                "content": msg.content,
                "sender": msg.sender,
                "timestamp": msg.timestamp.isoformat(),
            }
            await manager.broadcast(room, payload)
    except WebSocketDisconnect:
        manager.disconnect(room, websocket)
        await manager.broadcast(room, {"type": "leave", "room": room, "sender": sender})
        logger.info(f"WS.disconnect: sender={sender} room={room}")

