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
export const API_BASE_URL =
  V.VITE_API_URL ||
  (V.VITE_SYSTEM_IP
    ? `http://${V.VITE_SYSTEM_IP}:8000`
    : `http://${hostname}:8000`);

export async function fetchMessages(
  room: string,
  limit = 50
): Promise<Message[]> {
  const res = await fetch(
    `${API_BASE_URL}/messages/?room=${encodeURIComponent(room)}&limit=${limit}`
  );
  if (!res.ok) throw new Error(`Failed to fetch messages (${res.status})`);
  const data: MessageListResponse = await res.json();
  return data.messages;
}

export function openWebSocket(room: string, sender: string): WebSocket {
  const wsBase = (API_BASE_URL || "").replace(/^http/, "ws");
  return new WebSocket(
    `${wsBase.replace(/\/$/, "")}/ws/${encodeURIComponent(
      room
    )}/${encodeURIComponent(sender)}`
  );
}
