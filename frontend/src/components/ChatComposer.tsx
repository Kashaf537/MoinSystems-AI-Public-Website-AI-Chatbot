import { useState } from "react";

interface ChatComposerProps {
  onSend: (message: string) => Promise<unknown>;
  loading: boolean;
  disabled?: boolean;
}

export default function ChatComposer({
  onSend,
  loading,
  disabled = false,
}: ChatComposerProps) {
  const [message, setMessage] = useState("");

  async function handleSubmit(
    event: {
      preventDefault: () => void;
    },
  ) {
    event.preventDefault();

    const trimmed = message.trim();

    if (!trimmed || loading || disabled) {
      return;
    }

    setMessage("");

    await onSend(trimmed);
  }

  function handleKeyDown(
    event: {
      key: string;
      shiftKey: boolean;
      preventDefault: () => void;
      currentTarget: HTMLTextAreaElement;
    },
  ) {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();

      event.currentTarget.form?.requestSubmit();
    }
  }

  return (
    <form
      className="chat-composer"
      onSubmit={handleSubmit}
    >
      <label
        htmlFor="chat-message"
        className="sr-only"
      >
        Type your message
      </label>

      <textarea
        id="chat-message"
        value={message}
        onChange={(event) =>
          setMessage(event.target.value)
        }
        onKeyDown={handleKeyDown}
        placeholder="Type your message..."
        rows={1}
        maxLength={4000}
        disabled={loading || disabled}
        aria-label="Message"
      />

      <button
        type="submit"
        className="send-button"
        disabled={
          loading ||
          disabled ||
          !message.trim()
        }
        aria-label="Send message"
      >
        {loading ? "..." : "➤"}
      </button>
    </form>
  );
}