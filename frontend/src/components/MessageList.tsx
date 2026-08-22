import {
  useEffect,
  useRef
} from "react";

import type {
  ChatMessage,
} from "../types/api";

import MessageBubble from "./MessageBubble";

interface MessageListProps {
  messages: ChatMessage[];
  loading: boolean;
}

export default function MessageList({
  messages,
  loading,
}: MessageListProps) {

  const bottomRef =
    useRef<HTMLDivElement | null>(null);


useEffect(() => {
  if (bottomRef.current) {
    bottomRef.current.scrollIntoView?.({
      behavior: "smooth",
    });
  }
}, [messages, loading]);


  return (
    <main
      className="message-list"
      aria-live="polite"
      aria-label="Chat messages"
    >

      {messages.length === 0 && (
        <div className="welcome-message">
          <div className="welcome-icon">
            AI
          </div>

          <h3>
            Welcome to MoinSystems AI
          </h3>

          <p>
            Ask me about our services,
            projects, pricing, or anything
            else you'd like to know.
          </p>
        </div>
      )}


      {messages.map((message) => (
        <MessageBubble
          key={message.id}
          role={message.role}
          content={message.content}
          timestamp={message.timestamp}
        />
      ))}


      {loading && (
        <div
          className="message-row message-row-assistant"
          aria-label="Assistant is typing"
        >
          <div className="message-bubble message-assistant typing-indicator">
            <span />
            <span />
            <span />
          </div>
        </div>
      )}


      <div ref={bottomRef} />

    </main>
  );
}