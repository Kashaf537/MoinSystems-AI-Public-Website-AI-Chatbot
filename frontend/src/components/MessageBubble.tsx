interface MessageBubbleProps {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export default function MessageBubble({
  role,
  content,
  timestamp,
}: MessageBubbleProps) {
  const isUser = role === "user";

  return (
    <div
      className={`message-row ${
        isUser ? "message-row-user" : "message-row-assistant"
      }`}
    >
      <div
        className={`message-bubble ${
          isUser
            ? "message-user"
            : "message-assistant"
        }`}
      >
        <div className="message-content">
          {content}
        </div>

        <time
          className="message-time"
          dateTime={timestamp.toISOString()}
        >
          {timestamp.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </time>
      </div>
    </div>
  );
}