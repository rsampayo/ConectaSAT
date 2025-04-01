"""Unit tests for CFDI History service."""

from datetime import datetime
from typing import Any, Dict, cast

from sqlalchemy.orm import Session

from app.schemas.cfdi_history import CFDIHistoryCreate
from app.services.cfdi_history import (
    create_cfdi_history,
    create_cfdi_history_from_verification,
    get_cfdi_history_by_uuid,
    get_user_cfdi_history,
    get_user_cfdi_history_count,
)


def test_create_cfdi_history(db_session: Session):
    """Test creating a CFDI history entry."""
    # Setup test data
    cfdi_data: Dict[str, Any] = {
        "uuid": "6128396f-c09b-4ec6-8699-43c5f7e3b230",
        "rfc_emisor": "CDZ050722LA9",
        "rfc_receptor": "XIN06112344A",
        "total": "12000.00",
        "user_id": "1",
        "estado": "Vigente",
        "es_cancelable": "Cancelable sin aceptación",
        "estatus_cancelacion": "No cancelado",
        "codigo_estatus": "S - Comprobante obtenido satisfactoriamente",
        "validacion_efos": "200",
    }

    # Create a proper CFDIHistoryCreate model
    history_create = CFDIHistoryCreate(**cfdi_data)

    # Call function under test
    history_item = create_cfdi_history(db_session, history_create)

    # Assert results
    assert history_item.id is not None
    assert history_item.uuid == cfdi_data["uuid"]
    assert history_item.emisor_rfc == cfdi_data["rfc_emisor"]
    assert history_item.receptor_rfc == cfdi_data["rfc_receptor"]
    assert history_item.total == cfdi_data["total"]
    assert history_item.user_id == int(cfdi_data["user_id"])
    assert history_item.estado == cfdi_data["estado"]
    assert history_item.created_at is not None


def test_get_cfdi_history_by_uuid(db_session: Session):
    """Test retrieving CFDI history by UUID."""
    # Setup test data
    cfdi_data: Dict[str, Any] = {
        "uuid": "6128396f-c09b-4ec6-8699-43c5f7e3b230",
        "rfc_emisor": "CDZ050722LA9",
        "rfc_receptor": "XIN06112344A",
        "total": "12000.00",
        "user_id": "1",
        "estado": "Vigente",
        "es_cancelable": "Cancelable sin aceptación",
        "estatus_cancelacion": "No cancelado",
        "codigo_estatus": "S - Comprobante obtenido satisfactoriamente",
        "validacion_efos": "200",
    }

    # Create a proper CFDIHistoryCreate model
    history_create = CFDIHistoryCreate(**cfdi_data)

    # Create test record
    create_cfdi_history(db_session, history_create)

    # Call function under test
    history_items = get_cfdi_history_by_uuid(db_session, str(cfdi_data["uuid"]))

    # Assert results
    assert len(history_items) >= 1
    # Now testing dict access instead of attribute access
    assert history_items[0]["uuid"] == cfdi_data["uuid"]
    assert history_items[0]["emisor_rfc"] == cfdi_data["rfc_emisor"]


def test_get_user_cfdi_history(db_session: Session):
    """Test retrieving CFDI history for a specific user."""
    # Setup test data
    user_id = "1"
    cfdi_data1: Dict[str, Any] = {
        "uuid": "6128396f-c09b-4ec6-8699-43c5f7e3b230",
        "rfc_emisor": "CDZ050722LA9",
        "rfc_receptor": "XIN06112344A",
        "total": "12000.00",
        "user_id": user_id,
        "estado": "Vigente",
        "es_cancelable": "Cancelable sin aceptación",
        "estatus_cancelacion": "No cancelado",
        "codigo_estatus": "S - Comprobante obtenido satisfactoriamente",
        "validacion_efos": "200",
    }

    cfdi_data2: Dict[str, Any] = {
        "uuid": "a9e8f060-d1d7-4ed1-aa25-f9eacd51d46a",
        "rfc_emisor": "XAXX010101000",
        "rfc_receptor": "XIN06112344A",
        "total": "5000.00",
        "user_id": user_id,
        "estado": "Vigente",
        "es_cancelable": "Cancelable sin aceptación",
        "estatus_cancelacion": "No cancelado",
        "codigo_estatus": "S - Comprobante obtenido satisfactoriamente",
        "validacion_efos": "200",
    }

    # Create proper CFDIHistoryCreate models
    history_create1 = CFDIHistoryCreate(**cfdi_data1)
    history_create2 = CFDIHistoryCreate(**cfdi_data2)

    # Create test records
    create_cfdi_history(db_session, history_create1)
    create_cfdi_history(db_session, history_create2)

    # Call function under test
    history_items = get_user_cfdi_history(db_session, int(user_id))

    # Assert results
    assert len(history_items) >= 2
    uuids = [item.uuid for item in history_items]
    assert cfdi_data1["uuid"] in uuids
    assert cfdi_data2["uuid"] in uuids


def test_get_user_cfdi_history_count(db_session: Session):
    """Test counting CFDI history entries for a specific user."""
    # Setup test data
    user_id = "2"  # Using a different user_id to avoid interference with other tests
    cfdi_data1: Dict[str, Any] = {
        "uuid": "6128396f-c09b-4ec6-8699-43c5f7e3b231",
        "rfc_emisor": "CDZ050722LA9",
        "rfc_receptor": "XIN06112344A",
        "total": "12000.00",
        "user_id": user_id,
        "estado": "Vigente",
        "es_cancelable": "Cancelable sin aceptación",
        "estatus_cancelacion": "No cancelado",
        "codigo_estatus": "S - Comprobante obtenido satisfactoriamente",
        "validacion_efos": "200",
    }

    cfdi_data2: Dict[str, Any] = {
        "uuid": "a9e8f060-d1d7-4ed1-aa25-f9eacd51d46b",
        "rfc_emisor": "XAXX010101000",
        "rfc_receptor": "XIN06112344A",
        "total": "5000.00",
        "user_id": user_id,
        "estado": "Vigente",
        "es_cancelable": "Cancelable sin aceptación",
        "estatus_cancelacion": "No cancelado",
        "codigo_estatus": "S - Comprobante obtenido satisfactoriamente",
        "validacion_efos": "200",
    }

    # Create proper CFDIHistoryCreate models
    history_create1 = CFDIHistoryCreate(**cfdi_data1)
    history_create2 = CFDIHistoryCreate(**cfdi_data2)

    # Create test records
    create_cfdi_history(db_session, history_create1)
    create_cfdi_history(db_session, history_create2)

    # Call function under test
    count = get_user_cfdi_history_count(db_session, int(user_id))

    # Assert the count is at least 2 (may be more if other tests have created records)
    assert count >= 2


def test_create_cfdi_history_from_verification(db_session: Session):
    """Test creating a CFDI history entry from verification data."""
    # Setup test data
    user_id = 3
    cfdi_request = {
        "uuid": "6128396f-c09b-4ec6-8699-43c5f7e3b232",
        "emisor_rfc": "CDZ050722LA9",
        "receptor_rfc": "XIN06112344A",
        "total": "12000.00",
    }
    verification_result = {
        "estado": "Vigente",
        "es_cancelable": "Cancelable sin aceptación",
        "estatus_cancelacion": "No cancelado",
        "codigo_estatus": "S - Comprobante obtenido satisfactoriamente",
        "validacion_efos": "200",
    }

    # Call function under test - this function internally handles dictionary conversion
    history_item = create_cfdi_history_from_verification(
        db=db_session,
        user_id=user_id,
        cfdi_request=cfdi_request,
        verification_result=verification_result,
    )

    # Assert results
    assert history_item.id is not None
    assert history_item.uuid == cfdi_request["uuid"]
    assert history_item.emisor_rfc == cfdi_request["emisor_rfc"]
    assert history_item.receptor_rfc == cfdi_request["receptor_rfc"]
    assert history_item.total == cfdi_request["total"]
    assert history_item.user_id == user_id
    assert history_item.estado == verification_result["estado"]
    assert history_item.es_cancelable == verification_result["es_cancelable"]
    assert (
        history_item.estatus_cancelacion == verification_result["estatus_cancelacion"]
    )
    assert history_item.codigo_estatus == verification_result["codigo_estatus"]
    assert history_item.validacion_efos == verification_result["validacion_efos"]
