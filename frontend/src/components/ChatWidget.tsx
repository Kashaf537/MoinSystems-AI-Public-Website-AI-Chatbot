import {
  useState,
} from "react";

import {
  useChat,
} from "../hooks/useChat";

import ChatHeader from "./ChatHeader";
import MessageList from "./MessageList";
import ChatComposer from "./ChatComposer";
import LeadCapture from "./LeadCapture";


export default function ChatWidget() {

  const [
    isOpen,
    setIsOpen,
  ] = useState(false);


  const [
    isMinimized,
    setIsMinimized,
  ] = useState(false);


  const {
    messages,
    loading,
    initializing,
    error,
    send,
    retry,
    canRetry,
    chatResponse,
  } = useChat();


  // ==========================================================
  // LAUNCHER
  // ==========================================================

  if (!isOpen) {

    return (
      <button
        type="button"
        className="chat-launcher"
        onClick={() =>
          setIsOpen(true)
        }
        aria-label="Open MoinSystems AI chat"
      >
        <span className="launcher-icon">
          AI
        </span>

        <span className="launcher-text">
          Chat with us
        </span>
      </button>
    );
  }


  // ==========================================================
  // MINIMIZED STATE
  // ==========================================================

  if (isMinimized) {

    return (
      <button
        type="button"
        className="chat-minimized"
        onClick={() =>
          setIsMinimized(false)
        }
        aria-label="Restore chat"
      >
        <span className="status-dot" />
        MoinSystems AI
      </button>
    );
  }


  // ==========================================================
  // MAIN WIDGET
  // ==========================================================

  return (
    <section
      className="chat-widget"
      aria-label="MoinSystems AI chatbot"
    >

      <ChatHeader
        onMinimize={() =>
          setIsMinimized(true)
        }
        onClose={() =>
          setIsOpen(false)
        }
      />


      {initializing ? (

        <div
          className="chat-initializing"
          role="status"
          aria-live="polite"
        >
          <div className="loading-spinner" />

          <p>
            Starting chat...
          </p>
        </div>

      ) : (

        <>

          <MessageList
            messages={messages}
            loading={loading}
          />


          <LeadCapture
            active={
              chatResponse
                ?.lead_capture_required === true
            }
          />


          {error && (

            <div
              className="chat-error"
              role="alert"
            >

              <span>
                {error}
              </span>


              {canRetry && (

                <button
                  type="button"
                  onClick={retry}
                  disabled={loading}
                  className="retry-button"
                >
                  Retry
                </button>

              )}

            </div>
          )}


          <ChatComposer
            onSend={send}
            loading={loading}
            disabled={initializing}
          />

        </>
      )}

    </section>
  );
}