"""
Dependency injection functions
"""

import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import authenticate_admin, verify_api_token
from app.db.database import get_db
from app.models.user import APIToken, SuperAdmin, User

# Security schemes
security_bearer = HTTPBearer()
security_basic = HTTPBasic()


async def get_current_token(
    token: str = Depends(security_bearer), db: Session = Depends(get_db)
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


async def get_user_id_from_token(
    token: str = Depends(get_current_token), db: Session = Depends(get_db)
) -> int:
    """
    Get the user ID associated with the current token

    For now, since we don't have user-specific tokens, return a default user ID.
    In a real implementation, this would look up the token in the database and
    return the associated user ID.
    """
    # Find the API token in the database
    api_token = db.query(APIToken).filter(APIToken.token == token).first()

    if api_token and api_token.user_id:
        # Return the associated user ID
        return api_token.user_id

    # If there's no user association, create or get the default user
    default_user = db.query(User).filter(User.email == "default@conectasat.com").first()

    if not default_user:
        # Create a default user if one doesn't exist
        default_user = User(
            name="Default User", email="default@conectasat.com", is_active=True
        )
        db.add(default_user)
        db.commit()
        db.refresh(default_user)

        # Associate the token with this user
        if api_token:
            api_token.user_id = default_user.id
            db.commit()

    return default_user.id


async def get_current_admin(
    credentials: HTTPBasicCredentials = Depends(security_basic),
    db: Session = Depends(get_db),
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
