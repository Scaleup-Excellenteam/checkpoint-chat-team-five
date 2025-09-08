import asyncio
import pytest


@pytest.mark.asyncio
async def test_root_and_health(async_client):
    res = await async_client.get("/")
    assert res.status_code == 200
    assert res.json()["message"].startswith("Welcome")

    res_h = await async_client.get("/health/")
    assert res_h.status_code == 200
    assert res_h.json()["status"] in {"healthy", "degraded"}


@pytest.mark.asyncio
async def test_send_and_get_messages_order_and_pagination(async_client):
    for i in range(20):
        res = await async_client.post("/messages/", json={
            "room": "general",
            "content": f"hello {i}",
            "sender": "alice",
        })
        assert res.status_code == 200
        assert res.json()["processed"] is True

    res_list = await async_client.get("/messages/", params={"room": "general", "limit": 2})
    assert res_list.status_code == 200
    payload = res_list.json()
    assert payload["total"] == 2
    assert [m["content"] for m in payload["messages"]] == ["hello 0", "hello 1"]

    after_id = payload["messages"][1]["id"]
    res_next = await async_client.get("/messages/", params={"room": "general", "after_id": after_id, "limit": 10})
    nxt = res_next.json()["messages"]

    assert len(nxt) > 0
    assert nxt[0]["content"] == "hello 2"


@pytest.mark.asyncio
async def test_edge_cases_validation_and_special_chars(async_client):
    # Empty trimmed content rejected
    res_empty = await async_client.post("/messages/", json={"room": "general", "content": "   ", "sender": "bob"})
    assert res_empty.status_code == 400

    # Overly long content rejected by pydantic validation (max_length=2000)
    res_long = await async_client.post("/messages/", json={"room": "general", "content": "x" * 5001, "sender": "bob"})
    assert res_long.status_code == 422

    # Special characters allowed subset preserved after cleaning
    res_special = await async_client.post("/messages/", json={
        "room": "general",
        "content": "Hello @$%^&*()[]{} <> /\\ 😀",
        "sender": "bob",
    })
    assert res_special.status_code == 200
    cleaned = res_special.json()["content"]
    assert "Hello" in cleaned
    assert "@" in cleaned
    assert "/" in cleaned



@pytest.mark.asyncio
async def test_idempotency_key_duplicate_rejected(async_client):
    headers = {"Idempotency-Key": "dup-key"}
    res1 = await async_client.post("/messages/", headers=headers, json={"room": "general", "content": "one", "sender": "alice"})
    assert res1.status_code == 200
    res2 = await async_client.post("/messages/", headers=headers, json={"room": "general", "content": "two", "sender": "alice"})
    assert res2.status_code == 400


