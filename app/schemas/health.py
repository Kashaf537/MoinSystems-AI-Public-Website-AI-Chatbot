from pydantic import BaseModel


class DatabaseHealth(BaseModel):
    status: str  # "ok" | "error"
    detail: str


class HealthResponse(BaseModel):
    status: str  # "ok" | "degraded"
    app_env: str
    database: DatabaseHealth
