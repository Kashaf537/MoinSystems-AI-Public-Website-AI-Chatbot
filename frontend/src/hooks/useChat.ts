// ============================================================
// MoinSystems AI Chatbot
// Day 7 - Chat Hook
//
// Handles:
// - Session creation
// - Session persistence
// - Chat messages
// - Loading state
// - Error state
// - Retry
// - Duplicate-click prevention
// - Request timeout
// - API/provider rate-limit handling
// - Session recovery
// ============================================================

import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";

import {
  createSession,
  sendMessage,
  ApiError,
} from "../api/client";

import type {
  ChatMessage,
  ChatResponse,
} from "../types/api";


// ============================================================
// CONSTANTS
// ============================================================

const SESSION_STORAGE_KEY =
  "moinsystems_chat_session_id";

const REQUEST_TIMEOUT_MS = 30_000;


// ============================================================
// HOOK
// ============================================================

export function useChat() {

  // ----------------------------------------------------------
  // Session
  // ----------------------------------------------------------

  const [
    sessionId,
    setSessionId,
  ] = useState<string | null>(null);


  // ----------------------------------------------------------
  // Messages
  // ----------------------------------------------------------

  const [
    messages,
    setMessages,
  ] = useState<ChatMessage[]>([]);


  // ----------------------------------------------------------
  // UI states
  // ----------------------------------------------------------

  const [
    loading,
    setLoading,
  ] = useState(false);

  const [
    initializing,
    setInitializing,
  ] = useState(true);

  const [
    error,
    setError,
  ] = useState<string | null>(null);


  // ----------------------------------------------------------
  // Last failed message
  // ----------------------------------------------------------

  const [
    lastFailedMessage,
    setLastFailedMessage,
  ] = useState<string | null>(null);


  // ----------------------------------------------------------
  // Last response metadata
  // ----------------------------------------------------------

  const [
    chatResponse,
    setChatResponse,
  ] = useState<ChatResponse | null>(null);


  // ----------------------------------------------------------
  // Request lock
  //
  // Prevents duplicate clicks before React re-renders.
  // ----------------------------------------------------------

  const requestInProgress =
    useRef(false);


  // ==========================================================
  // INITIALIZE SESSION
  // ==========================================================

  useEffect(() => {

    let cancelled = false;

    async function initialize() {

      try {

        setInitializing(true);
        setError(null);


        // ----------------------------------------------------
        // Check localStorage
        // ----------------------------------------------------

        const storedSessionId =
          localStorage.getItem(
            SESSION_STORAGE_KEY,
          );


        if (
          storedSessionId &&
          !cancelled
        ) {

          setSessionId(
            storedSessionId,
          );

          return;
        }


        // ----------------------------------------------------
        // Create new backend session
        // ----------------------------------------------------

        const session =
          await createSession(
            window.location.href,
          );


        if (cancelled) {
          return;
        }


        // ----------------------------------------------------
        // Persist session
        // ----------------------------------------------------

        localStorage.setItem(
          SESSION_STORAGE_KEY,
          session.session_id,
        );


        setSessionId(
          session.session_id,
        );

      } catch (err) {

        if (cancelled) {
          return;
        }


        console.error(
          "Session initialization failed:",
          err,
        );


        setError(
          "Unable to connect to the chatbot. Please try again.",
        );

      } finally {

        if (!cancelled) {
          setInitializing(false);
        }
      }
    }


    initialize();


    return () => {
      cancelled = true;
    };

  }, []);


  // ==========================================================
  // ADD MESSAGE
  // ==========================================================

  const addMessage = useCallback(
    (
      role: "user" | "assistant",
      content: string,
    ) => {

      const message: ChatMessage = {
        id: crypto.randomUUID(),
        role,
        content,
        timestamp: new Date(),
      };


      setMessages(
        previous => [
          ...previous,
          message,
        ],
      );

    },
    [],
  );


  // ==========================================================
  // SEND MESSAGE
  // ==========================================================

  const send = useCallback(
    async (
      message: string,
      options?: {
        isRetry?: boolean;
      },
    ): Promise<ChatResponse | null> => {

      const trimmedMessage =
        message.trim();


      const isRetry =
        options?.isRetry === true;


      // ------------------------------------------------------
      // Validate message
      // ------------------------------------------------------

      if (!trimmedMessage) {
        return null;
      }


      // ------------------------------------------------------
      // Validate session
      // ------------------------------------------------------

      if (!sessionId) {

        setError(
          "Chat session is not ready. Please try again.",
        );

        return null;
      }


      // ------------------------------------------------------
      // Prevent duplicate requests
      // ------------------------------------------------------

      if (
        loading ||
        requestInProgress.current
      ) {

        return null;
      }


      // ------------------------------------------------------
      // Lock request
      // ------------------------------------------------------

      requestInProgress.current = true;

      setError(null);


      if (!isRetry) {
        setLastFailedMessage(null);
      }


      // ------------------------------------------------------
      // Add user message
      //
      // Do NOT add it again when retrying.
      // ------------------------------------------------------

      if (!isRetry) {

        addMessage(
          "user",
          trimmedMessage,
        );
      }


      setLoading(true);


      try {

        // ====================================================
        // API REQUEST
        //
        // IMPORTANT:
        // Your existing sendMessage() accepts ONE argument.
        // Therefore we only pass the request payload here.
        // ====================================================

        const requestPromise =
          sendMessage({
            session_id: sessionId,
            message: trimmedMessage,
          });


        // ====================================================
        // TIMEOUT
        //
        // We use Promise.race() instead of AbortSignal,
        // so client.ts does NOT need to be changed.
        // ====================================================

        const timeoutPromise =
          new Promise<never>(
            (_, reject) => {

              window.setTimeout(
                () => {

                  reject(
                    new Error(
                      "CHAT_REQUEST_TIMEOUT",
                    ),
                  );

                },
                REQUEST_TIMEOUT_MS,
              );

            },
          );


        const result =
          await Promise.race([
            requestPromise,
            timeoutPromise,
          ]);


        // ----------------------------------------------------
        // Store backend response
        // ----------------------------------------------------

        setChatResponse(result);


        // ----------------------------------------------------
        // Clear failed message
        // ----------------------------------------------------

        setLastFailedMessage(null);


        // ----------------------------------------------------
        // Display assistant response
        // ----------------------------------------------------

        addMessage(
          "assistant",
          result.response,
        );


        return result;

      } catch (err) {

        console.error(
          "Chat request failed:",
          err,
        );


        // ----------------------------------------------------
        // Save failed message for retry
        // ----------------------------------------------------

        setLastFailedMessage(
          trimmedMessage,
        );


        // ====================================================
        // TIMEOUT
        // ====================================================

        if (
          err instanceof Error &&
          err.message ===
            "CHAT_REQUEST_TIMEOUT"
        ) {

          setError(
            "The request is taking too long. Please try again.",
          );
        }


        // ====================================================
        // API ERROR
        // ====================================================

        else if (
          err instanceof ApiError
        ) {

          // --------------------------------------------------
          // Session expired
          // --------------------------------------------------

          if (
            err.status === 404
          ) {

            localStorage.removeItem(
              SESSION_STORAGE_KEY,
            );


            setSessionId(null);


            setError(
              "Your chat session has expired. Please refresh the page.",
            );
          }


          // --------------------------------------------------
          // Rate limit
          // --------------------------------------------------

          else if (
            err.status === 429
          ) {

            setError(
              "The AI service is temporarily busy. Please wait a moment and try again.",
            );
          }


          // --------------------------------------------------
          // Client error
          // --------------------------------------------------

          else if (
            err.status >= 400 &&
            err.status < 500
          ) {

            setError(
              err.message ||
              "Unable to process your message.",
            );
          }


          // --------------------------------------------------
          // Server error
          // --------------------------------------------------

          else if (
            err.status >= 500
          ) {

            setError(
              "The chatbot is temporarily unavailable. Please try again.",
            );
          }


          // --------------------------------------------------
          // Unknown API error
          // --------------------------------------------------

          else {

            setError(
              "Unable to send your message. Please try again.",
            );
          }

        }


        // ====================================================
        // NETWORK ERROR
        // ====================================================

        else {

          setError(
            "Network error. Please check your connection and try again.",
          );
        }


        return null;

      } finally {

        setLoading(false);

        requestInProgress.current = false;
      }

    },
    [
      sessionId,
      loading,
      addMessage,
    ],
  );


  // ==========================================================
  // RETRY
  // ==========================================================

  const retry = useCallback(
    async () => {

      if (
        !lastFailedMessage ||
        loading ||
        requestInProgress.current
      ) {

        return;
      }


      const message =
        lastFailedMessage;


      setError(null);


      await send(
        message,
        {
          isRetry: true,
        },
      );

    },
    [
      lastFailedMessage,
      loading,
      send,
    ],
  );


  // ==========================================================
  // CLEAR CHAT
  // ==========================================================

  const clearChat = useCallback(
    async () => {

      if (
        loading ||
        requestInProgress.current
      ) {

        return;
      }


      requestInProgress.current = true;


      try {

        setLoading(true);
        setError(null);


        // ----------------------------------------------------
        // Remove old session
        // ----------------------------------------------------

        localStorage.removeItem(
          SESSION_STORAGE_KEY,
        );


        // ----------------------------------------------------
        // Create new session
        // ----------------------------------------------------

        const session =
          await createSession(
            window.location.href,
          );


        // ----------------------------------------------------
        // Persist new session
        // ----------------------------------------------------

        localStorage.setItem(
          SESSION_STORAGE_KEY,
          session.session_id,
        );


        setSessionId(
          session.session_id,
        );


        // ----------------------------------------------------
        // Reset chat
        // ----------------------------------------------------

        setMessages([]);

        setChatResponse(null);

        setLastFailedMessage(null);

      } catch (err) {

        console.error(
          "Unable to create new session:",
          err,
        );


        setError(
          "Unable to start a new chat. Please try again.",
        );

      } finally {

        setLoading(false);

        requestInProgress.current = false;
      }

    },
    [
      loading,
    ],
  );


  // ==========================================================
  // RETURN PUBLIC API
  // ==========================================================

  return {

    // Session
    sessionId,

    // Messages
    messages,

    // States
    loading,
    initializing,
    error,

    // Backend response
    chatResponse,

    // Actions
    send,
    retry,
    clearChat,

    // Retry availability
    canRetry:
      Boolean(lastFailedMessage) &&
      !loading &&
      !requestInProgress.current,
  };
}