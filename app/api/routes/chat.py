"""
Day 5 + Day 6 - Chat API route.

Handles:
- Server-side session validation
- Intent routing
- Message persistence
- Day 4 RAG/LLM generation
- Lead capture state machine
- Answer-first behavior
- Server-side lead validation
- Day 6 lead email notification
- False-success prevention
- Day 6 rate limiting
- Provider quota/rate-limit handling
"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
)

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.chat import ChatRequest, ChatResponse

from app.services.chat_service import ChatService
from app.services.intent_service import IntentService
from app.services.lead_capture_service import LeadCaptureService
from app.services.notification_service import NotificationService
from app.services.session_service import SessionService

from app.core.rate_limiter import (
    RateLimitExceeded,
    rate_limiter,
)


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post(
    "/messages",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
    request_obj: Request,
    db: Session = Depends(get_db),
) -> ChatResponse:

    # =========================================================
    # 1. Validate session
    # =========================================================

    session = SessionService.get_session(
        db,
        request.session_id,
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found.",
        )

    # =========================================================
    # 1.1 Day 6 - Rate limiting
    # =========================================================
    #
    # Apply both:
    # - Per-IP limiting
    # - Per-session limiting
    #
    # This protects the LLM-backed endpoint from abuse.
    # =========================================================

    client_ip = (
        request_obj.client.host
        if request_obj.client
        else "unknown"
    )

    try:

        rate_limiter.check(
            ip_address=client_ip,
            session_id=str(request.session_id),
        )

    except RateLimitExceeded as exc:

        raise HTTPException(
            status_code=429,
            detail=exc.message,
            headers={
                "Retry-After": "60",
            },
        )

    # =========================================================
    # 1.2 Validate message
    # =========================================================

    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    # =========================================================
    # 2. Detect intent
    # =========================================================

    intent = IntentService.classify(message)

    session.current_intent = intent

    # =========================================================
    # 3. Save visitor message
    # =========================================================

    SessionService.add_message(
        db=db,
        session=session,
        role="user",
        content=message,
        intent=intent,
        lead_state=session.lead_state,
    )

    # =========================================================
    # 4. Lead-capture state machine
    # =========================================================

    if session.lead_state in {
        "COLLECTING_NAME",
        "COLLECTING_EMAIL",
        "COLLECTING_PHONE",
    }:

        current_field = LeadCaptureService.next_field(
            session
        )

        should_process = False

        # =====================================================
        # Full name
        # =====================================================

        if current_field == "full_name":

            should_process = (
                len(message.split()) <= 6
                and "?" not in message
                and not any(
                    word in message.lower().split()
                    for word in {
                        "what",
                        "how",
                        "why",
                        "can",
                        "do",
                        "does",
                        "is",
                        "are",
                    }
                )
            )

        # =====================================================
        # Email
        # =====================================================

        elif current_field == "email":

            # Always pass the value to the validation service.
            # Do not perform weak frontend-style validation here.
            should_process = True

        # =====================================================
        # Contact number
        # =====================================================

        elif current_field == "contact_number":

            digits = "".join(
                char
                for char in message
                if char.isdigit()
            )

            should_process = len(digits) >= 7

        # =====================================================
        # Process lead field
        # =====================================================

        if should_process:

            valid, error = (
                LeadCaptureService.process_field(
                    session,
                    message,
                )
            )

            # =================================================
            # Invalid field
            # =================================================

            if not valid:

                SessionService.add_message(
                    db=db,
                    session=session,
                    role="assistant",
                    content=error,
                    intent=intent,
                    lead_state=session.lead_state,
                )

                db.commit()

                return ChatResponse(
                    response=error,
                    provider="state_machine",
                    model="none",
                    session_id=session.id,
                    intent=intent,
                    lead_state=session.lead_state,
                    lead_capture_required=True,
                )

            # =================================================
            # All required fields collected
            # =================================================

            if session.lead_state == "COMPLETE":

                # -------------------------------------------------
                # Create lead
                # -------------------------------------------------

                lead = LeadCaptureService.create_lead(
                    db=db,
                    session=session,
                )

                if not lead:

                    raise HTTPException(
                        status_code=500,
                        detail="Unable to create lead submission.",
                    )

                # -------------------------------------------------
                # Day 6 - Send notification
                # -------------------------------------------------

                try:

                    notification_result = (
                        NotificationService.send_lead_notification(
                            db=db,
                            lead=lead,
                        )
                    )

                except Exception as exc:

                    print(
                        f"Lead notification error: {exc}"
                    )

                    notification_result = None

                # =================================================
                # Notification SUCCESS
                # =================================================

                if (
                    notification_result
                    and notification_result.success
                ):

                    response_text = (
                        "Thank you. I have all the required "
                        "details and your information has been "
                        "submitted successfully. Our team will "
                        "follow up with you regarding your project."
                    )

                    SessionService.add_message(
                        db=db,
                        session=session,
                        role="assistant",
                        content=response_text,
                        intent=intent,
                        lead_state="COMPLETE",
                    )

                    db.commit()

                    return ChatResponse(
                        response=response_text,
                        provider="state_machine",
                        model="none",
                        session_id=session.id,
                        intent=intent,
                        lead_state="COMPLETE",
                        lead_capture_required=False,
                    )

                # =================================================
                # Notification FAILURE
                # =================================================

                response_text = (
                    "Thank you. I have securely saved the details "
                    "you provided, but I was unable to complete "
                    "the notification to our team right now. "
                    "Please try submitting again later."
                )

                SessionService.add_message(
                    db=db,
                    session=session,
                    role="assistant",
                    content=response_text,
                    intent=intent,
                    lead_state="COMPLETE",
                )

                db.commit()

                return ChatResponse(
                    response=response_text,
                    provider="state_machine",
                    model="none",
                    session_id=session.id,
                    intent=intent,
                    lead_state="COMPLETE",
                    lead_capture_required=False,
                )

            # =================================================
            # Field accepted
            # =================================================

            next_field = LeadCaptureService.next_field(
                session
            )

            response_text = (
                LeadCaptureService.question_for(
                    next_field
                )
            )

            SessionService.add_message(
                db=db,
                session=session,
                role="assistant",
                content=response_text,
                intent=intent,
                lead_state=session.lead_state,
            )

            db.commit()

            return ChatResponse(
                response=response_text,
                provider="state_machine",
                model="none",
                session_id=session.id,
                intent=intent,
                lead_state=session.lead_state,
                lead_capture_required=True,
            )

        # =====================================================
        # User did not answer requested field
        # =====================================================

        response_text = LeadCaptureService.question_for(
            current_field
        )

        SessionService.add_message(
            db=db,
            session=session,
            role="assistant",
            content=response_text,
            intent=intent,
            lead_state=session.lead_state,
        )

        db.commit()

        return ChatResponse(
            response=response_text,
            provider="state_machine",
            model="none",
            session_id=session.id,
            intent=intent,
            lead_state=session.lead_state,
            lead_capture_required=True,
        )

    # =========================================================
    # 5. Normal Day 4 RAG + LLM flow
    # =========================================================

    try:

        service = ChatService(db)

        recent_messages = (
            SessionService.get_recent_messages(
                db=db,
                session=session,
                limit=6,
            )
        )

        history = [
            {
                "role": item.role,
                "content": item.content,
            }
            for item in recent_messages
            if item.role in {
                "user",
                "assistant",
            }
        ]

        # Current message already saved above.
        if (
            history
            and history[-1]["role"] == "user"
        ):
            history = history[:-1]

        result = service.generate_response(
            message=message,
            history=history,
            intent=intent,
            lead_state=session.lead_state,
        )

        response_text = result.content

    except ValueError as exc:

        # -----------------------------------------------------
        # Validation / application-level errors
        # -----------------------------------------------------

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:

        # -----------------------------------------------------
        # Provider / generation error handling
        # -----------------------------------------------------
        #
        # Gemini may return errors such as:
        #
        #   429 RESOURCE_EXHAUSTED
        #   quota exceeded
        #   rate limit exceeded
        #
        # These should NOT become HTTP 500 because they represent
        # temporary provider capacity/quota problems.
        # -----------------------------------------------------

        error_text = str(exc)

        print(
            f"Chat generation error: {error_text}"
        )

        # =====================================================
        # Provider quota / rate-limit error
        # =====================================================

        if (
            "429" in error_text
            or "RESOURCE_EXHAUSTED" in error_text
            or "quota" in error_text.lower()
            or "rate limit" in error_text.lower()
        ):

            raise HTTPException(
                status_code=429,
                detail=(
                    "The AI service is temporarily at capacity. "
                    "Please try again shortly."
                ),
                headers={
                    "Retry-After": "30",
                },
            )

        # =====================================================
        # Other generation/provider errors
        # =====================================================

        raise HTTPException(
            status_code=500,
            detail="Unable to generate chat response.",
        )

    # =========================================================
    # 6. Start lead capture after answering
    # =========================================================

    if (
        intent in {
            "pricing",
            "high_intent",
        }
        and session.lead_state == "NONE"
    ):

        LeadCaptureService.start_capture(
            session
        )

        response_text = (
            response_text.rstrip()
            + "\n\n"
            + LeadCaptureService.question_for(
                "full_name"
            )
        )

    # =========================================================
    # 7. Save assistant response
    # =========================================================

    SessionService.add_message(
        db=db,
        session=session,
        role="assistant",
        content=response_text,
        intent=intent,
        lead_state=session.lead_state,
    )

    db.commit()

    # =========================================================
    # 8. Return structured response
    # =========================================================

    return ChatResponse(
        response=response_text,
        provider=result.provider,
        model=result.model,
        session_id=session.id,
        intent=intent,
        lead_state=session.lead_state,
        lead_capture_required=(
            session.lead_state
            not in {
                "NONE",
                "COMPLETE",
            }
        ),
    )