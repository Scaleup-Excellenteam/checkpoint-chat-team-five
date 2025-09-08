import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { fetchMessages, sendMessage, pollMessages, openWebSocket } from "./api";

const originalFetch = globalThis.fetch;

describe("api", () => {
  beforeEach(() => {
    globalThis.fetch = vi.fn();
  });
  afterEach(() => {
    globalThis.fetch = originalFetch;
    vi.restoreAllMocks();
  });

  it("fetchMessages retrieves and returns messages list", async () => {
    (globalThis.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ messages: [{ id: "1", room: "general", content: "hi", sender: "a", timestamp: new Date().toISOString(), processed: true }], total: 1, has_more: false }),
    });
    const res = await fetchMessages("general", 1);
    expect(res.length).toBe(1);
    expect(res[0].content).toBe("hi");
  });

  it("sendMessage trims and rejects empty", async () => {
    await expect(sendMessage({ room: "general", content: "   ", sender: "a" })).rejects.toThrow(/empty/);
  });

  it("sendMessage posts and returns payload", async () => {
    (globalThis.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: "1", room: "general", content: "hi", sender: "a", timestamp: new Date().toISOString(), processed: true }),
    });
    const res = await sendMessage({ room: "general", content: "hi", sender: "a" });
    expect(res.id).toBe("1");
  });

  it("pollMessages returns messages array", async () => {
    (globalThis.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ messages: [{ id: "2", room: "general", content: "pong", sender: "b", timestamp: new Date().toISOString(), processed: true }], timeout: false }),
    });
    const res = await pollMessages({ room: "general", user: "u" });
    expect(res[0].content).toBe("pong");
  });
});


