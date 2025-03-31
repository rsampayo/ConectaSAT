"""
Dependency injection functions
"""


from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import verify_api_token, verify_password
from app.db.database import get_db
from app.models.user import APIToken, SuperAdmin, User

# Security schemes
security_bearer = HTTPBearer()
security_basic = HTTPBasic()

# Create fixed variable for get_db dependency
db_dependency = Depends(get_db)


async def get_current_token(
    token: str = Depends(security_bearer), db: Session = db_dependency
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
    token: str = Depends(get_current_token), db: Session = db_dependency
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
        return int(api_token.user_id)

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

    return int(default_user.id)


def get_current_admin(
    credentials: HTTPBasicCredentials = Depends(security_basic),
    db: Session = db_dependency,
) -> SuperAdmin:
    """
    Get the current superadmin from HTTP Basic auth credentials
    """
    # Check if credentials are provided
    if not credentials.username or not credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    # Check if superadmin exists and password is correct
    admin = (
        db.query(SuperAdmin).filter(SuperAdmin.username == credentials.username).first()
    )
    if not admin or not verify_password(credentials.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    # Check if superadmin is active
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is inactive",
            headers={"WWW-Authenticate": "Basic"},
        )

    return admin


# Create fixed variable for get_current_admin dependency
current_admin_dependency = Depends(get_current_admin)
