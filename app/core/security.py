"""
Security utilities for authentication and authorization
"""
from datetime import datetime, timedelta
from typing import Union, Optional, Any

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import SuperAdmin, APIToken

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hash a password
    """
    return pwd_context.hash(password)

def authenticate_admin(db: Session, username: str, password: str) -> Optional[SuperAdmin]:
    """
    Authenticate a superadmin by username and password
    """
    admin = db.query(SuperAdmin).filter(SuperAdmin.username == username).first()
    if not admin or not verify_password(password, admin.hashed_password) or not admin.is_active:
        return None
    return admin

def verify_api_token(db: Session, token: str) -> bool:
    """
    Verify an API token
    """
    api_token = db.query(APIToken).filter(APIToken.token == token, APIToken.is_active == True).first()
    return api_token is not None

def create_api_token(db: Session, description: Optional[str] = None) -> APIToken:
    """
    Create a new API token
    """
    import secrets
    token_value = secrets.token_urlsafe(32)
    
    # Create new token
    db_token = APIToken(
        token=token_value,
        description=description
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    
    return db_token 