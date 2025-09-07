import React, { useState } from "react";

function GeneralRoom() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<string[]>([]);

  const handleSend = () => {
    if (message.trim() === "") return;
    setMessages([...messages, message]);
    setMessage("");
  };

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      {/* Left side: rooms */}
      <div
        style={{
          width: "200px",
          borderRight: "1px solid #ccc",
          padding: "1em",
        }}
      >
        <h3>Rooms</h3>
        {/* Future room list goes here */}
      </div>

      {/* Right side: chat */}
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          padding: "1em",
        }}
      >
        <h2>General chat for hating pineapple on pizza</h2>

        {/* Messages area */}
        <div
          style={{
            flex: 1,
            border: "1px solid #ccc",
            borderRadius: "8px",
            padding: "1em",
            marginBottom: "1em",
            overflowY: "auto",
          }}
        >
          {messages.length === 0 && <p>No messages yet.</p>}
          {messages.map((msg, index) => (
            <p key={index}>{msg}</p>
          ))}
        </div>

        {/* Input area */}
        <div style={{ display: "flex", gap: "0.5em" }}>
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Type a message..."
            style={{ flex: 1, padding: "0.5em" }}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
          />
          <button onClick={handleSend}>Send</button>
        </div>
      </div>
    </div>
  );
}

export default GeneralRoom;
