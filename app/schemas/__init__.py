"""Pydantic models for the application."""

from typing import Optional

from pydantic import BaseModel

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
from app.schemas.cfdi import (
    BatchCFDIRequest,
    BatchCFDIResponse,
    CFDIBatch,
    CFDIBatchItem,
    CFDIRequest, 
    CFDIResponse,
    CFDIVerifyRequest,
    VerifyCFDI
)
from app.schemas.cfdi_history import (
    CFDIHistoryBase,
    CFDIHistoryCreate,
    CFDIHistoryList,
    CFDIHistoryResponse
)

# Define classes that might be missing
class Token(BaseModel):
    """Token authentication schema."""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Token data schema."""
    username: Optional[str] = None

# Define a new class for verification response
class CFDIVerificationResponse(CFDIResponse):
    """CFDI verification response for the verification endpoint."""
    pass
