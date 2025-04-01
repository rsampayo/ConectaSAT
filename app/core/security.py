"""Security utilities for authentication and authorization."""

import logging
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import APIToken, SuperAdmin

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def authenticate_admin(
    db: Session, username: str, password: str
) -> Optional[SuperAdmin]:
    """Authenticate a superadmin by username and password."""
    admin = db.query(SuperAdmin).filter(SuperAdmin.username == username).first()
    if (
        not admin
        or not verify_password(password, str(admin.hashed_password))
        or not admin.is_active
    ):
        return None
    return admin


async def verify_api_token(db: Session, token: str) -> Optional[int]:
    """Verify an API token and return the associated user_id if valid."""
    try:
        api_token = db.query(APIToken).filter(APIToken.token == token).first()

        if api_token is None:
            return None

        if api_token.is_active:
            return int(api_token.user_id) if api_token.user_id else None

        return None
    except Exception as e:
        logging.error(f"Error verifying API token: {e}")
        return None


def create_api_token(db: Session, description: Optional[str] = None) -> APIToken:
    """Create a new API token."""
    import secrets

    token_value = secrets.token_urlsafe(32)

    # Create new token
    db_token = APIToken(token=token_value, description=description)
    db.add(db_token)
    db.commit()
    db.refresh(db_token)

    return db_token
