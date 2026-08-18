# # MoinSystems AI Public Website AI Chatbot

Day 1 backend foundation for the MOI Systems AI chatbot.

This project establishes the FastAPI backend, environment configuration,
PostgreSQL database, pgvector support, SQLAlchemy models, Alembic migrations,
health monitoring, testing, and code-quality tooling that will be extended
through the remaining project milestones.

---

## Day 1 Scope

The Day 1 implementation includes:

- FastAPI application skeleton
- Versioned API structure (`/api/v1`)
- Typed environment configuration using Pydantic Settings
- Python 3.12 virtual environment
- PostgreSQL database using Docker
- pgvector PostgreSQL extension
- SQLAlchemy ORM
- Connection pooling and database health checks
- Alembic database migrations
- Initial operational database schema
- RAG knowledge document and chunk tables
- LLM provider abstraction
- Health endpoint
- Pytest test setup
- Ruff linting and formatting
- Environment and secret management

---

## Tech Stack

- Python 3.12
- FastAPI
- Uvicorn
- Pydantic
- Pydantic Settings
- SQLAlchemy
- PostgreSQL 16
- pgvector
- Alembic
- OpenAI SDK
- Anthropic SDK
- Pytest
- Ruff
- Docker / Docker Compose

---

## Project Structure

```text
moinsystems-chatbot-day1/
│
├── alembic/
│   ├── versions/
│   │   └── 0001_initial_schema.py
│   ├── env.py
│   └── script.py.mako
│
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── health.py
│   │   │   └── router.py
│   │   └── __init__.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── session.py
│   │
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── anthropic_provider.py
│   │   ├── base.py
│   │   ├── factory.py
│   │   ├── openai_provider.py
│   │   └── basellm.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── chat_message.py
│   │   ├── chat_session.py
│   │   ├── email_notification.py
│   │   ├── knowledge_chunk.py
│   │   ├── knowledge_document.py
│   │   └── lead_submission.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── health.py
│   │
│   ├── __init__.py
│   └── main.py
│
├── tests/
│   ├── __init__.py
│   └── test_health.py
│
├── .env.example
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── README.md
└── requirements.txt