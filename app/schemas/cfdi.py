"""
Pydantic models for CFDI verification
"""

from typing import List, Optional, Dict, Any

from pydantic import BaseModel, ConfigDict, Field


class CFDIRequest(BaseModel):
    """
    CFDI verification request
    """

    uuid: str = Field(..., description="UUID del CFDI")
    emisor_rfc: str = Field(..., description="RFC del emisor")
    receptor_rfc: str = Field(..., description="RFC del receptor")
    total: str = Field(..., description="Monto total del CFDI")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "uuid": "6128396f-c09b-4ec6-8699-43c5f7e3b230",
                "emisor_rfc": "CDZ050722LA9",
                "receptor_rfc": "XIN06112344A",
                "total": "12000.00",
            }
        }
    )


class CFDIVerifyRequest(BaseModel):
    """
    New CFDI verification request format
    """
    uuid: str = Field(..., description="UUID del CFDI")
    rfc_emisor: str = Field(..., description="RFC del emisor")
    rfc_receptor: str = Field(..., description="RFC del receptor")
    total: float = Field(..., description="Monto total del CFDI")


class CFDIResponse(BaseModel):
    """
    CFDI verification response
    """

    estado: Optional[str] = Field(None, description="Estado del CFDI")
    es_cancelable: Optional[str] = Field(None, description="Si el CFDI es cancelable")
    estatus_cancelacion: Optional[str] = Field(
        None, description="Estatus de cancelación"
    )
    codigo_estatus: Optional[str] = Field(None, description="Código de estatus")
    validacion_efos: Optional[str] = Field(None, description="Validación EFOS")
    efos_emisor: Optional[str] = Field(None, description="Estatus EFOS del emisor")
    efos_receptor: Optional[str] = Field(None, description="Estatus EFOS del receptor")
    raw_response: Optional[str] = Field(None, description="Respuesta XML completa")
    # New fields for updated API
    status: Optional[str] = Field(None, description="Estado de la petición")
    message: Optional[str] = Field(None, description="Mensaje descriptivo")
    data: Optional[Dict[str, Any]] = Field(None, description="Datos de la verificación")


class VerifyCFDI(BaseModel):
    """
    CFDI verification result for batch processing
    """
    uuid: str = Field(..., description="UUID del CFDI verificado")
    status: str = Field(..., description="Estado de la verificación (success/error)")
    message: str = Field(..., description="Mensaje descriptivo")
    data: Optional[Dict[str, Any]] = Field(None, description="Datos de la verificación")


class CFDIBatch(BaseModel):
    """
    Batch response for CFDI verifications
    """
    results: List[VerifyCFDI] = Field(..., description="Resultados de las verificaciones")


class BatchCFDIRequest(BaseModel):
    """
    Batch CFDI verification request
    """

    cfdis: List[CFDIRequest] = Field(
        ..., description="Lista de CFDIs a verificar", min_length=1
    )


class CFDIBatchItem(BaseModel):
    """
    Single item in a batch CFDI response
    """

    request: CFDIRequest
    response: CFDIResponse
    error: Optional[str] = Field(None, description="Error message if validation failed")

    model_config = ConfigDict(populate_by_name=True)


class BatchCFDIResponse(BaseModel):
    """
    Batch CFDI verification response
    """

    results: List[CFDIBatchItem]

    model_config = ConfigDict(populate_by_name=True)
