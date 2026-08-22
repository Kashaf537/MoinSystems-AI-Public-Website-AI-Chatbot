// ============================================================
// MoinSystems AI Chatbot
// Day 7 - Frontend API Types
//
// These types mirror the FastAPI backend schemas.
// No AI/provider/database logic belongs here.
// ============================================================


// ============================================================
// SESSION
// ============================================================

export interface SessionCreateRequest {
  source_page?: string | null;
}

export interface SessionCreateResponse {
  session_id: string;
  lead_state: string;
}


// ============================================================
// CHAT
// ============================================================

export interface HistoryMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatRequest {
  session_id: string;
  message: string;
  history?: HistoryMessage[];
  intent?: string | null;
  lead_state?: string | null;
}

export interface ChatResponse {
  response: string;
  provider: string;
  model: string;
  session_id: string;
  intent: string;
  lead_state: string;
  lead_capture_required: boolean;
}


// ============================================================
// LEAD CAPTURE
// ============================================================

export interface LeadCaptureRequest {
  session_id: string;

  full_name?: string | null;
  email?: string | null;
  contact_number?: string | null;

  company_name?: string | null;
  project_summary?: string | null;
  required_services?: string | null;
  timeline?: string | null;
  budget_range?: string | null;

  source_page?: string | null;
}

export interface LeadCaptureResponse {
  success: boolean;
  lead_id?: string | null;
  lead_state: string;
  message: string;
}


// ============================================================
// FRONTEND MESSAGE TYPE
// ============================================================

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}