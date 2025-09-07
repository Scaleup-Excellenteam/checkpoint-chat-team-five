from fastapi import APIRouter
import time

router = APIRouter()
start_time = time.time()

@router.get("/health")
def health():
    uptime = int(time.time() - start_time)
    return {
        "status": "ok",
        "uptimeSec": uptime,
        "roomsCount": 0,
        "messagesCount": 0
    }
