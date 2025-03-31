"""Admin API endpoints for managing superadmins and API tokens."""

import secrets

from fastapi import APIRouter, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from app.core.deps import current_admin_dependency, db_dependency
from app.core.security import create_api_token, get_password_hash, verify_password
from app.models.user import APIToken, SuperAdmin
from app.schemas.auth import (
    MessageResponse,
    SuperAdminCreate,
    SuperAdminResponse,
    SuperAdminUpdate,
    TokenCreate,
    TokenList,
    TokenResponse,
    TokenUpdate,
)

router = APIRouter(tags=["admin"])

# Create reusable Path and Query parameters to avoid B008
path_token_id = Path(..., description="The ID of the token to operate on")
path_username = Path(..., description="The username of the superadmin")
query_skip = Query(0, description="Number of items to skip")
query_limit = Query(100, description="Maximum number of items to return")


# Token management routes
@router.post(
    "/tokens",
    response_model=TokenResponse,
    summary="Create Api Token",
    description=(
        "Create a new API token. "
        "Requires superadmin authentication using HTTP Basic auth."
    ),
)
async def create_api_token_endpoint(
    token_data: TokenCreate,
    db: Session = db_dependency,
    admin: SuperAdmin = current_admin_dependency,
) -> TokenResponse:
    """Create a new API token."""
    # Create token
    db_token = create_api_token(db, token_data.description)

    return TokenResponse(
        id=int(db_token.id),
        token=str(db_token.token),
        description=(str(db_token.description) if db_token.description else None),
        is_active=bool(db_token.is_active),
        created_at=db_token.created_at,
        updated_at=db_token.updated_at,
    )


@router.get(
    "/tokens",
    response_model=TokenList,
    summary="List Api Tokens",
    description=(
        "List all API tokens. "
        "Requires superadmin authentication using HTTP Basic auth."
    ),
)
async def list_api_tokens_endpoint(
    skip: int = query_skip,
    limit: int = query_limit,
    db: Session = db_dependency,
    admin: SuperAdmin = current_admin_dependency,
) -> TokenList:
    """List all API tokens."""
    # Get active tokens only
    active_tokens = (
        db.query(APIToken)
        .filter(APIToken.is_active.is_(True))
        .offset(skip)
        .limit(limit)
        .all()
    )
    total = db.query(APIToken).count()

    # Convert to response models
    token_responses = [
        TokenResponse(
            id=int(token.id),
            token=str(token.token),
            description=(str(token.description) if token.description else None),
            is_active=bool(token.is_active),
            created_at=token.created_at,
            updated_at=token.updated_at,
        )
        for token in active_tokens
    ]

    # Return TokenList with tokens and total count
    return TokenList(tokens=token_responses, total=total)


@router.get(
    "/tokens/{token_id}",
    response_model=TokenResponse,
    summary="Get Api Token",
    description=(
        "Get a specific API token by ID. "
        "Requires superadmin authentication using HTTP Basic auth."
    ),
)
async def get_api_token_endpoint(
    token_id: int = path_token_id,
    db: Session = db_dependency,
    admin: SuperAdmin = current_admin_dependency,
) -> TokenResponse:
    """Get a specific API token by ID."""
    # Get token
    token = db.query(APIToken).filter(APIToken.id == token_id).first()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Token not found"
        )

    return TokenResponse(
        id=int(token.id),
        token=str(token.token),
        description=(str(token.description) if token.description else None),
        is_active=bool(token.is_active),
        created_at=token.created_at,
        updated_at=token.updated_at,
    )


@router.put(
    "/tokens/{token_id}",
    response_model=TokenResponse,
    summary="Update Api Token",
    description=(
        "Update an API token. "
        "Requires superadmin authentication using HTTP Basic auth."
    ),
)
async def update_api_token_endpoint(
    token_data: TokenUpdate,
    token_id: int = path_token_id,
    db: Session = db_dependency,
    admin: SuperAdmin = current_admin_dependency,
) -> TokenResponse:
    """Update an existing API token by ID."""
    # Get token
    token = db.query(APIToken).filter(APIToken.id == token_id).first()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Token not found"
        )

    # Update fields if provided
    if token_data.description is not None:
        token.description = str(token_data.description)
    if token_data.is_active is not None:
        token.is_active = bool(token_data.is_active)

    db.commit()
    db.refresh(token)

    return TokenResponse(
        id=int(token.id),
        token=str(token.token),
        description=(str(token.description) if token.description else None),
        is_active=bool(token.is_active),
        created_at=token.created_at,
        updated_at=token.updated_at,
    )


@router.delete(
    "/tokens/{token_id}",
    response_model=MessageResponse,
    summary="Delete Api Token",
    description=(
        "Delete an API token. "
        "Requires superadmin authentication using HTTP Basic auth."
    ),
)
async def delete_api_token_endpoint(
    token_id: int = path_token_id,
    db: Session = db_dependency,
    admin: SuperAdmin = current_admin_dependency,
) -> MessageResponse:
    """Delete an API token by ID."""
    # Get token
    token = db.query(APIToken).filter(APIToken.id == token_id).first()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Token not found"
        )

    # Delete token
    db.delete(token)
    db.commit()

    return MessageResponse(message=f"Token {token_id} successfully deleted")


@router.post(
    "/tokens/{token_id}/regenerate",
    response_model=TokenResponse,
    summary="Regenerate Api Token",
    description=(
        "Regenerate an API token with a new value. "
        "Requires superadmin authentication using HTTP Basic auth."
    ),
)
async def regenerate_api_token_endpoint(
    token_id: int = path_token_id,
    db: Session = db_dependency,
    admin: SuperAdmin = current_admin_dependency,
) -> TokenResponse:
    """Regenerate an API token with a new value."""
    # Get token
    token = db.query(APIToken).filter(APIToken.id == token_id).first()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Token not found"
        )

    # Generate a new token value
    token.token = secrets.token_urlsafe(32)
    db.commit()
    db.refresh(token)

    # Return token data
    return TokenResponse(
        id=int(token.id),
        token=str(token.token),
        description=(str(token.description) if token.description else None),
        is_active=bool(token.is_active),
        created_at=token.created_at,
        updated_at=token.updated_at,
    )


# Superadmin management routes
@router.post(
    "/superadmin",
    response_model=SuperAdminResponse,
    summary="Create Superadmin",
    description=(
        "Create a new superadmin. "
        "Requires superadmin authentication using HTTP Basic auth."
    ),
)
async def create_new_superadmin_endpoint(
    admin_data: SuperAdminCreate,
    db: Session = db_dependency,
    current_admin: SuperAdmin = current_admin_dependency,
) -> SuperAdminResponse:
    """Create a new superadmin account."""
    # Check if superadmin exists with this username
    existing_admin = (
        db.query(SuperAdmin).filter(SuperAdmin.username == admin_data.username).first()
    )
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Superadmin with this username already exists",
        )

    # Create new superadmin
    hashed_password = get_password_hash(admin_data.password)
    db_admin = SuperAdmin(
        username=admin_data.username,
        hashed_password=hashed_password,
        full_name=admin_data.full_name,
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)

    return SuperAdminResponse(
        id=db_admin.id,
        username=db_admin.username,
        full_name=db_admin.full_name,
        is_active=db_admin.is_active,
        created_at=db_admin.created_at,
    )


@router.put(
    "/superadmin/{username}/password",
    response_model=MessageResponse,
    summary="Update Superadmin Password",
    description=(
        "Update a superadmin password. "
        "Requires superadmin authentication using HTTP Basic auth."
    ),
)
async def update_admin_password_endpoint(
    password_data: SuperAdminUpdate,
    username: str = path_username,
    db: Session = db_dependency,
    current_admin: SuperAdmin = current_admin_dependency,
) -> MessageResponse:
    """Update a superadmin password."""
    # Get admin
    admin = db.query(SuperAdmin).filter(SuperAdmin.username == username).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Superadmin not found"
        )

    # Verify old password if updating own password
    if admin.id == current_admin.id:
        if not verify_password(password_data.old_password, admin.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect old password"
            )

    # Update password
    admin.hashed_password = get_password_hash(password_data.new_password)
    db.commit()

    message = f"Password for superadmin '{username}' updated successfully"
    return MessageResponse(message=message)


@router.delete(
    "/superadmin/{username}",
    response_model=MessageResponse,
    summary="Deactivate Superadmin",
    description=(
        "Deactivate a superadmin account. "
        "Requires superadmin authentication using HTTP Basic auth."
    ),
)
async def deactivate_admin_account_endpoint(
    username: str = path_username,
    db: Session = db_dependency,
    current_admin: SuperAdmin = current_admin_dependency,
) -> MessageResponse:
    """Deactivate a superadmin account."""
    # Find admin
    admin = db.query(SuperAdmin).filter(SuperAdmin.username == username).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Superadmin not found"
        )

    # Prevent self-deactivation
    if admin.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account",
        )

    # Check if this is the last active admin
    active_admins = db.query(SuperAdmin).filter(SuperAdmin.is_active.is_(True)).count()
    if active_admins <= 1:
        detail = "Cannot deactivate the last active admin account"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )

    # Deactivate account instead of deletion
    admin.is_active = False

    db.commit()

    message = f"Superadmin '{username}' deactivated successfully"
    return MessageResponse(message=message)
