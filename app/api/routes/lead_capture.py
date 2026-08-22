"""
Day 5 - Lead capture API.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.validation import (
    validate_contact_number,
    validate_email,
    validate_full_name,
)
from app.db.session import SessionLocal
from app.schemas.lead import (
    LeadCaptureRequest,
    LeadCaptureResponse,
)
from app.services.lead_capture_service import (
    LeadCaptureService,
)
from app.services.session_service import SessionService


router = APIRouter(
    prefix="/lead-capture",
    tags=["Lead Capture"],
)


def get_db():

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post(
    "",
    response_model=LeadCaptureResponse,
)
def capture_lead(
    request: LeadCaptureRequest,
    db: Session = Depends(get_db),
):

    session = SessionService.get_session(
        db,
        request.session_id,
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found.",
        )

    if not request.full_name:
        raise HTTPException(
            status_code=400,
            detail="Full name is required.",
        )

    if not request.email:
        raise HTTPException(
            status_code=400,
            detail="Email is required.",
        )

    if not request.contact_number:
        raise HTTPException(
            status_code=400,
            detail="Contact number is required.",
        )

    valid, error = validate_full_name(
        request.full_name
    )

    if not valid:
        raise HTTPException(
            status_code=400,
            detail=error,
        )

    valid, error = validate_email(
        request.email
    )

    if not valid:
        raise HTTPException(
            status_code=400,
            detail=error,
        )

    valid, error = validate_contact_number(
        request.contact_number
    )

    if not valid:
        raise HTTPException(
            status_code=400,
            detail=error,
        )

    data = dict(
        session.lead_data or {}
    )

    data.update({
        "full_name": request.full_name.strip(),
        "email": request.email.strip().lower(),
        "contact_number": request.contact_number.strip(),
    })

    optional_fields = {
        "company_name": request.company_name,
        "project_summary": request.project_summary,
        "required_services": request.required_services,
        "timeline": request.timeline,
        "budget_range": request.budget_range,
    }

    for key, value in optional_fields.items():

        if value is not None:
            data[key] = value

    session.lead_data = data
    session.lead_state = "COMPLETE"

    db.commit()

    lead = LeadCaptureService.create_lead(
        db=db,
        session=session,
    )

    if not lead:
        raise HTTPException(
            status_code=400,
            detail="Unable to create lead.",
        )

    return LeadCaptureResponse(
        success=True,
        lead_id=lead.id,
        lead_state="COMPLETE",
        message=(
            "Thank you. Your details have been "
            "successfully captured."
        ),
    )