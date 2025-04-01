"""Pydantic models for authentication."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# Token schemas
class TokenCreate(BaseModel):
    """Create token request."""

    description: Optional[str] = Field(
        None, description="Description of the token's purpose"
    )

    model_config = ConfigDict(populate_by_name=True)


class TokenUpdate(BaseModel):
    """Update token request."""

    description: Optional[str] = Field(
        None, description="Description of the token's purpose"
    )
    is_active: Optional[bool] = Field(None, description="Whether the token is active")

    model_config = ConfigDict(populate_by_name=True)


class TokenResponse(BaseModel):
    """Token response."""

    id: int
    token: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    description: Optional[str] = Field(
        None, description="Description of the token's purpose"
    )

    model_config = ConfigDict(populate_by_name=True)


class TokenList(BaseModel):
    """List of tokens."""

    tokens: List[TokenResponse]
    total: int

    model_config = ConfigDict(populate_by_name=True)


# Superadmin schemas
class SuperAdminCreate(BaseModel):
    """Create superadmin request."""

    username: str = Field(..., description="Username for the superadmin")
    password: str = Field(..., description="Password for the superadmin")
    full_name: Optional[str] = Field(None, description="Full name of the superadmin")

    model_config = ConfigDict(populate_by_name=True)


class SuperAdminUpdate(BaseModel):
    """Update superadmin password."""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., description="New password")

    model_config = ConfigDict(populate_by_name=True)


class SuperAdminResponse(BaseModel):
    """Superadmin response."""

    username: str
    is_active: bool
    created_at: datetime
    full_name: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


# Message response
class MessageResponse(BaseModel):
    """Simple message response."""

    message: str

    model_config = ConfigDict(populate_by_name=True)
