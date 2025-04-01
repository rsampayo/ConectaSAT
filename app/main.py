"""Main FastAPI application."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import admin, cfdi, health
from app.core.config import settings
from app.db.database import engine, get_db
from app.db.init_db import init_db
from app.models import cfdi_history, user

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create database tables
user.Base.metadata.create_all(bind=engine)
cfdi_history.Base.metadata.create_all(bind=engine)


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB with admin user
    db = next(get_db())
    init_db(db)
    logger.info("Application startup complete")
    yield
    # Shutdown: Cleanup if needed
    logger.info("Application shutting down")


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para verificar la validez de Comprobantes Fiscales Digitales por Internet (CFDI)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Include routers
app.include_router(cfdi.router)  # New API v1 router (/api/v1/cfdi/*)
app.include_router(cfdi.legacy_router)  # Legacy router for backward compatibility
app.include_router(health.router, tags=["Health"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs",
    }
