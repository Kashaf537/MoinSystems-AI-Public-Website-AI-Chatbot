"""
Day 5 - Deterministic lead capture state machine.
"""

import uuid

from sqlalchemy.orm import Session

from app.core.validation import (
    validate_contact_number,
    validate_email,
    validate_full_name,
)
from app.models.chat_session import ChatSession
from app.models.lead_submission import LeadSubmission


class LeadCaptureService:

    STATES = {
        "NONE",
        "COLLECTING_NAME",
        "COLLECTING_EMAIL",
        "COLLECTING_PHONE",
        "COMPLETE",
    }

    @staticmethod
    def start_capture(
        session: ChatSession,
    ) -> None:

        if session.lead_state == "NONE":

            session.lead_state = "COLLECTING_NAME"

            if not session.lead_data:
                session.lead_data = {}

    @staticmethod
    def next_field(
        session: ChatSession,
    ) -> str | None:

        data = session.lead_data or {}

        if not data.get("full_name"):
            return "full_name"

        if not data.get("email"):
            return "email"

        if not data.get("contact_number"):
            return "contact_number"

        return None

    @staticmethod
    def question_for(
        field: str,
    ) -> str:

        questions = {
            "full_name": (
                "To prepare a quote, may I have your full name?"
            ),
            "email": (
                "Thanks. What email address should we use "
                "to contact you?"
            ),
            "contact_number": (
                "And what is the best contact number "
                "to reach you?"
            ),
        }

        return questions[field]

    @classmethod
    def process_field(
        cls,
        session: ChatSession,
        value: str,
    ) -> tuple[bool, str]:

        field = cls.next_field(session)

        if field is None:
            session.lead_state = "COMPLETE"
            return True, ""

        data = dict(
            session.lead_data or {}
        )

        if field == "full_name":

            valid, error = validate_full_name(
                value
            )

            if not valid:
                return False, error

            data["full_name"] = value.strip()

        elif field == "email":

            valid, error = validate_email(
                value
            )

            if not valid:
                return False, error

            data["email"] = value.strip().lower()

        elif field == "contact_number":

            valid, error = validate_contact_number(
                value
            )

            if not valid:
                return False, error

            data["contact_number"] = value.strip()

        session.lead_data = data

        next_field = cls.next_field(session)

        if next_field is None:
            session.lead_state = "COMPLETE"
        elif next_field == "full_name":
            session.lead_state = "COLLECTING_NAME"
        elif next_field == "email":
            session.lead_state = "COLLECTING_EMAIL"
        elif next_field == "contact_number":
            session.lead_state = "COLLECTING_PHONE"

        return True, ""

    @staticmethod
    def create_lead(
        db: Session,
        session: ChatSession,
    ) -> LeadSubmission | None:

        data = session.lead_data or {}

        required = [
            "full_name",
            "email",
            "contact_number",
        ]

        if not all(
            data.get(field)
            for field in required
        ):
            return None

        # Prevent duplicate lead creation.
        existing = (
            db.query(LeadSubmission)
            .filter(
                LeadSubmission.session_id == session.id
            )
            .first()
        )

        if existing:
            return existing

        lead = LeadSubmission(
            id=uuid.uuid4(),
            session_id=session.id,
            full_name=data["full_name"],
            email=data["email"],
            contact_number=data["contact_number"],
            company_name=data.get("company_name"),
            project_summary=data.get(
                "project_summary"
            ),
            required_services=data.get(
                "required_services"
            ),
            timeline=data.get("timeline"),
            budget_range=data.get(
                "budget_range"
            ),
            source_page=session.source_page,
            conversation_summary=data.get(
                "conversation_summary"
            ),
            lead_status="New",
        )

        db.add(lead)

        session.lead_state = "COMPLETE"

        db.commit()
        db.refresh(lead)

        return lead