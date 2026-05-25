"""
Health check endpoints
"""

from fastapi import APIRouter, Response
from app.core.logger import log

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    log.info("health_check_called")
    return {"status": "ok", "service": "clipflow-ai"}

@router.get("/ready")
async def ready_check():
    """Readiness check endpoint"""
    return {"ready": True}
