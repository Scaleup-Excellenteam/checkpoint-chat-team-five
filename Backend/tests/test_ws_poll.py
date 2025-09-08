from starlette.testclient import TestClient
from main import app


def test_websocket_broadcast_and_history_many_clients():
    client = TestClient(app)
    # Connect 20 clients to the same room
    senders = [f"user{i:02d}" for i in range(20)]
    sockets = []
    try:
        for sender in senders:
            ws = client.websocket_connect(f"/ws/general/{sender}")
            sockets.append(ws)

        # Sender 0 sends a message
        sockets[0].send_text("hello from user00")

        # Ensure that all clients eventually receive a chat message with this content
        received_count = 0
        for ws in sockets:
            found = False
            # Consume a few frames to skip join/leave notifications
            for _ in range(10):
                msg = ws.receive_json()
                if msg.get("type") == "chat" and msg.get("content") == "hello from user00":
                    found = True
                    break
            if found:
                received_count += 1

        # All connected clients (including sender) should see the broadcast
        assert received_count == len(sockets)

        # Verify message persisted in REST history
        res = client.get("/messages/", params={"room": "general", "limit": 5})
        assert res.status_code == 200
        contents = [m["content"] for m in res.json()["messages"]]
        assert "hello from user00" in contents
    finally:
        for ws in sockets:
            try:
                ws.close()
            except Exception:
                pass


