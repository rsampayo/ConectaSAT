"""
Unit tests for CFDI History service
"""
import pytest
from datetime import datetime
from sqlalchemy.orm import Session
from unittest.mock import patch, MagicMock

from app.models.cfdi_history import CFDIHistory
from app.services.cfdi_history import create_cfdi_history, get_cfdi_history_by_uuid, get_user_cfdi_history


def test_create_cfdi_history(db_session: Session):
    """Test creating a CFDI history entry"""
    # Setup test data
    cfdi_data = {
        "uuid": "6128396f-c09b-4ec6-8699-43c5f7e3b230",
        "emisor_rfc": "CDZ050722LA9",
        "receptor_rfc": "XIN06112344A",
        "total": "12000.00",
        "user_id": 1,
        "estado": "Vigente",
        "es_cancelable": "Cancelable sin aceptación",
        "estatus_cancelacion": "No cancelado",
        "codigo_estatus": "S - Comprobante obtenido satisfactoriamente",
        "validacion_efos": "200"
    }
    
    # Call function under test
    history_item = create_cfdi_history(db_session, **cfdi_data)
    
    # Assert results
    assert history_item.id is not None
    assert history_item.uuid == cfdi_data["uuid"]
    assert history_item.emisor_rfc == cfdi_data["emisor_rfc"]
    assert history_item.receptor_rfc == cfdi_data["receptor_rfc"]
    assert history_item.total == cfdi_data["total"]
    assert history_item.user_id == cfdi_data["user_id"]
    assert history_item.estado == cfdi_data["estado"]
    assert history_item.created_at is not None
    

def test_get_cfdi_history_by_uuid(db_session: Session):
    """Test retrieving CFDI history by UUID"""
    # Setup test data
    cfdi_data = {
        "uuid": "6128396f-c09b-4ec6-8699-43c5f7e3b230",
        "emisor_rfc": "CDZ050722LA9",
        "receptor_rfc": "XIN06112344A",
        "total": "12000.00",
        "user_id": 1,
        "estado": "Vigente",
        "es_cancelable": "Cancelable sin aceptación",
        "estatus_cancelacion": "No cancelado",
        "codigo_estatus": "S - Comprobante obtenido satisfactoriamente",
        "validacion_efos": "200"
    }
    
    # Create test record
    create_cfdi_history(db_session, **cfdi_data)
    
    # Call function under test
    history_items = get_cfdi_history_by_uuid(db_session, cfdi_data["uuid"])
    
    # Assert results
    assert len(history_items) >= 1
    assert history_items[0].uuid == cfdi_data["uuid"]
    assert history_items[0].emisor_rfc == cfdi_data["emisor_rfc"]


def test_get_user_cfdi_history(db_session: Session):
    """Test retrieving CFDI history for a specific user"""
    # Setup test data
    user_id = 1
    cfdi_data1 = {
        "uuid": "6128396f-c09b-4ec6-8699-43c5f7e3b230",
        "emisor_rfc": "CDZ050722LA9",
        "receptor_rfc": "XIN06112344A",
        "total": "12000.00",
        "user_id": user_id,
        "estado": "Vigente",
        "es_cancelable": "Cancelable sin aceptación",
        "estatus_cancelacion": "No cancelado",
        "codigo_estatus": "S - Comprobante obtenido satisfactoriamente",
        "validacion_efos": "200"
    }
    
    cfdi_data2 = {
        "uuid": "a9e8f060-d1d7-4ed1-aa25-f9eacd51d46a",
        "emisor_rfc": "XAXX010101000",
        "receptor_rfc": "XIN06112344A",
        "total": "5000.00",
        "user_id": user_id,
        "estado": "Vigente",
        "es_cancelable": "Cancelable sin aceptación",
        "estatus_cancelacion": "No cancelado",
        "codigo_estatus": "S - Comprobante obtenido satisfactoriamente",
        "validacion_efos": "200"
    }
    
    # Create test records
    create_cfdi_history(db_session, **cfdi_data1)
    create_cfdi_history(db_session, **cfdi_data2)
    
    # Call function under test
    history_items = get_user_cfdi_history(db_session, user_id)
    
    # Assert results
    assert len(history_items) >= 2
    uuids = [item.uuid for item in history_items]
    assert cfdi_data1["uuid"] in uuids
    assert cfdi_data2["uuid"] in uuids 