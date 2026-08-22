
"""
Day 5 - Chat API route.

Handles:
- Server-side session validation
- Intent routing
- Message persistence
- Day 4 RAG/LLM generation
- Lead capture state machine
- Answer-first behavior
- Server-side lead validation
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.services.intent_service import IntentService
from app.services.lead_capture_service import LeadCaptureService
from app.services.session_service import SessionService


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
    #
    # IMPORTANT:
    # Once lead capture has started, the state machine gets
    # priority over RAG/LLM.
    # =========================================================

    if session.lead_state in {
        "COLLECTING_NAME",
        "COLLECTING_EMAIL",
        "COLLECTING_PHONE",
    }:

        current_field = LeadCaptureService.next_field(
            session
        )

        # -----------------------------------------------------
        # Check whether this message is actually an attempt
        # to answer the currently requested field.
        # -----------------------------------------------------

        should_process = False

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

        elif current_field == "email":

            should_process = "@" in message

        elif current_field == "contact_number":

            digits = "".join(
                char
                for char in message
                if char.isdigit()
            )

            should_process = len(digits) >= 7

        # -----------------------------------------------------
        # If the user is clearly answering the requested field,
        # process it through the deterministic state machine.
        # -----------------------------------------------------

        if should_process:

            valid, error = (
                LeadCaptureService.process_field(
                    session,
                    message,
                )
            )

            # -------------------------------------------------
            # Invalid field
            # -------------------------------------------------

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

            # -------------------------------------------------
            # All required fields collected
            # -------------------------------------------------

            if session.lead_state == "COMPLETE":

                LeadCaptureService.create_lead(
                    db=db,
                    session=session,
                )

                response_text = (
                    "Thank you. I have all the required "
                    "details and your information has been "
                    "captured successfully. Our team can "
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

            # -------------------------------------------------
            # Field accepted.
            #
            # Ask for the next required field immediately.
            # Do NOT call RAG/LLM for this.
            # -------------------------------------------------

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

        # -----------------------------------------------------
        # User is currently in lead capture but their message
        # does NOT look like an answer to the requested field.
        #
        # Do NOT send it to the LLM.
        # Remind them which field is required.
        # -----------------------------------------------------

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

        # -----------------------------------------------------
        # Get recent server-side conversation history
        # -----------------------------------------------------

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

        # Current message is already saved above.
        # ChatService adds it itself.
        if (
            history
            and history[-1]["role"] == "user"
        ):
            history = history[:-1]

        # -----------------------------------------------------
        # Generate grounded response
        # -----------------------------------------------------

        result = service.generate_response(
            message=message,
            history=history,
            intent=intent,
            lead_state=session.lead_state,
        )

        response_text = result.content

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:

        print(
            f"Chat generation error: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to generate chat response.",
        )

    # =========================================================
    # 6. Start lead capture after answering the question
    #
    # This preserves Day 5 "answer-first" behavior.
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

