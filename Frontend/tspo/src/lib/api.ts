// Minimal API client for TSPO backend

export type Message = {
  id: string;
  room: string;
  content: string;
  sender: string;
  timestamp: string;
  processed: boolean;
};

type MessageListResponse = {
  messages: Message[];
  total: number;
  has_more: boolean;
};

const V = (import.meta as any)?.env || {};
const BASE_URL =
  V.VITE_API_URL ||
  (V.VITE_SYSTEM_IP
    ? `http://${V.VITE_SYSTEM_IP}:8000`
    : "http://localhost:8000");

export async function fetchMessages(
  room: string,
  limit = 50
): Promise<Message[]> {
  const res = await fetch(
    `${BASE_URL}/messages/?room=${encodeURIComponent(room)}&limit=${limit}`
  );
  if (!res.ok) throw new Error(`Failed to fetch messages (${res.status})`);
  const data: MessageListResponse = await res.json();
  return data.messages;
}

export async function sendMessage(
  params: { room: string; content: string; sender: string },
  idempotencyKey?: string
): Promise<Message> {
  // Clean the message content
  const cleanedContent = params.content.trim();
  if (!cleanedContent) {
    throw new Error("Message content cannot be empty");
  }

  const res = await fetch(`${BASE_URL}/messages/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(idempotencyKey ? { "Idempotency-Key": idempotencyKey } : {}),
    },
    body: JSON.stringify({
      ...params,
      content: cleanedContent,
    }),
  });

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to send message (${res.status}): ${errorText}`);
  }

  return res.json();
}

export async function pollMessages(
  params: { room: string; user: string; timeoutSec?: number },
  signal?: AbortSignal
): Promise<Message[]> {
  const { room, user, timeoutSec = 30 } = params;
  const url = `${BASE_URL}/messages/poll?room=${encodeURIComponent(
    room
  )}&user=${encodeURIComponent(user)}&timeout_sec=${timeoutSec}`;
  const res = await fetch(url, { signal });
  if (!res.ok) throw new Error(`Polling failed (${res.status})`);
  const data: { messages: Message[]; timeout: boolean } = await res.json();
  return data.messages || [];
}

export function openWebSocket(room: string, sender: string): WebSocket {
  const wsBase = (BASE_URL || "").replace(/^http/, "ws");
  return new WebSocket(
    `${wsBase.replace(/\/$/, "")}/ws/${encodeURIComponent(
      room
    )}/${encodeURIComponent(sender)}`
  );
}
