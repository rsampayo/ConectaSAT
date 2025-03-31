"""
Main FastAPI application
"""
import logging
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.api import cfdi, health, admin
from app.core.config import settings
from app.db.database import get_db, engine
from app.db.init_db import init_db
from app.models import user

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create database tables
user.Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para verificar la validez de Comprobantes Fiscales Digitales por Internet (CFDI)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    db = next(get_db())
    init_db(db)
    logger.info("Application startup complete")

# Include routers
app.include_router(cfdi.router, tags=["CFDI"])
app.include_router(health.router, tags=["Health"])
app.include_router(admin.router, tags=["Admin"])

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs"
    }
