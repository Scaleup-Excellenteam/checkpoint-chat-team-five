import asyncio
import pytest
from httpx import AsyncClient

from main import app
from storage.memory import storage


@pytest.fixture(autouse=True)
def reset_storage():
    storage._messages.clear()
    storage._rooms.clear()
    storage._idempotency_keys.clear()
    storage._poll_waiters.clear()
    yield


@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


