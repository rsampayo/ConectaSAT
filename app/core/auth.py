"""Authentication utilities."""

from datetime import timedelta
from typing import Any, Dict, Optional

from jose import jwt

from app.core.config import settings
from app.core.security import create_token


def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    """Create an access token for a user.

    Args:     user_id: User ID to include in the token     expires_delta: Optional
    expiration delta

    Returns:     JWT token as string
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    token_data = {"sub": str(user_id), "type": "access"}
    return create_token(token_data, expires_delta)


def get_token_data(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT token.

    Args:     token: JWT token to decode

    Returns:     Token payload data
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def get_user_id_from_token_data(token_data: Dict[str, Any]) -> int:
    """Extract user ID from token data.

    Args:     token_data: Decoded token data

    Returns:     User ID from token
    """
    return int(token_data.get("sub"))
