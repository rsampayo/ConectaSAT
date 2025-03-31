"""
Pydantic models for authentication
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# Token schemas
class TokenCreate(BaseModel):
    """Create token request"""
    description: Optional[str] = Field(None, description="Description of the token's purpose")

class TokenUpdate(BaseModel):
    """Update token request"""
    description: Optional[str] = Field(None, description="Description of the token's purpose")
    is_active: Optional[bool] = Field(None, description="Whether the token is active")

class TokenResponse(BaseModel):
    """Token response"""
    id: int
    token: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    description: Optional[str] = Field(None, description="Description of the token's purpose")

class TokenList(BaseModel):
    """List of tokens"""
    tokens: List[TokenResponse]
    total: int

# Superadmin schemas
class SuperAdminCreate(BaseModel):
    """Create superadmin request"""
    username: str = Field(..., description="Username for the superadmin")
    password: str = Field(..., description="Password for the superadmin")

class SuperAdminUpdate(BaseModel):
    """Update superadmin password"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., description="New password")

class SuperAdminResponse(BaseModel):
    """Superadmin response"""
    username: str
    is_active: bool
    created_at: datetime

# Message response
class MessageResponse(BaseModel):
    """Simple message response"""
    message: str 