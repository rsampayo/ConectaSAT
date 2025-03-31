"""
Admin API router for managing tokens and superadmins
"""
from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.orm import Session
from typing import Any, List, Optional

from app.core.deps import get_current_admin
from app.core.security import get_password_hash, verify_password, create_api_token
from app.db.database import get_db
from app.models.user import SuperAdmin, APIToken
from app.schemas.auth import (
    TokenCreate, TokenUpdate, TokenResponse, TokenList,
    SuperAdminCreate, SuperAdminUpdate, SuperAdminResponse,
    MessageResponse
)

router = APIRouter(prefix="/admin")

# Token management routes
@router.post("/tokens", response_model=TokenResponse, 
            summary="Create Api Token",
            description="""
            Create a new API token
            
            Requires superadmin authentication using HTTP Basic auth.
            """)
async def create_api_token_endpoint(
    token_data: TokenCreate,
    db: Session = Depends(get_db),
    admin: SuperAdmin = Depends(get_current_admin)
) -> Any:
    """
    Create a new API token
    """
    # Create token
    db_token = create_api_token(db, token_data.description)
    
    return TokenResponse(
        id=db_token.id,
        token=db_token.token,
        description=db_token.description,
        is_active=db_token.is_active,
        created_at=db_token.created_at,
        updated_at=db_token.updated_at
    )

@router.get("/tokens", response_model=TokenList, 
           summary="List Api Tokens",
           description="""
           List all API tokens
           
           Requires superadmin authentication using HTTP Basic auth.
           """)
async def list_api_tokens_endpoint(
    skip: int = Query(0),
    limit: int = Query(100),
    db: Session = Depends(get_db),
    admin: SuperAdmin = Depends(get_current_admin)
) -> TokenList:
    """
    List all API tokens
    """
    # Get tokens
    tokens = db.query(APIToken).offset(skip).limit(limit).all()
    total = db.query(APIToken).count()
    
    # Convert to response models
    token_responses = [
        TokenResponse(
            id=token.id,
            token=token.token,
            description=token.description,
            is_active=token.is_active,
            created_at=token.created_at,
            updated_at=token.updated_at
        )
        for token in tokens
    ]
    
    return TokenList(tokens=token_responses, total=total)

@router.get("/tokens/{token_id}", response_model=TokenResponse, 
           summary="Get Api Token",
           description="""
           Get a specific API token by ID
           
           Requires superadmin authentication using HTTP Basic auth.
           """)
async def get_api_token_endpoint(
    token_id: int = Path(...),
    db: Session = Depends(get_db),
    admin: SuperAdmin = Depends(get_current_admin)
) -> TokenResponse:
    """
    Get a specific API token
    """
    # Get token
    token = db.query(APIToken).filter(APIToken.id == token_id).first()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
    
    return TokenResponse(
        id=token.id,
        token=token.token,
        description=token.description,
        is_active=token.is_active,
        created_at=token.created_at,
        updated_at=token.updated_at
    )

@router.put("/tokens/{token_id}", response_model=TokenResponse, 
           summary="Update Api Token",
           description="""
           Update an API token
           
           Requires superadmin authentication using HTTP Basic auth.
           """)
async def update_api_token_endpoint(
    token_data: TokenUpdate,
    token_id: int = Path(...),
    db: Session = Depends(get_db),
    admin: SuperAdmin = Depends(get_current_admin)
) -> TokenResponse:
    """
    Update an API token
    """
    # Get token
    token = db.query(APIToken).filter(APIToken.id == token_id).first()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
    
    # Update fields if provided
    if token_data.description is not None:
        token.description = token_data.description
    if token_data.is_active is not None:
        token.is_active = token_data.is_active
    
    db.commit()
    db.refresh(token)
    
    return TokenResponse(
        id=token.id,
        token=token.token,
        description=token.description,
        is_active=token.is_active,
        created_at=token.created_at,
        updated_at=token.updated_at
    )

@router.delete("/tokens/{token_id}", response_model=MessageResponse, 
              summary="Delete Api Token",
              description="""
              Delete an API token
              
              Requires superadmin authentication using HTTP Basic auth.
              """)
async def delete_api_token_endpoint(
    token_id: int = Path(...),
    db: Session = Depends(get_db),
    admin: SuperAdmin = Depends(get_current_admin)
) -> MessageResponse:
    """
    Delete an API token
    """
    # Get token
    token = db.query(APIToken).filter(APIToken.id == token_id).first()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
    
    # Delete token
    db.delete(token)
    db.commit()
    
    return MessageResponse(message=f"Token {token_id} successfully deleted")

@router.post("/tokens/{token_id}/regenerate", response_model=TokenResponse, 
            summary="Regenerate Api Token",
            description="""
            Regenerate an API token
            
            Creates a new token value for the existing token ID.
            Requires superadmin authentication using HTTP Basic auth.
            """)
async def regenerate_api_token_endpoint(
    token_id: int = Path(...),
    db: Session = Depends(get_db),
    admin: SuperAdmin = Depends(get_current_admin)
) -> TokenResponse:
    """
    Regenerate an API token
    """
    # Get token
    token = db.query(APIToken).filter(APIToken.id == token_id).first()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
    
    # Generate new token value
    import secrets
    token.token = secrets.token_urlsafe(32)
    
    db.commit()
    db.refresh(token)
    
    return TokenResponse(
        id=token.id,
        token=token.token,
        description=token.description,
        is_active=token.is_active,
        created_at=token.created_at,
        updated_at=token.updated_at
    )

# Superadmin management routes
@router.post("/superadmins", response_model=SuperAdminResponse, 
            summary="Create New Superadmin",
            description="""
            Create a new superadmin
            
            Requires existing superadmin authentication using HTTP Basic auth.
            """)
async def create_new_superadmin_endpoint(
    admin_data: SuperAdminCreate,
    db: Session = Depends(get_db),
    current_admin: SuperAdmin = Depends(get_current_admin)
) -> SuperAdminResponse:
    """
    Create a new superadmin
    """
    # Check if username already exists
    existing_admin = db.query(SuperAdmin).filter(SuperAdmin.username == admin_data.username).first()
    
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Create new superadmin
    hashed_password = get_password_hash(admin_data.password)
    
    db_admin = SuperAdmin(
        username=admin_data.username,
        hashed_password=hashed_password
    )
    
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    
    return SuperAdminResponse(
        username=db_admin.username,
        is_active=db_admin.is_active,
        created_at=db_admin.created_at
    )

@router.put("/superadmins/{username}/password", response_model=MessageResponse, 
           summary="Update Admin Password",
           description="""
           Update a superadmin's password
           
           Requires superadmin authentication using HTTP Basic auth.
           """)
async def update_admin_password_endpoint(
    password_data: SuperAdminUpdate,
    username: str = Path(...),
    db: Session = Depends(get_db),
    current_admin: SuperAdmin = Depends(get_current_admin)
) -> MessageResponse:
    """
    Update a superadmin's password
    """
    # Get admin
    admin = db.query(SuperAdmin).filter(SuperAdmin.username == username).first()
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Superadmin not found"
        )
    
    # Verify current password if not updating own account
    if admin.id != current_admin.id:
        # Only allow updating other accounts if you know their password
        if not verify_password(password_data.current_password, admin.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect current password"
            )
    else:
        # Always verify current password when updating own account
        if not verify_password(password_data.current_password, admin.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect current password"
            )
    
    # Update password
    admin.hashed_password = get_password_hash(password_data.new_password)
    
    db.commit()
    
    return MessageResponse(message="Password updated successfully")

@router.delete("/superadmins/{username}", response_model=MessageResponse, 
              summary="Deactivate Admin Account",
              description="""
              Deactivate a superadmin account
              
              Requires superadmin authentication using HTTP Basic auth.
              """)
async def deactivate_admin_account_endpoint(
    username: str = Path(...),
    db: Session = Depends(get_db),
    current_admin: SuperAdmin = Depends(get_current_admin)
) -> MessageResponse:
    """
    Deactivate a superadmin account
    """
    # Get admin
    admin = db.query(SuperAdmin).filter(SuperAdmin.username == username).first()
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Superadmin not found"
        )
    
    # Prevent self-deactivation
    if admin.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    # Check if this is the last active admin
    active_admins_count = db.query(SuperAdmin).filter(SuperAdmin.is_active == True).count()
    if active_admins_count <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate the last active admin account"
        )
    
    # Deactivate account instead of deletion
    admin.is_active = False
    
    db.commit()
    
    return MessageResponse(message=f"Superadmin '{username}' deactivated successfully") 