"""
Day 5 - Server-side lead validation.
"""

import re


EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)

PHONE_PATTERN = re.compile(
    r"^\+?[0-9][0-9\s().-]{6,19}$"
)


INVALID_EMAILS = {
    "test@test.com",
    "test@example.com",
    "example@example.com",
    "user@example.com",
    "email@example.com",
}


def validate_full_name(
    value: str,
) -> tuple[bool, str]:

    value = value.strip()

    if len(value) < 2:
        return False, "Please provide your full name."

    if len(value) > 255:
        return False, "Your name is too long."

    if not re.search(
        r"[A-Za-z]",
        value,
    ):
        return False, "Please provide a valid name."

    return True, ""


def validate_email(
    value: str,
) -> tuple[bool, str]:

    value = value.strip().lower()

    if value in INVALID_EMAILS:
        return False, "Please provide your real email address."

    if not EMAIL_PATTERN.match(value):
        return False, "That email address does not look valid."

    return True, ""


def validate_contact_number(
    value: str,
) -> tuple[bool, str]:

    value = value.strip()

    digits = re.sub(
        r"\D",
        "",
        value,
    )

    if len(digits) < 7:
        return False, "Please provide a valid contact number."

    if len(digits) > 15:
        return False, "Please provide a valid contact number."

    if not PHONE_PATTERN.match(value):
        return False, "Please provide a valid contact number."

    return True, ""