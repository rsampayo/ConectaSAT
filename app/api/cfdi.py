"""
CFDI verification API router
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_token, get_db, get_user_id_from_token
from app.db.database import get_db
from app.schemas.cfdi import (
    BatchCFDIRequest,
    BatchCFDIResponse,
    CFDIBatchItem,
    CFDIRequest,
    CFDIResponse,
)
from app.schemas.cfdi_history import CFDIHistoryResponse
from app.services.cfdi_history import (
    create_cfdi_history_from_verification,
    get_cfdi_history_by_uuid,
    get_user_cfdi_history,
)
from app.services.sat_verification import verify_cfdi

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/verify-cfdi",
    response_model=CFDIResponse,
    summary="Verify Single CFDI",
    description=(
        "Verify a single CFDI with the SAT service. "
        "Requires API token authentication."
    ),
)
async def verify_cfdi_endpoint(
    cfdi: CFDIRequest,
    token: str = Depends(get_current_token),
    user_id: int = Depends(get_user_id_from_token),
    db: Session = Depends(get_db),
) -> CFDIResponse:
    """
    Verify a single CFDI with the SAT (Mexican tax authority).

    Args:
        cfdi: CFDI request data containing UUID, RFCs, and total
        token: API token
        user_id: User ID
        db: Database session

    Returns:
        Verification result from SAT
    """
    try:
        # Call the SAT verification service
        verification_result = await verify_cfdi(
            uuid=cfdi.uuid,
            emisor_rfc=cfdi.emisor_rfc,
            receptor_rfc=cfdi.receptor_rfc,
            total=cfdi.total,
        )

        # Record the verification in history
        create_cfdi_history_from_verification(
            db=db,
            user_id=user_id,
            cfdi_request=cfdi.dict(),
            verification_result=verification_result,
        )

        # Return the verification result
        return CFDIResponse(
            estado=verification_result["estado"],
            es_cancelable=verification_result["es_cancelable"],
            estatus_cancelacion=verification_result["estatus_cancelacion"],
            codigo_estatus=verification_result["codigo_estatus"],
            raw_response=verification_result.get("raw_response"),
        )
    except Exception as e:
        # Log the error
        logger.error(f"Error verifying CFDI: {str(e)}")
        # Re-raise the exception
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verifying CFDI: {str(e)}",
        )


@router.post(
    "/verify-cfdi-batch",
    response_model=BatchCFDIResponse,
    summary="Verify Cfdi Batch",
    description="""
            Verifica la validez de múltiples CFDIs con el SAT en una sola petición

            Esta API consulta el servicio oficial del SAT para verificar el estatus de múltiples CFDIs.
            Cada CFDI se procesa de forma independiente y los resultados se devuelven en un único response.
            Requiere autenticación mediante Bearer token.

            Returns:
                BatchCFDIResponse: Información sobre la validez de todos los CFDIs solicitados
            """,
)
async def verify_cfdi_batch_endpoint(
    batch_request: BatchCFDIRequest,
    token: str = Depends(get_current_token),
    user_id: int = Depends(get_user_id_from_token),
    db: Session = Depends(get_db),
) -> BatchCFDIResponse:
    """
    Verify multiple CFDIs with the SAT service
    """
    results = []

    for cfdi_request in batch_request.cfdis:
        item = {"request": cfdi_request, "response": None, "error": None}

        try:
            cfdi_result = await verify_cfdi(
                uuid=cfdi_request.uuid,
                emisor_rfc=cfdi_request.emisor_rfc,
                receptor_rfc=cfdi_request.receptor_rfc,
                total=cfdi_request.total,
            )

            # Convert boolean values to strings to match CFDIResponse schema
            if "efos_emisor" in cfdi_result and cfdi_result["efos_emisor"] is False:
                cfdi_result["efos_emisor"] = None
            if "efos_receptor" in cfdi_result and cfdi_result["efos_receptor"] is False:
                cfdi_result["efos_receptor"] = None

            response = CFDIResponse(**cfdi_result)
            item["response"] = response

            # Save verification to history
            create_cfdi_history_from_verification(
                db=db,
                user_id=user_id,
                cfdi_request=cfdi_request.model_dump(),
                verification_result=cfdi_result,
            )

        except Exception as e:
            item["response"] = CFDIResponse()
            item["error"] = str(e)

        results.append(CFDIBatchItem(**item))

    return BatchCFDIResponse(results=results)


@router.get(
    "/history",
    response_model=List[CFDIHistoryResponse],
    summary="Get CFDI History",
    description="""
            Obtiene el historial de consultas de CFDIs realizadas por el usuario

            Esta API devuelve el historial de consultas de CFDIs realizadas por el usuario autenticado.
            Requiere autenticación mediante Bearer token.

            Returns:
                List[CFDIHistoryResponse]: Lista de verificaciones de CFDIs realizadas
            """,
)
async def get_cfdi_history_endpoint(
    skip: int = 0,
    limit: int = 100,
    token: str = Depends(get_current_token),
    user_id: int = Depends(get_user_id_from_token),
    db: Session = Depends(get_db),
) -> List[CFDIHistoryResponse]:
    """
    Get CFDI verification history for the user
    """
    history_items = get_user_cfdi_history(db, user_id=user_id, skip=skip, limit=limit)
    return history_items


@router.get(
    "/history/{uuid}",
    response_model=List[CFDIHistoryResponse],
    summary="Get CFDI History by UUID",
    description="""
            Obtiene el historial de consultas de un CFDI específico

            Esta API devuelve el historial de consultas realizadas para un CFDI específico.
            Requiere autenticación mediante Bearer token.

            Returns:
                List[CFDIHistoryResponse]: Lista de verificaciones realizadas para el CFDI
            """,
)
async def get_cfdi_history_by_uuid_endpoint(
    uuid: str,
    token: str = Depends(get_current_token),
    user_id: int = Depends(get_user_id_from_token),
    db: Session = Depends(get_db),
) -> List[CFDIHistoryResponse]:
    """
    Get history for a specific CFDI
    """
    history_items = get_cfdi_history_by_uuid(db, uuid=uuid)
    return history_items
