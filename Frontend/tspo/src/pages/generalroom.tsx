import { useEffect, useMemo, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button, Input } from "../components";
import "../App.css";
import { fetchMessages, openWebSocket, type Message } from "../lib/api";

function GeneralRoom() {
  const navigate = useNavigate();
  const room = "general";
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [sending, setSending] = useState(false);
  const session = useMemo(() => {
    try {
      const raw = localStorage.getItem("tspo_session");
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  }, []);
  const displayName = session?.full_name || session?.email || "user";
  const wsRef = useRef<WebSocket | null>(null);
  const seenIdsRef = useRef<Set<string>>(new Set());

  useEffect(() => {
    if (!session) {
      navigate("/login");
    }
  }, [session, navigate]);

  // load initial history
  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const history = await fetchMessages(room, 50);
        if (mounted) {
          seenIdsRef.current = new Set(history.map((m) => m.id));
          setMessages(history);
        }
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
    if (!session) return;
    const ws = openWebSocket(room, displayName);
    wsRef.current = ws;
    ws.onopen = () => {};
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "error") {
          alert(data.detail || "Message blocked by policy");
          return;
        }
        if (data.type === "chat") {
          if (!seenIdsRef.current.has(data.id)) {
            seenIdsRef.current.add(data.id);
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
        }
      } catch {}
    };
    ws.onerror = () => {};
    ws.onclose = () => {};
    return () => {
      try {
        ws.close();
      } catch {}
      wsRef.current = null;
    };
  }, [room, session, displayName]);

  const handleSend = async () => {
    const trimmed = message.trim();
    if (trimmed === "" || sending) return;
    if (trimmed.length > 100) {
      alert("Message must be 100 characters or fewer.");
      return;
    }
    setSending(true);
    setMessage("");
    try {
      const ws = wsRef.current;
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(trimmed);
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
          <div style={{ marginTop: "0.5rem" }}>
            <Link to="/logout" className="back-link">
              Logout
            </Link>
          </div>
        </div>
      </div>

      <div className="chat-main">
        <div className="chat-header">
          <h2>Welcome to the General Chat, {displayName}</h2>
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
                <div className="message-content">
                  <strong>{msg.sender}:</strong> {msg.content}
                </div>
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
            maxLength={100}
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
        <div
          style={{
            textAlign: "right",
            fontSize: "0.85em",
            color: message.length > 100 ? "#d14343" : "#777",
            marginTop: "0.25rem",
          }}
        >
          {message.length}/100
        </div>
      </div>
    </div>
  );
}

export default GeneralRoom;
