"""
Service functions for CFDI history
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.cfdi_history import CFDIHistory
from app.schemas.cfdi_history import CFDIHistoryCreate


def create_cfdi_history(
    db: Session,
    uuid: str,
    emisor_rfc: str,
    receptor_rfc: str,
    total: str,
    user_id: int,
    estado: Optional[str] = None,
    es_cancelable: Optional[str] = None,
    estatus_cancelacion: Optional[str] = None,
    codigo_estatus: Optional[str] = None,
    validacion_efos: Optional[str] = None,
) -> CFDIHistory:
    """
    Create a new CFDI history entry

    Args:
        db: Database session
        uuid: CFDI UUID
        emisor_rfc: Issuer RFC
        receptor_rfc: Recipient RFC
        total: CFDI total amount
        user_id: ID of the user who performed the verification
        estado: CFDI status
        es_cancelable: Whether the CFDI is cancellable
        estatus_cancelacion: Cancellation status
        codigo_estatus: Status code
        validacion_efos: EFOS validation

    Returns:
        The created CFDIHistory object
    """
    db_history = CFDIHistory(
        uuid=uuid,
        emisor_rfc=emisor_rfc,
        receptor_rfc=receptor_rfc,
        total=total,
        user_id=user_id,
        estado=estado,
        es_cancelable=es_cancelable,
        estatus_cancelacion=estatus_cancelacion,
        codigo_estatus=codigo_estatus,
        validacion_efos=validacion_efos,
    )
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history


def get_cfdi_history_by_uuid(db: Session, uuid: str) -> List[CFDIHistory]:
    """
    Get CFDI history entries by UUID

    Args:
        db: Database session
        uuid: CFDI UUID

    Returns:
        List of CFDIHistory objects for the given UUID
    """
    return (
        db.query(CFDIHistory)
        .filter(CFDIHistory.uuid == uuid)
        .order_by(CFDIHistory.created_at.desc())
        .all()
    )


def get_user_cfdi_history(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[CFDIHistory]:
    """
    Get CFDI history entries for a user

    Args:
        db: Database session
        user_id: User ID
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return

    Returns:
        List of CFDIHistory objects for the given user
    """
    return (
        db.query(CFDIHistory)
        .filter(CFDIHistory.user_id == user_id)
        .order_by(CFDIHistory.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_user_cfdi_history_count(db: Session, user_id: int) -> int:
    """
    Get count of CFDI history entries for a user

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Count of CFDIHistory objects for the given user
    """
    return db.query(CFDIHistory).filter(CFDIHistory.user_id == user_id).count()


def create_cfdi_history_from_verification(
    db: Session, user_id: int, cfdi_request: dict, verification_result: dict
) -> CFDIHistory:
    """
    Create a CFDI history entry from verification request and result

    Args:
        db: Database session
        user_id: User ID
        cfdi_request: CFDI request dict with uuid, emisor_rfc, receptor_rfc, total
        verification_result: Verification result with estado, es_cancelable, etc.

    Returns:
        Created CFDIHistory object
    """
    return create_cfdi_history(
        db=db,
        uuid=cfdi_request["uuid"],
        emisor_rfc=cfdi_request["emisor_rfc"],
        receptor_rfc=cfdi_request["receptor_rfc"],
        total=cfdi_request["total"],
        user_id=user_id,
        estado=verification_result.get("estado"),
        es_cancelable=verification_result.get("es_cancelable"),
        estatus_cancelacion=verification_result.get("estatus_cancelacion"),
        codigo_estatus=verification_result.get("codigo_estatus"),
        validacion_efos=verification_result.get("validacion_efos"),
    )
