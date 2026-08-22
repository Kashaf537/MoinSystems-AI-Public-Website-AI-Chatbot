"""
Day 5 - Session management and message persistence.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession


class SessionService:

    @staticmethod
    def create_session(
        db: Session,
        source_page: str | None = None,
    ) -> ChatSession:

        session = ChatSession(
            id=uuid.uuid4(),
            source_page=source_page,
            lead_state="NONE",
            current_intent=None,
            lead_data={},
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        return session

    @staticmethod
    def get_session(
        db: Session,
        session_id: uuid.UUID,
    ) -> ChatSession | None:

        return (
            db.query(ChatSession)
            .filter(
                ChatSession.id == session_id
            )
            .first()
        )

    @staticmethod
    def update_state(
        db: Session,
        session: ChatSession,
        intent: str | None = None,
        lead_state: str | None = None,
        lead_data: dict | None = None,
    ) -> ChatSession:

        if intent is not None:
            session.current_intent = intent

        if lead_state is not None:
            session.lead_state = lead_state

        if lead_data is not None:
            session.lead_data = lead_data

        session.last_active_at = datetime.now(
            timezone.utc
        )

        db.commit()
        db.refresh(session)

        return session

    @staticmethod
    def add_message(
        db: Session,
        session: ChatSession,
        role: str,
        content: str,
        intent: str | None = None,
        lead_state: str | None = None,
    ) -> ChatMessage:

        message = ChatMessage(
            session_id=session.id,
            role=role,
            content=content,
            intent=intent,
            lead_state=lead_state,
        )

        db.add(message)

        session.last_active_at = datetime.now(
            timezone.utc
        )

        db.commit()
        db.refresh(message)

        return message

    @staticmethod
    def get_recent_messages(
        db: Session,
        session: ChatSession,
        limit: int = 6,
    ) -> list[ChatMessage]:

        messages = (
            db.query(ChatMessage)
            .filter(
                ChatMessage.session_id == session.id
            )
            .order_by(
                ChatMessage.created_at.desc()
            )
            .limit(limit)
            .all()
        )

        return list(reversed(messages))