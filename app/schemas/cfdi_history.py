"""
Pydantic models for CFDI History
"""

from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, ConfigDict, Field


class CFDIHistoryBase(BaseModel):
    """Base CFDI History attributes"""

    uuid: str = Field(..., description="UUID del CFDI")
    emisor_rfc: str = Field(..., description="RFC del emisor")
    receptor_rfc: str = Field(..., description="RFC del receptor")
    total: str = Field(..., description="Monto total del CFDI")

    model_config = ConfigDict(populate_by_name=True)


class CFDIHistoryCreate(BaseModel):
    """CFDI History attributes for creating a record"""

    uuid: str = Field(..., description="UUID del CFDI")
    rfc_emisor: str = Field(..., description="RFC del emisor")
    rfc_receptor: str = Field(..., description="RFC del receptor")
    total: str = Field(..., description="Monto total del CFDI")
    token_id: Optional[str] = Field("legacy", description="ID del token que se usó para la consulta")
    user_id: Optional[str] = Field("0", description="ID del usuario que realizó la consulta")
    details: Optional[Dict[str, Any]] = Field(None, description="Detalles de la verificación")

    # Legacy fields
    estado: Optional[str] = Field(None, description="Estado del CFDI")
    es_cancelable: Optional[str] = Field(None, description="Si el CFDI es cancelable")
    estatus_cancelacion: Optional[str] = Field(
        None, description="Estatus de cancelación"
    )
    codigo_estatus: Optional[str] = Field(None, description="Código de estatus")
    validacion_efos: Optional[str] = Field(None, description="Validación EFOS")

    model_config = ConfigDict(populate_by_name=True)


class CFDIHistoryResponse(CFDIHistoryBase):
    """CFDI History data returned to client"""

    id: int = Field(..., description="ID del registro")
    estado: Optional[str] = Field(None, description="Estado del CFDI")
    es_cancelable: Optional[str] = Field(None, description="Si el CFDI es cancelable")
    estatus_cancelacion: Optional[str] = Field(
        None, description="Estatus de cancelación"
    )
    codigo_estatus: Optional[str] = Field(None, description="Código de estatus")
    validacion_efos: Optional[str] = Field(None, description="Validación EFOS")
    created_at: datetime = Field(..., description="Fecha de creación del registro")

    model_config = ConfigDict(from_attributes=True)


class CFDIHistoryList(BaseModel):
    """Response model for a list of CFDI History items"""

    items: List[CFDIHistoryResponse]
    total_count: int = Field(..., description="Total number of history items")

    model_config = ConfigDict(from_attributes=True)
