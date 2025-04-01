"""Database configuration for the application."""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings


# Fix for Heroku PostgreSQL URL
def get_db_url():
    if settings.DATABASE_URL.startswith("postgres://"):
        # Replace postgres:// with postgresql:// for SQLAlchemy
        return settings.DATABASE_URL.replace("postgres://", "postgresql://", 1)
    return settings.DATABASE_URL


# Create engine
db_url = get_db_url()
if "sqlite" in db_url:
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
else:
    engine = create_engine(db_url)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()


# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
