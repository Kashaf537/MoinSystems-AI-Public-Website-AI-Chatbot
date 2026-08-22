"""
Day 5 - Deterministic lead capture state machine.

The backend, not the LLM, controls lead collection.
"""

import re
from dataclasses import dataclass
from enum import Enum


class LeadState(str, Enum):
    NONE = "NONE"
    COLLECTING_FULL_NAME = "COLLECTING_FULL_NAME"
    COLLECTING_EMAIL = "COLLECTING_EMAIL"
    COLLECTING_CONTACT_NUMBER = "COLLECTING_CONTACT_NUMBER"
    COMPLETE = "COMPLETE"


@dataclass
class LeadData:
    full_name: str | None = None
    email: str | None = None
    contact_number: str | None = None

    company_name: str | None = None
    project_summary: str | None = None
    service_interest: str | None = None
    timeline: str | None = None
    budget_range: str | None = None


class LeadStateManager:
    """
    Deterministic state machine for required lead fields.
    """

    def __init__(
        self,
        state: str | LeadState = LeadState.NONE,
        lead_data: LeadData | None = None,
    ) -> None:

        self.lead_data = lead_data or LeadData()

        try:
            self.state = LeadState(state)
        except ValueError:
            self.state = LeadState.NONE

    # =========================================================
    # Required field detection
    # =========================================================

    def next_required_state(self) -> LeadState:

        if not self.lead_data.full_name:
            return LeadState.COLLECTING_FULL_NAME

        if not self.lead_data.email:
            return LeadState.COLLECTING_EMAIL

        if not self.lead_data.contact_number:
            return LeadState.COLLECTING_CONTACT_NUMBER

        return LeadState.COMPLETE

    # =========================================================
    # Validation
    # =========================================================

    @staticmethod
    def validate_full_name(value: str) -> tuple[bool, str]:

        value = value.strip()

        if len(value) < 2:
            return False, "Please provide your full name."

        if len(value) > 255:
            return False, "Please provide a shorter name."

        if not re.fullmatch(
            r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ .'-]*",
            value,
        ):
            return False, "Please provide a valid full name."

        placeholder_values = {
            "test",
            "testing",
            "name",
            "your name",
            "john doe",
            "abc",
            "asdf",
        }

        if value.lower() in placeholder_values:
            return False, "Please provide your actual full name."

        return True, value

    @staticmethod
    def validate_email(value: str) -> tuple[bool, str]:

        value = value.strip().lower()

        if len(value) > 255:
            return False, "Please provide a valid email address."

        email_pattern = (
            r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+"
            r"@[A-Za-z0-9-]+"
            r"(?:\.[A-Za-z0-9-]+)+$"
        )

        if not re.fullmatch(email_pattern, value):
            return False, "Please provide a valid email address."

        placeholder_values = {
            "test@test.com",
            "test@example.com",
            "example@example.com",
            "user@example.com",
            "name@example.com",
        }

        if value in placeholder_values:
            return False, "Please provide your actual email address."

        return True, value

    @staticmethod
    def validate_contact_number(value: str) -> tuple[bool, str]:

        value = value.strip()

        digits = re.sub(r"\D", "", value)

        if len(digits) < 7 or len(digits) > 15:
            return False, "Please provide a valid contact number."

        # Reject obvious placeholders such as 0000000000 or 123456789
        if len(set(digits)) == 1:
            return False, "Please provide a valid contact number."

        if digits in {
            "123456789",
            "1234567890",
            "0123456789",
        }:
            return False, "Please provide a valid contact number."

        return True, value

    # =========================================================
    # Process current input
    # =========================================================

    def process(self, message: str) -> tuple[bool, str]:

        message = message.strip()

        if not message:
            return False, "Please provide the requested information."

        # -----------------------------------------------------
        # Full name
        # -----------------------------------------------------

        if self.state == LeadState.COLLECTING_FULL_NAME:

            valid, result = self.validate_full_name(message)

            if not valid:
                return False, result

            self.lead_data.full_name = result
            self.state = self.next_required_state()

            return True, self._next_prompt()

        # -----------------------------------------------------
        # Email
        # -----------------------------------------------------

        if self.state == LeadState.COLLECTING_EMAIL:

            valid, result = self.validate_email(message)

            if not valid:
                return False, result

            self.lead_data.email = result
            self.state = self.next_required_state()

            return True, self._next_prompt()

        # -----------------------------------------------------
        # Contact number
        # -----------------------------------------------------

        if self.state == LeadState.COLLECTING_CONTACT_NUMBER:

            valid, result = self.validate_contact_number(message)

            if not valid:
                return False, result

            self.lead_data.contact_number = result
            self.state = LeadState.COMPLETE

            return True, (
                "Thank you. I have all the required details and your "
                "information has been captured successfully. Our team "
                "can follow up with you regarding your project."
            )

        return False, ""

    # =========================================================
    # Prompts
    # =========================================================

    def _next_prompt(self) -> str:

        if self.state == LeadState.COLLECTING_FULL_NAME:
            return (
                "Thanks. May I have your full name?"
            )

        if self.state == LeadState.COLLECTING_EMAIL:
            return (
                "Thanks. What is the best email address to reach you?"
            )

        if self.state == LeadState.COLLECTING_CONTACT_NUMBER:
            return (
                "Thanks. What is the best contact number to reach you?"
            )

        if self.state == LeadState.COMPLETE:
            return (
                "Thank you. I have all the required details and your "
                "information has been captured successfully."
            )

        return ""

    # =========================================================
    # Start lead capture
    # =========================================================

    def start(self) -> str:

        self.state = self.next_required_state()

        return self._next_prompt()