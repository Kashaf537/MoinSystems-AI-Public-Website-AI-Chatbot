"""
Day 4 - Chat API route.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)
from app.services.chat_service import ChatService


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

    try:

        service = ChatService(db)

        result = service.generate_response(
            message=request.message,
            history=[
                message.model_dump()
                for message in request.history
            ],
            intent=request.intent,
            lead_state=request.lead_state,
        )

        return ChatResponse(
            response=result.content,
            provider=result.provider,
            model=result.model,
        )

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