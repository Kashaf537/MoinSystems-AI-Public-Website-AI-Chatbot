"""
PostgreSQL connection and session management.

- Engine is created once per process with pooling configured.
- get_db() provides a request-scoped SQLAlchemy session for FastAPI.
- session_scope() provides a transaction-scoped session for scripts/jobs.
- check_connection() verifies database connectivity for the health endpoint.
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


settings = get_settings()


engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    future=True,
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
)


def get_db() -> Generator[Session, None, None]:
    """Provide a database session for a FastAPI request."""

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """
    Provide a database session outside FastAPI request handling,
    such as scripts or ingestion jobs.
    """

    db = SessionLocal()

    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def check_connection() -> tuple[bool, str]:
    """
    Check PostgreSQL connectivity.

    Returns:
        (True, "connected") when the database is available.
        (False, error_detail) when the database is unavailable.

    This function never raises an exception so that the health
    endpoint can safely report database failures.
    """

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        return True, "connected"

    except Exception as exc:  # noqa: BLE001
        return False, str(exc)
