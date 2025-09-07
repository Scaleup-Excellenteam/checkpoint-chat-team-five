from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import uuid, time

router = APIRouter()

# בסיס נתונים פשוט בזיכרון
db = {"messages": []}

class MessageIn(BaseModel):
    room: str
    sender: str
    text: str

class MessageOut(MessageIn):
    id: str
    ts: int

@router.post("")
def post_message(msg: MessageIn, request: Request):
    if not msg.text.strip():
        raise HTTPException(status_code=400, detail="Empty message")

    new_msg = MessageOut(
        id=str(uuid.uuid4()),
        room=msg.room,
        sender=msg.sender,
        text=msg.text.strip(),
        ts=int(time.time() * 1000)
    )
    db["messages"].append(new_msg.dict())
    return new_msg
