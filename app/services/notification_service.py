"""
Day 6 - Lead notification service.

Builds and sends a structured notification for completed leads.
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.email_notification import EmailNotification
from app.models.lead_submission import LeadSubmission
from app.services.email_service import EmailService, EmailResult


class NotificationService:
    """Creates and sends lead notification emails."""

    @staticmethod
    def build_subject(
        lead: LeadSubmission,
    ) -> str:

        return (
            f"New MoinSystems AI Lead - "
            f"{lead.full_name}"
        )

    @staticmethod
    def build_body(
        lead: LeadSubmission,
    ) -> str:

        timestamp = (
            lead.created_at
            or datetime.now(timezone.utc)
        )

        return f"""
New Lead Submission
===================

Contact Information
-------------------
Name: {lead.full_name}
Email: {lead.email}
Contact Number: {lead.contact_number}
Company: {lead.company_name or "Not provided"}

Project Information
-------------------
Service Interest: {lead.required_services or "Not provided"}
Project Summary: {lead.project_summary or "Not provided"}
Timeline: {lead.timeline or "Not provided"}
Budget: {lead.budget_range or "Not provided"}

Source
------
Source Page: {lead.source_page or "Not provided"}

Conversation Summary
--------------------
{lead.conversation_summary or "Not available"}

Submitted At
------------
{timestamp}

Lead Status
-----------
{lead.lead_status}
""".strip()

    @staticmethod
    def send_lead_notification(
        db: Session,
        lead: LeadSubmission,
    ) -> EmailResult:

        settings = get_settings()

        # -----------------------------------------------------
        # Prevent uncontrolled duplicate notifications.
        # -----------------------------------------------------

        existing = (
            db.query(EmailNotification)
            .filter(
                EmailNotification.lead_id == lead.id,
                EmailNotification.status == "sent",
            )
            .first()
        )

        if existing:

            return EmailResult(
                success=True,
                provider=existing.provider or "smtp",
                message_id=existing.provider_message_id,
            )

        notification = EmailNotification(
            lead_id=lead.id,
            recipient=settings.EMAIL_TO,
            status="pending",
            provider="smtp",
        )

        db.add(notification)
        db.commit()
        db.refresh(notification)

        # -----------------------------------------------------
        # Build notification
        # -----------------------------------------------------

        subject = NotificationService.build_subject(
            lead
        )

        body = NotificationService.build_body(
            lead
        )

        # -----------------------------------------------------
        # Send email
        # -----------------------------------------------------

        result = EmailService.send(
            subject=subject,
            body=body,
        )

        notification.provider = result.provider
        notification.error_detail = result.error

        if result.success:

            notification.status = "sent"
            notification.sent_at = datetime.now(
                timezone.utc
            )

            notification.provider_message_id = (
                result.message_id
            )

        elif result.transient:

            notification.status = "retry"

        else:

            notification.status = "failed"

        db.commit()

        return result
