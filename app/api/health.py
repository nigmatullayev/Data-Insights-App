"""
Health check endpoint to verify API configuration
"""
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()

@router.get("/health")
def health_check():
    """
    Check API health and configuration
    """
    is_valid, error_msg = settings.validate()
    
    return {
        "status": "healthy" if is_valid else "unhealthy",
        "api_key_configured": bool(settings.CEREBRAS_API_KEY),
        "api_key_length": len(settings.CEREBRAS_API_KEY) if settings.CEREBRAS_API_KEY else 0,
        "error": error_msg if not is_valid else None
    }

