"""Database initialization script."""

import logging

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import SuperAdmin

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def init_db(db: Session) -> None:
    """Initialize database with admin user if it doesn't exist."""
    # Check if admin user already exists
    admin = (
        db.query(SuperAdmin)
        .filter(SuperAdmin.username == settings.ADMIN_USERNAME)
        .first()
    )

    if not admin and settings.ADMIN_USERNAME and settings.ADMIN_PASSWORD:
        logger.info("Creating first admin user")

        # Create admin user
        admin = SuperAdmin(
            username=settings.ADMIN_USERNAME,
            hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
        )

        db.add(admin)
        db.commit()

        logger.info(f"Admin user '{settings.ADMIN_USERNAME}' created")
    else:
        logger.info("Admin user already exists or not configured")
