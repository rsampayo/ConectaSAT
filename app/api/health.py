"""
Health check API router
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db

router = APIRouter()


@router.get(
    "/health",
    summary="Health Check",
    description="""
           Simple health check endpoint
           
           Permite verificar si el servicio está funcionando correctamente.
           Este endpoint no requiere autenticación.
           """,
)
async def health_check_endpoint():
    """
    Health check endpoint
    """
    return {"status": "healthy", "message": "Service is up and running"}
