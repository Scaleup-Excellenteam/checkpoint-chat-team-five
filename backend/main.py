from fastapi import FastAPI
from api.v1 import health, messages

app = FastAPI(title="Chat Server", version="1.0")

app.include_router(health.router, tags=["health"])
app.include_router(messages.router, prefix="/messages", tags=["messages"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
