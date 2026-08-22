"""
Day 6 - Email service adapter.

Responsible only for sending emails through SMTP.
No lead/database logic belongs here.
"""

import smtplib
from dataclasses import dataclass
from email.message import EmailMessage

from app.core.config import get_settings


@dataclass
class EmailResult:
    """Result returned by the email provider."""

    success: bool
    provider: str
    message_id: str | None = None
    error: str | None = None
    transient: bool = False


class EmailService:
    """SMTP email adapter."""

    @staticmethod
    def send(
        subject: str,
        body: str,
        recipient: str | None = None,
    ) -> EmailResult:

        settings = get_settings()

        recipient = (
            recipient
            or settings.EMAIL_TO
        )

        message = EmailMessage()

        message["Subject"] = subject
        message["From"] = settings.EMAIL_FROM
        message["To"] = recipient

        message.set_content(body)

        try:

            print(
                f"[EMAIL] Sending notification to {recipient}"
            )

            with smtplib.SMTP(
                settings.SMTP_HOST,
                settings.SMTP_PORT,
                timeout=settings.EMAIL_TIMEOUT,
            ) as smtp:

                smtp.starttls()

                smtp.login(
                    settings.SMTP_USERNAME,
                    settings.SMTP_PASSWORD,
                )

                smtp.send_message(message)

            print(
                "[EMAIL] Notification sent successfully"
            )

            return EmailResult(
                success=True,
                provider="smtp",
                message_id=None,
                error=None,
                transient=False,
            )

        except smtplib.SMTPAuthenticationError as exc:

            print(
                "[EMAIL] SMTP authentication failed"
            )

            return EmailResult(
                success=False,
                provider="smtp",
                error="SMTP authentication failed",
                transient=False,
            )

        except (
            smtplib.SMTPServerDisconnected,
            smtplib.SMTPConnectError,
            TimeoutError,
        ) as exc:

            print(
                f"[EMAIL] Temporary SMTP failure: {type(exc).__name__}"
            )

            return EmailResult(
                success=False,
                provider="smtp",
                error="Temporary email provider failure",
                transient=True,
            )

        except smtplib.SMTPException as exc:

            print(
                f"[EMAIL] SMTP failure: {type(exc).__name__}"
            )

            return EmailResult(
                success=False,
                provider="smtp",
                error="SMTP email delivery failed",
                transient=False,
            )

        except Exception as exc:

            print(
                f"[EMAIL] Unexpected email error: {type(exc).__name__}"
            )

            return EmailResult(
                success=False,
                provider="smtp",
                error="Unexpected email delivery error",
                transient=False,
            )
