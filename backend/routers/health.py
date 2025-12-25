"""
Health check endpoint.
"""
from fastapi import APIRouter

from config import settings
from database import is_db_initialized
from schemas.dto import HealthResponse

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    Returns status of database and OpenAI configuration.
    """
    # Check database connection
    db_status = "connected" if is_db_initialized() else "not_initialized"
    
    # Check OpenAI configuration (just whether key is present, don't call API)
    openai_status = "configured" if settings.openai_configured else "missing_key"
    
    return HealthResponse(
        status="ok",
        database=db_status,
        openai=openai_status
    )

