import { useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { Button, Input } from "../components";
import "../App.css";
import {
  fetchMessages,
  sendMessage,
  openWebSocket,
  type Message,
} from "../lib/api";

function GeneralRoom() {
  const room = "general";
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [sending, setSending] = useState(false);
  const user = useMemo(() => {
    // simple ephemeral user name per tab
    return `user-${Math.random().toString(36).slice(2, 8)}`;
  }, []);
  const abortRef = useRef<AbortController | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  // load initial history
  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const history = await fetchMessages(room, 50);
        if (mounted) setMessages(history);
      } catch (e) {
        // no-op for now
      }
    })();
    return () => {
      mounted = false;
    };
  }, [room]);

  // open WebSocket
  useEffect(() => {
    const ws = openWebSocket(room, user);
    wsRef.current = ws;
    ws.onopen = () => {
      // connected
    };
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "chat") {
          setMessages((prev) => [
            ...prev,
            {
              id: data.id,
              room: data.room,
              content: data.content,
              sender: data.sender,
              timestamp: data.timestamp,
              processed: true,
            },
          ]);
        }
      } catch {}
    };
    return () => {
      try {
        ws.close();
      } catch {}
      wsRef.current = null;
    };
  }, [room, user]);

  const handleSend = async () => {
    if (message.trim() === "" || sending) return;
    setSending(true);
    const content = message;
    setMessage("");
    try {
      const ws = wsRef.current;
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(content);
      } else {
        // fallback to REST persistence if WS not ready
        await sendMessage({ room, content, sender: user });
      }
    } catch (error) {
      console.error("Failed to send message:", error);
    } finally {
      setSending(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-container">
      <div className="sidebar">
        <h2>🍕 Rooms</h2>
        <div className="room-list">
          <div className="room-item active">
            <span>General</span>
            <span className="room-count">{messages.length}</span>
          </div>
          <div className="room-item">
            <span>Pizza Recipes</span>
            <span className="room-count">0</span>
          </div>
          <div className="room-item">
            <span>Toppings Debate</span>
            <span className="room-count">0</span>
          </div>
          <div className="room-item">
            <span>Restaurant Reviews</span>
            <span className="room-count">0</span>
          </div>
        </div>
        <div className="sidebar-footer">
          <Link to="/" className="back-link">
            ← Back to Home
          </Link>
        </div>
      </div>

      <div className="chat-main">
        <div className="chat-header">
          <h2>General Chat</h2>
          <p>For hating pineapple on pizza and discussing all things pizza</p>
        </div>

        <div className="messages-container">
          {messages.length === 0 ? (
            <div className="no-messages">
              <p>No messages yet. Start the conversation!</p>
              <p>
                Share your thoughts about pizza, favorite toppings, or
                restaurant recommendations.
              </p>
            </div>
          ) : (
            messages.map((msg) => (
              <div key={msg.id} className="message">
                <div className="message-content">{msg.content}</div>
                <div className="message-time">
                  {new Date(msg.timestamp).toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </div>
              </div>
            ))
          )}
        </div>

        <div className="input-container">
          <Input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Type your message about pizza..."
            className="message-input"
          />
          <Button
            onClick={handleSend}
            variant="primary"
            disabled={message.trim() === "" || sending}
            className="send-button"
          >
            Send
          </Button>
        </div>
      </div>
    </div>
  );
}

export default GeneralRoom;
