"""
CFDI verification API router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, List

from app.core.deps import get_current_token
from app.db.database import get_db
from app.schemas.cfdi import CFDIRequest, CFDIResponse, BatchCFDIRequest, BatchCFDIResponse, CFDIBatchItem
from app.services.sat_verification import verify_cfdi

router = APIRouter()

@router.post("/verify-cfdi", response_model=CFDIResponse, 
            summary="Verify Cfdi",
            description="""
            Verifica la validez de un CFDI con el SAT
            
            Esta API consulta el servicio oficial del SAT para verificar el estatus de un CFDI.
            Requiere autenticación mediante Bearer token.
            
            Returns:
                CFDIResponse: Información sobre la validez del CFDI
            """)
async def verify_cfdi_endpoint(
    cfdi: CFDIRequest,
    token: str = Depends(get_current_token)
) -> CFDIResponse:
    """
    Verify a CFDI with the SAT service
    """
    try:
        result = await verify_cfdi(
            uuid=cfdi.uuid,
            emisor_rfc=cfdi.emisor_rfc,
            receptor_rfc=cfdi.receptor_rfc,
            total=cfdi.total
        )
        return CFDIResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verifying CFDI: {str(e)}"
        )

@router.post("/verify-cfdi-batch", response_model=BatchCFDIResponse, 
            summary="Verify Cfdi Batch",
            description="""
            Verifica la validez de múltiples CFDIs con el SAT en una sola petición
            
            Esta API consulta el servicio oficial del SAT para verificar el estatus de múltiples CFDIs.
            Cada CFDI se procesa de forma independiente y los resultados se devuelven en un único response.
            Requiere autenticación mediante Bearer token.
            
            Returns:
                BatchCFDIResponse: Información sobre la validez de todos los CFDIs solicitados
            """)
async def verify_cfdi_batch_endpoint(
    batch_request: BatchCFDIRequest,
    token: str = Depends(get_current_token)
) -> BatchCFDIResponse:
    """
    Verify multiple CFDIs with the SAT service
    """
    results = []
    
    for cfdi_request in batch_request.cfdis:
        item = {"request": cfdi_request, "response": CFDIResponse(), "error": None}
        
        try:
            cfdi_result = await verify_cfdi(
                uuid=cfdi_request.uuid,
                emisor_rfc=cfdi_request.emisor_rfc,
                receptor_rfc=cfdi_request.receptor_rfc,
                total=cfdi_request.total
            )
            item["response"] = CFDIResponse(**cfdi_result)
        except Exception as e:
            item["error"] = str(e)
        
        results.append(CFDIBatchItem(**item))
    
    return BatchCFDIResponse(results=results) 