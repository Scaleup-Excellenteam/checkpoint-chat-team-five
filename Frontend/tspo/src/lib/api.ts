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
const hostname =
  typeof window !== "undefined" && (window as any)?.location?.hostname
    ? (window as any).location.hostname
    : "localhost";
const BASE_URL =
  V.VITE_API_URL ||
  (V.VITE_SYSTEM_IP
    ? `http://${V.VITE_SYSTEM_IP}:8000`
    : `http://${hostname}:8000`);

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

export function openWebSocket(room: string, sender: string): WebSocket {
  const wsBase = (BASE_URL || "").replace(/^http/, "ws");
  return new WebSocket(
    `${wsBase.replace(/\/$/, "")}/ws/${encodeURIComponent(
      room
    )}/${encodeURIComponent(sender)}`
  );
}
