import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";

import MessageBubble from "./MessageBubble";

describe("MessageBubble", () => {
  const timestamp = new Date(
    "2026-08-22T19:00:00"
  );

  // =========================================================
  // USER MESSAGE
  // =========================================================

  it("renders a user message", () => {
    render(
      <MessageBubble
        role="user"
        content="Hello MoinAI"
        timestamp={timestamp}
      />
    );

    expect(
      screen.getByText("Hello MoinAI")
    ).toBeInTheDocument();
  });

  // =========================================================
  // ASSISTANT MESSAGE
  // =========================================================

  it("renders an assistant message", () => {
    render(
      <MessageBubble
        role="assistant"
        content="Hello! How can I help you?"
        timestamp={timestamp}
      />
    );

    expect(
      screen.getByText(
        "Hello! How can I help you?"
      )
    ).toBeInTheDocument();
  });

  // =========================================================
  // USER CLASS
  // =========================================================

  it("applies the user message class", () => {
    const { container } = render(
      <MessageBubble
        role="user"
        content="Hello MoinAI"
        timestamp={timestamp}
      />
    );

    expect(
      container.querySelector(".message-row-user")
    ).toBeInTheDocument();

    expect(
      container.querySelector(".message-user")
    ).toBeInTheDocument();
  });

  // =========================================================
  // ASSISTANT CLASS
  // =========================================================

  it("applies the assistant message class", () => {
    const { container } = render(
      <MessageBubble
        role="assistant"
        content="Hello!"
        timestamp={timestamp}
      />
    );

    expect(
      container.querySelector(
        ".message-row-assistant"
      )
    ).toBeInTheDocument();

    expect(
      container.querySelector(
        ".message-assistant"
      )
    ).toBeInTheDocument();
  });

  // =========================================================
  // TIMESTAMP
  // =========================================================

  it("renders the message timestamp", () => {
    render(
      <MessageBubble
        role="user"
        content="Hello MoinAI"
        timestamp={timestamp}
      />
    );

    expect(
      screen.getByText("07:00 PM")
    ).toBeInTheDocument();
  });

  // =========================================================
  // SEMANTIC TIME ELEMENT
  // =========================================================

  it("renders a semantic time element", () => {
    render(
      <MessageBubble
        role="assistant"
        content="Hello!"
        timestamp={timestamp}
      />
    );

    const timeElement =
      screen.getByText("07:00 PM");

    expect(timeElement.tagName).toBe("TIME");

    expect(
      timeElement
    ).toHaveAttribute(
      "dateTime",
      timestamp.toISOString()
    );
  });
});