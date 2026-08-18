from fastapi import APIRouter

from app.core.config import get_settings
from app.db.session import check_connection
from app.schemas.health import HealthResponse

router = APIRouter(
    prefix="/api/v1",
    tags=["Health"],
)


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    settings = get_settings()

    db_healthy, db_detail = check_connection()

    return HealthResponse(
        status="ok" if db_healthy else "degraded",
        app_env=settings.APP_ENV,
        database={
            "status": "ok" if db_healthy else "error",
            "detail": db_detail,
        },
    )
