import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport

from main import app
from storage.memory import storage


@pytest.fixture(autouse=True)
def reset_storage():
    storage._messages.clear()
    storage._rooms.clear()
    storage._idempotency_keys.clear()
    yield


@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

@pytest.fixture
def host():
    return "localhost"

@pytest.fixture
def port():
    return 8000