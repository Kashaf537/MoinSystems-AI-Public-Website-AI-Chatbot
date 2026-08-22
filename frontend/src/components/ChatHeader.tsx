interface ChatHeaderProps {
  onMinimize: () => void;
  onClose: () => void;
}

export default function ChatHeader({
  onMinimize,
  onClose,
}: ChatHeaderProps) {
  return (
    <header className="chat-header">
      <div className="chat-header-info">
        <div className="chat-avatar">
          AI
        </div>

        <div>
          <h2>MoinSystems AI</h2>

          <span className="chat-status">
            <span className="status-dot" />
            Online
          </span>
        </div>
      </div>

      <div className="chat-header-actions">
        <button
          type="button"
          className="icon-button"
          onClick={onMinimize}
          aria-label="Minimize chat"
          title="Minimize"
        >
          −
        </button>

        <button
          type="button"
          className="icon-button"
          onClick={onClose}
          aria-label="Close chat"
          title="Close"
        >
          ×
        </button>
      </div>
    </header>
  );
}