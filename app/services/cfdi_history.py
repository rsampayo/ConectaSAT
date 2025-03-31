"""
Service functions for CFDI history
"""

from typing import List, Optional, Dict, Any, Union

from sqlalchemy.orm import Session

from app.models.cfdi_history import CFDIHistory
from app.schemas.cfdi_history import CFDIHistoryCreate


def create_cfdi_history(
    db: Session,
    cfdi_history: Optional[CFDIHistoryCreate] = None,
    **kwargs
) -> CFDIHistory:
    """
    Create a new CFDI history entry - supports both new and old parameter formats for compatibility
    
    Can be called with either:
    1. A CFDIHistoryCreate object: create_cfdi_history(db, cfdi_history_obj)
    2. Old style kwargs: create_cfdi_history(db, uuid="123", emisor_rfc="ABC", ...)
    
    Args:
        db: Database session
        cfdi_history: CFDI history data as object (new style)
        **kwargs: Individual fields (old style)

    Returns:
        The created CFDIHistory object
    """
    # Handle old-style parameter format
    if cfdi_history is None and kwargs:
        # Map old parameter names to new model
        if 'emisor_rfc' in kwargs and 'rfc_emisor' not in kwargs:
            kwargs['rfc_emisor'] = kwargs.pop('emisor_rfc')
        if 'receptor_rfc' in kwargs and 'rfc_receptor' not in kwargs:
            kwargs['rfc_receptor'] = kwargs.pop('receptor_rfc')
        
        # For older calls that don't provide token_id
        if 'token_id' not in kwargs:
            kwargs['token_id'] = 'legacy'
            
        # Convert user_id to string if it's not
        if 'user_id' in kwargs and not isinstance(kwargs['user_id'], str):
            kwargs['user_id'] = str(kwargs['user_id'])
            
        # Create a CFDIHistoryCreate object from kwargs
        cfdi_history = CFDIHistoryCreate(**kwargs)
    
    if not cfdi_history:
        raise ValueError("Either cfdi_history or kwargs must be provided")
    
    # Create database entry from the CFDIHistoryCreate object
    db_history = CFDIHistory(
        uuid=cfdi_history.uuid,
        emisor_rfc=cfdi_history.rfc_emisor,
        receptor_rfc=cfdi_history.rfc_receptor,
        total=cfdi_history.total,
        token_id=cfdi_history.token_id,
        user_id=int(cfdi_history.user_id),  # Ensure user_id is an int in the database
        details=cfdi_history.details,
        estado=cfdi_history.estado,
        es_cancelable=cfdi_history.es_cancelable,
        estatus_cancelacion=cfdi_history.estatus_cancelacion,
        codigo_estatus=cfdi_history.codigo_estatus,
        validacion_efos=cfdi_history.validacion_efos,
    )
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history


def create_cfdi_history_old(
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
    Create a new CFDI history entry (legacy function)

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
    # Now just calls the main function with old-style parameters
    return create_cfdi_history(
        db=db,
        uuid=uuid,
        rfc_emisor=emisor_rfc,
        rfc_receptor=receptor_rfc,
        total=total,
        user_id=user_id,
        estado=estado,
        es_cancelable=es_cancelable,
        estatus_cancelacion=estatus_cancelacion,
        codigo_estatus=codigo_estatus,
        validacion_efos=validacion_efos,
        token_id="legacy",  # Add default token_id for legacy calls
    )


def get_cfdi_history_by_uuid(db: Session, uuid: str, token_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get CFDI history entries by UUID

    Args:
        db: Database session
        uuid: CFDI UUID
        token_id: Optional token ID to filter by

    Returns:
        List of CFDIHistory objects for the given UUID
    """
    query = db.query(CFDIHistory).filter(CFDIHistory.uuid == uuid)
    
    if token_id:
        query = query.filter(CFDIHistory.token_id == token_id)
    
    results = query.order_by(CFDIHistory.created_at.desc()).all()
    
    return [
        {
            "uuid": item.uuid,
            "emisor_rfc": item.emisor_rfc,
            "receptor_rfc": item.receptor_rfc,
            "total": item.total,
            "token_id": item.token_id,
            "user_id": item.user_id,
            "details": item.details,
            "created_at": item.created_at
        }
        for item in results
    ]


def get_verified_cfdis_by_token_id(db: Session, token_id: str) -> List[Dict[str, Any]]:
    """
    Get all CFDI history entries for a token ID

    Args:
        db: Database session
        token_id: Token ID

    Returns:
        List of CFDIHistory objects for the given token ID
    """
    results = (
        db.query(CFDIHistory)
        .filter(CFDIHistory.token_id == token_id)
        .order_by(CFDIHistory.created_at.desc())
        .all()
    )
    
    return [
        {
            "uuid": item.uuid,
            "emisor_rfc": item.emisor_rfc,
            "receptor_rfc": item.receptor_rfc,
            "total": item.total,
            "token_id": item.token_id,
            "user_id": item.user_id,
            "details": item.details,
            "created_at": item.created_at
        }
        for item in results
    ]


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
    return create_cfdi_history_old(
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
