import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import ChatComposer from "./ChatComposer";


describe("ChatComposer", () => {

  it("renders the message input and send button", () => {

    render(
      <ChatComposer
        onSend={vi.fn().mockResolvedValue(null)}
        loading={false}
      />
    );

    expect(
      screen.getByRole("textbox", {
        name: /message/i,
      })
    ).toBeInTheDocument();

    expect(
      screen.getByRole("button", {
        name: /send message/i,
      })
    ).toBeInTheDocument();

  });


  it("prevents sending an empty message", async () => {

    const user = userEvent.setup();

    const onSend = vi.fn().mockResolvedValue(null);

    render(
      <ChatComposer
        onSend={onSend}
        loading={false}
      />
    );

    const sendButton =
      screen.getByRole("button", {
        name: /send message/i,
      });

    expect(sendButton).toBeDisabled();

    await user.click(sendButton);

    expect(onSend).not.toHaveBeenCalled();

  });


  it("sends a valid message", async () => {

    const user = userEvent.setup();

    const onSend = vi.fn().mockResolvedValue(null);

    render(
      <ChatComposer
        onSend={onSend}
        loading={false}
      />
    );

    const input =
      screen.getByRole("textbox", {
        name: /message/i,
      });

    await user.type(
      input,
      "What is MoinAI System?"
    );

    await user.click(
      screen.getByRole("button", {
        name: /send message/i,
      })
    );

    expect(onSend).toHaveBeenCalledTimes(1);

    expect(onSend).toHaveBeenCalledWith(
      "What is MoinAI System?"
    );

  });


  it("prevents sending while loading", () => {

    render(
      <ChatComposer
        onSend={vi.fn()}
        loading={true}
      />
    );

    expect(
      screen.getByRole("textbox", {
        name: /message/i,
      })
    ).toBeDisabled();

    expect(
      screen.getByRole("button", {
        name: /send message/i,
      })
    ).toBeDisabled();

  });


  it("supports Enter to submit", async () => {

    const user = userEvent.setup();

    const onSend = vi.fn().mockResolvedValue(null);

    render(
      <ChatComposer
        onSend={onSend}
        loading={false}
      />
    );

    const input =
      screen.getByRole("textbox", {
        name: /message/i,
      });

    await user.type(
      input,
      "Hello{Enter}"
    );

    expect(onSend).toHaveBeenCalledWith(
      "Hello"
    );

  });

});