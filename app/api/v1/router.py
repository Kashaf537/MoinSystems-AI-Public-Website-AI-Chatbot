from fastapi import APIRouter

from app.api.routes.chat import router as chat_router
from app.api.routes.sessions import router as sessions_router
from app.api.routes.lead_capture import router as lead_capture_router
from app.api.v1.health import router as health_router


router = APIRouter(
    prefix="/api/v1"
)


router.include_router(
    health_router
)

router.include_router(
    chat_router
)

router.include_router(
    sessions_router
)

router.include_router(
    lead_capture_router
)