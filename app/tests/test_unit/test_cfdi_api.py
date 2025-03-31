"""
Unit tests for CFDI API endpoints
"""
from unittest.mock import MagicMock, patch, AsyncMock
import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.api.cfdi import (
    verify_cfdi_endpoint,
    verify_cfdi_batch_endpoint,
    get_cfdi_history_endpoint,
    get_cfdi_history_by_uuid_endpoint
)
from app.schemas.cfdi import CFDIRequest, BatchCFDIRequest

# Test data
SAMPLE_CFDI_REQUEST = CFDIRequest(
    uuid="6128396f-c09b-4ec6-8699-43c5f7e3b230",
    emisor_rfc="CDZ050722LA9",
    receptor_rfc="XIN06112344A",
    total="12000.00"
)

SAMPLE_BATCH_REQUEST = BatchCFDIRequest(
    cfdis=[
        CFDIRequest(
            uuid="6128396f-c09b-4ec6-8699-43c5f7e3b230",
            emisor_rfc="CDZ050722LA9",
            receptor_rfc="XIN06112344A",
            total="12000.00"
        ),
        CFDIRequest(
            uuid="a9e8f060-d1d7-4ed1-aa25-f9eacd51d46a",
            emisor_rfc="XAXX010101000",
            receptor_rfc="XIN06112344A",
            total="5000.00"
        )
    ]
)

SAMPLE_VERIFICATION_RESULT = {
    "estado": "Vigente",
    "es_cancelable": "Cancelable sin aceptación",
    "estatus_cancelacion": "",
    "codigo_estatus": "S - Comprobante obtenido satisfactoriamente.",
    "validacion_efos": None,
    "efos_emisor": None,
    "efos_receptor": None,
    "raw_response": "<xml>Sample</xml>"
}


@pytest.mark.asyncio
async def test_verify_cfdi_endpoint_success():
    """Test verifying a CFDI through the API endpoint"""
    # Setup mocks
    mock_db = MagicMock(spec=Session)
    mock_token = "test-token"
    mock_user_id = 1
    
    # Mock the verify_cfdi service
    with patch("app.api.cfdi.verify_cfdi", new_callable=AsyncMock) as mock_verify, \
         patch("app.api.cfdi.create_cfdi_history_from_verification") as mock_create_history:
        
        # Configure mock return value
        mock_verify.return_value = SAMPLE_VERIFICATION_RESULT
        
        # Call the function
        result = await verify_cfdi_endpoint(
            cfdi=SAMPLE_CFDI_REQUEST,
            token=mock_token,
            user_id=mock_user_id,
            db=mock_db
        )
        
        # Assert verify_cfdi was called with the right parameters
        mock_verify.assert_called_once_with(
            uuid=SAMPLE_CFDI_REQUEST.uuid,
            emisor_rfc=SAMPLE_CFDI_REQUEST.emisor_rfc,
            receptor_rfc=SAMPLE_CFDI_REQUEST.receptor_rfc,
            total=SAMPLE_CFDI_REQUEST.total
        )
        
        # Assert history was created
        mock_create_history.assert_called_once()
        
        # Assert response matches the verification result
        assert result.estado == SAMPLE_VERIFICATION_RESULT["estado"]
        assert result.es_cancelable == SAMPLE_VERIFICATION_RESULT["es_cancelable"]
        assert result.codigo_estatus == SAMPLE_VERIFICATION_RESULT["codigo_estatus"]


@pytest.mark.asyncio
async def test_verify_cfdi_endpoint_error():
    """Test verifying a CFDI when an error occurs"""
    # Setup mocks
    mock_db = MagicMock(spec=Session)
    mock_token = "test-token"
    mock_user_id = 1
    
    # Mock the verify_cfdi service to raise an exception
    with patch("app.api.cfdi.verify_cfdi", new_callable=AsyncMock) as mock_verify:
        # Configure mock to raise an exception
        mock_verify.side_effect = Exception("Test error")
        
        # Call the function and expect an exception
        with pytest.raises(HTTPException) as excinfo:
            await verify_cfdi_endpoint(
                cfdi=SAMPLE_CFDI_REQUEST,
                token=mock_token,
                user_id=mock_user_id,
                db=mock_db
            )
        
        # Assert the exception contains the expected error message
        assert "Error verifying CFDI" in str(excinfo.value.detail)
        assert excinfo.value.status_code == 500


@pytest.mark.asyncio
async def test_verify_cfdi_batch_endpoint():
    """Test batch verification of CFDIs"""
    # Setup mocks
    mock_db = MagicMock(spec=Session)
    mock_token = "test-token"
    mock_user_id = 1
    
    # Mock the verify_cfdi service
    with patch("app.api.cfdi.verify_cfdi", new_callable=AsyncMock) as mock_verify, \
         patch("app.api.cfdi.create_cfdi_history_from_verification") as mock_create_history:
        
        # Configure mock return value
        mock_verify.return_value = SAMPLE_VERIFICATION_RESULT
        
        # Call the function
        result = await verify_cfdi_batch_endpoint(
            batch_request=SAMPLE_BATCH_REQUEST,
            token=mock_token,
            user_id=mock_user_id,
            db=mock_db
        )
        
        # Assert verify_cfdi was called for each CFDI
        assert mock_verify.call_count == len(SAMPLE_BATCH_REQUEST.cfdis)
        
        # Assert history was created for each CFDI
        assert mock_create_history.call_count == len(SAMPLE_BATCH_REQUEST.cfdis)
        
        # Assert response contains the correct number of results
        assert len(result.results) == len(SAMPLE_BATCH_REQUEST.cfdis)
        
        # Check each result
        for item in result.results:
            assert item.response.estado == SAMPLE_VERIFICATION_RESULT["estado"]
            assert item.error is None


@pytest.mark.asyncio
async def test_verify_cfdi_batch_endpoint_with_error():
    """Test batch verification with an error for one CFDI"""
    # Setup mocks
    mock_db = MagicMock(spec=Session)
    mock_token = "test-token"
    mock_user_id = 1
    
    # Mock the verify_cfdi service
    with patch("app.api.cfdi.verify_cfdi", new_callable=AsyncMock) as mock_verify, \
         patch("app.api.cfdi.create_cfdi_history_from_verification") as mock_create_history:
        
        # Configure mock to succeed first time and fail second time
        mock_verify.side_effect = [
            SAMPLE_VERIFICATION_RESULT,
            Exception("Error processing CFDI")
        ]
        
        # Call the function
        result = await verify_cfdi_batch_endpoint(
            batch_request=SAMPLE_BATCH_REQUEST,
            token=mock_token,
            user_id=mock_user_id,
            db=mock_db
        )
        
        # Assert verify_cfdi was called for each CFDI
        assert mock_verify.call_count == len(SAMPLE_BATCH_REQUEST.cfdis)
        
        # Assert history was created only for the successful CFDI
        assert mock_create_history.call_count == 1
        
        # Assert response contains the correct number of results
        assert len(result.results) == len(SAMPLE_BATCH_REQUEST.cfdis)
        
        # Check the results
        assert result.results[0].error is None
        assert result.results[0].response.estado == SAMPLE_VERIFICATION_RESULT["estado"]
        assert "Error processing CFDI" in result.results[1].error


@pytest.mark.asyncio
async def test_get_cfdi_history_endpoint():
    """Test retrieving CFDI history for a user"""
    # Setup mocks
    mock_db = MagicMock(spec=Session)
    mock_token = "test-token"
    mock_user_id = 1
    
    # Mock history items
    history_items = [MagicMock() for _ in range(3)]
    
    # Mock the get_user_cfdi_history service
    with patch("app.api.cfdi.get_user_cfdi_history") as mock_get_history:
        # Configure mock return value
        mock_get_history.return_value = history_items
        
        # Call the function
        result = await get_cfdi_history_endpoint(
            skip=0,
            limit=10,
            token=mock_token,
            user_id=mock_user_id,
            db=mock_db
        )
        
        # Assert get_user_cfdi_history was called with the right parameters
        mock_get_history.assert_called_once_with(
            mock_db, user_id=mock_user_id, skip=0, limit=10
        )
        
        # Assert the result is the history items
        assert result == history_items


@pytest.mark.asyncio
async def test_get_cfdi_history_by_uuid_endpoint():
    """Test retrieving CFDI history for a specific UUID"""
    # Setup mocks
    mock_db = MagicMock(spec=Session)
    mock_token = "test-token"
    mock_user_id = 1
    uuid = "6128396f-c09b-4ec6-8699-43c5f7e3b230"
    
    # Mock history items
    history_items = [MagicMock() for _ in range(2)]
    
    # Mock the get_cfdi_history_by_uuid service
    with patch("app.api.cfdi.get_cfdi_history_by_uuid") as mock_get_history:
        # Configure mock return value
        mock_get_history.return_value = history_items
        
        # Call the function
        result = await get_cfdi_history_by_uuid_endpoint(
            uuid=uuid,
            token=mock_token,
            user_id=mock_user_id,
            db=mock_db
        )
        
        # Assert get_cfdi_history_by_uuid was called with the right parameters
        mock_get_history.assert_called_once_with(mock_db, uuid=uuid)
        
        # Assert the result is the history items
        assert result == history_items 