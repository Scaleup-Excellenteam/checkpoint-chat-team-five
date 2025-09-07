import { useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { Button, Input } from "../components";
import "../App.css";
import {
  fetchMessages,
  sendMessage,
  pollMessages,
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

  // start long-poll loop
  useEffect(() => {
    let cancelled = false;
    const loop = async () => {
      while (!cancelled) {
        try {
          abortRef.current?.abort();
          const controller = new AbortController();
          abortRef.current = controller;
          const incoming = await pollMessages(
            { room, user, timeoutSec: 25 },
            controller.signal
          );
          if (incoming.length) {
            // Filter out messages from the current user to avoid duplicates
            const filteredIncoming = incoming.filter(
              (msg) => msg.sender !== user
            );
            if (filteredIncoming.length) {
              setMessages((prev) => [...prev, ...filteredIncoming]);
            }
          }
        } catch (_) {
          // brief backoff on error
          await new Promise((r) => setTimeout(r, 500));
        }
      }
    };
    loop();
    return () => {
      cancelled = true;
      abortRef.current?.abort();
    };
  }, [room, user]);

  const handleSend = async () => {
    if (message.trim() === "" || sending) return;
    setSending(true);
    const content = message;
    setMessage("");
    try {
      const created = await sendMessage({ room, content, sender: user });
      setMessages((prev) => [...prev, created]);
    } catch (error) {
      console.error("Failed to send message:", error);
      // fallback: reinsert locally on failure so UI doesn't feel broken
      setMessages((prev) => [
        ...prev,
        {
          id: `tmp-${Date.now()}`,
          room,
          content,
          sender: user,
          timestamp: new Date().toISOString(),
          processed: false,
        },
      ]);
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
