"""
Dependency injection functions
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
import secrets

from app.db.database import get_db
from app.models.user import SuperAdmin
from app.core.security import authenticate_admin, verify_api_token

# Security schemes
security_bearer = HTTPBearer()
security_basic = HTTPBasic()

async def get_current_token(
    token: str = Depends(security_bearer),
    db: Session = Depends(get_db)
) -> str:
    """
    Get and validate the current API token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token or not token.credentials:
        raise credentials_exception
    
    # Verify token
    if not verify_api_token(db, token.credentials):
        raise credentials_exception
    
    return token.credentials

async def get_current_admin(
    credentials: HTTPBasicCredentials = Depends(security_basic),
    db: Session = Depends(get_db)
) -> SuperAdmin:
    """
    Get and validate the current admin user
    """
    auth_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Basic"},
    )
    
    # Authenticate admin
    admin = authenticate_admin(db, credentials.username, credentials.password)
    if not admin:
        raise auth_exception
    
    return admin 