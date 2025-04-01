"""Dependency injection functions."""

from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPBasic,
    HTTPBasicCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
)
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import verify_api_token, verify_password
from app.db.database import SessionLocal
from app.models.user import APIToken, SuperAdmin, User

# Security schemes
security_bearer = HTTPBearer()
security_basic = HTTPBasic()

# Create module-level dependency variables for security schemes
security_bearer_dependency = Depends(security_bearer)
security_basic_dependency = Depends(security_basic)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator:
    """Get database session."""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


# Create module-level dependency variables
db_dependency = Depends(get_db)

# For backward compatibility
get_db_dependency = db_dependency


async def get_current_token(
    token=security_bearer_dependency,
    db: Session = db_dependency,
) -> str:
    """Get and validate the current API token."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_str = token.credentials
    result = await verify_api_token(db, token_str)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_str


# Create module-level dependency variable for get_current_token
get_current_token_dependency = Depends(get_current_token)


async def get_user_id_from_token(
    token: str = get_current_token_dependency,
    db: Session = db_dependency,
) -> int:
    """Get the user ID associated with the current token."""
    # Get the API token from the database
    api_token = db.query(APIToken).filter(APIToken.token == token).first()

    if not api_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API token",
        )

    # If the token has a user_id, return it
    if api_token.user_id:
        return int(api_token.user_id)

    # If not, look for an existing default user or create one
    default_user = db.query(User).filter(User.email == "default@user.com").first()

    if not default_user:
        # Create a new default user
        default_user = User(
            name="Default User",
            email="default@user.com",
            is_active=True,
        )
        db.add(default_user)
        db.commit()
        db.refresh(default_user)

    # Associate the token with the default user - only update the token
    api_token.user_id = default_user.id
    db.commit()

    return int(default_user.id)


# Create module-level dependency variable for get_user_id_from_token
get_user_id_from_token_dependency = Depends(get_user_id_from_token)


def get_current_admin(
    credentials: HTTPBasicCredentials = security_basic_dependency,
    db: Session = db_dependency,
) -> SuperAdmin:
    """Get the current superadmin from HTTP Basic auth credentials."""
    admin = (
        db.query(SuperAdmin).filter(SuperAdmin.username == credentials.username).first()
    )

    if not admin or not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    if not verify_password(credentials.password, str(admin.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    return admin


# Create module-level dependency variable for get_current_admin
current_admin_dependency = Depends(get_current_admin)
