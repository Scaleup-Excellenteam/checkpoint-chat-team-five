import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, afterEach, beforeEach } from "vitest";
import GeneralRoom from "./generalroom";

vi.mock("../lib/api", () => {
  const msgs = [
    { id: "1", room: "general", content: "hello 0", sender: "a", timestamp: new Date().toISOString(), processed: true },
  ];
  return {
    fetchMessages: vi.fn().mockResolvedValue(msgs),
    sendMessage: vi.fn().mockResolvedValue({ id: "2", room: "general", content: "typed", sender: "u", timestamp: new Date().toISOString(), processed: true }),
    pollMessages: vi.fn().mockResolvedValue([]),
    openWebSocket: vi.fn().mockReturnValue({
      readyState: 0,
      close: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      set onopen(fn: any) {},
      set onmessage(fn: any) {},
      set onerror(fn: any) {},
      set onclose(fn: any) {},
      send: vi.fn(),
    }),
  };
});

describe("GeneralRoom", () => {
  it("loads initial history and renders message list", async () => {
    render(<GeneralRoom />);
    expect(await screen.findByText(/hello 0/)).toBeInTheDocument();
  });

  it("disables send on empty, enables on input, and calls send", async () => {
    const { getByPlaceholderText, getByText } = render(<GeneralRoom />);
    const input = getByPlaceholderText(/Type your message/i) as HTMLInputElement;
    const button = getByText(/Send/i) as HTMLButtonElement;
    expect(button).toBeDisabled();
    fireEvent.change(input, { target: { value: "typed" } });
    expect(button).not.toBeDisabled();
    fireEvent.click(button);
    await waitFor(() => expect(input.value).toBe(""));
  });
});


