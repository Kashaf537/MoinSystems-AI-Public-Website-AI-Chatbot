"""
Day 5 - Session API.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.session import (
    SessionCreateRequest,
    SessionCreateResponse,
)
from app.services.session_service import SessionService


router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"],
)


def get_db():

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post(
    "",
    response_model=SessionCreateResponse,
)
def create_session(
    request: SessionCreateRequest,
    db: Session = Depends(get_db),
):

    session = SessionService.create_session(
        db=db,
        source_page=request.source_page,
    )

    return SessionCreateResponse(
        session_id=session.id,
        lead_state=session.lead_state,
    )