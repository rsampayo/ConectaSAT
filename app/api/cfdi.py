"""
CFDI verification API router
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_token, get_db, get_user_id_from_token
from app.schemas.cfdi import CFDIBatch, CFDIResponse, CFDIVerifyRequest, VerifyCFDI
from app.schemas.cfdi_history import CFDIHistoryCreate
from app.services.cfdi_history import (
    create_cfdi_history,
    get_cfdi_history_by_uuid,
    get_verified_cfdis_by_token_id,
)
from app.services.sat_verification import CFDIVerification

router = APIRouter(prefix="/api/v1/cfdi", tags=["cfdi"])


@router.post(
    "/verify",
    response_model=CFDIResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify Cfdi",
    description="""
            Verifica la validez de un CFDI con el SAT y devuelve el resultado
            de dicha verificación, así como información del mismo.
            """,
)
async def verify_cfdi_endpoint(
    cfdi_data: CFDIVerifyRequest,
    db: Session = Depends(get_db),
    token_id: str = Depends(get_current_token),
    user_id: str = Depends(get_user_id_from_token),
):
    """
    Verifies a CFDI with the SAT and returns the validation result along with CFDI information.
    """
    cfdi_verification = CFDIVerification()
    try:
        cfdi_info = cfdi_verification.validate_cfdi(
            cfdi_data.uuid,
            cfdi_data.rfc_emisor,
            cfdi_data.rfc_receptor,
            cfdi_data.total,
        )

        # Save to history
        history_entry = CFDIHistoryCreate(
            uuid=cfdi_data.uuid,
            rfc_emisor=cfdi_data.rfc_emisor,
            rfc_receptor=cfdi_data.rfc_receptor,
            total=str(cfdi_data.total),
            token_id=token_id,
            details=cfdi_info,
            user_id=user_id,
        )
        create_cfdi_history(db, history_entry)

        return CFDIResponse(
            status="success",
            message="CFDI verificado exitosamente",
            data=cfdi_info,
        )
    except Exception as e:
        logging.error(f"Error verifying CFDI: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/verify-batch",
    response_model=CFDIBatch,
    status_code=status.HTTP_200_OK,
    summary="Verify Cfdi Batch",
    description="""
            Verifica la validez de múltiples CFDIs con el SAT en una sola petición

            Devuelve un objeto con los resultados de cada CFDI procesado.
            """,
)
async def verify_cfdi_batch_endpoint(
    cfdi_data: List[CFDIVerifyRequest],
    db: Session = Depends(get_db),
    token_id: str = Depends(get_current_token),
    user_id: str = Depends(get_user_id_from_token),
):
    """
    Verifies multiple CFDIs with the SAT in a single request.
    Returns an object with results for each CFDI processed.
    """
    results = []
    cfdi_verification = CFDIVerification()

    for cfdi in cfdi_data:
        try:
            cfdi_info = cfdi_verification.validate_cfdi(
                cfdi.uuid, cfdi.rfc_emisor, cfdi.rfc_receptor, cfdi.total
            )

            # Save to history
            history_entry = CFDIHistoryCreate(
                uuid=cfdi.uuid,
                rfc_emisor=cfdi.rfc_emisor,
                rfc_receptor=cfdi.rfc_receptor,
                total=str(cfdi.total),
                token_id=token_id,
                details=cfdi_info,
                user_id=user_id,
            )
            create_cfdi_history(db, history_entry)

            results.append(
                VerifyCFDI(
                    uuid=cfdi.uuid,
                    status="success",
                    message="CFDI verificado exitosamente",
                    data=cfdi_info,
                )
            )
        except Exception as e:
            logging.error(f"Error verifying CFDI {cfdi.uuid}: {e}")
            results.append(
                VerifyCFDI(uuid=cfdi.uuid, status="error", message=str(e), data=None)
            )

    return CFDIBatch(results=results)


@router.get(
    "/history",
    status_code=status.HTTP_200_OK,
    summary="Get CFDI History",
    description="Obtiene el historial de CFDIs verificados",
)
async def get_cfdi_history_endpoint(
    db: Session = Depends(get_db),
    token_id: str = Depends(get_current_token),
    user_id: str = Depends(get_user_id_from_token),
):
    """
    Gets the history of verified CFDIs.
    """
    try:
        history = get_verified_cfdis_by_token_id(db, token_id)
        return {
            "status": "success",
            "message": "Historial obtenido exitosamente",
            "data": history,
        }
    except Exception as e:
        logging.error(f"Error getting CFDI history: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/history/{uuid}",
    status_code=status.HTTP_200_OK,
    summary="Get CFDI History by UUID",
    description="Obtiene el historial de un CFDI específico por su UUID",
)
async def get_cfdi_history_by_uuid_endpoint(
    uuid: str,
    db: Session = Depends(get_db),
    token_id: str = Depends(get_current_token),
    user_id: str = Depends(get_user_id_from_token),
):
    """
    Gets the history of a specific CFDI by its UUID.
    """
    try:
        history = get_cfdi_history_by_uuid(db, uuid, token_id)
        return {
            "status": "success",
            "message": "Historial obtenido exitosamente",
            "data": history,
        }
    except Exception as e:
        logging.error(f"Error getting CFDI history for UUID {uuid}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
