// ============================================================
// MoinSystems AI Chatbot
// Day 7 - Typed API Client
//
// Responsible only for communication with FastAPI.
// No Gemini, RAG, database, SMTP, or provider logic here.
// ============================================================

import type {
  SessionCreateRequest,
  SessionCreateResponse,
  ChatRequest,
  ChatResponse,
  LeadCaptureRequest,
  LeadCaptureResponse,
} from "../types/api";


// ============================================================
// CONFIGURATION
// ============================================================

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000/api/v1";


// ============================================================
// CUSTOM API ERROR
// ============================================================

export class ApiError extends Error {
  status: number;

  constructor(
    message: string,
    status: number,
  ) {
    super(message);

    this.name = "ApiError";
    this.status = status;
  }
}


// ============================================================
// GENERIC REQUEST HELPER
// ============================================================

async function request<T>(
  endpoint: string,
  options: RequestInit = {},
): Promise<T> {

  const response = await fetch(
    `${API_BASE_URL}${endpoint}`,
    {
      ...options,

      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
    },
  );


  // ----------------------------------------------------------
  // Parse response
  // ----------------------------------------------------------

  let data: unknown = null;

  try {
    data = await response.json();
  } catch {
    data = null;
  }


  // ----------------------------------------------------------
  // Handle HTTP errors
  // ----------------------------------------------------------

  if (!response.ok) {

    let message = "Something went wrong.";

    if (
      data &&
      typeof data === "object" &&
      "detail" in data
    ) {
      const detail = (
        data as { detail?: unknown }
      ).detail;

      if (typeof detail === "string") {
        message = detail;
      }
    }

    throw new ApiError(
      message,
      response.status,
    );
  }


  return data as T;
}


// ============================================================
// SESSION API
// ============================================================

export async function createSession(
  sourcePage?: string,
): Promise<SessionCreateResponse> {

  const payload: SessionCreateRequest = {
    source_page:
      sourcePage ||
      window.location.href,
  };

  return request<SessionCreateResponse>(
    "/sessions",
    {
      method: "POST",

      body: JSON.stringify(
        payload,
      ),
    },
  );
}


// ============================================================
// CHAT API
// ============================================================

export async function sendMessage(
  payload: ChatRequest,
): Promise<ChatResponse> {

  return request<ChatResponse>(
    "/chat/messages",
    {
      method: "POST",

      body: JSON.stringify(
        payload,
      ),
    },
  );
}


// ============================================================
// LEAD CAPTURE API
// ============================================================

export async function captureLead(
  payload: LeadCaptureRequest,
): Promise<LeadCaptureResponse> {

  return request<LeadCaptureResponse>(
    "/lead-capture",
    {
      method: "POST",

      body: JSON.stringify(
        payload,
      ),
    },
  );
}